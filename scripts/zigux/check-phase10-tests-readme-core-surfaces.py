#!/usr/bin/env python3
"""Check that the Phase 10 tests-root reminders match current direct-readback reality."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SURFACE_PATH = Path("Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md")
TESTS_ROOT_README_PATH = Path("zigux/tests/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
PHASE10_START = "## Phase 10 tests-root packet"
PHASE10_END = "## Phase 11 tests-root packet"

REQUIRED_DIRECT_MARKERS = (
    "`Documentation/zigux/phase10-closure-evidence.md`",
    "`Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`",
    "`scripts/zigux/check-phase10-bootstrap-route.py`",
    "`scripts/zigux/check-phase10-shared-freeze-boundary.py`",
    "`scripts/zigux/check-phase10-ring-packet.py`",
    "`scripts/zigux/check-phase10-input-packet.py`",
    "`scripts/zigux/check-phase10-mmio-packet.py`",
    "`scripts/zigux/check-phase10-harness-coverage.py`",
    "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`scripts/zigux/validate-phase10-closure.py`",
    "`Documentation/zigux/phase10-virtio-core-survey.md`",
    "`Documentation/zigux/phase10-virtio-ring-survey.md`",
    "`Documentation/zigux/phase10-virtio-ring-slice.md`",
    "`Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`",
    "`drivers/virtio/virtio_ring.zig`",
    "`drivers/virtio/virtio_ring_verify.zig`",
    "`zigux/tests/phase10_virtio_ring_manifest.json`",
    "`zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`",
    "`zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig`",
    "`zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
    "`zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig`",
    "`zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig`",
    "`zigux/tests/phase10_virtio_ring_survey.zig`",
    "`Documentation/zigux/phase10-virtio-input-survey.md`",
    "`Documentation/zigux/phase10-virtio-input-slice.md`",
    "`Documentation/zigux/phase10-virtio-input-module-slice.md`",
    "`drivers/virtio/virtio_input.zig`",
    "`drivers/virtio/virtio_input_probe_preflight.zig`",
    "`drivers/virtio/virtio_input_queue_callback_preflight.zig`",
    "`drivers/virtio/virtio_input_registration_preflight.zig`",
    "`drivers/virtio/virtio_input_status_drain.zig`",
    "`drivers/virtio/virtio_input_teardown_observation.zig`",
    "`drivers/virtio/virtio_input_verify.zig`",
    "`zigux/tests/phase10_virtio_input.zig`",
    "`zigux/tests/phase10_virtio_input_manifest.json`",
    "`zigux/tests/phase10_virtio_input_probe_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_registration_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_status_drain.zig`",
    "`zigux/tests/phase10_virtio_input_teardown_observation.zig`",
    "`zigux/tests/phase10_virtio_input_survey.zig`",
    "`Documentation/zigux/phase10-virtio-mmio-survey.md`",
    "`Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`",
    "`Documentation/zigux/phase10-virtio-mmio-slice.md`",
    "`drivers/virtio/virtio_mmio.zig`",
    "`drivers/virtio/virtio_mmio_verify.zig`",
    "`zigux/tests/phase10_closure_manifest.json`",
    "`zigux/tests/phase10_virtio_mmio_manifest.json`",
    "`zigux/tests/phase10_virtio_mmio.zig`",
    "`zigux/tests/phase10_virtio_mmio_survey.zig`",
    "`zigux/tests/phase10_build.zig`",
)

REQUIRED_REPO_REALITY_GAP_MARKERS = (
    "current `master` still does not materialize",
    "`scripts/zigux/validate-phase10.py`",
    "`Documentation/zigux/phase10-virtio-core-slice.md`",
    "`zigux/tests/phase10_virtio_core.zig`",
    "`zigux/tests/phase10_virtio_core_reset_queue.zig`",
    "`zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`",
    "`drivers/virtio/virtio_driver_id.zig`",
    "`drivers/virtio/virtio_verify.zig`",
    "`zigux/tests/phase10_virtio_core_manifest.json`",
    "`zigux/tests/phase10_virtio_core_survey.zig`",
    "`zigux/tests/phase10_virtio_ring.zig`",
    "last-known packet members or repo-reality gaps",
)

REQUIRED_RETURNED_MAKEFILE_MARKERS = (
    "The returned shared build gate now runs through `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, `make -C zigux phase10`, and `zigux/tests/phase10_build.zig`.",
    "Current `master` does materialize `zigux/Makefile`, and its live body now exposes the dedicated `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` routes,",
    "the returned `zigux/Makefile` body plus `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` explicit as the shared build gate",
)

REQUIRED_ALIGNMENT_MARKERS = (
    "blocked risky-transport posture",
    "allowed `drivers/virtio/*.zig` plus justified `zigux/kernel/` or `zigux/helpers/` destination family",
    "shared closure-packet vocabulary around `zigux/tests/phase10_closure_manifest.json`",
    "Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`",
    "workflow-backed bootstrap route",
    "Treat `scripts/zigux/README.md` as the current dedicated Phase 10 scripts-root packet on current `master` and keep it aligned with the shared closure note, lane-sequencing note, review checklist, and tests-root reminder instead of leaving it in neighboring-surface wording.",
)

REQUIRED_WRAPPER_SPLIT_MARKERS = (
    "Wrapper ownership for the input lane stays split:",
    "`drivers/virtio/virtio.zig` owns shared device-status bookkeeping",
    "`drivers/virtio/virtio_ring.zig` owns virtqueue wrapper shape and notification planning",
    "`drivers/virtio/virtio_mmio.zig` owns MMIO wrapper planning",
)

REQUIRED_TESTS_ROOT_MARKERS = (
    "`Documentation/zigux/phase10-closure-evidence.md`",
    "`Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`",
    "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
    "The returned shared build gate now runs through `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, `make -C zigux phase10`, and `zigux/tests/phase10_build.zig`.",
    "Current `master` does materialize `zigux/Makefile`, and its live body now exposes the dedicated `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` routes,",
    "the returned `zigux/Makefile` body plus `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` explicit as the shared build gate",
)

REQUIRED_SCRIPTS_README_MARKERS = (
    "## Phase 10",
    "the current scripts-root virtio packet stays reviewable through the bootstrap-route guard, the shared freeze-boundary guard, the ring, input, and MMIO packet guards, the harness-coverage and tests-readme core-surface guards, the returned validator pair, the closure manifest, and the Makefile-backed shared build gate instead of widening into the still-missing core-side slice or risky transport follow-through",
    "`scripts/zigux/check-phase10-input-packet.py`",
    "`scripts/zigux/validate-phase10.py`",
    "`scripts/zigux/validate-phase10-closure.py`",
    "`zigux/tests/phase10_closure_manifest.json`, `zigux/tests/phase10_build.zig`, `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` keep the returned closure-manifest and shared build gate explicit from the scripts root beside the same checker-backed review packet",
    "keep risky transport parked behind the shared closure note, freeze map, and adjacent survey packet instead of widening this scripts-root reminder into queue restart, registration lifecycle, IRQ delivery, DMA behavior, or broader transport claims",
)

FORBIDDEN_GAP_MARKERS = (
    "`Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-mmio-slice.md`",
    "`zigux/tests/phase10_closure_manifest.json`, `zigux/tests/phase10_virtio_core.zig`",
    "`zigux/tests/phase10_virtio_ring_survey.zig` framed as last-known packet members or repo-reality gaps",
    "Current `master` does materialize `zigux/Makefile`, but it still does not materialize the dedicated `make -C zigux phase10-validate`, `make -C zigux phase10-test`, or `make -C zigux phase10` routes,",
    "`scripts/zigux/validate-phase10-closure.py`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, `make -C zigux phase10`",
    "`Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `.github/workflows/zigux-bootstrap.yml`",
)


def phase10_section(text: str) -> str:
    start = text.find(PHASE10_START)
    if start == -1:
        raise SystemExit("phase10 companion checker missing `## Phase 10 tests-root packet` section heading")
    end = text.find(PHASE10_END, start)
    if end == -1:
        raise SystemExit("phase10 companion checker missing `## Phase 11 tests-root packet` section heading")
    return text[start:end]


def check_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"phase10 companion checker missing {label} markers: " + ", ".join(missing))


def check_absent_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    present = [marker for marker in markers if marker in text]
    if present:
        raise SystemExit(f"phase10 companion checker found forbidden {label} markers: " + ", ".join(present))


def check_companion_text(text: str) -> None:
    section = phase10_section(text)
    check_markers(section, REQUIRED_DIRECT_MARKERS, "direct-readback")
    check_markers(section, REQUIRED_REPO_REALITY_GAP_MARKERS, "repo-reality-gap")
    check_markers(section, REQUIRED_RETURNED_MAKEFILE_MARKERS, "returned-makefile")
    check_markers(section, REQUIRED_ALIGNMENT_MARKERS, "alignment")
    check_markers(section, REQUIRED_WRAPPER_SPLIT_MARKERS, "wrapper-split")
    check_absent_markers(section, FORBIDDEN_GAP_MARKERS, "repo-reality-gap")


def check_tests_root_readme(text: str) -> None:
    check_markers(text, REQUIRED_TESTS_ROOT_MARKERS, "tests-root-readme")


def check_scripts_readme(text: str) -> None:
    check_markers(text, REQUIRED_SCRIPTS_README_MARKERS, "scripts-readme")


def run_self_test() -> int:
    good_companion = """# Phase 10, 11, and 13 Tests-Root Review Companion

