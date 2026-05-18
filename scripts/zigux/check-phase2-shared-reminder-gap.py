#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

NOTE_RELATIVE = Path("Documentation/zigux/phase2-shared-reminder-gap.md")

REQUIRED_MARKERS = (
    "# Phase 2 Shared Reminder Gap",
    "## Remaining same-lane drift",
    "## Current direct packet",
    "## Historical packet members",
    "## Alignment nuance",
    "## Close condition",
    "Those four shared reminder surfaces still need the same narrowing pass before Lane 25 can close.",
    "`scripts/zigux/check-phase2-shared-reminder-gap.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "Treat those closure-side, validator-first, cross-route, toolchain-helper, make-wrapper, and missing-fixture names as historical packet members until current `master` rematerializes them.",
    "Any final close-out pass needs to narrow all four together if Lane 25 is going to stay checker-backed.",
)

NOTE_TEXT = """# Phase 2 Shared Reminder Gap

This note records the remaining shared-surface Phase 2 drift after the current scripts-root packet was reread against `master`.

## Remaining same-lane drift

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`

Those four shared reminder surfaces still need the same narrowing pass before Lane 25 can close.

## Current direct packet

- `Documentation/zigux/phase2-shared-reminder-gap.md`
- `scripts/zigux/check-phase2-shared-reminder-gap.py`
- `scripts/zigux/README.md`
- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `scripts/zigux/check-phase2-kbuild-routes.py`
- `scripts/zigux/check-phase2-toolchain-pinning.py`
- `scripts/zigux/fixdep.zig`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `zigux/tests/fixtures/phase2_tool_manifest.json`

Treat that set as the current directly readable Phase 2 reminder packet on `master`.

## Historical packet members

- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `Documentation/zigux/phase2-closure.md`
- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `scripts/zigux/check-phase2-cross.py`
- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `scripts/zigux/genksyms.zig`
- `scripts/zigux/genksyms_crc.zig`
- `scripts/zigux/mk_elfconfig.zig`
- `zigux/Makefile`
- `zigux/tests/fixtures/phase2_cross_targets.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
- `make -C zigux phase2-toolchain`
- `make -C zigux phase2-validate`
- `make -C zigux phase2-tools`
- `make -C zigux phase2-kconfig`
- `make -C zigux phase2-cross`
- `make -C zigux phase2`

Treat those closure-side, validator-first, cross-route, toolchain-helper, make-wrapper, and missing-fixture names as historical packet members until current `master` rematerializes them.

## Alignment nuance

The narrow `scripts/zigux/README.md` summary already describes the current scripts-root packet, but these four shared reminder surfaces still overstate the older Phase 2 closure stack or broader pre-narrowing packet:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`

Any final close-out pass needs to narrow all four together if Lane 25 is going to stay checker-backed.

## Close condition

Lane 25 closes when `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase2-tests-readme-alignment.py` describe and guard the same current direct packet and the same historical packet members captured here while staying aligned with the already-narrowed scripts-root reminder in `scripts/zigux/README.md`.
"""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def collect_issues(root: Path) -> list[str]:
    text = read_text(root / NOTE_RELATIVE)
    return [marker for marker in REQUIRED_MARKERS if marker not in text]


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p2_shared_gap_") as tmp_dir:
        root = Path(tmp_dir)
        write_text(root / NOTE_RELATIVE, NOTE_TEXT)
        assert collect_issues(root) == []
        checks_run += 1
        (root / NOTE_RELATIVE).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing note did not abort")
    print("PHASE2_SHARED_REMINDER_GAP_SELF_TEST=pass")
    print(f"PHASE2_SHARED_REMINDER_GAP_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Keep the bounded Lane 25 shared Phase 2 reminder gap explicit.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root)
    if issues:
        print("PHASE2_SHARED_REMINDER_GAP=fail")
        print("MISSING_MARKERS_START")
        for issue in issues:
            print(issue)
        print("MISSING_MARKERS_END")
        return 1
    print("PHASE2_SHARED_REMINDER_GAP=pass")
    print(f"PHASE2_SHARED_REMINDER_GAP_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
