import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

YEAR_RE = re.compile(r"\b([0-9]{4})(?:[ \t]*[-\u2013][ \t]*([0-9]{4}|[0-9]{2}))?\b")
COPYRIGHT_RE = re.compile(
    rf"SPDX-FileCopyrightText:[^\r\n]*?(?P<years>{YEAR_RE.pattern}"
    rf"(?:[ \t]*,[ \t]*{YEAR_RE.pattern})*)",
    re.IGNORECASE,
)
IGNORE_BLOCK_RE = re.compile(r"REUSE-IgnoreStart.*?(?:REUSE-IgnoreEnd|\Z)", re.DOTALL)
IGNORED_NAME_RE = re.compile(
    r"(?:LICEN[CS]E|COPYING)(?:[-.].*)?$"
    r"|(?:REUSE\.toml|\.git|\.hgtags)$"
    r"|.*(?:\.license|\.spdx(?:\.(?:rdf|json|xml|ya?ml))?)$"
    r"|CAL-1\.0(?:-Combined-Work-Exception)?(?:\..+)?$"
    r"|SHL-2\.1(?:\..+)?$"
)


def git_paths(*args):
    output = subprocess.check_output(["git", *args])
    return {os.fsdecode(path) for path in output.split(b"\0") if path}


def is_covered(path):
    parts = Path(path).parts
    directories = parts[:-1]
    return (
        not any(part in {".git", ".hg", ".sl", ".reuse", "LICENSES"} for part in directories)
        and not any(part == "subprojects" for part in directories[:-1])
        and not IGNORED_NAME_RE.fullmatch(parts[-1])
        and not os.path.islink(path)
        and os.path.isfile(path)
        and os.path.getsize(path) > 0
    )


def main(base):
    base = subprocess.check_output(
        ["git", "rev-parse", "--verify", "--end-of-options", f"{base}^{{commit}}"],
        text=True,
    ).strip()
    changed = git_paths(
        "diff", "--name-only", "--find-renames=100%", "--diff-filter=AMT",
        "-z", base, "HEAD", "--",
    )
    year = datetime.now(timezone.utc).year
    failed = False

    for path in sorted(changed):
        if not is_covered(path):
            continue
        with open(path, "r", encoding="utf-8-sig", errors="replace") as source:
            text = source.read(2048)
        for match in COPYRIGHT_RE.finditer(IGNORE_BLOCK_RE.sub("\n", text)):
            last_range = list(YEAR_RE.finditer(match.group("years")))[-1]
            start = int(last_range.group(1))
            end = last_range.group(2)
            last_year = int(end) if end else start
            if end and len(end) == 2:
                last_year += start // 100 * 100
                if last_year < start:
                    last_year += 100
            if last_year != year:
                print(f"{path}: copyright year must end in {year}")
                failed = True
                break

    return int(failed)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: check-copyright-year.py BASE_REVISION")
    raise SystemExit(main(sys.argv[1]))