#!/usr/bin/env python3
"""Check that the shared Phase 10 reminder surfaces match current repo reality."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SURFACE_PATH = Path("Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md")
TESTS_ROOT_README_PATH = Path("zigux/tests/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
PHASE10_START = "## Phase 10 tests-root packet"
PHASE10_END = "## Phase 11 tests-root packet"

COMPANION_REQUIRED_MARKERS = (
    "Keep the current bounded virtio closure packet explicit through the shared reminder surfaces, the directly re-readable ring packet anchors, the directly re-readable input packet, the helper-local MMIO packet, the returned shared closure validator, manifest, and count guard, and the shared build gate:",
    "`scripts/zigux/check-phase10-bootstrap-route.py`",
    "`scripts/zigux/check-phase10-shared-freeze-boundary.py`",
    "`scripts/zigux/check-phase10-harness-coverage.py`",
    "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
    "`scripts/zigux/check-phase10-closure-manifest-counts.py`",
    "`Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md`",
    "`Documentation/zigux/phase10-virtio-ring-survey.md`",
    "`drivers/virtio/virtio_ring_publish_readiness.zig`",
    "`zigux/tests/phase10_virtio_ring_survey.zig`",
    "Keep the returned driver-id pair and those mixed-source returned core companions explicit here, and keep `zigux/tests/phase10_virtio_ring.zig` explicit as the directly re-readable broader ring companion.",
    "`Documentation/zigux/phase10-virtio-input-module-slice.md`",
    "`drivers/virtio/virtio_input_queue_callback_preflight.zig`",
    "`drivers/virtio/virtio_input_teardown_preflight.zig`",
    "`drivers/virtio/virtio_input_verify.zig`",
    "`zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_teardown_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_teardown_observation.zig`",
    "`Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`",
    "`zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`",
    "`zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig`",
    "`zigux/tests/phase10_virtio_mmio_survey.zig`, `scripts/zigux/check-phase10-mmio-packet.py`, and `zigux/tests/phase10_build.zig`",
    "`zigux/tests/phase10_virtio_mmio_manifest.json`",
    "returned shared closure packet anchors: `scripts/zigux/check-phase10-closure-manifest-counts.py`, `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, `Documentation/zigux/phase10-virtio-core-survey.md`, `zigux/tests/phase10_virtio_core.zig`, and `zigux/tests/phase10_closure_manifest.json`",
    "The returned shared build gate now runs through `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, `make -C zigux phase10`, and `zigux/tests/phase10_build.zig`.",
    "Current `master` does materialize `zigux/Makefile`, and its live body now exposes the dedicated `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` routes, so keep the returned file and those returned Phase 10 route names explicit as the shared build gate instead of treating them as repo-reality gaps.",
    "blocked risky-transport posture",
    "Treat `scripts/zigux/README.md` as the current dedicated Phase 10 scripts-root packet on current `master` and keep it aligned with the shared closure note, lane-sequencing note, review checklist, and tests-root reminder instead of leaving it in neighboring-surface wording.",
    "Keep the returned shared validator pair `scripts/zigux/validate-phase10.py` and `scripts/zigux/validate-phase10-closure.py` plus the returned `zigux/Makefile` explicit in that directly re-readable anchor set instead of leaving them visible only in the shared build-gate reminder.",
    "Keep `zigux/tests/phase10_virtio_ring_survey.zig` explicit as the returned dedicated ring survey gate beside `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and `zigux/tests/phase10_build.zig` instead of framing that survey replay as a last-known packet member.",
    "Keep that landed apply-observation replay pair framed as helper-local observation evidence rather than transport-backed lifecycle proof.",
    "Keep the queue-local `P10-L10` ring freeze-boundary packet distinct from the bounded `P10-L11` MMIO helper packet",
    "Wrapper ownership for the input lane stays split:",
    "`drivers/virtio/virtio.zig` owns shared device-status bookkeeping",
    "`drivers/virtio/virtio_ring.zig` owns virtqueue wrapper shape and notification planning",
    "`drivers/virtio/virtio_mmio.zig` owns MMIO wrapper planning",
    "current direct lane readback now rematerializes `drivers/virtio/virtio_driver_id.zig` and `zigux/tests/phase10_virtio_driver_id.zig`",
)

COMPANION_FORBIDDEN_MARKERS = (
    "current `master` still does not materialize `scripts/zigux/validate-phase10.py`",
    "current `master` still does not materialize `Documentation/zigux/phase10-virtio-core-slice.md`, `zigux/tests/phase10_virtio_core.zig`",
    "keep `zigux/tests/phase10_virtio_ring_survey.zig` framed as a last-known packet member until a fresh reread proves it rematerializes on current `master`.",
    "current direct lane readback still does not materialize `drivers/virtio/virtio_driver_id.zig` and `zigux/tests/phase10_virtio_driver_id.zig` through the direct readback available in this lane",
    "the public current-`master` `zigux/tests/phase10_virtio_ring.zig` replay kept explicit as the returned broader ring companion while exact direct-path readback in this runtime still misses it",
)

TESTS_ROOT_REQUIRED_MARKERS = (
    "`Documentation/zigux/phase10-closure-evidence.md`",
    "`Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`",
    "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
    "Keep the returned checker-backed build gate explicit through `scripts/zigux/check-phase10-bootstrap-route.py`, `scripts/zigux/check-phase10-harness-coverage.py`, `scripts/zigux/validate-phase10-closure.py`, `zigux/tests/phase10_closure_manifest.json`, and `zigux/tests/phase10_build.zig`",
    "The returned shared build gate now runs through `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, `make -C zigux phase10`.",
    "Current `master` does materialize `zigux/Makefile`, and its live body now exposes the dedicated `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` routes, so keep the returned file and those returned Phase 10 route names explicit as the shared build gate instead of treating them as repo-reality gaps.",
    "`Documentation/zigux/phase10-virtio-input-module-slice.md`",
    "`drivers/virtio/virtio_input_queue_callback_preflight.zig`",
    "`drivers/virtio/virtio_ring_publish_readiness.zig`",
    "`zigux/tests/phase10_virtio_input_registration_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_teardown_observation.zig`",
    "queue-callback-preflight, registration-preflight, status-drain, and teardown-observation replays explicit here",
    "without widening into input registration lifecycle closure, transport callbacks, IRQ delivery, or DMA behavior",
    "Keep the helper-local MMIO replay pair explicit too through `zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig` and `zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig`",
    "`zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`",
    "`zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig`",
    "without widening into lifecycle, IRQ-delivery, or DMA claims",
)

SCRIPTS_ROOT_REQUIRED_MARKERS = (
    "## Phase 10",
    "`scripts/zigux/check-phase10-ring-packet.py`",
    "`scripts/zigux/check-phase10-input-packet.py`",
    "`scripts/zigux/check-phase10-mmio-packet.py`",
    "`scripts/zigux/validate-phase10.py`",
    "`scripts/zigux/validate-phase10-closure.py`",
    "`Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/phase10_closure_manifest.json`, `.github/workflows/zigux-bootstrap.yml`, and `scripts/zigux/README.md` remain the current reminder-surface companions for that shared closure packet",
    "`drivers/virtio/virtio_ring_publish_readiness.zig`",
    "`Documentation/zigux/phase10-virtio-core-survey.md`, `zigux/tests/phase10_virtio_core.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, and `zigux/tests/phase10_virtio_core_survey.zig` keep the bounded core packet explicit, and the now-returned exact-path `drivers/virtio/virtio_driver_id.zig` plus `zigux/tests/phase10_virtio_driver_id.zig` pair stays explicit as the narrower core-side follow-through evidence on current `master`",
    "`zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` keep the returned shared build gate explicit from the scripts root instead of treating those routes as missing-current-master gaps",
    "keep same-lane follow-through narrowed to one shared reminder or checker-backed truthfulness repair at a time; do not widen this scripts-root packet into queue execution parity, IRQ delivery, DMA behavior, input registration lifecycle closure, or risky transport follow-through",
)

SCRIPTS_ROOT_FORBIDDEN_MARKERS = (
    "while only `drivers/virtio/virtio_driver_id.zig` and `zigux/tests/phase10_virtio_driver_id.zig` remain the narrower core-side repo-reality gaps on current `master`",
)


def phase10_section(text: str) -> str:
    start = text.find(PHASE10_START)
    if start == -1:
        raise SystemExit("phase10 companion checker missing Phase 10 section heading")
    end = text.find(PHASE10_END, start)
    if end == -1:
        raise SystemExit("phase10 companion checker missing Phase 11 section heading")
    return text[start:end]


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"phase10 companion checker missing {label} markers: " + ", ".join(missing))


def forbid_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    present = [marker for marker in markers if marker in text]
    if present:
        raise SystemExit(f"phase10 companion checker found forbidden {label} markers: " + ", ".join(present))


def check_companion_text(text: str) -> None:
    section = phase10_section(text)
    require_markers(section, COMPANION_REQUIRED_MARKERS, "companion")
    forbid_markers(section, COMPANION_FORBIDDEN_MARKERS, "companion")


def check_tests_root_readme(text: str) -> None:
    require_markers(text, TESTS_ROOT_REQUIRED_MARKERS, "tests-root-readme")


def check_scripts_readme(text: str) -> None:
    require_markers(text, SCRIPTS_ROOT_REQUIRED_MARKERS, "scripts-readme")
    forbid_markers(text, SCRIPTS_ROOT_FORBIDDEN_MARKERS, "scripts-readme")


def run_self_test() -> int:
    good_companion = """# Phase 10, 11, and 13 Tests-Root Review Companion

