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

SELF_REFERENCE_MARKER = "Documentation/zigux/phase15-architecture-council-review-process.md"
PRODUCT_BOUNDARY_MARKER = (
    "product boundary:\n"
    "  - `Documentation/zigux/freeze-map.md`"
)
REQUIRED_MANIFEST_BOUNDARY_MARKERS = [
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
]
REQUIRED_REVIEW_PACKET_FIELD_MARKERS = [
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
    "retained discussion state",
    "reopen triggers",
    "parity scorecard link or blocker record",
    "explicit non-goals",
    "written rationale",
]
REQUIRED_OWNERSHIP_EVIDENCE_FIELDS = [
    "phase",
    "current status bucket",
    "owner",
    "rollback owner",
    "validation gate summary",
    "evidence archive path",
    "latest blocker disposition",
    "benchmark notes",
    "replay command",
    "retained discussion state",
    "reopen triggers",
    "parity scorecard link or blocker record",
]
REQUIRED_CURRENT_APPROVAL_POSTURE_MARKERS = [
    "current review-process evidence is limited to named `phase`",
    "`current status bucket`",
    "`validation gate summary`",
    "landed `phase15-roadmap-minimum-field-sync`",
]

OPTIONAL_LANE_ROUTE_MARKERS = [
    "scripts-root validator path",
    "Linux-style `make -C zigux phase15-validate` route",
    "tests-root guidance path",
    "dedicated handoff-checker route",
]

REQUIRED_DOCS_README_MARKERS = [
    "Phase 15 notes",
    "`Documentation/zigux/freeze-map.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
    "`zigux/tests/phase15_freeze_map_governance.zig`",
    "`zigux/tests/phase15_parity_scorecard.zig`",
    "`zigux/tests/phase15_architecture_council_review_process.zig`",
    "`zigux/tests/phase15_indefinite_c_policy.json`",
    "`zigux/tests/phase15_indefinite_c_policy.zig`",
    "`zigux/tests/phase15_build.zig`",
    "`zigux/Makefile`",
    "`make -C zigux phase15`",
    "no Architecture Council approval is recorded yet",
]

REQUIRED_REVIEW_CHECKLIST_MARKERS = [
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
]

REQUIRED_SCRIPT_README_MARKERS = [
    "Phase 15 flow",
    "phase15-freeze-map-governance.md",
    "phase15-architecture-council-review-process.md",
    "phase15-parity-scorecard.md",
    "phase15-indefinite-c-policy.md",
    "check-phase15-review-process-handoff.py",
    "phase15_architecture_council_review_process_manifest.json",
    "phase15_freeze_map_governance.zig",
    "phase15_parity_scorecard.zig",
    "phase15_architecture_council_review_process.zig",
    "phase15_indefinite_c_policy.json",
    "phase15_indefinite_c_policy.zig",
    "phase15_build.zig",
    "make -C zigux phase15",
]

EXACT_ONCE_SCRIPT_README_MARKERS = [
    "Phase 15 flow",
]

REQUIRED_TESTS_README_MARKERS = [
    "keep the parked Phase 15 governance packet explicit in the tests root too",
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
    "zigux/Makefile",
    "zig build test --build-file zigux/tests/phase15_build.zig",
    "make -C zigux phase15",
]

REQUIRED_MAKEFILE_MARKERS = [
    "PHONY += phase15-validate phase15-test phase15",
    "phase15-validate:",
    "scripts/zigux/check-phase15-review-process-handoff.py --self-test",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "phase15-test:",
    "zigux/tests/phase15_build.zig",
]