## Phase 10 tests-root packet

Keep the current bounded virtio closure packet explicit through the shared reminder surfaces, the directly re-readable ring packet anchors, the directly re-readable input packet, the helper-local MMIO packet, the returned shared closure validator and manifest, and the shared build gate:
- shared reminder surfaces: `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `scripts/zigux/check-phase10-bootstrap-route.py`, `scripts/zigux/check-phase10-shared-freeze-boundary.py`, `scripts/zigux/check-phase10-ring-packet.py`, `scripts/zigux/check-phase10-input-packet.py`, `scripts/zigux/check-phase10-mmio-packet.py`, `scripts/zigux/check-phase10-harness-coverage.py`, `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `.github/workflows/zigux-bootstrap.yml`
- directly re-readable ring packet anchors: `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`, `zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig`, `zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, and `zigux/tests/phase10_build.zig`
- directly re-readable input packet anchors: `Documentation/zigux/phase10-virtio-input-survey.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_probe_preflight.zig`, `drivers/virtio/virtio_input_queue_callback_preflight.zig`, `drivers/virtio/virtio_input_registration_preflight.zig`, `drivers/virtio/virtio_input_status_drain.zig`, `drivers/virtio/virtio_input_teardown_observation.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_manifest.json`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, and `zigux/tests/phase10_virtio_input_survey.zig`
- helper-local MMIO packet anchors: `Documentation/zigux/phase10-virtio-mmio-survey.md`, `Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`, `Documentation/zigux/phase10-virtio-mmio-slice.md`, `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio.zig`, and `zigux/tests/phase10_virtio_mmio_survey.zig`
- returned shared closure packet anchors: `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, `Documentation/zigux/phase10-virtio-core-survey.md`, and `zigux/tests/phase10_closure_manifest.json`
- current `master` still does not materialize `Documentation/zigux/phase10-virtio-core-slice.md`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `drivers/virtio/virtio_driver_id.zig`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core_survey.zig`, and `zigux/tests/phase10_virtio_ring.zig` through the direct readback available in this lane, so keep them framed as last-known packet members or repo-reality gaps instead of direct current-head evidence.

The returned shared build gate now runs through `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, `make -C zigux phase10`, and `zigux/tests/phase10_build.zig`.