## Phase 10 tests-root packet

Keep the current bounded virtio closure packet explicit through the shared reminder surfaces, the directly re-readable ring packet anchors, the directly re-readable input packet, the helper-local MMIO packet, the returned shared closure validator, manifest, and count guard, and the shared build gate:
- shared reminder surfaces: `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md`, `scripts/zigux/check-phase10-bootstrap-route.py`, `scripts/zigux/check-phase10-shared-freeze-boundary.py`, `scripts/zigux/check-phase10-ring-packet.py`, `scripts/zigux/check-phase10-input-packet.py`, `scripts/zigux/check-phase10-mmio-packet.py`, `scripts/zigux/check-phase10-harness-coverage.py`, `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`, `scripts/zigux/check-phase10-closure-manifest-counts.py`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `.github/workflows/zigux-bootstrap.yml`
- directly re-readable ring packet anchors: `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_ring_publish_readiness.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`, `zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig`, `zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, and `zigux/tests/phase10_build.zig`
- directly re-readable input packet anchors: `Documentation/zigux/phase10-virtio-input-survey.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_probe_preflight.zig`, `drivers/virtio/virtio_input_queue_callback_preflight.zig`, `drivers/virtio/virtio_input_registration_preflight.zig`, `drivers/virtio/virtio_input_status_drain.zig`, `drivers/virtio/virtio_input_teardown_preflight.zig`, `drivers/virtio/virtio_input_teardown_observation.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_manifest.json`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_teardown_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, and `zigux/tests/phase10_virtio_input_survey.zig`
- helper-local MMIO packet anchors: `Documentation/zigux/phase10-virtio-mmio-survey.md`, `Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`, `Documentation/zigux/phase10-virtio-mmio-slice.md`, `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`, `zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `scripts/zigux/check-phase10-mmio-packet.py`, and `zigux/tests/phase10_build.zig`
- returned shared closure packet anchors: `scripts/zigux/check-phase10-closure-manifest-counts.py`, `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, `Documentation/zigux/phase10-virtio-core-survey.md`, `zigux/tests/phase10_virtio_core.zig`, and `zigux/tests/phase10_closure_manifest.json`
- current direct lane readback now rematerializes `drivers/virtio/virtio_driver_id.zig` and `zigux/tests/phase10_virtio_driver_id.zig`

The returned shared build gate now runs through `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, `make -C zigux phase10`, and `zigux/tests/phase10_build.zig`.

