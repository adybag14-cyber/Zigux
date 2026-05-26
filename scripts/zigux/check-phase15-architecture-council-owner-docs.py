#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

FREEZE_MAP_REL = "Documentation/zigux/freeze-map.md"
REVIEW_CHECKLIST_REL = "Documentation/zigux/review-checklist.md"
FREEZE_GOVERNANCE_REL = "Documentation/zigux/phase15-freeze-map-governance.md"
REVIEW_PROCESS_REL = "Documentation/zigux/phase15-architecture-council-review-process.md"
DECISION_TEMPLATE_REL = "Documentation/zigux/phase15-architecture-council-decision-record-template.md"
INDEFINITE_C_POLICY_REL = "Documentation/zigux/phase15-indefinite-c-policy.md"

REQUIRED_FILES = (
    FREEZE_MAP_REL,
    REVIEW_CHECKLIST_REL,
    FREEZE_GOVERNANCE_REL,
    REVIEW_PROCESS_REL,
    DECISION_TEMPLATE_REL,
    INDEFINITE_C_POLICY_REL,
)

FREEZE_MAP_MARKERS = (
    f"`{REVIEW_PROCESS_REL}`",
    f"`{DECISION_TEMPLATE_REL}`",
    f"`{FREEZE_GOVERNANCE_REL}`",
    f"`{INDEFINITE_C_POLICY_REL}`",
    "required approver set",
    "evidence archive path",
    "`retired_from_active_discussion` state",
    "trigger-specific evidence refresh",
    "study-only anchor accounting",
)

REVIEW_CHECKLIST_MARKERS = (
    "if a freeze-map anchor is entering Architecture Council status review",
    f"`{REVIEW_PROCESS_REL}`",
    f"`{DECISION_TEMPLATE_REL}`",
    "owners of the exact Architecture Council field inventory",
    "stay-in-C closeout record",
    "reopen-evidence details",
    f"`{INDEFINITE_C_POLICY_REL}`",
    "retained blocker posture",
    "trigger-specific evidence refresh",
    "return-to-blocked wording",
)

FREEZE_GOVERNANCE_MARKERS = (
    "freeze-map status-change requests must keep the root policy layer aligned with the broader Architecture Council review packet fields",
    "required approver set",
    "evidence archive path",
    "replay command",
    "rollback threshold",
    "`retired_from_active_discussion`",
    "trigger-specific evidence refresh",
    "explicit non-goals",
    "written rationale",
)

REVIEW_PROCESS_MARKERS = (
    "PHASE15_STATUS=architecture_council_review_process_landed",
    "PHASE15_LANE_KEY=P15-L08",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    f"`{DECISION_TEMPLATE_REL}`",
    f"`{INDEFINITE_C_POLICY_REL}`",
    f"`{FREEZE_GOVERNANCE_REL}`",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
    "study-only anchor accounting link or explicit freeze-map-anchor confirmation",
)

DECISION_TEMPLATE_MARKERS = (
    "`PHASE15_PROVENANCE_MODE=dated_master_readback`",
    "`SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD`",
    "exact-head provenance exception note:",
    "study-only anchor accounting link or explicit freeze-map-anchor confirmation:",
    "Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.",
)

