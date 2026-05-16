#!/usr/bin/env python3
"""Check that the Phase 10 tests-root flow keeps direct virtio core and ring surfaces explicit."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

TESTS_README_PATH = Path("zigux/tests/README.md")
PHASE10_START = "Phase 10 flow"
PHASE10_END = "Phase 11 review packet"

REQUIRED_MARKERS = (
    "`zigux/tests/phase10_build.zig`",
    "`zigux/tests/phase10_virtio_core.zig`",
    "`zigux/tests/phase10_virtio_core_reset_queue.zig`",
    "`zigux/tests/phase10_virtio_core_survey.zig`",
    "`zigux/tests/phase10_virtio_core_manifest.json`",
    "`zigux/tests/phase10_virtio_driver_id.zig`",
    "`zigux/tests/phase10_virtio_ring.zig`",
    "`zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
    "`zigux/tests/phase10_virtio_ring_survey.zig`",
    "`zigux/tests/phase10_virtio_ring_manifest.json`",
    "`zigux/tests/phase10_virtio_input_probe_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_registration_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_teardown_observation.zig`",
    "`zigux/tests/phase10_virtio_input_status_drain.zig`",
    "`zigux/tests/phase10_virtio_input_manifest.json`",
    "`zigux/tests/phase10_virtio_mmio.zig`",
    "`zigux/tests/phase10_virtio_mmio_survey.zig`",
    "`zigux/tests/phase10_virtio_mmio_manifest.json`",
)

EXPECTED_MARKER_COUNTS = {
    "`zigux/tests/phase10_build.zig`": 1,
    "`zigux/tests/phase10_virtio_core.zig`": 1,
    "`zigux/tests/phase10_virtio_ring.zig`": 1,
    "`zigux/tests/phase10_virtio_input_probe_preflight.zig`": 1,
    "`zigux/tests/phase10_virtio_mmio_manifest.json`": 1,
}


def phase10_section(text: str) -> str:
    start = text.find(PHASE10_START)
    if start == -1:
        raise SystemExit(
            "phase10 tests-readme core-surfaces checker missing `Phase 10 flow` section heading"
        )

    end = text.find(PHASE10_END, start)
    if end == -1:
        raise SystemExit(
            "phase10 tests-readme core-surfaces checker missing `Phase 11 review packet` section heading"
        )

    return text[start:end]


def check_section(section: str) -> None:
    missing = [marker for marker in REQUIRED_MARKERS if marker not in section]
    if missing:
        raise SystemExit(
            "phase10 tests-readme core-surfaces checker missing markers: "
            + ", ".join(missing)
        )

    for marker, expected_count in EXPECTED_MARKER_COUNTS.items():
        actual_count = section.count(marker)
        if actual_count != expected_count:
            raise SystemExit(
                "phase10 tests-readme core-surfaces checker expected exactly "
                f"{expected_count} occurrences of {marker}, found {actual_count}"
            )


def check_text(text: str) -> None:
    check_section(phase10_section(text))


def run_self_test() -> int:
    good = """# zigux/tests

Phase 10 flow

  * `zigux/tests/phase10_build.zig`
  * `zigux/tests/phase10_virtio_core.zig`
  * `zigux/tests/phase10_virtio_core_reset_queue.zig`
  * `zigux/tests/phase10_virtio_core_survey.zig`
  * `zigux/tests/phase10_virtio_core_manifest.json`
  * `zigux/tests/phase10_virtio_driver_id.zig`
  * `zigux/tests/phase10_virtio_ring.zig`
  * `zigux/tests/phase10_virtio_ring_reset_reuse.zig`
  * `zigux/tests/phase10_virtio_ring_survey.zig`
  * `zigux/tests/phase10_virtio_ring_manifest.json`
  * `zigux/tests/phase10_virtio_input_probe_preflight.zig`
  * `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`
  * `zigux/tests/phase10_virtio_input_registration_preflight.zig`
  * `zigux/tests/phase10_virtio_input_teardown_observation.zig`
  * `zigux/tests/phase10_virtio_input_status_drain.zig`
  * `zigux/tests/phase10_virtio_input_manifest.json`
  * `zigux/tests/phase10_virtio_mmio.zig`
  * `zigux/tests/phase10_virtio_mmio_survey.zig`
  * `zigux/tests/phase10_virtio_mmio_manifest.json`

