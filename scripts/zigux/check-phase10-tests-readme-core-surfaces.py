#!/usr/bin/env python3
"""Check that the Phase 10 tests-root companion matches current direct-readback reality."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

SURFACE_PATH = Path("Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md")
PHASE10_START = "## Phase 10 tests-root packet"
PHASE10_END = "## Phase 11 tests-root packet"
REQUIRED_DIRECT_MARKERS = (
    "`Documentation/zigux/phase10-closure-evidence.md`",
    "`Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`",
    "`scripts/zigux/check-phase10-ring-packet.py`",
    "`scripts/zigux/check-phase10-input-packet.py`",
    "`scripts/zigux/check-phase10-mmio-packet.py`",
    "`scripts/zigux/check-phase10-harness-coverage.py`",
    "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
    "`Documentation/zigux/phase10-virtio-ring-survey.md`",
    "`Documentation/zigux/phase10-virtio-ring-slice.md`",
    "`drivers/virtio/virtio_ring.zig`",
    "`drivers/virtio/virtio_ring_verify.zig`",
    "`zigux/tests/phase10_virtio_ring_manifest.json`",
    "`zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig`",
    "`zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
    "`zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig`",
    "`zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig`",
    "`Documentation/zigux/phase10-virtio-input-survey.md`",
    "`drivers/virtio/virtio_input.zig`",
    "`zigux/tests/phase10_virtio_input_status_drain.zig`",
    "`Documentation/zigux/phase10-virtio-mmio-survey.md`",
    "`drivers/virtio/virtio_mmio.zig`",
    "`drivers/virtio/virtio_mmio_verify.zig`",
    "`zigux/tests/phase10_build.zig`",
)
REQUIRED_REPO_REALITY_GAP_MARKERS = (
    "current `master` still does not materialize",
    "`scripts/zigux/validate-phase10.py`",
    "`scripts/zigux/validate-phase10-closure.py`",
    "`zigux/Makefile`",
    "`make -C zigux phase10-validate`",
    "`make -C zigux phase10-test`",
    "`make -C zigux phase10`",
    "`Documentation/zigux/phase10-virtio-core-survey.md`",
    "`Documentation/zigux/phase10-virtio-core-slice.md`",
    "`Documentation/zigux/phase10-virtio-mmio-slice.md`",
    "`zigux/tests/phase10_closure_manifest.json`",
    "`zigux/tests/phase10_virtio_core.zig`",
    "`zigux/tests/phase10_virtio_mmio.zig`",
    "`zigux/tests/phase10_virtio_mmio_manifest.json`",
    "`zigux/tests/phase10_virtio_mmio_survey.zig`",
    "last-known packet members or repo-reality gaps",
)
REQUIRED_ALIGNMENT_MARKERS = (
    "blocked risky-transport posture",
    "allowed `drivers/virtio/*.zig` plus justified `zigux/kernel/` or `zigux/helpers/` destination family",
    "shared closure-packet vocabulary around `zigux/tests/phase10_closure_manifest.json`",
    "Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`",
)
FORBIDDEN_RING_GAP_MARKERS = (
    "keep `drivers/virtio/virtio_ring_verify.zig` and `zigux/tests/phase10_virtio_ring_survey.zig` framed as last-known packet members until a fresh reread proves they rematerialize on current `master`.",
    "`drivers/virtio/virtio_ring_verify.zig` and `zigux/tests/phase10_virtio_ring_survey.zig` framed as missing direct-readback ring companions",
)
def phase10_section(text: str) -> str:
    start = text.find(PHASE10_START)
    if start == -1:
        raise SystemExit("phase10 companion checker missing `## Phase 10 tests-root packet` section heading")
    end = text.find(PHASE10_END, start)
    if end == -1:
        raise SystemExit("phase10 companion checker missing `## Phase 11 tests-root packet` section heading")
    return text[start:end]
def check_markers(section: str, markers: tuple[str, ...], label: str) -> None:
    missing = [marker for marker in markers if marker not in section]
    if missing:
        raise SystemExit(f"phase10 companion checker missing {label} markers: " + ", ".join(missing))
def check_absent_markers(section: str, markers: tuple[str, ...], label: str) -> None:
    present = [marker for marker in markers if marker in section]
    if present:
        raise SystemExit(f"phase10 companion checker found forbidden {label} markers: " + ", ".join(present))
def check_text(text: str) -> None:
    section = phase10_section(text)
    check_markers(section, REQUIRED_DIRECT_MARKERS, "direct-readback")
    check_markers(section, REQUIRED_REPO_REALITY_GAP_MARKERS, "repo-reality-gap")
    check_markers(section, REQUIRED_ALIGNMENT_MARKERS, "alignment")
    check_absent_markers(section, FORBIDDEN_RING_GAP_MARKERS, "ring-gap")
def run_self_test() -> int:
    good = """# Phase 10, 11, and 13 Tests-Root Review Companion

