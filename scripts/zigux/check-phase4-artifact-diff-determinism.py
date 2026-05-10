#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIFF_NOTE = ROOT / "Documentation" / "zigux" / "artifact-diff.md"

EXPECTED_PHASE4_USE_MARKERS = [
    "- `scripts/zigux/check-phase4-artifact-diff-determinism.py` rechecks the helper and contract summary catalogs together so case-count, case-order, and repeat-case drift fail closed before the shared Phase 4 validator and Zig gates run.",
]

EXPECTED_REVIEW_NOTE_MARKERS = [
    "- owner: `Zigux product maintainers working in scripts/zigux and Documentation/zigux`",
    "- rollback owner: `Zigux product maintainers working in scripts/zigux and Documentation/zigux`",
    "- fallback rule: if `scripts/zigux/artifact_diff.py` regresses, keep the committed expected artifact plus the current authoritative C or documented replay command as the source of truth until the helper contract is repaired",
    "- deterministic replay entrypoint: `python3 scripts/zigux/check-artifact-diff-contract.py` is the reviewable contract rerun for the shared host-side helper and should stay aligned with the outward line rules below",
    "- deterministic survey entrypoint: `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py` must keep the helper self-test catalog, the contract summary catalog, and the repeat-case packet aligned with this note and the shared validator packet",
    "- review rule: any change to the helper's emitted `ARTIFACT_DIFF=*`, `MODE=*`, `EXPECTED=*`, `ACTUAL=*`, `SHA256=*`, `EXPECTED_EXISTS=*`, `ACTUAL_EXISTS=*`, `EXPECTED_JSON_ERROR=*`, or `ACTUAL_JSON_ERROR=*` lines must update this note in the same change so the published host-side artifact packet stays reviewable",
    "- boundary: keep this note scoped to the shared host-side diff helper; Phase 4 gate ownership for `zigux/tests/*.zig` still belongs in `Documentation/zigux/phase4-validation-matrix.md`",
    "- deterministic helper contract: `ARTIFACT_DIFF_RESULT_LINES=ARTIFACT_DIFF,MODE,EXPECTED,ACTUAL[,SHA256|EXPECTED_EXISTS|ACTUAL_EXISTS|EXPECTED_JSON_ERROR|ACTUAL_JSON_ERROR]`",
    "- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_TEXT` must prove both the stable text pass shape and the direct text mismatch fail shape",
    "- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_JSON` must prove canonical JSON equivalence while `ARTIFACT_DIFF_SELF_TEST_JSON_INVALID` proves malformed JSON fails without inventing digest or exists markers",
    "- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_SHA256` must prove both the shared digest pass line and the exact expected-vs-actual digest drift lines",
    "- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_MISSING` must prove missing-path failures emit only the EXISTS markers",
    "- deterministic helper catalog: `ARTIFACT_DIFF_SELF_TEST_CASE_COUNT` and `ARTIFACT_DIFF_SELF_TEST_CASES` must stay aligned with the helper's published `--self-test` packet",
    "- deterministic checker catalog: `ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT`, `ARTIFACT_DIFF_CONTRACT_BASE_CASES`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASES`, `ARTIFACT_DIFF_CONTRACT_CASE_COUNT`, and `ARTIFACT_DIFF_CONTRACT_CASES` must stay aligned with the published contract replay packet",
    "- deterministic checker self-test catalog: `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT` and `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES` must stay aligned with the isolated stale-catalog and review-note drift coverage",
]

EXPECTED_HELPER_SELF_TEST_CASES = [
    "text_pass",
    "text_mismatch",
    "json_pass",
    "json_mismatch",
    "json_invalid_expected",
    "json_invalid_actual",
    "json_invalid_both",
    "json_missing_expected",
    "json_missing_actual",
    "json_missing_both",
    "sha256_pass",
    "sha256_drift",
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
    "sha256_missing_expected",
    "sha256_missing_actual",
    "sha256_missing_both",
    "cli_help_output",
    "cli_missing_required_args",
    "cli_missing_actual_operand",
    "cli_invalid_mode",
    "invalid_mode_rejected",
]

