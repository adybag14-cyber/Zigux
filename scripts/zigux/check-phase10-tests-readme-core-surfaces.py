#!/usr/bin/env python3
"""Check that the Phase 10 tests-root packet matches current direct-readback reality."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


TESTS_README_PATH = Path("zigux/tests/README.md")
PHASE10_START = "Phase 10 flow"
PHASE10_END = "Phase 11 review packet"

REQUIRED_DIRECT_MARKERS = (
    "`Documentation/zigux/phase10-closure-evidence.md`",
    "`Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase10-virtio-ring-survey.md`",
    "`Documentation/zigux/phase10-virtio-ring-slice.md`",
    "`zigux/tests/phase10_virtio_ring_manifest.json`",
    "`zigux/tests/phase10_build.zig`",
    "`Documentation/zigux/phase10-virtio-input-survey.md`",
    "`drivers/virtio/virtio_input.zig`",
    "`zigux/tests/phase10_virtio_input_status_drain.zig`",
    "`Documentation/zigux/phase10-virtio-mmio-survey.md`",
    "`drivers/virtio/virtio_mmio.zig`",
    "`drivers/virtio/virtio_mmio_verify.zig`",
)

REQUIRED_REPO_REALITY_GAP_MARKERS = (
    "current `master` still does not materialize",
    "`Documentation/zigux/phase10-virtio-core-survey.md`",
    "`Documentation/zigux/phase10-virtio-core-slice.md`",
    "`zigux/tests/phase10_virtio_core.zig`",
    "`zigux/tests/phase10_virtio_ring.zig`",
    "`zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
    "`drivers/virtio/virtio_ring.zig`",
    "`drivers/virtio/virtio_ring_verify.zig`",
    "closure-manifest-backed ring packet vocabulary",
    "repo-reality gaps instead of direct current-head evidence",
)

EXPECTED_MARKER_COUNTS = {
    "`zigux/tests/phase10_build.zig`": 2,
    "`zigux/tests/phase10_virtio_ring_manifest.json`": 3,
    "`Documentation/zigux/phase10-virtio-ring-slice.md`": 3,
    "`Documentation/zigux/phase10-virtio-ring-survey.md`": 3,
    "`drivers/virtio/virtio_mmio.zig`": 3,
}


def phase10_section(text: str) -> str:
    start = text.find(PHASE10_START)
    if start == -1:
        raise SystemExit(
            "phase10 tests-readme checker missing `Phase 10 flow` section heading"
        )

    end = text.find(PHASE10_END, start)
    if end == -1:
        raise SystemExit(
            "phase10 tests-readme checker missing `Phase 11 review packet` section heading"
        )

    return text[start:end]


def check_markers(section: str, markers: tuple[str, ...], label: str) -> None:
    missing = [marker for marker in markers if marker not in section]
    if missing:
        raise SystemExit(
            f"phase10 tests-readme checker missing {label} markers: "
            + ", ".join(missing)
        )


def check_counts(section: str) -> None:
    for marker, expected_count in EXPECTED_MARKER_COUNTS.items():
        actual_count = section.count(marker)
        if actual_count != expected_count:
            raise SystemExit(
                "phase10 tests-readme checker expected exactly "
                f"{expected_count} occurrences of {marker}, found {actual_count}"
            )


def check_text(text: str) -> None:
    section = phase10_section(text)
    check_markers(section, REQUIRED_DIRECT_MARKERS, "direct-readback")
    check_markers(section, REQUIRED_REPO_REALITY_GAP_MARKERS, "repo-reality-gap")
    check_counts(section)


def run_self_test() -> int:
    good = """# zigux/tests