Current `master` does materialize `zigux/Makefile`, and its live body now exposes the dedicated `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` routes, so keep the returned file and those returned Phase 10 route names explicit as the shared build gate instead of treating them as repo-reality gaps.

Treat `scripts/zigux/README.md` as the current dedicated Phase 10 scripts-root packet on current `master` and keep it aligned with the shared closure note, lane-sequencing note, review checklist, and tests-root reminder instead of leaving it in neighboring-surface wording.

Keep the returned shared validator pair `scripts/zigux/validate-phase10.py` and `scripts/zigux/validate-phase10-closure.py` plus the returned `zigux/Makefile` explicit in that directly re-readable anchor set instead of leaving them visible only in the shared build-gate reminder.

Keep `zigux/tests/phase10_virtio_ring_survey.zig` explicit as the returned dedicated ring survey gate beside `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and `zigux/tests/phase10_build.zig` instead of framing that survey replay as a last-known packet member.

Keep the MMIO helper names `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`, `zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig`, and `zigux/tests/phase10_virtio_mmio_survey.zig` explicit beside `Documentation/zigux/phase10-virtio-mmio-survey.md`, `Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`, `Documentation/zigux/phase10-virtio-mmio-slice.md`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `scripts/zigux/check-phase10-mmio-packet.py`, and the shared `zigux/tests/phase10_build.zig` gate on the same narrower basis. Keep that landed apply-observation replay pair framed as helper-local observation evidence rather than transport-backed lifecycle proof.

Keep the returned driver-id pair and those mixed-source returned core companions explicit here, and keep `zigux/tests/phase10_virtio_ring.zig` explicit as the directly re-readable broader ring companion.

Tests-root reviewer prompt:
- keep the blocked risky-transport posture explicit while keeping the now-returned driver-id pair explicit beside the returned core-side companions and `zigux/tests/phase10_virtio_ring.zig` explicit as the directly re-readable broader ring companion.

Keep the queue-local `P10-L10` ring freeze-boundary packet distinct from the bounded `P10-L11` MMIO helper packet when shared reviewer-facing reminders refresh, so the returned ring survey, the helper-local MMIO survey, and their blocked risky-transport wording do not collapse back into one generic freeze-boundary bucket.

Wrapper ownership for the input lane stays split: `drivers/virtio/virtio.zig` owns shared device-status bookkeeping, `drivers/virtio/virtio_ring.zig` owns virtqueue wrapper shape and notification planning, and `drivers/virtio/virtio_mmio.zig` owns MMIO wrapper planning.

Keep the returned driver-id pair and those mixed-source returned core companions explicit here, and keep `zigux/tests/phase10_virtio_ring.zig` explicit as the directly re-readable broader ring companion.

## Phase 11 tests-root packet
"""
    good_tests_root = """# zigux/tests

## Phase 10 shared virtio closure packet

Keep `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, and `scripts/zigux/check-phase10-tests-readme-core-surfaces.py` explicit as the shared Phase 10 tests-root reminder packet.

