#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
NOTE_PATH = "Documentation/zigux/phase14-skbuff-bridge-survey.md"

GUARDRAIL_MARKER = (
    "- manifest-backed guardrail: `phase14-skbuff-stay-in-c-guardrail` keeps this "
    "review-only packet fail-closed until the same packet carries explicit reopen "
    "evidence instead of lighter bridge-presence wording"
)
REQUIRED_EVIDENCE_HEADING = "- required evidence before any status review:"
REQUIRED_EVIDENCE_MARKERS = [
    "- `Architecture Council` reopen record linked from the active skbuff packet",
    "- parity scorecard evidence and benchmark notes attached to the same skbuff packet",
    "- validation replay command and evidence archive path recorded beside the latest blocker disposition",
]
RETURN_TO_BLOCKED_HEADING = "- automatic return-to-blocked triggers:"
RETURN_TO_BLOCKED_MARKERS = [
    "- any `net/core/skbuff_bridge.zig` claim or status review that drops `phase14-skbuff-live-ownership-blocker`",
    "- missing qdisc-facing publication, checksum ownership, segmentation metadata, zerocopy fragment orphaning, shared-frag ownership transfer, destructor ordering, or final sock-owned tail transfer wording in the active skbuff packet",
    "- any bridge-presence wording that upgrades the packet into parity, runtime ownership, or a freeze-map status change without the required reopen evidence",
]
NEXT_STEP_COORDINATION_MARKERS = [
    "Leave this lane parked unless a future current-`master` reread finds another survey-only drift against the live skbuff bridge packet or the Phase 14 roadmap.",
    "If the packet ever moves toward status review, update this note and `scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py` together before any broader shared Phase 14 reminder surface repeats the claim.",
]


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / NOTE_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

REQUIRED_MARKERS = [
    "`PHASE14_LANE_KEY=P14-L11`",
    "`PHASE14_BLOCKED_GAP=phase14-skbuff-live-ownership-blocker`",
    "`PHASE14_POSTURE=boundary_map_only`",
    "current `master` ships the bounded skbuff anchor packet again through `net/core/skbuff_bridge.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_skbuff_bridge_manifest.json`, and `zigux/tests/phase14_build.zig`",
    "explicit stay-in-C ownership for qdisc-facing publication, queue ownership, skb lifetime ownership, checksum ownership, destructor coordination, segmentation metadata, zerocopy fragment orphaning, shared-frag ownership transfer, and the final sock-owned tail transfer remains the Phase 14 boundary",
    "`zigux/tests/phase14_build.zig` wires `../../net/core/skbuff_bridge.zig` and `phase14_skbuff_bridge.zig` into the dedicated Phase 14 build shard, so there is now a live skbuff-local review route on current `master`",
    "The live bridge packet therefore remains review-only boundary evidence, not a delivery, parity, or ownership-transfer claim.",
    "`validate_xmit_skb_list()`, qdisc-facing publication, checksum ownership, segmentation metadata, destructor ordering, zerocopy fragment orphaning, `skb_orphan_frags()`, `skb_zerocopy_clone()`, `SKBFL_SHARED_FRAG`, `sock_wfree`, `tail->destructor`, `tail->sk`, `tail->next`, `segs->prev`, `skb_mark_not_on_list()`, `tail = skb->prev`, and the final sock-owned tail transfer must remain named as C-owned review points",
    "`phase14-skbuff-stay-in-c-guardrail`",
    GUARDRAIL_MARKER,
    "`scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py`",
    "rollback owner: `Repo Tooling Pod`",
    REQUIRED_EVIDENCE_HEADING,
    *REQUIRED_EVIDENCE_MARKERS,
    RETURN_TO_BLOCKED_HEADING,
    *RETURN_TO_BLOCKED_MARKERS,
    *NEXT_STEP_COORDINATION_MARKERS,
]


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    note = root / NOTE_PATH
    if not note.exists():
        return [f"missing_file:{NOTE_PATH}"]

    text = note.read_text(encoding="utf-8")
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            failures.append(f"missing_marker:{marker}")
    guard_phrases = [
        "status change, parity claim, or ownership transfer",
        "delivery, parity, or ownership-transfer claim",
    ]
    if not any(phrase in text for phrase in guard_phrases):
        failures.append("missing_guard_phrase:no_parity_or_ownership_transfer")
    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


