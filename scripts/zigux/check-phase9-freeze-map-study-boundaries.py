#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()
FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
STUDY_ONLY_ACCOUNTING_PATH = "Documentation/zigux/phase15-study-only-anchor-accounting.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
DOCS_README_PATH = "Documentation/zigux/README.md"
LANE_SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
SAMPLES_README_PATH = "samples/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"


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
    "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
    "`zigux/tests/phase9_build.zig`",
    "`zigux/kernel/runtime_loader.zig`",
    "`zigux/kernel/runtime_loader_contract.zig`",
    "`samples/zigux/runtime_*_loader.zig`",
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

DOCS_README_REQUIRED_MARKERS = [
    "Phase 9 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md` - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` - `Documentation/zigux/review-checklist.md` - `Documentation/zigux/README.md` - `scripts/zigux/README.md` - `samples/zigux/README.md` - `zigux/tests/README.md` - `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py` - `scripts/zigux/check-phase9-freeze-map-study-boundaries.py` keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.",
    "keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues, and any shared reminder surface that summarizes them must route back through those two owner notes.",
]

REVIEW_CHECKLIST_REQUIRED_MARKERS = [
    "if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence?",
]

LANE_SEQUENCING_REQUIRED_MARKERS = [
    "keep the freeze-map study-only anchors explicit through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain cautionary non-owner context rather than proof of runtime-substrate or bridge readiness",
]

SCRIPTS_README_REQUIRED_MARKERS = [
    "keep the freeze-map boundary explicit too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues",
]

SAMPLES_README_REQUIRED_MARKERS = [
    "Keep that bitmap packet framed as a separate Phase 9 runtime reminder rather than as proof that the broader shared runtime-loader packet returned or as evidence that a fifth approved Phase 5 sample family landed here.",
]

TESTS_README_REQUIRED_MARKERS = [
    "Keep the current bounded Phase 15 governance reminder explicit through `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-parity-scorecard-survey.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase15-shared-summary-gap.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`.",
    "without implying any Architecture Council approval for a freeze-map status change",
]

WORKFLOW_REQUIRED_MARKERS = [
    "python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py --self-test",
    "python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py",
]

WORKFLOW_EXACT_ONCE_MARKERS = [
    "        run: python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py --self-test",
    "        run: python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py",
]

REQUIRED_MARKERS = {
    FREEZE_MAP_PATH: FREEZE_MAP_REQUIRED_MARKERS,
    STUDY_ONLY_ACCOUNTING_PATH: STUDY_ONLY_ACCOUNTING_REQUIRED_MARKERS,
    REVIEW_CHECKLIST_PATH: REVIEW_CHECKLIST_REQUIRED_MARKERS,
    DOCS_README_PATH: DOCS_README_REQUIRED_MARKERS,
    LANE_SEQUENCING_PATH: LANE_SEQUENCING_REQUIRED_MARKERS,
    SCRIPTS_README_PATH: SCRIPTS_README_REQUIRED_MARKERS,
    SAMPLES_README_PATH: SAMPLES_README_REQUIRED_MARKERS,
    TESTS_README_PATH: TESTS_README_REQUIRED_MARKERS,
    WORKFLOW_PATH: WORKFLOW_REQUIRED_MARKERS,
}