INDEFINITE_C_POLICY_MARKERS = (
    "PHASE15_STATUS=indefinite_c_policy_packet_landed",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "decision record ID, lane owner, required approver set, and rollback owner",
    "automatic return-to-blocked trigger",
    "trigger-specific evidence refresh",
    "parity scorecard link or blocker record",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _require_markers(text: str, markers: tuple[str, ...], prefix: str, failures: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{prefix}:missing:{marker}")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    freeze_map = _read(root / FREEZE_MAP_REL)
    review_checklist = _read(root / REVIEW_CHECKLIST_REL)
    freeze_governance = _read(root / FREEZE_GOVERNANCE_REL)
    review_process = _read(root / REVIEW_PROCESS_REL)
    decision_template = _read(root / DECISION_TEMPLATE_REL)
    indefinite_c_policy = _read(root / INDEFINITE_C_POLICY_REL)

    _require_markers(freeze_map, FREEZE_MAP_MARKERS, "freeze_map", failures)
    _require_markers(review_checklist, REVIEW_CHECKLIST_MARKERS, "review_checklist", failures)
    _require_markers(freeze_governance, FREEZE_GOVERNANCE_MARKERS, "freeze_governance", failures)
    _require_markers(review_process, REVIEW_PROCESS_MARKERS, "review_process", failures)
    _require_markers(decision_template, DECISION_TEMPLATE_MARKERS, "decision_template", failures)
    _require_markers(indefinite_c_policy, INDEFINITE_C_POLICY_MARKERS, "indefinite_c_policy", failures)

    return failures


def _seed(root: Path) -> None:
    _write(
        root / FREEZE_MAP_REL,
        f"""# Zigux Freeze Map

- freeze-map status-change requests must route through `{REVIEW_PROCESS_REL}`, `{FREEZE_GOVERNANCE_REL}`, `Documentation/zigux/phase15-parity-scorecard.md`, `{INDEFINITE_C_POLICY_REL}`, and `{DECISION_TEMPLATE_REL}`, and keep the required approver set, evidence archive path, rollback threshold, `retired_from_active_discussion` state, trigger-specific evidence refresh, and study-only anchor accounting link explicit
""",
    )
    _write(
        root / REVIEW_CHECKLIST_REL,
        f"""# Zigux Review Checklist

- if a freeze-map anchor is entering Architecture Council status review, does this checklist keep the shared entry-review prompt explicit while `{REVIEW_PROCESS_REL}` and `{DECISION_TEMPLATE_REL}` remain the owners of the exact Architecture Council field inventory, stay-in-C closeout record, and reopen-evidence details, and `{INDEFINITE_C_POLICY_REL}` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording?
""",
    )
    _write(
        root / FREEZE_GOVERNANCE_REL,
        """# Phase 15 Freeze-Map Governance

- freeze-map status-change requests must keep the root policy layer aligned with the broader Architecture Council review packet fields, including required approver set, evidence archive path, replay command, rollback threshold, `retired_from_active_discussion`, trigger-specific evidence refresh, explicit non-goals, and written rationale
""",
    )
    _write(
        root / REVIEW_PROCESS_REL,
        f"""# Phase 15 Architecture Council Review Process

- `PHASE15_STATUS=architecture_council_review_process_landed`
- `PHASE15_LANE_KEY=P15-L08`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- this note stays aligned with `{DECISION_TEMPLATE_REL}`, `{INDEFINITE_C_POLICY_REL}`, `{FREEZE_GOVERNANCE_REL}`, and no Architecture Council approval is currently recorded for a freeze-map status change
- the supporting context must keep the study-only anchor accounting link or explicit freeze-map-anchor confirmation
""",
    )
    _write(
        root / DECISION_TEMPLATE_REL,
        """# Phase 15 Architecture Council Decision Record Template

- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- `SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD`
- exact-head provenance exception note:
- study-only anchor accounting link or explicit freeze-map-anchor confirmation:
- Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.
""",
    )
    _write(
        root / INDEFINITE_C_POLICY_REL,
        """# Phase 15 Indefinite-C Policy

- `PHASE15_STATUS=indefinite_c_policy_packet_landed`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- keep the decision record ID, lane owner, required approver set, and rollback owner explicit together with the automatic return-to-blocked trigger, trigger-specific evidence refresh, and parity scorecard link or blocker record
""",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_architecture_council_owner_docs_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)
        failures = validate(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_freeze_marker = root / "missing_freeze_marker"
        _seed(missing_freeze_marker)
        _write(
            missing_freeze_marker / FREEZE_MAP_REL,
            _read(missing_freeze_marker / FREEZE_MAP_REL).replace("required approver set, ", "", 1),
        )
        failures = validate(missing_freeze_marker)
        expected = ["freeze_map:missing:required approver set"]
        if failures != expected:
            raise AssertionError(f"unexpected freeze-map failure: {failures}")

        missing_checklist_owner = root / "missing_checklist_owner"
        _seed(missing_checklist_owner)
        _write(
            missing_checklist_owner / REVIEW_CHECKLIST_REL,
            _read(missing_checklist_owner / REVIEW_CHECKLIST_REL).replace(
                "owners of the exact Architecture Council field inventory, ", "", 1
            ),
        )
        failures = validate(missing_checklist_owner)
        expected = ["review_checklist:missing:owners of the exact Architecture Council field inventory"]
        if failures != expected:
            raise AssertionError(f"unexpected checklist failure: {failures}")

        missing_template_rule = root / "missing_template_rule"
        _seed(missing_template_rule)
        _write(
            missing_template_rule / DECISION_TEMPLATE_REL,
            _read(missing_template_rule / DECISION_TEMPLATE_REL).replace(
                "- Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.\n",
                "",
                1,
            ),
        )
        failures = validate(missing_template_rule)
        expected = [
            "decision_template:missing:Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first."
        ]
        if failures != expected:
            raise AssertionError(f"unexpected template failure: {failures}")

        missing_policy_marker = root / "missing_policy_marker"
        _seed(missing_policy_marker)
        _write(
            missing_policy_marker / INDEFINITE_C_POLICY_REL,
            _read(missing_policy_marker / INDEFINITE_C_POLICY_REL).replace(
                "automatic return-to-blocked trigger, ", "", 1
            ),
        )
        failures = validate(missing_policy_marker)
        expected = ["indefinite_c_policy:missing:automatic return-to-blocked trigger"]
        if failures != expected:
            raise AssertionError(f"unexpected policy failure: {failures}")

    print("PHASE15_ARCHITECTURE_COUNCIL_OWNER_DOCS_SELF_TEST=pass")
    print("PHASE15_ARCHITECTURE_COUNCIL_OWNER_DOCS_SELF_TEST_CASES=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 Architecture Council owner-doc packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("PHASE15_ARCHITECTURE_COUNCIL_OWNER_DOCS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
