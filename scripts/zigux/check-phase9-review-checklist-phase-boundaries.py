#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "Documentation/zigux/review-checklist.md").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
LANE_SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
MODULE_SLICE_PATH = "Documentation/zigux/phase9-runtime-trace-events-module-slice.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
SAMPLES_README_PATH = "samples/zigux/README.md"
MAKEFILE_PATH = "zigux/Makefile"

TRACE_EVENTS_PACKET_CHECKER_MARKER = "`scripts/zigux/check-phase9-trace-events-runtime-packet.py`"
PHASE9_BOUNDARY_CHECKER_MARKER = "`scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`"
PHASE2_CONF_BRIDGE_MARKER = "`scripts/zigux/kconfig/conf_bridge.zig`"
PHASE2_CONFDATA_BRIDGE_MARKER = "`scripts/zigux/kconfig/confdata_bridge.zig`"
PHASE3_EXPORTS_MARKER = "`rust/exports.c`"
PHASE3_EXPORT_SHIM_MARKER = "`zigux/kernel/export_shim.zig`"
PHASE2_BOUNDARY_MARKER = "remain Phase 2 config-surface bridge references"
PHASE3_BOUNDARY_MARKER = "remain Phase 3 export-boundary references rather than runtime-pilot evidence"

CHECKLIST_REQUIRED_MARKERS = [
    "if the change touches the shared Phase 9 runtime-pilot packet",
    "`samples/zigux/runtime_trace_events.zig`",
    "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
    "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
    "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
    ".provides_selftest_hook = true",
    "initialized, selftest_complete, and exited lifecycle tracking",
    "failed-exit rollback explicit after reusable selftest replay",
    "balanced registration re-entry companion that keeps function-thread registration reusable before and after selftest",
    "does not currently expose the broader shared runtime-loader packet",
    "`zigux/tests/phase9_build.zig` now stays explicit only as the returned narrow `phase9-runtime-atomic64-diff` build shard rooted in `zigux/tests/runtime_atomic64_diff.zig`",
    "`Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_survey.zig`, and `zigux/tests/phase9_build.zig` while `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, and `zigux/tests/runtime_bitmap_manifest.json` stay repo-reality gaps on the trusted contents path",
    TRACE_EVENTS_PACKET_CHECKER_MARKER,
    PHASE2_CONF_BRIDGE_MARKER,
    PHASE2_CONFDATA_BRIDGE_MARKER,
    PHASE3_EXPORTS_MARKER,
    PHASE3_EXPORT_SHIM_MARKER,
    PHASE2_BOUNDARY_MARKER,
    PHASE3_BOUNDARY_MARKER,
]

LANE_SEQUENCING_REQUIRED_MARKERS = [
    TRACE_EVENTS_PACKET_CHECKER_MARKER,
    "surviving direct runtime-module sample: `samples/zigux/runtime_trace_events.zig`",
    "`.provides_selftest_hook = true` together with initialized, selftest_complete, and exited lifecycle tracking",
    "surviving fail-closed runtime companion: `samples/zigux/runtime_trace_events_unregistered_gate.zig`",
    "surviving registration-reentry runtime companion: `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
    "balanced registration re-entry replay in `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` across both the initialized and selftest_complete stages",
    "the runtime bitmap side is narrower than older shared reminders claimed.",
    "current `master` therefore supports a partial runtime bitmap reminder packet plus a bounded build bundle, not a fully returned bitmap sample family",
    "does not currently expose the broader shared runtime-loader packet",
    "keep the freeze-map study-only anchors explicit through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain cautionary non-owner context rather than proof of runtime-substrate or bridge readiness",
    "Treat stale reminder overclaim as the active blocker before reopening checker-local or runtime-behavior work.",
]

