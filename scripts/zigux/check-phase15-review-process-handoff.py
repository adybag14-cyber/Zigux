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
EXPECTED_LANE_KEY = "P15-L07"
EXPECTED_ROADMAP_REQUIREMENT = "Architecture Council review process"
DATED_READBACK_PREFIX = "current-master-readback-"
LEGACY_VERIFIED_HEAD = "4fc891b380cdd2991dff7676ade7f844df1b55fd"

PRODUCT_BOUNDARY_MARKER = "product boundary:"
REQUIRED_PRODUCT_BOUNDARY_MARKERS = (
    "  - `Documentation/zigux/freeze-map.md`",
    "  - `Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "  - `Documentation/zigux/phase15-readiness-gate-survey.md`",
    "  - `Documentation/zigux/phase15-parity-scorecard.md`",
    "  - `Documentation/zigux/phase15-indefinite-c-policy.md`",
    "  - `Documentation/zigux/phase15-governance-lane-sequencing.md`",
    "  - `Documentation/zigux/review-checklist.md`",
    "  - `scripts/zigux/README.md`",
    "  - `zigux/tests/README.md`",
    "  - `zigux/Makefile`",
    "  - `scripts/zigux/check-phase15-scripts-readme-alignment.py`",
    "  - `scripts/zigux/check-phase15-review-process-handoff.py`",
    "  - `.github/workflows/zigux-bootstrap.yml`",
    "  - `zigux/tests/phase15_architecture_council_review_process.zig`",
    "  - `zigux/tests/phase15_handoff_next_steps_manifest.json`",
    "  - `zigux/tests/phase15_handoff_next_steps.zig`",
    "  - `zigux/tests/phase15_indefinite_c_policy.json`",
    "  - `zigux/tests/phase15_indefinite_c_policy.zig`",
    "  - `zigux/tests/phase15_indefinite_c_blocker_evidence.zig`",
    "  - `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
    "  - `zigux/tests/phase15_governance_lane_sequencing.zig`",
    "  - `zigux/tests/phase15_readiness_gate_manifest.json`",
    "  - `zigux/tests/phase15_readiness_gate.zig`",
    "  - `zigux/tests/phase15_build.zig`",
)
REQUIRED_GENERIC_NOTE_MARKERS = (
    f"`PHASE15_LANE_KEY={EXPECTED_LANE_KEY}`",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
    "current review-process evidence is limited to named `phase`",
    "`current status bucket`",
    "`required approver set`",
    "`validation gate summary`",
    "`parity scorecard link or blocker record`",
    "`indefinite-C policy link or non-applicability note`",
    "workflow-backed replay anchor `.github/workflows/zigux-bootstrap.yml`",
    "dedicated `make -C zigux phase15-test` route",
    "landed `phase15-roadmap-minimum-field-sync`",
    "landed `phase15-workflow-replay-anchor-visible`",
    "landed `phase15-dedicated-make-test-replay-visible`",
)
VERIFIED_MODE_NOTE_MARKERS = (
    "`PHASE15_PROVENANCE_MODE=verified_master_head`",
    "survey provenance refreshed against verified `master` head `",
    "exact branch-head parity is now recorded for this packet",
    "landed `phase15-verified-master-head-provenance-sync`",
)
DATED_MODE_NOTE_MARKERS = (
    "`PHASE15_PROVENANCE_MODE=dated_master_readback`",
    "survey provenance refreshed against dated `master` readback marker `",
    "exact branch-head parity is not recorded for this packet",
    f"previously recorded verified head `{LEGACY_VERIFIED_HEAD}`",
    "landed `phase15-dated-readback-provenance-refresh`",
)

REQUIRED_REVIEW_PACKET_FIELDS = (
    "linux anchor path",
    "phase",
    "current status bucket",
    "requested decision bucket",
    "decision record ID",
    "owner",
    "rollback owner",
    "required approver set",
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
    "required approver set",
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
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
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
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_indefinite_c_blocker_evidence.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_readiness_gate.zig",
    "zigux/tests/phase15_build.zig",
)

REQUIRED_CURRENT_BOUNDED_LANE_MARKERS = (
    "scripts-root validator path",
    "workflow-backed replay path",
    "dedicated `make -C zigux phase15-test` route",
    "direct `zig build test --build-file zigux/tests/phase15_build.zig` route",
    "Linux-style `make -C zigux phase15-validate` route",
    "tests-root guidance path",
    "dedicated handoff-checker route",
)