Phase 11 review packet
"""
    check_text(good)

    missing_phase10_heading = good.replace("Phase 10 flow", "Phase Ten flow", 1)
    try:
        check_text(missing_phase10_heading)
    except SystemExit as exc:
        assert "`Phase 10 flow`" in str(exc)
    else:
        raise AssertionError("expected missing Phase 10 heading failure")

    missing_phase11_heading = good.replace("Phase 11 review packet", "Phase Eleven review packet", 1)
    try:
        check_text(missing_phase11_heading)
    except SystemExit as exc:
        assert "`Phase 11 review packet`" in str(exc)
    else:
        raise AssertionError("expected missing Phase 11 review packet heading failure")

    missing_phase10_build = good.replace("  * `zigux/tests/phase10_build.zig`\n", "", 1)
    try:
        check_text(missing_phase10_build)
    except SystemExit as exc:
        assert "`zigux/tests/phase10_build.zig`" in str(exc)
    else:
        raise AssertionError("expected missing phase10 build marker failure")

    missing_core_reset_queue = good.replace(
        "  * `zigux/tests/phase10_virtio_core_reset_queue.zig`\n",
        "",
        1,
    )
    try:
        check_text(missing_core_reset_queue)
    except SystemExit as exc:
        assert "`zigux/tests/phase10_virtio_core_reset_queue.zig`" in str(exc)
    else:
        raise AssertionError("expected missing core reset queue marker failure")

    missing_ring_surface = good.replace("  * `zigux/tests/phase10_virtio_ring.zig`\n", "", 1)
    try:
        check_text(missing_ring_surface)
    except SystemExit as exc:
        assert "`zigux/tests/phase10_virtio_ring.zig`" in str(exc)
    else:
        raise AssertionError("expected missing ring surface marker failure")

    missing_ring_reset_reuse = good.replace(
        "  * `zigux/tests/phase10_virtio_ring_reset_reuse.zig`\n",
        "",
        1,
    )
    try:
        check_text(missing_ring_reset_reuse)
    except SystemExit as exc:
        assert "`zigux/tests/phase10_virtio_ring_reset_reuse.zig`" in str(exc)
    else:
        raise AssertionError("expected missing ring reset reuse marker failure")

    missing_input_probe_preflight = good.replace(
        "  * `zigux/tests/phase10_virtio_input_probe_preflight.zig`\n",
        "",
        1,
    )
    try:
        check_text(missing_input_probe_preflight)
    except SystemExit as exc:
        assert "`zigux/tests/phase10_virtio_input_probe_preflight.zig`" in str(exc)
    else:
        raise AssertionError("expected missing input probe preflight marker failure")

    missing_mmio_manifest = good.replace(
        "  * `zigux/tests/phase10_virtio_mmio_manifest.json`\n",
        "",
        1,
    )
    try:
        check_text(missing_mmio_manifest)
    except SystemExit as exc:
        assert "`zigux/tests/phase10_virtio_mmio_manifest.json`" in str(exc)
    else:
        raise AssertionError("expected missing MMIO manifest marker failure")

    duplicate_ring_surface = good.replace(
        "`zigux/tests/phase10_virtio_ring.zig`",
        "`zigux/tests/phase10_virtio_ring.zig`\n  * `zigux/tests/phase10_virtio_ring.zig`",
        1,
    )
    try:
        check_text(duplicate_ring_surface)
    except SystemExit as exc:
        assert "`zigux/tests/phase10_virtio_ring.zig`" in str(exc)
        assert "expected exactly 1 occurrences" in str(exc)
    else:
        raise AssertionError("expected duplicate ring marker failure")

    print("PHASE10_TESTS_README_CORE_SURFACES_CHECKER_SELF_TEST=pass")
    print("PHASE10_TESTS_README_CORE_SURFACES_CHECKER_SELF_TEST_CASE_COUNT=9")
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