EXACT_ONCE_MAKEFILE_MARKERS = [
    "PHONY += phase15-validate phase15-test phase15",
    "phase15-validate:",
    "phase15-test:",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def load_json(root: Path, rel_path: str) -> dict:
    return json.loads(read_text(root, rel_path))


def expect_exact_once(text: str, marker: str, label: str, failures: list[str]) -> None:
    count = text.count(marker)
    if count != 1:
        failures.append(f"{label}:{marker}:count={count}")


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    required_paths = [
        DOCS_README_PATH,
        REVIEW_CHECKLIST_PATH,
        NOTE_PATH,
        MANIFEST_PATH,
        SCRIPT_README_PATH,
        TESTS_README_PATH,
        MAKEFILE_PATH,
    ]
    for rel_path in required_paths:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
            return failures

    docs_readme = read_text(root, DOCS_README_PATH)
    review_checklist = read_text(root, REVIEW_CHECKLIST_PATH)
    note = read_text(root, NOTE_PATH)
    manifest = load_json(root, MANIFEST_PATH)
    script_readme = read_text(root, SCRIPT_README_PATH)
    tests_readme = read_text(root, TESTS_README_PATH)
    makefile = read_text(root, MAKEFILE_PATH)

    for marker in REQUIRED_DOCS_README_MARKERS:
        if marker not in docs_readme:
            failures.append(f"docs_readme:{marker}")

    for marker in REQUIRED_REVIEW_CHECKLIST_MARKERS:
        if marker not in review_checklist:
            failures.append(f"review_checklist:{marker}")

    expect_exact_once(note, SELF_REFERENCE_MARKER, "note_self_reference", failures)
    if PRODUCT_BOUNDARY_MARKER not in note:
        failures.append("note:product_boundary_self_reference")
    for marker in REQUIRED_CURRENT_APPROVAL_POSTURE_MARKERS:
        if marker not in note:
            failures.append(f"note_current_approval_posture:{marker}")

    for marker in REQUIRED_SCRIPT_README_MARKERS:
        if marker not in script_readme:
            failures.append(f"script_readme:{marker}")
    for marker in EXACT_ONCE_SCRIPT_README_MARKERS:
        expect_exact_once(script_readme, marker, "script_readme_exact_once", failures)

    for marker in REQUIRED_TESTS_README_MARKERS:
        if marker not in tests_readme:
            failures.append(f"tests_readme:{marker}")

    for marker in REQUIRED_MAKEFILE_MARKERS:
        if marker not in makefile:
            failures.append(f"makefile:{marker}")
    for marker in EXACT_ONCE_MAKEFILE_MARKERS:
        expect_exact_once(makefile, marker, "makefile_exact_once", failures)

    required_review_packet_fields = manifest.get("required_review_packet_fields")
    if required_review_packet_fields is None:
        failures.append("manifest:required_review_packet_fields:missing")
    elif not isinstance(required_review_packet_fields, list):
        failures.append("manifest:required_review_packet_fields:not_list")
    else:
        for marker in REQUIRED_REVIEW_PACKET_FIELD_MARKERS:
            if marker not in required_review_packet_fields:
                failures.append(f"manifest_required_review_packet_fields:{marker}")

    ownership_evidence_fields = manifest.get("ownership_evidence_fields")
    if ownership_evidence_fields is None:
        failures.append("manifest:ownership_evidence_fields:missing")
    elif not isinstance(ownership_evidence_fields, list):
        failures.append("manifest:ownership_evidence_fields:not_list")
    else:
        for marker in REQUIRED_OWNERSHIP_EVIDENCE_FIELDS:
            if marker not in ownership_evidence_fields:
                failures.append(f"manifest_ownership_evidence_fields:{marker}")

    handoff = manifest.get("handoff_evidence")
    if handoff is None:
        return failures
    if not isinstance(handoff, dict):
        failures.append("manifest:handoff_evidence:not_object")
        return failures

    current_repo_handoff = handoff.get("current_repo_handoff")
    if current_repo_handoff is not None:
        if not isinstance(current_repo_handoff, str):
            failures.append("manifest:handoff_evidence.current_repo_handoff:not_string")
        else:
            for marker in REQUIRED_MANIFEST_BOUNDARY_MARKERS:
                if marker not in current_repo_handoff:
                    failures.append(f"manifest_handoff:{marker}")

    current_bounded_lane = handoff.get("current_bounded_lane")
    if current_bounded_lane is not None:
        if not isinstance(current_bounded_lane, str):
            failures.append("manifest:handoff_evidence.current_bounded_lane:not_string")
        else:
            for marker in OPTIONAL_LANE_ROUTE_MARKERS:
                if marker not in current_bounded_lane:
                    failures.append(f"manifest_lane:{marker}")

    return failures


def write_fixture_tree(root: Path) -> None:
    (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
    (root / "zigux/tests").mkdir(parents=True, exist_ok=True)
    (root / "scripts/zigux").mkdir(parents=True, exist_ok=True)
    (root / "zigux").mkdir(parents=True, exist_ok=True)

    docs_readme = """# Documentation/zigux
Phase 15 notes
- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `zigux/tests/phase15_architecture_council_review_process_manifest.json`
- `zigux/tests/phase15_freeze_map_governance.zig`
- `zigux/tests/phase15_parity_scorecard.zig`
- `zigux/tests/phase15_architecture_council_review_process.zig`
- `zigux/tests/phase15_indefinite_c_policy.json`
- `zigux/tests/phase15_indefinite_c_policy.zig`
- `zigux/tests/phase15_build.zig`
- `zigux/Makefile`
- `make -C zigux phase15`
- no Architecture Council approval is recorded yet
"""
    (root / DOCS_README_PATH).write_text(docs_readme, encoding="utf-8")

    review_checklist = """# Review Checklist
if the change touches the shared Phase 15 governance packet
- Documentation/zigux/freeze-map.md
- Documentation/zigux/phase15-freeze-map-governance.md
- Documentation/zigux/phase15-architecture-council-review-process.md
- Documentation/zigux/phase15-parity-scorecard.md
- Documentation/zigux/phase15-indefinite-c-policy.md
- Documentation/zigux/review-checklist.md
- scripts/zigux/check-phase15-review-process-handoff.py
- zigux/tests/phase15_architecture_council_review_process_manifest.json
- zigux/tests/phase15_freeze_map_governance.zig
- zigux/tests/phase15_parity_scorecard.zig
- zigux/tests/phase15_architecture_council_review_process.zig
- zigux/tests/phase15_indefinite_c_policy.json
- zigux/tests/phase15_indefinite_c_policy.zig
- zigux/tests/phase15_build.zig
- make -C zigux phase15
"""
    (root / REVIEW_CHECKLIST_PATH).write_text(review_checklist, encoding="utf-8")

    note = """# Phase 15 Architecture Council Review Process Survey
## Status
- product boundary:
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/phase15-architecture-council-review-process.md`
  - `Documentation/zigux/phase15-parity-scorecard.md`

## Current Approval Posture
- current review-process evidence is limited to named `phase`, `current status bucket`, `owner`, `rollback owner`, `validation gate summary`, evidence archive, blocker-disposition, benchmark-notes, replay-command, retained-discussion-state, and reopen-trigger records

## Recorded Gaps
- landed `phase15-roadmap-minimum-field-sync`
"""
    (root / NOTE_PATH).write_text(note, encoding="utf-8")

    manifest = {
        "lane_key": "P15-L14",
        "phase": "Phase 15",
        "ownership_evidence_fields": REQUIRED_OWNERSHIP_EVIDENCE_FIELDS,
        "required_review_packet_fields": REQUIRED_REVIEW_PACKET_FIELD_MARKERS,
        "handoff_evidence": {
            "current_repo_handoff": (
                "The current repo handoff explicitly names "
                "Documentation/zigux/freeze-map.md, "
                "Documentation/zigux/phase15-freeze-map-governance.md, "
                "Documentation/zigux/phase15-architecture-council-review-process.md, "
                "Documentation/zigux/phase15-parity-scorecard.md, "
                "Documentation/zigux/phase15-indefinite-c-policy.md, "
                "Documentation/zigux/review-checklist.md, "
                "scripts/zigux/check-phase15-review-process-handoff.py, "
                "zigux/tests/phase15_architecture_council_review_process_manifest.json, "
                "zigux/tests/phase15_freeze_map_governance.zig, "
                "zigux/tests/phase15_parity_scorecard.zig, "
                "zigux/tests/phase15_architecture_council_review_process.zig, "
                "zigux/tests/phase15_indefinite_c_policy.json, "
                "zigux/tests/phase15_indefinite_c_policy.zig, "
                "and zigux/tests/phase15_build.zig as the parked governance packet boundary."
            ),
            "current_bounded_lane": (
                "The parked Architecture Council packet stays aligned with its "
                "scripts-root validator path, its Linux-style `make -C zigux phase15-validate` route, its tests-root guidance path, and its "
                "dedicated handoff-checker route."
            ),
        },
    }
    (root / MANIFEST_PATH).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    script_readme = """# scripts/zigux
Phase 15 flow
- the current shared Phase 15 governance surface on `master` is `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase15-review-process-handoff.py`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_freeze_map_governance.zig`, `zigux/tests/phase15_parity_scorecard.zig`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, and `zigux/tests/phase15_build.zig`.
- `check-phase15-review-process-handoff.py` keeps the dedicated review-process note and its manifest-backed handoff evidence aligned around the self-reference, product-boundary, and parked-route markers that keep the Architecture Council packet reviewable without inventing a broader governance surface.
- `zig build test --build-file zigux/tests/phase15_build.zig` and `make -C zigux phase15` rerun the parked freeze-map governance, Architecture Council review-process, parity-scorecard, and dedicated indefinite-C policy packet without implying any new approval claim for a freeze-map anchor.
"""
    (root / SCRIPT_README_PATH).write_text(script_readme, encoding="utf-8")

    tests_readme = """# zigux/tests
keep the parked Phase 15 governance packet explicit in the tests root too
- Documentation/zigux/freeze-map.md
- Documentation/zigux/phase15-freeze-map-governance.md
- Documentation/zigux/phase15-architecture-council-review-process.md
- Documentation/zigux/phase15-parity-scorecard.md
- Documentation/zigux/phase15-indefinite-c-policy.md
- Documentation/zigux/review-checklist.md
- scripts/zigux/check-phase15-review-process-handoff.py
- zigux/tests/phase15_architecture_council_review_process_manifest.json
- zigux/tests/phase15_freeze_map_governance.zig
- zigux/tests/phase15_parity_scorecard.zig
- zigux/tests/phase15_architecture_council_review_process.zig
- zigux/tests/phase15_indefinite_c_policy.json
- zigux/tests/phase15_indefinite_c_policy.zig
- zigux/Makefile
- zig build test --build-file zigux/tests/phase15_build.zig
- make -C zigux phase15
"""
    (root / TESTS_README_PATH).write_text(tests_readme, encoding="utf-8")

    makefile = """PHONY += phase15-validate phase15-test phase15
phase15-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py
phase15-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase15_build.zig
phase15: phase15-validate phase15-test
"""
    (root / MAKEFILE_PATH).write_text(makefile, encoding="utf-8")


def expect_failure(root: Path, expected: str, label: str) -> None:
    failures = validate(root)
    if expected not in failures:
        actual = ",".join(failures) if failures else "none"
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_handoff_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture_tree(tmp_root)
        baseline = validate(tmp_root)
        if baseline:
            raise SystemExit("baseline_failed:" + ",".join(baseline))

        note_path = tmp_root / NOTE_PATH
        original_note = note_path.read_text(encoding="utf-8")
        note_path.write_text(
            original_note.replace(
                "`Documentation/zigux/phase15-architecture-council-review-process.md`",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "note_self_reference:Documentation/zigux/phase15-architecture-council-review-process.md:count=0",
            "missing_note_self_reference",
        )

        note_path.write_text(original_note, encoding="utf-8")
        note_path.write_text(
            original_note.replace(
                "product boundary:\n  - `Documentation/zigux/freeze-map.md`",
                "product boundary:",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "note:product_boundary_self_reference",
            "missing_product_boundary_marker",
        )

        note_path.write_text(original_note, encoding="utf-8")
        note_path.write_text(
            original_note.replace(
                "`validation gate summary`",
                "`validation summary`",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "note_current_approval_posture:`validation gate summary`",
            "missing_note_current_approval_posture_marker",
        )

        note_path.write_text(original_note, encoding="utf-8")
        manifest_path = tmp_root / MANIFEST_PATH
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["required_review_packet_fields"] = [
            field for field in manifest["required_review_packet_fields"] if field != "rollback owner"
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            tmp_root,
            "manifest_required_review_packet_fields:rollback owner",
            "missing_required_review_packet_field",
        )

        write_fixture_tree(tmp_root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["ownership_evidence_fields"] = [
            field for field in manifest["ownership_evidence_fields"] if field != "phase"
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            tmp_root,
            "manifest_ownership_evidence_fields:phase",
            "missing_ownership_evidence_field",
        )

        write_fixture_tree(tmp_root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["handoff_evidence"]["current_repo_handoff"] = manifest["handoff_evidence"][
            "current_repo_handoff"
        ].replace("zigux/tests/phase15_build.zig", "zigux/tests/phase15_phase_build.zig", 1)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            tmp_root,
            "manifest_handoff:zigux/tests/phase15_build.zig",
            "missing_manifest_boundary_marker",
        )

        write_fixture_tree(tmp_root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["handoff_evidence"]["current_bounded_lane"] = "The parked Architecture Council packet stays aligned with its Linux-style `make -C zigux phase15-validate` route, its tests-root guidance path, and its dedicated handoff-checker route."
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            tmp_root,
            "manifest_lane:scripts-root validator path",
            "missing_manifest_lane_route_marker",
        )

        write_fixture_tree(tmp_root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["handoff_evidence"]["current_bounded_lane"] = "The parked Architecture Council packet stays aligned with its scripts-root validator path, its tests-root guidance path, and its dedicated handoff-checker route."
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            tmp_root,
            "manifest_lane:Linux-style `make -C zigux phase15-validate` route",
            "missing_manifest_validate_route_marker",
        )

        write_fixture_tree(tmp_root)
        script_readme_path = tmp_root / SCRIPT_README_PATH
        script_readme = script_readme_path.read_text(encoding="utf-8")
        script_readme_path.write_text(
            script_readme.replace("check-phase15-review-process-handoff.py", "", 1),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "script_readme:check-phase15-review-process-handoff.py",
            "missing_script_readme_checker_marker",
        )

        write_fixture_tree(tmp_root)
        docs_readme_path = tmp_root / DOCS_README_PATH
        docs_readme = docs_readme_path.read_text(encoding="utf-8")
        docs_readme_path.write_text(
            docs_readme.replace("no Architecture Council approval is recorded yet", "", 1),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "docs_readme:no Architecture Council approval is recorded yet",
            "missing_docs_readme_approval_marker",
        )

        write_fixture_tree(tmp_root)
        docs_readme = docs_readme_path.read_text(encoding="utf-8")
        docs_readme_path.write_text(
            docs_readme.replace("`zigux/tests/phase15_architecture_council_review_process_manifest.json`\n", "", 1),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "docs_readme:`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
            "missing_docs_readme_manifest_marker",
        )

        write_fixture_tree(tmp_root)
        docs_readme = docs_readme_path.read_text(encoding="utf-8")
        docs_readme_path.write_text(
            docs_readme.replace("`zigux/tests/phase15_freeze_map_governance.zig`\n", "", 1),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "docs_readme:`zigux/tests/phase15_freeze_map_governance.zig`",
            "missing_docs_readme_freeze_map_governance_replay_marker",
        )

        write_fixture_tree(tmp_root)
        review_checklist_path = tmp_root / REVIEW_CHECKLIST_PATH
        review_checklist = review_checklist_path.read_text(encoding="utf-8")
        review_checklist_path.write_text(
            review_checklist.replace("scripts/zigux/check-phase15-review-process-handoff.py", "", 1),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "review_checklist:scripts/zigux/check-phase15-review-process-handoff.py",
            "missing_review_checklist_checker_marker",
        )

        write_fixture_tree(tmp_root)
        tests_readme_path = tmp_root / TESTS_README_PATH
        tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            tests_readme.replace("zig build test --build-file zigux/tests/phase15_build.zig", "", 1),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "tests_readme:zig build test --build-file zigux/tests/phase15_build.zig",
            "missing_tests_readme_build_marker",
        )

        write_fixture_tree(tmp_root)
        tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            tests_readme.replace("zigux/tests/phase15_architecture_council_review_process_manifest.json\n", "", 1),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "tests_readme:zigux/tests/phase15_architecture_council_review_process_manifest.json",
            "missing_tests_readme_manifest_marker",
        )

        write_fixture_tree(tmp_root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["handoff_evidence"]["current_repo_handoff"] = manifest["handoff_evidence"][
            "current_repo_handoff"
        ].replace("zigux/tests/phase15_parity_scorecard.zig", "zigux/tests/phase15_scorecard.zig", 1)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            tmp_root,
            "manifest_handoff:zigux/tests/phase15_parity_scorecard.zig",
            "missing_manifest_parity_scorecard_replay_marker",
        )

        write_fixture_tree(tmp_root)
        makefile_path = tmp_root / MAKEFILE_PATH
        makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            makefile.replace(
                "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "makefile:scripts/zigux/check-phase15-review-process-handoff.py --self-test",
            "missing_makefile_self_test_marker",
        )

    print("PHASE15_REVIEW_PROCESS_HANDOFF_SELF_TEST=pass")
    print("PHASE15_REVIEW_PROCESS_HANDOFF_SELF_TEST_CASE_COUNT=18")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 15 Architecture Council review-process handoff surfaces."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the current directory.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the fixture-backed self-test.",
    )
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
        f"{2 + len(REQUIRED_MANIFEST_BOUNDARY_MARKERS) + len(REQUIRED_REVIEW_PACKET_FIELD_MARKERS) + len(REQUIRED_OWNERSHIP_EVIDENCE_FIELDS) + len(REQUIRED_CURRENT_APPROVAL_POSTURE_MARKERS) + len(OPTIONAL_LANE_ROUTE_MARKERS) + len(REQUIRED_DOCS_README_MARKERS) + len(REQUIRED_REVIEW_CHECKLIST_MARKERS) + len(REQUIRED_SCRIPT_README_MARKERS) + len(EXACT_ONCE_SCRIPT_README_MARKERS) + len(REQUIRED_TESTS_README_MARKERS) + len(REQUIRED_MAKEFILE_MARKERS) + len(EXACT_ONCE_MAKEFILE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
