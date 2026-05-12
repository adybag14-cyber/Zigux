#!/usr/bin/env python3
"""Validate the remaining-gap rows in the Phase 4 validation matrix."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
MATRIX_REL = Path("Documentation/zigux/phase4-validation-matrix.md")

REQUIRED_MARKERS = [
    "## Remaining Roadmap Gaps",
    "### `samples/zigux/kprobe_example.zig`",
    "* dedicated local survey wrapper: `make -C zigux phase4-kprobe-example-survey`",
    "* validation entrypoint: `zig test zigux/tests/phase4_kprobe_example_survey.zig`",
    "* current measurable status: absent on current `master`; the dedicated parked gap packet at `Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig` now keeps the current C anchor, replay command, dedicated local survey wrapper, direct validation entrypoint, owner, and rollback owner reviewable, and the shared exact-readback packet at `Documentation/zigux/phase4-gate-evidence.md` plus `scripts/zigux/check-phase4-gate-evidence.py` now keep that same adjacent survey note, manifest, replay command, direct validation entrypoint, and local survey wrapper machine-checkable without claiming a shipped Zig starter",
    "### `samples/zigux/test_fsmount.zig`",
    "* dedicated local survey wrapper: `make -C zigux phase4-test-fsmount-survey`",
    "* validation entrypoint: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
    "* current measurable status: absent on current `master`; the dedicated parked gap packet at `Documentation/zigux/phase4-test-fsmount-gap-survey.md`, `zigux/tests/phase4_test_fsmount_manifest.json`, and `zigux/tests/phase4_test_fsmount_survey.zig`, together with the dedicated local survey wrapper `make -C zigux phase4-test-fsmount-survey` and the direct validation entrypoint at `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`, now keep the current C anchor, replay command, owner, rollback owner, and the explicit reviewability-only no-perf-threshold posture reviewable, and the packet now stays under the shared exact-readback checker while still remaining outside the shared `phase4-test` target set until a later bounded promotion lands",
    "### `Phase 4 perf thresholds`",
    "* current benchmark-command status: the dedicated survey packet at `zigux/tests/phase4_perf_baseline_manifest.json` and `zigux/tests/phase4_perf_baseline_survey.zig`, together with the matching Linux-style wrapper `make -C zigux phase4-perf-baseline-survey`, is now shipped, the local benchmark commands are approved for both landed gates, and the dedicated survey intentionally keeps that posture local rather than treating it as shared CI perf coverage",
    "* current acceptable-limit status: the dedicated survey packet now carries approved local-only acceptable limits for both atomic64 and bitmap, and shared CI perf coverage is still not claimed",
    "* next bounded evidence step: keep the current local-only acceptable limits survey-only until a later bounded lane intentionally decides whether the existing bounds should stay local-only or support a broader shared CI perf-coverage claim, with the Validation and Perf Team owning that policy decision in coordination with the ABI and Runtime Team and Shared Subsystems Pod as the current gate rollback owners so the validator-first packet does not widen by accident. This matrix, `scripts/zigux/validate-phase4.py`, the dedicated workflow-route-count checker, `zigux/Makefile`, and the shared `zigux/tests/phase4_build.zig` entrypoint should stay aligned around the still-correctness-only shared replay routes while the dedicated perf-baseline survey keeps the approved local benchmark commands and the approved local-only acceptable limits for both rollback gates explicit until a later Phase 4 lane intentionally decides whether any broader shared perf promotion belongs in the shipped packet.",
]

SELF_TEST_CASES = [
    "baseline_round_trip",
    "missing_matrix_file",
    "kprobe_wrapper_drift",
    "test_fsmount_gap_packet_drift",
    "perf_limit_status_drift",
    "perf_owner_coordination_drift",
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


def validate_root(root: Path) -> list[str]:
    matrix_path = root / MATRIX_REL
    if not matrix_path.exists():
        return [f"file:{MATRIX_REL.as_posix()}"]

    text = read_text(matrix_path)
    failures: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            failures.append(f"missing_marker:{marker}")
    return failures


def build_fixture_text() -> str:
    return "\n".join(
        [
            "# Phase 4 Validation Matrix",
            "## Remaining Roadmap Gaps",
            "### `samples/zigux/kprobe_example.zig`",
            "* dedicated local survey wrapper: `make -C zigux phase4-kprobe-example-survey`",
            "* validation entrypoint: `zig test zigux/tests/phase4_kprobe_example_survey.zig`",
            "* current measurable status: absent on current `master`; the dedicated parked gap packet at `Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig` now keeps the current C anchor, replay command, dedicated local survey wrapper, direct validation entrypoint, owner, and rollback owner reviewable, and the shared exact-readback packet at `Documentation/zigux/phase4-gate-evidence.md` plus `scripts/zigux/check-phase4-gate-evidence.py` now keep that same adjacent survey note, manifest, replay command, direct validation entrypoint, and local survey wrapper machine-checkable without claiming a shipped Zig starter",
            "### `samples/zigux/test_fsmount.zig`",
            "* dedicated local survey wrapper: `make -C zigux phase4-test-fsmount-survey`",
            "* validation entrypoint: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
            "* current measurable status: absent on current `master`; the dedicated parked gap packet at `Documentation/zigux/phase4-test-fsmount-gap-survey.md`, `zigux/tests/phase4_test_fsmount_manifest.json`, and `zigux/tests/phase4_test_fsmount_survey.zig`, together with the dedicated local survey wrapper `make -C zigux phase4-test-fsmount-survey` and the direct validation entrypoint at `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`, now keep the current C anchor, replay command, owner, rollback owner, and the explicit reviewability-only no-perf-threshold posture reviewable, and the packet now stays under the shared exact-readback checker while still remaining outside the shared `phase4-test` target set until a later bounded promotion lands",
            "### `Phase 4 perf thresholds`",
            "* current benchmark-command status: the dedicated survey packet at `zigux/tests/phase4_perf_baseline_manifest.json` and `zigux/tests/phase4_perf_baseline_survey.zig`, together with the matching Linux-style wrapper `make -C zigux phase4-perf-baseline-survey`, is now shipped, the local benchmark commands are approved for both landed gates, and the dedicated survey intentionally keeps that posture local rather than treating it as shared CI perf coverage",
            "* current acceptable-limit status: the dedicated survey packet now carries approved local-only acceptable limits for both atomic64 and bitmap, and shared CI perf coverage is still not claimed",
            "* next bounded evidence step: keep the current local-only acceptable limits survey-only until a later bounded lane intentionally decides whether the existing bounds should stay local-only or support a broader shared CI perf-coverage claim, with the Validation and Perf Team owning that policy decision in coordination with the ABI and Runtime Team and Shared Subsystems Pod as the current gate rollback owners so the validator-first packet does not widen by accident. This matrix, `scripts/zigux/validate-phase4.py`, the dedicated workflow-route-count checker, `zigux/Makefile`, and the shared `zigux/tests/phase4_build.zig` entrypoint should stay aligned around the still-correctness-only shared replay routes while the dedicated perf-baseline survey keeps the approved local benchmark commands and the approved local-only acceptable limits for both rollback gates explicit until a later Phase 4 lane intentionally decides whether any broader shared perf promotion belongs in the shipped packet.",
            "",
        ]
    )


def expect_failure(root: Path, expected_prefix: str) -> bool:
    failures = validate_root(root)
    return any(item.startswith(expected_prefix) for item in failures)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_gap_matrix_") as tmp_dir:
        root = Path(tmp_dir)
        matrix_path = root / MATRIX_REL
        baseline = build_fixture_text()
        write_text(matrix_path, baseline)

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

        write_text(
            matrix_path,
            replace_once(
                baseline,
                "make -C zigux phase4-kprobe-example-survey",
                "make -C zigux phase4-kprobe-gap-survey",
            ),
        )
        if not expect_failure(
            root,
            "missing_marker:* dedicated local survey wrapper: `make -C zigux phase4-kprobe-example-survey`",
        ):
            print("PHASE4_REMAINING_GAP_MATRIX_SELF_TEST=fail")
            print("kprobe wrapper drift case did not fail closed")
            return 1
        case_count += 1

        write_text(
            matrix_path,
            replace_once(
                baseline,
                "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
                "Documentation/zigux/phase4-test-fsmount-gap-note.md",
            ),
        )
        if not expect_failure(
            root,
            "missing_marker:* current measurable status: absent on current `master`; the dedicated parked gap packet at `Documentation/zigux/phase4-test-fsmount-gap-survey.md`",
        ):
            print("PHASE4_REMAINING_GAP_MATRIX_SELF_TEST=fail")
            print("test_fsmount packet drift case did not fail closed")
            return 1
        case_count += 1

        write_text(
            matrix_path,
            replace_once(
                baseline,
                "approved local-only acceptable limits for both atomic64 and bitmap",
                "tentative local-only acceptable limits",
            ),
        )
        if not expect_failure(
            root,
            "missing_marker:* current acceptable-limit status: the dedicated survey packet now carries approved local-only acceptable limits for both atomic64 and bitmap",
        ):
            print("PHASE4_REMAINING_GAP_MATRIX_SELF_TEST=fail")
            print("perf limit drift case did not fail closed")
            return 1
        case_count += 1

        write_text(
            matrix_path,
            replace_once(
                baseline,
                "Validation and Perf Team owning that policy decision in coordination with the ABI and Runtime Team and Shared Subsystems Pod",
                "Tooling and Validation Team owning that policy decision on its own",
            ),
        )
        if not expect_failure(
            root,
            "missing_marker:* next bounded evidence step: keep the current local-only acceptable limits survey-only until a later bounded lane intentionally decides whether the existing bounds should stay local-only or support a broader shared CI perf-coverage claim, with the Validation and Perf Team owning that policy decision in coordination with the ABI and Runtime Team and Shared Subsystems Pod as the current gate rollback owners so the validator-first packet does not widen by accident. This matrix, `scripts/zigux/validate-phase4.py`, the dedicated workflow-route-count checker, `zigux/Makefile`, and the shared `zigux/tests/phase4_build.zig` entrypoint should stay aligned around the still-correctness-only shared replay routes while the dedicated perf-baseline survey keeps the approved local benchmark commands and the approved local-only acceptable limits for both rollback gates explicit until a later Phase 4 lane intentionally decides whether any broader shared perf promotion belongs in the shipped packet.",
        ):
            print("PHASE4_REMAINING_GAP_MATRIX_SELF_TEST=fail")
            print("perf owner drift case did not fail closed")
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
    print(f"PHASE4_REMAINING_GAP_MATRIX_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
