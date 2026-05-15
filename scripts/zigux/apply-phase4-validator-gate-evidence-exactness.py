#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import tempfile


EXPECTED_VALIDATOR_BLOB_SHA = "694ad85743612aa0a595cd1752dd03c1013603ab"
PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT = 33
PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT = 19
PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT = 33
PHASE4_GATE_EVIDENCE_SELF_TEST_CASES_LINE = (
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=baseline_round_trip,shipped_target_count_drift,"
    "missing_exact_readback_heading,validator_blob_pin_drift,phase4_build_manifest_blob_pin_drift,"
    "phase4_build_survey_blob_pin_drift,phase9_build_manifest_blob_pin_drift,phase9_build_survey_blob_pin_drift,"
    "doc_readme_blob_pin_drift,script_readme_blob_pin_drift,tests_readme_blob_pin_drift,"
    "gate_evidence_self_test_case_count_drift,gate_evidence_self_test_cases_drift,"
    "shared_validator_reruns_gate_evidence_self_test_drift,shared_validator_expected_target_count_drift,"
    "shared_validator_expected_self_test_case_count_drift,runtime_atomic64_survey_packet_presence_drift,"
    "bitmap_diff_survey_replay_marker_drift,kprobe_gap_packet_presence_drift,kprobe_owner_drift,"
    "kprobe_validation_entrypoint_drift,kprobe_next_step_drift,perf_baseline_packet_presence_drift,"
    "perf_baseline_note_split_marker_drift,perf_baseline_owner_drift,"
    "perf_baseline_shared_promotion_status_drift,test_fsmount_gap_packet_presence_drift,"
    "test_fsmount_threshold_posture_drift,test_fsmount_owner_drift,test_fsmount_validation_entrypoint_drift,"
    "test_fsmount_linux_style_wrapper_drift,test_fsmount_next_step_drift,missing_note_file"
)

CONSTANTS_BLOCK = f"""PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT = {PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}
PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT = {PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT}
PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT = {PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}
PHASE4_GATE_EVIDENCE_SELF_TEST_CASES_LINE = (
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=baseline_round_trip,shipped_target_count_drift,"
    "missing_exact_readback_heading,validator_blob_pin_drift,phase4_build_manifest_blob_pin_drift,"
    "phase4_build_survey_blob_pin_drift,phase9_build_manifest_blob_pin_drift,phase9_build_survey_blob_pin_drift,"
    "doc_readme_blob_pin_drift,script_readme_blob_pin_drift,tests_readme_blob_pin_drift,"
    "gate_evidence_self_test_case_count_drift,gate_evidence_self_test_cases_drift,"
    "shared_validator_reruns_gate_evidence_self_test_drift,shared_validator_expected_target_count_drift,"
    "shared_validator_expected_self_test_case_count_drift,runtime_atomic64_survey_packet_presence_drift,"
    "bitmap_diff_survey_replay_marker_drift,kprobe_gap_packet_presence_drift,kprobe_owner_drift,"
    "kprobe_validation_entrypoint_drift,kprobe_next_step_drift,perf_baseline_packet_presence_drift,"
    "perf_baseline_note_split_marker_drift,perf_baseline_owner_drift,"
    "perf_baseline_shared_promotion_status_drift,test_fsmount_gap_packet_presence_drift,"
    "test_fsmount_threshold_posture_drift,test_fsmount_owner_drift,test_fsmount_validation_entrypoint_drift,"
    "test_fsmount_linux_style_wrapper_drift,test_fsmount_next_step_drift,missing_note_file"
)

"""

