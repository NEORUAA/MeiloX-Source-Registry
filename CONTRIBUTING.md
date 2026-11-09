# Contributing sources

Keep implementation and releases in each source's own GitHub repository. Submit
only an entry in `index.json` here. Never include plugin code, credentials,
session exports, private captures or generated logs in this repository.

1. Commit the final `.meisource` package in the official source repository.
2. Add or update the six fields documented in [README.md](README.md): stable
   package/provider IDs, display name, canonical repository, relative package path
   and API version. Keep IDs stable across updates.
3. The host resolves the newest package commit (or current `HEAD` when the
   GitHub API is rate-limited) and reads the package manifest. Do not copy a version, commit SHA or digest into this registry; those
   values must come from the package that is actually downloaded.
4. Run `python3 validate.py --test` and describe the change in a pull request.
5. Include links to the source repository and readable manifest, plus a concise
   explanation of added/removed permissions. Explain any identity or repository
   ownership change explicitly; it must not silently inherit an existing listing.

Do not add a download URL, branch/tag URL, release redirect, URL shortener or
custom download server. The package path must stay inside the same GitHub
repository and end in `.meisource`.

The index is limited to 256 KiB and 200 sources. Names are plain text. Package and
provider IDs are unique; the host's `local` provider is not a market package.

## Maintainer review

Check publisher ownership, source changes, license/attribution and manifest
identity/permissions before merging. A passing metadata check is not a plugin
security review or a guarantee that a service grants playback rights. Permission
changes must stay visible to host package review rather than being approved by
index metadata.

The PR workflow runs the base branch's validator and reads only the proposed JSON
blob. It never checks out a submission, installs dependencies from it, runs its
tests/build scripts, imports its plugin or downloads its package. Review changes to
the schema, validator and workflow separately before merging them into the trusted
base. Do not add PR-controlled commands or package execution to this job.