FIXTURE_NOTE = """# Phase 14 Skbuff Bridge Survey
This document records the bounded Phase 14 survey lane around `net/core/skbuff.c`.

## Status
- `PHASE14_LANE_KEY=P14-L11`
- `PHASE14_PREVIOUS_PACKET_LANE=P14-Y03`
- `PHASE14_BLOCKED_GAP=phase14-skbuff-live-ownership-blocker`
- `PHASE14_POSTURE=boundary_map_only`
- current `master` ships the bounded skbuff anchor packet again through `net/core/skbuff_bridge.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_skbuff_bridge_manifest.json`, and `zigux/tests/phase14_build.zig`
- `phase14-skbuff-live-ownership-blocker` is the live Phase 14 blocker: the review-only packet exists, but it still records explicit stay-in-C ownership rather than a parity or runtime-ownership transfer
- the previous absent-anchor wording is no longer truthful on current `master` and must not be used as a substitute for reading the returned bridge-local packet
- explicit stay-in-C ownership for qdisc-facing publication, queue ownership, skb lifetime ownership, checksum ownership, destructor coordination, segmentation metadata, zerocopy fragment orphaning, shared-frag ownership transfer, and the final sock-owned tail transfer remains the Phase 14 boundary

## Boundary Reading
The live bridge packet therefore remains review-only boundary evidence, not a delivery, parity, or ownership-transfer claim.

## Compile Evidence
- `zigux/tests/phase14_build.zig` wires `../../net/core/skbuff_bridge.zig` and `phase14_skbuff_bridge.zig` into the dedicated Phase 14 build shard, so there is now a live skbuff-local review route on current `master`

## Gates
3. keep the blocked consumer-tail contract explicit
   - `validate_xmit_skb_list()`, qdisc-facing publication, checksum ownership, segmentation metadata, destructor ordering, zerocopy fragment orphaning, `skb_orphan_frags()`, `skb_zerocopy_clone()`, `SKBFL_SHARED_FRAG`, `sock_wfree`, `tail->destructor`, `tail->sk`, `tail->next`, `segs->prev`, `skb_mark_not_on_list()`, `tail = skb->prev`, and the final sock-owned tail transfer must remain named as C-owned review points

## Stay-In-C Guardrail
""" + GUARDRAIL_MARKER + """
- machine-check surface: `scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py` keeps the dedicated note fail-closed on its lane key, blocked gap, review-only posture, live-packet wording, and required stay-in-C evidence
- rollback owner: `Repo Tooling Pod`
""" + REQUIRED_EVIDENCE_HEADING + """
""" + "\n".join(f"  {marker}" for marker in REQUIRED_EVIDENCE_MARKERS) + """
""" + RETURN_TO_BLOCKED_HEADING + """
""" + "\n".join(f"  {marker}" for marker in RETURN_TO_BLOCKED_MARKERS) + """

## Next bounded step
""" + "\n".join(NEXT_STEP_COORDINATION_MARKERS) + """
"""


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-skbuff-guardrail-"))
    try:
        write_text(base / NOTE_PATH, FIXTURE_NOTE)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture should pass but failed: {failures!r}")

        cases = [
            ("remove-lane-key", "`PHASE14_LANE_KEY=P14-L11`", "missing_marker:`PHASE14_LANE_KEY=P14-L11`"),
            (
                "remove-blocked-gap",
                "`PHASE14_BLOCKED_GAP=phase14-skbuff-live-ownership-blocker`",
                "missing_marker:`PHASE14_BLOCKED_GAP=phase14-skbuff-live-ownership-blocker`",
            ),
            (
                "remove-guardrail-marker",
                GUARDRAIL_MARKER,
                f"missing_marker:{GUARDRAIL_MARKER}",
            ),
            (
                "remove-required-evidence-heading",
                REQUIRED_EVIDENCE_HEADING,
                f"missing_marker:{REQUIRED_EVIDENCE_HEADING}",
            ),
            (
                "remove-return-trigger",
                RETURN_TO_BLOCKED_MARKERS[0],
                f"missing_marker:{RETURN_TO_BLOCKED_MARKERS[0]}",
            ),
            (
                "remove-next-step-coordination",
                NEXT_STEP_COORDINATION_MARKERS[1],
                f"missing_marker:{NEXT_STEP_COORDINATION_MARKERS[1]}",
            ),
        ]
        for _, marker, expected in cases:
            write_text(base / NOTE_PATH, FIXTURE_NOTE.replace(marker, "", 1))
            failures = validate(base)
            if expected not in failures:
                raise SystemExit(f"expected {expected!r}, got {failures!r}")

        write_text(
            base / NOTE_PATH,
            FIXTURE_NOTE.replace(
                "The live bridge packet therefore remains review-only boundary evidence, not a delivery, parity, or ownership-transfer claim.",
                "The live bridge packet therefore remains review-only boundary evidence.",
                1,
            ),
        )
        failures = validate(base)
        if "missing_guard_phrase:no_parity_or_ownership_transfer" not in failures:
            raise SystemExit(f"expected guard phrase failure, got {failures!r}")

        print("PHASE14_SKBUFF_STAY_IN_C_GUARDRAIL_SELF_TEST=pass")
        print("PHASE14_SKBUFF_STAY_IN_C_GUARDRAIL_SELF_TEST_CASE_COUNT=7")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the dedicated Phase 14 skbuff survey stays aligned with the "
            "current review-only stay-in-C guardrail wording."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run the fixture-backed self-test.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE14_SKBUFF_STAY_IN_C_GUARDRAIL=fail")
        print("PHASE14_SKBUFF_STAY_IN_C_GUARDRAIL_DRIFT_START")
        for failure in failures:
            print(failure)
        print("PHASE14_SKBUFF_STAY_IN_C_GUARDRAIL_DRIFT_END")
        return 1

    print("PHASE14_SKBUFF_STAY_IN_C_GUARDRAIL=pass")
    print(f"PHASE14_SKBUFF_STAY_IN_C_GUARDRAIL_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
