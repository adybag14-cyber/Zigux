#!/usr/bin/env python3
"""Guard the current-head Phase 4 validation-lane sequencing packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SEQUENCING_NOTE = Path("Documentation/zigux/phase4-validation-lane-sequencing.md")
REVERSIBLE_NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
REPO_WARNING = Path("scripts/zigux/check-phase4-repo-reality-warning.py")
PERF_PACKET = Path("scripts/zigux/check-phase4-perf-baseline-packet.py")

EXPECTED_SELF_TEST_CASES = 10

SEQUENCING_MARKERS = (
    "current direct-readback shared handoff:",
    "`scripts/zigux/check-phase4-repo-reality-warning.py`",
    "recovered broader shared exact-readback and owner-map companions that now reread directly on current `master`:",
    "`Documentation/zigux/phase4-validation-lane-sequencing.md`",
    "Current shared reminder ownership is narrower than that historical label: `P4-L24` now covers the matrix-side and sequencing-note reminder wording around `Documentation/zigux/phase4-validation-matrix.md` plus `scripts/zigux/check-phase4-remaining-gap-matrix.py`, while the live `P4-L19` lane now owns checker-local measurability follow-through",
    "If the drift is limited to the matrix-side or sequencing-note reminder surfaces around `scripts/zigux/check-phase4-remaining-gap-matrix.py`, keep it in the live `P4-L24` matrix reminder lane; if the drift is limited to the dedicated remaining-gap checker falling behind those already-landed markers, keep it in the live `P4-L19` checker-maintenance lane before reopening either parked starter-gap packet.",
    "reopen the dedicated perf lane only for one checker, manifest, survey, benchmark-command, acceptable-limit, or local-only policy truthfulness repair",
)

REVERSIBLE_MARKERS = (
    "Current direct readback in this run confirmed this note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-tests-readme-packet.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-perf-threshold-matrix.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
    "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`",
    "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.",
    "Current direct contents reads for `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`, and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` now return on current `master`",
)

REPO_WARNING_MARKERS = (
    'EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 32',
    'EXPECTED_PIN_SELF_TEST_CASES = 20',
    'SEQUENCING_NOTE = Path("Documentation/zigux/phase4-validation-lane-sequencing.md")',
    'REMAINING_GAP_PACKET = (',
    '    "scripts/zigux/validate-phase4.py",',
    '    "zigux/tests/phase4_build.zig",',
)

PERF_PACKET_MARKERS = (
    'EXPECTED_SELF_TEST_CASES = 38',
    'MANIFEST = Path("zigux/tests/phase4_perf_baseline_manifest.json")',
    'REVIEW_CHECKLIST_MARKERS = (',
    'NOTE_MARKERS = (',
    'Current direct-readback dedicated local-only perf checkers: `scripts/zigux/check-phase4-perf-baseline-packet.py` and `scripts/zigux/check-phase4-perf-threshold-matrix.py`.',
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def read(root: Path, rel: Path) -> str:
    path = root / rel
    if not path.is_file():
        raise RuntimeError(f"missing required file: {rel.as_posix()}")
    return path.read_text(encoding="utf-8")


def write(root: Path, rel: Path, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require(text: str, markers: tuple[str, ...], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise RuntimeError(f"{label} is missing required fragments: {missing}")


def check(root: Path) -> None:
    require(read(root, SEQUENCING_NOTE), SEQUENCING_MARKERS, SEQUENCING_NOTE.as_posix())
    require(read(root, REVERSIBLE_NOTE), REVERSIBLE_MARKERS, REVERSIBLE_NOTE.as_posix())
    require(read(root, REPO_WARNING), REPO_WARNING_MARKERS, REPO_WARNING.as_posix())
    require(read(root, PERF_PACKET), PERF_PACKET_MARKERS, PERF_PACKET.as_posix())


def build_fixture_tree(root: Path) -> None:
    write(root, SEQUENCING_NOTE, "\n".join(SEQUENCING_MARKERS) + "\n")
    write(root, REVERSIBLE_NOTE, "\n".join(REVERSIBLE_MARKERS) + "\n")
    write(root, REPO_WARNING, "\n".join(REPO_WARNING_MARKERS) + "\n")
    write(root, PERF_PACKET, "\n".join(PERF_PACKET_MARKERS) + "\n")


def expect_failure(root: Path, rel: Path, old: str | None = None, new: str | None = None) -> None:
    build_fixture_tree(root)
    target = root / rel
    if old is None:
        target.unlink()
    else:
        text = target.read_text(encoding="utf-8")
        if old not in text:
            raise AssertionError(f"missing replacement target: {old!r}")
        target.write_text(text.replace(old, new, 1), encoding="utf-8")
    try:
        check(root)
    except RuntimeError:
        return
    raise AssertionError(f"expected failure for {rel.as_posix()}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase4-validation-lane-sequencing-") as tmp:
        root = Path(tmp)
        build_fixture_tree(root)
        check(root)
        cases = 1

        expect_failure(root, SEQUENCING_NOTE, SEQUENCING_MARKERS[2], "historical broader shared exact-readback packet:")
        cases += 1
        expect_failure(root, SEQUENCING_NOTE, "checker-local measurability follow-through", "review-checklist reminder ownership")
        cases += 1
        expect_failure(root, REVERSIBLE_NOTE, REVERSIBLE_MARKERS[2], "The broader Phase 4 validator packet is still a current-master gap.")
        cases += 1
        expect_failure(root, REPO_WARNING, REPO_WARNING_MARKERS[0], 'EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 16')
        cases += 1
        expect_failure(root, PERF_PACKET, PERF_PACKET_MARKERS[0], 'EXPECTED_SELF_TEST_CASES = 13')
        cases += 1
        expect_failure(root, SEQUENCING_NOTE)
        cases += 1
        expect_failure(root, REVERSIBLE_NOTE)
        cases += 1
        expect_failure(root, REPO_WARNING)
        cases += 1
        expect_failure(root, PERF_PACKET)
        cases += 1

        if cases != EXPECTED_SELF_TEST_CASES:
            print("PHASE4_VALIDATION_LANE_SEQUENCING_SELF_TEST=fail")
            print(f"expected {EXPECTED_SELF_TEST_CASES} self-test cases, saw {cases}")
            return 1

    print("PHASE4_VALIDATION_LANE_SEQUENCING_SELF_TEST=pass")
    print(f"PHASE4_VALIDATION_LANE_SEQUENCING_SELF_TEST_CASES={EXPECTED_SELF_TEST_CASES}")
    return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    try:
        check(args.root.resolve())
    except RuntimeError as exc:
        print(f"PHASE4_VALIDATION_LANE_SEQUENCING_CHECK=fail: {exc}")
        return 1
    print("PHASE4_VALIDATION_LANE_SEQUENCING_CHECK=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
