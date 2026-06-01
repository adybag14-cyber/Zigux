#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NOTE = Path("Documentation/zigux/phase4-artifact-diff-exact-replay.md")
HELPER = Path("scripts/zigux/artifact_diff.py")
CONTRACT = Path("scripts/zigux/check-artifact-diff-contract.py")
DETERMINISM = Path("scripts/zigux/check-phase4-artifact-diff-determinism.py")
VALIDATOR_REPLAYS = Path("scripts/zigux/check-phase4-artifact-diff-validator-replays.py")
VALIDATOR = Path("scripts/zigux/validate-phase4.py")

DIRECT_REPLAY_COMMANDS = (
    "python3 scripts/zigux/artifact_diff.py --self-test",
    "python3 scripts/zigux/check-artifact-diff-contract.py --self-test",
    "python3 scripts/zigux/check-artifact-diff-contract.py",
    "python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
    "python3 scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test",
    "python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
    "python3 scripts/zigux/check-phase4-artifact-diff-exact-replay.py --self-test",
    "python3 scripts/zigux/check-phase4-artifact-diff-exact-replay.py",
)

SELF_TEST_CASES = (
    "catalog_shape",
    "note_command_round_trip",
    "note_command_drift",
    "note_helper_catalog_drift",
    "note_contract_catalog_drift",
    "note_determinism_catalog_drift",
    "note_validator_catalog_drift",
    "note_exact_replay_catalog_drift",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the Phase 4 artifact-diff exact replay note keeps the exact "
            "replay commands and top-level output markers aligned with the current "
            "helper and checker packet."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def read(root: Path, rel: Path) -> str:
    try:
        return (root / rel).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing required file: {rel.as_posix()}") from exc


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def extract_literal_assignment(text: str, name: str, label: str):
    try:
        module = ast.parse(text)
    except SyntaxError as exc:
        raise RuntimeError(f"{label} is not valid Python: {exc}") from exc
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
    raise RuntimeError(f"{label} is missing `{name}`")


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise RuntimeError(f"{label} is missing required fragments: {missing}")


def expected_exact_replay_markers(root: Path) -> tuple[str, ...]:
    helper_text = read(root, HELPER)
    contract_text = read(root, CONTRACT)
    determinism_text = read(root, DETERMINISM)
    validator_replays_text = read(root, VALIDATOR_REPLAYS)

    helper_cases = tuple(extract_literal_assignment(helper_text, "SELF_TEST_CASES", HELPER.as_posix()))
    contract_self_test_cases = tuple(
        extract_literal_assignment(contract_text, "SELF_TEST_CASES", CONTRACT.as_posix())
    )
    contract_base_cases = tuple(
        extract_literal_assignment(contract_text, "BASE_CONTRACT_CASES", CONTRACT.as_posix())
    )
    contract_repeat_cases = tuple(
        extract_literal_assignment(contract_text, "REPEAT_CONTRACT_CASES", CONTRACT.as_posix())
    )
    determinism_cases = tuple(
        extract_literal_assignment(determinism_text, "EXPECTED_SELF_TEST_CASES", DETERMINISM.as_posix())
    )
    direct_packet = tuple(
        extract_literal_assignment(determinism_text, "CURRENT_DIRECT_PACKET", DETERMINISM.as_posix())
    )
    auth_missing = tuple(
        extract_literal_assignment(
            determinism_text, "AUTH_MISSING_BROADER_COMPANIONS", DETERMINISM.as_posix()
        )
    )
    validator_replay_cases = tuple(
        extract_literal_assignment(
            validator_replays_text, "EXPECTED_SELF_TEST_CASES", VALIDATOR_REPLAYS.as_posix()
        )
    )
    validator_markers = tuple(
        extract_literal_assignment(
            validator_replays_text,
            "EXPECTED_VALIDATOR_REPLAY_MARKERS",
            VALIDATOR_REPLAYS.as_posix(),
        )
    )
    workflow_markers = tuple(
        extract_literal_assignment(
            validator_replays_text,
            "EXPECTED_WORKFLOW_REPLAY_MARKERS",
            VALIDATOR_REPLAYS.as_posix(),
        )
    )

    return (
        *DIRECT_REPLAY_COMMANDS,
        "These are the exact top-level pass markers required by the current directly readable command packet in this run.",
        "ARTIFACT_DIFF_SELF_TEST=pass",
        f"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(helper_cases)}",
        "ARTIFACT_DIFF_SELF_TEST_CASES=" + ",".join(helper_cases),
        "ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass",
        f"ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT={len(contract_self_test_cases)}",
        "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES=" + ",".join(contract_self_test_cases),
        "ARTIFACT_DIFF_CONTRACT=pass",
        f"ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT={len(contract_base_cases)}",
        f"ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT={len(contract_repeat_cases)}",
        f"ARTIFACT_DIFF_CONTRACT_CASE_COUNT={len(contract_base_cases) + len(contract_repeat_cases)}",
        "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass",
        f"PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT={len(determinism_cases)}",
        "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASES=" + ",".join(determinism_cases),
        "PHASE4_ARTIFACT_DIFF_DETERMINISM=pass",
        f"PHASE4_ARTIFACT_DIFF_DETERMINISM_DIRECT_PACKET_MEMBERS={len(direct_packet)}",
        f"PHASE4_ARTIFACT_DIFF_DETERMINISM_AUTH_MISSING_BROADER_COMPANIONS={len(auth_missing)}",
        "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST=pass",
        f"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT={len(validator_replay_cases)}",
        "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASES=" + ",".join(validator_replay_cases),
        "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS=pass",
        "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MODE=validator_present",
        f"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT={len(validator_markers)}",
        f"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT={len(workflow_markers)}",
        "PHASE4_ARTIFACT_DIFF_EXACT_REPLAY_SELF_TEST=pass",
        f"PHASE4_ARTIFACT_DIFF_EXACT_REPLAY_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}",
        "PHASE4_ARTIFACT_DIFF_EXACT_REPLAY_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES),
        "PHASE4_ARTIFACT_DIFF_EXACT_REPLAY=pass",
        f"PHASE4_ARTIFACT_DIFF_EXACT_REPLAY_COMMAND_COUNT={len(DIRECT_REPLAY_COMMANDS)}",
    )


def check(root: Path) -> None:
    note = read(root, NOTE)
    read(root, VALIDATOR)
    require_markers(note, expected_exact_replay_markers(root), NOTE.as_posix())


def helper_fixture_text() -> str:
    return "\n".join(
        [
            "MODE_CHOICES = (\"text\", \"json\", \"bytes\")",
            "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}",
            "SELF_TEST_CASES = [",
            '    "text_pass",',
            '    "text_mismatch",',
            '    "json_pass",',
            '    "json_mismatch",',
            '    "json_invalid_expected",',
            '    "json_invalid_actual",',
            '    "json_invalid_both",',
            '    "json_missing_expected",',
            '    "json_missing_actual",',
            '    "json_missing_both",',
            '    "bytes_pass",',
            '    "bytes_drift",',
            '    "text_missing_expected",',
            '    "text_missing_actual",',
            '    "text_missing_both",',
            '    "bytes_missing_expected",',
            '    "bytes_missing_actual",',
            '    "bytes_missing_both",',
            '    "legacy_sha256_alias",',
            '    "missing_mode_value_rejected",',
            '    "missing_positional_arguments_rejected",',
            '    "invalid_mode_rejected",',
            '    "extra_positional_rejected",',
            "]",
            "",
        ]
    )


def contract_fixture_text() -> str:
    return "\n".join(
        [
            "HELPER_SELF_TEST_CASES = [",
            '    "text_pass",',
            '    "text_mismatch",',
            '    "json_pass",',
            '    "json_mismatch",',
            '    "json_invalid_expected",',
            '    "json_invalid_actual",',
            '    "json_invalid_both",',
            '    "json_missing_expected",',
            '    "json_missing_actual",',
            '    "json_missing_both",',
            '    "bytes_pass",',
            '    "bytes_drift",',
            '    "text_missing_expected",',
            '    "text_missing_actual",',
            '    "text_missing_both",',
            '    "bytes_missing_expected",',
            '    "bytes_missing_actual",',
            '    "bytes_missing_both",',
            '    "legacy_sha256_alias",',
            '    "missing_mode_value_rejected",',
            '    "missing_positional_arguments_rejected",',
            '    "invalid_mode_rejected",',
            '    "extra_positional_rejected",',
            "]",
            "BASE_CONTRACT_CASES = [",
            '    "helper_self_test",',
            '    "cli_help_output",',
            '    "cli_missing_required_args",',
            '    "cli_missing_mode_value",',
            '    "cli_missing_actual_operand",',
            '    "cli_invalid_mode",',
            '    "cli_extra_positional_args",',
            '    "text_pass",',
            '    "text_mismatch",',
            '    "text_missing_expected",',
            '    "text_missing_actual",',
            '    "text_missing_both",',
            '    "json_pass",',
            '    "json_mismatch",',
            '    "json_missing_expected",',
            '    "json_missing_actual",',
            '    "json_missing_both",',
            '    "json_invalid_expected",',
            '    "json_invalid_actual",',
            '    "json_invalid_both",',
            '    "bytes_pass",',
            '    "bytes_missing_expected",',
            '    "bytes_missing_actual",',
            '    "bytes_missing_both",',
            '    "bytes_drift",',
            "]",
            "REPEAT_CONTRACT_CASES = [",
            '    "helper_self_test_repeat",',
            '    "cli_help_output_repeat",',
            '    "text_pass_repeat",',
            '    "json_mismatch_repeat",',
            '    "bytes_drift_repeat",',
            "]",
            "SELF_TEST_CASES = [",
            '    "catalog_shape",',
            '    "review_note_marker_round_trip",',
            '    "review_note_owner_marker_drift",',
            '    "review_note_marker_drift",',
            '    "cli_help_round_trip",',
            '    "cli_help_line_drift",',
            '    "cli_missing_argument_parser_round_trip",',
            '    "cli_missing_argument_parser_stderr_drift",',
            '    "cli_invalid_mode_parser_round_trip",',
            '    "cli_invalid_mode_parser_stderr_drift",',
            '    "helper_summary_round_trip",',
            '    "contract_summary_round_trip",',
            '    "helper_summary_status_drift",',
            '    "helper_summary_count_drift",',
            '    "helper_summary_duplicate_case_drift",',
            '    "helper_summary_case_order_drift",',
            '    "contract_summary_status_drift",',
            '    "contract_summary_base_count_drift",',
            '    "contract_summary_base_case_order_drift",',
            '    "contract_summary_repeat_count_drift",',
            '    "contract_summary_repeat_case_order_drift",',
            '    "contract_summary_case_count_drift",',
            '    "contract_summary_duplicate_case_drift",',
            '    "contract_summary_case_order_drift",',
            "]",
            "",
        ]
    )


def determinism_fixture_text() -> str:
    return "\n".join(
        [
            "CURRENT_DIRECT_PACKET = (",
            '    "Documentation/zigux/phase4-artifact-diff-tooling-survey.md",',
            '    "Documentation/zigux/phase4-reversible-delivery-evidence.md",',
            '    "Documentation/zigux/review-checklist.md",',
            '    "Documentation/zigux/artifact-diff.md",',
            '    "scripts/zigux/check-phase4-repo-reality-warning.py",',
            '    "scripts/zigux/check-phase4-reversible-delivery-pins.py",',
            '    "scripts/zigux/check-phase4-artifact-diff-determinism.py",',
            '    "scripts/zigux/check-phase4-artifact-diff-validator-replays.py",',
            '    "scripts/zigux/validate-phase4.py",',
            '    "scripts/zigux/artifact_diff.py",',
            '    "scripts/zigux/check-artifact-diff-contract.py",',
            ")",
            "AUTH_MISSING_BROADER_COMPANIONS = ()",
            "EXPECTED_SELF_TEST_CASES = (",
            '    "round_trip",',
            '    "survey_marker_drift",',
            '    "survey_packet_drift",',
            '    "review_checklist_drift",',
            '    "note_marker_drift",',
            '    "broader_note_marker_drift",',
            '    "broader_note_stale_packet_drift",',
            '    "repo_warning_drift",',
            '    "helper_mode_drift",',
            '    "helper_catalog_drift",',
            '    "contract_catalog_drift",',
            '    "direct_packet_missing",',
            ")",
            "",
        ]
    )


def validator_replays_fixture_text() -> str:
    return "\n".join(
        [
            "EXPECTED_VALIDATOR_REPLAY_MARKERS = [",
            '    "helper",',
            '    "contract_self_test",',
            '    "contract",',
            '    "determinism_self_test",',
            '    "determinism",',
            '    "validator_replays_self_test",',
            '    "validator_replays",',
            "]",
            "EXPECTED_WORKFLOW_REPLAY_MARKERS = [",
            '    "make route",',
            '    "artifact_diff self-test",',
            '    "artifact_diff contract self-test",',
            '    "artifact_diff contract",',
            '    "determinism self-test",',
            '    "determinism",',
            '    "validator replay self-test",',
            '    "validator replay",',
            '    "phase4 make route",',
            '    "phase4 test route",',
            '    "phase4 validate route",',
            '    "repo warning",',
            '    "pins",',
            '    "perf baseline",',
            '    "gate evidence",',
            '    "remaining gap",',
            "]",
            "EXPECTED_SELF_TEST_CASES = [",
            '    "catalog_shape",',
            '    "validator_marker_round_trip",',
            '    "validator_helper_marker_drift",',
            '    "validator_marker_drift",',
            '    "validator_replay_marker_drift",',
            '    "repo_reality_handoff_round_trip",',
            '    "repo_reality_handoff_drift",',
            '    "repo_reality_handoff_note_missing",',
            '    "workflow_marker_round_trip",',
            '    "workflow_make_route_marker_drift",',
            '    "workflow_marker_drift",',
            '    "workflow_missing",',
            '    "artifact_diff_note_round_trip",',
            '    "artifact_diff_note_marker_drift",',
            "]",
            "",
        ]
    )


def note_fixture_text(root: Path) -> str:
    markers = expected_exact_replay_markers(root)
    return "\n".join(
        [
            "# Phase 4 Artifact-Diff Exact Replay",
            "",
            "This note records the current exact Phase 4 artifact-diff replay packet and the top-level pass markers that must stay aligned with the current helper and checker catalogs.",
            "",
            "## Commands",
            *[f"  * `{command}`" for command in DIRECT_REPLAY_COMMANDS],
            "",
            "## Top-Level Pass Markers",
            "These are the exact top-level pass markers required by the current directly readable command packet in this run.",
            *[f"  * `{marker}`" for marker in markers if marker not in DIRECT_REPLAY_COMMANDS and not marker.startswith("These are the exact top-level pass markers required")],
            "",
        ]
    )


def fixture_root(root: Path) -> None:
    write(root / HELPER, helper_fixture_text())
    write(root / CONTRACT, contract_fixture_text())
    write(root / DETERMINISM, determinism_fixture_text())
    write(root / VALIDATOR_REPLAYS, validator_replays_fixture_text())
    write(root / VALIDATOR, "# validator placeholder\n")
    write(root / NOTE, note_fixture_text(root))


def expect_failure(root: Path, label: str) -> str:
    try:
        check(root)
    except RuntimeError:
        return label
    raise AssertionError(f"expected {label} to fail closed")


def self_test() -> None:
    covered: list[str] = []
    with tempfile.TemporaryDirectory(prefix="phase4-artifact-diff-exact-replay-") as tmp:
        root = Path(tmp)

        fixture_root(root)
        check(root)
        covered.append("note_command_round_trip")

        fixture_root(root)
        write(
            root / NOTE,
            read(root, NOTE).replace(
                DIRECT_REPLAY_COMMANDS[-1],
                "python3 scripts/zigux/check-phase4-artifact-diff-stale-replay.py",
                1,
            ),
        )
        covered.append(expect_failure(root, "note_command_drift"))

        fixture_root(root)
        write(
            root / NOTE,
            read(root, NOTE).replace(
                "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23",
                "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=22",
                1,
            ),
        )
        covered.append(expect_failure(root, "note_helper_catalog_drift"))

        fixture_root(root)
        write(
            root / NOTE,
            read(root, NOTE).replace(
                "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=30",
                "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=29",
                1,
            ),
        )
        covered.append(expect_failure(root, "note_contract_catalog_drift"))

        fixture_root(root)
        write(
            root / NOTE,
            read(root, NOTE).replace(
                "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=12",
                "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=11",
                1,
            ),
        )
        covered.append(expect_failure(root, "note_determinism_catalog_drift"))

        fixture_root(root)
        write(
            root / NOTE,
            read(root, NOTE).replace(
                "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT=16",
                "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT=13",
                1,
            ),
        )
        covered.append(expect_failure(root, "note_validator_catalog_drift"))

        fixture_root(root)
        write(
            root / NOTE,
            read(root, NOTE).replace(
                f"PHASE4_ARTIFACT_DIFF_EXACT_REPLAY_COMMAND_COUNT={len(DIRECT_REPLAY_COMMANDS)}",
                f"PHASE4_ARTIFACT_DIFF_EXACT_REPLAY_COMMAND_COUNT={len(DIRECT_REPLAY_COMMANDS) - 1}",
                1,
            ),
        )
        covered.append(expect_failure(root, "note_exact_replay_catalog_drift"))

    catalog = ["catalog_shape", *covered]
    if tuple(catalog) != SELF_TEST_CASES:
        raise AssertionError(f"self-test catalog drifted: expected {SELF_TEST_CASES}, got {tuple(catalog)}")

    print("PHASE4_ARTIFACT_DIFF_EXACT_REPLAY_SELF_TEST=pass")
    print(f"PHASE4_ARTIFACT_DIFF_EXACT_REPLAY_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
    print("PHASE4_ARTIFACT_DIFF_EXACT_REPLAY_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES))


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    try:
        check(args.root.resolve())
    except RuntimeError as exc:
        print(f"PHASE4_ARTIFACT_DIFF_EXACT_REPLAY=fail: {exc}")
        return 1
    print("PHASE4_ARTIFACT_DIFF_EXACT_REPLAY=pass")
    print(f"PHASE4_ARTIFACT_DIFF_EXACT_REPLAY_COMMAND_COUNT={len(DIRECT_REPLAY_COMMANDS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
