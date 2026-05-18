#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / "Documentation" / "zigux" / "phase2-shared-reminder-gap.md"
DOCS_README = ROOT / "Documentation" / "zigux" / "README.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
TESTS_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"

NOTE_MARKERS = (
    "# Phase 2 Shared Reminder Gap",
    "## Shared surfaces now aligned",
    "Those four shared reminder surfaces now agree on the same current Phase 2 packet and the same remaining historical packet members.",
    "## Current shared packet",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "Treat that set as the current shared Phase 2 reminder packet already aligned across the docs-root, checklist, tests-root, and scripts-root surfaces.",
    "## Remaining historical packet members",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "## Remaining same-lane work",
    "`Documentation/zigux/phase2-scripts-surface-reconciliation.md`",
    "`Documentation/zigux/artifact-diff.md`",
    "`zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`",
    "The remaining Lane 25 work is no longer another four-surface narrowing pass.",
    "## Close condition",
)

FILE_MARKERS = {
    DOCS_README: (
        "`scripts/zigux/check-phase2-required-make-routes.py`",
        "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
        "repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    ),
    REVIEW_CHECKLIST: (
        "`scripts/zigux/check-phase2-required-make-routes.py`",
        "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
        "`scripts/zigux/validate-phase2-closure.py`",
        "`scripts/zigux/install-zig.py`",
        "`scripts/zigux/check-phase2-cross.py`",
        "`zigux/tests/fixtures/phase2_cross_targets.json`",
    ),
    TESTS_README: (
        "the current directly readable Phase 2 packet is the scripts-root kbuild, toolchain-pinning, toolchain pin-scope, cross-selftest, docs-shared-reminder, required-make-route, and toolchain reminder set plus the live kconfig bridge helpers, the restored closure-side note and validator entrypoint, the shipped `zigux/Makefile` wrappers, and their fixture roster",
        "repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    ),
    TESTS_CHECKER: (
        "the current directly readable Phase 2 packet is the scripts-root kbuild, toolchain-pinning, toolchain pin-scope, cross-selftest, docs-shared-reminder, required-make-route, and toolchain reminder set plus the live kconfig bridge helpers, the restored closure-side note and validator entrypoint, the shipped `zigux/Makefile` wrappers, and their fixture roster",
        "repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    ),
    SCRIPTS_README: (
        "`scripts/zigux/check-phase2-required-make-routes.py`",
        "`Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-validate`, `make -C zigux phase2`, and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the shipped closure-side reminder, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set",
        "repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    ),
}

SYNTHETIC_NOTE = """# Phase 2 Shared Reminder Gap

## Shared surfaces now aligned

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`

Those four shared reminder surfaces now agree on the same current Phase 2 packet and the same remaining historical packet members.

## Current shared packet

- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `Documentation/zigux/phase2-closure.md`
- `scripts/zigux/check-phase2-required-make-routes.py`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`

Treat that set as the current shared Phase 2 reminder packet already aligned across the docs-root, checklist, tests-root, and scripts-root surfaces.

## Remaining historical packet members

- `scripts/zigux/validate-phase2-closure.py`
- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-phase2-cross.py`
- `zigux/tests/fixtures/phase2_cross_targets.json`

## Remaining same-lane work

- `Documentation/zigux/phase2-scripts-surface-reconciliation.md`
- `Documentation/zigux/artifact-diff.md`
- `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`

The remaining Lane 25 work is no longer another four-surface narrowing pass.

## Close condition
"""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve(root: Path, path: Path) -> Path:
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        rel = path
    return root / rel


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    note_text = read_text(resolve(root, NOTE))
    for marker in NOTE_MARKERS:
        if marker not in note_text:
            issues.append(("MISSING_NOTE_MARKERS", marker))
    for path, markers in FILE_MARKERS.items():
        text = read_text(resolve(root, path))
        for marker in markers:
            if marker not in text:
                issues.append(("MISSING_ALIGNMENT_MARKERS", f"{path.relative_to(ROOT)}::{marker}"))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_SHARED_REMINDER_GAP=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(resolve(root, NOTE), SYNTHETIC_NOTE)
    for path, markers in FILE_MARKERS.items():
        write_text(resolve(root, path), "\n".join(markers) + "\n")


def remove_marker(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(NOTE_MARKERS) + sum(len(v) for v in FILE_MARKERS.values()) + 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_shared_gap_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in NOTE_MARKERS:
            build_self_test_root(root)
            path = resolve(root, NOTE)
            write_text(path, remove_marker(read_text(path), marker))
            issues = collect_issues(root)
            assert ("MISSING_NOTE_MARKERS", marker) in issues
            checks_run += 1

        for path, markers in FILE_MARKERS.items():
            for marker in markers:
                build_self_test_root(root)
                file_path = resolve(root, path)
                write_text(file_path, remove_marker(read_text(file_path), marker))
                issues = collect_issues(root)
                key = f"{path.relative_to(ROOT)}::{marker}"
                assert ("MISSING_ALIGNMENT_MARKERS", key) in issues
                checks_run += 1

        build_self_test_root(root)
        resolve(root, NOTE).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing note did not abort")

    assert checks_run == expected_case_count
    print("PHASE2_SHARED_REMINDER_GAP_SELF_TEST=pass")
    print(f"PHASE2_SHARED_REMINDER_GAP_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 25 shared-gap sidecar aligned to the now-harmonized Phase 2 shared reminder surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_SHARED_REMINDER_GAP=pass")
    print(f"PHASE2_SHARED_REMINDER_GAP_NOTE_MARKER_COUNT={len(NOTE_MARKERS)}")
    print(f"PHASE2_SHARED_REMINDER_GAP_ALIGNMENT_MARKER_COUNT={sum(len(v) for v in FILE_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
