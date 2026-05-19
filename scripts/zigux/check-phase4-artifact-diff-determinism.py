#!/usr/bin/env python3
"""Guard the current Phase 4 artifact-diff determinism handoff against repo reality."""

from __future__ import annotations

import argparse
import ast
import sys
import tempfile
from pathlib import Path

PHASE4_NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
SURVEY = Path("Documentation/zigux/phase4-artifact-diff-tooling-survey.md")
DOCS_ROOT = Path("Documentation/zigux/README.md")
SCRIPTS_ROOT = Path("scripts/zigux/README.md")
REPO_WARNING = Path("scripts/zigux/check-phase4-repo-reality-warning.py")
DIRECT_HELPER = Path("scripts/zigux/artifact_diff.py")
SELF_PATH = Path("scripts/zigux/check-phase4-artifact-diff-determinism.py")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
TESTS_README = Path("zigux/tests/README.md")
PINS_CHECKER = Path("scripts/zigux/check-phase4-reversible-delivery-pins.py")
VALIDATOR_REPLAYS = Path("scripts/zigux/check-phase4-artifact-diff-validator-replays.py")

EXPECTED_SELF_TEST_CASES = (
    "round_trip",
    "helper_mode_drift",
    "helper_alias_drift",
    "helper_self_test_catalog_drift",
    "helper_marker_drift",
    "survey_helper_drift",
    "historical_packet_drift",
    "docs_root_drift",
    "scripts_root_drift",
    "review_checklist_drift",
    "tests_readme_drift",
    "pins_checker_drift",
    "validator_replays_drift",
    "missing_direct_helper",
    "broader_companion_return",
    "repo_warning_drift",
)

HISTORICAL_ARTIFACT_DIFF_PACKET = (
    "Documentation/zigux/artifact-diff.md",
    "Documentation/zigux/phase4-gate-evidence.md",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "scripts/zigux/validate-phase4.py",
)

SURVEY_DIRECT_PACKET = (
    "Documentation/zigux/phase4-artifact-diff-tooling-survey.md",
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
    "scripts/zigux/artifact_diff.py",
)

CURRENT_DIRECT_PACKET = (
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
)

SURVEY_MARKERS = (
    "PHASE4_ARTIFACT_DIFF_TOOLING_STATUS=helper_direct_readback_restored_but_broader_contract_packet_still_partial_on_current_master",
    "current direct-readback helper packet:",
    "authenticated contents reads on current `master` still return missing for these broader artifact-diff companions:",
    "The helper itself is directly readable again on current `master` through `scripts/zigux/artifact_diff.py`",
)

NOTE_MARKERS = (
    "The broader Phase 4 validator, lab-matrix, and local-only perf companions are still repo-reality gaps in this run",
    "Historical broader validator and owner-map packet members:",
    "host-side artifact-diff tooling contract",
    "historical provenance, not current-head proof",
)

DOCS_ROOT_MARKERS = (
    "Phase 4 notes - `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, and `scripts/zigux/check-phase4-reversible-delivery-pins.py` now keep the current direct-readback rollback packet reviewable from the docs root while the broader validator, lab-matrix, local-only perf, and bitmap-diff companions remain repo-reality gaps on current `master`.",
    "scripts/zigux/validate-phase4.py",
    "host-side artifact-diff tooling contract",
)

SCRIPTS_ROOT_MARKERS = (
    "Phase 4 flow - the current shared rollback reminder packet is kept reviewable through the directly readable docs-root, tests-root, scripts-root, and dedicated local-only perf surfaces while the broader validator, lab-matrix, and bitmap-diff companions remain authenticated-readback repo-reality gaps on current `master`, so this note should stay aligned with that narrower direct-readback packet instead of treating public fallback visibility as the same thing as direct current-head proof",
    "host-side artifact-diff contract",
    "scripts/zigux/validate-phase4.py",
)

REPO_WARNING_MARKERS = (
    '"scripts/zigux/validate-phase4.py"',
    "MISSING_BROADER_PACKET",
    "broader packet entries are now present and the repo-reality warning must be narrowed",
)

REVIEW_CHECKLIST_MARKERS = (
    "Phase 4 exact-readback packet remains the current shared rollback reminder",
    "The dedicated local-only perf packet remains outside the shared validator-first route",
    "broader validator, lab-matrix, and bitmap-diff companions still remain repo-reality gaps",
)

TESTS_README_MARKERS = (
    "current shared Phase 4 ownership reminder",
    "artifact-diff contract references",
    "remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md`",
)

PINS_CHECKER_MARKERS = (
    "PHASE4_REVERSIBLE_DELIVERY_STATUS=shared_evidence_packet_requires_partial_repo_reality_recheck",
    "PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=16",
    "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=14",
)

VALIDATOR_REPLAY_MARKERS = (
    "Historical broader validator packet members that still stay explicit here:",
    "scripts/zigux/validate-phase4.py",
    "scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
)

