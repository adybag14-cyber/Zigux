#!/usr/bin/env python3
"""Guard the current-head Phase 4 repo-reality warning packet."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
CHECKLIST = Path("Documentation/zigux/review-checklist.md")
README = Path("zigux/tests/README.md")

MISSING = (
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
    "The next honest same-family follow-through is one shared-packet truthfulness repair for `Documentation/zigux/review-checklist.md`",
)
README_REQ = (
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "repo-reality warning for the broader Phase 4 packet",
    "last-known packet members",
)
CHECKLIST_REQ = (
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "missing broader Phase 4 validator, lab-matrix, and local-only perf companions",
    "Validation and Perf Team as the decision owner for any broader shared-CI perf promotion",
    "ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call",
    "pending shared-CI perf-promotion posture explicit",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
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
    require(note, NOTE_REQ + MISSING, "phase4 note")
    require(readme, README_REQ + MISSING, "tests README")
    require(checklist, CHECKLIST_REQ, "review checklist")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_root(root: Path) -> None:
    missing = ", ".join(f"`{item}`" for item in MISSING)
    write(
        root / NOTE,
        "# Phase 4 Reversible Delivery Evidence\n\n"
        "Current direct readback in this run confirmed this note, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md`.\n\n"
        f"Several older companion paths named by earlier Phase 4 packet history currently returned missing contents reads on `master`, including {missing}. Keep those paths as last-known packet members that require a fresh reread or re-materialization before they are treated as shipped evidence again.\n\n"
        "The tests-root guide should mirror this same current-head posture.\n\n"
        "The next honest same-family follow-through is one shared-packet truthfulness repair for `Documentation/zigux/review-checklist.md`, then either re-materialize the missing `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, and dedicated local-only perf companions on `master`, or narrow the remaining shared reminders so they stop claiming those missing paths are current direct evidence.\n",
    )
    write(
        root / README,
        "# zigux/tests\n\n"
        "  * current direct-readback Phase 4 rollback packet:\n"
        "    `Documentation/zigux/phase4-reversible-delivery-evidence.md`\n"
        "    `Documentation/zigux/review-checklist.md`\n"
        "    `zigux/tests/README.md`\n"
        f"  * repo-reality warning for the broader Phase 4 packet: {missing}\n"
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

        write(root / README, read(root, README).replace(MISSING[0], "Documentation/zigux/not-the-right-file.md"))
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected README mismatch to fail")

        fixture_root(root)
        write(root / NOTE, read(root, NOTE).replace(NOTE_REQ[2], "The tests-root guide drifted away from this packet."))
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected note marker mismatch to fail")

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
    print("PHASE4_REPO_REALITY_WARNING_DIRECT_READBACK_FILES=3")
    print(f"PHASE4_REPO_REALITY_WARNING_MISSING_PACKET_FILES={len(MISSING)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
