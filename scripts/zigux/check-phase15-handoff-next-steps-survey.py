#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")

DIRECT_PACKET_PATHS = (
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-deep-core-blocker-survey.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-parity-scorecard-survey.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "Documentation/zigux/phase15-shared-summary-gap.md",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_parity_scorecard.json",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_architecture_council_review_process_build.zig",
    "zigux/tests/phase15_governance_lane_sequencing_manifest.json",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "scripts/zigux/check-phase15-docs-readme-alignment.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
    "scripts/zigux/check-phase15-readiness-gate-packet.py",
    "scripts/zigux/check-phase15-tests-readme-alignment.py",
    "scripts/zigux/check-phase15-shared-summary-gap.py",
    "scripts/zigux/check-phase15-handoff-note-alignment.py",
    "scripts/zigux/validate-phase15.py",
)

BROAD_REMINDER_PATHS = (
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
)

STATUS_MARKERS = (
    "PHASE15_STATUS=handoff_next_steps_survey_landed",
    "PHASE15_LANE_KEY=P15-L12",
    "PHASE15_SLICE=existing_governance_packet_handoff_inventory",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
)

REQUIRED_TEXT_MARKERS = (
    "surveyed against dated current-master readback marker `current-master-readback-2026-05-25`",
    "The dedicated validator, the shared build companion, the governance-lane sequencing companions, and the directly materialized reminder-surface checkers now define the tighter same-lane boundaries, while the broader wrapper-route and shared-CI follow-through should only reopen when fresh drift actually appears.",
    "The dedicated governance-lane sequencing manifest `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, the focused governance-lane sequencing Zig replay `zigux/tests/phase15_governance_lane_sequencing.zig`, the dedicated handoff-specific manifest `zigux/tests/phase15_handoff_next_steps_manifest.json`, and the focused handoff-specific Zig replay `zigux/tests/phase15_handoff_next_steps.zig` are directly materialized on current `master`.",
    "The focused freeze-map governance replay `zigux/tests/phase15_freeze_map_governance.zig`, the focused parity-scorecard machine-readable companion `zigux/tests/phase15_parity_scorecard.json`, and the focused parity-scorecard Zig replay `zigux/tests/phase15_parity_scorecard.zig` are also directly materialized on current `master`.",
    "Treat this note together with `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, `zigux/tests/phase15_governance_lane_sequencing.zig`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_handoff_next_steps.zig`, and `zigux/tests/phase15_build.zig` as the handoff-specific source of truth while the blocked route bodies and shared-CI route remain gap-tracked.",
    "The roadmap-required Phase 15 governance features are already materialized on current `master`: the freeze map, the Architecture Council review process, the parity scorecard, and the policy for code that remains in C indefinitely all have directly readable owner notes in the current packet.",
    "These are handoff and reminder-surface gaps, not missing ownership of the roadmap's four required governance features.",
    "keep the four freeze-in-C anchors parked: `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c`",
    "keep the two roadmap study-only anchors parked: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`",
    "no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`",
    "no dedicated shared-CI Phase 15 validate, test, or aggregate route is materialized in `.github/workflows/zigux-bootstrap.yml` on current `master`",
    "no Architecture Council approval is currently recorded for a freeze-map status change, so the packet remains in maintenance-mode blocker accounting rather than port-readiness",
)

BROAD_REMINDER_MARKERS = (
    "`Documentation/zigux/README.md`, which still stops at Phase 14 on current `master` and should stay treated as an active shared-summary gap source until a dedicated Phase 15 docs-root reminder lands and aligns with `scripts/zigux/check-phase15-docs-readme-alignment.py` plus the directly materialized governance packet",
    "`scripts/zigux/README.md`, which should be reread with `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the directly materialized governance packet rather than being treated as a dedicated handoff-local truth source by default",
    "`zigux/tests/README.md` reminder surface, which should be reread with `scripts/zigux/check-phase15-tests-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the directly materialized governance packet instead of being carried here as an unlanded future target by default",
)