EXPECTED_CONTRACT_CASES = [
    "helper_self_test",
    "helper_self_test_repeat",
    "cli_help_output",
    "cli_help_output_repeat",
    "cli_missing_required_args",
    "cli_missing_actual_operand",
    "cli_invalid_mode",
    "text_pass",
    "text_pass_repeat",
    "text_mismatch",
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
    "json_pass",
    "json_mismatch",
    "json_mismatch_repeat",
    "json_missing_expected",
    "json_missing_actual",
    "json_missing_both",
    "json_invalid_expected",
    "json_invalid_actual",
    "json_invalid_both",
    "sha256_pass",
    "sha256_missing_expected",
    "sha256_missing_actual",
    "sha256_missing_both",
    "sha256_drift",
    "sha256_drift_repeat",
]

EXPECTED_REPEAT_CONTRACT_CASES = [
    "helper_self_test_repeat",
    "cli_help_output_repeat",
    "text_pass_repeat",
    "json_mismatch_repeat",
    "sha256_drift_repeat",
]

EXPECTED_CONTRACT_SELF_TEST_CASES = [
    "catalog_shape",
    "review_note_marker_round_trip",
    "review_note_marker_drift",
    "helper_summary_round_trip",
    "contract_summary_round_trip",
    "helper_summary_status_drift",
    "helper_summary_count_drift",
    "helper_summary_duplicate_case_drift",
    "helper_summary_case_order_drift",
    "contract_summary_status_drift",
    "contract_summary_base_count_drift",
    "contract_summary_base_case_order_drift",
    "contract_summary_repeat_count_drift",
    "contract_summary_repeat_case_order_drift",
    "contract_summary_case_count_drift",
    "contract_summary_duplicate_case_drift",
    "contract_summary_case_order_drift",
]

EXPECTED_SELF_TEST_CASES = [
    "phase4_use_marker_missing",
    "phase4_use_marker_duplicate",
    "review_note_marker_missing",
    "review_note_marker_duplicate",
    "helper_status_drift",
    "helper_case_order_drift",
    "helper_case_count_drift",
    "helper_duplicate_case_drift",
    "contract_self_test_status_drift",
    "contract_self_test_case_drift",
    "contract_self_test_duplicate_case_drift",
    "contract_catalog_status_drift",
    "contract_catalog_missing_cli_invalid_mode",
    "contract_base_case_order_drift",
    "contract_repeat_case_order_drift",
    "contract_repeat_case_duplicate_drift",
    "contract_catalog_case_order_drift",
    "contract_catalog_duplicate_case_drift",
]


def _extract_value(lines: list[str], prefix: str) -> str:
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix) :]
    raise AssertionError(f"missing output line for {prefix!r}: {lines}")


def _parse_case_list(lines: list[str], count_prefix: str, list_prefix: str) -> list[str]:
    count_text = _extract_value(lines, count_prefix)
    cases_text = _extract_value(lines, list_prefix)
    try:
        expected_count = int(count_text)
    except ValueError as exc:
        raise AssertionError(f"invalid integer for {count_prefix!r}: {count_text!r}") from exc
    cases = [] if not cases_text else cases_text.split(",")
    if len(cases) != expected_count:
        raise AssertionError(
            f"count/list drift for {count_prefix!r} and {list_prefix!r}: count={expected_count} cases={cases}"
        )
    if len(set(cases)) != len(cases):
        raise AssertionError(f"duplicate cases in {list_prefix!r}: {cases}")
    return cases


def assert_phase4_use_markers(note_text: str) -> None:
    missing, duplicate = [], []
    for marker in EXPECTED_PHASE4_USE_MARKERS:
        count = note_text.count(marker)
        if count == 0:
            missing.append(marker)
        elif count != 1:
            duplicate.append(f"{marker}:{count}")
    if missing or duplicate:
        problems = []
        if missing:
            problems.append(
                "artifact-diff Current Phase 4 use section missing required markers: "
                f"{missing}"
            )
        if duplicate:
            problems.append(
                "artifact-diff Current Phase 4 use section duplicated required markers: "
                f"{duplicate}"
            )
        raise AssertionError("; ".join(problems))