MODULE_SLICE_REQUIRED_MARKERS = [
    TRACE_EVENTS_PACKET_CHECKER_MARKER,
    "`samples/zigux/runtime_trace_events.zig`",
    "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
    "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
    ".provides_selftest_hook = true",
    "initialized, selftest_complete, and exited lifecycle tracking",
    "The shipped cold-stage guard in `test \"trace-events sample keeps selftest replay-summary continuity explicit after direct pilot activity\"`",
    "Its paired initialized-direct-activity proof in `test \"phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest\"`",
    "sample-local pilot-module reviewability",
    "Current `master` does now expose `zigux/tests/phase9_build.zig`, but the live file is still a bounded shared Phase 9 build bundle: it keeps `phase9-runtime-atomic64-diff` rooted in `runtime_atomic64_diff.zig` and also names the separate bitmap-family rerun handles.",
    "Current `master` still keeps the separate Phase 9 runtime bitmap reminder packet visible through `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_survey.zig`, and the bounded `zigux/tests/phase9_build.zig` bundle, while `samples/zigux/runtime_bitmap_loader.zig` and the other direct bitmap sample-family files remain trusted-contents gaps.",
    "Do not invent `validate-phase9.py`",
    PHASE2_CONF_BRIDGE_MARKER,
    PHASE2_CONFDATA_BRIDGE_MARKER,
    PHASE3_EXPORTS_MARKER,
    PHASE3_EXPORT_SHIM_MARKER,
]

SCRIPTS_README_REQUIRED_MARKERS = [
    "Phase 9 flow - the current shared runtime-pilot packet is narrow and review-first",
    PHASE9_BOUNDARY_CHECKER_MARKER,
    TRACE_EVENTS_PACKET_CHECKER_MARKER,
    "`python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test`",
    "`python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test`",
    "`python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`",
    "`python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py`",
    "`samples/zigux/runtime_trace_events.zig`",
    "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
    "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
    "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
    ".provides_selftest_hook = true",
    "initialized, selftest_complete, and exited lifecycle tracking",
    "failed-exit rollback explicit after reusable selftest replay together with later post-exit invalid-lifecycle rejections",
    "keeps balanced function-thread registration reusable before and after selftest",
    "direct authenticated contents rereads still return missing for `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, and `zigux/tests/runtime_bitmap_manifest.json`",
    "keep the returned `zigux/tests/phase9_build.zig` bundle explicit only as bounded bitmap-family evidence rather than proof that the broader shared runtime-loader packet returned",
    "current `master` still does not materialize the broader shared `zigux/tests/runtime_*` replay family beyond the returned trace-events survey witness, `zigux/kernel/runtime_loader.zig`, or `zigux/kernel/runtime_loader_contract.zig`",
    "keep `zigux/Makefile` explicit only as a readable non-owner surface whose live body still lacks dedicated `phase9-*` runtime-pilot routes",
    "keep the freeze-map boundary explicit too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues",
    PHASE2_CONF_BRIDGE_MARKER,
    PHASE2_CONFDATA_BRIDGE_MARKER,
    PHASE3_EXPORTS_MARKER,
    PHASE3_EXPORT_SHIM_MARKER,
    PHASE2_BOUNDARY_MARKER,
    PHASE3_BOUNDARY_MARKER,
]

SAMPLES_README_REQUIRED_MARKERS = [
    PHASE9_BOUNDARY_CHECKER_MARKER,
    TRACE_EVENTS_PACKET_CHECKER_MARKER,
    "`samples/zigux/runtime_trace_events.zig`",
    ".provides_selftest_hook = true",
    "initialized, selftest_complete, and exited lifecycle tracking",
    "`Documentation/zigux/phase9-runtime-trace-events-survey.md`",
    "`Documentation/zigux/phase9-runtime-trace-events-module-slice.md`",
    "`zigux/tests/runtime_trace_events_manifest.json`",
    "`zigux/tests/runtime_trace_events_survey.zig`",
    "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
    "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig` keeps failed-exit rollback explicit after reusable selftest replay",
    "post-exit invalid-lifecycle rejections",
    "initialized-before/after, selftest_complete-before/after, and exited-before/after summary-stability checks",
    "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
    "balanced function-thread registration reusable before and after selftest",
    "balanced registration re-entry companion across the initialized and selftest_complete stages",
    "direct authenticated contents reads still return missing for `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, and `zigux/tests/runtime_bitmap_manifest.json`, while the same trusted reread still materializes `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_survey.zig`, and `zigux/tests/phase9_build.zig`",
    "Keep that partial bitmap reminder packet framed as a separate Phase 9 runtime family reminder rather than as direct proof that the broader shared runtime-loader packet returned or as evidence that a fifth approved Phase 5 sample family landed here.",
    "does not currently expose the broader shared runtime-loader packet",
    PHASE2_CONF_BRIDGE_MARKER,
    PHASE2_CONFDATA_BRIDGE_MARKER,
    PHASE3_EXPORTS_MARKER,
    PHASE3_EXPORT_SHIM_MARKER,
    PHASE2_BOUNDARY_MARKER,
    PHASE3_BOUNDARY_MARKER,
]

