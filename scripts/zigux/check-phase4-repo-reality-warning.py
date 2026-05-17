#!/usr/bin/env python3
"""Guard the current-head Phase 4 reversible-delivery note packet."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
CHECKLIST = Path("Documentation/zigux/review-checklist.md")
README = Path("zigux/tests/README.md")

DIRECT_READBACK_PACKET = (
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/check-phase4-perf-baseline-packet.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "scripts/zigux/validate-phase4.py",
    "zigux/tests/phase4_build.zig",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
)

NOTE_REQ = (
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "The tests-root guide should mirror this same current-head posture.",
    "The next honest same-family follow-through is to refresh the stale repo-reality warning in `zigux/tests/README.md`",
    "The live repo-reality gap in this note is therefore stale provenance, not path absence",
    "leaving the `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` provenance fields intact",
)

README_PENDING_REQ = (
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "repo-reality warning for the broader Phase 4 packet",
    "last-known packet members",
)

CHECKLIST_PENDING_REQ = (
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "Validation and Perf Team as the decision owner for any broader shared-CI perf promotion",
    "ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call",
    "pending shared-CI perf-promotion posture explicit",
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
        raise RuntimeError(f"missing required file: {rel}") from exc


def require(text: str, parts: tuple[str, ...], label: str) -> None:
    missing = [part for part in parts if part not in text]
    if missing:
        raise RuntimeError(f"{label} is missing required fragments: {missing}")


def check(root: Path) -> None:
    note = read(root, NOTE)
    checklist = read(root, CHECKLIST)
    readme = read(root, README)
    require(note, NOTE_REQ + DIRECT_READBACK_PACKET, "phase4 note")
    require(readme, README_PENDING_REQ, "tests README")
    require(checklist, CHECKLIST_PENDING_REQ, "review checklist")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_root(root: Path) -> None:
    direct = ", ".join(f"`{item}`" for item in DIRECT_READBACK_PACKET)
    write(
        root / NOTE,
        "# Phase 4 Reversible Delivery Evidence\n\n"
        "Current direct readback in this run confirmed this note, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, "
        f"and {direct} on current `master`. The live repo-reality gap in this note is therefore stale provenance, not path absence: "
        "the `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines still record the older blob-pin packet and should stay framed as historical provenance until a separate exact-pin refresh rereads every companion blob value together.\n\n"
        "The tests-root guide should mirror this same current-head posture.\n\n"
        "The next honest same-family follow-through is to refresh the stale repo-reality warning in `zigux/tests/README.md`, "
        "then run the dedicated exact-pin pass across the directly readable validator, lab-matrix, and local-only perf companions while leaving the `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` provenance fields intact until that broader blob refresh lands.\n",
    )
    write(
        root / README,
        "# zigux/tests\n\n"
        "  * current direct-readback Phase 4 rollback packet:\n"
        "    `Documentation/zigux/phase4-reversible-delivery-evidence.md`\n"
        "    `Documentation/zigux/review-checklist.md`\n"
        "    `zigux/tests/README.md`\n"
        "  * repo-reality warning for the broader Phase 4 packet: keep the older validator, lab-matrix, and dedicated local-only perf inventory framed as last-known packet members until the tests-root wording is refreshed from the current-head note\n"
        "  * Phase 4 follow-through should treat those paths as last-known packet members that require fresh reread or re-materialization before they are presented as shipped direct evidence again\n",
    )
    write(
        root / CHECKLIST,
        "# Zigux Review Checklist\n\n"
        "  * if the change touches the shared Phase 4 rollback-ownership and lab-matrix packet, do `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md` still agree on the current direct-readback packet, keep the repo-reality warning explicit for the missing broader Phase 4 validator, lab-matrix, and local-only perf companions, keep the host-side artifact-diff contract plus remaining-gap wording truthful, keep the parked kprobe and parked `test_fsmount` reminder packet framed as last-known packet members rather than current direct evidence, keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion, keep the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call, and keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval?\n",
    )


def self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase4-repo-reality-") as tmp:
        root = Path(tmp)
        fixture_root(root)
        check(root)
        cases += 1

        write(root / NOTE, read(root, NOTE).replace(DIRECT_READBACK_PACKET[0], "Documentation/zigux/not-the-right-file.md"))
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected note direct-readback drift to fail")

        fixture_root(root)
        write(root / README, read(root, README).replace(README_PENDING_REQ[3], "broader packet wording drifted"))
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected README marker drift to fail")

        fixture_root(root)
        write(root / CHECKLIST, read(root, CHECKLIST).replace(CHECKLIST_PENDING_REQ[3], "different owner wording"))
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected checklist owner drift to fail")

    print("PHASE4_REPO_REALITY_WARNING_SELF_TEST=pass")
    print(f"PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES={cases}")


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    try:
        check(args.root.resolve())
    except RuntimeError as exc:
        print(f"PHASE4_REPO_REALITY_WARNING=fail: {exc}", file=sys.stderr)
        return 1
    print("PHASE4_REPO_REALITY_WARNING=pass")
    print("PHASE4_REPO_REALITY_WARNING_DIRECT_READBACK_FILES=12")
    print("PHASE4_REPO_REALITY_WARNING_PENDING_SURFACES=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
