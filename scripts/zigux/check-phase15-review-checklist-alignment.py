#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")
REVIEW_PROCESS_PATH = Path("Documentation/zigux/phase15-architecture-council-review-process.md")
DECISION_RECORD_TEMPLATE_PATH = Path(
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md"
)
INDEFINITE_C_POLICY_PATH = Path("Documentation/zigux/phase15-indefinite-c-policy.md")
STUDY_ONLY_ACCOUNTING_PATH = Path("Documentation/zigux/phase15-study-only-anchor-accounting.md")

ENTRY_REVIEW_PROMPT = "if a freeze-map anchor is entering Architecture Council status review"
STUDY_ONLY_PROMPT = "if a shared reminder surface summarizes the study-only freeze-map anchors"
PHASE15_PACKET_PROMPT = "if the change touches the shared Phase 15 governance packet"

ENTRY_REVIEW_MARKERS = (
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "owners of the exact Architecture Council field inventory",
    "stay-in-C closeout record",
    "reopen-evidence details",
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "retained blocker posture",
    "trigger-specific evidence refresh",
    "return-to-blocked wording",
)

STUDY_ONLY_MARKERS = (
    "`Documentation/zigux/freeze-map.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c`",
    "study-only boundary context rather than runtime-substrate or bridge-readiness evidence",
)

PHASE15_PACKET_MARKERS = (
    "`Documentation/zigux/phase15-readiness-gate-survey.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`",
    "`scripts/zigux/check-phase15-review-process-handoff.py`",
    "`scripts/zigux/check-phase15-handoff-note-alignment.py`",
    "`zigux/tests/phase15_architecture_council_review_process_build.zig`",
    "`zigux/tests/phase15_handoff_next_steps_manifest.json`",
    "`zigux/tests/phase15_handoff_next_steps.zig`",
    "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
    "`scripts/zigux/validate-phase15.py`",
    "`zigux/tests/phase15_build.zig`",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit as study-only boundary anchors rather than delivery-ready runtime evidence",
)

FREEZE_MAP_MARKERS = (
    "freeze-map status-change requests must route through `Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "shared reminder surfaces that summarize freeze posture",
    "must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
)

REVIEW_PROCESS_MARKERS = (
    "`Documentation/zigux/review-checklist.md` keeps the shared entry-review and closeout prompts explicit",
    "exact Linux anchor path",
    "roadmap phase",
    "decision record ID",
    "lane owner",
    "required approver set",
    "rollback owner",
    "the retained `freeze_in_c` decision",
    "the automatic return-to-blocked trigger",
    "the exact reopen trigger being exercised",
    "`scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`",
    "`scripts/zigux/check-phase15-review-process-handoff.py`",
)

DECISION_TEMPLATE_MARKERS = (
    "`PHASE15_PROVENANCE_MODE=dated_master_readback`",
    "`SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD`",
    "exact-head provenance exception note:",
    "Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review",
    "If any required field above cannot be stated honestly, keep the request blocked and leave the C implementation as the product source of truth.",
)

INDEFINITE_C_POLICY_MARKERS = (
    "the decision record ID, lane owner, required approver set, and rollback owner",
    "the automatic return-to-blocked trigger, retained `retired_from_active_discussion` state, reopen triggers, and trigger-specific evidence refresh",
    "There is no silent exception path around the indefinite-C policy.",
    "the named reopen trigger now being exercised",
)