## Phase 10 tests-root packet

Keep the current bounded virtio closure packet explicit through the shared reminder surfaces, the directly re-readable ring packet anchors, the directly re-readable input packet, the helper-local MMIO packet, and the shared build gate:
- shared reminder surfaces: `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `scripts/zigux/check-phase10-ring-packet.py`, `scripts/zigux/check-phase10-input-packet.py`, `scripts/zigux/check-phase10-mmio-packet.py`, `scripts/zigux/check-phase10-harness-coverage.py`, `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `.github/workflows/zigux-bootstrap.yml`
- directly re-readable ring packet anchors: `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig`, `zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig`, and `zigux/tests/phase10_build.zig`
- directly re-readable input packet anchors: `Documentation/zigux/phase10-virtio-input-survey.md`, `drivers/virtio/virtio_input.zig`, and `zigux/tests/phase10_virtio_input_status_drain.zig`
- helper-local MMIO packet anchors: `Documentation/zigux/phase10-virtio-mmio-survey.md`, `drivers/virtio/virtio_mmio.zig`, and `drivers/virtio/virtio_mmio_verify.zig`
- current `master` still does not materialize `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, `make -C zigux phase10`, `Documentation/zigux/phase10-virtio-core-survey.md`, `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-mmio-slice.md`, `zigux/tests/phase10_closure_manifest.json`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, and `zigux/tests/phase10_virtio_mmio_survey.zig` through the direct readback available in this lane, so keep them framed as last-known packet members or repo-reality gaps instead of direct current-head evidence.

Tests-root reviewer prompt:
- Do the docs-root notes, scripts-root guards, tests-root packet, the shared closure note, the lane-sequencing note, the ring survey and slice notes, the direct ring helper packet through `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig`, `zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig`, and the shared `zigux/tests/phase10_build.zig` gate, the input slice, input module slice, input survey, direct input helpers, queue-callback-preflight, registration-preflight, teardown-observation, and status-drain replays, the helper-local MMIO survey plus `drivers/virtio/virtio_mmio.zig` and `drivers/virtio/virtio_mmio_verify.zig`, while keeping `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio_survey.zig`, and `zigux/tests/phase10_virtio_ring_survey.zig` framed as last-known packet members or repo-reality gaps, the blocked risky-transport posture, the allowed `drivers/virtio/*.zig` plus justified `zigux/kernel/` or `zigux/helpers/` destination family, the shared closure-packet vocabulary around `zigux/tests/phase10_closure_manifest.json`, and the Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay aligned on the same bounded virtio story?

## Phase 11 tests-root packet
"""
    check_text(good)
    tests = []
    tests.append((good.replace("## Phase 10 tests-root packet", "## Phase Ten tests-root packet", 1), "`## Phase 10 tests-root packet`"))
    tests.append((good.replace("## Phase 11 tests-root packet", "## Phase Eleven tests-root packet", 1), "`## Phase 11 tests-root packet`"))
    tests.append((good.replace("`zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig`", "`zigux/tests/phase10_virtio_ring_delayed_callback_budget_missing.zig`"), "`zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig`"))
    tests.append((good.replace("`zigux/Makefile`", "`zigux/Makefile_missing`", 1), "`zigux/Makefile`"))
    tests.append((good.replace("blocked risky-transport posture", "blocked transport posture", 1), "blocked risky-transport posture"))
    tests.append((good.replace("and `zigux/tests/phase10_virtio_ring_survey.zig` framed as last-known packet members or repo-reality gaps", "and `drivers/virtio/virtio_ring_verify.zig` and `zigux/tests/phase10_virtio_ring_survey.zig` framed as missing direct-readback ring companions", 1), "missing direct-readback ring companions"))
    tests.append((good.replace("- current `master` still does not materialize", "keep `drivers/virtio/virtio_ring_verify.zig` and `zigux/tests/phase10_virtio_ring_survey.zig` framed as last-known packet members until a fresh reread proves they rematerialize on current `master`.\n- current `master` still does not materialize", 1), "last-known packet members until a fresh reread proves they rematerialize"))
    for text, expected in tests:
        try:
            check_text(text)
        except SystemExit as exc:
            assert expected in str(exc), str(exc)
        else:
            raise AssertionError(f"expected failure for {expected}")
    print("PHASE10_TESTS_ROOT_COMPANION_CHECKER_SELF_TEST=pass")
    print("PHASE10_TESTS_ROOT_COMPANION_CHECKER_SELF_TEST_CASE_COUNT=7")
    return 0
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--source", type=Path, default=SURFACE_PATH, help="path to the shared Phase 10/11/13 tests-root companion note")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    text = args.source.read_text(encoding="utf-8")
    check_text(text)
    print("PHASE10_TESTS_ROOT_COMPANION_CHECK=pass")
    return 0
if __name__ == "__main__":
    sys.exit(main())
