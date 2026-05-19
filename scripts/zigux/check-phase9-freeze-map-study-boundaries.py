#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()
FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
STUDY_ONLY_ACCOUNTING_PATH = "Documentation/zigux/phase15-study-only-anchor-accounting.md"
LANE_SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
SAMPLES_README_PATH = "samples/zigux/README.md"


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
    "PHASE15_STATUS=study_only_accounting_slice_landed",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "`study_only`",
    "tracked outside the freeze-in-C scorecard",
    "this note is an inventory and handoff surface, not an approval record",
    "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
    "the freeze-map governance note, the parity scorecard, the handoff-next-steps survey, and the shared-summary gap note",
    "boundary-study target first, not a rewrite target",
    "remain future-only and not current product claims",
    "no Architecture Council approval is currently recorded for a deep-core status change",
    "a direct Zigux bridge for `kernel/workqueue.c`",
    "a direct Zigux bridge for `kernel/trace/ring_buffer.c`",
    "any future status-bucket change for either anchor must update the freeze map, the Phase 15 governance note, the parity scorecard, and this study-only accounting note together",
]

LANE_SEQUENCING_REQUIRED_MARKERS = [
    "keep the freeze-map study-only anchors explicit through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain cautionary non-owner context rather than proof of runtime-substrate or bridge readiness",
    "Keep `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` framed as freeze-map study-only anchors, and route that shared anchor inventory back through `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
]

SCRIPTS_README_REQUIRED_MARKERS = [
    "keep the freeze-map boundary explicit too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues",
]

