# Contributing sources

Keep implementation and releases in your source's own GitHub repository. Submit
only an entry in `index.json` here. Never include plugin code, credentials,
session exports, private captures or generated logs in this repository.

1. Commit the final `.meisource` package in the official source repository.
2. Use its full commit ID in a raw GitHub URL. Compute SHA-256 from those exact ZIP
   bytes, not the JavaScript entry or an unpacked directory.
3. Add or update the eight fields documented in [README.md](README.md). Package
   ID, provider ID, version and API version must match the package manifest. Keep
   IDs stable across updates and increase the semantic version.
4. Run `python3 validate.py --test` and describe the change in a pull request.
5. Include links to the source commit and readable manifest, plus a concise
   explanation of added/removed permissions. Explain any identity or repository
   ownership change explicitly; it must not silently inherit an existing listing.

Do not use a branch, tag, `latest` release URL, URL shortener or custom download
server. The package URL must use the same GitHub owner and repository as the
source repository and end in `.meisource`. Leave the index unchanged until the
actual package, immutable URL and real digest exist.

The index is limited to 256 KiB and 200 sources. Names are plain text. Package and
provider IDs are unique; the host's `local` provider is not a market package.

## Maintainer review

Check publisher ownership, source changes, license/attribution, digest and manifest
identity/permissions before merging. A passing metadata check is not a plugin
security review or a guarantee that a service grants playback rights. Permission
changes must stay visible to host package review rather than being approved by
index metadata.

The PR workflow runs the base branch's validator and reads only the proposed JSON
blob. It never checks out a submission, installs dependencies from it, runs its
tests/build scripts, imports its plugin or downloads its package. Review changes
to the schema, validator and workflow separately before merging them into the
trusted base. Do not add PR-controlled commands or package execution to this job.