Current `master` does materialize `zigux/Makefile`, and its live body now exposes the dedicated `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` routes, so keep the returned file and those returned Phase 10 route names explicit as the shared build gate instead of treating them as repo-reality gaps.

Treat `scripts/zigux/README.md` as the current dedicated Phase 10 scripts-root packet on current `master` and keep it aligned with the shared closure note, lane-sequencing note, review checklist, and tests-root reminder instead of leaving it in neighboring-surface wording.

Tests-root reviewer prompt:
- Do the docs-root notes, scripts-root guards, tests-root packet, the workflow-backed bootstrap route through `scripts/zigux/check-phase10-bootstrap-route.py` and `.github/workflows/zigux-bootstrap.yml`, the shared closure note, the lane-sequencing note, the returned closure validator and closure manifest, the returned core survey note, the ring survey and slice notes, the direct ring helper packet through `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig`, `zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, the shared `zigux/tests/phase10_build.zig` gate, and the broader `zigux/tests/phase10_virtio_ring.zig` replay framed as a last-known packet member until a fresh reread rematerializes it, the input slice, input module slice, input survey, direct input helpers, `zigux/tests/phase10_virtio_input_manifest.json`, queue-callback-preflight, registration-preflight, teardown-observation, status-drain, and `zigux/tests/phase10_virtio_input_survey.zig` replays, the helper-local MMIO survey plus `Documentation/zigux/phase10-virtio-mmio-slice.md`, `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio.zig`, and `zigux/tests/phase10_virtio_mmio_survey.zig`, the blocked risky-transport posture, the returned `zigux/Makefile` body plus `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` explicit as the shared build gate, the allowed `drivers/virtio/*.zig` plus justified `zigux/kernel/` or `zigux/helpers/` destination family, the shared closure-packet vocabulary around `zigux/tests/phase10_closure_manifest.json`, and the Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay aligned on the same bounded virtio story while keeping `scripts/zigux/validate-phase10.py` and the missing core-side packet companions framed as last-known packet members or repo-reality gaps instead of direct current-head evidence?

Wrapper ownership for the input lane stays split: `drivers/virtio/virtio.zig` owns shared device-status bookkeeping, `drivers/virtio/virtio_ring.zig` owns virtqueue wrapper shape and notification planning, and `drivers/virtio/virtio_mmio.zig` owns MMIO wrapper planning, so transport-facing queue work, registration lifecycle, IRQ delivery, DMA behavior, and broader probe or remove follow-through stay parked outside this tests-root reminder.

## Phase 11 tests-root packet
"""
    good_tests_root_readme = """# zigux/tests

Keep `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, and `scripts/zigux/check-phase10-tests-readme-core-surfaces.py` explicit as the shared Phase 10 tests-root reminder packet.

The returned shared build gate now runs through `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, `make -C zigux phase10`, and `zigux/tests/phase10_build.zig`.

Current `master` does materialize `zigux/Makefile`, and its live body now exposes the dedicated `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` routes, so keep the returned file and those returned Phase 10 route names explicit as the shared build gate instead of treating them as repo-reality gaps.

Tests-root reviewer prompt:
- keep the returned `zigux/Makefile` body plus `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` explicit as the shared build gate
"""
    good_scripts_readme = """# scripts/zigux

## Phase 10

- Phase 10 flow - the current scripts-root virtio packet stays reviewable through the bootstrap-route guard, the shared freeze-boundary guard, the ring, input, and MMIO packet guards, the harness-coverage and tests-readme core-surface guards, the returned validator pair, the closure manifest, and the Makefile-backed shared build gate instead of widening into the still-missing core-side slice or risky transport follow-through
- `scripts/zigux/check-phase10-bootstrap-route.py`, `scripts/zigux/check-phase10-shared-freeze-boundary.py`, `scripts/zigux/check-phase10-ring-packet.py`, `scripts/zigux/check-phase10-input-packet.py`, `scripts/zigux/check-phase10-mmio-packet.py`, `scripts/zigux/check-phase10-harness-coverage.py`, `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`, `scripts/zigux/validate-phase10.py`, and `scripts/zigux/validate-phase10-closure.py` keep the shipped shared Phase 10 scripts-root packet explicit on current `master`
- `zigux/tests/phase10_closure_manifest.json`, `zigux/tests/phase10_build.zig`, `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` keep the returned closure-manifest and shared build gate explicit from the scripts root beside the same checker-backed review packet
- current `master` still does not materialize `Documentation/zigux/phase10-virtio-core-slice.md`, so keep the broader core-side slice framed as a repo-reality gap while the returned core survey, ring, input, and MMIO packet anchors continue to carry the bounded shared reminder
- keep risky transport parked behind the shared closure note, freeze map, and adjacent survey packet instead of widening this scripts-root reminder into queue restart, registration lifecycle, IRQ delivery, DMA behavior, or broader transport claims
"""
    check_companion_text(good_companion)
    check_tests_root_readme(good_tests_root_readme)
    check_scripts_readme(good_scripts_readme)

    bad_companion = good_companion.replace(
        "`zigux/tests/phase10_virtio_input_manifest.json`",
        "`zigux/tests/phase10_virtio_input_manifest_missing.json`",
        1,
    )
    try:
        check_companion_text(bad_companion)
    except SystemExit as exc:
        assert "direct-readback" in str(exc)
    else:
        raise AssertionError("expected missing input manifest marker failure")

    bad_scripts_readme = good_scripts_readme.replace(
        "`scripts/zigux/check-phase10-input-packet.py`",
        "`scripts/zigux/check-phase10-input-packet-missing.py`",
        1,
    )
    try:
        check_scripts_readme(bad_scripts_readme)
    except SystemExit as exc:
        assert "scripts-readme" in str(exc)
    else:
        raise AssertionError("expected missing scripts README input checker marker failure")

    print("PHASE10_TESTS_ROOT_COMPANION_CHECKER_SELF_TEST=pass")
    print("PHASE10_TESTS_ROOT_COMPANION_CHECKER_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--source",
        type=Path,
        default=SURFACE_PATH,
        help="path to the shared Phase 10/11/13 tests-root companion note",
    )
    parser.add_argument(
        "--tests-root-readme",
        type=Path,
        default=TESTS_ROOT_README_PATH,
        help="path to zigux/tests/README.md",
    )
    parser.add_argument(
        "--scripts-readme",
        type=Path,
        default=SCRIPTS_README_PATH,
        help="path to scripts/zigux/README.md",
    )
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    check_companion_text(args.source.read_text(encoding="utf-8"))
    check_tests_root_readme(args.tests_root_readme.read_text(encoding="utf-8"))
    check_scripts_readme(args.scripts_readme.read_text(encoding="utf-8"))
    print("PHASE10_TESTS_ROOT_COMPANION_CHECK=pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
