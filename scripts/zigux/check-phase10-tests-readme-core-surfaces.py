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
SCRIPTS_PHASE10_START = "## Phase 10"
SCRIPTS_PHASE10_END = "## Phase 12"


COMPANION_REQUIRED_MARKERS = (
    "Keep the current bounded virtio closure packet explicit through the shared reminder surfaces",
    "`scripts/zigux/check-phase10-bootstrap-route.py`",
    "`scripts/zigux/check-phase10-core-packet.py`",
    "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
    "`scripts/zigux/check-phase10-closure-manifest-counts.py`",
    "`Documentation/zigux/phase10-virtio-ring-survey.md`",
    "`drivers/virtio/virtio_ring_publish_readiness.zig`",
    "`zigux/tests/phase10_virtio_ring_survey.zig`",
    "`Documentation/zigux/phase10-virtio-input-module-slice.md`",
    "`drivers/virtio/virtio_input_queue_callback_preflight.zig`",
    "`drivers/virtio/virtio_input_teardown_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_teardown_preflight.zig`",
    "`Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`",
    "`zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`",
    "`zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig`",
    "`scripts/zigux/validate-phase10.py`",
    "`scripts/zigux/validate-phase10-closure.py`",
    "`zigux/tests/phase10_closure_manifest.json`",
    "The returned shared build gate now runs through `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, `make -C zigux phase10`, and `zigux/tests/phase10_build.zig`.",
    "current direct lane readback now rematerializes `drivers/virtio/virtio_driver_id.zig` and `zigux/tests/phase10_virtio_driver_id.zig`",
    "Keep the queue-local `P10-L10` ring freeze-boundary packet distinct from the bounded `P10-L11` MMIO helper packet",
    "`drivers/virtio/virtio.zig` owns shared device-status bookkeeping",
    "`drivers/virtio/virtio_ring.zig` owns virtqueue wrapper shape and notification planning",
    "`drivers/virtio/virtio_mmio.zig` owns MMIO wrapper planning",
)

COMPANION_FORBIDDEN_MARKERS = (
    "current `master` still does not materialize `scripts/zigux/validate-phase10.py`",
    "current direct lane readback still does not materialize `drivers/virtio/virtio_driver_id.zig`",
    "last-known packet member",
)

TESTS_ROOT_REQUIRED_MARKERS = (
    "`Documentation/zigux/phase10-closure-evidence.md`",
    "`Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`",
    "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
    "`scripts/zigux/check-phase10-bootstrap-route.py`",
    "`scripts/zigux/check-phase10-harness-coverage.py`",
    "`scripts/zigux/validate-phase10-closure.py`",
    "`zigux/tests/phase10_closure_manifest.json`",
    "The returned shared build gate now runs through `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, `make -C zigux phase10`.",
    "`Documentation/zigux/phase10-virtio-input-module-slice.md`",
    "`drivers/virtio/virtio_input_queue_callback_preflight.zig`",
    "`drivers/virtio/virtio_input_teardown_preflight.zig`",
    "`drivers/virtio/virtio_ring_publish_readiness.zig`",
    "`zigux/tests/phase10_virtio_input_teardown_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_teardown_observation.zig`",
    "queue-callback-preflight, registration-preflight, teardown-preflight, status-drain, and teardown-observation replays explicit here",
    "`zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`",
    "`zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig`",
    "without widening into lifecycle, IRQ-delivery, or DMA claims",
)

SCRIPTS_ROOT_REQUIRED_MARKERS = (
    "`scripts/zigux/check-phase10-ring-packet.py`",
    "`scripts/zigux/check-phase10-input-packet.py`",
    "`scripts/zigux/check-phase10-mmio-packet.py`",
    "`scripts/zigux/check-phase10-harness-coverage.py`",
    "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
    "`scripts/zigux/validate-phase10.py`",
    "`scripts/zigux/validate-phase10-closure.py`",
    "`drivers/virtio/virtio_ring_publish_readiness.zig`",
    "`Documentation/zigux/phase10-virtio-core-survey.md`, `zigux/tests/phase10_virtio_core.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, and `zigux/tests/phase10_virtio_core_survey.zig` keep the bounded core packet explicit",
    "`drivers/virtio/virtio_driver_id.zig` plus `zigux/tests/phase10_virtio_driver_id.zig` pair stays explicit",
    "`zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` keep the returned shared build gate explicit",
    "do not widen this scripts-root packet into queue execution parity, IRQ delivery, DMA behavior, input registration lifecycle closure, or risky transport follow-through",
)

SCRIPTS_ROOT_FORBIDDEN_MARKERS = (
    "remain the narrower core-side repo-reality gaps on current `master`",
)


def section(text: str, start_marker: str, end_marker: str) -> str:
    start = text.find(start_marker)
    if start == -1:
        raise SystemExit(f"missing section heading: {start_marker}")
    end = text.find(end_marker, start)
    if end == -1:
        raise SystemExit(f"missing section heading: {end_marker}")
    return text[start:end]


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"missing {label} markers: " + ", ".join(missing))


def forbid_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    present = [marker for marker in markers if marker in text]
    if present:
        raise SystemExit(f"found forbidden {label} markers: " + ", ".join(present))


def check_companion_text(text: str) -> None:
    phase10 = section(text, PHASE10_START, PHASE10_END)
    require_markers(phase10, COMPANION_REQUIRED_MARKERS, "companion")
    forbid_markers(phase10, COMPANION_FORBIDDEN_MARKERS, "companion")


def check_tests_root_readme(text: str) -> None:
    require_markers(text, TESTS_ROOT_REQUIRED_MARKERS, "tests-root-readme")