REQUIRED_MARKERS = {
    REVIEW_CHECKLIST_PATH: CHECKLIST_REQUIRED_MARKERS,
    LANE_SEQUENCING_PATH: LANE_SEQUENCING_REQUIRED_MARKERS,
    MODULE_SLICE_PATH: MODULE_SLICE_REQUIRED_MARKERS,
    SCRIPTS_README_PATH: SCRIPTS_README_REQUIRED_MARKERS,
    SAMPLES_README_PATH: SAMPLES_README_REQUIRED_MARKERS,
}

MAKEFILE_FORBIDDEN_ROUTE_FIXTURES = ["phase9-test", "phase9-runtime-trace-events-sample-tests", "phase9"]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def find_makefile_phase9_routes(text: str) -> list[str]:
    routes: list[str] = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith(".PHONY:"):
            continue
        if stripped.startswith("phase9") and ":" in stripped:
            routes.append(stripped.split(":", 1)[0])
    return routes


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in [*REQUIRED_MARKERS, MAKEFILE_PATH]:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")

    makefile = read_text(root, MAKEFILE_PATH)
    for route in find_makefile_phase9_routes(makefile):
        failures.append(f"unexpected_phase9_route:{MAKEFILE_PATH}:{route}")

    return failures


def build_fixture_text(rel_path: str) -> str:
    if rel_path == MAKEFILE_PATH:
        return """PYTHON ?= python3
ZIG ?= zig
ZIGUX_ROOT := ..

.PHONY: phase8-test phase10-test phase12-test

phase8-test:
\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_build.zig --summary all

phase10-test:
\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase10_build.zig --summary all

phase12-test:
\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all
"""
    return "# fixture\n\n" + "\n".join(REQUIRED_MARKERS[rel_path]) + "\n"


def seed_fixture_tree(base: Path) -> None:
    for rel_path in [*REQUIRED_MARKERS, MAKEFILE_PATH]:
        write_text(base / rel_path, build_fixture_text(rel_path))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-review-checklist-boundaries-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, markers in REQUIRED_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = read_text(base, rel_path)
                write_text(base / rel_path, current.replace(marker, ""))
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for route in MAKEFILE_FORBIDDEN_ROUTE_FIXTURES:
            seed_fixture_tree(base)
            current = read_text(base, MAKEFILE_PATH)
            write_text(base / MAKEFILE_PATH, current + f"\n{route}:\n\t@true\n")
            expect_failure(base, f"unexpected_phase9_route:{MAKEFILE_PATH}:{route}")

        for rel_path in [*REQUIRED_MARKERS, MAKEFILE_PATH]:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_SELF_TEST=pass")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_CHECKLIST_MARKER_COUNT={len(CHECKLIST_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_LANE_SEQUENCING_MARKER_COUNT={len(LANE_SEQUENCING_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_MODULE_SLICE_MARKER_COUNT={len(MODULE_SLICE_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_SCRIPTS_README_MARKER_COUNT={len(SCRIPTS_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_SAMPLES_README_MARKER_COUNT={len(SAMPLES_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_FORBIDDEN_MAKEFILE_ROUTE_COUNT={len(MAKEFILE_FORBIDDEN_ROUTE_FIXTURES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 9 review checklist, lane-sequencing note, trace-events module-slice note, scripts-root reminder, samples-root reminder, and live Makefile posture all keep the surviving trace-events runtime packet, the partial bitmap reminder packet, the absent broader shared runtime-loader packet, the earlier Phase 2 and Phase 3 boundary references, and the no-Phase-9-make-route policy explicit."
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_ERROR={failure}")
        return 1

    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_CHECKLIST_MARKER_COUNT={len(CHECKLIST_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_LANE_SEQUENCING_MARKER_COUNT={len(LANE_SEQUENCING_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_MODULE_SLICE_MARKER_COUNT={len(MODULE_SLICE_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_SCRIPTS_README_MARKER_COUNT={len(SCRIPTS_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_SAMPLES_README_MARKER_COUNT={len(SAMPLES_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_FORBIDDEN_MAKEFILE_ROUTE_COUNT={len(MAKEFILE_FORBIDDEN_ROUTE_FIXTURES)}")
    print("PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
