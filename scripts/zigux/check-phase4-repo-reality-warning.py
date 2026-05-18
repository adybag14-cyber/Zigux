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
SELF = Path("scripts/zigux/check-phase4-repo-reality-warning.py")
PINS = Path("scripts/zigux/check-phase4-reversible-delivery-pins.py")
PERF_BASELINE_CHECKER = Path("scripts/zigux/check-phase4-perf-baseline-packet.py")

DIRECT_READBACK_PACKET = (
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
)

RECOVERED_NOTE_PACKET = (
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/phase4-validation-matrix.md",
)

REMAINING_GAP_PACKET = (
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/check-phase4-remaining-gap-matrix.py",
    "scripts/zigux/validate-phase4.py",
    "zigux/tests/phase4_build.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
)

PIN_SELF_TEST_COUNT_LABEL = "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT"
REPO_REALITY_WARNING_SELF_TEST_COUNT_LABEL = "PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES"
EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 16
EXPECTED_PIN_SELF_TEST_CASES = 12
PERF_CHECKER_MARKER = (
    "Current direct-readback dedicated local-only perf checker: "
    "`scripts/zigux/check-phase4-perf-baseline-packet.py`"
)

NOTE_REQ = (
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md` and `Documentation/zigux/phase4-validation-matrix.md` on current `master`",
    "The broader Phase 4 checker, validator, build, and bitmap replay companions are still repo-reality gaps in this run",
    "The `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines therefore remain mixed provenance in this handoff",
    "The remaining shared reminder follow-up from the older mixed-readback packet is now closed: `zigux/tests/README.md` now aligns with `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `Documentation/zigux/review-checklist.md` on the recovered note pair, the direct local-only perf packet, and the roadmap-backed `atomic64_diff` pair, while the broader checker, validator, build, and bitmap replay companions remain the only authenticated-readback gaps in this handoff",
    "scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair explicit as direct current-head evidence",
    "`PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
    "The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=16` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=12` here",
    PERF_CHECKER_MARKER,
)

README_PHASE4_REQ = (
    "current direct-readback Phase 4 rollback packet:",
    "Current direct-readback dedicated local-only perf checker: `scripts/zigux/check-phase4-perf-baseline-packet.py`",
    "Current direct-readback dedicated local-only perf companion members: `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`",
    "recovered current-head broader Phase 4 note companions: `Documentation/zigux/phase4-gate-evidence.md` and `Documentation/zigux/phase4-validation-matrix.md`",
    "repo-reality warning for the still-unreadable broader Phase 4 validator, checker, and bitmap-diff packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig`",
    "roadmap-backed Phase 4 differential-gate destinations directly readable on current `master`: `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig`",
    "current shared Phase 4 ownership reminder: keep rollback-owner wording, artifact-diff contract references, and remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md` instead of reconstructing the broader packet from older route names alone",
)

