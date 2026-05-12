#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

FILES = [
    "scripts/zigux/validate-phase15.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "zigux/tests/README.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_indefinite_c_blocker_evidence.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_readiness_gate.zig",
]

MAKE_MARKERS = [
    "PHONY += phase15-validate phase15-test phase15",
    "phase15-validate:",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py --self-test",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py --self-test",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/validate-phase15.py",
    "phase15-test:",
    "$(ZIG) build test --build-file zigux/tests/phase15_build.zig",
    "phase15: phase15-validate phase15-test",
]

WORKFLOW_MARKERS = [
    "Validate Phase 15 governance packet",
    "make -C zigux phase15-validate",
    "Run Phase 15 governance tests",
    "make -C zigux phase15-test",
]

DOCS_README_MARKERS = [
    "Phase 15 notes",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "zigux/tests/phase15_build.zig",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
    "no Architecture Council approval is recorded yet",
    "named reopen trigger",
    "deep-core blocker-posture change",
]

SCRIPTS_README_MARKERS = [
    "Phase 15 flow",
    "validate-phase15.py",
    "check-phase15-review-process-handoff.py",
    "check-phase15-scripts-readme-alignment.py",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_indefinite_c_blocker_evidence.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_readiness_gate.zig",
    "make -C zigux phase15-validate",
    "make -C zigux phase15",
]

TESTS_README_MARKERS = [
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_indefinite_c_blocker_evidence.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_readiness_gate.zig",
]

REVIEW_CHECKLIST_MARKERS = [
    "if the change touches the shared Phase 15 governance packet",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_readiness_gate.zig",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
    "no-approval-yet posture",
]

READINESS_SURVEY_MARKERS = [
    "PHASE15_LANE_KEY=P15-L01",
    "The packet remains parked.",
    "no Architecture Council approval is currently recorded",
    "validator-first route stays explicit through `python3 scripts/zigux/validate-phase15.py` and `make -C zigux phase15-validate`",
    "shared replay route stays explicit through `zigux/tests/phase15_build.zig`",
    "zig build test --build-file zigux/tests/phase15_build.zig",
    "make -C zigux phase15-test",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase15.py",
    "zigux/Makefile",
    "no-approval-yet maintenance-mode blocker posture",
    "the remaining blocker is still `phase15-deep-core-status-change-blocker`",
    "Later repo movement still requires a fresh bounded provenance refresh",
]

READINESS_MANIFEST_REL = "zigux/tests/phase15_readiness_gate_manifest.json"
READINESS_CHECKERS = [
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
]
READINESS_BOOL_FIELDS = [
    "phase15_validate_target_present",
    "phase15_test_target_present",
    "shared_ci_phase15_present",
    "phase15_replay_green_on_current_master",
]