Keep the returned checker-backed build gate explicit through `scripts/zigux/check-phase10-bootstrap-route.py`, `scripts/zigux/check-phase10-harness-coverage.py`, `scripts/zigux/validate-phase10-closure.py`, `zigux/tests/phase10_closure_manifest.json`, and `zigux/tests/phase10_build.zig` so the tests-root reminder stays aligned with the same bounded closure packet already named by the docs root, the lane-sequencing note, the shared review companion, and the scripts-root Phase 10 packet.

The returned shared build gate now runs through `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, `make -C zigux phase10`.

Current `master` does materialize `zigux/Makefile`, and its live body now exposes the dedicated `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` routes, so keep the returned file and those returned Phase 10 route names explicit as the shared build gate instead of treating them as repo-reality gaps.

Keep the bounded input packet explicit too through `Documentation/zigux/phase10-virtio-input-survey.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, `zigux/tests/phase10_virtio_input_manifest.json`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_probe_preflight.zig`, `drivers/virtio/virtio_input_queue_callback_preflight.zig`, `drivers/virtio/virtio_ring_publish_readiness.zig`, `drivers/virtio/virtio_input_registration_preflight.zig`, `drivers/virtio/virtio_input_status_drain.zig`, `drivers/virtio/virtio_input_teardown_observation.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, and `zigux/tests/phase10_virtio_input_survey.zig` so the tests-root reminder stays aligned with the same bounded input packet already carried by the survey, slice, module-slice, checker, closure manifest, and shared build gate instead of collapsing it back into core-only closure wording.

Keep the queue-callback-preflight, registration-preflight, status-drain, and teardown-observation replays explicit here so the current tests-root packet still records queue-readiness ordering, registration blockers, in-memory status reclamation, and teardown-reset parity without widening into input registration lifecycle closure, transport callbacks, IRQ delivery, or DMA behavior.

Keep the helper-local MMIO replay pair explicit too through `zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig` and `zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig` so the landed apply-observation shard stays reviewable beside `Documentation/zigux/phase10-virtio-mmio-survey.md`, `Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`, `Documentation/zigux/phase10-virtio-mmio-slice.md`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, and `scripts/zigux/check-phase10-mmio-packet.py` without widening into lifecycle, IRQ-delivery, or DMA claims.
"""
    good_scripts_root = """# scripts/zigux

## Phase 10

