#!/usr/bin/env python3
"""Guard the current-head Phase 4 reversible-delivery repo-reality packet."""

from __future__ import annotations

import argparse
import re
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

PIN_SELF_TEST_COUNT_LABEL = "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT"
REPO_REALITY_WARNING_SELF_TEST_COUNT_LABEL = "PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES"
EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 4
EXPECTED_PIN_SELF_TEST_CASES = 5

NOTE_REQ = (
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-artifact-diff-contract.py",
    "The broader Phase 4 validator, lab-matrix, and local-only perf companions are still repo-reality gaps in this run",
    "The `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines therefore remain historical provenance, not current-head proof",
    "The Phase 4 repo-reality warning in `zigux/tests/README.md` should stay open",
    "`PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
    "The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=4` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=5` here",
)

README_OWNER_MARKERS = (
    "current shared Phase 4 ownership reminder: keep rollback-owner wording, artifact-diff contract references, and remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md` instead of reconstructing the broader packet from older route names alone",
    "historical Phase 4 route names such as the parked kprobe and `test_fsmount` survey companions, the validator-first routes, and the direct local-only perf routes stay owned by the reversible-delivery handoff note until the dedicated exact-pin refresh or a broader republish makes those companion blob values directly readable again",
)

README_PENDING_REQ = (
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "repo-reality warning for the broader Phase 4 validator, lab-matrix, and local-only perf packet",
    "historical provenance for that missing broader packet",
) + README_OWNER_MARKERS

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


def require_exact_self_test_count(
    text: str,
    label: str,
    count_label: str,
    expected: int,
) -> None:
    matches = re.findall(rf"`{count_label}=(\d+)`", text)
    if not matches:
        raise RuntimeError(
            f"{label} is missing a numeric `{count_label}=...` marker"
        )
    if any(int(value) != expected for value in matches):
        raise RuntimeError(
            f"{label} must carry `{count_label}={expected}` exactly"
        )


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
    require_exact_self_test_count(
        note,
        "phase4 note",
        REPO_REALITY_WARNING_SELF_TEST_COUNT_LABEL,
        EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES,
    )
    require_exact_self_test_count(
        note,
        "phase4 note",
        PIN_SELF_TEST_COUNT_LABEL,
        EXPECTED_PIN_SELF_TEST_CASES,
    )
    _require_current_repo_reality(root)


def main() -> int:
    args = parse_args()
    if args.self_test:
        cases = 0
        with tempfile.TemporaryDirectory(prefix="phase4-repo-reality-") as tmp:
            root = Path(tmp)
            for rel in (
                NOTE,
                README,
                CHECKLIST,
                Path("scripts/zigux/check-phase4-repo-reality-warning.py"),
                Path("scripts/zigux/check-phase4-reversible-delivery-pins.py"),
            ):
                src = args.root.resolve() / rel
                dst = root / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            check(root)
            cases += 1

            drifted = root / NOTE
            drifted.write_text(
                drifted.read_text(encoding="utf-8").replace(
                    "`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=5`",
                    "`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=zero`",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected non-numeric pin self-test count to fail")

            note_text = (args.root.resolve() / NOTE).read_text(encoding="utf-8")
            drifted.write_text(
                note_text.replace(
                    "`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=4`",
                    "`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=99`",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError(
                    "expected stale repo-reality warning self-test count to fail"
                )

            readme_text = (args.root.resolve() / README).read_text(encoding="utf-8")
            drifted.write_text(note_text, encoding="utf-8")
            (root / README).write_text(
                readme_text.replace(
                    README_OWNER_MARKERS[0],
                    "current shared ownership reminder drifted",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected README ownership reminder drift to fail")

        print("PHASE4_REPO_REALITY_WARNING_SELF_TEST=pass")
        print(f"PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES={cases}")
        return 0
    try:
        check(args.root.resolve())
    except RuntimeError as exc:
        print(f"PHASE4_REPO_REALITY_WARNING=fail: {exc}", file=sys.stderr)
        return 1
    print("PHASE4_REPO_REALITY_WARNING=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
