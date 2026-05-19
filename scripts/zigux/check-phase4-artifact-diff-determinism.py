#!/usr/bin/env python3
"""Guard the current directly readable Phase 4 artifact-diff packet against drift."""

from __future__ import annotations

import argparse
import ast
import sys
import tempfile
from pathlib import Path

SURVEY = Path("Documentation/zigux/phase4-artifact-diff-tooling-survey.md")
PHASE4_NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
REPO_WARNING = Path("scripts/zigux/check-phase4-repo-reality-warning.py")
PINS_CHECKER = Path("scripts/zigux/check-phase4-reversible-delivery-pins.py")
VALIDATOR_REPLAYS = Path("scripts/zigux/check-phase4-artifact-diff-validator-replays.py")
DIRECT_HELPER = Path("scripts/zigux/artifact_diff.py")
CONTRACT_CHECKER = Path("scripts/zigux/check-artifact-diff-contract.py")
SELF_PATH = Path("scripts/zigux/check-phase4-artifact-diff-determinism.py")

CURRENT_DIRECT_PACKET = (
    "Documentation/zigux/phase4-artifact-diff-tooling-survey.md",
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-artifact-diff-contract.py",
)

MISSING_BROADER_COMPANIONS = (
    "Documentation/zigux/artifact-diff.md",
    "scripts/zigux/validate-phase4.py",
)

EXPECTED_SELF_TEST_CASES = (
    "round_trip",
    "survey_marker_drift",
    "survey_packet_drift",
    "review_checklist_drift",
    "note_marker_drift",
    "helper_mode_drift",
    "helper_alias_drift",
    "helper_catalog_drift",
    "contract_checker_missing",
    "broader_companion_return",
    "repo_warning_drift",
)

SURVEY_MARKERS = (
    "PHASE4_ARTIFACT_DIFF_TOOLING_STATUS=helper_and_contract_checker_direct_readback_restored_but_broader_note_and_validator_packet_still_partial_on_current_master",
    "current direct-readback helper-and-contract packet:",
    "authenticated contents reads on current `master` still return missing for these broader artifact-diff companions:",
    "`scripts/zigux/check-artifact-diff-contract.py` is also directly readable again on current `master`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_SELF_TEST_CASE_COUNT=20`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_BASE_CASE_COUNT=25`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_REPEAT_CASE_COUNT=5`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_CASE_COUNT=30`",
)

NOTE_MARKERS = (
    "The broader Phase 4 validator, build, and bitmap replay companions are still repo-reality gaps in this run",
    "Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, and `scripts/zigux/check-phase4-artifact-diff-determinism.py`",
    "Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` now return on current `master`",
)

REVIEW_CHECKLIST_MARKERS = (
    "shared Phase 4 rollback-ownership and lab-matrix packet",
    "`scripts/zigux/check-phase4-repo-reality-warning.py`",
    "`scripts/zigux/check-phase4-reversible-delivery-pins.py`",
    "keep the repo-reality warning explicit for the missing broader Phase 4 validator, lab-matrix, and bitmap-diff companions",
    "keep the roadmap-backed `atomic64_diff` pair explicit as direct current-head evidence",
)

