#!/usr/bin/env python3
"""Track the remaining follow-up after the Phase 13 shared-summary guard landed."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


REQUIRED_MARKERS = {
    "Documentation/zigux/phase13-shared-summary-guard-gap.md": [
        "This note records the closure of the old missing-checker gap.",
        "The shipped guard is `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`.",
        "The remaining follow-up is broader README and tests-root packet refresh work, not another missing guard.",
    ],
    "Documentation/zigux/phase13-contributor-workflow-guide.md": [
        "stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
    ],
}

FORBIDDEN_MARKERS = (
    "missing guard path: `scripts/zigux/check-phase13-shared-summary-surfaces.py`",
    "`scripts/zigux/check-phase13-shared-summary-surfaces.py` is still absent on current `master`",
)


def read_text(root: Path, relpath: str) -> str:
    path = root / relpath
    if not path.exists():
        raise SystemExit(f"required file missing: {relpath}")
    return path.read_text(encoding="utf-8")


def write_text(root: Path, relpath: str, content: str) -> None:
    path = root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    if not (root / "scripts/zigux/check-phase13-shared-summary-surfaces.py").exists():
        issues.append("missing_file:scripts/zigux/check-phase13-shared-summary-surfaces.py")

    for relpath, markers in REQUIRED_MARKERS.items():
        try:
            text = read_text(root, relpath)
        except SystemExit as exc:
            issues.append(str(exc))
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing_marker:{relpath}:{marker}")
        for marker in FORBIDDEN_MARKERS:
            if marker in text:
                issues.append(f"forbidden_marker:{relpath}:{marker}")

    return issues


def populate_repo(root: Path) -> None:
    write_text(
        root,
        "scripts/zigux/check-phase13-shared-summary-surfaces.py",
        "#!/usr/bin/env python3\nprint('placeholder')\n",
    )
    for relpath, markers in REQUIRED_MARKERS.items():
        write_text(root, relpath, "\n".join(markers) + "\n")


def run_self_test() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix="phase13-shared-summary-guard-gap-"))
    checks_run = 0
    try:
        populate_repo(tempdir)
        assert collect_issues(tempdir) == []
        checks_run += 1

        (tempdir / "scripts/zigux/check-phase13-shared-summary-surfaces.py").unlink()
        issues = collect_issues(tempdir)
        assert "missing_file:scripts/zigux/check-phase13-shared-summary-surfaces.py" in issues
        populate_repo(tempdir)
        checks_run += 1

        gap_path = tempdir / "Documentation/zigux/phase13-shared-summary-guard-gap.md"
        gap_path.write_text(
            gap_path.read_text(encoding="utf-8")
            + "missing guard path: `scripts/zigux/check-phase13-shared-summary-surfaces.py`\n",
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "forbidden_marker:Documentation/zigux/phase13-shared-summary-guard-gap.md:missing guard path: `scripts/zigux/check-phase13-shared-summary-surfaces.py`"
            in issues
        )
        checks_run += 1
    finally:
        shutil.rmtree(tempdir)

    print("PHASE13_SHARED_SUMMARY_GUARD_GAP_SELF_TEST=pass")
    print(f"PHASE13_SHARED_SUMMARY_GUARD_GAP_SELF_TEST_CASES={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 13 shared-summary handoff note honest after the guard landed."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.repo_root)
    if issues:
        print("PHASE13_SHARED_SUMMARY_GUARD_GAP=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE13_SHARED_SUMMARY_GUARD_GAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())