#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NOTE_REL = Path("Documentation/zigux/artifact-diff.md")

REQUIRED_PHASE4_USE_MARKERS = [
    "- `scripts/zigux/artifact_diff.py` stays the shared host-side comparison helper behind the committed artifact-check packets.",
    "- `scripts/zigux/check-artifact-diff-contract.py` reruns the bounded helper self-test, CLI help output, missing-required-args, missing-actual-operand, and invalid-mode parser coverage plus the text, JSON, SHA-256, missing-path, malformed-input, and repeat-run cases so the helper's outward contract stays deterministic before the broader Phase 4 validator and Zig gates run.",
    "- `scripts/zigux/check-phase4-artifact-diff-determinism.py` rechecks the helper and contract summary catalogs together so case-count, case-order, and repeat-case drift fail closed before the shared Phase 4 validator and Zig gates run.",
]

REQUIRED_EXACT_PACKET_MARKERS = [
    "`python3 scripts/zigux/artifact_diff.py --self-test` is the direct helper replay and must emit `ARTIFACT_DIFF_SELF_TEST=pass`",
    "`python3 scripts/zigux/check-artifact-diff-contract.py --self-test` is the isolated checker replay and must emit `ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass`",
    "`python3 scripts/zigux/check-artifact-diff-contract.py` is the live outward contract replay and must rerun `python3 scripts/zigux/artifact_diff.py --self-test` twice",
    "`python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test` is the isolated catalog-drift replay and must emit `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass`",
    "`python3 scripts/zigux/check-phase4-artifact-diff-determinism.py` is the live summary replay and must rerun the helper self-test summary packet",
]

REQUIRED_REVIEW_NOTE_MARKERS = [
    "- deterministic helper contract: `ARTIFACT_DIFF_RESULT_LINES=ARTIFACT_DIFF,MODE,EXPECTED,ACTUAL[,SHA256|EXPECTED_EXISTS|ACTUAL_EXISTS|EXPECTED_JSON_ERROR|ACTUAL_JSON_ERROR]`",
    "- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_JSON_INVALID` must prove malformed JSON fails without inventing digest or exists markers",
    "- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_MISSING` must prove missing-path failures emit only the EXISTS markers",
    "- deterministic helper catalog: `ARTIFACT_DIFF_SELF_TEST_CASE_COUNT` and `ARTIFACT_DIFF_SELF_TEST_CASES` must stay aligned with the helper's published `--self-test` packet",
    "- deterministic checker catalog: `ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT`, `ARTIFACT_DIFF_CONTRACT_BASE_CASES`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASES`, `ARTIFACT_DIFF_CONTRACT_CASE_COUNT`, and `ARTIFACT_DIFF_CONTRACT_CASES` must stay aligned with the published contract replay packet",
    "- deterministic checker self-test catalog: `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT` and `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES` must stay aligned with the isolated stale-catalog and review-note drift coverage",
    "- deterministic survey self-test catalog: `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT` and `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASES` must stay aligned with the isolated phase4-use, survey-note, survey-replay, review-note, docs-root, scripts-root, helper-summary, and contract-catalog drift coverage",
]

SELF_TEST_CASES = [
    "baseline_round_trip",
    "phase4_use_marker_drift",
    "helper_replay_marker_drift",
    "contract_self_test_marker_drift",
    "contract_replay_marker_drift",
    "determinism_self_test_marker_drift",
    "determinism_live_marker_drift",
    "result_lines_marker_drift",
    "json_invalid_marker_drift",
    "missing_path_marker_drift",
    "helper_catalog_marker_drift",
    "contract_catalog_marker_drift",
    "contract_selftest_catalog_marker_drift",
    "determinism_catalog_marker_drift",
    "missing_note_file",
]


def required_marker_count() -> int:
    return (
        len(REQUIRED_PHASE4_USE_MARKERS)
        + len(REQUIRED_EXACT_PACKET_MARKERS)
        + len(REQUIRED_REVIEW_NOTE_MARKERS)
    )


def validate_note_text(text: str) -> list[str]:
    failures: list[str] = []
    for marker in REQUIRED_PHASE4_USE_MARKERS:
        if marker not in text:
            failures.append(f"phase4_use:{marker}")
    for marker in REQUIRED_EXACT_PACKET_MARKERS:
        if marker not in text:
            failures.append(f"exact_packet:{marker}")
    for marker in REQUIRED_REVIEW_NOTE_MARKERS:
        if marker not in text:
            failures.append(f"review_note:{marker}")
    return failures


def validate_root(root: Path) -> list[str]:
    note_path = root / NOTE_REL
    if not note_path.exists():
        return [f"file:{NOTE_REL.as_posix()}"]
    return validate_note_text(note_path.read_text(encoding="utf-8"))