REPO_WARNING_MARKERS = (
    "Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, and `scripts/zigux/check-phase4-artifact-diff-determinism.py`",
    "\"scripts/zigux/validate-phase4.py\"",
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
    "invalid_mode_rejected",
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


def extract_literal_assignment(text: str, name: str):
    try:
        module = ast.parse(text)
    except SyntaxError as exc:
        raise RuntimeError(f"{DIRECT_HELPER.as_posix()} is not valid Python: {exc}") from exc
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
    raise RuntimeError(f"{DIRECT_HELPER.as_posix()} is missing `{name}`")


def require_current_helper_contract(text: str) -> None:
    mode_choices = tuple(extract_literal_assignment(text, "MODE_CHOICES"))
    if mode_choices != HELPER_EXPECTED_MODE_CHOICES:
        raise RuntimeError(
            f"{DIRECT_HELPER.as_posix()} must keep MODE_CHOICES={HELPER_EXPECTED_MODE_CHOICES}, saw {mode_choices}"
        )

    legacy_aliases = extract_literal_assignment(text, "LEGACY_MODE_ALIASES")
    if legacy_aliases != HELPER_EXPECTED_LEGACY_MODE_ALIASES:
        raise RuntimeError(
            f"{DIRECT_HELPER.as_posix()} must keep LEGACY_MODE_ALIASES={HELPER_EXPECTED_LEGACY_MODE_ALIASES}, saw {legacy_aliases}"
        )

    self_test_cases = tuple(extract_literal_assignment(text, "SELF_TEST_CASES"))
    if self_test_cases != HELPER_EXPECTED_SELF_TEST_CASES:
        raise RuntimeError(
            f"{DIRECT_HELPER.as_posix()} must keep the current 20-case self-test catalog"
        )


def require_current_repo_reality(root: Path) -> None:
    missing_direct = [
        path for path in CURRENT_DIRECT_PACKET if not (root / Path(path)).exists()
    ]
    if missing_direct:
        raise RuntimeError(
            "current direct-readback packet is missing required members: "
            f"{missing_direct}"
        )

    present_broader = [
        path for path in MISSING_BROADER_COMPANIONS if (root / Path(path)).exists()
    ]
    if present_broader:
        raise RuntimeError(
            "broader artifact-diff companions returned and this checker must be narrowed: "
            f"{present_broader}"
        )


def check(root: Path) -> None:
    survey = read(root, SURVEY)
    note = read(root, PHASE4_NOTE)
    review_checklist = read(root, REVIEW_CHECKLIST)
    repo_warning = read(root, REPO_WARNING)
    helper_text = read(root, DIRECT_HELPER)

    require_markers(survey, SURVEY_MARKERS, SURVEY.as_posix())
    require_paths_listed(survey, CURRENT_DIRECT_PACKET, SURVEY.as_posix())
    require_paths_listed(survey, MISSING_BROADER_COMPANIONS, SURVEY.as_posix())
    require_markers(note, NOTE_MARKERS, PHASE4_NOTE.as_posix())
    require_markers(review_checklist, REVIEW_CHECKLIST_MARKERS, REVIEW_CHECKLIST.as_posix())
    require_markers(repo_warning, REPO_WARNING_MARKERS, REPO_WARNING.as_posix())
    require_current_helper_contract(helper_text)
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


def fixture_root(root: Path) -> None:
    write(
        root / SURVEY,
        "\n".join(
            [
                *SURVEY_MARKERS,
                bullet_paths(CURRENT_DIRECT_PACKET),
                bullet_paths(MISSING_BROADER_COMPANIONS),
            ]
        )
        + "\n",
    )
    write(root / PHASE4_NOTE, "\n".join(NOTE_MARKERS) + "\n")
    write(root / REVIEW_CHECKLIST, "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write(root / REPO_WARNING, "\n".join(REPO_WARNING_MARKERS) + "\n")
    write(root / PINS_CHECKER, "# pins checker placeholder\n")
    write(root / VALIDATOR_REPLAYS, "# validator replay placeholder\n")
    write(root / CONTRACT_CHECKER, "# contract checker placeholder\n")
    write(root / DIRECT_HELPER, helper_fixture_text())
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
        write(root / SURVEY, read(root, SURVEY).replace("helper-and-contract packet", "helper packet", 1))
        covered.append(expect_failure(root, "survey_marker_drift"))

        fixture_root(root)
        write(root / SURVEY, read(root, SURVEY).replace("`scripts/zigux/check-artifact-diff-contract.py`", "`scripts/zigux/not-the-right-checker.py`", 1))
        covered.append(expect_failure(root, "survey_packet_drift"))

        fixture_root(root)
        write(root / REVIEW_CHECKLIST, read(root, REVIEW_CHECKLIST).replace("roadmap-backed `atomic64_diff` pair", "older atomic64 pair", 1))
        covered.append(expect_failure(root, "review_checklist_drift"))

        fixture_root(root)
        write(root / PHASE4_NOTE, read(root, PHASE4_NOTE).replace("scripts/zigux/check-artifact-diff-contract.py", "scripts/zigux/not-the-right-checker.py", 1))
        covered.append(expect_failure(root, "note_marker_drift"))

        fixture_root(root)
        write(root / DIRECT_HELPER, read(root, DIRECT_HELPER).replace('MODE_CHOICES = ("text", "json", "bytes")', 'MODE_CHOICES = ("text", "json")', 1))
        covered.append(expect_failure(root, "helper_mode_drift"))

        fixture_root(root)
        write(root / DIRECT_HELPER, read(root, DIRECT_HELPER).replace('LEGACY_MODE_ALIASES = {"sha256": "bytes"}', 'LEGACY_MODE_ALIASES = {"sha256": "text"}', 1))
        covered.append(expect_failure(root, "helper_alias_drift"))

        fixture_root(root)
        write(root / DIRECT_HELPER, read(root, DIRECT_HELPER).replace('    "invalid_mode_rejected",\n', "", 1))
        covered.append(expect_failure(root, "helper_catalog_drift"))

        fixture_root(root)
        (root / CONTRACT_CHECKER).unlink()
        covered.append(expect_failure(root, "contract_checker_missing"))

        fixture_root(root)
        write(root / Path("Documentation/zigux/artifact-diff.md"), "# returned broader note\n")
        covered.append(expect_failure(root, "broader_companion_return"))

        fixture_root(root)
        write(root / REPO_WARNING, read(root, REPO_WARNING).replace("\"scripts/zigux/validate-phase4.py\"", "\"scripts/zigux/not-the-right-file.py\"", 1))
        covered.append(expect_failure(root, "repo_warning_drift"))

    if tuple(covered) != EXPECTED_SELF_TEST_CASES:
        raise AssertionError(
            f"expected self-test catalog {EXPECTED_SELF_TEST_CASES}, saw {tuple(covered)}"
        )

    print("PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass")
    print(
        "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT="
        f"{len(EXPECTED_SELF_TEST_CASES)}"
    )


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    try:
        check(args.root.resolve())
    except RuntimeError as exc:
        print(f"PHASE4_ARTIFACT_DIFF_DETERMINISM=fail: {exc}", file=sys.stderr)
        return 1
    print("PHASE4_ARTIFACT_DIFF_DETERMINISM=pass")
    print(
        "PHASE4_ARTIFACT_DIFF_DETERMINISM_DIRECT_PACKET_MEMBERS="
        f"{len(CURRENT_DIRECT_PACKET)}"
    )
    print(
        "PHASE4_ARTIFACT_DIFF_DETERMINISM_MISSING_BROADER_COMPANIONS="
        f"{len(MISSING_BROADER_COMPANIONS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())