CHECKLIST_PHASE4_REQ = (
    "if the change touches the shared Phase 4 rollback-ownership and lab-matrix packet, do `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase4-repo-reality-warning.py` and `scripts/zigux/check-phase4-reversible-delivery-pins.py` still agree on the current direct-readback packet",
    "keep the directly readable local-only perf packet explicit",
    "keep the repo-reality warning explicit for the missing broader Phase 4 validator, lab-matrix, and bitmap-diff companions",
    "keep the roadmap-backed `atomic64_diff` pair explicit as direct current-head evidence",
    "keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion",
    "keep the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call",
    "keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval?",
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


def write(root: Path, rel: Path, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require(text: str, parts: tuple[str, ...], label: str) -> None:
    missing = [part for part in parts if part not in text]
    if missing:
        raise RuntimeError(f"{label} is missing required fragments: {missing}")


def require_exact_self_test_count(text: str, label: str, count_label: str, expected: int) -> None:
    matches = re.findall(rf"`{count_label}=(\d+)`", text)
    if not matches:
        raise RuntimeError(f"{label} is missing a numeric `{count_label}=...` marker")
    if any(int(value) != expected for value in matches):
        raise RuntimeError(f"{label} must carry `{count_label}={expected}` exactly")


def _require_direct_packet(root: Path) -> None:
    missing_direct = [rel for rel in DIRECT_READBACK_PACKET if not (root / Path(rel)).exists()]
    if not (root / PERF_BASELINE_CHECKER).exists():
        missing_direct.append(PERF_BASELINE_CHECKER.as_posix())
    for rel in (
        Path("zigux/tests/phase4_perf_baseline_manifest.json"),
        Path("zigux/tests/phase4_perf_baseline_survey.zig"),
        Path("Documentation/zigux/phase4-gate-evidence.md"),
        Path("Documentation/zigux/phase4-validation-matrix.md"),
    ):
        if not (root / rel).exists():
            missing_direct.append(rel.as_posix())
    if missing_direct:
        raise RuntimeError("direct-readback packet no longer matches the current tree: " + ", ".join(missing_direct))


def check(root: Path) -> None:
    note = read(root, NOTE)
    require(note, NOTE_REQ + DIRECT_READBACK_PACKET + RECOVERED_NOTE_PACKET + REMAINING_GAP_PACKET, "phase4 note")
    require(read(root, README), README_PHASE4_REQ, "phase4 tests readme")
    require(read(root, CHECKLIST), CHECKLIST_PHASE4_REQ, "phase4 review checklist")
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
    _require_direct_packet(root)


def baseline_note() -> str:
    direct_packet = ", ".join(f"`{item}`" for item in DIRECT_READBACK_PACKET)
    gap_packet = ", ".join(f"`{item}`" for item in REMAINING_GAP_PACKET)
    return "\\n".join([
        "# Phase 4 Reversible Delivery Evidence",
        "",
        f"Current direct readback in this run confirmed this note, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
        f"Current direct-readback packet members: {direct_packet}.",
        f"Current direct-readback dedicated local-only perf checker: `{PERF_BASELINE_CHECKER.as_posix()}`.",
        "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md` and `Documentation/zigux/phase4-validation-matrix.md` on current `master`.",
        "The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=16` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=12` here.",
        f"The broader Phase 4 checker, validator, build, and bitmap replay companions are still repo-reality gaps in this run: authenticated contents reads returned missing for {gap_packet}.",
        "The `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines therefore remain mixed provenance in this handoff.",
        "The remaining shared reminder follow-up from the older mixed-readback packet is now closed: `zigux/tests/README.md` now aligns with `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `Documentation/zigux/review-checklist.md` on the recovered note pair, the direct local-only perf packet, and the roadmap-backed `atomic64_diff` pair, while the broader checker, validator, build, and bitmap replay companions remain the only authenticated-readback gaps in this handoff.",
        "Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, and `scripts/zigux/check-phase4-artifact-diff-determinism.py`.",
        "Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair explicit as direct current-head evidence.",
        "`PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
        "`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=16`",
        "`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=12`",
    ]) + "\\n"


def baseline_tests_readme() -> str:
    return "\\n".join([
        "# zigux/tests",
        "",
        "  * current direct-readback Phase 4 rollback packet:",
        "    `Documentation/zigux/phase4-reversible-delivery-evidence.md`",
        "    `Documentation/zigux/review-checklist.md`",
        "    `zigux/tests/README.md`",
        "    `scripts/zigux/check-phase4-repo-reality-warning.py`",
        "    `scripts/zigux/check-phase4-reversible-delivery-pins.py`",
        "  * Current direct-readback dedicated local-only perf checker: `scripts/zigux/check-phase4-perf-baseline-packet.py`",
        "  * Current direct-readback dedicated local-only perf companion members: `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`",
        "  * recovered current-head broader Phase 4 note companions: `Documentation/zigux/phase4-gate-evidence.md` and `Documentation/zigux/phase4-validation-matrix.md`",
        "  * repo-reality warning for the still-unreadable broader Phase 4 validator, checker, and bitmap-diff packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig`",
        "  * roadmap-backed Phase 4 differential-gate destinations directly readable on current `master`: `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig`",
        "  * current shared Phase 4 ownership reminder: keep rollback-owner wording, artifact-diff contract references, and remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md` instead of reconstructing the broader packet from older route names alone",
    ]) + "\\n"


def baseline_checklist() -> str:
    return "\\n".join([
        "# Zigux Review Checklist",
        "",
        "  * if the change touches the shared Phase 4 rollback-ownership and lab-matrix packet, do `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase4-repo-reality-warning.py` and `scripts/zigux/check-phase4-reversible-delivery-pins.py` still agree on the current direct-readback packet, keep the directly readable local-only perf packet explicit, keep the repo-reality warning explicit for the missing broader Phase 4 validator, lab-matrix, and bitmap-diff companions, keep the roadmap-backed `atomic64_diff` pair explicit as direct current-head evidence, keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion, keep the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call, and keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval?",
    ]) + "\\n"


def build_baseline_tree(root: Path) -> None:
    write(root, NOTE, baseline_note())
    write(root, README, baseline_tests_readme())
    write(root, CHECKLIST, baseline_checklist())
    write(root, SELF, "# repo-reality warning checker placeholder\\n")
    write(root, PINS, "# reversible-delivery pin checker placeholder\\n")
    write(root, PERF_BASELINE_CHECKER, "# direct-readback perf checker placeholder\\n")
    write(root, Path("zigux/tests/phase4_perf_baseline_manifest.json"), "{}\\n")
    write(root, Path("zigux/tests/phase4_perf_baseline_survey.zig"), "// direct-readback perf survey placeholder\\n")
    write(root, Path("Documentation/zigux/phase4-gate-evidence.md"), "# gate evidence placeholder\\n")
    write(root, Path("Documentation/zigux/phase4-validation-matrix.md"), "# validation matrix placeholder\\n")


def main() -> int:
    args = parse_args()
    if args.self_test:
        cases = 0
        with tempfile.TemporaryDirectory(prefix="phase4-repo-reality-") as tmp:
            root = Path(tmp)
            build_baseline_tree(root)
            check(root)
            cases += 1

            build_baseline_tree(root)
            note_path = root / NOTE
            note_path.write_text(
                note_path.read_text(encoding="utf-8").replace(
                    "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md` and `Documentation/zigux/phase4-validation-matrix.md` on current `master`.",
                    "Current direct contents reads in this run also confirmed only one recovered note.",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected recovered-note wording drift to fail")

            build_baseline_tree(root)
            note_path = root / NOTE
            note_path.write_text(
                note_path.read_text(encoding="utf-8").replace(
                    "The broader Phase 4 checker, validator, build, and bitmap replay companions are still repo-reality gaps in this run",
                    "The broader Phase 4 validator and bitmap companions are still repo-reality gaps in this run",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected remaining-gap wording drift to fail")

            build_baseline_tree(root)
            note_path = root / NOTE
            note_path.write_text(
                note_path.read_text(encoding="utf-8").replace(
                    "`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=16`",
                    "`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=15`",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected repo-reality self-test count drift to fail")

            build_baseline_tree(root)
            note_path = root / NOTE
            note_path.write_text(
                note_path.read_text(encoding="utf-8").replace(
                    "`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=12`",
                    "`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=10`",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected pin self-test count drift to fail")

            build_baseline_tree(root)
            readme_path = root / README
            readme_path.write_text(
                readme_path.read_text(encoding="utf-8").replace(
                    "recovered current-head broader Phase 4 note companions: `Documentation/zigux/phase4-gate-evidence.md` and `Documentation/zigux/phase4-validation-matrix.md`",
                    "recovered current-head broader Phase 4 note companions: `Documentation/zigux/phase4-gate-evidence.md` only",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected tests-readme recovered-note marker drift to fail")

            build_baseline_tree(root)
            readme_path = root / README
            readme_path.write_text(
                readme_path.read_text(encoding="utf-8").replace(
                    "repo-reality warning for the still-unreadable broader Phase 4 validator, checker, and bitmap-diff packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig`",
                    "repo-reality warning for the broader Phase 4 packet has drifted",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected tests-readme remaining-gap marker drift to fail")

            build_baseline_tree(root)
            perf_survey = root / Path("zigux/tests/phase4_perf_baseline_survey.zig")
            perf_survey.unlink()
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected missing perf survey to fail")

            build_baseline_tree(root)
            note_path = root / NOTE
            note_path.write_text(
                note_path.read_text(encoding="utf-8").replace(
                    "Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` now return on current `master`",
                    "Current direct contents reads for the atomic64 pair drifted",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected atomic64 direct-readback wording drift to fail")

            build_baseline_tree(root)
            readme_path = root / README
            readme_path.write_text(
                readme_path.read_text(encoding="utf-8").replace(
                    "Current direct-readback dedicated local-only perf checker: `scripts/zigux/check-phase4-perf-baseline-packet.py`",
                    "Current direct-readback dedicated local-only perf checker: `scripts/zigux/check-phase4-perf-baseline-packet-drift.py`",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected tests-readme perf-checker drift to fail")

            build_baseline_tree(root)
            readme_path = root / README
            readme_path.write_text(
                readme_path.read_text(encoding="utf-8").replace(
                    "roadmap-backed Phase 4 differential-gate destinations directly readable on current `master`: `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig`",
                    "roadmap-backed Phase 4 differential-gate destinations are no longer direct current-head evidence",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected tests-readme atomic64 marker drift to fail")

            build_baseline_tree(root)
            checklist_path = root / CHECKLIST
            checklist_path.write_text(
                checklist_path.read_text(encoding="utf-8").replace(
                    "keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion",
                    "keep the ABI and Runtime Team as the decision owner for any broader shared-CI perf promotion",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected checklist decision-owner drift to fail")

            build_baseline_tree(root)
            checklist_path = root / CHECKLIST
            checklist_path.write_text(
                checklist_path.read_text(encoding="utf-8").replace(
                    "still agree on the current direct-readback packet",
                    "still agree on the current historical packet",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected checklist direct-readback drift to fail")

            build_baseline_tree(root)
            perf_manifest = root / Path("zigux/tests/phase4_perf_baseline_manifest.json")
            perf_manifest.unlink()
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected missing perf manifest to fail")

            build_baseline_tree(root)
            recovered_note = root / Path("Documentation/zigux/phase4-gate-evidence.md")
            recovered_note.unlink()
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected missing recovered note to fail")

            build_baseline_tree(root)
            note_path = root / NOTE
            note_path.write_text(
                note_path.read_text(encoding="utf-8").replace(
                    "The `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines therefore remain mixed provenance in this handoff.",
                    "The provenance wording drifted.",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected provenance wording drift to fail")

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