REQUIRED_DOCS_README_MARKERS = (
    "Phase 15 notes",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`scripts/zigux/check-phase15-review-process-handoff.py`",
    "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
    "`zigux/tests/phase15_architecture_council_review_process.zig`",
    "`zigux/tests/phase15_build.zig`",
    "`make -C zigux phase15-validate`",
    "`make -C zigux phase15`",
    "no Architecture Council approval is recorded yet",
)

REQUIRED_REVIEW_CHECKLIST_MARKERS = (
    "if the change touches the shared Phase 15 governance packet",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    ".github/workflows/zigux-bootstrap.yml",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "make -C zigux phase15-validate",
    "zig build test --build-file zigux/tests/phase15_build.zig",
    "make -C zigux phase15",
    "if a freeze-map anchor is entering Architecture Council status review, are the decision record ID, lane owner, required approver set, rollback owner, validation gate summary, evidence archive path, latest blocker disposition, benchmark notes, replay command, rollback threshold, parity scorecard link or blocker record, indefinite-C policy link or non-applicability note, explicit non-goals, and written rationale explicit?",
    "if a freeze-map anchor is closing review with a stay-in-C outcome, are the retained discussion state, the current blocker, and reopen triggers explicit?",
)

REQUIRED_SCRIPT_README_MARKERS = (
    "Phase 15 flow",
    "phase15-architecture-council-review-process.md",
    "check-phase15-review-process-handoff.py",
    "phase15_architecture_council_review_process_manifest.json",
    "phase15_architecture_council_review_process.zig",
    "phase15_build.zig",
    "make -C zigux phase15",
)

