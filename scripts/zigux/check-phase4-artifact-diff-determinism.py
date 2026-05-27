#!/usr/bin/env python3
"""Guard the current directly readable Phase 4 artifact-diff packet against drift."""

from __future__ import annotations

import argparse
import ast
import tempfile
from pathlib import Path

SURVEY = Path("Documentation/zigux/phase4-artifact-diff-tooling-survey.md")
PHASE4_NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
ARTIFACT_DIFF_NOTE = Path("Documentation/zigux/artifact-diff.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
REPO_WARNING = Path("scripts/zigux/check-phase4-repo-reality-warning.py")
PINS_CHECKER = Path("scripts/zigux/check-phase4-reversible-delivery-pins.py")
VALIDATOR_REPLAYS = Path("scripts/zigux/check-phase4-artifact-diff-validator-replays.py")
VALIDATOR = Path("scripts/zigux/validate-phase4.py")
DIRECT_HELPER = Path("scripts/zigux/artifact_diff.py")
CONTRACT_CHECKER = Path("scripts/zigux/check-artifact-diff-contract.py")
SELF_PATH = Path("scripts/zigux/check-phase4-artifact-diff-determinism.py")

CURRENT_DIRECT_PACKET = (
    "Documentation/zigux/phase4-artifact-diff-tooling-survey.md",
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/artifact-diff.md",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
    "scripts/zigux/validate-phase4.py",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-artifact-diff-contract.py",
)

AUTH_MISSING_BROADER_COMPANIONS = ()

EXPECTED_SELF_TEST_CASES = (
    "round_trip",
    "survey_marker_drift",
    "survey_packet_drift",
    "survey_exact_packet_drift",
    "review_checklist_drift",
    "note_marker_drift",
    "broader_note_marker_drift",
    "broader_note_stale_packet_drift",
    "repo_warning_drift",
    "helper_mode_drift",
    "helper_catalog_drift",
    "contract_catalog_drift",
    "direct_packet_missing",
)

SURVEY_MARKERS = (
    "PHASE4_ARTIFACT_DIFF_TOOLING_STATUS=helper_contract_validator_and_owner_note_direct_readback_aligned_on_current_master",
    "current direct-readback helper-contract-validator-and-owner-note packet:",
    "Current `master` now keeps the directly readable helper, contract checker, determinism checker, validator-replay checker, shared validator packet, and broader owner-and-rollback note aligned around the same bytes-capable artifact-diff contract.",
    "The broader `Documentation/zigux/artifact-diff.md` note is directly readable on current `master` again and now matches the current 23-case helper packet, the current 25-base-case / 30-case contract packet, and the current 13-case determinism self-test packet.",
    "`scripts/zigux/check-phase4-artifact-diff-determinism.py` now exact-requires the broader `Documentation/zigux/artifact-diff.md` note to keep the refreshed helper, contract, and determinism anchor lines whenever that file is present in the checked tree.",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_SELF_TEST_CASE_COUNT=23`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_SELF_TEST_CASE_COUNT=24`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_BASE_CASE_COUNT=25`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_REPEAT_CASE_COUNT=5`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_CASE_COUNT=30`",
    "No remaining owner-and-rollback note readback caveat is left inside this lane on current `master`, so the same lane should stay parked unless the broader note or exact packet drifts again.",
    "this survey now treats `Documentation/zigux/artifact-diff.md` as direct current-head evidence on current `master`",
)

SURVEY_EXACT_PACKET_MARKERS = (
    "`PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_SELF_TEST_CASE_COUNT=23`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_MODES=text,json,bytes`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_LEGACY_MODE_ALIASES=sha256->bytes`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_HELPER_SELF_TEST_CASE_COUNT=23`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_SELF_TEST_CASE_COUNT=24`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_BASE_CASE_COUNT=25`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_REPEAT_CASE_COUNT=5`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_CASE_COUNT=30`",
    "`ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23`",
    "`ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=24`",
    "`ARTIFACT_DIFF_CONTRACT_CASE_COUNT=30`",
    "`PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=13`",
    "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=14`",
    "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT=7`",
    "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT=14`",
)

NOTE_MARKERS = (
    "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.",
    "Direct authenticated contents reads in this runtime now return `scripts/zigux/validate-phase4.py` directly, while `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` still flap on that same route; public raw fallback rereads continue to return the full set on current `master`, matching the broader review packet's recovered note-and-checker companions.",
    "Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, and `scripts/zigux/check-phase4-artifact-diff-determinism.py`.",
    "Current direct contents reads for `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`, and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` now return on current `master`",
)

ARTIFACT_DIFF_NOTE_MARKERS = (
    "`scripts/zigux/artifact_diff.py` as the stable comparison entrypoint",
    "`scripts/zigux/check-artifact-diff-contract.py` reruns the bounded helper self-test, CLI help output, missing-required-args, missing-mode-value, missing-actual-operand, invalid-mode, and extra-positional parser coverage plus the text, JSON, bytes, missing-path, malformed-input, and repeat-run cases",
    "`scripts/zigux/check-phase4-artifact-diff-determinism.py` rechecks the helper and contract summary catalogs together so case-count, case-order, and repeat-case drift fail closed",
    "`ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23`",
    "`ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=25`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=5`, and `ARTIFACT_DIFF_CONTRACT_CASE_COUNT=30`",
    "`PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=13`",
    "`PHASE4_ARTIFACT_DIFF_DETERMINISM_DIRECT_PACKET_MEMBERS=11`",
    "`PHASE4_ARTIFACT_DIFF_DETERMINISM_AUTH_MISSING_BROADER_COMPANIONS=0`",
)

REVIEW_CHECKLIST_MARKERS = (
    "shared Phase 4 rollback-ownership and lab-matrix packet",
    "`scripts/zigux/check-phase4-repo-reality-warning.py` and `scripts/zigux/check-phase4-reversible-delivery-pins.py`",
    "keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, and `scripts/zigux/check-phase4-remaining-gap-matrix.py`",
    "keep the repo-reality warning explicit for the broader Phase 4 validator, build, and bitmap-diff companions still needing raw-fallback proof or fresh authenticated blob capture",
    "keep the roadmap-backed `atomic64_diff` pair explicit as direct current-head evidence",
)

REPO_WARNING_MARKERS = (
    "Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, and `scripts/zigux/check-phase4-artifact-diff-determinism.py`",
    "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.",
    "Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair explicit as direct current-head evidence",
)

HELPER_EXPECTED_MODE_CHOICES = ("text", "json", "bytes")
HELPER_EXPECTED_LEGACY_MODE_ALIASES = {"sha256": "bytes"}
HELPER_EXPECTED_SELF_TEST_CASES = (
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
    "bytes_pass",
    "bytes_drift",
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
    "bytes_missing_expected",
    "bytes_missing_actual",
    "bytes_missing_both",
    "legacy_sha256_alias",
    "missing_mode_value_rejected",
    "missing_positional_arguments_rejected",
    "invalid_mode_rejected",
    "extra_positional_rejected",
)

CONTRACT_HELPER_SELF_TEST_CASES = HELPER_EXPECTED_SELF_TEST_CASES

CONTRACT_BASE_CASES = (
    "helper_self_test",
    "cli_help_output",
    "cli_missing_required_args",
    "cli_missing_mode_value",
    "cli_missing_actual_operand",
    "cli_invalid_mode",
    "cli_extra_positional_args",
    "text_pass",
    "text_mismatch",
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
    "json_pass",
    "json_mismatch",
    "json_missing_expected",
    "json_missing_actual",
    "json_missing_both",
    "json_invalid_expected",
    "json_invalid_actual",
    "json_invalid_both",
    "bytes_pass",
    "bytes_missing_expected",
    "bytes_missing_actual",
    "bytes_missing_both",
    "bytes_drift",
)

CONTRACT_REPEAT_CASES = (
    "helper_self_test_repeat",
    "cli_help_output_repeat",
    "text_pass_repeat",
    "json_mismatch_repeat",
    "bytes_drift_repeat",
)

CONTRACT_SELF_TEST_CASES = (
    "catalog_shape",
    "review_note_marker_round_trip",
    "review_note_owner_marker_drift",
    "review_note_marker_drift",
    "cli_help_round_trip",
    "cli_help_line_drift",
    "cli_missing_argument_parser_round_trip",
    "cli_missing_argument_parser_stderr_drift",
    "cli_invalid_mode_parser_round_trip",
    "cli_invalid_mode_parser_stderr_drift",
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
)

VALIDATOR_REPLAYS_EXPECTED_SELF_TEST_CASES = (
    "catalog_shape",
    "validator_marker_round_trip",
    "validator_helper_marker_drift",
    "validator_marker_drift",
    "validator_replay_marker_drift",
    "repo_reality_handoff_round_trip",
    "repo_reality_handoff_drift",
    "repo_reality_handoff_note_missing",
    "workflow_marker_round_trip",
    "workflow_make_route_marker_drift",
    "workflow_marker_drift",
    "workflow_missing",
    "artifact_diff_note_round_trip",
    "artifact_diff_note_marker_drift",
)

VALIDATOR_MARKERS = (
    '"phase4-artifact-diff-determinism-self-test": (',
    '"PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass",',
    '"PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=13",',
    '"PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASES="',
    '"phase4-artifact-diff-determinism": (',
    '"PHASE4_ARTIFACT_DIFF_DETERMINISM=pass",',
    '"PHASE4_ARTIFACT_DIFF_DETERMINISM_DIRECT_PACKET_MEMBERS=11",',
    '"PHASE4_ARTIFACT_DIFF_DETERMINISM_AUTH_MISSING_BROADER_COMPANIONS=0",',
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
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


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise RuntimeError(f"{label} is missing required fragments: {missing}")


def require_paths_listed(text: str, paths: tuple[str, ...], label: str) -> None:
    missing = [path for path in paths if f"`{path}`" not in text]
    if missing:
        raise RuntimeError(f"{label} is missing required path markers: {missing}")


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


def require_current_helper_contract(text: str) -> None:
    mode_choices = tuple(extract_literal_assignment(text, "MODE_CHOICES", DIRECT_HELPER.as_posix()))
    if mode_choices != HELPER_EXPECTED_MODE_CHOICES:
        raise RuntimeError(
            f"{DIRECT_HELPER.as_posix()} must keep MODE_CHOICES={HELPER_EXPECTED_MODE_CHOICES}, saw {mode_choices}"
        )
    legacy_aliases = extract_literal_assignment(text, "LEGACY_MODE_ALIASES", DIRECT_HELPER.as_posix())
    if legacy_aliases != HELPER_EXPECTED_LEGACY_MODE_ALIASES:
        raise RuntimeError(
            f"{DIRECT_HELPER.as_posix()} must keep LEGACY_MODE_ALIASES={HELPER_EXPECTED_LEGACY_MODE_ALIASES}, saw {legacy_aliases}"
        )
    self_test_cases = tuple(extract_literal_assignment(text, "SELF_TEST_CASES", DIRECT_HELPER.as_posix()))
    if self_test_cases != HELPER_EXPECTED_SELF_TEST_CASES:
        raise RuntimeError(f"{DIRECT_HELPER.as_posix()} must keep the current 23-case self-test catalog")


def require_current_contract_checker(text: str) -> None:
    helper_cases = tuple(extract_literal_assignment(text, "HELPER_SELF_TEST_CASES", CONTRACT_CHECKER.as_posix()))
    if helper_cases != CONTRACT_HELPER_SELF_TEST_CASES:
        raise RuntimeError(f"{CONTRACT_CHECKER.as_posix()} must keep the current 23-case helper replay catalog")
    base_cases = tuple(extract_literal_assignment(text, "BASE_CONTRACT_CASES", CONTRACT_CHECKER.as_posix()))
    if base_cases != CONTRACT_BASE_CASES:
        raise RuntimeError(f"{CONTRACT_CHECKER.as_posix()} must keep the current 25-case base contract catalog")
    repeat_cases = tuple(extract_literal_assignment(text, "REPEAT_CONTRACT_CASES", CONTRACT_CHECKER.as_posix()))
    if repeat_cases != CONTRACT_REPEAT_CASES:
        raise RuntimeError(f"{CONTRACT_CHECKER.as_posix()} must keep the current 5-case repeat contract catalog")
    self_test_cases = tuple(extract_literal_assignment(text, "SELF_TEST_CASES", CONTRACT_CHECKER.as_posix()))
    if self_test_cases != CONTRACT_SELF_TEST_CASES:
        raise RuntimeError(f"{CONTRACT_CHECKER.as_posix()} must keep the current 24-case self-test catalog")


def require_current_validator_replays_checker(text: str) -> None:
    self_test_cases = tuple(
        extract_literal_assignment(text, "EXPECTED_SELF_TEST_CASES", VALIDATOR_REPLAYS.as_posix())
    )
    if self_test_cases != VALIDATOR_REPLAYS_EXPECTED_SELF_TEST_CASES:
        raise RuntimeError(
            f"{VALIDATOR_REPLAYS.as_posix()} must keep the current 14-case self-test catalog"
        )


def require_current_validator(text: str) -> None:
    require_markers(text, VALIDATOR_MARKERS, VALIDATOR.as_posix())


def require_current_repo_reality(root: Path) -> None:
    missing = [path for path in CURRENT_DIRECT_PACKET if not (root / Path(path)).exists()]
    if missing:
        raise RuntimeError(f"current direct-readback packet is missing required members: {missing}")


def check(root: Path) -> None:
    survey = read(root, SURVEY)
    note = read(root, PHASE4_NOTE)
    review_checklist = read(root, REVIEW_CHECKLIST)
    repo_warning = read(root, REPO_WARNING)
    helper_text = read(root, DIRECT_HELPER)
    contract_text = read(root, CONTRACT_CHECKER)
    validator_replays_text = read(root, VALIDATOR_REPLAYS)
    validator_text = read(root, VALIDATOR)

    require_markers(survey, SURVEY_MARKERS, SURVEY.as_posix())
    require_markers(survey, SURVEY_EXACT_PACKET_MARKERS, SURVEY.as_posix())
    require_paths_listed(survey, CURRENT_DIRECT_PACKET, SURVEY.as_posix())
    require_paths_listed(survey, AUTH_MISSING_BROADER_COMPANIONS, SURVEY.as_posix())
    require_markers(note, NOTE_MARKERS, PHASE4_NOTE.as_posix())
    if (root / ARTIFACT_DIFF_NOTE).exists():
        require_markers(read(root, ARTIFACT_DIFF_NOTE), ARTIFACT_DIFF_NOTE_MARKERS, ARTIFACT_DIFF_NOTE.as_posix())
    require_markers(review_checklist, REVIEW_CHECKLIST_MARKERS, REVIEW_CHECKLIST.as_posix())
    require_markers(repo_warning, REPO_WARNING_MARKERS, REPO_WARNING.as_posix())
    require_current_helper_contract(helper_text)
    require_current_contract_checker(contract_text)
    require_current_validator_replays_checker(validator_replays_text)
    require_current_validator(validator_text)
    require_current_repo_reality(root)


def bullet_paths(paths: tuple[str, ...]) -> str:
    return "\n".join(f"- `{path}`" for path in paths)


def helper_fixture_text() -> str:
    cases = "\n".join(f'    "{case}",' for case in HELPER_EXPECTED_SELF_TEST_CASES)
    return "\n".join(
        [
            'MODE_CHOICES = ("text", "json", "bytes")',
            'LEGACY_MODE_ALIASES = {"sha256": "bytes"}',
            "SELF_TEST_CASES = [",
            cases,
            "]",
            "",
        ]
    ) + "\n"


def contract_fixture_text() -> str:
    def block(name: str, values: tuple[str, ...]) -> list[str]:
        return [
            f"{name} = [",
            *[f'    "{value}",' for value in values],
            "]",
            "",
        ]

    lines: list[str] = []
    lines.extend(block("HELPER_SELF_TEST_CASES", CONTRACT_HELPER_SELF_TEST_CASES))
    lines.extend(block("BASE_CONTRACT_CASES", CONTRACT_BASE_CASES))
    lines.extend(block("REPEAT_CONTRACT_CASES", CONTRACT_REPEAT_CASES))
    lines.extend(block("SELF_TEST_CASES", CONTRACT_SELF_TEST_CASES))
    return "\n".join(lines)


def validator_replays_fixture_text() -> str:
    cases = "\n".join(
        f'    "{case}",' for case in VALIDATOR_REPLAYS_EXPECTED_SELF_TEST_CASES
    )
    return "\n".join(
        [
            "EXPECTED_SELF_TEST_CASES = (",
            cases,
            ")",
            "",
        ]
    ) + "\n"


def validator_fixture_text() -> str:
    return "\n".join(VALIDATOR_MARKERS) + "\n"


def artifact_note_fixture_text() -> str:
    return "\n".join(ARTIFACT_DIFF_NOTE_MARKERS) + "\n"


def fixture_root(root: Path) -> None:
    write(
        root / SURVEY,
        "\n".join(
            [
                *SURVEY_MARKERS,
                *SURVEY_EXACT_PACKET_MARKERS,
                bullet_paths(CURRENT_DIRECT_PACKET),
                bullet_paths(AUTH_MISSING_BROADER_COMPANIONS),
            ]
        )
        + "\n",
    )
    write(root / PHASE4_NOTE, "\n".join(NOTE_MARKERS) + "\n")
    write(root / ARTIFACT_DIFF_NOTE, artifact_note_fixture_text())
    write(root / REVIEW_CHECKLIST, "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write(root / REPO_WARNING, "\n".join(REPO_WARNING_MARKERS) + "\n")
    write(root / PINS_CHECKER, "# pins checker placeholder\n")
    write(root / VALIDATOR_REPLAYS, validator_replays_fixture_text())
    write(root / VALIDATOR, validator_fixture_text())
    write(root / DIRECT_HELPER, helper_fixture_text())
    write(root / CONTRACT_CHECKER, contract_fixture_text())
    write(root / SELF_PATH, "# current checker\n")


def expect_failure(root: Path, label: str) -> str:
    try:
        check(root)
    except RuntimeError:
        return label
    raise AssertionError(f"expected {label} to fail")


def self_test() -> None:
    covered: list[str] = []
    with tempfile.TemporaryDirectory(prefix="phase4-artifact-diff-history-") as tmp:
        root = Path(tmp)

        fixture_root(root)
        check(root)
        covered.append("round_trip")

        fixture_root(root)
        write(
            root / SURVEY,
            read(root, SURVEY).replace(
                "current direct-readback helper-contract-validator-and-owner-note packet",
                "current helper-contract-validator-and-owner-note packet",
                1,
            ),
        )
        covered.append(expect_failure(root, "survey_marker_drift"))

        fixture_root(root)
        write(
            root / SURVEY,
            read(root, SURVEY).replace(
                "`scripts/zigux/check-artifact-diff-contract.py`",
                "`scripts/zigux/not-the-right-checker.py`",
                1,
            ),
        )
        covered.append(expect_failure(root, "survey_packet_drift"))

        fixture_root(root)
        write(
            root / SURVEY,
            read(root, SURVEY).replace(
                "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=14`",
                "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=13`",
                1,
            ),
        )
        covered.append(expect_failure(root, "survey_exact_packet_drift"))

        fixture_root(root)
        write(
            root / REVIEW_CHECKLIST,
            read(root, REVIEW_CHECKLIST).replace(
                "roadmap-backed `atomic64_diff` pair",
                "older atomic64 pair",
                1,
            ),
        )
        covered.append(expect_failure(root, "review_checklist_drift"))

        fixture_root(root)
        write(
            root / PHASE4_NOTE,
            read(root, PHASE4_NOTE).replace(
                "scripts/zigux/check-artifact-diff-contract.py",
                "scripts/zigux/not-the-right-checker.py",
                1,
            ),
        )
        covered.append(expect_failure(root, "note_marker_drift"))

        fixture_root(root)
        write(
            root / ARTIFACT_DIFF_NOTE,
            read(root, ARTIFACT_DIFF_NOTE).replace(
                "rechecks the helper and contract summary catalogs together so case-count, case-order, and repeat-case drift fail closed",
                "rechecks helper drift in a stale way",
                1,
            ),
        )
        covered.append(expect_failure(root, "broader_note_marker_drift"))

        fixture_root(root)
        write(
            root / ARTIFACT_DIFF_NOTE,
            read(root, ARTIFACT_DIFF_NOTE).replace(
                "`ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23`",
                "`ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=19`",
                1,
            ),
        )
        covered.append(expect_failure(root, "broader_note_stale_packet_drift"))

        fixture_root(root)
        write(
            root / REPO_WARNING,
            read(root, REPO_WARNING).replace(
                "scripts/zigux/check-artifact-diff-contract.py",
                "scripts/zigux/not-the-right-checker.py",
                1,
            ),
        )
        covered.append(expect_failure(root, "repo_warning_drift"))

        fixture_root(root)
        write(
            root / DIRECT_HELPER,
            read(root, DIRECT_HELPER).replace(
                'MODE_CHOICES = ("text", "json", "bytes")',
                'MODE_CHOICES = ("text", "json")',
                1,
            ),
        )
        covered.append(expect_failure(root, "helper_mode_drift"))

        fixture_root(root)
        write(root / DIRECT_HELPER, read(root, DIRECT_HELPER).replace('    "extra_positional_rejected",\n', "", 1))
        covered.append(expect_failure(root, "helper_catalog_drift"))

        fixture_root(root)
        write(root / CONTRACT_CHECKER, read(root, CONTRACT_CHECKER).replace('    "cli_missing_mode_value",\n', "", 1))
        covered.append(expect_failure(root, "contract_catalog_drift"))

        fixture_root(root)
        (root / VALIDATOR).unlink()
        covered.append(expect_failure(root, "direct_packet_missing"))

    if tuple(covered) != EXPECTED_SELF_TEST_CASES:
        raise AssertionError(f"expected self-test catalog {EXPECTED_SELF_TEST_CASES}, saw {tuple(covered)}")

    print("PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass")
    print(f"PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT={len(EXPECTED_SELF_TEST_CASES)}")
    print("PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASES=" + ",".join(EXPECTED_SELF_TEST_CASES))


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    try:
        check(args.root.resolve())
    except RuntimeError as exc:
        print(f"PHASE4_ARTIFACT_DIFF_DETERMINISM=fail: {exc}")
        return 1
    print("PHASE4_ARTIFACT_DIFF_DETERMINISM=pass")
    print(f"PHASE4_ARTIFACT_DIFF_DETERMINISM_DIRECT_PACKET_MEMBERS={len(CURRENT_DIRECT_PACKET)}")
    print(
        "PHASE4_ARTIFACT_DIFF_DETERMINISM_AUTH_MISSING_BROADER_COMPANIONS="
        f"{len(AUTH_MISSING_BROADER_COMPANIONS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
