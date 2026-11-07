# MeiloX Source Registry

A small, declarative catalog of independently maintained MeiloX music sources.
The host reads `index.json` to discover sources and check installed versions.
This repository stores metadata, not plugin code or account configuration.

## Index contract

The root object contains `schemaVersion: 1` and `sources`. Every source has exactly
these fields:

| Field | Meaning |
| --- | --- |
| `packageId` | Stable package identity, equal to manifest `id` |
| `providerId` | Stable content identity, equal to manifest `providerId` |
| `name` | Display name |
| `version` | Semantic version, equal to manifest `version` |
| `repository` | Canonical HTTPS GitHub source repository |
| `packageUrl` | HTTPS raw GitHub `.meisource` URL pinned to a full 40-character commit |
| `sha256` | Lowercase SHA-256 of the exact ZIP bytes |
| `apiVersion` | Supported MeiloX source API version, currently 1 or 2 |

Package URLs must belong to the declared repository. Branches, tags, release
redirects, custom download hosts, query strings and credentials are not accepted.
Package and provider IDs are unique. `index.schema.json` describes the wire
format; the validator additionally checks repository ownership and uniqueness.

The initial sources are pinned to their reviewed producer commits:

| Source | Package ID | Provider ID | Repository |
| --- | --- | --- | --- |
| 网易云音乐 | `org.meilox.source.netease` | `netease` | [MeiloX-Netease-Source](https://github.com/NEORUAA/MeiloX-Netease-Source) |
| QQ 音乐 | `org.meilox.qqmusic` | `qqmusic` | [MeiloX-QQMusic-Source](https://github.com/NEORUAA/MeiloX-QQMusic-Source) |


## Trust and updates

A listing does not grant permissions. Hosts must verify the downloaded ZIP digest,
package identity, provider identity, version, API compatibility and manifest
before installing it. Network hosts and interactive/native SDK permissions are
reviewed from the actual package manifest.

Automatic updates require an established matching repository origin and no new
permissions. An externally imported package is not trusted just because its ID
matches a listing. A host may establish origin after comparing its installed
payload with the registry's digest-verified package, or after explicit reviewed
installation/update. New permissions require a fresh review. Disabled and
uninstalled sources must not be silently re-enabled or reinstalled.

## Validate locally

Python 3.10 or newer is sufficient. No packages, plugin runtimes or network access
are required:

```sh
python3 validate.py --test
python3 validate.py --index index.json
```

The aggregate checks cover immutable URLs, repository binding, identifiers,
versions, digests, duplicate entries/JSON keys, unknown fields and bounded input.
The validator reads metadata only and never downloads or executes a plugin.

## Contribute

Submit a pull request updating `index.json`; see [CONTRIBUTING.md](CONTRIBUTING.md).
Each source stays in its own repository. Maintainers review source identity,
package bytes and manifest permissions before merging a listing or new version.

PR validation uses the trusted base branch's workflow, schema and validator. It
fetches the proposed `index.json` as data without checking out or executing PR
code. No plugin is downloaded and no credentials are provided. This follows the
[GitHub base-context event model](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request_target).
Changes to validation policy or workflows require separate maintainer review.

## 用户说明

音源由各自仓库独立维护，可通过 PR 投稿。市场索引只提供版本、下载地址和校验值。
安装时仍需核对插件实际申请的权限；新增权限不会自动放行。自行导入的同名插件不会
仅凭相同 ID 获得自动更新信任，卸载后的插件也不会自动装回。

Licensed under GPL-3.0-only; see [LICENSE](LICENSE).