EXACT_ONCE_MARKERS = {
    WORKFLOW_PATH: WORKFLOW_EXACT_ONCE_MARKERS,
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_line_occurrences(content: str, marker: str) -> int:
    return sum(1 for line in content.splitlines() if line == marker)


def duplicate_marker_occurrence(content: str, marker: str) -> str:
    return content.replace(marker, f"{marker}\n{marker}", 1)


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_MARKERS:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")

    for rel_path, markers in EXACT_ONCE_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            count = count_exact_line_occurrences(text, marker)
            if count != 1:
                failures.append(f"expected_exact_once:{rel_path}:{marker}:count={count}")

    return failures


def build_fixture_text(rel_path: str) -> str:
    if rel_path == FREEZE_MAP_PATH:
        return """# Zigux Freeze Map

- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`
- shared reminder surfaces that summarize freeze posture must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- shared Phase 9 runtime-pilot freeze-boundary packet must keep `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, `scripts/zigux/check-phase9-freeze-map-study-boundaries.py`, `.github/workflows/zigux-bootstrap.yml`, `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` explicit together, keep `zigux/Makefile` explicit only as a readable non-owner surface whose live body still lacks dedicated `phase9-*` runtime-pilot routes, keep the returned shared runtime-loader allocator/init-flow packet explicit through `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_manifest.json`, `zigux/tests/runtime_loader_gap_survey.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/tests/phase9_build.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and the `samples/zigux/runtime_*_loader.zig` scaffolds, and must treat the still-missing broader shared `zigux/tests/runtime_*` replay family beyond the returned survey and allocator/init-flow packet, and blocked publication or install-root loader boundaries as historical blocked-boundary vocabulary unless a fresh repo reread proves they returned, so the surviving narrow trace-events packet and the neighboring returned loader packet do not imply that `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` has crossed the study-only boundary into delivery-ready runtime-substrate evidence
"""
    if rel_path == STUDY_ONLY_ACCOUNTING_PATH:
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
    if rel_path == DOCS_README_PATH:
        return """# Zigux Documentation

- Phase 9 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md` - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` - `Documentation/zigux/review-checklist.md` - `Documentation/zigux/README.md` - `scripts/zigux/README.md` - `samples/zigux/README.md` - `zigux/tests/README.md` - `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py` - `scripts/zigux/check-phase9-freeze-map-study-boundaries.py` keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.
- keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues, and any shared reminder surface that summarizes them must route back through those two owner notes.
"""
    if rel_path == REVIEW_CHECKLIST_PATH:
        return """# Zigux Review Checklist

- if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence?
"""
    if rel_path == LANE_SEQUENCING_PATH:
        return """# Phase 9 Runtime Pilot Lane Sequencing

- keep the freeze-map study-only anchors explicit through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain cautionary non-owner context rather than proof of runtime-substrate or bridge readiness
"""
    if rel_path == SCRIPTS_README_PATH:
        return """# scripts/zigux

- keep the freeze-map boundary explicit too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues
"""
    if rel_path == SAMPLES_README_PATH:
        return """# samples/zigux

- Keep that bitmap packet framed as a separate Phase 9 runtime reminder rather than as proof that the broader shared runtime-loader packet returned or as evidence that a fifth approved Phase 5 sample family landed here.
"""
    if rel_path == TESTS_README_PATH:
        return """# zigux/tests

Keep the current bounded Phase 15 governance reminder explicit through `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-parity-scorecard-survey.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase15-shared-summary-gap.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`.

Tests-root reviewer prompt:
- Does the bounded Phase 15 reminder keep the directly readable governance packet, the returned readiness and handoff survey packet members, the shared-summary gap note, the active-governance replay entrypoints, and the still-missing validator-first, route-level, and build-level surfaces aligned without promoting blocked governance wrappers or deeper-core status changes into current tests-root evidence without implying any Architecture Council approval for a freeze-map status change or a returned validator-first build packet?
"""
    if rel_path == WORKFLOW_PATH:
        return """name: zigux-bootstrap

jobs:
  bootstrap:
    steps:
      - name: Self-test current Phase 9 freeze-map study-boundaries checker
        run: python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py --self-test

      - name: Check current Phase 9 freeze-map study-boundaries packet
        run: python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py
"""
    raise ValueError(f"no fixture template for {rel_path}")


def seed_fixture_tree(base: Path) -> None:
    for rel_path in REQUIRED_MARKERS:
        write_text(base / rel_path, build_fixture_text(rel_path))


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

        for rel_path, markers in REQUIRED_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = build_fixture_text(rel_path)
                if current.count(marker) != 1:
                    continue
                write_text(base / rel_path, current.replace(marker, "", 1))
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for rel_path, markers in EXACT_ONCE_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = build_fixture_text(rel_path)
                write_text(base / rel_path, duplicate_marker_occurrence(current, marker))
                expect_failure(base, f"expected_exact_once:{rel_path}:{marker}:count=2")

        for rel_path in REQUIRED_MARKERS:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_FREEZE_MAP_STUDY_BOUNDARIES_SELF_TEST=pass")
    print(f"PHASE9_FREEZE_MAP_MARKER_COUNT={len(FREEZE_MAP_REQUIRED_MARKERS)}")
    print(f"PHASE15_STUDY_ONLY_ACCOUNTING_MARKER_COUNT={len(STUDY_ONLY_ACCOUNTING_REQUIRED_MARKERS)}")
    print(f"PHASE9_DOCS_README_STUDY_BOUNDARY_MARKER_COUNT={len(DOCS_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_STUDY_BOUNDARY_MARKER_COUNT={len(REVIEW_CHECKLIST_REQUIRED_MARKERS)}")
    print(f"PHASE9_LANE_SEQUENCING_MARKER_COUNT={len(LANE_SEQUENCING_REQUIRED_MARKERS)}")
    print(f"PHASE9_SCRIPTS_README_MARKER_COUNT={len(SCRIPTS_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_SAMPLES_README_MARKER_COUNT={len(SAMPLES_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_TESTS_README_MARKER_COUNT={len(TESTS_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_WORKFLOW_MARKER_COUNT={len(WORKFLOW_REQUIRED_MARKERS)}")
    print(
        "PHASE9_WORKFLOW_EXACT_ONCE_MARKER_COUNT="
        f"{sum(len(markers) for markers in EXACT_ONCE_MARKERS.values())}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the Phase 9 freeze-map boundary packet keeps the study-only anchors, "
            "the reviewer-facing checklist route-back wording, the shared runtime-trace-events "
            "reminder surfaces, the workflow coverage for this checker, and the fuller Phase 15 "
            "study-only accounting posture explicit together."
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
    print(f"PHASE9_DOCS_README_STUDY_BOUNDARY_MARKER_COUNT={len(DOCS_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_STUDY_BOUNDARY_MARKER_COUNT={len(REVIEW_CHECKLIST_REQUIRED_MARKERS)}")
    print(f"PHASE9_LANE_SEQUENCING_MARKER_COUNT={len(LANE_SEQUENCING_REQUIRED_MARKERS)}")
    print(f"PHASE9_SCRIPTS_README_MARKER_COUNT={len(SCRIPTS_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_SAMPLES_README_MARKER_COUNT={len(SAMPLES_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_TESTS_README_MARKER_COUNT={len(TESTS_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_WORKFLOW_MARKER_COUNT={len(WORKFLOW_REQUIRED_MARKERS)}")
    print(
        "PHASE9_WORKFLOW_EXACT_ONCE_MARKER_COUNT="
        f"{sum(len(markers) for markers in EXACT_ONCE_MARKERS.values())}"
    )
    print("PHASE9_FREEZE_MAP_STUDY_BOUNDARIES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
