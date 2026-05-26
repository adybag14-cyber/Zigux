#!/usr/bin/env python3
"""Fail closed when zigux/tests/README.md drifts from the shared Phase 9 packet."""

from __future__ import annotations

import argparse
from pathlib import Path


TESTS_README_PATH = Path("zigux/tests/README.md")
SECTION_HEADING = "## Phase 9 shared runtime packet"
NEXT_HEADING = "## Phase 10 shared virtio closure packet"

REQUIRED_MARKERS = (
    "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/README.md`",
    "`scripts/zigux/README.md`",
    "`zigux/tests/README.md`",
    "`scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`",
    "`scripts/zigux/check-phase9-trace-events-runtime-packet.py`",
    "`scripts/zigux/check-phase9-freeze-map-study-boundaries.py`",
    "`samples/zigux/runtime_trace_events.zig`",
    "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
    "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
    "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
    "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
    "`zigux/kernel/runtime_loader.zig`",
    "`zigux/kernel/runtime_loader_contract.zig`",
    "`zigux/kernel/runtime_loader_command_env_boundary_guard.zig`",
    "`phase9-runtime-loader-shared-tests`",
    "`phase9-runtime-loader-command-env-boundary-guard-tests`",
    "`Documentation/zigux/phase9-runtime-bitmap-survey.md`",
    "`zigux/tests/runtime_bitmap_manifest.json`",
    "`phase9-runtime-bitmap-cold-stage-guard-tests`",
    "`phase9-runtime-bitmap-tests`",
    "`samples/zigux/runtime_kretprobe.zig`",
    "`samples/zigux/runtime_kretprobe_loader.zig`",
    "`samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`",
    "`samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`",
    "`zigux/tests/runtime_kretprobe_survey.zig`",
    "`zigux/tests/runtime_kretprobe_module.zig`",
    "`zigux/tests/runtime_first_loadable_parity_behavior.zig`",
    "`phase9-runtime-kretprobe-sample-tests`",
    "`phase9-runtime-kretprobe-loader-tests`",
    "`phase9-runtime-kretprobe-initialized-snapshot-guard-tests`",
    "`phase9-runtime-kretprobe-registration-reentry-gate-tests`",
    "`phase9-runtime-kretprobe-survey-tests`",
    "`phase9-runtime-kretprobe-module-tests`",
    "`phase9-runtime-kretprobe-tests`",
    "`phase9-first-loadable-runtime-module-parity-behavior-tests`",
    "`Documentation/zigux/phase9-runtime-loader-gap-survey.md`",
    "`zigux/tests/runtime_loader_gap_manifest.json`",
    "`zigux/tests/runtime_loader_gap_survey.zig`",
    "`samples/zigux/runtime_trace_events_loader.zig`",
    "historical wider-family vocabulary",
    "family-local pilot evidence rather than proof that the broader shared runtime-loader packet, blocked publication boundaries, or install-root surfaces are complete",
)

FORBIDDEN_MARKERS = (
    "Phase 9 still has no dedicated tests-root reminder packet",
    "treat the returned kretprobe pilot as absent",
)


def extract_phase9_section(text: str) -> str:
    start = text.find(SECTION_HEADING)
    if start == -1:
        raise SystemExit(
            "PHASE9_TESTS_README_SHARED_PACKET=fail\n"
            "PHASE9_TESTS_README_SHARED_PACKET_REASON=missing_phase9_tests_heading"
        )

    end = text.find(NEXT_HEADING, start)
    if end == -1:
        raise SystemExit(
            "PHASE9_TESTS_README_SHARED_PACKET=fail\n"
            "PHASE9_TESTS_README_SHARED_PACKET_REASON=missing_phase10_heading"
        )

    return text[start:end]


def require_markers(section: str) -> None:
    missing = [marker for marker in REQUIRED_MARKERS if marker not in section]
    if missing:
        raise SystemExit(
            "PHASE9_TESTS_README_SHARED_PACKET=fail\n"
            "PHASE9_TESTS_README_SHARED_PACKET_REASON=missing_markers\n"
            "PHASE9_TESTS_README_SHARED_PACKET_MISSING=" + " | ".join(missing)
        )


