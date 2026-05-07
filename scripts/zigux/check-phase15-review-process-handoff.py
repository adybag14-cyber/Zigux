#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

DOCS_README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
NOTE_PATH = "Documentation/zigux/phase15-architecture-council-review-process.md"
MANIFEST_PATH = "zigux/tests/phase15_architecture_council_review_process_manifest.json"
SCRIPT_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
EXPECTED_LANE_KEY = "P15-L08"

PRODUCT_BOUNDARY_MARKER = "product boundary:\n  - `Documentation/zigux/freeze-map.md`"
REQUIRED_NOTE_MARKERS = (
    f"`PHASE15_LANE_KEY={EXPECTED_LANE_KEY}`",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
    "current review-process evidence is limited to named `phase`",
    "`current status bucket`",
    "`validation gate summary`",
    "`indefinite-C policy link or non-applicability note`",
    "`rollback-threshold`",
    "landed `phase15-roadmap-minimum-field-sync`",
)

REQUIRED_REVIEW_PACKET_FIELDS = (
    "linux anchor path",
    "phase",
    "current status bucket",
    "requested decision bucket",
    "decision record ID",
    "owner",
    "rollback owner",
    "validation gate summary",
    "evidence archive path",
    "latest blocker disposition",
    "benchmark notes",
    "replay command",
    "rollback threshold",
    "retained discussion state",
    "reopen triggers",
    "parity scorecard link or blocker record",
    "indefinite-C policy link or non-applicability note",
    "explicit non-goals",
    "written rationale",
)

REQUIRED_OWNERSHIP_FIELDS = (
    "phase",
    "current status bucket",
    "owner",
    "rollback owner",
    "validation gate summary",
    "indefinite-C policy link or non-applicability note",
    "evidence archive path",
    "latest blocker disposition",
    "benchmark notes",
    "replay command",
    "rollback threshold",
    "retained discussion state",
    "reopen triggers",
    "parity scorecard link or blocker record",
)

REQUIRED_CURRENT_REPO_HANDOFF_MARKERS = (
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_readiness_gate.zig",
    "zigux/tests/phase15_build.zig",
)

REQUIRED_CURRENT_BOUNDED_LANE_MARKERS = (
    "scripts-root validator path",
    "Linux-style `make -C zigux phase15-validate` route",
    "tests-root guidance path",
    "dedicated handoff-checker route",
)

REQUIRED_DOCS_README_MARKERS = (
    "Phase 15 notes",
    "`Documentation/zigux/freeze-map.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`Documentation/zigux/phase15-readiness-gate-survey.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/check-phase15-scripts-readme-alignment.py`",
    "`scripts/zigux/check-phase15-review-process-handoff.py`",
    "`zigux/tests/README.md`",
    "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
    "`zigux/tests/phase15_freeze_map_governance.zig`",
    "`zigux/tests/phase15_parity_scorecard.zig`",
    "`zigux/tests/phase15_architecture_council_review_process.zig`",
    "`zigux/tests/phase15_handoff_next_steps.zig`",
    "`zigux/tests/phase15_indefinite_c_policy.json`",
    "`zigux/tests/phase15_indefinite_c_policy.zig`",
    "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
    "`zigux/tests/phase15_readiness_gate.zig`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`zigux/tests/phase15_build.zig`",
    "`zigux/Makefile`",
    "`make -C zigux phase15-validate`",
    "`make -C zigux phase15`",
    "no Architecture Council approval is recorded yet",
)

REQUIRED_REVIEW_CHECKLIST_MARKERS = (
    "if the change touches the shared Phase 15 governance packet",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_build.zig",
    "make -C zigux phase15",
)

REQUIRED_SCRIPT_README_MARKERS = (
    "Phase 15 flow",
    "phase15-freeze-map-governance.md",
    "phase15-architecture-council-review-process.md",
    "phase15-handoff-next-steps-survey.md",
    "phase15-readiness-gate-survey.md",
    "phase15-parity-scorecard.md",
    "phase15-indefinite-c-policy.md",
    "check-phase15-scripts-readme-alignment.py",
    "check-phase15-review-process-handoff.py",
    "phase15_architecture_council_review_process_manifest.json",
    "phase15_freeze_map_governance.zig",
    "phase15_parity_scorecard.zig",
    "phase15_architecture_council_review_process.zig",
    "phase15_indefinite_c_policy.json",
    "phase15_indefinite_c_policy.zig",
    "phase15_build.zig",
    "make -C zigux phase15",
)