def check_scripts_readme(text: str) -> None:
    phase10 = section(text, SCRIPTS_PHASE10_START, SCRIPTS_PHASE10_END)
    require_markers(phase10, SCRIPTS_ROOT_REQUIRED_MARKERS, "scripts-readme")
    forbid_markers(phase10, SCRIPTS_ROOT_FORBIDDEN_MARKERS, "scripts-readme")


def run_self_test() -> int:
    good_companion = """# Companion

## Phase 10 tests-root packet
Keep the current bounded virtio closure packet explicit through the shared reminder surfaces.
`scripts/zigux/check-phase10-bootstrap-route.py`
`scripts/zigux/check-phase10-core-packet.py`
`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`
`scripts/zigux/check-phase10-closure-manifest-counts.py`
`Documentation/zigux/phase10-virtio-ring-survey.md`
`drivers/virtio/virtio_ring_publish_readiness.zig`
`zigux/tests/phase10_virtio_ring_survey.zig`
`Documentation/zigux/phase10-virtio-input-module-slice.md`
`drivers/virtio/virtio_input_queue_callback_preflight.zig`
`drivers/virtio/virtio_input_teardown_preflight.zig`
`zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`
`zigux/tests/phase10_virtio_input_teardown_preflight.zig`
`Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`
`zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`
`zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig`
`scripts/zigux/validate-phase10.py`
`scripts/zigux/validate-phase10-closure.py`
`zigux/tests/phase10_closure_manifest.json`
The returned shared build gate now runs through `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, `make -C zigux phase10`, and `zigux/tests/phase10_build.zig`.
current direct lane readback now rematerializes `drivers/virtio/virtio_driver_id.zig` and `zigux/tests/phase10_virtio_driver_id.zig`
Keep the queue-local `P10-L10` ring freeze-boundary packet distinct from the bounded `P10-L11` MMIO helper packet
`drivers/virtio/virtio.zig` owns shared device-status bookkeeping
`drivers/virtio/virtio_ring.zig` owns virtqueue wrapper shape and notification planning
`drivers/virtio/virtio_mmio.zig` owns MMIO wrapper planning

## Phase 11 tests-root packet
"""
    good_tests_root = """# Tests
`Documentation/zigux/phase10-closure-evidence.md`
`Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`
`scripts/zigux/check-phase10-bootstrap-route.py`
`scripts/zigux/check-phase10-harness-coverage.py`
`scripts/zigux/validate-phase10-closure.py`
`zigux/tests/phase10_closure_manifest.json`
The returned shared build gate now runs through `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, `make -C zigux phase10`.
`Documentation/zigux/phase10-virtio-input-module-slice.md`
`drivers/virtio/virtio_input_queue_callback_preflight.zig`
`drivers/virtio/virtio_input_teardown_preflight.zig`
`drivers/virtio/virtio_ring_publish_readiness.zig`
`zigux/tests/phase10_virtio_input_teardown_preflight.zig`
`zigux/tests/phase10_virtio_input_teardown_observation.zig`
queue-callback-preflight, registration-preflight, teardown-preflight, status-drain, and teardown-observation replays explicit here
`zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`
`zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig`
without widening into lifecycle, IRQ-delivery, or DMA claims
"""
    good_scripts = """# Scripts

## Phase 10
`scripts/zigux/check-phase10-ring-packet.py`
`scripts/zigux/check-phase10-input-packet.py`
`scripts/zigux/check-phase10-mmio-packet.py`
`scripts/zigux/check-phase10-harness-coverage.py`
`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`
`scripts/zigux/validate-phase10.py`
`scripts/zigux/validate-phase10-closure.py`
`drivers/virtio/virtio_ring_publish_readiness.zig`
`Documentation/zigux/phase10-virtio-core-survey.md`, `zigux/tests/phase10_virtio_core.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, and `zigux/tests/phase10_virtio_core_survey.zig` keep the bounded core packet explicit
`drivers/virtio/virtio_driver_id.zig` plus `zigux/tests/phase10_virtio_driver_id.zig` pair stays explicit
`zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` keep the returned shared build gate explicit
do not widen this scripts-root packet into queue execution parity, IRQ delivery, DMA behavior, input registration lifecycle closure, or risky transport follow-through

## Phase 12
"""

    check_companion_text(good_companion)
    check_tests_root_readme(good_tests_root)
    check_scripts_readme(good_scripts)

    try:
        check_companion_text(good_companion.replace("`scripts/zigux/check-phase10-core-packet.py`\n", "", 1))
    except SystemExit:
        pass
    else:
        raise AssertionError("expected companion marker failure")

    try:
        check_tests_root_readme(good_tests_root.replace("`zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig`\n", "", 1))
    except SystemExit:
        pass
    else:
        raise AssertionError("expected tests-root marker failure")

    try:
        check_tests_root_readme(good_tests_root.replace("`drivers/virtio/virtio_input_teardown_preflight.zig`\n", "", 1))
    except SystemExit:
        pass
    else:
        raise AssertionError("expected teardown-preflight helper marker failure")

    try:
        check_tests_root_readme(good_tests_root.replace("`zigux/tests/phase10_virtio_input_teardown_preflight.zig`\n", "", 1))
    except SystemExit:
        pass
    else:
        raise AssertionError("expected teardown-preflight replay marker failure")

    try:
        check_scripts_readme(good_scripts.replace("pair stays explicit", "pair remain the narrower core-side repo-reality gaps on current `master`", 1))
    except SystemExit:
        pass
    else:
        raise AssertionError("expected scripts-root forbidden marker failure")

    print("PHASE10_TESTS_ROOT_COMPANION_CHECKER_SELF_TEST=pass")
    print("PHASE10_TESTS_ROOT_COMPANION_CHECKER_SELF_TEST_CASE_COUNT=8")
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