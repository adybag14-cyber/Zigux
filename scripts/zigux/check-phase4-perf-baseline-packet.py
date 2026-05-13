#!/usr/bin/env python3
"""Validate the dedicated local-only Phase 4 perf-baseline packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
MANIFEST_REL = Path("zigux/tests/phase4_perf_baseline_manifest.json")
SURVEY_REL = Path("zigux/tests/phase4_perf_baseline_survey.zig")
MATRIX_REL = Path("Documentation/zigux/phase4-validation-matrix.md")
GATE_EVIDENCE_REL = Path("Documentation/zigux/phase4-gate-evidence.md")
CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
TESTS_README_REL = Path("zigux/tests/README.md")
BUILD_REL = Path("zigux/tests/phase4_build.zig")

REQUIRED_FILES = [
    MANIFEST_REL,
    SURVEY_REL,
    MATRIX_REL,
    GATE_EVIDENCE_REL,
    CHECKLIST_REL,
    TESTS_README_REL,
    BUILD_REL,
    Path("scripts/zigux/check-phase4-perf-baseline-packet.py"),
]

MANIFEST_MARKERS = [
    '"lane_key": "P4-L20"',
    '"owner": "Validation and Perf Team"',
    '"rollback_owner": "Validation and Perf Team"',
    '"decision_owner": "Validation and Perf Team"',
    '"shared_ci_perf_promotion_status": "pending"',
    '"surface": "zigux/tests/atomic64_diff.zig"',
    '"surface": "zigux/tests/bitmap_diff.zig"',
    '"gate_owner": "ABI and Runtime Team"',
    '"gate_owner": "Shared Subsystems Pod"',
    '"linux_style_wrapper": "make -C zigux phase4-perf-baseline-survey"',
    '"acceptable_limit_status": "approved_local_only"',
    '"acceptable_limit_max_elapsed_ns": 8192',
    '"acceptable_limit_max_elapsed_ns": 12288',
    '"status": "shared CI perf promotion pending"',
    "scripts/zigux/check-phase4-perf-baseline-packet.py",
]

SURVEY_MARKERS = [
    'test "phase4 perf baseline survey keeps the dedicated local checker packet explicit" {',
    'test "phase4 perf baseline survey keeps the dedicated local checker local-only" {',
    "scripts/zigux/check-phase4-perf-baseline-packet.py",
    "PHASE4_PERF_BASELINE_PACKET_CHECK=pass",
    "PHASE4_PERF_BASELINE_PACKET_SELF_TEST=pass",
    "phase4 perf baseline packet stays local-only and self-tested",
]

MATRIX_MARKERS = [
    "`zigux/tests/phase4_perf_baseline_survey.zig` dedicated local survey that keeps the approved local benchmark commands and the approved local-only acceptable limits machine-checked for both landed rollback gates",
    "`local_only_commands_and_limits_approved_shared_ci_perf_promotion_pending`",
    "Validation and Perf Team owning that policy decision in coordination with the ABI and Runtime Team and Shared Subsystems Pod as the current gate rollback owners",
]

GATE_EVIDENCE_MARKERS = [
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "shared CI perf coverage out of scope",
    "Validation and Perf Team stays named as the decision owner for any broader shared-CI perf promotion",
]

CHECKLIST_MARKERS = [
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion",
    "the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call",
]

TESTS_README_MARKERS = [
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
    "make -C zigux phase4-perf-baseline-survey",
]

BUILD_PRESENT_MARKERS = [
    'const perf_baseline_survey_step = b.step(',
    '"phase4-perf-baseline-survey"',
]

BUILD_ABSENT_MARKERS = [
    "test_step.dependOn(&run_perf_baseline_survey_tests.step);",
]

SELF_TEST_CASES = [
    "baseline_round_trip",
    "missing_manifest_file",
    "manifest_checker_reference_drift",
    "manifest_limit_drift",
    "survey_checker_test_drift",
    "survey_local_only_test_drift",
    "matrix_local_only_posture_drift",
    "gate_evidence_promotion_owner_drift",
    "review_checklist_coordination_owner_drift",
    "tests_readme_wrapper_drift",
    "build_shared_test_scope_drift",
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
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path.as_posix()}")
    if failures:
        return failures

    manifest_text = read_text(root / MANIFEST_REL)
    survey_text = read_text(root / SURVEY_REL)
    matrix_text = read_text(root / MATRIX_REL)
    gate_evidence_text = read_text(root / GATE_EVIDENCE_REL)
    checklist_text = read_text(root / CHECKLIST_REL)
    tests_readme_text = read_text(root / TESTS_README_REL)
    build_text = read_text(root / BUILD_REL)

    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        return [f"manifest_json:{exc.msg}"]

    for marker in MANIFEST_MARKERS:
        if marker not in manifest_text:
            failures.append(f"manifest_marker:{marker}")
    if manifest.get("shared_ci_perf_promotion_status") != "pending":
        failures.append("manifest_field:shared_ci_perf_promotion_status")
    if "scripts/zigux/check-phase4-perf-baseline-packet.py" not in manifest.get("reversible_delivery_evidence", ""):
        failures.append("manifest_field:reversible_delivery_evidence_checker")
    if "scripts/zigux/check-phase4-perf-baseline-packet.py" not in manifest.get("ready_next", ""):
        failures.append("manifest_field:ready_next_checker")

    for marker in SURVEY_MARKERS:
        if marker not in survey_text:
            failures.append(f"survey_marker:{marker}")
    for marker in MATRIX_MARKERS:
        if marker not in matrix_text:
            failures.append(f"matrix_marker:{marker}")
    for marker in GATE_EVIDENCE_MARKERS:
        if marker not in gate_evidence_text:
            failures.append(f"gate_evidence_marker:{marker}")
    for marker in CHECKLIST_MARKERS:
        if marker not in checklist_text:
            failures.append(f"checklist_marker:{marker}")
    for marker in TESTS_README_MARKERS:
        if marker not in tests_readme_text:
            failures.append(f"tests_readme_marker:{marker}")
    for marker in BUILD_PRESENT_MARKERS:
        if marker not in build_text:
            failures.append(f"build_marker:{marker}")
    for marker in BUILD_ABSENT_MARKERS:
        if marker in build_text:
            failures.append(f"build_unexpected_marker:{marker}")

    return failures


def build_fixture_tree(root: Path) -> None:
    write_text(
        root / MANIFEST_REL,
        json.dumps(
            {
                "lane_key": "P4-L20",
                "phase": "Phase 4",
                "owner": "Validation and Perf Team",
                "rollback_owner": "Validation and Perf Team",
                "decision_owner": "Validation and Perf Team",
                "coordination_owners": [
                    "ABI and Runtime Team",
                    "Shared Subsystems Pod",
                ],
                "shared_ci_perf_promotion_status": "pending",
                "reversible_delivery_evidence": (
                    "keep scripts/zigux/check-phase4-perf-baseline-packet.py, "
                    "zigux/tests/phase4_perf_baseline_manifest.json, "
                    "zigux/tests/phase4_perf_baseline_survey.zig, "
                    "Documentation/zigux/phase4-validation-matrix.md, "
                    "Documentation/zigux/phase4-gate-evidence.md, "
                    "Documentation/zigux/review-checklist.md, and "
                    "zigux/tests/phase4_build.zig aligned."
                ),
                "ready_next": (
                    "keep scripts/zigux/check-phase4-perf-baseline-packet.py, "
                    "zigux/tests/phase4_perf_baseline_survey.zig, and the "
                    "local-only perf packet aligned until a later lane "
                    "intentionally approves broader shared CI perf coverage."
                ),
                "surfaces": [
                    {
                        "surface": "zigux/tests/atomic64_diff.zig",
                        "gate_owner": "ABI and Runtime Team",
                        "gate_rollback_owner": "ABI and Runtime Team",
                        "threshold_posture": "threshold_pending_until_runtime_atomic64_scope_widens",
                    },
                    {
                        "surface": "zigux/tests/bitmap_diff.zig",
                        "gate_owner": "Shared Subsystems Pod",
                        "gate_rollback_owner": "Shared Subsystems Pod",
                        "threshold_posture": "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
                    },
                ],
                "atomic64": {
                    "linux_style_wrapper": "make -C zigux phase4-perf-baseline-survey",
                    "acceptable_limit_status": "approved_local_only",
                    "acceptable_limit_max_elapsed_ns": 8192,
                },
                "bitmap": {
                    "linux_style_wrapper": "make -C zigux phase4-perf-baseline-survey",
                    "acceptable_limit_status": "approved_local_only",
                    "acceptable_limit_max_elapsed_ns": 12288,
                },
                "promotion_decision": {
                    "status": "shared CI perf promotion pending",
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / SURVEY_REL,
        '\n'.join(
            [
                'const std = @import("std");',
                '',
                'test "phase4 perf baseline survey keeps the dedicated local checker packet explicit" {',
                '    const checker = try std.fs.cwd().readFileAlloc(',
                '        std.testing.allocator,',
                '        "scripts/zigux/check-phase4-perf-baseline-packet.py",',
                '        1024 * 1024,',
                '    );',
                '    defer std.testing.allocator.free(checker);',
                '    try std.testing.expect(std.mem.indexOf(u8, checker, "PHASE4_PERF_BASELINE_PACKET_CHECK=pass") != null);',
                '    try std.testing.expect(std.mem.indexOf(u8, checker, "PHASE4_PERF_BASELINE_PACKET_SELF_TEST=pass") != null);',
                '}',
                '',
                'test "phase4 perf baseline survey keeps the dedicated local checker local-only" {',
                '    const checker = try std.fs.cwd().readFileAlloc(',
                '        std.testing.allocator,',
                '        "scripts/zigux/check-phase4-perf-baseline-packet.py",',
                '        1024 * 1024,',
                '    );',
                '    defer std.testing.allocator.free(checker);',
                '    try std.testing.expect(std.mem.indexOf(u8, checker, "phase4 perf baseline packet stays local-only and self-tested") != null);',
                '}',
                '',
            ]
        ),
    )
    write_text(
        root / MATRIX_REL,
        "\n".join(
            [
                "# Phase 4 Validation Matrix",
                "`zigux/tests/phase4_perf_baseline_survey.zig` dedicated local survey that keeps the approved local benchmark commands and the approved local-only acceptable limits machine-checked for both landed rollback gates",
                "`local_only_commands_and_limits_approved_shared_ci_perf_promotion_pending`",
                "Validation and Perf Team owning that policy decision in coordination with the ABI and Runtime Team and Shared Subsystems Pod as the current gate rollback owners",
            ]
        )
        + "\n",
    )
    write_text(
        root / GATE_EVIDENCE_REL,
        "\n".join(
            [
                "# Phase 4 Gate Evidence",
                "zigux/tests/phase4_perf_baseline_manifest.json",
                "zigux/tests/phase4_perf_baseline_survey.zig",
                "shared CI perf coverage out of scope",
                "Validation and Perf Team stays named as the decision owner for any broader shared-CI perf promotion",
            ]
        )
        + "\n",
    )
    write_text(
        root / CHECKLIST_REL,
        "\n".join(
            [
                "# Zigux Review Checklist",
                "zigux/tests/phase4_perf_baseline_manifest.json",
                "zigux/tests/phase4_perf_baseline_survey.zig",
                "the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion",
                "the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call",
            ]
        )
        + "\n",
    )
    write_text(
        root / TESTS_README_REL,
        "\n".join(
            [
                "# zigux/tests",
                "zigux/tests/phase4_perf_baseline_manifest.json",
                "zigux/tests/phase4_perf_baseline_survey.zig",
                "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
                "make -C zigux phase4-perf-baseline-survey",
            ]
        )
        + "\n",
    )
    write_text(
        root / BUILD_REL,
        "\n".join(
            [
                'const perf_baseline_survey_step = b.step(',
                '    "phase4-perf-baseline-survey",',
                '    "Run the dedicated Phase 4 perf-baseline posture survey without widening the shared correctness-first packet",',
                ");",
            ]
        )
        + "\n",
    )
    write_text(root / "scripts/zigux/check-phase4-perf-baseline-packet.py", SCRIPT_PATH.read_text(encoding="utf-8"))


def expect_failure(root: Path, expected_prefix: str) -> bool:
    failures = validate_root(root)
    return any(item.startswith(expected_prefix) for item in failures)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_perf_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_fixture_tree(root)

        if validate_root(root):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("baseline fixture did not validate")
            return 1
        case_count += 1

        (root / MANIFEST_REL).unlink()
        if not expect_failure(root, "missing_file:zigux/tests/phase4_perf_baseline_manifest.json"):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("missing manifest case did not fail closed")
            return 1
        case_count += 1
        build_fixture_tree(root)

        write_text(
            root / MANIFEST_REL,
            replace_once(read_text(root / MANIFEST_REL), "scripts/zigux/check-phase4-perf-baseline-packet.py", "scripts/zigux/check-phase4-perf-baseline-note.py"),
        )
        if not expect_failure(root, "manifest_field:reversible_delivery_evidence_checker"):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("manifest checker reference drift case did not fail closed")
            return 1
        case_count += 1
        build_fixture_tree(root)

        write_text(
            root / MANIFEST_REL,
            replace_once(read_text(root / MANIFEST_REL), '"acceptable_limit_max_elapsed_ns": 12288', '"acceptable_limit_max_elapsed_ns": 12289'),
        )
        if not expect_failure(root, "manifest_marker:\"acceptable_limit_max_elapsed_ns\": 12288"):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("manifest limit drift case did not fail closed")
            return 1
        case_count += 1
        build_fixture_tree(root)

        write_text(
            root / SURVEY_REL,
            replace_once(
                read_text(root / SURVEY_REL),
                'test "phase4 perf baseline survey keeps the dedicated local checker packet explicit" {',
                'test "phase4 perf baseline survey keeps the dedicated local checker packet hidden" {',
            ),
        )
        if not expect_failure(root, 'survey_marker:test "phase4 perf baseline survey keeps the dedicated local checker packet explicit" {'):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("survey checker test drift case did not fail closed")
            return 1
        case_count += 1
        build_fixture_tree(root)

        write_text(
            root / SURVEY_REL,
            replace_once(
                read_text(root / SURVEY_REL),
                'test "phase4 perf baseline survey keeps the dedicated local checker local-only" {',
                'test "phase4 perf baseline survey widens the dedicated checker" {',
            ),
        )
        if not expect_failure(root, 'survey_marker:test "phase4 perf baseline survey keeps the dedicated local checker local-only" {'):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("survey local-only test drift case did not fail closed")
            return 1
        case_count += 1
        build_fixture_tree(root)

        write_text(
            root / MATRIX_REL,
            replace_once(
                read_text(root / MATRIX_REL),
                "`local_only_commands_and_limits_approved_shared_ci_perf_promotion_pending`",
                "`shared_ci_perf_promoted`",
            ),
        )
        if not expect_failure(root, "matrix_marker:`local_only_commands_and_limits_approved_shared_ci_perf_promotion_pending`"):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("matrix local-only posture drift case did not fail closed")
            return 1
        case_count += 1
        build_fixture_tree(root)

        write_text(
            root / GATE_EVIDENCE_REL,
            replace_once(
                read_text(root / GATE_EVIDENCE_REL),
                "Validation and Perf Team stays named as the decision owner for any broader shared-CI perf promotion",
                "Tooling and Validation Team stays named as the decision owner for any broader shared-CI perf promotion",
            ),
        )
        if not expect_failure(root, "gate_evidence_marker:Validation and Perf Team stays named as the decision owner for any broader shared-CI perf promotion"):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("gate evidence promotion owner drift case did not fail closed")
            return 1
        case_count += 1
        build_fixture_tree(root)

        write_text(
            root / CHECKLIST_REL,
            replace_once(
                read_text(root / CHECKLIST_REL),
                "the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call",
                "the Tooling and Validation Team as the only coordination owner for that policy call",
            ),
        )
        if not expect_failure(root, "checklist_marker:the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call"):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("review checklist coordination owner drift case did not fail closed")
            return 1
        case_count += 1
        build_fixture_tree(root)

        write_text(
            root / TESTS_README_REL,
            replace_once(
                read_text(root / TESTS_README_REL),
                "make -C zigux phase4-perf-baseline-survey",
                "make -C zigux phase4-perf-baseline-note",
            ),
        )
        if not expect_failure(root, "tests_readme_marker:make -C zigux phase4-perf-baseline-survey"):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("tests README wrapper drift case did not fail closed")
            return 1
        case_count += 1
        build_fixture_tree(root)

        write_text(
            root / BUILD_REL,
            read_text(root / BUILD_REL) + "test_step.dependOn(&run_perf_baseline_survey_tests.step);\n",
        )
        if not expect_failure(root, "build_unexpected_marker:test_step.dependOn(&run_perf_baseline_survey_tests.step);"):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("build shared-test scope drift case did not fail closed")
            return 1
        case_count += 1

    if case_count != len(SELF_TEST_CASES):
        print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
        print(f"unexpected self-test case count {case_count} != {len(SELF_TEST_CASES)}")
        return 1

    print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=pass")
    print(f"PHASE4_PERF_BASELINE_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the dedicated local-only Phase 4 perf-baseline packet."
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
        print("PHASE4_PERF_BASELINE_PACKET_CHECK=fail")
        print("PHASE4_PERF_BASELINE_PACKET_FAILURES_START")
        for item in failures:
            print(item)
        print("PHASE4_PERF_BASELINE_PACKET_FAILURES_END")
        return 1

    print("PHASE4_PERF_BASELINE_PACKET_CHECK=pass")
    print(f"PHASE4_PERF_BASELINE_PACKET_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