def assert_review_note_markers(note_text: str) -> None:
    missing, duplicate = [], []
    for marker in EXPECTED_REVIEW_NOTE_MARKERS:
        count = note_text.count(marker)
        if count == 0:
            missing.append(marker)
        elif count != 1:
            duplicate.append(f"{marker}:{count}")
    if missing or duplicate:
        problems = []
        if missing:
            problems.append(f"artifact-diff review note missing required markers: {missing}")
        if duplicate:
            problems.append(f"artifact-diff review note duplicated required markers: {duplicate}")
        raise AssertionError("; ".join(problems))


def assert_helper_self_test_lines(lines: list[str]) -> None:
    if _extract_value(lines, "ARTIFACT_DIFF_SELF_TEST=") != "pass":
        raise AssertionError(f"unexpected helper self-test status: {lines}")
    cases = _parse_case_list(
        lines,
        "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=",
        "ARTIFACT_DIFF_SELF_TEST_CASES=",
    )
    if cases != EXPECTED_HELPER_SELF_TEST_CASES:
        raise AssertionError(
            "artifact-diff helper self-test catalog drifted: "
            f"expected {EXPECTED_HELPER_SELF_TEST_CASES}, got {cases}"
        )


def assert_contract_self_test_lines(lines: list[str]) -> None:
    if _extract_value(lines, "ARTIFACT_DIFF_CONTRACT_SELF_TEST=") != "pass":
        raise AssertionError(f"unexpected contract self-test status: {lines}")
    cases = _parse_case_list(
        lines,
        "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=",
        "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES=",
    )
    if cases != EXPECTED_CONTRACT_SELF_TEST_CASES:
        raise AssertionError(
            "artifact-diff contract self-test catalog drifted: "
            f"expected {EXPECTED_CONTRACT_SELF_TEST_CASES}, got {cases}"
        )


def assert_contract_lines(lines: list[str]) -> None:
    if _extract_value(lines, "ARTIFACT_DIFF_CONTRACT=") != "pass":
        raise AssertionError(f"unexpected contract status: {lines}")
    base_cases = _parse_case_list(
        lines,
        "ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=",
        "ARTIFACT_DIFF_CONTRACT_BASE_CASES=",
    )
    repeat_cases = _parse_case_list(
        lines,
        "ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=",
        "ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=",
    )
    all_cases = _parse_case_list(
        lines,
        "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=",
        "ARTIFACT_DIFF_CONTRACT_CASES=",
    )
    expected_base_cases = [
        case for case in EXPECTED_CONTRACT_CASES if case not in EXPECTED_REPEAT_CONTRACT_CASES
    ]
    if base_cases != expected_base_cases:
        raise AssertionError(
            f"artifact-diff base contract catalog drifted: expected {expected_base_cases}, got {base_cases}"
        )
    if repeat_cases != EXPECTED_REPEAT_CONTRACT_CASES:
        raise AssertionError(
            f"artifact-diff repeat contract catalog drifted: expected {EXPECTED_REPEAT_CONTRACT_CASES}, got {repeat_cases}"
        )
    if all_cases != EXPECTED_CONTRACT_CASES:
        raise AssertionError(
            f"artifact-diff full contract catalog drifted: expected {EXPECTED_CONTRACT_CASES}, got {all_cases}"
        )


def _run_script(script: Path, *args: str) -> list[str]:
    completed = subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"{script.name} {' '.join(args)} failed with exit {completed.returncode}: "
            f"stdout={completed.stdout.splitlines()} stderr={completed.stderr.splitlines()}"
        )
    if completed.stderr:
        raise AssertionError(
            f"{script.name} {' '.join(args)} emitted stderr: {completed.stderr.splitlines()}"
        )
    return completed.stdout.splitlines()