def forbid_markers(section: str) -> None:
    present = [marker for marker in FORBIDDEN_MARKERS if marker in section]
    if present:
        raise SystemExit(
            "PHASE9_TESTS_README_SHARED_PACKET=fail\n"
            "PHASE9_TESTS_README_SHARED_PACKET_REASON=forbidden_markers\n"
            "PHASE9_TESTS_README_SHARED_PACKET_FORBIDDEN=" + " | ".join(present)
        )


def check_text(text: str) -> None:
    section = extract_phase9_section(text)
    require_markers(section)
    forbid_markers(section)


def run_self_test() -> int:
    good = """# zigux/tests

## Phase 9 shared runtime packet

Keep `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, and `scripts/zigux/check-phase9-freeze-map-study-boundaries.py` explicit as the shared Phase 9 tests-root reminder packet.

Keep `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` explicit as the shipped trace-events runtime proof.

Keep the narrower shared loader shard explicit through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, `phase9-runtime-loader-shared-tests`, and `phase9-runtime-loader-command-env-boundary-guard-tests`.

Keep the bounded runtime bitmap reminder packet explicit through `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `zigux/tests/runtime_bitmap_manifest.json`, `phase9-runtime-bitmap-cold-stage-guard-tests`, and `phase9-runtime-bitmap-tests`.

Keep the returned family-local runtime kretprobe packet explicit through `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`, `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_first_loadable_parity_behavior.zig`, `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-loader-tests`, `phase9-runtime-kretprobe-initialized-snapshot-guard-tests`, `phase9-runtime-kretprobe-registration-reentry-gate-tests`, `phase9-runtime-kretprobe-survey-tests`, `phase9-runtime-kretprobe-module-tests`, `phase9-runtime-kretprobe-tests`, and `phase9-first-loadable-runtime-module-parity-behavior-tests`, and keep that packet framed as family-local pilot evidence rather than proof that the broader shared runtime-loader packet, blocked publication boundaries, or install-root surfaces are complete.

Keep `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_manifest.json`, `zigux/tests/runtime_loader_gap_survey.zig`, and `samples/zigux/runtime_trace_events_loader.zig` framed as historical wider-family vocabulary until trusted rereads return them.

## Phase 10 shared virtio closure packet
"""

    check_text(good)

    missing_heading = good.replace("## Phase 9 shared runtime packet\n\n", "", 1)
    try:
        check_text(missing_heading)
    except SystemExit as exc:
        assert "missing_phase9_tests_heading" in str(exc)
    else:
        raise AssertionError("expected missing Phase 9 heading failure")

    missing_marker = good.replace("`phase9-runtime-kretprobe-loader-tests`, ", "", 1)
    try:
        check_text(missing_marker)
    except SystemExit as exc:
        assert "missing_markers" in str(exc)
        assert "phase9-runtime-kretprobe-loader-tests" in str(exc)
    else:
        raise AssertionError("expected missing marker failure")

    forbidden = good.replace(
        "historical wider-family vocabulary until trusted rereads return them.",
        "historical wider-family vocabulary until trusted rereads return them.\n\n"
        "Phase 9 still has no dedicated tests-root reminder packet.",
        1,
    )
    try:
        check_text(forbidden)
    except SystemExit as exc:
        assert "forbidden_markers" in str(exc)
    else:
        raise AssertionError("expected forbidden marker failure")

    print("PHASE9_TESTS_README_SHARED_PACKET_SELF_TEST=pass")
    print("PHASE9_TESTS_README_SHARED_PACKET_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tests-readme",
        default=str(TESTS_README_PATH),
        help="Path to the zigux/tests README to validate.",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    text = Path(args.tests_readme).read_text(encoding="utf-8")
    check_text(text)
    print("PHASE9_TESTS_README_SHARED_PACKET=pass")
    print(f"PHASE9_TESTS_README_SHARED_PACKET_PATH={args.tests_readme}")
    print(f"PHASE9_TESTS_README_SHARED_PACKET_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