STALE_TEXT_MARKERS = (
    "PHASE15_LANE_KEY=P15-L11",
    "current-master-readback-2026-05-18",
    "no dedicated handoff-specific manifest or Zig replay is directly materialized on current `master`",
    "## Missing dedicated handoff companions",
)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing file: {path}") from exc


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def collect_failures(root: Path) -> list[str]:
    handoff_note = _read_text(root / HANDOFF_NOTE_PATH)
    failures: list[str] = []

    for marker in STATUS_MARKERS:
        if marker not in handoff_note:
            failures.append(f"handoff_note:missing_status:{marker}")

    for marker in REQUIRED_TEXT_MARKERS:
        if marker not in handoff_note:
            failures.append(f"handoff_note:missing_marker:{marker}")

    for rel in DIRECT_PACKET_PATHS:
        if f"`{rel}`" not in handoff_note:
            failures.append(f"handoff_note:missing_path:`{rel}`")
        if not (root / rel).exists():
            failures.append(f"repo:missing_direct_path:{rel}")

    for rel, marker in zip(BROAD_REMINDER_PATHS, BROAD_REMINDER_MARKERS):
        if marker not in handoff_note:
            failures.append(f"handoff_note:missing_broad_marker:{rel}")
        if not (root / rel).exists():
            failures.append(f"repo:missing_broad_path:{rel}")

    for marker in STALE_TEXT_MARKERS:
        if marker in handoff_note:
            failures.append(f"handoff_note:stale_marker:{marker}")

    return failures


def _sample_handoff_note() -> str:
    direct_docs = ", ".join(f"`{rel}`" for rel in DIRECT_PACKET_PATHS[:13])
    direct_tests = ", ".join(f"`{rel}`" for rel in DIRECT_PACKET_PATHS[13:28])
    direct_scripts = ", ".join(f"`{rel}`" for rel in DIRECT_PACKET_PATHS[28:])
    return f"""# Phase 15 Handoff Next Steps Survey

## Status

- `PHASE15_STATUS=handoff_next_steps_survey_landed`
- `PHASE15_LANE_KEY=P15-L12`
- `PHASE15_SLICE=existing_governance_packet_handoff_inventory`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-25`

## Why this note exists

The dedicated validator, the shared build companion, the governance-lane sequencing companions, and the directly materialized reminder-surface checkers now define the tighter same-lane boundaries, while the broader wrapper-route and shared-CI follow-through should only reopen when fresh drift actually appears.

The dedicated governance-lane sequencing manifest `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, the focused governance-lane sequencing Zig replay `zigux/tests/phase15_governance_lane_sequencing.zig`, the dedicated handoff-specific manifest `zigux/tests/phase15_handoff_next_steps_manifest.json`, and the focused handoff-specific Zig replay `zigux/tests/phase15_handoff_next_steps.zig` are directly materialized on current `master`.

The focused freeze-map governance replay `zigux/tests/phase15_freeze_map_governance.zig`, the focused parity-scorecard machine-readable companion `zigux/tests/phase15_parity_scorecard.json`, and the focused parity-scorecard Zig replay `zigux/tests/phase15_parity_scorecard.zig` are also directly materialized on current `master`.

Treat this note together with `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, `zigux/tests/phase15_governance_lane_sequencing.zig`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_handoff_next_steps.zig`, and `zigux/tests/phase15_build.zig` as the handoff-specific source of truth while the blocked route bodies and shared-CI route remain gap-tracked.

## Current handed-off packet on current master

- {direct_docs}
- {direct_tests}
- {direct_scripts}
- the broad docs-root reminder surface `Documentation/zigux/README.md`, which still stops at Phase 14 on current `master` and should stay treated as an active shared-summary gap source until a dedicated Phase 15 docs-root reminder lands and aligns with `scripts/zigux/check-phase15-docs-readme-alignment.py` plus the directly materialized governance packet
- the broad scripts-root reminder surface `scripts/zigux/README.md`, which should be reread with `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the directly materialized governance packet rather than being treated as a dedicated handoff-local truth source by default
- the broad `zigux/tests/README.md` reminder surface, which should be reread with `scripts/zigux/check-phase15-tests-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the directly materialized governance packet instead of being carried here as an unlanded future target by default

## Current governance posture to preserve

- keep the four freeze-in-C anchors parked: `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c`
- keep the two roadmap study-only anchors parked: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`

## Roadmap-backed open handoff gaps

The roadmap-required Phase 15 governance features are already materialized on current `master`: the freeze map, the Architecture Council review process, the parity scorecard, and the policy for code that remains in C indefinitely all have directly readable owner notes in the current packet.

- no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`
- no dedicated shared-CI Phase 15 validate, test, or aggregate route is materialized in `.github/workflows/zigux-bootstrap.yml` on current `master`
- no Architecture Council approval is currently recorded for a freeze-map status change, so the packet remains in maintenance-mode blocker accounting rather than port-readiness
- These are handoff and reminder-surface gaps, not missing ownership of the roadmap's four required governance features.
"""


