#!/usr/bin/env python3
"""Check that the Phase 10 tests-root reminder keeps direct virtio core surfaces explicit."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

TESTS_README_PATH = Path("zigux/tests/README.md")
PHASE10_PREFIX = "  * keep the active Phase 10 virtio packet explicit in the tests root too:"

REQUIRED_SURFACES = (
    "`drivers/virtio/virtio.zig`",
    "`drivers/virtio/virtio_driver_id.zig`",
)

REQUIRED_CONTEXT = (
    "`scripts/zigux/check-phase10-harness-coverage.py`",
    "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
    "`scripts/zigux/validate-phase10.py`",
    "`scripts/zigux/validate-phase10-closure.py`",
    "`zigux/tests/phase10_closure_manifest.json`",
    "`zigux/tests/phase10_virtio_core.zig`",
    "`zigux/tests/phase10_virtio_core_reset_queue.zig`",
    "`zigux/tests/phase10_virtio_driver_id.zig`",
    "`drivers/virtio/virtio_verify.zig`",
    "`zigux/tests/phase10_virtio_ring.zig`",
    "`zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
    "`drivers/virtio/virtio_ring_verify.zig`",
    "`zigux/tests/phase10_virtio_input.zig`",
    "`drivers/virtio/virtio_input_verify.zig`",
    "`zigux/tests/phase10_virtio_mmio.zig`",
    "`drivers/virtio/virtio_mmio_verify.zig`",
    "`make -C zigux phase10-validate`",
    "`zig build test --build-file zigux/tests/phase10_build.zig`",
    "`make -C zigux phase10-test`",
    "`make -C zigux phase10`",
)

REQUIRED_SUMMARY_MARKERS = (
    "the current virtio core, the direct `drivers/virtio/virtio.zig` plus "
    "`drivers/virtio/virtio_driver_id.zig` review surfaces, the bounded reset replay",
    "the lane-sequenced virtio ring plus the focused `drivers/virtio/virtio_ring_verify.zig` "
    "and `zigux/tests/phase10_virtio_ring_reset_reuse.zig` drained-reset reuse replays",
)

EXPECTED_SURFACE_COUNTS = {
    "`drivers/virtio/virtio.zig`": 2,
    "`drivers/virtio/virtio_driver_id.zig`": 2,
}


def phase10_line(text: str) -> str:
    matches = [line for line in text.splitlines() if line.startswith(PHASE10_PREFIX)]
    if len(matches) != 1:
        raise SystemExit(
            "phase10 tests-readme core-surfaces checker expected exactly one "
            f"Phase 10 tests-root line, found {len(matches)}"
        )
    return matches[0]


def check_line(line: str) -> None:
    missing = [marker for marker in REQUIRED_SURFACES + REQUIRED_CONTEXT if marker not in line]
    if missing:
        raise SystemExit(
            "phase10 tests-readme core-surfaces checker missing markers: "
            + ", ".join(missing)
        )
    for marker in REQUIRED_SUMMARY_MARKERS:
        if marker not in line:
            raise SystemExit(
                "phase10 tests-readme core-surfaces checker missing summary marker: "
                + marker
            )
    for marker, expected_count in EXPECTED_SURFACE_COUNTS.items():
        if line.count(marker) != expected_count:
            raise SystemExit(
                "phase10 tests-readme core-surfaces checker expected exactly "
                f"{expected_count} occurrences of {marker}, found {line.count(marker)}"
            )


def check_text(text: str) -> None:
    check_line(phase10_line(text))


def run_self_test() -> int:
    good_line = (
        "  * keep the active Phase 10 virtio packet explicit in the tests root too: "
        "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, "
        "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, "
        "`Documentation/zigux/phase10-closure-evidence.md`, `scripts/zigux/README.md`, "
        "`Documentation/zigux/phase10-virtio-core-slice.md`, "
        "`Documentation/zigux/phase10-virtio-core-survey.md`, "
        "`Documentation/zigux/phase10-virtio-ring-slice.md`, "
        "`Documentation/zigux/phase10-virtio-ring-survey.md`, "
        "`Documentation/zigux/phase10-virtio-input-slice.md`, "
        "`Documentation/zigux/phase10-virtio-input-module-slice.md`, "
        "`Documentation/zigux/phase10-virtio-input-survey.md`, "
        "`Documentation/zigux/phase10-virtio-mmio-slice.md`, "
        "`Documentation/zigux/phase10-virtio-mmio-survey.md`, "
        "`Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, "
        "`scripts/zigux/check-phase10-core-packet.py`, "
        "`scripts/zigux/check-phase10-ring-packet.py`, "
        "`scripts/zigux/check-phase10-input-packet.py`, "
        "`scripts/zigux/check-phase10-mmio-packet.py`, "
        "`scripts/zigux/check-phase10-mmio-freeze-boundary.py`, "
        "`scripts/zigux/check-phase10-harness-coverage.py`, "
        "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`, "
        "`scripts/zigux/validate-phase10.py`, "
        "`scripts/zigux/validate-phase10-closure.py`, "
        "`zigux/tests/phase10_build.zig`, `zigux/tests/phase10_closure_manifest.json`, "
        "`drivers/virtio/virtio.zig`, `drivers/virtio/virtio_driver_id.zig`, "
        "`zigux/tests/phase10_virtio_core.zig`, "
        "`zigux/tests/phase10_virtio_core_reset_queue.zig`, "
        "`zigux/tests/phase10_virtio_core_manifest.json`, "
        "`zigux/tests/phase10_virtio_core_survey.zig`, "
        "`zigux/tests/phase10_virtio_driver_id.zig`, "
        "`drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_ring.zig`, "
        "`drivers/virtio/virtio_ring_verify.zig`, "
        "`zigux/tests/phase10_virtio_ring_manifest.json`, "
        "`zigux/tests/phase10_virtio_ring_survey.zig`, "
        "`zigux/tests/phase10_virtio_ring_reset_reuse.zig`, "
        "`zigux/tests/phase10_virtio_input.zig`, "
        "`drivers/virtio/virtio_input_verify.zig`, "
        "`zigux/tests/phase10_virtio_input_probe_preflight.zig`, "
        "`zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, "
        "`zigux/tests/phase10_virtio_input_registration_preflight.zig`, "
        "`zigux/tests/phase10_virtio_input_teardown_observation.zig`, "
        "`zigux/tests/phase10_virtio_input_status_drain.zig`, "
        "`zigux/tests/phase10_virtio_input_manifest.json`, "
        "`zigux/tests/phase10_virtio_input_survey.zig`, "
        "`zigux/tests/phase10_virtio_mmio.zig`, "
        "`drivers/virtio/virtio_mmio_verify.zig`, "
        "`zigux/tests/phase10_virtio_mmio_manifest.json`, "
        "`zigux/tests/phase10_virtio_mmio_survey.zig`, `zigux/Makefile`, "
        "`make -C zigux phase10-validate`, "
        "`zig build test --build-file zigux/tests/phase10_build.zig`, "
        "`make -C zigux phase10-test`, and `make -C zigux phase10` should continue "
        "to keep the current virtio core, the direct `drivers/virtio/virtio.zig` plus "
        "`drivers/virtio/virtio_driver_id.zig` review surfaces, the bounded reset replay, "
        "core survey, the focused core-verify replay, the lane-sequenced virtio ring "
        "plus the focused `drivers/virtio/virtio_ring_verify.zig` and "
        "`zigux/tests/phase10_virtio_ring_reset_reuse.zig` drained-reset reuse replays, "
        "the lane-sequenced virtio input plus the focused input-verify, probe-preflight, "
        "queue-callback-preflight, registration-preflight, teardown-observation, and "
        "status-drain replays, and the virtio mmio packet plus the focused mmio-verify replay"
    )
    good = "# zigux/tests\n\nGuidance\n" + good_line + "\n"
    check_text(good)

    missing_surfaces = good.replace(
        "`drivers/virtio/virtio.zig`, `drivers/virtio/virtio_driver_id.zig`, ", "", 1
    )
    try:
        check_text(missing_surfaces)
    except SystemExit as exc:
        message = str(exc)
        assert "missing markers" in message or "expected exactly 2 occurrences" in message
    else:
        raise AssertionError("expected missing direct surfaces failure")

    missing_closure_manifest = good.replace(
        "`zigux/tests/phase10_build.zig`, `zigux/tests/phase10_closure_manifest.json`, ",
        "`zigux/tests/phase10_build.zig`, ",
        1,
    )
    try:
        check_text(missing_closure_manifest)
    except SystemExit as exc:
        assert "`zigux/tests/phase10_closure_manifest.json`" in str(exc)
    else:
        raise AssertionError("expected missing closure manifest failure")

    missing_core_surfaces_checker = good.replace(
        "`scripts/zigux/check-phase10-harness-coverage.py`, "
        "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`, ",
        "`scripts/zigux/check-phase10-harness-coverage.py`, ",
        1,
    )
    try:
        check_text(missing_core_surfaces_checker)
    except SystemExit as exc:
        assert "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`" in str(exc)
    else:
        raise AssertionError("expected missing direct checker failure")

    missing_phase10_validate = good.replace(
        "`scripts/zigux/validate-phase10.py`, ",
        "",
        1,
    )
    try:
        check_text(missing_phase10_validate)
    except SystemExit as exc:
        assert "`scripts/zigux/validate-phase10.py`" in str(exc)
    else:
        raise AssertionError("expected missing shared validator failure")

    missing_phase10_closure_validate = good.replace(
        "`scripts/zigux/validate-phase10-closure.py`, ",
        "",
        1,
    )
    try:
        check_text(missing_phase10_closure_validate)
    except SystemExit as exc:
        assert "`scripts/zigux/validate-phase10-closure.py`" in str(exc)
    else:
        raise AssertionError("expected missing shared closure validator failure")

    missing_phase10_validate_route = good.replace(
        "`make -C zigux phase10-validate`, ",
        "",
        1,
    )
    try:
        check_text(missing_phase10_validate_route)
    except SystemExit as exc:
        assert "`make -C zigux phase10-validate`" in str(exc)
    else:
        raise AssertionError("expected missing phase10-validate route failure")

    duplicate_surface = good.replace(
        "`drivers/virtio/virtio.zig`",
        "`drivers/virtio/virtio.zig`, `drivers/virtio/virtio.zig`",
        1,
    )
    try:
        check_text(duplicate_surface)
    except SystemExit as exc:
        assert "expected exactly 2 occurrences" in str(exc)
    else:
        raise AssertionError("expected duplicate direct surface failure")

    missing_summary = good.replace(
        "the current virtio core, the direct `drivers/virtio/virtio.zig` plus "
        "`drivers/virtio/virtio_driver_id.zig` review surfaces, the bounded reset replay, ",
        "the current virtio core, the bounded reset replay, ",
        1,
    )
    try:
        check_text(missing_summary)
    except SystemExit as exc:
        assert "missing summary marker" in str(exc)
    else:
        raise AssertionError("expected direct-surface summary failure")

    missing_ring_reset_reuse_entry = good.replace(
        "`zigux/tests/phase10_virtio_ring_survey.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, ",
        "`zigux/tests/phase10_virtio_ring_survey.zig`, ",
        1,
    ).replace(
        "`zigux/tests/phase10_virtio_ring_reset_reuse.zig` drained-reset reuse replays",
        "ring drained-reset reuse replays",
        1,
    )
    try:
        check_text(missing_ring_reset_reuse_entry)
    except SystemExit as exc:
        assert "`zigux/tests/phase10_virtio_ring_reset_reuse.zig`" in str(exc)
    else:
        raise AssertionError("expected ring reset reuse marker failure")

    missing_ring_reset_reuse_summary = good.replace(
        "the lane-sequenced virtio ring plus the focused `drivers/virtio/virtio_ring_verify.zig` and "
        "`zigux/tests/phase10_virtio_ring_reset_reuse.zig` drained-reset reuse replays, ",
        "the lane-sequenced virtio ring plus the focused `drivers/virtio/virtio_ring_verify.zig` replay, ",
        1,
    )
    try:
        check_text(missing_ring_reset_reuse_summary)
    except SystemExit as exc:
        assert "`zigux/tests/phase10_virtio_ring_reset_reuse.zig` drained-reset reuse replays" in str(exc)
    else:
        raise AssertionError("expected ring reset reuse summary failure")

    print("PHASE10_TESTS_README_CORE_SURFACES_CHECKER_SELF_TEST=pass")
    print("PHASE10_TESTS_README_CORE_SURFACES_CHECKER_SELF_TEST_CASE_COUNT=11")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--source",
        type=Path,
        default=TESTS_README_PATH,
        help="path to zigux/tests/README.md",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    text = args.source.read_text(encoding="utf-8")
    check_text(text)
    print("PHASE10_TESTS_README_CORE_SURFACES_CHECK=pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
