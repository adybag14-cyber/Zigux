#!/usr/bin/env python3
"""Keep the Phase 13 shared-summary handoff note aligned with current reminder state."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


REQUIRED_MARKERS = {
    "Documentation/zigux/phase13-shared-summary-guard-gap.md": [
        "This note records the closure of the old missing-checker gap.",
        "The shipped guard is `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`.",
        "- companion handoff check: `python3 scripts/zigux/check-phase13-shared-summary-guard-gap.py`",
        "The remaining follow-up is now narrower than the old missing-checker gap and no longer includes the earlier tests-root release-validator undercount.",
        "Fresh authenticated file checks in this run also show the scripts-root Phase 13 reminder is now the only remaining broader shared-surface drift.",
        "Current `master` already keeps the tests-root README and its dedicated checker aligned around `scripts/zigux/validate-phase13-release.py`",
        "- `Documentation/zigux/phase13-release-notes-survey.md`",
        "`scripts/zigux/README.md`",
        "`zigux/tests/README.md`",
    ],
    "Documentation/zigux/phase13-contributor-workflow-guide.md": [
        "stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
    ],
}

FORBIDDEN_MARKERS = (
    "missing guard path: `scripts/zigux/check-phase13-shared-summary-surfaces.py`",
    "`scripts/zigux/check-phase13-shared-summary-surfaces.py` is still absent on current `master`",
    "The remaining follow-up is broader README and tests-root packet refresh work, not another missing guard.",
    "That closes the older scripts-root reminder gap too, so the next same-lane follow-through should stay parked until a fresh reread identifies a new one-file drift across the broader Phase 13 reminder packet.",
    "zigux/tests/README.md still needs the returned `scripts/zigux/validate-phase13-release.py` kept explicit as shipped release-discipline support",
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
        checks_run += 1

        populate_repo(tempdir)
        gap_path = tempdir / "Documentation/zigux/phase13-shared-summary-guard-gap.md"
        gap_path.write_text(
            gap_path.read_text(encoding="utf-8").replace(
                "The remaining follow-up is now narrower than the old missing-checker gap and no longer includes the earlier tests-root release-validator undercount.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "missing_marker:Documentation/zigux/phase13-shared-summary-guard-gap.md:The remaining follow-up is now narrower than the old missing-checker gap and no longer includes the earlier tests-root release-validator undercount."
            in issues
        )
        checks_run += 1

        populate_repo(tempdir)
        gap_path = tempdir / "Documentation/zigux/phase13-shared-summary-guard-gap.md"
        gap_path.writeText = None
        gap_path.write_text(
            gap_path.read_text(encoding="utf-8").replace(
                "Fresh authenticated file checks in this run also show the scripts-root Phase 13 reminder is now the only remaining broader shared-surface drift.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "missing_marker:Documentation/zigux/phase13-shared-summary-guard-gap.md:Fresh authenticated file checks in this run also show the scripts-root Phase 13 reminder is now the only remaining broader shared-surface drift."
            in issues
        )
        checks_run += 1

        populate_repo(tempdir)
        gap_path = tempdir / "Documentation/zigux/phase13-shared-summary-guard-gap.md"
        gap_path.write_text(
            gap_path.read_text(encoding="utf-8")
            + "That closes the older scripts-root reminder gap too, so the next same-lane follow-through should stay parked until a fresh reread identifies a new one-file drift across the broader Phase 13 reminder packet.\n",
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "forbidden_marker:Documentation/zigux/phase13-shared-summary-guard-gap.md:That closes the older scripts-root reminder gap too, so the next same-lane follow-through should stay parked until a fresh reread identifies a new one-file drift across the broader Phase 13 reminder packet."
            in issues
        )
        checks_run += 1

        populate_repo(tempdir)
        gap_path = tempdir / "Documentation/zigux/phase13-shared-summary-guard-gap.md"
        gap_path.write_text(
            gap_path.read_text(encoding="utf-8")
            + "zigux/tests/README.md still needs the returned `scripts/zigux/validate-phase13-release.py` kept explicit as shipped release-discipline support\n",
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "forbidden_marker:Documentation/zigux/phase13-shared-summary-guard-gap.md:zigux/tests/README.md still needs the returned `scripts/zigux/validate-phase13-release.py` kept explicit as shipped release-discipline support"
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
        print("PHASE13_SHARED_SUMMARY_GUARD_GAP_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE13_SHARED_SUMMARY_GUARD_GAP_ISSUES_END")
        return 1

    print("PHASE13_SHARED_SUMMARY_GUARD_GAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