SAMPLES_README_REQUIRED_MARKERS = [
    "Do not widen this lane into runtime-loader, module-registration, procfs, sysfs, user-copy, workqueue, ring-buffer, or other runtime-substrate claims.",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in [
        FREEZE_MAP_PATH,
        STUDY_ONLY_ACCOUNTING_PATH,
        LANE_SEQUENCING_PATH,
        SCRIPTS_README_PATH,
        SAMPLES_README_PATH,
    ]:
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

    lane_sequencing = read_text(root, LANE_SEQUENCING_PATH)
    for marker in LANE_SEQUENCING_REQUIRED_MARKERS:
        if marker not in lane_sequencing:
            failures.append(f"missing_marker:{LANE_SEQUENCING_PATH}:{marker}")

    scripts_readme = read_text(root, SCRIPTS_README_PATH)
    for marker in SCRIPTS_README_REQUIRED_MARKERS:
        if marker not in scripts_readme:
            failures.append(f"missing_marker:{SCRIPTS_README_PATH}:{marker}")

    samples_readme = read_text(root, SAMPLES_README_PATH)
    for marker in SAMPLES_README_REQUIRED_MARKERS:
        if marker not in samples_readme:
            failures.append(f"missing_marker:{SAMPLES_README_PATH}:{marker}")

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

- `PHASE15_STATUS=study_only_accounting_slice_landed`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`
- posture: `study_only`
- current Phase 15 role: tracked outside the freeze-in-C scorecard
- current companions: the freeze-map governance note, the parity scorecard, the handoff-next-steps survey, and the shared-summary gap note
- roadmap reason: boundary-study target first, not a rewrite target
- speculative direct ports remain future-only and not current product claims
- no Architecture Council approval is currently recorded for a deep-core status change

## Accounting Rules

- this note is an inventory and handoff surface, not an approval record
- if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it
- any future status-bucket change for either anchor must update the freeze map, the Phase 15 governance note, the parity scorecard, and this study-only accounting note together

## Non-Goals

- a direct Zigux bridge for `kernel/workqueue.c`
- a direct Zigux bridge for `kernel/trace/ring_buffer.c`
"""


def build_lane_sequencing_fixture_text() -> str:
    return """# Phase 9 Runtime Pilot Lane Sequencing

- keep the freeze-map study-only anchors explicit through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain cautionary non-owner context rather than proof of runtime-substrate or bridge readiness
- Keep `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` framed as freeze-map study-only anchors, and route that shared anchor inventory back through `Documentation/zigux/phase15-study-only-anchor-accounting.md`
"""


def build_scripts_readme_fixture_text() -> str:
    return """# scripts/zigux

- keep the freeze-map boundary explicit too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues
"""


def build_samples_readme_fixture_text() -> str:
    return """# samples/zigux

- Do not widen this lane into runtime-loader, module-registration, procfs, sysfs, user-copy, workqueue, ring-buffer, or other runtime-substrate claims.
"""


def seed_fixture_tree(base: Path) -> None:
    write_text(base / FREEZE_MAP_PATH, build_freeze_map_fixture_text())
    write_text(base / STUDY_ONLY_ACCOUNTING_PATH, build_study_only_accounting_fixture_text())
    write_text(base / LANE_SEQUENCING_PATH, build_lane_sequencing_fixture_text())
    write_text(base / SCRIPTS_README_PATH, build_scripts_readme_fixture_text())
    write_text(base / SAMPLES_README_PATH, build_samples_readme_fixture_text())


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
            current = build_freeze_map_fixture_text()
            if current.count(marker) != 1:
                continue
            write_text(base / FREEZE_MAP_PATH, current.replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{FREEZE_MAP_PATH}:{marker}")

        for marker in STUDY_ONLY_ACCOUNTING_REQUIRED_MARKERS:
            seed_fixture_tree(base)
            current = build_study_only_accounting_fixture_text()
            if current.count(marker) != 1:
                continue
            write_text(base / STUDY_ONLY_ACCOUNTING_PATH, current.replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{STUDY_ONLY_ACCOUNTING_PATH}:{marker}")

        for marker in LANE_SEQUENCING_REQUIRED_MARKERS:
            seed_fixture_tree(base)
            current = build_lane_sequencing_fixture_text()
            if current.count(marker) != 1:
                continue
            write_text(base / LANE_SEQUENCING_PATH, current.replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{LANE_SEQUENCING_PATH}:{marker}")

        for marker in SCRIPTS_README_REQUIRED_MARKERS:
            seed_fixture_tree(base)
            current = build_scripts_readme_fixture_text()
            if current.count(marker) != 1:
                continue
            write_text(base / SCRIPTS_README_PATH, current.replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{SCRIPTS_README_PATH}:{marker}")

        for marker in SAMPLES_README_REQUIRED_MARKERS:
            seed_fixture_tree(base)
            current = build_samples_readme_fixture_text()
            if current.count(marker) != 1:
                continue
            write_text(base / SAMPLES_README_PATH, current.replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{SAMPLES_README_PATH}:{marker}")

        for rel_path in [
            FREEZE_MAP_PATH,
            STUDY_ONLY_ACCOUNTING_PATH,
            LANE_SEQUENCING_PATH,
            SCRIPTS_README_PATH,
            SAMPLES_README_PATH,
        ]:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_FREEZE_MAP_STUDY_BOUNDARIES_SELF_TEST=pass")
    print(f"PHASE9_FREEZE_MAP_MARKER_COUNT={len(FREEZE_MAP_REQUIRED_MARKERS)}")
    print(f"PHASE15_STUDY_ONLY_ACCOUNTING_MARKER_COUNT={len(STUDY_ONLY_ACCOUNTING_REQUIRED_MARKERS)}")
    print(f"PHASE9_LANE_SEQUENCING_MARKER_COUNT={len(LANE_SEQUENCING_REQUIRED_MARKERS)}")
    print(f"PHASE9_SCRIPTS_README_MARKER_COUNT={len(SCRIPTS_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_SAMPLES_README_MARKER_COUNT={len(SAMPLES_README_REQUIRED_MARKERS)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the Phase 9 freeze-map boundary packet keeps the study-only anchors, "
            "shared runtime-trace-events reminder surfaces, and the fuller Phase 15 study-only "
            "accounting posture explicit together."
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
    print(f"PHASE9_LANE_SEQUENCING_MARKER_COUNT={len(LANE_SEQUENCING_REQUIRED_MARKERS)}")
    print(f"PHASE9_SCRIPTS_README_MARKER_COUNT={len(SCRIPTS_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_SAMPLES_README_MARKER_COUNT={len(SAMPLES_README_REQUIRED_MARKERS)}")
    print("PHASE9_FREEZE_MAP_STUDY_BOUNDARIES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