def _read(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _require_markers(name: str, source: str, markers: list[str], missing: list[str]) -> None:
    for marker in markers:
        if marker not in source:
            missing.append(f"{name}:{marker}")


def _validate_readiness_manifest(root: Path, missing: list[str]) -> None:
    manifest = json.loads(_read(root, READINESS_MANIFEST_REL))
    repo_evidence = manifest.get("repo_evidence")
    if not isinstance(repo_evidence, dict):
        missing.append("readiness_manifest:repo_evidence")
        return

    for field in READINESS_BOOL_FIELDS:
        if repo_evidence.get(field) is not True:
            missing.append(f"readiness_manifest:{field}")

    checkers = manifest.get("phase15_validate_checkers")
    if checkers != READINESS_CHECKERS:
        missing.append("readiness_manifest:phase15_validate_checkers")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []
    _require_markers("make", _read(root, "zigux/Makefile"), MAKE_MARKERS, missing_markers)
    _require_markers(
        "workflow",
        _read(root, ".github/workflows/zigux-bootstrap.yml"),
        WORKFLOW_MARKERS,
        missing_markers,
    )
    _require_markers(
        "docs_readme",
        _read(root, "Documentation/zigux/README.md"),
        DOCS_README_MARKERS,
        missing_markers,
    )
    _require_markers(
        "scripts_readme",
        _read(root, "scripts/zigux/README.md"),
        SCRIPTS_README_MARKERS,
        missing_markers,
    )
    _require_markers(
        "tests_readme",
        _read(root, "zigux/tests/README.md"),
        TESTS_README_MARKERS,
        missing_markers,
    )
    _require_markers(
        "review_checklist",
        _read(root, "Documentation/zigux/review-checklist.md"),
        REVIEW_CHECKLIST_MARKERS,
        missing_markers,
    )
    _require_markers(
        "readiness_survey",
        _read(root, "Documentation/zigux/phase15-readiness-gate-survey.md"),
        READINESS_SURVEY_MARKERS,
        missing_markers,
    )
    _validate_readiness_manifest(root, missing_markers)
    return [], missing_markers


def _baseline_docs_readme() -> str:
    return "\n".join(
        (
            "# Zigux Documentation",
            "Phase 15 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-freeze-map-governance.md` - `Documentation/zigux/phase15-architecture-council-review-process.md` - `Documentation/zigux/phase15-parity-scorecard.md` - `Documentation/zigux/phase15-indefinite-c-policy.md` - `zigux/tests/phase15_build.zig` - `make -C zigux phase15-validate` - `make -C zigux phase15-test` - `make -C zigux phase15` now keep the current freeze-map, dedicated freeze-map-governance note, Architecture Council review-process, parity-scorecard, dedicated indefinite-C policy note, and stay-in-C governance packet reviewable through the shipped validator-first route, the shared build replay, and the full Linux-style Phase 15 lane instead of widening into ad hoc deep-core status claims.",
            "- the current bounded Phase 15 decision is not whether a freeze-in-C anchor is ready for a direct Zigux port; no Architecture Council approval is recorded yet, so the next follow-up should wait for a named reopen trigger or a real deep-core blocker-posture change before opening another governance slice.",
            "",
        )
    )


def _seed_fixture_tree(root: Path) -> None:
    _write(root, "scripts/zigux/validate-phase15.py", "# stub\n")
    _write(root, "scripts/zigux/check-phase15-scripts-readme-alignment.py", "# stub\n")
    _write(root, "scripts/zigux/check-phase15-review-process-handoff.py", "# stub\n")
    _write(root, "scripts/zigux/README.md", "\n".join(SCRIPTS_README_MARKERS) + "\n")
    _write(root, "Documentation/zigux/README.md", _baseline_docs_readme())
    _write(root, "Documentation/zigux/freeze-map.md", "# freeze map\n")
    _write(root, "Documentation/zigux/review-checklist.md", "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    _write(root, "Documentation/zigux/phase15-freeze-map-governance.md", "# freeze governance\n")
    _write(
        root,
        "Documentation/zigux/phase15-architecture-council-review-process.md",
        "# review process\n",
    )
    _write(root, "Documentation/zigux/phase15-parity-scorecard.md", "# parity\n")
    _write(root, "Documentation/zigux/phase15-indefinite-c-policy.md", "# policy\n")
    _write(
        root,
        "Documentation/zigux/phase15-readiness-gate-survey.md",
        "\n".join(READINESS_SURVEY_MARKERS) + "\n",
    )
    _write(root, "Documentation/zigux/phase15-handoff-next-steps-survey.md", "# handoff\n")
    _write(root, "Documentation/zigux/phase15-governance-lane-sequencing.md", "# lane sequencing\n")
    _write(root, "zigux/tests/README.md", "\n".join(TESTS_README_MARKERS) + "\n")
    _write(
        root,
        ".github/workflows/zigux-bootstrap.yml",
        "\n".join(WORKFLOW_MARKERS) + "\n",
    )
    _write(root, "zigux/Makefile", "\n".join(MAKE_MARKERS) + "\n")
    for rel in (
        "zigux/tests/phase15_build.zig",
        "zigux/tests/phase15_freeze_map_governance.zig",
        "zigux/tests/phase15_parity_scorecard.zig",
        "zigux/tests/phase15_architecture_council_review_process.zig",
        "zigux/tests/phase15_indefinite_c_policy.zig",
        "zigux/tests/phase15_handoff_next_steps.zig",
        "zigux/tests/phase15_indefinite_c_blocker_evidence.zig",
        "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
        "zigux/tests/phase15_governance_lane_sequencing.zig",
        "zigux/tests/phase15_readiness_gate.zig",
    ):
        _write(root, rel, "// stub\n")
    for rel in (
        "zigux/tests/phase15_architecture_council_review_process_manifest.json",
        "zigux/tests/phase15_handoff_next_steps_manifest.json",
        "zigux/tests/phase15_indefinite_c_policy.json",
    ):
        _write(root, rel, "{}\n")
    _write(
        root,
        READINESS_MANIFEST_REL,
        json.dumps(
            {
                "repo_evidence": {
                    "phase15_validate_target_present": True,
                    "phase15_test_target_present": True,
                    "shared_ci_phase15_present": True,
                    "phase15_replay_green_on_current_master": True,
                },
                "phase15_validate_checkers": READINESS_CHECKERS,
            },
            indent=2,
        )
        + "\n",
    )


def _assert_result(
    missing_files: list[str],
    missing_markers: list[str],
    expected_files: list[str],
    expected_markers: list[str],
    label: str,
) -> None:
    if missing_files != expected_files or missing_markers != expected_markers:
        raise SystemExit(
            f"phase15-self-test:{label}:got_files={missing_files}:got_markers={missing_markers}:"
            f"want_files={expected_files}:want_markers={expected_markers}"
        )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_validate_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_fixture_tree(root)
        _assert_result(*validate(root), [], [], "baseline")
        case_count += 1

        docs_rel = "Documentation/zigux/README.md"
        docs_text = _read(root, docs_rel)
        missing_docs_marker = "make -C zigux phase15-validate"
        _write(root, docs_rel, docs_text.replace(missing_docs_marker, "", 1))
        _assert_result(*validate(root), [], [f"docs_readme:{missing_docs_marker}"], "docs_marker")
        _seed_fixture_tree(root)
        case_count += 1

        docs_text = _read(root, docs_rel)
        missing_docs_test_marker = "make -C zigux phase15-test"
        _write(root, docs_rel, docs_text.replace(missing_docs_test_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"docs_readme:{missing_docs_test_marker}"],
            "docs_test_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        checklist_rel = "Documentation/zigux/review-checklist.md"
        checklist_text = _read(root, checklist_rel)
        missing_checklist_lane_marker = "Documentation/zigux/phase15-governance-lane-sequencing.md"
        _write(root, checklist_rel, checklist_text.replace(missing_checklist_lane_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"review_checklist:{missing_checklist_lane_marker}"],
            "review_checklist_lane_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        checklist_text = _read(root, checklist_rel)
        missing_handoff_manifest_marker = "zigux/tests/phase15_handoff_next_steps_manifest.json"
        _write(root, checklist_rel, checklist_text.replace(missing_handoff_manifest_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"review_checklist:{missing_handoff_manifest_marker}"],
            "review_checklist_handoff_manifest_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        checklist_text = _read(root, checklist_rel)
        missing_readiness_manifest_marker = "zigux/tests/phase15_readiness_gate_manifest.json"
        _write(root, checklist_rel, checklist_text.replace(missing_readiness_manifest_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"review_checklist:{missing_readiness_manifest_marker}"],
            "review_checklist_readiness_manifest_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        readiness_rel = "Documentation/zigux/phase15-readiness-gate-survey.md"
        readiness_text = _read(root, readiness_rel)
        missing_readiness_marker = "make -C zigux phase15-test"
        _write(root, readiness_rel, readiness_text.replace(missing_readiness_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"readiness_survey:{missing_readiness_marker}"],
            "readiness_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        readiness_text = _read(root, readiness_rel)
        missing_readiness_scope_marker = "Documentation/zigux/review-checklist.md"
        _write(
            root,
            readiness_rel,
            readiness_text.replace(missing_readiness_scope_marker, "", 1),
        )
        _assert_result(
            *validate(root),
            [],
            [f"readiness_survey:{missing_readiness_scope_marker}"],
            "readiness_scope_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        make_rel = "zigux/Makefile"
        make_text = _read(root, make_rel)
        missing_make_marker = "scripts/zigux/check-phase15-review-process-handoff.py --self-test"
        _write(root, make_rel, make_text.replace(missing_make_marker + "\n", "", 1))
        _assert_result(*validate(root), [], [f"make:{missing_make_marker}"], "make_marker")
        _seed_fixture_tree(root)
        case_count += 1

        manifest_text = json.loads(_read(root, READINESS_MANIFEST_REL))
        manifest_text["repo_evidence"]["phase15_validate_target_present"] = False
        _write(root, READINESS_MANIFEST_REL, json.dumps(manifest_text, indent=2) + "\n")
        _assert_result(
            *validate(root),
            [],
            ["readiness_manifest:phase15_validate_target_present"],
            "manifest_validate_target_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        manifest_text = json.loads(_read(root, READINESS_MANIFEST_REL))
        manifest_text["phase15_validate_checkers"] = [READINESS_CHECKERS[0]]
        _write(root, READINESS_MANIFEST_REL, json.dumps(manifest_text, indent=2) + "\n")
        _assert_result(
            *validate(root),
            [],
            ["readiness_manifest:phase15_validate_checkers"],
            "manifest_checker_pair_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        missing_file = "zigux/tests/phase15_handoff_next_steps.zig"
        (root / missing_file).unlink()
        _assert_result(*validate(root), [missing_file], [], "missing_file")
        case_count += 1

    print("PHASE15_VALIDATE_SELF_TEST=pass")
    print(f"PHASE15_VALIDATE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the parked Phase 15 governance packet surfaces."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(args.root)
    if missing_files:
        print("PHASE15_VALIDATION=fail")
        print("MISSING_PHASE15_FILES_START")
        for path in missing_files:
            print(path)
        print("MISSING_PHASE15_FILES_END")
        return 1

    if missing_markers:
        print("PHASE15_VALIDATION=fail")
        print("PHASE15_VALIDATION_MISSING_START")
        for item in missing_markers:
            print(item)
        print("PHASE15_VALIDATION_MISSING_END")
        return 1

    print("PHASE15_VALIDATION=pass")
    print(f"PHASE15_REQUIRED_FILE_COUNT={len(FILES)}")
    print(
        "PHASE15_REQUIRED_MARKER_COUNT="
        + str(
            len(MAKE_MARKERS)
            + len(WORKFLOW_MARKERS)
            + len(DOCS_README_MARKERS)
            + len(SCRIPTS_README_MARKERS)
            + len(TESTS_README_MARKERS)
            + len(REVIEW_CHECKLIST_MARKERS)
            + len(READINESS_SURVEY_MARKERS)
            + len(READINESS_BOOL_FIELDS)
            + len(READINESS_CHECKERS)
        )
    )
    print("PHASE15_REMAINING_BLOCKERS=phase15-deep-core-status-change-blocker")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
