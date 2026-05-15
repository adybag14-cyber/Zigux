#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

DOCS_README_REL = "Documentation/zigux/README.md"
TESTS_README_REL = "zigux/tests/README.md"
REVIEW_CHECKLIST_REL = "Documentation/zigux/review-checklist.md"
SCRIPTS_README_REL = "scripts/zigux/README.md"
LANE_NOTE_REL = "Documentation/zigux/phase15-governance-lane-sequencing.md"
DOCS_ALIGNMENT_CHECKER_REL = "scripts/zigux/check-phase15-docs-readme-alignment.py"
FREEZE_MAP_REL = "Documentation/zigux/freeze-map.md"
FREEZE_MAP_GOVERNANCE_REL = "Documentation/zigux/phase15-freeze-map-governance.md"

REQUIRED_FILES = (
    DOCS_README_REL,
    REVIEW_CHECKLIST_REL,
    FREEZE_MAP_REL,
    FREEZE_MAP_GOVERNANCE_REL,
    "Documentation/zigux/phase15-parity-scorecard-survey.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    SCRIPTS_README_REL,
    TESTS_README_REL,
    LANE_NOTE_REL,
    DOCS_ALIGNMENT_CHECKER_REL,
)

REVIEW_PROCESS_MARKER = "Documentation/zigux/phase15-architecture-council-review-process.md"
SURVEY_MARKER = "Documentation/zigux/phase15-parity-scorecard-survey.md"
PARITY_SCORECARD_MARKER = "Documentation/zigux/phase15-parity-scorecard.md"
INDEFINITE_C_POLICY_MARKER = "Documentation/zigux/phase15-indefinite-c-policy.md"
READINESS_MARKER = "Documentation/zigux/phase15-readiness-gate-survey.md"
HANDOFF_MARKER = "Documentation/zigux/phase15-handoff-next-steps-survey.md"
SEQUENCING_MARKER = "Documentation/zigux/phase15-governance-lane-sequencing.md"
CHECKER_MARKER = "scripts/zigux/check-phase15-shared-summary-gap.py"
DOCS_ALIGNMENT_CHECKER_MARKER = "scripts/zigux/check-phase15-docs-readme-alignment.py"
ALIGNMENT_CHECKER_MARKER = "scripts/zigux/check-phase15-scripts-readme-alignment.py"
HANDOFF_CHECKER_MARKER = "scripts/zigux/check-phase15-review-process-handoff.py"
LANE_OWNER_ALIGNMENT_MARKER = "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig"
BLOCKER_EVIDENCE_MARKER = "zigux/tests/phase15_indefinite_c_blocker_evidence.zig"
PHASE15_BUILD_MARKER = "zigux/tests/phase15_build.zig"
VALIDATE_MARKER = "scripts/zigux/validate-phase15.py"
HANDOFF_MANIFEST_MARKER = "zigux/tests/phase15_handoff_next_steps_manifest.json"
READINESS_MANIFEST_MARKER = "zigux/tests/phase15_readiness_gate_manifest.json"
PHASE15_VALIDATE_ROUTE = "`make -C zigux phase15-validate`"
PHASE15_TEST_ROUTE = "`make -C zigux phase15-test`"
PHASE15_ROUTE = "`make -C zigux phase15`"
NO_APPROVAL_MARKER = "no-approval-yet posture"