MISSING_BROADER_ARTIFACT_DIFF_COMPANIONS = (
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/validate-phase4.py",
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

HELPER_REQUIRED_SOURCE_MARKERS = (
    'print("ARTIFACT_DIFF_SELF_TEST=pass")',
    'print(f"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")',
    "EXPECTED_JSON_ERROR=",
    "ACTUAL_JSON_ERROR=",
    'assert_case("MODE=bytes" in legacy_alias.stdout, "legacy_sha256_alias")',
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
        raise RuntimeError(f"missing required file: {rel.as_posix()}" ) from exc


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

    require_markers(text, HELPER_REQUIRED_SOURCE_MARKERS, DIRECT_HELPER.as_posix())


def require_current_repo_reality(root: Path) -> None:
    required_present = (SELF_PATH, SURVEY, DIRECT_HELPER)
    missing_present = [path.as_posix() for path in required_present if not (root / path).exists()]
    if missing_present:
        raise RuntimeError(
            "current tree is missing required direct-readback artifact-diff members: "
            f"{missing_present}"
        )

    present = [
        path
        for path in MISSING_BROADER_ARTIFACT_DIFF_COMPANIONS
        if (root / Path(path)).exists()
    ]
    if present:
        raise RuntimeError(
            "broader artifact-diff companions returned on current master and this handoff must be narrowed: "
            f"{present}"
        )


def check(root: Path) -> None:
    survey = read(root, SURVEY)
    note = read(root, PHASE4_NOTE)
    docs_root = read(root, DOCS_ROOT)
    scripts_root = read(root, SCRIPTS_ROOT)
    repo_warning = read(root, REPO_WARNING)
    review_checklist = read(root, REVIEW_CHECKLIST)
    tests_readme = read(root, TESTS_README)
    pins_checker = read(root, PINS_CHECKER)
    validator_replays = read(root, VALIDATOR_REPLAYS)
    helper_text = read(root, DIRECT_HELPER)

    require_markers(survey, SURVEY_MARKERS, SURVEY.as_posix())
    require_paths_listed(survey, SURVEY_DIRECT_PACKET, SURVEY.as_posix())
    require_paths_listed(survey, MISSING_BROADER_ARTIFACT_DIFF_COMPANIONS, SURVEY.as_posix())
    require_markers(note, NOTE_MARKERS, PHASE4_NOTE.as_posix())
    require_paths_listed(note, HISTORICAL_ARTIFACT_DIFF_PACKET, PHASE4_NOTE.as_posix())
    require_paths_listed(note, CURRENT_DIRECT_PACKET, PHASE4_NOTE.as_posix())
    require_markers(docs_root, DOCS_ROOT_MARKERS, DOCS_ROOT.as_posix())
    require_markers(scripts_root, SCRIPTS_ROOT_MARKERS, SCRIPTS_ROOT.as_posix())
    require_markers(repo_warning, REPO_WARNING_MARKERS, REPO_WARNING.as_posix())
    require_markers(review_checklist, REVIEW_CHECKLIST_MARKERS, REVIEW_CHECKLIST.as_posix())
    require_markers(tests_readme, TESTS_README_MARKERS, TESTS_README.as_posix())
    require_markers(pins_checker, PINS_CHECKER_MARKERS, PINS_CHECKER.as_posix())
    require_markers(validator_replays, VALIDATOR_REPLAY_MARKERS, VALIDATOR_REPLAYS.as_posix())
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
            "def marker_probe(legacy_alias):",
            '    print("ARTIFACT_DIFF_SELF_TEST=pass")',
            '    print(f"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")',
            '    print("EXPECTED_JSON_ERROR=")',
            '    print("ACTUAL_JSON_ERROR=")',
            '    assert_case("MODE=bytes" in legacy_alias.stdout, "legacy_sha256_alias")',
            "",
        ]
    )