def build_fixture_note() -> str:
    lines = [
        "# Artifact Diff Policy",
        "",
        "Current Phase 4 use",
        *REQUIRED_PHASE4_USE_MARKERS,
        "",
        "## Phase 4 Exact Check Packet",
        "",
        *REQUIRED_EXACT_PACKET_MARKERS,
        "",
        "## Phase 4 Tooling Review Note",
        "",
        *REQUIRED_REVIEW_NOTE_MARKERS,
        "",
    ]
    return "\n".join(lines)


def expect_failure(label: str, root: Path, expected_prefix: str) -> None:
    failures = validate_root(root)
    if not failures:
        raise AssertionError(f"expected failure for {label}")
    if not any(item.startswith(expected_prefix) for item in failures):
        raise AssertionError(
            f"unexpected failures for {label}: expected prefix {expected_prefix!r}, got {failures}"
        )


def run_self_test() -> int:
    if len(set(SELF_TEST_CASES)) != len(SELF_TEST_CASES):
        raise AssertionError(f"duplicate self-test cases: {SELF_TEST_CASES}")

    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_artifact_note_") as tmp_dir:
        root = Path(tmp_dir)
        note_path = root / NOTE_REL
        note_path.parent.mkdir(parents=True, exist_ok=True)
        baseline = build_fixture_note()
        note_path.write_text(baseline, encoding="utf-8")

        failures = validate_root(root)
        if failures:
            raise AssertionError(f"baseline fixture failed: {failures}")
        case_count += 1

        drift_cases = [
            (
                "phase4_use_marker_drift",
                REQUIRED_PHASE4_USE_MARKERS[0],
                "phase4_use:",
            ),
            (
                "helper_replay_marker_drift",
                REQUIRED_EXACT_PACKET_MARKERS[0],
                "exact_packet:",
            ),
            (
                "contract_self_test_marker_drift",
                REQUIRED_EXACT_PACKET_MARKERS[1],
                "exact_packet:",
            ),
            (
                "contract_replay_marker_drift",
                REQUIRED_EXACT_PACKET_MARKERS[2],
                "exact_packet:",
            ),
            (
                "determinism_self_test_marker_drift",
                REQUIRED_EXACT_PACKET_MARKERS[3],
                "exact_packet:",
            ),
            (
                "determinism_live_marker_drift",
                REQUIRED_EXACT_PACKET_MARKERS[4],
                "exact_packet:",
            ),
            (
                "result_lines_marker_drift",
                REQUIRED_REVIEW_NOTE_MARKERS[0],
                "review_note:",
            ),
            (
                "json_invalid_marker_drift",
                REQUIRED_REVIEW_NOTE_MARKERS[1],
                "review_note:",
            ),
            (
                "missing_path_marker_drift",
                REQUIRED_REVIEW_NOTE_MARKERS[2],
                "review_note:",
            ),
            (
                "helper_catalog_marker_drift",
                REQUIRED_REVIEW_NOTE_MARKERS[3],
                "review_note:",
            ),
            (
                "contract_catalog_marker_drift",
                REQUIRED_REVIEW_NOTE_MARKERS[4],
                "review_note:",
            ),
            (
                "contract_selftest_catalog_marker_drift",
                REQUIRED_REVIEW_NOTE_MARKERS[5],
                "review_note:",
            ),
            (
                "determinism_catalog_marker_drift",
                REQUIRED_REVIEW_NOTE_MARKERS[6],
                "review_note:",
            ),
        ]

        for _label, marker, prefix in drift_cases:
            note_path.write_text(baseline.replace(marker, "", 1), encoding="utf-8")
            expect_failure(_label, root, prefix)
            case_count += 1

        note_path.unlink()
        expect_failure("missing_note_file", root, "file:")
        case_count += 1

    if case_count != len(SELF_TEST_CASES):
        raise AssertionError(
            f"self-test case drift: {case_count} != {len(SELF_TEST_CASES)}"
        )

    print("PHASE4_ARTIFACT_DIFF_NOTE_PACKET_SELF_TEST=pass")
    print(f"PHASE4_ARTIFACT_DIFF_NOTE_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    print(
        "PHASE4_ARTIFACT_DIFF_NOTE_PACKET_SELF_TEST_CASES="
        + ",".join(SELF_TEST_CASES)
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 4 artifact-diff note packet markers."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in checker coverage against a temporary fixture tree.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate_root(ROOT)
    if failures:
        print("PHASE4_ARTIFACT_DIFF_NOTE_PACKET=fail")
        print("MISSING_PHASE4_ARTIFACT_DIFF_NOTE_PACKET_MARKERS_START")
        for item in failures:
            print(item)
        print("MISSING_PHASE4_ARTIFACT_DIFF_NOTE_PACKET_MARKERS_END")
        return 1

    print("PHASE4_ARTIFACT_DIFF_NOTE_PACKET=pass")
    print(
        f"PHASE4_ARTIFACT_DIFF_NOTE_PACKET_MARKER_COUNT={required_marker_count()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