STUDY_ONLY_ACCOUNTING_MARKERS = (
    "### `kernel/workqueue.c`",
    "### `kernel/trace/ring_buffer.c`",
    "tracked outside the freeze-in-C scorecard",
    "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _line_with(text: str, marker: str) -> str | None:
    for line in text.splitlines():
        if marker in line:
            return line
    return None


def collect_failures(root: Path) -> list[str]:
    review_checklist = _read(root / REVIEW_CHECKLIST_PATH)
    freeze_map = _read(root / FREEZE_MAP_PATH)
    review_process = _read(root / REVIEW_PROCESS_PATH)
    decision_template = _read(root / DECISION_RECORD_TEMPLATE_PATH)
    indefinite_c_policy = _read(root / INDEFINITE_C_POLICY_PATH)
    study_only_accounting = _read(root / STUDY_ONLY_ACCOUNTING_PATH)

    failures: list[str] = []

    entry_line = _line_with(review_checklist, ENTRY_REVIEW_PROMPT)
    if entry_line is None:
        failures.append("review checklist is missing the Architecture Council entry-review prompt")
    else:
        for marker in ENTRY_REVIEW_MARKERS:
            if marker not in entry_line:
                failures.append(f"entry-review prompt missing marker: {marker}")

    study_only_line = _line_with(review_checklist, STUDY_ONLY_PROMPT)
    if study_only_line is None:
        failures.append("review checklist is missing the study-only anchor reminder prompt")
    else:
        for marker in STUDY_ONLY_MARKERS:
            if marker not in study_only_line:
                failures.append(f"study-only prompt missing marker: {marker}")

    phase15_packet_line = _line_with(review_checklist, PHASE15_PACKET_PROMPT)
    if phase15_packet_line is None:
        failures.append("review checklist is missing the shared Phase 15 governance packet prompt")
    else:
        for marker in PHASE15_PACKET_MARKERS:
            if marker not in phase15_packet_line:
                failures.append(f"phase15 governance prompt missing marker: {marker}")

    for marker in FREEZE_MAP_MARKERS:
        if marker not in freeze_map:
            failures.append(f"freeze map missing governance marker: {marker}")

    for marker in REVIEW_PROCESS_MARKERS:
        if marker not in review_process:
            failures.append(f"review-process note missing marker: {marker}")

    for marker in DECISION_TEMPLATE_MARKERS:
        if marker not in decision_template:
            failures.append(f"decision-record template missing marker: {marker}")

    for marker in INDEFINITE_C_POLICY_MARKERS:
        if marker not in indefinite_c_policy:
            failures.append(f"indefinite-C policy missing marker: {marker}")

    for marker in STUDY_ONLY_ACCOUNTING_MARKERS:
        if marker not in study_only_accounting:
            failures.append(f"study-only accounting note missing marker: {marker}")

    return failures


def _sample_review_checklist() -> str:
    return """# Zigux Review Checklist

  * if a freeze-map anchor is entering Architecture Council status review, does this checklist keep the shared entry-review prompt explicit while `Documentation/zigux/phase15-architecture-council-review-process.md` and `Documentation/zigux/phase15-architecture-council-decision-record-template.md` remain the owners of the exact Architecture Council field inventory, stay-in-C closeout record, and reopen-evidence details, and `Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording?
  * if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence?
  * if the change touches the shared Phase 15 governance packet, do `Documentation/zigux/freeze-map.md`, `Documentation/zigux/README.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-parity-scorecard-survey.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase15-shared-summary-gap.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/check-phase15-handoff-note-alignment.py`, `scripts/zigux/check-phase15-readiness-gate-packet.py`, `zigux/tests/phase15_architecture_council_review_process_build.zig`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_handoff_next_steps.zig`, and `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig` still agree on the current maintenance-mode governance packet, keep `scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig` framed as repo-reality gaps until direct current-`master` rereads restore them, keep `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit as study-only boundary anchors rather than delivery-ready runtime evidence, and avoid implying any Architecture Council approval or freeze-map status change that the current packet does not record?
"""


def _sample_freeze_map() -> str:
    return """# Zigux Freeze Map

- freeze-map status-change requests must route through `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- shared reminder surfaces that summarize freeze posture, especially `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md`, must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md` when they summarize that boundary set
- study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md` so the `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` inventory does not drift from this file
"""


def _sample_review_process() -> str:
    return """# Phase 15 Architecture Council Review Process

- `Documentation/zigux/review-checklist.md` keeps the shared entry-review and closeout prompts explicit, but the exact Architecture Council field inventory stays owned by this note and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- exact Linux anchor path
- roadmap phase
- decision record ID
- lane owner
- required approver set
- rollback owner
- the retained `freeze_in_c` decision
- the automatic return-to-blocked trigger
- the exact reopen trigger being exercised
- `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`
- `scripts/zigux/check-phase15-review-process-handoff.py`
"""


def _sample_decision_template() -> str:
    return """# Phase 15 Architecture Council Decision Record Template

- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- `SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD`
- exact-head provenance exception note:
- Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.
- If any required field above cannot be stated honestly, keep the request blocked and leave the C implementation as the product source of truth.
"""


def _sample_indefinite_c_policy() -> str:
    return """# Phase 15 Indefinite-C Policy

- the decision record ID, lane owner, required approver set, and rollback owner
- the automatic return-to-blocked trigger, retained `retired_from_active_discussion` state, reopen triggers, and trigger-specific evidence refresh
- There is no silent exception path around the indefinite-C policy.
- the named reopen trigger now being exercised
"""


def _sample_study_only_accounting() -> str:
    return """# Phase 15 Study-Only Anchor Accounting

### `kernel/workqueue.c`
- current Phase 15 role: tracked outside the freeze-in-C scorecard and outside blocked status-change rows

### `kernel/trace/ring_buffer.c`
- current Phase 15 role: tracked outside the freeze-in-C scorecard and outside blocked status-change rows

- if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it
"""


def _seed_repo(root: Path) -> None:
    _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
    _write(root / FREEZE_MAP_PATH, _sample_freeze_map())
    _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
    _write(root / DECISION_RECORD_TEMPLATE_PATH, _sample_decision_template())
    _write(root / INDEFINITE_C_POLICY_PATH, _sample_indefinite_c_policy())
    _write(root / STUDY_ONLY_ACCOUNTING_PATH, _sample_study_only_accounting())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_review_checklist_") as tmpdir:
        root = Path(tmpdir)

        _seed_repo(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        missing_entry_root = root / "missing_entry"
        _seed_repo(missing_entry_root)
        _write(
            missing_entry_root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace(
                "if a freeze-map anchor is entering Architecture Council status review",
                "if a freeze-map anchor is entering some other review",
                1,
            ),
        )
        failures = collect_failures(missing_entry_root)
        expected = ["review checklist is missing the Architecture Council entry-review prompt"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-entry failure: {failures}")
        case_count += 1

        missing_policy_boundary_root = root / "missing_policy_boundary"
        _seed_repo(missing_policy_boundary_root)
        _write(
            missing_policy_boundary_root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace(
                "and `Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_policy_boundary_root)
        expected = [
            "entry-review prompt missing marker: `Documentation/zigux/phase15-indefinite-c-policy.md`",
            "entry-review prompt missing marker: retained blocker posture",
            "entry-review prompt missing marker: trigger-specific evidence refresh",
            "entry-review prompt missing marker: return-to-blocked wording",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-policy-boundary failure: {failures}")
        case_count += 1

        missing_study_route_root = root / "missing_study_route"
        _seed_repo(missing_study_route_root)
        _write(
            missing_study_route_root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace(
                "`Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
                "`Documentation/zigux/freeze-map.md`",
                1,
            ),
        )
        failures = collect_failures(missing_study_route_root)
        expected = [
            "study-only prompt missing marker: `Documentation/zigux/phase15-study-only-anchor-accounting.md`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-study-route failure: {failures}")
        case_count += 1

        missing_phase15_packet_root = root / "missing_phase15_packet"
        _seed_repo(missing_phase15_packet_root)
        _write(
            missing_phase15_packet_root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace(
                "`scripts/zigux/check-phase15-review-process-handoff.py`, ",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_phase15_packet_root)
        expected = [
            "phase15 governance prompt missing marker: `scripts/zigux/check-phase15-review-process-handoff.py`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-phase15-packet failure: {failures}")
        case_count += 1

        missing_gap_marker_root = root / "missing_gap_marker"
        _seed_repo(missing_gap_marker_root)
        _write(
            missing_gap_marker_root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace(
                "keep `scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig` framed as repo-reality gaps until direct current-`master` rereads restore them, ",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_gap_marker_root)
        expected = [
            "phase15 governance prompt missing marker: `scripts/zigux/validate-phase15.py`",
            "phase15 governance prompt missing marker: `zigux/tests/phase15_build.zig`",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-gap-marker failure: {failures}")
        case_count += 1

        missing_freeze_map_rule_root = root / "missing_freeze_map_rule"
        _seed_repo(missing_freeze_map_rule_root)
        _write(
            missing_freeze_map_rule_root / FREEZE_MAP_PATH,
            _sample_freeze_map().replace(
                "study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md` so the `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` inventory does not drift from this file",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_freeze_map_rule_root)
        expected = [
            "freeze map missing governance marker: study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-freeze-map-rule failure: {failures}")
        case_count += 1

    print("PHASE15_REVIEW_CHECKLIST_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE15_REVIEW_CHECKLIST_ALIGNMENT_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 review-checklist surface stays aligned with Architecture Council governance boundaries."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--self-test", action="store_true", help="run the built-in synthetic self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 review-checklist alignment check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