def _seed_repo(root: Path) -> None:
    _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
    for rel in DIRECT_PACKET_PATHS + BROAD_REMINDER_PATHS:
        _write(root / rel, "present\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_handoff_next_steps_") as tmpdir:
        root = Path(tmpdir)
        _seed_repo(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        missing_status_root = root / "missing_status"
        _seed_repo(missing_status_root)
        _write(
            missing_status_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace("- `PHASE15_LANE_KEY=P15-L12`\n", "", 1),
        )
        failures = collect_failures(missing_status_root)
        expected = ["handoff_note:missing_status:PHASE15_LANE_KEY=P15-L12"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-status failure: {failures}")
        case_count += 1

        missing_marker_root = root / "missing_marker"
        _seed_repo(missing_marker_root)
        _write(
            missing_marker_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "The dedicated validator, the shared build companion, the governance-lane sequencing companions, and the directly materialized reminder-surface checkers now define the tighter same-lane boundaries, while the broader wrapper-route and shared-CI follow-through should only reopen when fresh drift actually appears.\n\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_marker_root)
        expected = [
            "handoff_note:missing_marker:The dedicated validator, the shared build companion, the governance-lane sequencing companions, and the directly materialized reminder-surface checkers now define the tighter same-lane boundaries, while the broader wrapper-route and shared-CI follow-through should only reopen when fresh drift actually appears."
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-marker failure: {failures}")
        case_count += 1

        missing_direct_root = root / "missing_direct"
        _seed_repo(missing_direct_root)
        (missing_direct_root / "zigux/tests/phase15_handoff_next_steps.zig").unlink()
        failures = collect_failures(missing_direct_root)
        expected = ["repo:missing_direct_path:zigux/tests/phase15_handoff_next_steps.zig"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-direct failure: {failures}")
        case_count += 1

        missing_broad_root = root / "missing_broad"
        _seed_repo(missing_broad_root)
        _write(
            missing_broad_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "- the broad docs-root reminder surface `Documentation/zigux/README.md`, which still stops at Phase 14 on current `master` and should stay treated as an active shared-summary gap source until a dedicated Phase 15 docs-root reminder lands and aligns with `scripts/zigux/check-phase15-docs-readme-alignment.py` plus the directly materialized governance packet\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_broad_root)
        expected = ["handoff_note:missing_broad_marker:Documentation/zigux/README.md"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-broad-marker failure: {failures}")
        case_count += 1

        stale_root = root / "stale"
        _seed_repo(stale_root)
        _write(
            stale_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace("PHASE15_LANE_KEY=P15-L12", "PHASE15_LANE_KEY=P15-L11", 1),
        )
        failures = collect_failures(stale_root)
        expected = [
            "handoff_note:missing_status:PHASE15_LANE_KEY=P15-L12",
            "handoff_note:stale_marker:PHASE15_LANE_KEY=P15-L11",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected stale-marker failure: {failures}")
        case_count += 1

    print("PHASE15_HANDOFF_NEXT_STEPS_SURVEY_SELF_TEST=pass")
    print(f"PHASE15_HANDOFF_NEXT_STEPS_SURVEY_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 handoff-next-steps note stays aligned with the current governance packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        failures = collect_failures(args.root)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE15_HANDOFF_NEXT_STEPS_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