SELF_TEST_INSERT_BLOCK = """
        gate_evidence_path.write_text(
            original_gate_evidence.replace(
                f"- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}`\\n",
                f"- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT - 1}`\\n",
                1,
            ),
            encoding=\"utf-8\",
        )
        failures = validate_root(root)
        if (
            f\"gate_evidence:PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}\"
            not in failures
        ):
            print(\"PHASE4_VALIDATOR_SELF_TEST=fail\")
            print(\"PHASE4_VALIDATOR_SELF_TEST_FAILURES_START\")
            for item in failures:
                print(item)
            print(\"PHASE4_VALIDATOR_SELF_TEST_FAILURES_END\")
            return 1
        gate_evidence_path.write_text(original_gate_evidence, encoding=\"utf-8\")

        gate_evidence_path.write_text(
            original_gate_evidence.replace(
                f\"- `{PHASE4_GATE_EVIDENCE_SELF_TEST_CASES_LINE}`\\n\",
                \"- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=baseline_round_trip`\\n\",
                1,
            ),
            encoding=\"utf-8\",
        )
        failures = validate_root(root)
        if f\"gate_evidence:{PHASE4_GATE_EVIDENCE_SELF_TEST_CASES_LINE}\" not in failures:
            print(\"PHASE4_VALIDATOR_SELF_TEST=fail\")
            print(\"PHASE4_VALIDATOR_SELF_TEST_FAILURES_START\")
            for item in failures:
                print(item)
            print(\"PHASE4_VALIDATOR_SELF_TEST_FAILURES_END\")
            return 1
        gate_evidence_path.write_text(original_gate_evidence, encoding=\"utf-8\")

        gate_evidence_path.write_text(
            original_gate_evidence.replace(
                f\"- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT}`\\n\",
                f\"- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT - 1}`\\n\",
                1,
            ),
            encoding=\"utf-8\",
        )
        failures = validate_root(root)
        if (
            \"gate_evidence:PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=\"
            f\"{PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT}\"
            not in failures
        ):
            print(\"PHASE4_VALIDATOR_SELF_TEST=fail\")
            print(\"PHASE4_VALIDATOR_SELF_TEST_FAILURES_START\")
            for item in failures:
                print(item)
            print(\"PHASE4_VALIDATOR_SELF_TEST_FAILURES_END\")
            return 1
        gate_evidence_path.write_text(original_gate_evidence, encoding=\"utf-8\")

        gate_evidence_path.write_text(
            original_gate_evidence.replace(
                f\"- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}`\\n\",
                f\"- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT - 1}`\\n\",
                1,
            ),
            encoding=\"utf-8\",
        )
        failures = validate_root(root)
        if (
            \"gate_evidence:PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=\"
            f\"{PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}\"
            not in failures
        ):
            print(\"PHASE4_VALIDATOR_SELF_TEST=fail\")
            print(\"PHASE4_VALIDATOR_SELF_TEST_FAILURES_START\")
            for item in failures:
                print(item)
            print(\"PHASE4_VALIDATOR_SELF_TEST_FAILURES_END\")
            return 1
        gate_evidence_path.write_text(original_gate_evidence, encoding=\"utf-8\")
"""


def replace_once(source: str, old: str, new: str) -> str:
    count = source.count(old)
    if count != 1:
        raise ValueError(f"expected exactly one occurrence of snippet, found {count}: {old[:80]!r}")
    return source.replace(old, new, 1)


