#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

REVIEW_PROCESS_PATH = Path("Documentation/zigux/phase15-architecture-council-review-process.md")
DECISION_RECORD_TEMPLATE_PATH = Path(
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md"
)
INDEFINITE_C_POLICY_PATH = Path("Documentation/zigux/phase15-indefinite-c-policy.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
SHARED_GAP_NOTE_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
MANIFEST_PATH = Path("zigux/tests/phase15_architecture_council_review_process_manifest.json")
TEST_PATH = Path("zigux/tests/phase15_architecture_council_review_process.zig")
BUILD_GATE_PATH = Path("zigux/tests/phase15_architecture_council_review_process_build.zig")
CURRENT_READBACK_MARKER = "current-master-readback-2026-05-19"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _marker_to_repo_path(marker: str) -> Path | None:
    if marker.startswith("`") and marker.endswith("`") and "/" in marker:
        return Path(marker.strip("`"))
    return None


def _line_containing(text: str, marker: str) -> str | None:
    for line in text.splitlines():
        if marker in line:
            return line
    return None


def collect_failures(root: Path) -> list[str]:
    review_process = _read_text(root / REVIEW_PROCESS_PATH)
    decision_record_template = _read_text(root / DECISION_RECORD_TEMPLATE_PATH)
    indefinite_c_policy = _read_text(root / INDEFINITE_C_POLICY_PATH)
    review_checklist = _read_text(root / REVIEW_CHECKLIST_PATH)
    handoff_note = _read_text(root / HANDOFF_NOTE_PATH)
    gap_note = _read_text(root / SHARED_GAP_NOTE_PATH)
    manifest = _read_manifest(root / MANIFEST_PATH)

    failures: list[str] = []

    if manifest["surveyed_commit"] not in review_process:
        failures.append("review-process note is missing the manifest surveyed_commit marker")

    if manifest["decision_record_template"] not in review_process:
        failures.append("review-process note is missing the decision-record template path")

    if manifest["indefinite_c_policy_note"] not in review_process:
        failures.append("review-process note is missing the indefinite-C policy companion path")

    build_gate = manifest.get("build_gate")
    if build_gate is None:
        failures.append("review-process manifest is missing build_gate")
        build_gate_path = BUILD_GATE_PATH
    else:
        build_gate_path = Path(build_gate)
        if build_gate not in review_process:
            failures.append("review-process note is missing the focused build-file replay path")

    if manifest["decision_record_template"] not in handoff_note:
        failures.append("handoff note is missing the decision-record template path")

    if manifest["review_checklist_boundary_rule"] not in review_process:
        failures.append("review-process note is missing the review-checklist boundary rule")

    for marker in (
        "PHASE15_STATUS=architecture_council_review_process_landed",
        "PHASE15_LANE_KEY=P15-L08",
        "PHASE15_PROVENANCE_MODE=dated_master_readback",
        "`scripts/zigux/check-phase15-review-process-handoff.py`",
        "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
        "`zigux/tests/phase15_architecture_council_review_process.zig`",
    ):
        if marker not in review_process:
            failures.append(f"review-process note is missing required marker: {marker}")

    for field in manifest["required_review_fields"]:
        if field not in review_process:
            failures.append(f"review-process note is missing required review field: {field}")
        if field not in decision_record_template:
            failures.append(f"decision-record template is missing required review field: {field}")

    checklist_entry_prompt = _line_containing(
        review_checklist, manifest["review_checklist_entry_prompt"]
    )
    if checklist_entry_prompt is None:
        failures.append(
            "review checklist is missing the Phase 15 Architecture Council entry-review prompt"
        )
    else:
        checklist_expected_markers = (
            manifest["review_process_note"],
            manifest["decision_record_template"],
            "owners of the exact Architecture Council field inventory",
            "stay-in-C closeout record",
            "reopen-evidence details",
        )
        for marker in checklist_expected_markers:
            if marker not in checklist_entry_prompt:
                failures.append(
                    f"review checklist entry prompt is missing required boundary marker: {marker}"
                )

    for field in manifest["stay_in_c_closeout_fields"]:
        if field not in review_process:
            failures.append(f"review-process note is missing stay-in-C closeout field: {field}")
        if field not in decision_record_template:
            failures.append(f"decision-record template is missing stay-in-C closeout field: {field}")

    for field in manifest["reopen_evidence_fields"]:
        if field not in review_process:
            failures.append(f"review-process note is missing reopen-evidence field: {field}")
        if field not in decision_record_template:
            failures.append(f"decision-record template is missing reopen-evidence field: {field}")

    for marker in manifest["indefinite_c_policy_required_markers"]:
        if marker not in indefinite_c_policy:
            failures.append(f"indefinite-C policy note is missing required marker: {marker}")

    for marker in manifest["decision_record_template_required_markers"]:
        if marker not in decision_record_template:
            failures.append(f"decision-record template is missing required marker: {marker}")

    for marker in manifest["handoff_required_markers"]:
        if marker not in handoff_note:
            failures.append(f"handoff note is missing required marker: {marker}")

    for marker in manifest["shared_gap_expected_present_paths"]:
        if marker not in gap_note:
            failures.append(f"shared-summary gap note is missing newly landed path: {marker}")
        repo_path = _marker_to_repo_path(marker)
        if repo_path is not None and not (root / repo_path).exists():
            failures.append(f"shared-summary gap note claims materialized path is missing from repo: {marker}")

    for marker in manifest["shared_gap_expected_missing_paths"]:
        if marker not in gap_note:
            failures.append(f"shared-summary gap note is missing still-blocked path: {marker}")
        repo_path = _marker_to_repo_path(marker)
        if repo_path is not None and (root / repo_path).exists():
            failures.append(f"shared-summary gap note still frames shipped path as missing gap: {marker}")

    if not (root / TEST_PATH).exists():
        failures.append(
            "focused review-process Zig replay is missing from repo: "
            "`zigux/tests/phase15_architecture_council_review_process.zig`"
        )

    if not (root / build_gate_path).exists():
        failures.append(
            "focused review-process build-file replay is missing from repo: "
            f"`{build_gate_path.as_posix()}`"
        )

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_manifest() -> str:
    return json.dumps(
        {
            "lane_key": "P15-L08",
            "phase": "Phase 15",
            "surveyed_commit": CURRENT_READBACK_MARKER,
            "surveyed_commit_mode": "dated_master_readback",
            "review_process_note": "Documentation/zigux/phase15-architecture-council-review-process.md",
            "decision_record_template": "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
            "indefinite_c_policy_note": "Documentation/zigux/phase15-indefinite-c-policy.md",
            "handoff_note": "Documentation/zigux/phase15-handoff-next-steps-survey.md",
            "shared_summary_gap_note": "Documentation/zigux/phase15-shared-summary-gap.md",
            "checker": "scripts/zigux/check-phase15-review-process-handoff.py",
            "build_gate": "zigux/tests/phase15_architecture_council_review_process_build.zig",
            "review_checklist_entry_prompt": "if a freeze-map anchor is entering Architecture Council status review",
            "review_checklist_boundary_rule": (
                "`Documentation/zigux/review-checklist.md` keeps the shared entry-review "
                "and closeout prompts explicit, but the exact Architecture Council field "
                "inventory stays owned by this note and "
                "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`"
            ),
            "required_review_fields": [
                "exact Linux anchor path",
                "roadmap phase",
                "decision record ID",
                "lane owner",
                "current status bucket",
                "requested decision bucket",
                "required approver set",
                "rollback owner",
                "validation gate summary",
                "evidence archive path",
                "latest blocker disposition",
                "benchmark notes",
                "replay command",
                "rollback threshold",
                "automatic return-to-blocked trigger",
                "`retired_from_active_discussion` state",
                "reopen triggers",
                "trigger-specific evidence refresh",
                "parity scorecard link or blocker record",
                "indefinite-C policy link or explicit non-applicability note",
                "explicit non-goals",
                "written rationale",
            ],
            "stay_in_c_closeout_fields": [
                "the retained `freeze_in_c` decision",
                "the current blocker",
                "the required approver set",
                "`retired_from_active_discussion` state",
                "the automatic return-to-blocked trigger",
                "the reopen triggers",
                "the trigger-specific evidence refresh",
                "the evidence archive path that will be refreshed before any later reopen request",
            ],
            "reopen_evidence_fields": [
                "the exact reopen trigger being exercised",
                "refreshed evidence by path",
                "the blocker disposition being challenged",
                "the narrower seam or policy change that makes the new review safe to consider",
            ],
            "indefinite_c_policy_required_markers": [
                "required approver set",
                "automatic return-to-blocked trigger",
                "trigger-specific evidence refresh",
                "parity scorecard link or blocker record",
            ],
            "decision_record_template_required_markers": [
                "`PHASE15_PROVENANCE_MODE=dated_master_readback`",
                "`SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD`",
                "exact-head provenance exception note:",
                "Prefer the dated master readback form for parked governance and stay-in-C review packets.",
                "Only record an exact head when the linked review needs it to anchor a named published decision",
            ],
            "handoff_required_markers": [
                "`Documentation/zigux/review-checklist.md`",
                "`Documentation/zigux/README.md`",
                "`Documentation/zigux/phase15-architecture-council-review-process.md`",
                "`Documentation/zigux/phase15-indefinite-c-policy.md`",
                "`Documentation/zigux/phase15-shared-summary-gap.md`",
                "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
                "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
                "`zigux/tests/phase15_architecture_council_review_process_build.zig`",
                "`zigux/tests/phase15_handoff_next_steps_manifest.json`",
                "`scripts/zigux/check-phase15-review-process-handoff.py`",
                "`scripts/zigux/check-phase15-tests-readme-alignment.py`",
                "`scripts/zigux/check-phase15-handoff-note-alignment.py`",
                "one focused review-process checker, one focused tests-readme checker, the shared-summary gap checker, and the focused handoff-note checker",
            ],
            "shared_gap_expected_present_paths": [
                "`Documentation/zigux/phase15-parity-scorecard-survey.md`",
                "`Documentation/zigux/phase15-readiness-gate-survey.md`",
                "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
                "`scripts/zigux/check-phase15-scripts-readme-alignment.py`",
                "`scripts/zigux/check-phase15-tests-readme-alignment.py`",
                "`zigux/tests/phase15_freeze_map_governance.zig`",
                "`zigux/tests/phase15_parity_scorecard.zig`",
                "`zigux/tests/phase15_indefinite_c_policy.json`",
                "`zigux/tests/phase15_indefinite_c_policy.zig`",
                "`zigux/tests/phase15_architecture_council_review_process.zig`",
                "`zigux/tests/phase15_architecture_council_review_process_build.zig`",
                "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
                "`zigux/tests/phase15_handoff_next_steps_manifest.json`",
                "`scripts/zigux/check-phase15-review-process-handoff.py`",
                "`scripts/zigux/check-phase15-handoff-note-alignment.py`",
            ],
            "shared_gap_expected_missing_paths": [
                "`scripts/zigux/validate-phase15.py`",
                "`zigux/tests/phase15_build.zig`",
                "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
            ],
        },
        indent=2,
    ) + "\n"


def _sample_review_process() -> str:
    manifest = json.loads(_sample_manifest())
    required_fields = "\n".join(f"- {field}" for field in manifest["required_review_fields"])
    stay_in_c_fields = "\n".join(f"- {field}" for field in manifest["stay_in_c_closeout_fields"])
    reopen_fields = "\n".join(f"- {field}" for field in manifest["reopen_evidence_fields"])
    return f"""# Phase 15 Architecture Council Review Process

- `PHASE15_STATUS=architecture_council_review_process_landed`
- `PHASE15_LANE_KEY=P15-L08`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `{CURRENT_READBACK_MARKER}`
- this note keeps the docs-root field inventory, the dedicated decision-record template, the dedicated review-process manifest, the focused review-process handoff checker, the focused Zig replay, and the focused build-file replay are landed through `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `scripts/zigux/check-phase15-review-process-handoff.py`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_architecture_council_review_process.zig`, and `zigux/tests/phase15_architecture_council_review_process_build.zig`
- broader validator-first shared-summary surfaces remain gap-tracked
- defaults that record to dated-master-readback provenance
- focused review-process replay
- focused build-file replay
- {manifest["review_checklist_boundary_rule"]}

Any freeze-map anchor entering Architecture Council status review must keep all of the following explicit:
{required_fields}

If a freeze-in-C review closes without a status change, the closeout record must keep all of the following explicit:
{stay_in_c_fields}

A later reopen request must not rely on generic intent alone. It must cite:
{reopen_fields}
"""


def _sample_decision_record_template() -> str:
    manifest = json.loads(_sample_manifest())
    required_fields = "\n".join(f"- {field}" for field in manifest["required_review_fields"])
    stay_in_c_fields = "\n".join(f"- {field}" for field in manifest["stay_in_c_closeout_fields"])
    reopen_fields = "\n".join(f"- {field}" for field in manifest["reopen_evidence_fields"])
    markers = "\n".join(f"- {marker}" for marker in manifest["decision_record_template_required_markers"])
    return f"""# Phase 15 Architecture Council Decision Record Template

{required_fields}

## Stay-In-C Closeout
{stay_in_c_fields}

## Reopen Evidence
{reopen_fields}

## Usage Rules
{markers}
"""


def _sample_indefinite_c_policy() -> str:
    manifest = json.loads(_sample_manifest())
    markers = "\n".join(f"- {marker}" for marker in manifest["indefinite_c_policy_required_markers"])
    return f"""# Phase 15 Indefinite-C Policy

- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `{CURRENT_READBACK_MARKER}`

## Required recorded fields
{markers}
"""


def _sample_review_checklist() -> str:
    manifest = json.loads(_sample_manifest())
    return f"""# Zigux Review Checklist

- if a freeze-map anchor is entering Architecture Council status review, does this checklist keep the shared entry-review prompt explicit while `{manifest["review_process_note"]}` and `{manifest["decision_record_template"]}` remain the owners of the exact Architecture Council field inventory, stay-in-C closeout record, and reopen-evidence details?
"""


def _sample_handoff_note() -> str:
    manifest = json.loads(_sample_manifest())
    markers = "\n".join(f"- {marker}" for marker in manifest["handoff_required_markers"])
    return f"""# Phase 15 Handoff Next Steps Survey

- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `{CURRENT_READBACK_MARKER}`
- the dedicated handoff-specific manifest `zigux/tests/phase15_handoff_next_steps_manifest.json` is directly materialized on current `master`
- no dedicated handoff-specific Zig replay is directly materialized on current `master`
- treat this note together with `zigux/tests/phase15_handoff_next_steps_manifest.json` as the handoff-specific source of truth until that replay lands

## Current handed-off packet on current master
{markers}

## Non-goals
- an Architecture Council approval workflow implementation
- a direct port-readiness decision for any Phase 15 anchor
"""


def _sample_shared_gap_note() -> str:
    manifest = json.loads(_sample_manifest())
    present = "\n".join(f"- {marker}" for marker in manifest["shared_gap_expected_present_paths"])
    missing = "\n".join(f"- {marker}" for marker in manifest["shared_gap_expected_missing_paths"])
    return f"""# Phase 15 Shared Summary Gap

## Materialized focused companions on current master
{present}

## Still-missing broader validator-first companions on current master
{missing}
"""


def _seed_repo(root: Path) -> None:
    _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
    _write(root / DECISION_RECORD_TEMPLATE_PATH, _sample_decision_record_template())
    _write(root / INDEFINITE_C_POLICY_PATH, _sample_indefinite_c_policy())
    _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
    _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
    _write(root / SHARED_GAP_NOTE_PATH, _sample_shared_gap_note())
    _write(root / MANIFEST_PATH, _sample_manifest())
    _write(root / TEST_PATH, "// focused review-process replay fixture\n")
    _write(
        root / BUILD_GATE_PATH,
        "const std = @import(\"std\");\n"
        "pub fn build(b: *std.Build) void {\n"
        "    _ = b.path(\"phase15_architecture_council_review_process.zig\");\n"
        "    const test_step = b.step(\"test\", \"Run the focused Phase 15 Architecture Council review-process test\");\n"
        "    _ = test_step;\n"
        "}\n",
    )

    manifest = json.loads(_sample_manifest())
    for marker in manifest["shared_gap_expected_present_paths"]:
        repo_path = _marker_to_repo_path(marker)
        if repo_path is not None and repo_path not in {TEST_PATH, BUILD_GATE_PATH, MANIFEST_PATH}:
            _write(root / repo_path, "present\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_architecture_council_review_process_") as tmpdir:
        root = Path(tmpdir)
        _seed_repo(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_prompt_root = root / "missing_prompt"
        _seed_repo(missing_prompt_root)
        _write(missing_prompt_root / REVIEW_CHECKLIST_PATH, "# Zigux Review Checklist\n")
        failures = collect_failures(missing_prompt_root)
        expected = ["review checklist is missing the Phase 15 Architecture Council entry-review prompt"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-prompt failure: {failures}")

        missing_build_gate_root = root / "missing_build_gate"
        _seed_repo(missing_build_gate_root)
        (missing_build_gate_root / BUILD_GATE_PATH).unlink()
        failures = collect_failures(missing_build_gate_root)
        expected = [
            "shared-summary gap note claims materialized path is missing from repo: "
            "`zigux/tests/phase15_architecture_council_review_process_build.zig`",
            "focused review-process build-file replay is missing from repo: "
            "`zigux/tests/phase15_architecture_council_review_process_build.zig`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-build-gate failure: {failures}")

        missing_present_path_root = root / "missing_present_path"
        _seed_repo(missing_present_path_root)
        (missing_present_path_root / "zigux/tests/phase15_handoff_next_steps_manifest.json").unlink()
        failures = collect_failures(missing_present_path_root)
        expected = [
            "shared-summary gap note claims materialized path is missing from repo: "
            "`zigux/tests/phase15_handoff_next_steps_manifest.json`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-present-path failure: {failures}")

        returned_gap_root = root / "returned_gap"
        _seed_repo(returned_gap_root)
        _write(returned_gap_root / "zigux/tests/phase15_build.zig", "present\n")
        failures = collect_failures(returned_gap_root)
        expected = [
            "shared-summary gap note still frames shipped path as missing gap: "
            "`zigux/tests/phase15_build.zig`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected returned-gap failure: {failures}")

    print("PHASE15_ARCHITECTURE_COUNCIL_REVIEW_PROCESS_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that the Phase 15 Architecture Council review-process note stays "
            "aligned with the template, manifest, checklist prompt, and focused replay packet."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing Documentation/zigux, scripts/zigux, and zigux/tests",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic repo fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 Architecture Council review-process check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())