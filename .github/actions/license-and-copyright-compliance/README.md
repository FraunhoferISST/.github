# License and Copyright Compliance

This composite action runs REUSE lint, optionally checks whether the LICENSE file matches the license file used by REUSE, and checks copyright years in changed files. It operates on the checked-out repository.

```yaml
name: License and Copyright Compliance
on: pull_request
jobs:
  compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: FraunhoferISST/.github/.github/actions/license-and-copyright-compliance@main
        with:
          base-sha: ${{ github.event.pull_request.base.sha }}
          license-file: LICENSE
          reference-license-file: LICENSES/LicenseRef-Fraunhofer-License.txt
```

`fetch-depth: 0` ensures the base commit is available. The action needs Git, Python 3 and Docker on a Linux runner. REUSE runs in Docker; the year check uses the runner's Python.

| Input | Default | Description |
| --- | --- | --- |
| `base-sha` | empty | Base revision to compare directly with `HEAD`; required when the year check is enabled. |
| `check-copyright-years` | `true` | Set to `false` to skip the year check. |
| `check-license-text` | `true` | Set to `false` to skip license file comparison. |
| `license-file` | `LICENSE` | First file for the byte-for-byte comparison. |
| `reference-license-file` | empty | Second file for the comparison; required when the license text check is enabled. |

Boolean inputs must be `true` or `false`. File paths are relative to the checked-out repository. License comparison requires both files to exist; it does not check their contents against an authoritative license. REUSE lint always runs and accepts any valid REUSE metadata, including metadata supplied via `.license` files and `REUSE.toml`.

The year check considers added, copied, modified, renamed and type-changed files of any type. In the first 2048 characters, excluding REUSE ignore blocks, it checks the first year or year range after each `SPDX-FileCopyrightText:` marker on the same line. It supports four-digit years, ranges with four- or two-digit end years, and comma-separated lists; the last year must be the current UTC year. It does not require copyright markers or years and does not check sidecar or global REUSE metadata. Its local REUSE-style file exclusions may differ if REUSE changes.