def run_live_check(root: Path) -> None:
    helper_script = root / "scripts/zigux/artifact_diff.py"
    contract_script = root / "scripts/zigux/check-artifact-diff-contract.py"
    note_text = ARTIFACT_DIFF_NOTE.read_text(encoding="utf-8") if root == ROOT else (root / "Documentation/zigux/artifact-diff.md").read_text(encoding="utf-8")
    assert_phase4_use_markers(note_text)
    assert_review_note_markers(note_text)
    assert_helper_self_test_lines(_run_script(helper_script, "--self-test"))
    assert_contract_self_test_lines(_run_script(contract_script, "--self-test"))
    assert_contract_lines(_run_script(contract_script))


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def build_fixture_tree(root: Path) -> None:
    helper_lines = [
        "ARTIFACT_DIFF_SELF_TEST=pass",
        f"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(EXPECTED_HELPER_SELF_TEST_CASES)}",
        "ARTIFACT_DIFF_SELF_TEST_CASES=" + ",".join(EXPECTED_HELPER_SELF_TEST_CASES),
    ]
    contract_self_test_lines = [
        "ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass",
        f"ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT={len(EXPECTED_CONTRACT_SELF_TEST_CASES)}",
        "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES=" + ",".join(EXPECTED_CONTRACT_SELF_TEST_CASES),
    ]
    base_cases = [
        case for case in EXPECTED_CONTRACT_CASES if case not in EXPECTED_REPEAT_CONTRACT_CASES
    ]
    contract_lines = [
        "ARTIFACT_DIFF_CONTRACT=pass",
        f"ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT={len(base_cases)}",
        "ARTIFACT_DIFF_CONTRACT_BASE_CASES=" + ",".join(base_cases),
        f"ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT={len(EXPECTED_REPEAT_CONTRACT_CASES)}",
        "ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=" + ",".join(EXPECTED_REPEAT_CONTRACT_CASES),
        f"ARTIFACT_DIFF_CONTRACT_CASE_COUNT={len(EXPECTED_CONTRACT_CASES)}",
        "ARTIFACT_DIFF_CONTRACT_CASES=" + ",".join(EXPECTED_CONTRACT_CASES),
    ]
    _write(
        root / "scripts/zigux/artifact_diff.py",
        "\n".join([
            "#!/usr/bin/env python3",
            "import sys",
            "if '--self-test' in sys.argv:",
            *[f"    print({line!r})" for line in helper_lines],
            "    raise SystemExit(0)",
            "raise SystemExit(1)",
            "",
        ]),
    )
    _write(
        root / "scripts/zigux/check-artifact-diff-contract.py",
        "\n".join([
            "#!/usr/bin/env python3",
            "import sys",
            "if '--self-test' in sys.argv:",
            *[f"    print({line!r})" for line in contract_self_test_lines],
            "    raise SystemExit(0)",
            *[f"print({line!r})" for line in contract_lines],
            "raise SystemExit(0)",
            "",
        ]),
    )
    _write(
        root / "Documentation/zigux/artifact-diff.md",
        "\n".join([
            "# Artifact Diff Policy",
            "",
            "Current Phase 4 use",
            *EXPECTED_PHASE4_USE_MARKERS,
            "",
            "## Phase 4 Tooling Review Note",
            "",
            *EXPECTED_REVIEW_NOTE_MARKERS,
            "",
        ]),
    )


def expect_assertion(label: str, callback) -> None:
    try:
        callback()
    except AssertionError:
        return
    raise AssertionError(f"expected AssertionError for self-test case {label}")


