#!/usr/bin/env python3
"""Validate the remaining-gap rows in the Phase 4 validation matrix."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
MATRIX_REL = Path("Documentation/zigux/phase4-validation-matrix.md")
PERF_SECTION_HEADER = "### `Phase 4 perf thresholds`"
PERF_SECTION_FOOTER = "## Review Rules"

REQUIRED_MARKERS = [
    "## Remaining Roadmap Gaps",
    "### `samples/zigux/kprobe_example.zig`",
    "* current C anchor: `samples/kprobes/kprobe_example.c`",
    "* current replay path: `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`",
    "* explicit local lab replay marker: `make -C zigux phase4-kprobe-example-survey`",
    "* dedicated local survey wrapper: `make -C zigux phase4-kprobe-example-survey`",
    "* validation entrypoint: `zig test zigux/tests/phase4_kprobe_example_survey.zig`",
    "* validation entrypoint: `zig test zigux/tests/phase4_kprobe_example_survey.zig`\n* survey owner: `Validation and Perf Team`",
    "* rollback owner: `Validation and Perf Team`\n* current measurable status: absent on current `master`; the dedicated parked gap packet at `Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig` now keeps the current C anchor, replay command, explicit local lab replay marker, dedicated local survey wrapper, direct validation entrypoint, owner, and rollback owner reviewable, and the shared exact-readback packet at `Documentation/zigux/phase4-gate-evidence.md` plus `scripts/zigux/check-phase4-gate-evidence.py` now keep that same adjacent survey note, manifest, replay command, explicit local lab replay marker, direct validation entrypoint, and local survey wrapper machine-checkable without claiming a shipped Zig starter",
    "* next bounded evidence step: keep the dedicated parked survey packet, the explicit local lab replay marker, the dedicated local survey wrapper, and the current shared exact-readback coverage adjacent to the shared Phase 4 gate-evidence note until a later bounded lane intentionally opens either the Zig starter itself or a broader replay promotion beyond today's parked-gap packet",
    "### `samples/zigux/test_fsmount.zig`",
    "* current C anchor: `samples/vfs/test-fsmount.c`",
    "* current replay path: `make M=samples/vfs`",
    "* dedicated local survey wrapper: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
    "* dedicated Linux-style survey wrapper: `make -C zigux phase4-test-fsmount-survey`",
    "* validation entrypoint: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
    "* validation entrypoint: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`\n* survey owner: `Validation and Perf Team`",
    "* rollback owner: `Validation and Perf Team`\n* current measurable status: absent on current `master`; the dedicated parked gap packet at `Documentation/zigux/phase4-test-fsmount-gap-survey.md`, `zigux/tests/phase4_test_fsmount_manifest.json`, and `zigux/tests/phase4_test_fsmount_survey.zig`, together with the dedicated local survey wrapper `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` and the matching Linux-style survey wrapper `make -C zigux phase4-test-fsmount-survey`, now keeps the current C anchor, replay command, owner, rollback owner, and the explicit reviewability-only no-perf-threshold posture reviewable, and the packet now stays under the shared exact-readback checker while still remaining outside the shared `phase4-test` target set until a later bounded promotion lands",
    "* next bounded evidence step: keep the dedicated parked survey packet, the dedicated local `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` survey wrapper, the matching Linux-style `make -C zigux phase4-test-fsmount-survey` wrapper, and the explicit reviewability-only no-perf-threshold posture adjacent to the shared Phase 4 exact-readback packet while the current validator and gate-evidence checker continue to carry that same note, manifest, replay commands, and threshold posture without claiming a shipped Zig starter; if that same-family follow-through still stays below starter work, land one focused promotion that widens the local survey packet or shared replay surface rather than reopening measurability wording alone",
    PERF_SECTION_HEADER,
]

REQUIRED_PERF_SECTION_MARKERS = [
    "* current gate anchors: `zigux/tests/atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig`",
    "* current replay path: `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` and `make -C zigux phase4-perf-baseline-survey`",
    "* gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
    "* rollback owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
    "* current benchmark-command status: the dedicated survey packet at `zigux/tests/phase4_perf_baseline_manifest.json` and `zigux/tests/phase4_perf_baseline_survey.zig`, together with the matching Linux-style wrapper `make -C zigux phase4-perf-baseline-survey`, is now shipped, the local benchmark commands are approved for both landed gates, and the dedicated survey intentionally keeps that posture local rather than treating it as shared CI perf coverage",
    "* current acceptable-limit status: the dedicated survey packet now carries approved local-only acceptable limits for both atomic64 and bitmap, and shared CI perf coverage is still not claimed",
    "* next bounded evidence step: keep the current local-only acceptable limits survey-only until a later bounded lane intentionally decides whether the existing bounds should stay local-only or support a broader shared CI perf-coverage claim, with the Validation and Perf Team owning that policy decision in coordination with the ABI and Runtime Team and Shared Subsystems Pod as the current gate rollback owners so the validator-first packet does not widen by accident. This matrix, `scripts/zigux/validate-phase4.py`, the dedicated workflow-route-count checker, `zigux/Makefile`, and the shared `zigux/tests/phase4_build.zig` entrypoint should stay aligned around the still-correctness-only shared replay routes while the dedicated perf-baseline survey keeps the approved local benchmark commands and the approved local-only acceptable limits for both rollback gates explicit until a later Phase 4 lane intentionally decides whether any broader shared perf promotion belongs in the shipped packet.",
]

BASELINE_MATRIX = "\n".join(
    [
        "# Phase 4 Validation Matrix",
        "## Remaining Roadmap Gaps",
        "### `samples/zigux/kprobe_example.zig`",
        "* current C anchor: `samples/kprobes/kprobe_example.c`",
        "* current replay path: `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`",
        "* explicit local lab replay marker: `make -C zigux phase4-kprobe-example-survey`",
        "* dedicated local survey wrapper: `make -C zigux phase4-kprobe-example-survey`",
        "* validation entrypoint: `zig test zigux/tests/phase4_kprobe_example_survey.zig`",
        "* survey owner: `Validation and Perf Team`",
        "* rollback owner: `Validation and Perf Team`",
        "* current measurable status: absent on current `master`; the dedicated parked gap packet at `Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig` now keeps the current C anchor, replay command, explicit local lab replay marker, dedicated local survey wrapper, direct validation entrypoint, owner, and rollback owner reviewable, and the shared exact-readback packet at `Documentation/zigux/phase4-gate-evidence.md` plus `scripts/zigux/check-phase4-gate-evidence.py` now keep that same adjacent survey note, manifest, replay command, explicit local lab replay marker, direct validation entrypoint, and local survey wrapper machine-checkable without claiming a shipped Zig starter",
        "* next bounded evidence step: keep the dedicated parked survey packet, the explicit local lab replay marker, the dedicated local survey wrapper, and the current shared exact-readback coverage adjacent to the shared Phase 4 gate-evidence note until a later bounded lane intentionally opens either the Zig starter itself or a broader replay promotion beyond today's parked-gap packet",
        "",
        "### `samples/zigux/test_fsmount.zig`",
        "* current C anchor: `samples/vfs/test-fsmount.c`",
        "* current replay path: `make M=samples/vfs`",
        "* dedicated local survey wrapper: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
        "* dedicated Linux-style survey wrapper: `make -C zigux phase4-test-fsmount-survey`",
        "* validation entrypoint: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
        "* survey owner: `Validation and Perf Team`",
        "* rollback owner: `Validation and Perf Team`",
        "* current measurable status: absent on current `master`; the dedicated parked gap packet at `Documentation/zigux/phase4-test-fsmount-gap-survey.md`, `zigux/tests/phase4_test_fsmount_manifest.json`, and `zigux/tests/phase4_test_fsmount_survey.zig`, together with the dedicated local survey wrapper `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` and the matching Linux-style survey wrapper `make -C zigux phase4-test-fsmount-survey`, now keeps the current C anchor, replay command, owner, rollback owner, and the explicit reviewability-only no-perf-threshold posture reviewable, and the packet now stays under the shared exact-readback checker while still remaining outside the shared `phase4-test` target set until a later bounded promotion lands",
        "* next bounded evidence step: keep the dedicated parked survey packet, the dedicated local `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` survey wrapper, the matching Linux-style `make -C zigux phase4-test-fsmount-survey` wrapper, and the explicit reviewability-only no-perf-threshold posture adjacent to the shared Phase 4 exact-readback packet while the current validator and gate-evidence checker continue to carry that same note, manifest, replay commands, and threshold posture without claiming a shipped Zig starter; if that same-family follow-through still stays below starter work, land one focused promotion that widens the local survey packet or shared replay surface rather than reopening measurability wording alone",
        "",
        PERF_SECTION_HEADER,
        "* current gate anchors: `zigux/tests/atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig`",
        "* current replay path: `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` and `make -C zigux phase4-perf-baseline-survey`",
        "* gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
        "* rollback owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
        "* current benchmark-command status: the dedicated survey packet at `zigux/tests/phase4_perf_baseline_manifest.json` and `zigux/tests/phase4_perf_baseline_survey.zig`, together with the matching Linux-style wrapper `make -C zigux phase4-perf-baseline-survey`, is now shipped, the local benchmark commands are approved for both landed gates, and the dedicated survey intentionally keeps that posture local rather than treating it as shared CI perf coverage",
        "* current acceptable-limit status: the dedicated survey packet now carries approved local-only acceptable limits for both atomic64 and bitmap, and shared CI perf coverage is still not claimed",
        "* next bounded evidence step: keep the current local-only acceptable limits survey-only until a later bounded lane intentionally decides whether the existing bounds should stay local-only or support a broader shared CI perf-coverage claim, with the Validation and Perf Team owning that policy decision in coordination with the ABI and Runtime Team and Shared Subsystems Pod as the current gate rollback owners so the validator-first packet does not widen by accident. This matrix, `scripts/zigux/validate-phase4.py`, the dedicated workflow-route-count checker, `zigux/Makefile`, and the shared `zigux/tests/phase4_build.zig` entrypoint should stay aligned around the still-correctness-only shared replay routes while the dedicated perf-baseline survey keeps the approved local benchmark commands and the approved local-only acceptable limits for both rollback gates explicit until a later Phase 4 lane intentionally decides whether any broader shared perf promotion belongs in the shipped packet.",
        "",
        PERF_SECTION_FOOTER,
        "",
    ]
)

SELF_TEST_CASES = [
    "baseline_round_trip",
    "missing_matrix_file",
    "kprobe_c_anchor_drift",
    "kprobe_replay_path_drift",
    "kprobe_local_lab_replay_drift",
    "kprobe_wrapper_drift",
    "kprobe_validation_entrypoint_drift",
    "kprobe_owner_drift",
    "kprobe_rollback_owner_drift",
    "kprobe_status_local_lab_replay_drift",
    "kprobe_next_step_drift",
    "test_fsmount_c_anchor_drift",
    "test_fsmount_replay_path_drift",
    "test_fsmount_gap_packet_drift",
    "test_fsmount_threshold_posture_drift",
    "test_fsmount_local_wrapper_drift",
    "test_fsmount_linux_style_wrapper_drift",
    "test_fsmount_validation_entrypoint_drift",
    "test_fsmount_owner_drift",
    "test_fsmount_rollback_owner_drift",
    "test_fsmount_next_step_drift",
    "perf_gate_anchor_drift",
    "perf_replay_path_drift",
    "perf_benchmark_command_status_drift",
    "perf_limit_status_drift",
    "perf_gate_owner_drift",
    "perf_rollback_owner_drift",
    "perf_owner_coordination_drift",
    "perf_section_scope_drift",
    "perf_section_footer_drift",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing marker: {old}")
    return text.replace(old, new, 1)


def normalize_matrix_text(text: str) -> str:
    return text.replace("\n  *", "\n*")


def require_section(text: str, header: str, footer: str) -> str:
    start = text.find(header)
    if start == -1:
        raise ValueError(f"missing section header: {header}")
    end = text.find(footer, start)
    if end == -1:
        raise ValueError(f"missing section footer: {footer}")
    return text[start:end]


def validate_root(root: Path) -> list[str]:
    matrix_path = root / MATRIX_REL
    if not matrix_path.exists():
        return [f"file:{MATRIX_REL.as_posix()}"]

    text = normalize_matrix_text(read_text(matrix_path))
    failures: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            failures.append(f"missing_marker:{marker}")

    try:
        perf_section = require_section(text, PERF_SECTION_HEADER, PERF_SECTION_FOOTER)
    except ValueError as exc:
        failures.append(f"missing_perf_section:{exc}")
        return failures

    for marker in REQUIRED_PERF_SECTION_MARKERS:
        if marker not in perf_section:
            failures.append(f"missing_perf_section_marker:{marker}")
    return failures


def expect_failure(root: Path, expected_prefix: str) -> bool:
    return any(item.startswith(expected_prefix) for item in validate_root(root))


def run_self_test() -> int:
    cases = [
        (
            "kprobe_c_anchor_drift",
            replace_once(
                BASELINE_MATRIX,
                "samples/kprobes/kprobe_example.c",
                "samples/kprobes/kprobe_example_drift.c",
            ),
            "missing_marker:* current C anchor: `samples/kprobes/kprobe_example.c`",
        ),
        (
            "kprobe_replay_path_drift",
            replace_once(
                BASELINE_MATRIX,
                "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
                "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=n",
            ),
            "missing_marker:* current replay path: `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`",
        ),
        (
            "kprobe_local_lab_replay_drift",
            replace_once(
                BASELINE_MATRIX,
                "* explicit local lab replay marker: `make -C zigux phase4-kprobe-example-survey`",
                "* explicit local lab replay marker: `make -C zigux phase4-kprobe-gap-survey`",
            ),
            "missing_marker:* explicit local lab replay marker: `make -C zigux phase4-kprobe-example-survey`",
        ),
        (
            "kprobe_wrapper_drift",
            replace_once(
                BASELINE_MATRIX,
                "* dedicated local survey wrapper: `make -C zigux phase4-kprobe-example-survey`",
                "* dedicated local survey wrapper: `make -C zigux phase4-kprobe-gap-survey`",
            ),
            "missing_marker:* dedicated local survey wrapper: `make -C zigux phase4-kprobe-example-survey`",
        ),
        (
            "kprobe_validation_entrypoint_drift",
            replace_once(
                BASELINE_MATRIX,
                "* validation entrypoint: `zig test zigux/tests/phase4_kprobe_example_survey.zig`",
                "* validation entrypoint: `zig build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig`",
            ),
            "missing_marker:* validation entrypoint: `zig test zigux/tests/phase4_kprobe_example_survey.zig`",
        ),
        (
            "kprobe_owner_drift",
            replace_once(
                BASELINE_MATRIX,
                "* survey owner: `Validation and Perf Team`",
                "* survey owner: `Tooling and Validation Team`",
            ),
            "missing_marker:* validation entrypoint: `zig test zigux/tests/phase4_kprobe_example_survey.zig`\n* survey owner: `Validation and Perf Team`",
        ),
        (
            "kprobe_rollback_owner_drift",
            replace_once(
                BASELINE_MATRIX,
                "* rollback owner: `Validation and Perf Team`\n* current measurable status:",
                "* rollback owner: `Tooling and Validation Team`\n* current measurable status:",
            ),
            "missing_marker:* rollback owner: `Validation and Perf Team`\n* current measurable status: absent on current `master`; the dedicated parked gap packet at `Documentation/zigux/phase4-kprobe-example-gap-survey.md`",
        ),
        (
            "kprobe_status_local_lab_replay_drift",
            replace_once(
                BASELINE_MATRIX,
                "explicit local lab replay marker, dedicated local survey wrapper",
                "dedicated local survey wrapper, dedicated local survey wrapper",
            ),
            "missing_marker:* rollback owner: `Validation and Perf Team`\n* current measurable status: absent on current `master`; the dedicated parked gap packet at `Documentation/zigux/phase4-kprobe-example-gap-survey.md`",
        ),
        (
            "kprobe_next_step_drift",
            replace_once(
                BASELINE_MATRIX,
                "* next bounded evidence step: keep the dedicated parked survey packet, the explicit local lab replay marker, the dedicated local survey wrapper, and the current shared exact-readback coverage adjacent to the shared Phase 4 gate-evidence note until a later bounded lane intentionally opens either the Zig starter itself or a broader replay promotion beyond today's parked-gap packet",
                "* next bounded evidence step: keep the dedicated parked survey packet, the dedicated local survey wrapper, and the current shared exact-readback coverage adjacent to the shared Phase 4 gate-evidence note until a later bounded lane intentionally opens either the Zig starter itself or a broader replay promotion beyond today's parked-gap packet",
            ),
            "missing_marker:* next bounded evidence step: keep the dedicated parked survey packet, the explicit local lab replay marker, the dedicated local survey wrapper, and the current shared exact-readback coverage adjacent to the shared Phase 4 gate-evidence note until a later bounded lane intentionally opens either the Zig starter itself or a broader replay promotion beyond today's parked-gap packet",
        ),
        (
            "test_fsmount_c_anchor_drift",
            replace_once(BASELINE_MATRIX, "samples/vfs/test-fsmount.c", "samples/vfs/test-fsmount-drift.c"),
            "missing_marker:* current C anchor: `samples/vfs/test-fsmount.c`",
        ),
        (
            "test_fsmount_replay_path_drift",
            replace_once(BASELINE_MATRIX, "make M=samples/vfs", "make M=samples/vfs-drift"),
            "missing_marker:* current replay path: `make M=samples/vfs`",
        ),
        (
            "test_fsmount_gap_packet_drift",
            replace_once(
                BASELINE_MATRIX,
                "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
                "Documentation/zigux/phase4-test-fsmount-gap-note.md",
            ),
            "missing_marker:* rollback owner: `Validation and Perf Team`\n* current measurable status: absent on current `master`; the dedicated parked gap packet at `Documentation/zigux/phase4-test-fsmount-gap-survey.md`",
        ),
        (
            "test_fsmount_threshold_posture_drift",
            replace_once(
                BASELINE_MATRIX,
                "explicit reviewability-only no-perf-threshold posture reviewable",
                "explicit shared-CI perf-threshold posture reviewable",
            ),
            "missing_marker:* rollback owner: `Validation and Perf Team`\n* current measurable status: absent on current `master`; the dedicated parked gap packet at `Documentation/zigux/phase4-test-fsmount-gap-survey.md`",
        ),
        (
            "test_fsmount_local_wrapper_drift",
            replace_once(
                BASELINE_MATRIX,
                "* dedicated local survey wrapper: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
                "* dedicated local survey wrapper: `zig build phase4-test-fsmount-gap-survey --build-file zigux/tests/phase4_build.zig`",
            ),
            "missing_marker:* dedicated local survey wrapper: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
        ),
        (
            "test_fsmount_linux_style_wrapper_drift",
            replace_once(
                BASELINE_MATRIX,
                "* dedicated Linux-style survey wrapper: `make -C zigux phase4-test-fsmount-survey`",
                "* dedicated Linux-style survey wrapper: `make -C zigux phase4-test-fsmount-gap-survey`",
            ),
            "missing_marker:* dedicated Linux-style survey wrapper: `make -C zigux phase4-test-fsmount-survey`",
        ),
        (
            "test_fsmount_validation_entrypoint_drift",
            replace_once(
                BASELINE_MATRIX,
                "* validation entrypoint: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
                "* validation entrypoint: `zig build phase4-test-fsmount-gap-survey --build-file zigux/tests/phase4_build.zig`",
            ),
            "missing_marker:* validation entrypoint: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
        ),
        (
            "test_fsmount_owner_drift",
            replace_once(
                BASELINE_MATRIX,
                "* validation entrypoint: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`\n* survey owner: `Validation and Perf Team`",
                "* validation entrypoint: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`\n* survey owner: `Tooling and Validation Team`",
            ),
            "missing_marker:* validation entrypoint: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`\n* survey owner: `Validation and Perf Team`",
        ),
        (
            "test_fsmount_rollback_owner_drift",
            replace_once(
                BASELINE_MATRIX,
                "* rollback owner: `Validation and Perf Team`\n* current measurable status: absent on current `master`; the dedicated parked gap packet at `Documentation/zigux/phase4-test-fsmount-gap-survey.md`",
                "* rollback owner: `Tooling and Validation Team`\n* current measurable status: absent on current `master`; the dedicated parked gap packet at `Documentation/zigux/phase4-test-fsmount-gap-survey.md`",
            ),
            "missing_marker:* rollback owner: `Validation and Perf Team`\n* current measurable status: absent on current `master`; the dedicated parked gap packet at `Documentation/zigux/phase4-test-fsmount-gap-survey.md`",
        ),
        (
            "test_fsmount_next_step_drift",
            replace_once(
                BASELINE_MATRIX,
                "land one focused promotion that widens the local survey packet or shared replay surface rather than reopening measurability wording alone",
                "land one focused promotion that widens the shared replay surface rather than reopening measurability wording alone",
            ),
            "missing_marker:* next bounded evidence step: keep the dedicated parked survey packet, the dedicated local `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` survey wrapper, the matching Linux-style `make -C zigux phase4-test-fsmount-survey` wrapper, and the explicit reviewability-only no-perf-threshold posture adjacent to the shared Phase 4 exact-readback packet while the current validator and gate-evidence checker continue to carry that same note, manifest, replay commands, and threshold posture without claiming a shipped Zig starter; if that same-family follow-through still stays below starter work, land one focused promotion that widens the local survey packet or shared replay surface rather than reopening measurability wording alone",
        ),
        (
            "perf_gate_anchor_drift",
            replace_once(
                BASELINE_MATRIX,
                "* current gate anchors: `zigux/tests/atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig`",
                "* current gate anchors: `zigux/tests/runtime_atomic64_diff.zig` and `zigux/tests/phase4_bitmap_diff_survey.zig`",
            ),
            "missing_perf_section_marker:* current gate anchors: `zigux/tests/atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig`",
        ),
        (
            "perf_replay_path_drift",
            replace_once(
                BASELINE_MATRIX,
                "* current replay path: `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` and `make -C zigux phase4-perf-baseline-survey`",
                "* current replay path: `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` only",
            ),
            "missing_perf_section_marker:* current replay path: `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` and `make -C zigux phase4-perf-baseline-survey`",
        ),
        (
            "perf_benchmark_command_status_drift",
            replace_once(
                BASELINE_MATRIX,
                "the local benchmark commands are approved for both landed gates",
                "the local benchmark commands remain provisional for both landed gates",
            ),
            "missing_perf_section_marker:* current benchmark-command status: the dedicated survey packet at `zigux/tests/phase4_perf_baseline_manifest.json` and `zigux/tests/phase4_perf_baseline_survey.zig`, together with the matching Linux-style wrapper `make -C zigux phase4-perf-baseline-survey`, is now shipped, the local benchmark commands are approved for both landed gates, and the dedicated survey intentionally keeps that posture local rather than treating it as shared CI perf coverage",
        ),
        (
            "perf_limit_status_drift",
            replace_once(
                BASELINE_MATRIX,
                "approved local-only acceptable limits for both atomic64 and bitmap",
                "tentative local-only acceptable limits",
            ),
            "missing_perf_section_marker:* current acceptable-limit status: the dedicated survey packet now carries approved local-only acceptable limits for both atomic64 and bitmap",
        ),
        (
            "perf_gate_owner_drift",
            replace_once(
                BASELINE_MATRIX,
                "* gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
                "* gate owners: `Validation and Perf Team` only",
            ),
            "missing_perf_section_marker:* gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
        ),
        (
            "perf_rollback_owner_drift",
            replace_once(
                BASELINE_MATRIX,
                "* rollback owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
                "* rollback owners: `Validation and Perf Team` only",
            ),
            "missing_perf_section_marker:* rollback owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
        ),
        (
            "perf_owner_coordination_drift",
            replace_once(
                BASELINE_MATRIX,
                "Validation and Perf Team owning that policy decision in coordination with the ABI and Runtime Team and Shared Subsystems Pod",
                "Tooling and Validation Team owning that policy decision on its own",
            ),
            "missing_perf_section_marker:* next bounded evidence step: keep the current local-only acceptable limits survey-only until a later bounded lane intentionally decides whether the existing bounds should stay local-only or support a broader shared CI perf-coverage claim, with the Validation and Perf Team owning that policy decision in coordination with the ABI and Runtime Team and Shared Subsystems Pod as the current gate rollback owners so the validator-first packet does not widen by accident.",
        ),
        (
            "perf_section_scope_drift",
            replace_once(
                BASELINE_MATRIX,
                "* current replay path: `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` and `make -C zigux phase4-perf-baseline-survey`",
                "* current replay path: `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` only",
            )
            + "\nShared replay note duplicate:\n"
            + "* current replay path: `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` and `make -C zigux phase4-perf-baseline-survey`\n",
            "missing_perf_section_marker:* current replay path: `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` and `make -C zigux phase4-perf-baseline-survey`",
        ),
        (
            "perf_section_footer_drift",
            replace_once(BASELINE_MATRIX, PERF_SECTION_FOOTER, "## Review Drift"),
            f"missing_perf_section:missing section footer: {PERF_SECTION_FOOTER}",
        ),
    ]

    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_gap_matrix_") as tmp_dir:
        root = Path(tmp_dir)
        matrix_path = root / MATRIX_REL

        write_text(matrix_path, BASELINE_MATRIX)
        if validate_root(root):
            print("PHASE4_REMAINING_GAP_MATRIX_SELF_TEST=fail")
            print("baseline fixture did not validate")
            return 1
        case_count += 1

        matrix_path.unlink()
        if not expect_failure(root, f"file:{MATRIX_REL.as_posix()}"):
            print("PHASE4_REMAINING_GAP_MATRIX_SELF_TEST=fail")
            print("missing matrix file case did not fail closed")
            return 1
        case_count += 1

        for name, drifted_text, failure_prefix in cases:
            write_text(matrix_path, drifted_text)
            if not expect_failure(root, failure_prefix):
                print("PHASE4_REMAINING_GAP_MATRIX_SELF_TEST=fail")
                print(f"{name} case did not fail closed")
                return 1
            case_count += 1

    if case_count != len(SELF_TEST_CASES):
        print("PHASE4_REMAINING_GAP_MATRIX_SELF_TEST=fail")
        print(f"unexpected self-test case count {case_count} != {len(SELF_TEST_CASES)}")
        return 1

    print("PHASE4_REMAINING_GAP_MATRIX_SELF_TEST=pass")
    print(f"PHASE4_REMAINING_GAP_MATRIX_SELF_TEST_CASE_COUNT={case_count}")
    print("PHASE4_REMAINING_GAP_MATRIX_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 4 remaining-gap measurability rows."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run isolated coverage checks in a temporary workspace.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate_root(ROOT)
    if failures:
        print("PHASE4_REMAINING_GAP_MATRIX_CHECK=fail")
        print("PHASE4_REMAINING_GAP_MATRIX_FAILURES_START")
        for item in failures:
            print(item)
        print("PHASE4_REMAINING_GAP_MATRIX_FAILURES_END")
        return 1

    print("PHASE4_REMAINING_GAP_MATRIX_CHECK=pass")
    print(
        f"PHASE4_REMAINING_GAP_MATRIX_MARKER_COUNT="
        f"{len(REQUIRED_MARKERS) + len(REQUIRED_PERF_SECTION_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