REQUIRED_TESTS_README_MARKERS = (
    "keep the parked Phase 15 governance packet explicit in the tests root too",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_architecture_council_review_process.zig",
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

REQUIRED_HANDOFF_REPLAY_COMMANDS = (
    "make -C zigux phase15-validate",
    ".github/workflows/zigux-bootstrap.yml",
    "make -C zigux phase15-test",
    "zig build test --build-file zigux/tests/phase15_build.zig",
    "make -C zigux phase15",
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


def is_lower_hex_40(value: str) -> bool:
    return len(value) == 40 and all(ch in "0123456789abcdef" for ch in value)


def validate_provenance(note: str, manifest: dict, failures: list[str]) -> None:
    mode = manifest.get("surveyed_commit_mode")
    surveyed_commit = manifest.get("surveyed_commit")
    reason = manifest.get("surveyed_commit_mode_reason")

    if mode == "verified_master_head":
        if not isinstance(surveyed_commit, str) or not is_lower_hex_40(surveyed_commit):
            failures.append(f"manifest:surveyed_commit:{surveyed_commit}")
        if not isinstance(reason, str) or "exact verified master-head SHA" not in reason:
            failures.append(f"manifest:surveyed_commit_mode_reason:{reason}")
        expect_markers(note, VERIFIED_MODE_NOTE_MARKERS, "note", failures)
    elif mode == "dated_master_readback":
        if not isinstance(surveyed_commit, str) or not surveyed_commit.startswith(DATED_READBACK_PREFIX):
            failures.append(f"manifest:surveyed_commit:{surveyed_commit}")
        if not isinstance(reason, str) or "dated readback marker" not in reason or LEGACY_VERIFIED_HEAD not in reason:
            failures.append(f"manifest:surveyed_commit_mode_reason:{reason}")
        expect_markers(note, DATED_MODE_NOTE_MARKERS, "note", failures)
    else:
        failures.append(f"manifest:surveyed_commit_mode:{mode}")


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
    expect_markers(note, REQUIRED_PRODUCT_BOUNDARY_MARKERS, "note_boundary", failures)
    expect_markers(note, REQUIRED_GENERIC_NOTE_MARKERS, "note", failures)
    expect_markers(script_readme, REQUIRED_SCRIPT_README_MARKERS, "script_readme", failures)
    expect_markers(tests_readme, REQUIRED_TESTS_README_MARKERS, "tests_readme", failures)
    expect_markers(makefile, REQUIRED_MAKEFILE_MARKERS, "makefile", failures)
    expect_markers(workflow, REQUIRED_WORKFLOW_MARKERS, "workflow", failures)

    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        failures.append(f"manifest:lane_key:{manifest.get('lane_key')}")
    if manifest.get("roadmap_requirement") != EXPECTED_ROADMAP_REQUIREMENT:
        failures.append(f"manifest:roadmap_requirement:{manifest.get('roadmap_requirement')}")

    validate_provenance(note, manifest, failures)

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

    handoff = manifest.get("handoff")
    if not isinstance(handoff, dict):
        failures.append("manifest:handoff")
    else:
        replay_commands = handoff.get("replay_commands")
        if not isinstance(replay_commands, list):
            failures.append("manifest:handoff_replay_commands")
        else:
            for command in REQUIRED_HANDOFF_REPLAY_COMMANDS:
                if command not in replay_commands:
                    failures.append(f"manifest_handoff_replay:{command}")

    handoff_evidence = manifest.get("handoff_evidence")
    if not isinstance(handoff_evidence, dict):
        failures.append("manifest:handoff_evidence")
    else:
        current_repo_handoff = handoff_evidence.get("current_repo_handoff")
        if not isinstance(current_repo_handoff, str):
            failures.append("manifest:current_repo_handoff")
        else:
            expect_markers(current_repo_handoff, REQUIRED_CURRENT_REPO_HANDOFF_MARKERS, "manifest_handoff", failures)

        current_bounded_lane = handoff_evidence.get("current_bounded_lane")
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

    (root / DOCS_README_PATH).write_text("\n".join(("# docs", *REQUIRED_DOCS_README_MARKERS, "")), encoding="utf-8")
    (root / REVIEW_CHECKLIST_PATH).writeText if False else None
    (root / REVIEW_CHECKLIST_PATH).write_text("\n".join(("# checklist", *REQUIRED_REVIEW_CHECKLIST_MARKERS, "")), encoding="utf-8")
    (root / SCRIPT_README_PATH).write_text("\n".join(("# scripts", *REQUIRED_SCRIPT_README_MARKERS, "")), encoding="utf-8")
    (root / TESTS_README_PATH).write_text("\n".join(("# tests", *REQUIRED_TESTS_README_MARKERS, "")), encoding="utf-8")
    (root / MAKEFILE_PATH).write_text("\n".join((*REQUIRED_MAKEFILE_MARKERS, "")), encoding="utf-8")
    (root / WORKFLOW_PATH).write_text("\n".join((*REQUIRED_WORKFLOW_MARKERS, "")), encoding="utf-8")

    note = "\n".join((
        "# Phase 15 Architecture Council Review Process Survey",
        *REQUIRED_GENERIC_NOTE_MARKERS,
        *DATED_MODE_NOTE_MARKERS,
        PRODUCT_BOUNDARY_MARKER,
        *REQUIRED_PRODUCT_BOUNDARY_MARKERS,
        "workflow-backed replay anchor `.github/workflows/zigux-bootstrap.yml`",
        "dedicated `make -C zigux phase15-test` route",
        "",
    ))
    (root / NOTE_PATH).write_text(note, encoding="utf-8")

    manifest = {
        "lane_key": EXPECTED_LANE_KEY,
        "surveyed_commit": "current-master-readback-2026-05-09",
        "surveyed_commit_mode": "dated_master_readback",
        "surveyed_commit_mode_reason": f"Live compare-against-master showed the previously recorded verified head {LEGACY_VERIFIED_HEAD} now sits 2591 commits behind current master, so this parked review-process packet uses an explicit dated readback marker instead of stale exact-head parity.",
        "roadmap_requirement": EXPECTED_ROADMAP_REQUIREMENT,
        "required_review_packet_fields": list(REQUIRED_REVIEW_PACKET_FIELDS),
        "ownership_evidence_fields": list(REQUIRED_OWNERSHIP_FIELDS),
        "handoff": {"replay_commands": list(REQUIRED_HANDOFF_REPLAY_COMMANDS)},
        "handoff_evidence": {
            "current_repo_handoff": " ".join(REQUIRED_CURRENT_REPO_HANDOFF_MARKERS),
            "current_bounded_lane": " ".join(REQUIRED_CURRENT_BOUNDED_LANE_MARKERS),
        },
    }
    (root / MANIFEST_PATH).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


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
        manifest_path = root / MANIFEST_PATH
        original_note = note_path.read_text(encoding="utf-8")
        original_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        note_path.write_text(original_note.replace("`PHASE15_PROVENANCE_MODE=dated_master_readback`", "`PHASE15_PROVENANCE_MODE=verified_master_head`", 1), encoding="utf-8")
        expect_only(root, ["note:`PHASE15_PROVENANCE_MODE=dated_master_readback`"], "missing_dated_mode_marker")
        note_path.write_text(original_note, encoding="utf-8")
        case_count += 1

        bad = dict(original_manifest)
        bad["surveyed_commit_mode"] = "invalid_mode"
        manifest_path.write_text(json.dumps(bad, indent=2) + "\n", encoding="utf-8")
        expect_only(root, ["manifest:surveyed_commit_mode:invalid_mode"], "invalid_mode")
        manifest_path.write_text(json.dumps(original_manifest, indent=2) + "\n", encoding="utf-8")
        case_count += 1

        bad = dict(original_manifest)
        bad["surveyed_commit"] = "not-a-dated-marker"
        manifest_path.write_text(json.dumps(bad, indent=2) + "\n", encoding="utf-8")
        expect_only(root, ["manifest:surveyed_commit:not-a-dated-marker"], "bad_dated_commit")
        manifest_path.write_text(json.dumps(original_manifest, indent=2) + "\n", encoding="utf-8")
        case_count += 1

        bad = dict(original_manifest)
        bad["surveyed_commit_mode_reason"] = "reason without dated readback marker"
        manifest_path.write_text(json.dumps(bad, indent=2) + "\n", encoding="utf-8")
        expect_only(root, ["manifest:surveyed_commit_mode_reason:reason without dated readback marker"], "bad_reason")
        manifest_path.write_text(json.dumps(original_manifest, indent=2) + "\n", encoding="utf-8")
        case_count += 1

        note_path.write_text(original_note.replace("workflow-backed replay anchor `.github/workflows/zigux-bootstrap.yml`", "workflow-backed replay anchor `.github/workflows/missing.yml`"), encoding="utf-8")
        expect_only(root, ["note:workflow-backed replay anchor `.github/workflows/zigux-bootstrap.yml`"], "missing_workflow_anchor")
        note_path.write_text(original_note, encoding="utf-8")
        case_count += 1

        bad = dict(original_manifest)
        bad["required_review_packet_fields"] = [x for x in original_manifest["required_review_packet_fields"] if x != "required approver set"]
        manifest_path.write_text(json.dumps(bad, indent=2) + "\n", encoding="utf-8")
        expect_only(root, ["manifest_required_review_packet_fields:required approver set"], "missing_review_field")
        manifest_path.write_text(json.dumps(original_manifest, indent=2) + "\n", encoding="utf-8")
        case_count += 1

        tests_readme_path = root / TESTS_README_PATH
        original_tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(original_tests_readme.replace("zigux/tests/phase15_architecture_council_review_process.zig", "zigux/tests/missing.zig", 1), encoding="utf-8")
        expect_only(root, ["tests_readme:zigux/tests/phase15_architecture_council_review_process.zig"], "missing_tests_root_marker")
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")
        case_count += 1

        bad = dict(original_manifest)
        handoff = dict(original_manifest["handoff"])
        handoff["replay_commands"] = [x for x in original_manifest["handoff"]["replay_commands"] if x != "make -C zigux phase15-test"]
        bad["handoff"] = handoff
        manifest_path.write_text(json.dumps(bad, indent=2) + "\n", encoding="utf-8")
        expect_only(root, ["manifest_handoff_replay:make -C zigux phase15-test"], "missing_handoff_replay")
        manifest_path.write_text(json.dumps(original_manifest, indent=2) + "\n", encoding="utf-8")
        case_count += 1

        note_path.write_text(
            original_note.replace("  - `Documentation/zigux/phase15-handoff-next-steps-survey.md`\n", "", 1),
            encoding="utf-8",
        )
        expect_only(
            root,
            ["note_boundary:  - `Documentation/zigux/phase15-handoff-next-steps-survey.md`"],
            "missing_product_boundary_handoff_note",
        )
        note_path.write_text(original_note, encoding="utf-8")
        case_count += 1

        note_path.write_text(
            original_note.replace("  - `scripts/zigux/check-phase15-scripts-readme-alignment.py`\n", "", 1),
            encoding="utf-8",
        )
        expect_only(
            root,
            ["note_boundary:  - `scripts/zigux/check-phase15-scripts-readme-alignment.py`"],
            "missing_product_boundary_scripts_alignment_checker",
        )
        note_path.write_text(original_note, encoding="utf-8")
        case_count += 1

        note_path.write_text(
            original_note.replace("  - `zigux/tests/phase15_indefinite_c_blocker_evidence.zig`\n", "", 1),
            encoding="utf-8",
        )
        expect_only(
            root,
            ["note_boundary:  - `zigux/tests/phase15_indefinite_c_blocker_evidence.zig`"],
            "missing_product_boundary_blocker_evidence",
        )
        note_path.write_text(original_note, encoding="utf-8")
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