def git_blob_sha1_bytes(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("utf-8")
    return hashlib.sha1(header + payload).hexdigest()


def verify_expected_input_blob(
    target: Path,
    source: str,
    *,
    expected_blob_sha: str,
) -> None:
    actual_blob_sha = git_blob_sha1_bytes(source.encode("utf-8"))
    if actual_blob_sha != expected_blob_sha:
        raise ValueError(
            "refusing to rewrite unexpected validate-phase4.py blob: "
            f"{target} -> {actual_blob_sha} != {expected_blob_sha}"
        )


def rewrite(source: str) -> str:
    updated = source
    updated = replace_once(updated, "REQUIRED_GATE_EVIDENCE_MARKERS = [\n", CONSTANTS_BLOCK + "REQUIRED_GATE_EVIDENCE_MARKERS = [\n")
    updated = replace_once(
        updated,
        '    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=",\n',
        '    f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}",\n',
    )
    updated = replace_once(
        updated,
        '    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=",\n',
        '    PHASE4_GATE_EVIDENCE_SELF_TEST_CASES_LINE,\n',
    )
    updated = replace_once(
        updated,
        '    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=",\n',
        '    f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT}",\n',
    )
    updated = replace_once(
        updated,
        '    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=",\n',
        '    f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}",\n',
    )
    updated = replace_once(
        updated,
        '        "- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=21`",\n',
        '        f"- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}`",\n',
    )
    updated = replace_once(
        updated,
        '        "- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=baseline_round_trip,...`",\n',
        '        f"- `{PHASE4_GATE_EVIDENCE_SELF_TEST_CASES_LINE}`",\n',
    )
    updated = replace_once(
        updated,
        '        "- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=16`",\n',
        '        f"- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT}`",\n',
    )
    updated = replace_once(
        updated,
        '        "- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=21`",\n',
        '        f"- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}`",\n',
    )
    updated = replace_once(
        updated,
        '        gate_evidence_path.write_text(original_gate_evidence, encoding="utf-8")\n\n        matrix_path = root / "Documentation/zigux/phase4-validation-matrix.md"\n',
        '        gate_evidence_path.write_text(original_gate_evidence, encoding="utf-8")\n'
        + SELF_TEST_INSERT_BLOCK
        + '\n        matrix_path = root / "Documentation/zigux/phase4-validation-matrix.md"\n',
    )
    return updated


def self_test() -> int:
    sample_source = """REQUIRED_GATE_EVIDENCE_MARKERS = [
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=",
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=",
    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=",
    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=",
]

    lines = [
        "- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=21`",
        "- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=baseline_round_trip,...`",
        "- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=16`",
        "- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=21`",
    ]

        gate_evidence_path.write_text(original_gate_evidence, encoding="utf-8")

        matrix_path = root / "Documentation/zigux/phase4-validation-matrix.md"
"""
    rewritten = rewrite(sample_source)
    required_markers = [
        f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT = {PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}",
        "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES_LINE = (",
        f'f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={{PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}}"',
        "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES_LINE,",
        'f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT}"',
        'f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}"',
        "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT - 1",
        "gate_evidence:PHASE4_GATE_EVIDENCE_SELF_TEST_CASES_LINE" if False else "gate_evidence:{PHASE4_GATE_EVIDENCE_SELF_TEST_CASES_LINE}",
        'matrix_path = root / "Documentation/zigux/phase4-validation-matrix.md"',
    ]
    missing = [marker for marker in required_markers if marker not in rewritten]
    if missing:
        print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_APPLY_SELF_TEST=fail")
        for marker in missing:
            print(f"MISSING:{marker}")
        return 1
    if rewritten.count("PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=baseline_round_trip,...") != 0:
        print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_APPLY_SELF_TEST=fail")
        print("STALE_SHORT_CASES_LINE_REMAINED")
        return 1
    sample_blob_sha = git_blob_sha1_bytes(sample_source.encode("utf-8"))
    with tempfile.TemporaryDirectory(prefix="phase4-validator-exactness-apply-") as tmp_dir:
        sample_path = Path(tmp_dir) / "validate-phase4.py"
        sample_path.write_text(sample_source, encoding="utf-8", newline="\n")
        verify_expected_input_blob(
            sample_path,
            sample_source,
            expected_blob_sha=sample_blob_sha,
        )
        drifted_source = sample_source + "\n# drifted\n"
        sample_path.write_text(drifted_source, encoding="utf-8", newline="\n")
        try:
            verify_expected_input_blob(
                sample_path,
                drifted_source,
                expected_blob_sha=sample_blob_sha,
            )
        except ValueError as exc:
            if "refusing to rewrite unexpected validate-phase4.py blob" not in str(exc):
                print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_APPLY_SELF_TEST=fail")
                print(f"UNEXPECTED_BLOB_GUARD_MESSAGE:{exc}")
                return 1
        else:
            print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_APPLY_SELF_TEST=fail")
            print("BLOB_GUARD_DID_NOT_FAIL_CLOSED")
            return 1
    print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_APPLY_SELF_TEST=pass")
    return 0


def resolve_target_path(args: argparse.Namespace) -> Path | None:
    if args.input_file:
        return Path(args.input_file).resolve()
    if args.repo_root:
        repo_root = Path(args.repo_root).resolve()
        return repo_root / "scripts/zigux/validate-phase4.py"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rewrite scripts/zigux/validate-phase4.py so the Phase 4 validator exact-checks current gate-evidence self-test counts and the full cases line."
    )
    parser.add_argument("repo_root", nargs="?", help="Path to a Zigux checkout.")
    parser.add_argument(
        "--input-file",
        help="Rewrite this exact validate-phase4.py file instead of resolving it from repo_root.",
    )
    parser.add_argument("--write-in-place", action="store_true", help="Rewrite the file in place.")
    parser.add_argument("--output", help="Write the rewritten file to this path instead of stdout.")
    parser.add_argument("--self-test", action="store_true", help="Run a focused rewrite self-test.")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    target = resolve_target_path(args)
    if target is None:
        parser.error("repo_root or --input-file is required unless --self-test is used")

    source = target.read_text(encoding="utf-8")
    verify_expected_input_blob(
        target,
        source,
        expected_blob_sha=EXPECTED_VALIDATOR_BLOB_SHA,
    )
    rewritten = rewrite(source)

    if args.write_in_place:
        target.write_text(rewritten, encoding="utf-8", newline="\n")
        print(f"rewrote {target}")
        return 0

    if args.output:
        output_path = Path(args.output).resolve()
        output_path.write_text(rewritten, encoding="utf-8", newline="\n")
        print(f"wrote {output_path}")
        return 0

    print(rewritten, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
