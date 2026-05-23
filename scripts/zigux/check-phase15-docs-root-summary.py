#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SUMMARY_REL = "Documentation/zigux/phase15-docs-root-summary.md"

PRESENT_PATHS = (
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-parity-scorecard-survey.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "Documentation/zigux/phase15-shared-summary-gap.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check-phase15-docs-readme-alignment.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-tests-readme-alignment.py",
    "scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-handoff-note-alignment.py",
    "scripts/zigux/check-phase15-shared-summary-gap.py",
    "scripts/zigux/check-phase15-readiness-gate-packet.py",
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_architecture_council_review_process_build.zig",
    "zigux/tests/phase15_governance_lane_sequencing_manifest.json",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_parity_scorecard.json",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
)

GAP_PATHS = (
    "zigux/tests/phase15_build.zig",
)

REQUIRED_MARKERS = (
    "# Phase 15 Docs-Root Summary",
    "`PHASE15_STATUS=docs_root_summary_landed`",
    "`PHASE15_LANE_KEY=arch-council`",
    "`PHASE15_PROVENANCE_MODE=dated_master_readback`",
    "surveyed against dated current-master readback marker `current-master-readback-2026-05-23`",
    "Current `master` now directly materializes `scripts/zigux/validate-phase15.py`",
    "Current `master` now directly materializes `zigux/tests/phase15_architecture_council_review_process_build.zig`",
    "Current `master` now directly materializes `zigux/tests/phase15_handoff_next_steps_manifest.json` and `zigux/tests/phase15_handoff_next_steps.zig`",
    "Current `master` now directly materializes `zigux/tests/phase15_governance_lane_sequencing_manifest.json` and `zigux/tests/phase15_governance_lane_sequencing.zig`",
    "Current `master` now directly materializes `zigux/tests/phase15_parity_scorecard.json`",
    "Current `master` now directly materializes `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
    "Current `master` still does not materialize `zigux/tests/phase15_build.zig`",
    "Although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`",
    "No Architecture Council approval is currently recorded for a freeze-map status change.",
    "Keep the current docs-root reminder narrowed to truthfulness maintenance rather than a fresh freeze-map status change claim.",
    "the named reopen trigger",
    "the blocker disposition being challenged",
    "the narrower seam or policy change that makes review safe",
    "the exact supporting evidence path refresh",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    summary_path = root / SUMMARY_REL
    if not summary_path.exists():
        return [f"missing_file:{SUMMARY_REL}"]

    summary = _read(summary_path)

    for marker in REQUIRED_MARKERS:
        if marker not in summary:
            failures.append(f"summary:missing:{marker}")

    for rel in PRESENT_PATHS:
        marker = f"`{rel}`"
        if marker not in summary:
            failures.append(f"summary:missing_present_path:{marker}")
        if not (root / rel).exists():
            failures.append(f"repo:missing_present_path:{rel}")

    for rel in GAP_PATHS:
        marker = f"`{rel}`"
        if marker not in summary:
            failures.append(f"summary:missing_gap_path:{marker}")
        if (root / rel).exists():
            failures.append(f"repo:gap_path_returned:{rel}")

    return failures


def _sample_summary() -> str:
    present = "\n".join(f"- `{rel}`" for rel in PRESENT_PATHS)
    gap = "\n".join(f"- `{rel}`" for rel in GAP_PATHS)
    return f"""# Phase 15 Docs-Root Summary

This note records the bounded docs-root summary for the current Phase 15 governance packet on `master`.

## Status

- `PHASE15_STATUS=docs_root_summary_landed`
- `PHASE15_LANE_KEY=arch-council`
- `PHASE15_SLICE=docs-root-summary`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-23`
- packet role: keep the docs-root Phase 15 summary truthful around the landed Architecture Council packet, the directly materialized maintenance checks, and the still-missing broader dedicated-build companion without implying a freeze-map status change or deep-core delivery approval

## Current landed docs-root packet

Keep the current docs-root Phase 15 summary anchored to the directly readable governance packet:

{present}

## Current truthfulness boundaries

- Current `master` now directly materializes `scripts/zigux/validate-phase15.py`, so keep that validator-first maintenance gate explicit as landed evidence instead of broader repo-reality-gap wording.
- Current `master` now directly materializes `zigux/tests/phase15_architecture_council_review_process_build.zig`, so keep that focused build-file replay explicit in the Architecture Council packet.
- Current `master` now directly materializes `zigux/tests/phase15_handoff_next_steps_manifest.json` and `zigux/tests/phase15_handoff_next_steps.zig`, so keep the handoff packet framed as manifest-plus-replay evidence rather than manifest-only inventory.
- Current `master` now directly materializes `zigux/tests/phase15_governance_lane_sequencing_manifest.json` and `zigux/tests/phase15_governance_lane_sequencing.zig`, so keep the lane-sequencing packet framed as manifest-plus-replay evidence rather than an undercounted side companion.
- Current `master` now directly materializes `zigux/tests/phase15_parity_scorecard.json`, so keep the machine-readable parity companion explicit beside `zigux/tests/phase15_parity_scorecard.zig`.
- Current `master` now directly materializes `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, so keep that lane-owner replay explicit inside the directly readable governance packet.
- Current `master` still does not materialize `zigux/tests/phase15_build.zig`, so keep that broader dedicated-build companion framed as a repo-reality gap rather than shipped replay evidence.
- Although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`, so keep those route names in blocked-route vocabulary rather than current replay evidence.
- No Architecture Council approval is currently recorded for a freeze-map status change.

## Review boundary

Keep the current docs-root reminder narrowed to truthfulness maintenance rather than a fresh freeze-map status change claim.

The shared Phase 15 docs-root handoff should also keep:

- the named reopen trigger
- the blocker disposition being challenged
- the narrower seam or policy change that makes review safe
- the exact supporting evidence path refresh

That handoff remains a governance boundary, not direct deep-core readiness evidence.

## Gap

{gap}
"""


def _seed(root: Path) -> None:
    _write(root / SUMMARY_REL, _sample_summary())
    for rel in PRESENT_PATHS:
        _write(root / rel, "present\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_docs_root_summary_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)
        failures = validate(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_validator = root / "missing_validator"
        _seed(missing_validator)
        _write(
            missing_validator / SUMMARY_REL,
            _sample_summary().replace(
                "Current `master` now directly materializes `scripts/zigux/validate-phase15.py`, so keep that validator-first maintenance gate explicit as landed evidence instead of broader repo-reality-gap wording.\n",
                "",
                1,
            ),
        )
        failures = validate(missing_validator)
        expected = [
            "summary:missing:Current `master` now directly materializes `scripts/zigux/validate-phase15.py`",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-validator failure: {failures}")

        returned_gap = root / "returned_gap"
        _seed(returned_gap)
        _write(returned_gap / GAP_PATHS[0], "present\n")
        failures = validate(returned_gap)
        expected = [f"repo:gap_path_returned:{GAP_PATHS[0]}"]
        if failures != expected:
            raise AssertionError(f"unexpected returned-gap failure: {failures}")

        missing_present = root / "missing_present"
        _seed(missing_present)
        (missing_present / PRESENT_PATHS[-1]).unlink()
        failures = validate(missing_present)
        expected = [f"repo:missing_present_path:{PRESENT_PATHS[-1]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-present failure: {failures}")

    print("PHASE15_DOCS_ROOT_SUMMARY_CHECK=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the bounded Phase 15 docs-root summary stays aligned with current governance packet reality."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE15_DOCS_ROOT_SUMMARY_CHECK=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
