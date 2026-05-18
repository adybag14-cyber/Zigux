#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()
FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
STUDY_ONLY_ACCOUNTING_PATH = "Documentation/zigux/phase15-study-only-anchor-accounting.md"


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / FREEZE_MAP_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

FREEZE_MAP_REQUIRED_MARKERS = [
    "# Zigux Freeze Map",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
    "`Documentation/zigux/README.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/README.md`",
    "`samples/zigux/README.md`",
    "`zigux/tests/README.md`",
    "`scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`",
    "`scripts/zigux/check-phase9-trace-events-runtime-packet.py`",
    "`scripts/zigux/check-phase9-freeze-map-study-boundaries.py`",
    "`samples/zigux/runtime_trace_events.zig`",
    "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
    "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
    "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
    "`Documentation/zigux/phase9-runtime-loader-gap-survey.md`",
    "`zigux/tests/runtime_loader_gap_manifest.json`",
    "`zigux/tests/runtime_loader_gap_survey.zig`",
    "`zigux/Makefile` explicit only as a readable non-owner surface whose live body still lacks dedicated `phase9-*` runtime-pilot routes",
]

STUDY_ONLY_ACCOUNTING_REQUIRED_MARKERS = [
    "# Phase 15 Study-Only Anchor Accounting",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "`study_only`",
    "tracked outside the freeze-in-C scorecard",
    "this note is an inventory and handoff surface, not an approval record",
    "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in [FREEZE_MAP_PATH, STUDY_ONLY_ACCOUNTING_PATH]:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    freeze_map = read_text(root, FREEZE_MAP_PATH)
    for marker in FREEZE_MAP_REQUIRED_MARKERS:
        if marker not in freeze_map:
            failures.append(f"missing_marker:{FREEZE_MAP_PATH}:{marker}")

    study_only_accounting = read_text(root, STUDY_ONLY_ACCOUNTING_PATH)
    for marker in STUDY_ONLY_ACCOUNTING_REQUIRED_MARKERS:
        if marker not in study_only_accounting:
            failures.append(f"missing_marker:{STUDY_ONLY_ACCOUNTING_PATH}:{marker}")

    return failures


def build_freeze_map_fixture_text() -> str:
    return """# Zigux Freeze Map

- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`
- shared reminder surfaces that summarize freeze posture must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- shared Phase 9 runtime-pilot freeze-boundary packet must keep `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, and `scripts/zigux/check-phase9-freeze-map-study-boundaries.py` explicit together beside `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`, keep `zigux/Makefile` explicit only as a readable non-owner surface whose live body still lacks dedicated `phase9-*` runtime-pilot routes, and treat `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_manifest.json`, and `zigux/tests/runtime_loader_gap_survey.zig` as historical blocked-boundary vocabulary unless a fresh repo reread proves they returned
"""


def build_study_only_accounting_fixture_text() -> str:
    return """# Phase 15 Study-Only Anchor Accounting

- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`
- posture: `study_only`
- current Phase 15 role: tracked outside the freeze-in-C scorecard

## Accounting Rules

- this note is an inventory and handoff surface, not an approval record
- if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it
"""


def seed_fixture_tree(base: Path) -> None:
    write_text(base / FREEZE_MAP_PATH, build_freeze_map_fixture_text())
    write_text(base / STUDY_ONLY_ACCOUNTING_PATH, build_study_only_accounting_fixture_text())


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-freeze-map-study-boundaries-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for marker in FREEZE_MAP_REQUIRED_MARKERS:
            seed_fixture_tree(base)
            write_text(base / FREEZE_MAP_PATH, build_freeze_map_fixture_text().replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{FREEZE_MAP_PATH}:{marker}")

        for marker in STUDY_ONLY_ACCOUNTING_REQUIRED_MARKERS:
            seed_fixture_tree(base)
            write_text(
                base / STUDY_ONLY_ACCOUNTING_PATH,
                build_study_only_accounting_fixture_text().replace(marker, "", 1),
            )
            expect_failure(base, f"missing_marker:{STUDY_ONLY_ACCOUNTING_PATH}:{marker}")

        for rel_path in [FREEZE_MAP_PATH, STUDY_ONLY_ACCOUNTING_PATH]:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_FREEZE_MAP_STUDY_BOUNDARIES_SELF_TEST=pass")
    print(f"PHASE9_FREEZE_MAP_MARKER_COUNT={len(FREEZE_MAP_REQUIRED_MARKERS)}")
    print(f"PHASE15_STUDY_ONLY_ACCOUNTING_MARKER_COUNT={len(STUDY_ONLY_ACCOUNTING_REQUIRED_MARKERS)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the Phase 9 freeze-map boundary packet keeps the study-only anchors, "
            "shared runtime-trace-events reminder surfaces, and Phase 15 study-only accounting "
            "note explicit together."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE9_FREEZE_MAP_STUDY_BOUNDARIES_ERROR={failure}")
        return 1

    print(f"PHASE9_FREEZE_MAP_MARKER_COUNT={len(FREEZE_MAP_REQUIRED_MARKERS)}")
    print(f"PHASE15_STUDY_ONLY_ACCOUNTING_MARKER_COUNT={len(STUDY_ONLY_ACCOUNTING_REQUIRED_MARKERS)}")
    print("PHASE9_FREEZE_MAP_STUDY_BOUNDARIES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
