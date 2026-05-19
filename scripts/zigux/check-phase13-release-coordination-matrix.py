#!/usr/bin/env python3
"""Guard the shipped Phase 13 release coordination matrix packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


RELEASE_MATRIX = Path("Documentation/zigux/phase13-release-coordination-matrix.md")

REQUIRED_TEXT = (
    "# Phase 13 Release Coordination Matrix",
    "shared-summary owner: `PMO / Release Management`",
    "workflow companion: `Documentation/zigux/phase13-contributor-workflow-guide.md`",
    "sequencing companion: `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`",
    "shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
    "Keep the Makefile-backed route family recorded as repo-reality gaps until current `master` rematerializes the shared build handle.",
    "The active shared packet stays contributor-facing and review-first. Helper-local proof remains owned by the `libfs`, `devres`, and `landlock` packets, while notifier evidence stays adjacent release-surface support through `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h`.",
    "- PMO / Release Management: keep this matrix, the workflow guide, the sequencing note, and the shared-summary guard aligned",
    "- adjacent notifier support: keep `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h` truthful as support evidence without promoting them into a fifth helper lane",
    "1. `Documentation/zigux/phase13-contributor-workflow-guide.md`",
    "2. `Documentation/zigux/phase13-release-coordination-matrix.md`",
    "3. `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`",
    "4. `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
    "- `make -C zigux phase13-validate`",
    "- `make -C zigux phase13`",
    "- `scripts/zigux/validate-phase13-release.py`",
    "- `scripts/zigux/check-phase13-devres-packet-alignment.py`",
    "- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
    "- `scripts/zigux/check-phase13-notifier-priority-signal.py`",
    "3. keep the Makefile-backed route family recorded as repo-reality gaps while distinguishing the returned `zigux/Makefile` file from the still-missing Phase 13 routes",
    "4. leave broader README or tests-root packet refresh for a separate same-lane step when a fresh reread proves a new reminder-surface drift",
    "This matrix does not imply a shipped Makefile-backed review handle.",
)

FORBIDDEN_TEXT = (
    "stable contributor-facing handle",
    "`zigux/Makefile` itself is the shared build handle",
    "The active shared packet stays build-first",
    "adjacent notifier support: keep `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/notifier_chain_view.zig`, `drivers/tty/hvc/hvc_console.h`",
    "Current `master` rematerializes `make -C zigux phase13-validate`",
    "This matrix implies a shipped Makefile-backed review handle.",
)


def read_text(root: Path, relpath: Path) -> str:
    path = root / relpath
    if not path.exists():
        raise SystemExit(f"required file missing: {relpath.as_posix()}")
    return path.read_text(encoding="utf-8")


def write_text(root: Path, relpath: Path, content: str) -> None:
    path = root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[str]:
    text = read_text(root, RELEASE_MATRIX)
    issues: list[str] = []
    for marker in REQUIRED_TEXT:
        if marker not in text:
            issues.append(f"missing_marker:{marker}")
    for marker in FORBIDDEN_TEXT:
        if marker in text:
            issues.append(f"forbidden_marker:{marker}")
    return issues


def emit_issues(issues: list[str]) -> int:
    print("PHASE13_RELEASE_COORDINATION_MATRIX=fail")
    print("PHASE13_RELEASE_COORDINATION_MATRIX_ISSUES_START")
    for issue in issues:
        print(issue)
    print("PHASE13_RELEASE_COORDINATION_MATRIX_ISSUES_END")
    return 1


def populate_repo(root: Path) -> None:
    write_text(root, RELEASE_MATRIX, "\n".join(REQUIRED_TEXT) + "\n")


def run_self_test() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix="phase13-release-coordination-matrix-"))
    checks_run = 0
    try:
        populate_repo(tempdir)
        assert collect_issues(tempdir) == []
        checks_run += 1

        matrix_path = tempdir / RELEASE_MATRIX
        matrix_path.write_text(
            matrix_path.read_text(encoding="utf-8").replace(REQUIRED_TEXT[6] + "\n", "", 1),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert f"missing_marker:{REQUIRED_TEXT[6]}" in issues
        populate_repo(tempdir)
        checks_run += 1

        matrix_path.write_text(
            matrix_path.read_text(encoding="utf-8").replace(REQUIRED_TEXT[18] + "\n", "", 1),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert f"missing_marker:{REQUIRED_TEXT[18]}" in issues
        populate_repo(tempdir)
        checks_run += 1

        matrix_path.write_text(
            matrix_path.read_text(encoding="utf-8") + FORBIDDEN_TEXT[0] + "\n",
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert f"forbidden_marker:{FORBIDDEN_TEXT[0]}" in issues
        populate_repo(tempdir)
        checks_run += 1

        matrix_path.write_text(
            matrix_path.read_text(encoding="utf-8") + FORBIDDEN_TEXT[-1] + "\n",
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert f"forbidden_marker:{FORBIDDEN_TEXT[-1]}" in issues
        populate_repo(tempdir)
        checks_run += 1

        matrix_path.unlink()
        try:
            collect_issues(tempdir)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing release matrix did not abort")
    finally:
        shutil.rmtree(tempdir)

    print("PHASE13_RELEASE_COORDINATION_MATRIX_SELF_TEST=pass")
    print(f"PHASE13_RELEASE_COORDINATION_MATRIX_SELF_TEST_CASES={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shipped Phase 13 release coordination matrix aligned."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.repo_root)
    if issues:
        return emit_issues(issues)

    print("PHASE13_RELEASE_COORDINATION_MATRIX=pass")
    print(f"PHASE13_RELEASE_COORDINATION_MATRIX_MARKER_COUNT={len(REQUIRED_TEXT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