def run_self_test() -> None:
    covered_cases: list[str] = []
    with tempfile.TemporaryDirectory(prefix="phase4_artifact_diff_determinism_") as tmp_dir:
        root = Path(tmp_dir)
        build_fixture_tree(root)
        run_live_check(root)

        expect_assertion("phase4_use_marker_missing", lambda: assert_phase4_use_markers("Current Phase 4 use\n"))
        covered_cases.append("phase4_use_marker_missing")
        expect_assertion(
            "phase4_use_marker_duplicate",
            lambda: assert_phase4_use_markers("\n".join(["Current Phase 4 use", *EXPECTED_PHASE4_USE_MARKERS, EXPECTED_PHASE4_USE_MARKERS[0]])),
        )
        covered_cases.append("phase4_use_marker_duplicate")
        expect_assertion("review_note_marker_missing", lambda: assert_review_note_markers("\n".join(EXPECTED_REVIEW_NOTE_MARKERS[:-1])))
        covered_cases.append("review_note_marker_missing")
        expect_assertion(
            "review_note_marker_duplicate",
            lambda: assert_review_note_markers("\n".join([*EXPECTED_REVIEW_NOTE_MARKERS, EXPECTED_REVIEW_NOTE_MARKERS[0]])),
        )
        covered_cases.append("review_note_marker_duplicate")

        expect_assertion(
            "helper_status_drift",
            lambda: assert_helper_self_test_lines([
                "ARTIFACT_DIFF_SELF_TEST=fail",
                f"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(EXPECTED_HELPER_SELF_TEST_CASES)}",
                "ARTIFACT_DIFF_SELF_TEST_CASES=" + ",".join(EXPECTED_HELPER_SELF_TEST_CASES),
            ]),
        )
        covered_cases.append("helper_status_drift")
        expect_assertion(
            "helper_case_order_drift",
            lambda: assert_helper_self_test_lines([
                "ARTIFACT_DIFF_SELF_TEST=pass",
                f"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(EXPECTED_HELPER_SELF_TEST_CASES)}",
                "ARTIFACT_DIFF_SELF_TEST_CASES=" + ",".join(["text_mismatch", "text_pass", *EXPECTED_HELPER_SELF_TEST_CASES[2:]]),
            ]),
        )
        covered_cases.append("helper_case_order_drift")
        expect_assertion(
            "helper_case_count_drift",
            lambda: assert_helper_self_test_lines([
                "ARTIFACT_DIFF_SELF_TEST=pass",
                "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=18",
                "ARTIFACT_DIFF_SELF_TEST_CASES=" + ",".join(EXPECTED_HELPER_SELF_TEST_CASES),
            ]),
        )
        covered_cases.append("helper_case_count_drift")
        expect_assertion(
            "helper_duplicate_case_drift",
            lambda: assert_helper_self_test_lines([
                "ARTIFACT_DIFF_SELF_TEST=pass",
                f"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(EXPECTED_HELPER_SELF_TEST_CASES)}",
                "ARTIFACT_DIFF_SELF_TEST_CASES=" + ",".join(["text_pass", "text_pass", *EXPECTED_HELPER_SELF_TEST_CASES[2:]]),
            ]),
        )
        covered_cases.append("helper_duplicate_case_drift")

        expect_assertion(
            "contract_self_test_status_drift",
            lambda: assert_contract_self_test_lines([
                "ARTIFACT_DIFF_CONTRACT_SELF_TEST=fail",
                f"ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT={len(EXPECTED_CONTRACT_SELF_TEST_CASES)}",
                "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES=" + ",".join(EXPECTED_CONTRACT_SELF_TEST_CASES),
            ]),
        )
        covered_cases.append("contract_self_test_status_drift")
        expect_assertion(
            "contract_self_test_case_drift",
            lambda: assert_contract_self_test_lines([
                "ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass",
                f"ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT={len(EXPECTED_CONTRACT_SELF_TEST_CASES)}",
                "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES=" + ",".join(["catalog_shape", "helper_summary_round_trip", *EXPECTED_CONTRACT_SELF_TEST_CASES[2:]]),
            ]),
        )
        covered_cases.append("contract_self_test_case_drift")
        expect_assertion(
            "contract_self_test_duplicate_case_drift",
            lambda: assert_contract_self_test_lines([
                "ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass",
                f"ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT={len(EXPECTED_CONTRACT_SELF_TEST_CASES)}",
                "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES=" + ",".join(["catalog_shape", "catalog_shape", *EXPECTED_CONTRACT_SELF_TEST_CASES[2:]]),
            ]),
        )
        covered_cases.append("contract_self_test_duplicate_case_drift")

        base_cases = [case for case in EXPECTED_CONTRACT_CASES if case not in EXPECTED_REPEAT_CONTRACT_CASES]
        expect_assertion(
            "contract_catalog_status_drift",
            lambda: assert_contract_lines([
                "ARTIFACT_DIFF_CONTRACT=fail",
                f"ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT={len(base_cases)}",
                "ARTIFACT_DIFF_CONTRACT_BASE_CASES=" + ",".join(base_cases),
                f"ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT={len(EXPECTED_REPEAT_CONTRACT_CASES)}",
                "ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=" + ",".join(EXPECTED_REPEAT_CONTRACT_CASES),
                f"ARTIFACT_DIFF_CONTRACT_CASE_COUNT={len(EXPECTED_CONTRACT_CASES)}",
                "ARTIFACT_DIFF_CONTRACT_CASES=" + ",".join(EXPECTED_CONTRACT_CASES),
            ]),
        )
        covered_cases.append("contract_catalog_status_drift")
        expect_assertion(
            "contract_catalog_missing_cli_invalid_mode",
            lambda: assert_contract_lines([
                "ARTIFACT_DIFF_CONTRACT=pass",
                "ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=22",
                "ARTIFACT_DIFF_CONTRACT_BASE_CASES=" + ",".join([case for case in base_cases if case != "cli_invalid_mode"]),
                f"ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT={len(EXPECTED_REPEAT_CONTRACT_CASES)}",
                "ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=" + ",".join(EXPECTED_REPEAT_CONTRACT_CASES),
                "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=27",
                "ARTIFACT_DIFF_CONTRACT_CASES=" + ",".join([case for case in EXPECTED_CONTRACT_CASES if case != "cli_invalid_mode"]),
            ]),
        )
        covered_cases.append("contract_catalog_missing_cli_invalid_mode")
        expect_assertion(
            "contract_base_case_order_drift",
            lambda: assert_contract_lines([
                "ARTIFACT_DIFF_CONTRACT=pass",
                f"ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT={len(base_cases)}",
                "ARTIFACT_DIFF_CONTRACT_BASE_CASES=" + ",".join([base_cases[1], base_cases[0], *base_cases[2:]]),
                f"ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT={len(EXPECTED_REPEAT_CONTRACT_CASES)}",
                "ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=" + ",".join(EXPECTED_REPEAT_CONTRACT_CASES),
                f"ARTIFACT_DIFF_CONTRACT_CASE_COUNT={len(EXPECTED_CONTRACT_CASES)}",
                "ARTIFACT_DIFF_CONTRACT_CASES=" + ",".join(EXPECTED_CONTRACT_CASES),
            ]),
        )
        covered_cases.append("contract_base_case_order_drift")
        expect_assertion(
            "contract_repeat_case_order_drift",
            lambda: assert_contract_lines([
                "ARTIFACT_DIFF_CONTRACT=pass",
                f"ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT={len(base_cases)}",
                "ARTIFACT_DIFF_CONTRACT_BASE_CASES=" + ",".join(base_cases),
                f"ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT={len(EXPECTED_REPEAT_CONTRACT_CASES)}",
                "ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=" + ",".join([EXPECTED_REPEAT_CONTRACT_CASES[1], EXPECTED_REPEAT_CONTRACT_CASES[0], *EXPECTED_REPEAT_CONTRACT_CASES[2:]]),
                f"ARTIFACT_DIFF_CONTRACT_CASE_COUNT={len(EXPECTED_CONTRACT_CASES)}",
                "ARTIFACT_DIFF_CONTRACT_CASES=" + ",".join(EXPECTED_CONTRACT_CASES),
            ]),
        )
        covered_cases.append("contract_repeat_case_order_drift")
        expect_assertion(
            "contract_repeat_case_duplicate_drift",
            lambda: assert_contract_lines([
                "ARTIFACT_DIFF_CONTRACT=pass",
                f"ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT={len(base_cases)}",
                "ARTIFACT_DIFF_CONTRACT_BASE_CASES=" + ",".join(base_cases),
                f"ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT={len(EXPECTED_REPEAT_CONTRACT_CASES)}",
                "ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=" + ",".join(["helper_self_test_repeat", "helper_self_test_repeat", *EXPECTED_REPEAT_CONTRACT_CASES[2:]]),
                f"ARTIFACT_DIFF_CONTRACT_CASE_COUNT={len(EXPECTED_CONTRACT_CASES)}",
                "ARTIFACT_DIFF_CONTRACT_CASES=" + ",".join(EXPECTED_CONTRACT_CASES),
            ]),
        )
        covered_cases.append("contract_repeat_case_duplicate_drift")
        expect_assertion(
            "contract_catalog_case_order_drift",
            lambda: assert_contract_lines([
                "ARTIFACT_DIFF_CONTRACT=pass",
                f"ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT={len(base_cases)}",
                "ARTIFACT_DIFF_CONTRACT_BASE_CASES=" + ",".join(base_cases),
                f"ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT={len(EXPECTED_REPEAT_CONTRACT_CASES)}",
                "ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=" + ",".join(EXPECTED_REPEAT_CONTRACT_CASES),
                f"ARTIFACT_DIFF_CONTRACT_CASE_COUNT={len(EXPECTED_CONTRACT_CASES)}",
                "ARTIFACT_DIFF_CONTRACT_CASES=" + ",".join([EXPECTED_CONTRACT_CASES[1], EXPECTED_CONTRACT_CASES[0], *EXPECTED_CONTRACT_CASES[2:]]),
            ]),
        )
        covered_cases.append("contract_catalog_case_order_drift")
        expect_assertion(
            "contract_catalog_duplicate_case_drift",
            lambda: assert_contract_lines([
                "ARTIFACT_DIFF_CONTRACT=pass",
                f"ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT={len(base_cases)}",
                "ARTIFACT_DIFF_CONTRACT_BASE_CASES=" + ",".join(["helper_self_test", "helper_self_test", *base_cases[2:]]),
                f"ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT={len(EXPECTED_REPEAT_CONTRACT_CASES)}",
                "ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=" + ",".join(EXPECTED_REPEAT_CONTRACT_CASES),
                f"ARTIFACT_DIFF_CONTRACT_CASE_COUNT={len(EXPECTED_CONTRACT_CASES)}",
                "ARTIFACT_DIFF_CONTRACT_CASES=" + ",".join(["helper_self_test", "helper_self_test", *EXPECTED_CONTRACT_CASES[2:]]),
            ]),
        )
        covered_cases.append("contract_catalog_duplicate_case_drift")

    if covered_cases != EXPECTED_SELF_TEST_CASES:
        raise AssertionError(
            f"artifact-diff determinism self-test catalog drifted: expected {EXPECTED_SELF_TEST_CASES}, got {covered_cases}"
        )

    print("PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass")
    print(
        "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT="
        f"{len(EXPECTED_SELF_TEST_CASES)}"
    )
    print(
        "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASES="
        + ",".join(EXPECTED_SELF_TEST_CASES)
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check exact deterministic artifact-diff helper and contract summary catalogs."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker coverage.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    run_live_check(ROOT)
    print("PHASE4_ARTIFACT_DIFF_DETERMINISM=pass")
    print(f"PHASE4_ARTIFACT_DIFF_HELPER_CASE_COUNT={len(EXPECTED_HELPER_SELF_TEST_CASES)}")
    print(f"PHASE4_ARTIFACT_DIFF_CONTRACT_CASE_COUNT={len(EXPECTED_CONTRACT_CASES)}")
    print("PHASE4_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=" + ",".join(EXPECTED_REPEAT_CONTRACT_CASES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