def fixture_root(root: Path) -> None:
    write(root / SURVEY, "\n".join([*SURVEY_MARKERS, bullet_paths(SURVEY_DIRECT_PACKET), bullet_paths(MISSING_BROADER_ARTIFACT_DIFF_COMPANIONS)]) + "\n")
    write(root / PHASE4_NOTE, "\n".join([*NOTE_MARKERS, bullet_paths(HISTORICAL_ARTIFACT_DIFF_PACKET), bullet_paths(CURRENT_DIRECT_PACKET)]) + "\n")
    write(root / DOCS_ROOT, "\n".join(DOCS_ROOT_MARKERS) + "\n")
    write(root / SCRIPTS_ROOT, "\n".join(SCRIPTS_ROOT_MARKERS) + "\n")
    write(root / REPO_WARNING, "\n".join(REPO_WARNING_MARKERS) + "\n")
    write(root / REVIEW_CHECKLIST, "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write(root / TESTS_README, "\n".join(TESTS_README_MARKERS) + "\n")
    write(root / PINS_CHECKER, "\n".join(PINS_CHECKER_MARKERS) + "\n")
    write(root / VALIDATOR_REPLAYS, "\n".join(VALIDATOR_REPLAY_MARKERS) + "\n")
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
        write(root / DIRECT_HELPER, read(root, DIRECT_HELPER).replace('MODE_CHOICES = ("text", "json", "bytes")', 'MODE_CHOICES = ("text", "json")', 1))
        covered.append(expect_failure(root, "helper_mode_drift"))

        fixture_root(root)
        write(root / DIRECT_HELPER, read(root, DIRECT_HELPER).replace('LEGACY_MODE_ALIASES = {"sha256": "bytes"}', 'LEGACY_MODE_ALIASES = {"sha256": "text"}', 1))
        covered.append(expect_failure(root, "helper_alias_drift"))

        fixture_root(root)
        write(root / DIRECT_HELPER, read(root, DIRECT_HELPER).replace('    "invalid_mode_rejected",\n', "", 1))
        covered.append(expect_failure(root, "helper_self_test_catalog_drift"))

        fixture_root(root)
        write(root / DIRECT_HELPER, read(root, DIRECT_HELPER).replace("ACTUAL_JSON_ERROR=", "ACTUAL_JSON_DETAIL=", 1))
        covered.append(expect_failure(root, "helper_marker_drift"))

        fixture_root(root)
        write(root / SURVEY, read(root, SURVEY).replace("scripts/zigux/artifact_diff.py", "scripts/zigux/not-the-right-helper.py", 1))
        covered.append(expect_failure(root, "survey_helper_drift"))

        fixture_root(root)
        write(root / PHASE4_NOTE, read(root, PHASE4_NOTE).replace("scripts/zigux/check-artifact-diff-contract.py", "scripts/zigux/not-the-right-checker.py", 1))
        covered.append(expect_failure(root, "historical_packet_drift"))

        fixture_root(root)
        write(root / DOCS_ROOT, read(root, DOCS_ROOT).replace("host-side artifact-diff tooling contract", "other tooling contract", 1))
        covered.append(expect_failure(root, "docs_root_drift"))

        fixture_root(root)
        write(root / SCRIPTS_ROOT, read(root, SCRIPTS_ROOT).replace("host-side artifact-diff contract", "other contract", 1))
        covered.append(expect_failure(root, "scripts_root_drift"))

        fixture_root(root)
        write(root / REVIEW_CHECKLIST, read(root, REVIEW_CHECKLIST).replace("The dedicated local-only perf packet remains outside the shared validator-first route", "The dedicated local-only perf packet now belongs on the shared validator-first route", 1))
        covered.append(expect_failure(root, "review_checklist_drift"))

        fixture_root(root)
        write(root / TESTS_README, read(root, TESTS_README).replace("artifact-diff contract references", "artifact-diff placeholder references", 1))
        covered.append(expect_failure(root, "tests_readme_drift"))

        fixture_root(root)
        write(root / PINS_CHECKER, read(root, PINS_CHECKER).replace("PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=14", "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=8", 1))
        covered.append(expect_failure(root, "pins_checker_drift"))

        fixture_root(root)
        write(root / VALIDATOR_REPLAYS, read(root, VALIDATOR_REPLAYS).replace("Historical broader validator packet members that still stay explicit here:", "Historical broader helper packet members that still stay explicit here:", 1))
        covered.append(expect_failure(root, "validator_replays_drift"))

        fixture_root(root)
        (root / DIRECT_HELPER).unlink()
        covered.append(expect_failure(root, "missing_direct_helper"))

        fixture_root(root)
        write(root / Path("scripts/zigux/check-artifact-diff-contract.py"), "# republished contract checker\n")
        covered.append(expect_failure(root, "broader_companion_return"))

        fixture_root(root)
        write(root / REPO_WARNING, read(root, REPO_WARNING).replace('"scripts/zigux/validate-phase4.py"', '"scripts/zigux/not-the-right-file.py"', 1))
        covered.append(expect_failure(root, "repo_warning_drift"))

    if tuple(covered) != EXPECTED_SELF_TEST_CASES:
        raise AssertionError(f"expected self-test catalog {EXPECTED_SELF_TEST_CASES}, saw {tuple(covered)}")

    print("PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass")
    print(f"PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT={len(EXPECTED_SELF_TEST_CASES)}")


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
    print(f"PHASE4_ARTIFACT_DIFF_DETERMINISM_SURVEY_DIRECT_PACKET_MEMBERS={len(SURVEY_DIRECT_PACKET)}")
    print(f"PHASE4_ARTIFACT_DIFF_DETERMINISM_MISSING_BROADER_COMPANIONS={len(MISSING_BROADER_ARTIFACT_DIFF_COMPANIONS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())