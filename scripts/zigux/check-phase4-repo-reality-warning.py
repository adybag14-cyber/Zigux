#!/usr/bin/env python3
"""Guard the current-head Phase 4 reversible-delivery repo-reality packet."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
CHECKLIST = Path("Documentation/zigux/review-checklist.md")
README = Path("zigux/tests/README.md")

DIRECT_READBACK_PACKET = (
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
)

MISSING_BROADER_PACKET = (
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/check-phase4-perf-baseline-packet.py",
    "scripts/zigux/validate-phase4.py",
    "zigux/tests/phase4_build.zig",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
)

NOTE_REQ = (
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "The broader Phase 4 validator, lab-matrix, and local-only perf companions are still repo-reality gaps in this run",
    "The `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines therefore remain historical provenance, not current-head proof",
    "The Phase 4 repo-reality warning in `zigux/tests/README.md` should stay open",
    "`PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
    "`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=4`",
)

README_PENDING_REQ = (
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "repo-reality warning for the broader Phase 4 validator, lab-matrix, and local-only perf packet",
    "historical provenance for that missing broader packet",
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


def _require_current_repo_reality(root: Path) -> None:
    missing_direct = [
        rel for rel in DIRECT_READBACK_PACKET if not (root / Path(rel)).exists()
    ]
    if missing_direct:
        raise RuntimeError(
            "direct-readback packet no longer matches the current tree: "
            + ", ".join(missing_direct)
        )

    present_broader = [
        rel for rel in MISSING_BROADER_PACKET if (root / Path(rel)).exists()
    ]
    if present_broader:
        raise RuntimeError(
            "broader packet entries are now present and the repo-reality warning must be narrowed: "
            + ", ".join(present_broader)
        )


def check(root: Path) -> None:
    note = read(root, NOTE)
    checklist = read(root, CHECKLIST)
    readme = read(root, README)
    require(note, NOTE_REQ + DIRECT_READBACK_PACKET + MISSING_BROADER_PACKET, "phase4 note")
    require(readme, README_PENDING_REQ + MISSING_BROADER_PACKET, "tests README")
    require(checklist, CHECKLIST_PENDING_REQ, "review checklist")
    _require_current_repo_reality(root)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_root(root: Path) -> None:
    direct = ", ".join(f"`{item}`" for item in DIRECT_READBACK_PACKET)
    missing = ", ".join(f"`{item}`" for item in MISSING_BROADER_PACKET)
    write(
        root / NOTE,
        "# Phase 4 Reversible Delivery Evidence\n\n"
        "Current direct readback in this run confirmed "
        f"{direct} on current `master`. The broader Phase 4 validator, lab-matrix, and local-only perf companions are still repo-reality gaps in this run: authenticated contents reads returned missing for {missing}. The `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines therefore remain historical provenance, not current-head proof.\n\n"
        "The Phase 4 repo-reality warning in `zigux/tests/README.md` should stay open until that broader packet is directly readable again.\n\n"
        "* `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`\n"
        "* `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=4`\n",
    )
    write(
        root / README,
        "# zigux/tests\n\n"
        "  * current direct-readback Phase 4 rollback packet: `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, and `scripts/zigux/check-phase4-reversible-delivery-pins.py`\n"
        f"  * repo-reality warning for the broader Phase 4 validator, lab-matrix, and local-only perf packet: authenticated contents reads still return missing for {missing}\n"
        "  * Phase 4 follow-through should treat the stale `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines in `Documentation/zigux/phase4-reversible-delivery-evidence.md` as historical provenance for that missing broader packet\n",
    )
    write(
        root / CHECKLIST,
        "# Zigux Review Checklist\n\n"
        "  * if the change touches the shared Phase 4 rollback-ownership and lab-matrix packet, do `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md` still agree on the current direct-readback packet, keep the repo-reality warning explicit for the missing broader Phase 4 validator, lab-matrix, and local-only perf companions, keep the host-side artifact-diff contract plus remaining-gap wording truthful, keep the parked kprobe and parked `test_fsmount` reminder packet framed as last-known packet members rather than current direct evidence, keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion, keep the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call, and keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval?\n",
    )
    write(root / Path(DIRECT_READBACK_PACKET[3]), "# current checker under test\n")
    write(root / Path(DIRECT_READBACK_PACKET[4]), "# sibling pin checker\n")


def self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase4-repo-reality-") as tmp:
        root = Path(tmp)
        fixture_root(root)
        check(root)
        cases += 1

        write(root / NOTE, read(root, NOTE).replace(MISSING_BROADER_PACKET[0], "Documentation/zigux/not-the-right-file.md"))
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected note missing-packet drift to fail")

        fixture_root(root)
        write(root / README, read(root, README).replace(README_PENDING_REQ[5], "broader packet wording drifted"))
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

        fixture_root(root)
        (root / Path(DIRECT_READBACK_PACKET[4])).unlink()
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected missing direct-readback file to fail")

        fixture_root(root)
        write(root / Path(MISSING_BROADER_PACKET[0]), "# returned broader packet member\n")
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected present broader packet file to fail")

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
    print(f"PHASE4_REPO_REALITY_WARNING_DIRECT_READBACK_FILES={len(DIRECT_READBACK_PACKET)}")
    print(f"PHASE4_REPO_REALITY_WARNING_MISSING_BROADER_COMPANIONS={len(MISSING_BROADER_PACKET)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
