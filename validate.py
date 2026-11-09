#!/usr/bin/env python3
"""Validate registry metadata offline; never import, fetch, or execute a source."""

import argparse
import copy
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
MAX_INDEX_BYTES = 256 * 1024


class ValidationError(ValueError):
    pass


def require(condition, path, message):
    if not condition:
        raise ValidationError(f"{path}: {message}")


def matches_type(value, name):
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": type(value) is int,
        "null": value is None,
    }[name]


def schema_check(value, spec, root, path="registry"):
    """Evaluate the small, closed JSON Schema vocabulary used by this index."""
    supported = {"$schema", "$defs", "$ref", "title", "type", "const", "enum", "minLength", "maxLength",
                 "pattern", "properties", "required", "additionalProperties", "maxItems", "items"}
    require(set(spec).issubset(supported), "schema", "unsupported schema keyword")
    if "$ref" in spec:
        reference = spec["$ref"]
        require(reference.startswith("#/$defs/"), path, "external schema references are unsupported")
        return schema_check(value, root["$defs"][reference.removeprefix("#/$defs/")], root, path)
    if "type" in spec:
        kinds = spec["type"] if isinstance(spec["type"], list) else [spec["type"]]
        require(any(matches_type(value, kind) for kind in kinds), path, "wrong JSON type")
    if "const" in spec:
        expected = spec["const"]
        require(type(value) is type(expected) and value == expected, path, "unsupported constant")
    if "enum" in spec:
        require(any(type(value) is type(item) and value == item for item in spec["enum"]), path, "unsupported value")
    if isinstance(value, str):
        require(len(value) >= spec.get("minLength", 0), path, "string is too short")
        require(len(value) <= spec.get("maxLength", sys.maxsize), path, "string is too long")
        if "pattern" in spec:
            require(re.fullmatch(spec["pattern"], value) is not None, path, "invalid string format")
    if isinstance(value, dict):
        properties = spec.get("properties", {})
        require(set(spec.get("required", [])).issubset(value), path, "required fields are missing")
        if spec.get("additionalProperties") is False:
            require(set(value).issubset(properties), path, "unknown fields are not allowed")
        for key, child in properties.items():
            if key in value:
                schema_check(value[key], child, root, f"{path}.{key}")
    if isinstance(value, list):
        require(len(value) <= spec.get("maxItems", sys.maxsize), path, "too many entries")
        if "items" in spec:
            for index, item in enumerate(value):
                schema_check(item, spec["items"], root, f"{path}[{index}]")


def reject_duplicates(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "registry", "duplicate JSON keys are not allowed")
        result[key] = value
    return result


def read_json(path, limit=MAX_INDEX_BYTES):
    require(path.is_file() and path.stat().st_size <= limit, "registry", "file is missing or exceeds 256 KiB")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicates,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValidationError("registry: non-finite numbers are invalid")))


def validate(value, schema):
    schema_check(value, schema, schema)
    packages, providers = set(), set()
    for index, source in enumerate(value["sources"]):
        path = f"registry.sources[{index}]"
        package, provider = source["packageId"].casefold(), source["providerId"].casefold()
        require(package not in packages, path, "packageId must be unique")
        require(provider not in providers, path, "providerId must be unique")
        require(provider != "local", path, "the local provider belongs to the host")
        require(source["name"].strip() == source["name"] and bool(source["name"].strip()), path, "name must not contain surrounding whitespace")
        repository = source["repository"].removeprefix("https://github.com/")
        require(not repository.endswith(".git") and all(part not in (".", "..") for part in repository.split("/")), path, "repository must be canonical")
        package_path = source["packagePath"]
        require(not package_path.startswith("/") and all(part not in (".", "..", "") for part in package_path.split("/")),
                path, "packagePath must be a relative path without traversal")
        require(package_path.endswith(".meisource"), path, "packagePath must name a .meisource package")
        packages.add(package)
        providers.add(provider)
    return value


def self_test(schema):
    seed = {"schemaVersion": 2, "sources": [{
        "packageId": "org.example.source", "providerId": "example", "name": "Example",
        "repository": "https://github.com/example/source",
        "packagePath": "dist/example.meisource", "apiVersion": 2,
    }]}
    validate(seed, schema)
    validate({"schemaVersion": 2, "sources": []}, schema)
    ready = copy.deepcopy(seed)
    cases = [
        ("packageId", "bad id"), ("packageId", "Org.Example"), ("packageId", "a" * 81),
        ("providerId", "ab"), ("providerId", "Uppercase"), ("providerId", "a" * 81),
        ("providerId", "local"), ("name", " Example"), ("name", "Bad\nname"),
        ("apiVersion", True), ("apiVersion", 3),
        ("repository", "https://github.com.evil.test/example/source"),
        ("repository", "http://github.com/example/source"),
        ("packagePath", "../example.meisource"), ("packagePath", "main/example.zip"),
        ("packagePath", "/example.meisource"), ("packagePath", "example.meisource?token=private"),
        ("packagePath", "example.meisource/extra"), ("packagePath", None),
    ]
    def rejected(value):
        try:
            validate(value, schema)
        except ValidationError:
            return
        raise AssertionError("Invalid metadata was accepted")
    for key, item in cases:
        invalid = copy.deepcopy(ready)
        invalid["sources"][0][key] = item
        rejected(invalid)
    for key in ("packageId", "providerId", "packagePath"):
        invalid = copy.deepcopy(ready)
        del invalid["sources"][0][key]
        rejected(invalid)
    for key in ("packageId", "providerId"):
        invalid = copy.deepcopy(ready)
        duplicate = copy.deepcopy(invalid["sources"][0])
        duplicate["packageId" if key == "providerId" else "providerId"] += "other"
        invalid["sources"].append(duplicate)
        rejected(invalid)
    invalid = copy.deepcopy(ready)
    invalid["sources"][0]["permissions"] = {"network": ["unreviewed.example"]}
    rejected(invalid)
    try:
        json.loads('{"schemaVersion":2,"schemaVersion":2}', object_pairs_hook=reject_duplicates)
    except ValidationError:
        pass
    else:
        raise AssertionError("Duplicate JSON keys were accepted")
    print("Offline registry contract tests passed.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=ROOT / "index.json")
    parser.add_argument("--test", action="store_true", help="run the aggregate offline contract checks")
    args = parser.parse_args()
    try:
        schema = read_json(ROOT / "index.schema.json")
        if args.test:
            self_test(schema)
            return 0
        value = validate(read_json(args.index), schema)
        print(f"Registry valid: {len(value['sources'])} sources.")
    except (ValidationError, json.JSONDecodeError, UnicodeDecodeError, OSError) as error:
        print(f"Registry validation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