Phase 10 flow

  * `Documentation/zigux/phase10-closure-evidence.md`
  * `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
  * directly re-readable ring packet anchors: `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and `zigux/tests/phase10_build.zig`
  * directly re-readable input packet anchors: `Documentation/zigux/phase10-virtio-input-survey.md`, `drivers/virtio/virtio_input.zig`, and `zigux/tests/phase10_virtio_input_status_drain.zig`
  * helper-local MMIO packet anchors: `Documentation/zigux/phase10-virtio-mmio-survey.md`, `drivers/virtio/virtio_mmio.zig`, and `drivers/virtio/virtio_mmio_verify.zig`
  * current `master` still does not materialize `Documentation/zigux/phase10-virtio-core-survey.md`, `Documentation/zigux/phase10-virtio-core-slice.md`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `drivers/virtio/virtio_ring.zig`, and `drivers/virtio/virtio_ring_verify.zig` through the direct readback available in this lane, so keep them framed as closure-manifest-backed ring packet vocabulary and repo-reality gaps instead of direct current-head evidence
  * treat `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, `drivers/virtio/virtio_mmio.zig`, and `zigux/tests/phase10_build.zig` as the current directly re-readable Phase 10 anchors in this reminder surface
  * keep `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`, and `Documentation/zigux/phase10-virtio-ring-survey.md` explicit as closure-manifest-backed ring packet vocabulary when broader shared summaries refresh, with `Documentation/zigux/phase10-virtio-ring-slice.md` still named separately as the directly re-readable packet-local companion
  * keep the MMIO helper names `drivers/virtio/virtio_mmio.zig` and `drivers/virtio/virtio_mmio_verify.zig` explicit beside `Documentation/zigux/phase10-virtio-mmio-survey.md`

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
        raise AssertionError("expected missing Phase 11 heading failure")

    missing_direct_ring_anchor = good.replace(
        "`Documentation/zigux/phase10-virtio-ring-slice.md`, ", "", 1
    )
    try:
        check_text(missing_direct_ring_anchor)
    except SystemExit as exc:
        assert "`Documentation/zigux/phase10-virtio-ring-slice.md`" in str(exc)
    else:
        raise AssertionError("expected missing direct ring anchor failure")

    missing_repo_gap_marker = good.replace(
        "`Documentation/zigux/phase10-virtio-core-survey.md`",
        "`Documentation/zigux/phase10-virtio-core-survey-missing.md`",
        1,
    )
    try:
        check_text(missing_repo_gap_marker)
    except SystemExit as exc:
        assert "`Documentation/zigux/phase10-virtio-core-survey.md`" in str(exc)
    else:
        raise AssertionError("expected missing repo-reality gap marker failure")

    missing_gap_phrase = good.replace(
        "repo-reality gaps instead of direct current-head evidence",
        "repo-reality gap wording",
        1,
    )
    try:
        check_text(missing_gap_phrase)
    except SystemExit as exc:
        assert "repo-reality gaps instead of direct current-head evidence" in str(exc)
    else:
        raise AssertionError("expected missing gap phrase failure")

    duplicate_build_marker = good.replace(
        "`zigux/tests/phase10_build.zig`",
        "`zigux/tests/phase10_build.zig` and `zigux/tests/phase10_build.zig`",
        1,
    )
    try:
        check_text(duplicate_build_marker)
    except SystemExit as exc:
        assert "`zigux/tests/phase10_build.zig`" in str(exc)
        assert "expected exactly 2 occurrences" in str(exc)
    else:
        raise AssertionError("expected duplicate build marker failure")

    missing_mmio_anchor = good.replace(
        "`zigux/tests/phase10_virtio_input_status_drain.zig`",
        "`zigux/tests/phase10_virtio_input_status_drain_missing.zig`",
        1,
    )
    try:
        check_text(missing_mmio_anchor)
    except SystemExit as exc:
        assert "`zigux/tests/phase10_virtio_input_status_drain.zig`" in str(exc)
    else:
        raise AssertionError("expected missing direct anchor failure")

    print("PHASE10_TESTS_README_CORE_SURFACES_CHECKER_SELF_TEST=pass")
    print("PHASE10_TESTS_README_CORE_SURFACES_CHECKER_SELF_TEST_CASE_COUNT=7")
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
