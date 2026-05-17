#!/usr/bin/env python3
"""Guard the parked Phase 4 validator exactness handoff against repo reality."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

NOTE = Path("Documentation/zigux/phase4-validator-gate-evidence-exactness-gap.md")
LIVE_HANDOFF = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
REPO_WARNING = Path("scripts/zigux/check-phase4-repo-reality-warning.py")

NOTE_MARKERS = (
    "`PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP=present`",
    "`PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_LANE_KEY=validation-perf`",
    "`PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_SCOPE=validator_local_truthfulness_only`",
    "`PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_STATUS_BUCKET=historical_followthrough_waiting_for_republish`",
    "`PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_OWNER=Validation and Perf Team`",
    "`PHASE4_VALIDATOR_TARGET=scripts/zigux/validate-phase4.py`",
    "`PHASE4_VALIDATOR_LAST_KNOWN_BLOB_SHA=694ad85743612aa0a595cd1752dd03c1013603ab`",
    "`PHASE4_GATE_EVIDENCE_LAST_KNOWN_NOTE=Documentation/zigux/phase4-gate-evidence.md`",
    "`PHASE4_GATE_EVIDENCE_LAST_KNOWN_BLOB_SHA=8f604959c5250433c5fca14b20d7ff75341c8d33`",
    "Current `master` no longer exposes direct authenticated readback for",
    "`Documentation/zigux/phase4-reversible-delivery-evidence.md`",
    "`scripts/zigux/check-phase4-repo-reality-warning.py`",
    "`scripts/zigux/check-phase4-reversible-delivery-pins.py`",
    "historical parked follow-through",
    "not current-head proof today",
    "Reopen this validator-local exactness follow-through only after a same-family",
)

LIVE_HANDOFF_MARKERS = (
    "`Documentation/zigux/phase4-gate-evidence.md`",
    "`scripts/zigux/validate-phase4.py`",
    "repo-reality gaps in this run",
    "historical provenance, not current-head proof",
)

REPO_WARNING_MARKERS = (
    '"Documentation/zigux/phase4-gate-evidence.md"',
    '"scripts/zigux/validate-phase4.py"',
    "repo-reality gaps in this run",
)

STALE_NOTE_MARKERS = (
    "Current `master` already records the exact Phase 4 gate-evidence contract in",
    "But current `master` still keeps the shared validator prefix-only",
    "Inside `REQUIRED_GATE_EVIDENCE_MARKERS`, the shared validator still accepts:",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def read(root: Path, rel: Path) -> str:
    try:
        return (root / rel).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing required file: {rel.as_posix()}") from exc


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise RuntimeError(f"{label} is missing required fragments: {missing}")


def require_absent_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    present = [marker for marker in markers if marker in text]
    if present:
        raise RuntimeError(f"{label} still carries stale current-head claims: {present}")


def check(root: Path) -> None:
    note = read(root, NOTE)
    live_handoff = read(root, LIVE_HANDOFF)
    repo_warning = read(root, REPO_WARNING)
    require_markers(note, NOTE_MARKERS, NOTE.as_posix())
    require_markers(live_handoff, LIVE_HANDOFF_MARKERS, LIVE_HANDOFF.as_posix())
    require_markers(repo_warning, REPO_WARNING_MARKERS, REPO_WARNING.as_posix())
    require_absent_markers(note, STALE_NOTE_MARKERS, NOTE.as_posix())


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_root(root: Path) -> None:
    write(
        root / NOTE,
        """# Phase 4 Validator Gate-Evidence Exactness Gap

## Status

- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP=present`
- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_LANE_KEY=validation-perf`
- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_SCOPE=validator_local_truthfulness_only`
- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_STATUS_BUCKET=historical_followthrough_waiting_for_republish`
- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_OWNER=Validation and Perf Team`
- `PHASE4_VALIDATOR_TARGET=scripts/zigux/validate-phase4.py`
- `PHASE4_VALIDATOR_LAST_KNOWN_BLOB_SHA=694ad85743612aa0a595cd1752dd03c1013603ab`
- `PHASE4_GATE_EVIDENCE_LAST_KNOWN_NOTE=Documentation/zigux/phase4-gate-evidence.md`
- `PHASE4_GATE_EVIDENCE_LAST_KNOWN_BLOB_SHA=8f604959c5250433c5fca14b20d7ff75341c8d33`

This note now records a historical parked follow-through, not a current-head exactness claim.
Current `master` no longer exposes direct authenticated readback for the validator pair.
The live repo-reality packet is `Documentation/zigux/phase4-reversible-delivery-evidence.md`,
`scripts/zigux/check-phase4-repo-reality-warning.py`, and
`scripts/zigux/check-phase4-reversible-delivery-pins.py`.
That keeps the last-known validator and gate-evidence blob SHAs reviewable while this work is
not current-head proof today.

Reopen this validator-local exactness follow-through only after a same-family lane republishes
the missing pair.
""",
    )
    write(
        root / LIVE_HANDOFF,
        """# Phase 4 Reversible Delivery Evidence

The broader packet still treats `Documentation/zigux/phase4-gate-evidence.md` and
`scripts/zigux/validate-phase4.py` as repo-reality gaps in this run, so their older exact
blob pins remain historical provenance, not current-head proof.
""",
    )
    write(
        root / REPO_WARNING,
        """#!/usr/bin/env python3
MISSING_BROADER_PACKET = (
    "Documentation/zigux/phase4-gate-evidence.md",
    "scripts/zigux/validate-phase4.py",
)
NOTE_REQ = (
    "repo-reality gaps in this run",
)
""",
    )


def self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase4-gap-note-") as tmp:
        root = Path(tmp)
        fixture_root(root)
        check(root)
        cases += 1

        write(
            root / NOTE,
            read(root, NOTE).replace(
                "`PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_STATUS_BUCKET=historical_followthrough_waiting_for_republish`",
                "`PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_STATUS_BUCKET=shared_validator_prefix_drift`",
            ),
        )
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected status bucket drift to fail")

        fixture_root(root)
        write(
            root / NOTE,
            read(root, NOTE).replace(
                "historical parked follow-through",
                "current-head exactness claim",
            ),
        )
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected historical posture drift to fail")

        fixture_root(root)
        write(
            root / NOTE,
            read(root, NOTE)
            + "\nCurrent `master` already records the exact Phase 4 gate-evidence contract in the live note.\n",
        )
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected stale current-head claim to fail")

        fixture_root(root)
        write(
            root / REPO_WARNING,
            read(root, REPO_WARNING).replace(
                '"scripts/zigux/validate-phase4.py"',
                '"scripts/zigux/not-the-right-file.py"',
            ),
        )
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected repo-warning drift to fail")

        fixture_root(root)
        write(
            root / LIVE_HANDOFF,
            read(root, LIVE_HANDOFF).replace(
                "historical provenance, not current-head proof",
                "fresh current-head proof",
            ),
        )
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected live handoff drift to fail")

    print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_SELF_TEST=pass")
    print(f"PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_SELF_TEST_CASES={cases}")


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    try:
        check(args.root.resolve())
    except RuntimeError as exc:
        print(
            f"PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP=fail: {exc}",
            file=sys.stderr,
        )
        return 1
    print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