FILE_MARKERS = {
    DOCS_README_REL: (
        "Phase 15 notes",
        FREEZE_MAP_REL,
        FREEZE_MAP_GOVERNANCE_REL,
        REVIEW_PROCESS_MARKER,
        SURVEY_MARKER,
        PARITY_SCORECARD_MARKER,
        INDEFINITE_C_POLICY_MARKER,
        READINESS_MARKER,
        HANDOFF_MARKER,
        SEQUENCING_MARKER,
        ALIGNMENT_CHECKER_MARKER,
        HANDOFF_CHECKER_MARKER,
        LANE_OWNER_ALIGNMENT_MARKER,
        PHASE15_BUILD_MARKER,
        PHASE15_VALIDATE_ROUTE,
        PHASE15_TEST_ROUTE,
        PHASE15_ROUTE,
    ),
    REVIEW_CHECKLIST_REL: (
        "shared Phase 15 governance packet",
        FREEZE_MAP_REL,
        FREEZE_MAP_GOVERNANCE_REL,
        SURVEY_MARKER,
        PARITY_SCORECARD_MARKER,
        INDEFINITE_C_POLICY_MARKER,
        READINESS_MARKER,
        HANDOFF_MARKER,
        SEQUENCING_MARKER,
        VALIDATE_MARKER,
        ALIGNMENT_CHECKER_MARKER,
        HANDOFF_CHECKER_MARKER,
        HANDOFF_MANIFEST_MARKER,
        READINESS_MANIFEST_MARKER,
        PHASE15_VALIDATE_ROUTE,
        PHASE15_TEST_ROUTE,
        PHASE15_ROUTE,
        NO_APPROVAL_MARKER,
    ),
    SCRIPTS_README_REL: (
        "Phase 15 flow",
        SURVEY_MARKER,
        READINESS_MARKER,
        HANDOFF_MARKER,
        SEQUENCING_MARKER,
        VALIDATE_MARKER,
        ALIGNMENT_CHECKER_MARKER,
        HANDOFF_CHECKER_MARKER,
        HANDOFF_MANIFEST_MARKER,
        READINESS_MANIFEST_MARKER,
        BLOCKER_EVIDENCE_MARKER,
        PHASE15_BUILD_MARKER,
        PHASE15_VALIDATE_ROUTE,
        PHASE15_TEST_ROUTE,
        PHASE15_ROUTE,
    ),
    TESTS_README_REL: (
        SEQUENCING_MARKER,
        "zigux/tests/phase15_governance_lane_sequencing.zig",
        PHASE15_VALIDATE_ROUTE,
        PHASE15_TEST_ROUTE,
        PHASE15_ROUTE,
    ),
    LANE_NOTE_REL: (
        SURVEY_MARKER,
        CHECKER_MARKER,
        DOCS_ALIGNMENT_CHECKER_MARKER,
        "`shared-summaries`",
    ),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")
    if issues:
        return issues

    for rel, markers in FILE_MARKERS.items():
        text = _read(root / rel)
        for marker in markers:
            if marker not in text:
                issues.append(f"{rel}:missing:{marker}")

    return issues


def _seed(root: Path) -> None:
    _write(
        root / DOCS_README_REL,
        "\n".join(
            (
                "# docs",
                "Phase 15 notes",
                FREEZE_MAP_REL,
                FREEZE_MAP_GOVERNANCE_REL,
                REVIEW_PROCESS_MARKER,
                SURVEY_MARKER,
                PARITY_SCORECARD_MARKER,
                INDEFINITE_C_POLICY_MARKER,
                READINESS_MARKER,
                HANDOFF_MARKER,
                SEQUENCING_MARKER,
                ALIGNMENT_CHECKER_MARKER,
                HANDOFF_CHECKER_MARKER,
                LANE_OWNER_ALIGNMENT_MARKER,
                PHASE15_BUILD_MARKER,
                PHASE15_VALIDATE_ROUTE,
                PHASE15_TEST_ROUTE,
                PHASE15_ROUTE,
                "",
            )
        ),
    )
    _write(
        root / REVIEW_CHECKLIST_REL,
        "\n".join(
            (
                "# review",
                "shared Phase 15 governance packet",
                FREEZE_MAP_REL,
                FREEZE_MAP_GOVERNANCE_REL,
                SURVEY_MARKER,
                PARITY_SCORECARD_MARKER,
                INDEFINITE_C_POLICY_MARKER,
                READINESS_MARKER,
                HANDOFF_MARKER,
                SEQUENCING_MARKER,
                VALIDATE_MARKER,
                ALIGNMENT_CHECKER_MARKER,
                HANDOFF_CHECKER_MARKER,
                HANDOFF_MANIFEST_MARKER,
                READINESS_MANIFEST_MARKER,
                PHASE15_VALIDATE_ROUTE,
                PHASE15_TEST_ROUTE,
                PHASE15_ROUTE,
                NO_APPROVAL_MARKER,
                "",
            )
        ),
    )
    _write(root / FREEZE_MAP_REL, "# freeze map\n")
    _write(root / FREEZE_MAP_GOVERNANCE_REL, "# freeze map governance\n")
    _write(root / REVIEW_PROCESS_MARKER, "# review process\n")
    _write(root / "Documentation/zigux/phase15-parity-scorecard-survey.md", "# survey\n")
    _write(root / "Documentation/zigux/phase15-parity-scorecard.md", "# parity scorecard\n")
    _write(root / "Documentation/zigux/phase15-indefinite-c-policy.md", "# indefinite c policy\n")
    _write(
        root / SCRIPTS_README_REL,
        "\n".join(
            (
                "# scripts",
                "Phase 15 flow",
                SURVEY_MARKER,
                READINESS_MARKER,
                HANDOFF_MARKER,
                SEQUENCING_MARKER,
                VALIDATE_MARKER,
                ALIGNMENT_CHECKER_MARKER,
                HANDOFF_CHECKER_MARKER,
                HANDOFF_MANIFEST_MARKER,
                READINESS_MANIFEST_MARKER,
                BLOCKER_EVIDENCE_MARKER,
                PHASE15_BUILD_MARKER,
                PHASE15_VALIDATE_ROUTE,
                PHASE15_TEST_ROUTE,
                PHASE15_ROUTE,
                "",
            )
        ),
    )
    _write(
        root / TESTS_README_REL,
        "\n".join(
            (
                "# tests",
                SEQUENCING_MARKER,
                "zigux/tests/phase15_governance_lane_sequencing.zig",
                PHASE15_VALIDATE_ROUTE,
                PHASE15_TEST_ROUTE,
                PHASE15_ROUTE,
                "",
            )
        ),
    )
    _write(
        root / LANE_NOTE_REL,
        "\n".join(
            (
                "# lane",
                "`shared-summaries`",
                CHECKER_MARKER,
                DOCS_ALIGNMENT_CHECKER_MARKER,
                SURVEY_MARKER,
                "",
            )
        ),
    )
    _write(root / DOCS_ALIGNMENT_CHECKER_REL, "# docs checker\n")


def _assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        got = ",".join(actual) or "none"
        want = ",".join(expected) or "none"
        raise SystemExit(f"phase15-shared-summary-gap-self-test:{label}:got={got}:want={want}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_shared_summary_gap_") as tmp_dir:
        root = Path(tmp_dir)
        _seed(root)
        _assert_only(validate(root), [], "baseline")
        case_count += 1

        path = root / DOCS_README_REL
        _write(path, _read(path).replace(FREEZE_MAP_REL + "\n", "", 1))
        _assert_only(
            validate(root),
            [f"{DOCS_README_REL}:missing:{FREEZE_MAP_REL}"],
            "docs_readme_missing_freeze_map",
        )
        _seed(root)
        case_count += 1

        path = root / DOCS_README_REL
        _write(path, _read(path).replace(FREEZE_MAP_GOVERNANCE_REL + "\n", "", 1))
        _assert_only(
            validate(root),
            [f"{DOCS_README_REL}:missing:{FREEZE_MAP_GOVERNANCE_REL}"],
            "docs_readme_missing_freeze_map_governance",
        )
        _seed(root)
        case_count += 1

        path = root / DOCS_README_REL
        _write(path, _read(path).replace(REVIEW_PROCESS_MARKER + "\n", "", 1))
        _assert_only(
            validate(root),
            [f"{DOCS_README_REL}:missing:{REVIEW_PROCESS_MARKER}"],
            "docs_readme_missing_review_process",
        )
        _seed(root)
        case_count += 1

        path = root / DOCS_README_REL
        _write(path, _read(path).replace(SURVEY_MARKER + "\n", "", 1))
        _assert_only(
            validate(root),
            [f"{DOCS_README_REL}:missing:{SURVEY_MARKER}"],
            "docs_readme_missing_survey",
        )
        _seed(root)
        case_count += 1

        path = root / REVIEW_CHECKLIST_REL
        _write(path, _read(path).replace(FREEZE_MAP_REL + "\n", "", 1))
        _assert_only(
            validate(root),
            [f"{REVIEW_CHECKLIST_REL}:missing:{FREEZE_MAP_REL}"],
            "review_checklist_missing_freeze_map",
        )
        _seed(root)
        case_count += 1

        path = root / REVIEW_CHECKLIST_REL
        _write(path, _read(path).replace(FREEZE_MAP_GOVERNANCE_REL + "\n", "", 1))
        _assert_only(
            validate(root),
            [f"{REVIEW_CHECKLIST_REL}:missing:{FREEZE_MAP_GOVERNANCE_REL}"],
            "review_checklist_missing_freeze_map_governance",
        )
        _seed(root)
        case_count += 1

        path = root / REVIEW_CHECKLIST_REL
        _write(path, _read(path).replace(SURVEY_MARKER + "\n", "", 1))
        _assert_only(
            validate(root),
            [f"{REVIEW_CHECKLIST_REL}:missing:{SURVEY_MARKER}"],
            "review_checklist_missing_survey",
        )
        _seed(root)
        case_count += 1

        path = root / SCRIPTS_README_REL
        _write(path, _read(path).replace(SURVEY_MARKER + "\n", "", 1))
        _assert_only(
            validate(root),
            [f"{SCRIPTS_README_REL}:missing:{SURVEY_MARKER}"],
            "scripts_readme_missing_survey",
        )
        _seed(root)
        case_count += 1

        path = root / TESTS_README_REL
        _write(path, _read(path).replace(SEQUENCING_MARKER + "\n", "", 1))
        _assert_only(
            validate(root),
            [f"{TESTS_README_REL}:missing:{SEQUENCING_MARKER}"],
            "tests_readme_missing_lane_note",
        )
        _seed(root)
        case_count += 1

        path = root / LANE_NOTE_REL
        _write(path, _read(path).replace(CHECKER_MARKER + "\n", "", 1))
        _assert_only(
            validate(root),
            [f"{LANE_NOTE_REL}:missing:{CHECKER_MARKER}"],
            "lane_note_missing_checker",
        )
        _seed(root)
        case_count += 1

        (root / "Documentation/zigux/phase15-parity-scorecard-survey.md").unlink()
        _assert_only(
            validate(root),
            ["missing_file:Documentation/zigux/phase15-parity-scorecard-survey.md"],
            "missing_survey_file",
        )
        case_count += 1

        _seed(root)
        (root / FREEZE_MAP_REL).unlink()
        _assert_only(
            validate(root),
            [f"missing_file:{FREEZE_MAP_REL}"],
            "missing_freeze_map_file",
        )
        case_count += 1

        _seed(root)
        (root / FREEZE_MAP_GOVERNANCE_REL).unlink()
        _assert_only(
            validate(root),
            [f"missing_file:{FREEZE_MAP_GOVERNANCE_REL}"],
            "missing_freeze_map_governance_file",
        )
        case_count += 1

        _seed(root)
        (root / LANE_NOTE_REL).unlink()
        _assert_only(
            validate(root),
            [f"missing_file:{LANE_NOTE_REL}"],
            "missing_lane_note_file",
        )
        case_count += 1

        _seed(root)
        (root / DOCS_ALIGNMENT_CHECKER_REL).unlink()
        _assert_only(
            validate(root),
            [f"missing_file:{DOCS_ALIGNMENT_CHECKER_REL}"],
            "missing_docs_alignment_checker_file",
        )
        case_count += 1

    print("PHASE15_SHARED_SUMMARY_GAP_SELF_TEST=pass")
    print(f"PHASE15_SHARED_SUMMARY_GAP_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the current Phase 15 shared summaries keep the freeze-map governance packet, the review-process "
            "survey marker, the parity-scorecard survey, the dedicated parity-scorecard and indefinite-C policy surfaces, "
            "readiness and handoff reminders, the review-process handoff checker, the scripts-root blocker-evidence marker, "
            "the lane-sequencing note, the docs-root and scripts-root alignment checkers, the replay-build surface, the "
            "validator-route packet, the manifest reminders, the lane-owner alignment surface, and the replay-route packet explicit."
        )
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        print("PHASE15_SHARED_SUMMARY_GAP=fail")
        print("PHASE15_SHARED_SUMMARY_GAP_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE15_SHARED_SUMMARY_GAP_ISSUES_END")
        return 1

    print("PHASE15_SHARED_SUMMARY_GAP=pass")
    print(f"PHASE15_SHARED_SUMMARY_GAP_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE15_SHARED_SUMMARY_GAP_REQUIRED_MARKER_COUNT={sum(len(v) for v in FILE_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())