REQUIRED_TESTS_README_MARKERS = (
    "keep the parked Phase 15 governance packet explicit in the tests root too",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_readiness_gate.zig",
    "zigux/Makefile",
    "make -C zigux phase15-validate",
    "zig build test --build-file zigux/tests/phase15_build.zig",
    "make -C zigux phase15",
    "without implying any Architecture Council approval for a freeze-map status change",
)

REQUIRED_MAKEFILE_MARKERS = (
    "PHONY += phase15-validate phase15-test phase15",
    "phase15-validate:",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py --self-test",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py --self-test",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "phase15-test:",
    "zigux/tests/phase15_build.zig",
)

REQUIRED_WORKFLOW_MARKERS = (
    "- name: Validate Phase 15 governance packet",
    "run: make -C zigux phase15-validate",
    "- name: Run Phase 15 governance tests",
    "run: make -C zigux phase15-test",
)

REQUIRED_FILES = (
    DOCS_README_PATH,
    REVIEW_CHECKLIST_PATH,
    NOTE_PATH,
    MANIFEST_PATH,
    SCRIPT_README_PATH,
    TESTS_README_PATH,
    MAKEFILE_PATH,
    WORKFLOW_PATH,
)


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def expect_markers(text: str, markers: tuple[str, ...], label: str, failures: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{label}:{marker}")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    docs_readme = read_text(root, DOCS_README_PATH)
    review_checklist = read_text(root, REVIEW_CHECKLIST_PATH)
    note = read_text(root, NOTE_PATH)
    manifest = json.loads(read_text(root, MANIFEST_PATH))
    script_readme = read_text(root, SCRIPT_README_PATH)
    tests_readme = read_text(root, TESTS_README_PATH)
    makefile = read_text(root, MAKEFILE_PATH)
    workflow = read_text(root, WORKFLOW_PATH)

    expect_markers(docs_readme, REQUIRED_DOCS_README_MARKERS, "docs_readme", failures)
    expect_markers(review_checklist, REQUIRED_REVIEW_CHECKLIST_MARKERS, "review_checklist", failures)
    if PRODUCT_BOUNDARY_MARKER not in note:
        failures.append("note:product_boundary")
    expect_markers(note, REQUIRED_NOTE_MARKERS, "note", failures)
    expect_markers(script_readme, REQUIRED_SCRIPT_README_MARKERS, "script_readme", failures)
    expect_markers(tests_readme, REQUIRED_TESTS_README_MARKERS, "tests_readme", failures)
    expect_markers(makefile, REQUIRED_MAKEFILE_MARKERS, "makefile", failures)
    expect_markers(workflow, REQUIRED_WORKFLOW_MARKERS, "workflow", failures)

    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        failures.append(f"manifest:lane_key:{manifest.get('lane_key')}")

    review_fields = manifest.get("required_review_packet_fields")
    if not isinstance(review_fields, list):
        failures.append("manifest:required_review_packet_fields")
    else:
        for field in REQUIRED_REVIEW_PACKET_FIELDS:
            if field not in review_fields:
                failures.append(f"manifest_required_review_packet_fields:{field}")

    ownership_fields = manifest.get("ownership_evidence_fields")
    if not isinstance(ownership_fields, list):
        failures.append("manifest:ownership_evidence_fields")
    else:
        for field in REQUIRED_OWNERSHIP_FIELDS:
            if field not in ownership_fields:
                failures.append(f"manifest_ownership_evidence_fields:{field}")

    handoff = manifest.get("handoff_evidence")
    if not isinstance(handoff, dict):
        failures.append("manifest:handoff_evidence")
        return failures

    current_repo_handoff = handoff.get("current_repo_handoff")
    if not isinstance(current_repo_handoff, str):
        failures.append("manifest:current_repo_handoff")
    else:
        expect_markers(current_repo_handoff, REQUIRED_CURRENT_REPO_HANDOFF_MARKERS, "manifest_handoff", failures)

    current_bounded_lane = handoff.get("current_bounded_lane")
    if not isinstance(current_bounded_lane, str):
        failures.append("manifest:current_bounded_lane")
    else:
        expect_markers(current_bounded_lane, REQUIRED_CURRENT_BOUNDED_LANE_MARKERS, "manifest_lane", failures)

    return failures


def write_fixture_tree(root: Path) -> None:
    (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
    (root / "zigux/tests").mkdir(parents=True, exist_ok=True)
    (root / "scripts/zigux").mkdir(parents=True, exist_ok=True)
    (root / "zigux").mkdir(parents=True, exist_ok=True)
    (root / ".github/workflows").mkdir(parents=True, exist_ok=True)

    (root / DOCS_README_PATH).write_text("\n".join((
        "# Documentation/zigux",
        "Phase 15 notes",
        *REQUIRED_DOCS_README_MARKERS[1:],
        "",
    )), encoding="utf-8")

    (root / REVIEW_CHECKLIST_PATH).write_text("\n".join((
        "# Review Checklist",
        *REQUIRED_REVIEW_CHECKLIST_MARKERS,
        "",
    )), encoding="utf-8")

    (root / NOTE_PATH).write_text("\n".join((
        "# Phase 15 Architecture Council Review Process Survey",
        "## Status",
        REQUIRED_NOTE_MARKERS[0],
        PRODUCT_BOUNDARY_MARKER,
        "## Current Approval Posture",
        "- current review-process evidence is limited to named `phase`, `current status bucket`, `owner`, `rollback owner`, `validation gate summary`, `indefinite-C policy link or non-applicability note`, evidence archive, blocker-disposition, benchmark-notes, replay-command, `rollback-threshold`, retained-discussion-state, and reopen-trigger records",
        "## Recorded Gaps",
        "- landed `phase15-roadmap-minimum-field-sync`",
        "- no Architecture Council approval is currently recorded for a freeze-map status change",
        "",
    )), encoding="utf-8")

    manifest = {
        "lane_key": EXPECTED_LANE_KEY,
        "required_review_packet_fields": list(REQUIRED_REVIEW_PACKET_FIELDS),
        "ownership_evidence_fields": list(REQUIRED_OWNERSHIP_FIELDS),
        "handoff_evidence": {
            "current_repo_handoff": " ".join(REQUIRED_CURRENT_REPO_HANDOFF_MARKERS),
            "current_bounded_lane": " ".join(REQUIRED_CURRENT_BOUNDED_LANE_MARKERS),
        },
    }
    (root / MANIFEST_PATH).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    (root / SCRIPT_README_PATH).write_text("\n".join((
        "# scripts/zigux",
        *REQUIRED_SCRIPT_README_MARKERS,
        "",
    )), encoding="utf-8")

    (root / TESTS_README_PATH).write_text("\n".join((
        "# zigux/tests",
        *REQUIRED_TESTS_README_MARKERS,
        "",
    )), encoding="utf-8")

    (root / MAKEFILE_PATH).write_text("\n".join((
        *REQUIRED_MAKEFILE_MARKERS,
        "",
    )), encoding="utf-8")

    (root / WORKFLOW_PATH).write_text("\n".join((
        *REQUIRED_WORKFLOW_MARKERS,
        "",
    )), encoding="utf-8")


def expect_only(root: Path, expected: list[str], label: str) -> None:
    failures = validate(root)
    if failures != expected:
        raise SystemExit(f"{label}:got={failures}:want={expected}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_review_process_handoff_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_tree(root)
        expect_only(root, [], "baseline")
        case_count += 1

        note_path = root / NOTE_PATH
        original_note = note_path.read_text(encoding="utf-8")
        note_path.write_text(original_note.replace("`rollback-threshold`", "`rollback ceiling`", 1), encoding="utf-8")
        expect_only(root, ["note:`rollback-threshold`"], "missing_rollback_threshold_marker")
        note_path.write_text(original_note, encoding="utf-8")
        case_count += 1

        note_path.write_text(original_note.replace("`indefinite-C policy link or non-applicability note`", "`indefinite-C policy link`", 1), encoding="utf-8")
        expect_only(root, ["note:`indefinite-C policy link or non-applicability note`"], "missing_indefinite_c_marker")
        note_path.write_text(original_note, encoding="utf-8")
        case_count += 1

        manifest_path = root / MANIFEST_PATH
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["required_review_packet_fields"].remove("rollback threshold")
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_only(root, ["manifest_required_review_packet_fields:rollback threshold"], "missing_review_packet_field")
        write_fixture_tree(root)
        case_count += 1

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["ownership_evidence_fields"].remove("indefinite-C policy link or non-applicability note")
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_only(root, ["manifest_ownership_evidence_fields:indefinite-C policy link or non-applicability note"], "missing_ownership_field")
        write_fixture_tree(root)
        case_count += 1

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["handoff_evidence"]["current_repo_handoff"] = manifest["handoff_evidence"]["current_repo_handoff"].replace("zigux/tests/phase15_build.zig", "zigux/tests/phase15_phase_build.zig", 1)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_only(root, ["manifest_handoff:zigux/tests/phase15_build.zig"], "missing_current_repo_handoff_marker")
        write_fixture_tree(root)
        case_count += 1

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["handoff_evidence"]["current_repo_handoff"] = manifest["handoff_evidence"]["current_repo_handoff"].replace(
            "Documentation/zigux/phase15-handoff-next-steps-survey.md",
            "",
            1,
        )
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_only(
            root,
            ["manifest_handoff:Documentation/zigux/phase15-handoff-next-steps-survey.md"],
            "missing_current_repo_handoff_handoff_note_marker",
        )
        write_fixture_tree(root)
        case_count += 1

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["handoff_evidence"]["current_repo_handoff"] = manifest["handoff_evidence"]["current_repo_handoff"].replace(
            "Documentation/zigux/phase15-readiness-gate-survey.md",
            "",
            1,
        )
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_only(
            root,
            ["manifest_handoff:Documentation/zigux/phase15-readiness-gate-survey.md"],
            "missing_current_repo_handoff_readiness_note_marker",
        )
        write_fixture_tree(root)
        case_count += 1

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["handoff_evidence"]["current_bounded_lane"] = manifest["handoff_evidence"]["current_bounded_lane"].replace("scripts-root validator path", "scripts validator path", 1)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_only(root, ["manifest_lane:scripts-root validator path"], "missing_current_bounded_lane_marker")
        write_fixture_tree(root)
        case_count += 1

        docs_readme_path = root / DOCS_README_PATH
        original_docs_readme = docs_readme_path.read_text(encoding="utf-8")
        docs_readme_path.write_text(
            original_docs_readme.replace(
                "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
                "`Documentation/zigux/phase15-handoff-next-steps.md`",
                1,
            ),
            encoding="utf-8",
        )
        expect_only(
            root,
            ["docs_readme:`Documentation/zigux/phase15-handoff-next-steps-survey.md`"],
            "missing_docs_readme_handoff_note_marker",
        )
        docs_readme_path.write_text(original_docs_readme, encoding="utf-8")
        case_count += 1

        script_readme_path = root / SCRIPT_README_PATH
        original_script_readme = script_readme_path.read_text(encoding="utf-8")
        script_readme_path.write_text(
            original_script_readme.replace(
                "phase15-readiness-gate-survey.md",
                "phase15-readiness-gate.md",
                1,
            ),
            encoding="utf-8",
        )
        expect_only(
            root,
            ["script_readme:phase15-readiness-gate-survey.md"],
            "missing_script_readme_readiness_note_marker",
        )
        script_readme_path.write_text(original_script_readme, encoding="utf-8")
        case_count += 1

    print("PHASE15_REVIEW_PROCESS_HANDOFF_SELF_TEST=pass")
    print(f"PHASE15_REVIEW_PROCESS_HANDOFF_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Phase 15 Architecture Council review-process handoff surfaces.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run the fixture-backed self-test.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE15_REVIEW_PROCESS_HANDOFF=fail")
        print("PHASE15_REVIEW_PROCESS_HANDOFF_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE15_REVIEW_PROCESS_HANDOFF_FAILURES_END")
        return 1

    print("PHASE15_REVIEW_PROCESS_HANDOFF=pass")
    print(
        "PHASE15_REVIEW_PROCESS_HANDOFF_MARKER_COUNT="
        f"{len(REQUIRED_NOTE_MARKERS) + len(REQUIRED_REVIEW_PACKET_FIELDS) + len(REQUIRED_OWNERSHIP_FIELDS) + len(REQUIRED_CURRENT_REPO_HANDOFF_MARKERS) + len(REQUIRED_CURRENT_BOUNDED_LANE_MARKERS) + len(REQUIRED_DOCS_README_MARKERS) + len(REQUIRED_REVIEW_CHECKLIST_MARKERS) + len(REQUIRED_SCRIPT_README_MARKERS) + len(REQUIRED_TESTS_README_MARKERS) + len(REQUIRED_MAKEFILE_MARKERS) + len(REQUIRED_WORKFLOW_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
