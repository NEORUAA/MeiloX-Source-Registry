# MeiloX Source Registry

A small, declarative catalog of independently maintained MeiloX music sources.
The host reads `index.json` to discover sources and resolves each listing to the
latest package committed in that source repository. This repository stores
metadata, not plugin code or account configuration.

## Index contract

The root object contains `schemaVersion: 2` and `sources`. Every source has exactly
these fields:

| Field | Meaning |
| --- | --- |
| `packageId` | Stable package identity, equal to manifest `id` |
| `providerId` | Stable content identity, equal to manifest `providerId` |
| `name` | Display name |
| `repository` | Canonical HTTPS GitHub source repository |
| `packagePath` | Relative `.meisource` path inside the repository |
| `apiVersion` | Supported MeiloX source API version, currently 1 or 2 |

The host asks GitHub for the newest commit touching the package path, then
downloads that commit-pinned archive. If GitHub's unauthenticated API rate limit is
reached, it falls back to the repository's current `HEAD` package and still checks
its archive and manifest before installation. It reads and
validates the package manifest, including its semantic version, and computes the
SHA-256 of the exact ZIP before installation. Registry metadata never copies a
version or digest that can become stale.

Package paths are relative, stay inside the declared repository and end in
`.meisource`; package and provider IDs are unique. `index.schema.json` describes
the wire format; the validator additionally checks repository ownership and path
traversal.

The initial sources follow their maintained producer repositories:

| Source | Package ID | Provider ID | Repository |
| --- | --- | --- | --- |
| 网易云音乐 | `org.meilox.source.netease` | `netease` | [MeiloX-Netease-Source](https://github.com/NEORUAA/MeiloX-Netease-Source) |
| QQ 音乐 | `org.meilox.qqmusic` | `qqmusic` | [MeiloX-QQMusic-Source](https://github.com/NEORUAA/MeiloX-QQMusic-Source) |

## Trust and updates

A listing does not grant permissions. Hosts must verify the downloaded ZIP digest,
package identity, provider identity, manifest version, API compatibility and
manifest before installing it. Network hosts and interactive/native SDK
permissions are reviewed from the actual package manifest.

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

The aggregate checks cover repository identity, package paths, identifiers,
unknown fields, duplicate entries and bounded input. The validator reads metadata
only and never downloads or executes a plugin.

## Contribute

Submit a pull request updating `index.json`; see [CONTRIBUTING.md](CONTRIBUTING.md).
Each source stays in its own repository. Maintainers review source identity,
package path and manifest permissions before merging a listing. A package version
change is read from the source repository automatically.

PR validation uses the trusted base branch's workflow and reads only the proposed
JSON blob. It never checks out a submission, installs dependencies from it, runs
its tests/build scripts, imports its plugin or downloads its package. This follows
the [GitHub base-context event model](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request_target).
Review changes to the schema, validator and workflow separately before merging them
into the trusted base. Do not add PR-controlled commands or package execution to
this job.

## 用户说明

音源由各自仓库独立维护，可通过 PR 投稿。市场索引只提供仓库和包路径，商店会读取
对应仓库当前最新版插件的 manifest 版本和校验值。安装时仍需核对插件实际申请的权限；
新增权限不会自动放行。自行导入的同名插件不会仅凭相同 ID 获得自动更新信任，卸载后的
插件也不会自动装回。

Licensed under GPL-3.0-only; see [LICENSE](LICENSE).