- Phase 10 flow - the current scripts-root virtio reminder should keep the shared closure packet reviewable through the live closure note, lane-sequencing note, validator-first guide, returned scripts-root guards and validators, the shared build gate, and the bounded core, ring, input, and MMIO companions instead of collapsing the lane into driver-local transport work or older missing-route vocabulary
- `scripts/zigux/check-phase10-bootstrap-route.py`, `scripts/zigux/check-phase10-shared-freeze-boundary.py`, `scripts/zigux/check-phase10-ring-packet.py`, `scripts/zigux/check-phase10-input-packet.py`, `scripts/zigux/check-phase10-mmio-packet.py`, `scripts/zigux/check-phase10-harness-coverage.py`, `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`, `scripts/zigux/validate-phase10.py`, and `scripts/zigux/validate-phase10-closure.py` keep the shipped Phase 10 scripts-root guard and validator packet explicit on current `master`
- `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/phase10_closure_manifest.json`, `.github/workflows/zigux-bootstrap.yml`, and `scripts/zigux/README.md` remain the current reminder-surface companions for that shared closure packet
- `drivers/virtio/virtio_ring_publish_readiness.zig` stays explicit in the returned ring packet so the scripts-root reminder keeps the queue-local publish-readiness wrapper visible beside the other ring companions without widening into transport claims
- `Documentation/zigux/phase10-virtio-core-survey.md`, `zigux/tests/phase10_virtio_core.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, and `zigux/tests/phase10_virtio_core_survey.zig` keep the bounded core packet explicit, and the now-returned exact-path `drivers/virtio/virtio_driver_id.zig` plus `zigux/tests/phase10_virtio_driver_id.zig` pair stays explicit as the narrower core-side follow-through evidence on current `master`
- `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` keep the returned shared build gate explicit from the scripts root instead of treating those routes as missing-current-master gaps
- keep same-lane follow-through narrowed to one shared reminder or checker-backed truthfulness repair at a time; do not widen this scripts-root packet into queue execution parity, IRQ delivery, DMA behavior, input registration lifecycle closure, or risky transport follow-through
"""

    check_companion_text(good_companion)
    check_tests_root_readme(good_tests_root)
    check_scripts_readme(good_scripts_root)

    bad_companion = good_companion.replace(
        "`scripts/zigux/check-phase10-closure-manifest-counts.py`, `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`",
        "`scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`",
        1,
    )
    try:
        check_companion_text(bad_companion)
    except SystemExit as exc:
        assert "companion" in str(exc)
    else:
        raise AssertionError("expected missing returned validator marker failure")

    stale_companion = good_companion.replace(
        "Wrapper ownership for the input lane stays split:",
        "current `master` still does not materialize `scripts/zigux/validate-phase10.py`\nWrapper ownership for the input lane stays split:",
        1,
    )
    try:
        check_companion_text(stale_companion)
    except SystemExit as exc:
        assert "forbidden" in str(exc)
    else:
        raise AssertionError("expected stale missing-validator marker failure")

    stale_ring_companion = good_companion.replace(
        "Keep the returned driver-id pair and those mixed-source returned core companions explicit here, and keep `zigux/tests/phase10_virtio_ring.zig` explicit as the directly re-readable broader ring companion.",
        "Keep the public current-`master` `zigux/tests/phase10_virtio_ring.zig` replay kept explicit as the returned broader ring companion while exact direct-path readback in this runtime still misses it.",
        1,
    )
    try:
        check_companion_text(stale_ring_companion)
    except SystemExit as exc:
        assert "forbidden" in str(exc)
    else:
        raise AssertionError("expected stale ring companion wording failure")

    bad_tests_root = good_tests_root.replace(
        "`make -C zigux phase10-test`",
        "`make -C zigux phase10-test-missing`",
        1,
    )
    try:
        check_tests_root_readme(bad_tests_root)
    except SystemExit as exc:
        assert "tests-root-readme" in str(exc)
    else:
        raise AssertionError("expected tests-root build gate failure")

    bad_tests_root_input = good_tests_root.replace(
        "`drivers/virtio/virtio_input_queue_callback_preflight.zig`",
        "`drivers/virtio/virtio_input_queueCallbackPreflightMissing.zig`",
        1,
    )
    try:
        check_tests_root_readme(bad_tests_root_input)
    except SystemExit as exc:
        assert "tests-root-readme" in str(exc)
    else:
        raise AssertionError("expected tests-root input packet marker failure")

    missing_companion_input_teardown_preflight_helper = good_companion.replace(
        "`drivers/virtio/virtio_input_teardown_preflight.zig`, ",
        "",
        1,
    )
    try:
        check_companion_text(missing_companion_input_teardown_preflight_helper)
    except SystemExit as exc:
        assert "companion" in str(exc)
    else:
        raise AssertionError("expected companion teardown-preflight helper marker failure")

    missing_companion_input_teardown_preflight_replay = good_companion.replace(
        "`zigux/tests/phase10_virtio_input_teardown_preflight.zig`, ",
        "",
        1,
    )
    try:
        check_companion_text(missing_companion_input_teardown_preflight_replay)
    except SystemExit as exc:
        assert "companion" in str(exc)
    else:
        raise AssertionError("expected companion teardown-preflight replay marker failure")

    missing_tests_root_checker = good_tests_root.replace(
        "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
        "`scripts/zigux/check-phase10-tests-readme-core-surfaces-missing.py`",
        1,
    )
    try:
        check_tests_root_readme(missing_tests_root_checker)
    except SystemExit as exc:
        assert "tests-root-readme" in str(exc)
    else:
        raise AssertionError("expected tests-root checker marker failure")

    missing_tests_root_validator = good_tests_root.replace(
        "`scripts/zigux/validate-phase10-closure.py`",
        "`scripts/zigux/validate-phase10-closure-missing.py`",
        1,
    )
    try:
        check_tests_root_readme(missing_tests_root_validator)
    except SystemExit as exc:
        assert "tests-root-readme" in str(exc)
    else:
        raise AssertionError("expected tests-root closure validator marker failure")

    missing_tests_root_ring_publish_readiness = good_tests_root.replace(
        "`drivers/virtio/virtio_ring_publish_readiness.zig`, ",
        "",
        1,
    )
    try:
        check_tests_root_readme(missing_tests_root_ring_publish_readiness)
    except SystemExit as exc:
        assert "tests-root-readme" in str(exc)
    else:
        raise AssertionError("expected tests-root ring publish-readiness marker failure")

    missing_tests_root_mmio_apply_observation_replay = good_tests_root.replace(
        "`zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`",
        "`zigux/tests/phase10_virtio_mmio_apply_observation_replay_missing.zig`",
        1,
    )
    try:
        check_tests_root_readme(missing_tests_root_mmio_apply_observation_replay)
    except SystemExit as exc:
        assert "tests-root-readme" in str(exc)
    else:
        raise AssertionError("expected tests-root mmio apply-observation replay marker failure")

    missing_tests_root_mmio_apply_observation_build = good_tests_root.replace(
        "`zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig`",
        "`zigux/tests/build.phase10_virtio_mmio_apply_observation_replay_missing.zig`",
        1,
    )
    try:
        check_tests_root_readme(missing_tests_root_mmio_apply_observation_build)
    except SystemExit as exc:
        assert "tests-root-readme" in str(exc)
    else:
        raise AssertionError("expected tests-root mmio apply-observation build marker failure")

    bad_scripts_root = good_scripts_root.replace(
        "`scripts/zigux/check-phase10-input-packet.py`",
        "`scripts/zigux/check-phase10-input-packet-missing.py`",
        1,
    )
    try:
        check_scripts_readme(bad_scripts_root)
    except SystemExit as exc:
        assert "scripts-readme" in str(exc)
    else:
        raise AssertionError("expected scripts-root marker failure")

    missing_scripts_ring_guard = good_scripts_root.replace(
        "`scripts/zigux/check-phase10-ring-packet.py`",
        "`scripts/zigux/check-phase10-ring-packet-missing.py`",
        1,
    )
    try:
        check_scripts_readme(missing_scripts_ring_guard)
    except SystemExit as exc:
        assert "scripts-readme" in str(exc)
    else:
        raise AssertionError("expected scripts-root ring-guard marker failure")

    missing_scripts_mmio_guard = good_companion.replace(
        "`zigux/tests/phase10_virtio_mmio_survey.zig`, `scripts/zigux/check-phase10-mmio-packet.py`, and `zigux/tests/phase10_build.zig`",
        "`zigux/tests/phase10_virtio_mmio_survey.zig`, `scripts/zigux/check-phase10-mmio-packet-missing.py`, and `zigux/tests/phase10_build.zig`",
        1,
    )
    try:
        check_companion_text(missing_scripts_mmio_guard)
    except SystemExit as exc:
        assert "companion" in str(exc)
    else:
        raise AssertionError("expected companion mmio-guard marker failure")

    missing_scripts_validator = good_scripts_root.replace(
        "`scripts/zigux/validate-phase10.py`, and `scripts/zigux/validate-phase10-closure.py`",
        "`scripts/zigux/validate-phase10-closure.py`",
        1,
    )
    try:
        check_scripts_readme(missing_scripts_validator)
    except SystemExit as exc:
        assert "scripts-readme" in str(exc)
    else:
        raise AssertionError("expected scripts-root validator-pair marker failure")

    bad_mmio_companion = good_companion.replace(
        "`Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`",
        "`Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion-missing.md`",
        2,
    )
    try:
        check_companion_text(bad_mmio_companion)
    except SystemExit as exc:
        assert "companion" in str(exc)
    else:
        raise AssertionError("expected missing mmio companion marker failure")

    missing_mmio_manifest_companion = good_companion.replace(
        "`zigux/tests/phase10_virtio_mmio_manifest.json`",
        "`zigux/tests/phase10_virtio_mmio_manifest_missing.json`",
        1,
    )
    try:
        check_companion_text(missing_mmio_manifest_companion)
    except SystemExit as exc:
        assert "companion" in str(exc)
    else:
        raise AssertionError("expected missing mmio manifest marker failure")

    bad_guide_companion = good_companion.replace(
        "`Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md`, ",
        "",
        1,
    )
    try:
        check_companion_text(bad_guide_companion)
    except SystemExit as exc:
        assert "companion" in str(exc)
    else:
        raise AssertionError("expected missing validator-first guide marker failure")

    bad_core_replay_companion = good_companion.replace(
        ", `zigux/tests/phase10_virtio_core.zig`, and `zigux/tests/phase10_closure_manifest.json`",
        ", and `zigux/tests/phase10_closure_manifest.json`",
        1,
    )
    try:
        check_companion_text(bad_core_replay_companion)
    except SystemExit as exc:
        assert "companion" in str(exc)
    else:
        raise AssertionError("expected missing returned core replay marker failure")

    bad_ring_publish_readiness_companion = good_companion.replace(
        "`drivers/virtio/virtio_ring_publish_readiness.zig`, ",
        "",
        1,
    )
    try:
        check_companion_text(bad_ring_publish_readiness_companion)
    except SystemExit as exc:
        assert "companion" in str(exc)
    else:
        raise AssertionError("expected missing ring publish-readiness marker failure")

    bad_ring_companion = good_companion.replace(
        "Keep the returned driver-id pair and those mixed-source returned core companions explicit here, and keep `zigux/tests/phase10_virtio_ring.zig` explicit as the directly re-readable broader ring companion.",
        "Keep the returned driver-id pair and those mixed-source returned core companions explicit here, and keep `zigux/tests/phase10_virtio_ring_missing.zig` explicit as the directly re-readable broader ring companion.",
    )
    try:
        check_companion_text(bad_ring_companion)
    except SystemExit as exc:
        assert "companion" in str(exc)
    else:
        raise AssertionError("expected missing returned broader ring companion marker failure")

    missing_driver_id_companion = good_companion.replace(
        "current direct lane readback now rematerializes `drivers/virtio/virtio_driver_id.zig` and `zigux/tests/phase10_virtio_driver_id.zig`",
        "current direct lane readback now rematerializes `drivers/virtio/virtio_driver_id.zig`",
        1,
    )
    try:
        check_companion_text(missing_driver_id_companion)
    except SystemExit as exc:
        assert "companion" in str(exc)
    else:
        raise AssertionError("expected missing driver-id pair companion marker failure")

    stale_scripts_root = good_scripts_root.replace(
        "and the now-returned exact-path `drivers/virtio/virtio_driver_id.zig` plus `zigux/tests/phase10_virtio_driver_id.zig` pair stays explicit as the narrower core-side follow-through evidence on current `master`",
        "while only `drivers/virtio/virtio_driver_id.zig` and `zigux/tests/phase10_virtio_driver_id.zig` remain the narrower core-side repo-reality gaps on current `master`",
        1,
    )
    try:
        check_scripts_readme(stale_scripts_root)
    except SystemExit as exc:
        assert "scripts-readme" in str(exc)
    else:
        raise AssertionError("expected stale scripts-root driver-id gap failure")

    missing_driver_id_scripts = good_scripts_root.replace(
        "`drivers/virtio/virtio_driver_id.zig` plus `zigux/tests/phase10_virtio_driver_id.zig` pair",
        "`drivers/virtio/virtio_driver_id.zig` pair",
        1,
    )
    try:
        check_scripts_readme(missing_driver_id_scripts)
    except SystemExit as exc:
        assert "scripts-readme" in str(exc)
    else:
        raise AssertionError("expected missing driver-id pair scripts-root marker failure")

    missing_direct_anchor_validator_pair = good_companion.replace(
        "Keep the returned shared validator pair `scripts/zigux/validate-phase10.py` and `scripts/zigux/validate-phase10-closure.py` plus the returned `zigux/Makefile` explicit in that directly re-readable anchor set instead of leaving them visible only in the shared build-gate reminder.",
        "Keep the returned shared validator pair `scripts/zigux/validate-phase10.py` explicit in that directly re-readable anchor set instead of leaving it visible only in the shared build-gate reminder.",
        1,
    )
    try:
        check_companion_text(missing_direct_anchor_validator_pair)
    except SystemExit as exc:
        assert "companion" in str(exc)
    else:
        raise AssertionError("expected missing direct-anchor validator pair marker failure")

    missing_ring_survey_gate = good_companion.replace(
        "Keep `zigux/tests/phase10_virtio_ring_survey.zig` explicit as the returned dedicated ring survey gate beside `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and `zigux/tests/phase10_build.zig` instead of framing that survey replay as a last-known packet member.",
        "Keep `zigux/tests/phase10_virtio_ring_survey_missing.zig` explicit as the returned dedicated ring survey gate beside `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and `zigux/tests/phase10_build.zig` instead of framing that survey replay as a last-known packet member.",
        1,
    )
    try:
        check_companion_text(missing_ring_survey_gate)
    except SystemExit as exc:
        assert "companion" in str(exc)
    else:
        raise AssertionError("expected missing ring survey gate marker failure")

    missing_companion_mmio_apply_replay = good_companion.replace(
        "`zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`",
        "`zigux/tests/phase10_virtio_mmio_apply_observation_replay_missing.zig`",
        1,
    )
    try:
        check_companion_text(missing_companion_mmio_apply_replay)
    except SystemExit as exc:
        assert "companion" in str(exc)
    else:
        raise AssertionError("expected companion mmio apply-observation replay marker failure")

    missing_companion_mmio_apply_build = good_companion.replace(
        "`zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig`",
        "`zigux/tests/build.phase10_virtio_mmio_apply_observation_replay_missing.zig`",
        1,
    )
    try:
        check_companion_text(missing_companion_mmio_apply_build)
    except SystemExit as exc:
        assert "companion" in str(exc)
    else:
        raise AssertionError("expected companion mmio apply-observation build marker failure")

    missing_mmio_observation_boundary = good_companion.replace(
        "Keep that landed apply-observation replay pair framed as helper-local observation evidence rather than transport-backed lifecycle proof.",
        "Keep that landed apply-observation replay pair framed as transport-backed lifecycle proof.",
        1,
    )
    try:
        check_companion_text(missing_mmio_observation_boundary)
    except SystemExit as exc:
        assert "companion" in str(exc)
    else:
        raise AssertionError("expected missing mmio observation-boundary marker failure")

    missing_ring_mmio_lane_split = good_companion.replace(
        "Keep the queue-local `P10-L10` ring freeze-boundary packet distinct from the bounded `P10-L11` MMIO helper packet when shared reviewer-facing reminders refresh, so the returned ring survey, the helper-local MMIO survey, and their blocked risky-transport wording do not collapse back into one generic freeze-boundary bucket.",
        "Keep the queue-local Phase 10 freeze-boundary packet aligned when shared reviewer-facing reminders refresh.",
        1,
    )
    try:
        check_companion_text(missing_ring_mmio_lane_split)
    except SystemExit as exc:
        assert "companion" in str(exc)
    else:
        raise AssertionError("expected missing ring-mmio lane split marker failure")

    missing_ring_publish_readiness_scripts = good_scripts_root.replace(
        "`drivers/virtio/virtio_ring_publish_readiness.zig`",
        "`drivers/virtio/virtio_ring_publish_readiness_missing.zig`",
        1,
    )
    try:
        check_scripts_readme(missing_ring_publish_readiness_scripts)
    except SystemExit as exc:
        assert "scripts-readme" in str(exc)
    else:
        raise AssertionError("expected missing ring publish-readiness scripts-root marker failure")

    print("PHASE10_TESTS_ROOT_COMPANION_CHECKER_SELF_TEST=pass")
    print("PHASE10_TESTS_ROOT_COMPANION_CHECKER_SELF_TEST_CASE_COUNT=34")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--source", type=Path, default=SURFACE_PATH)
    parser.add_argument("--tests-root-readme", type=Path, default=TESTS_ROOT_README_PATH)
    parser.add_argument("--scripts-readme", type=Path, default=SCRIPTS_README_PATH)
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
