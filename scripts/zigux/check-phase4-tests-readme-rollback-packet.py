#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

PASS_MARKER = "PHASE4_TESTS_README_ROLLBACK_PACKET_CHECK=pass"
SELF_TEST_PASS_MARKER = "PHASE4_TESTS_README_ROLLBACK_PACKET_SELF_TEST=pass"

README_PATH = Path("zigux/tests/README.md")
NOTE_PATH = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")

REQUIRED_README_MARKERS = [
    "current direct-readback Phase 4 rollback packet:",
    "direct readback now confirms the broader current Phase 4 validator, lab-matrix, and local-only perf companions on current `master`, including `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig`",
    "Phase 4 follow-through should treat the stale part of that handoff as historical blob-pin provenance in `Documentation/zigux/phase4-reversible-delivery-evidence.md`, not as path absence on current `master`",
    "the parked kprobe and `test_fsmount` survey companions stay adjacent but separate while those current validator, lab-matrix, and local-only perf companions remain directly readable on current `master`",
]

FORBIDDEN_README_MARKERS = [
    "return missing contents reads on current `master`",
    "require fresh reread or re-materialization before they are presented as shipped direct evidence again",
    "until a fresh reread confirms they are directly readable again on current `master`",
]

REQUIRED_NOTE_MARKERS = [
    "Current direct readback in this run confirmed this note, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
    "The tests-root guide should mirror this same current-head posture.",
    "stop describing those present Phase 4 validator, lab-matrix, and local-only perf companions as missing on current `master`",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 4 tests-root rollback packet matches the current direct-readback posture."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Repository root containing Documentation/zigux and zigux/tests.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run internal fixtures that prove the checker passes the corrected packet and fails the stale warning packet.",
    )
    return parser.parse_args()


def load_text(repo_root: Path, relative_path: Path) -> str:
    path = repo_root / relative_path
    return path.read_text(encoding="utf-8")


def run_check(repo_root: Path) -> list[str]:
    failures: list[str] = []
    readme_text = load_text(repo_root, README_PATH)
    note_text = load_text(repo_root, NOTE_PATH)

    for marker in REQUIRED_README_MARKERS:
        if marker not in readme_text:
            failures.append(f"missing_readme_marker:{marker}")

    for marker in FORBIDDEN_README_MARKERS:
        if marker in readme_text:
            failures.append(f"stale_readme_marker:{marker}")

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note_text:
            failures.append(f"missing_note_marker:{marker}")

    return failures


def write_packet(repo_root: Path, readme_text: str, note_text: str) -> None:
    (repo_root / README_PATH).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / NOTE_PATH).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / README_PATH).write_text(readme_text, encoding="utf-8")
    (repo_root / NOTE_PATH).write_text(note_text, encoding="utf-8")


def make_corrected_readme() -> str:
    return """# zigux/tests

Key entrypoints
  * current direct-readback Phase 4 rollback packet:
    `Documentation/zigux/phase4-reversible-delivery-evidence.md`
    `Documentation/zigux/review-checklist.md`
    `zigux/tests/README.md`
  * direct readback now confirms the broader current Phase 4 validator, lab-matrix, and local-only perf companions on current `master`, including `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig`
  * Phase 4 follow-through should treat the stale part of that handoff as historical blob-pin provenance in `Documentation/zigux/phase4-reversible-delivery-evidence.md`, not as path absence on current `master`
  * the parked kprobe and `test_fsmount` survey companions stay adjacent but separate while those current validator, lab-matrix, and local-only perf companions remain directly readable on current `master`
"""


def make_stale_readme() -> str:
    return """# zigux/tests

Key entrypoints
  * current direct-readback Phase 4 rollback packet:
    `Documentation/zigux/phase4-reversible-delivery-evidence.md`
    `Documentation/zigux/review-checklist.md`
    `zigux/tests/README.md`
  * repo-reality warning for the broader Phase 4 packet: the reversible-delivery handoff note currently records that several older Phase 4 validator, lab-matrix, and local-only perf files return missing contents reads on current `master`, including `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig`
  * Phase 4 follow-through should treat those paths as last-known packet members that require fresh reread or re-materialization before they are presented as shipped direct evidence again
  * historical Phase 4 route names such as the parked kprobe and `test_fsmount` survey companions, the validator-first routes, and the direct local-only perf routes stay owned by the reversible-delivery handoff note until a fresh reread confirms they are directly readable again on current `master`
"""


def make_note() -> str:
    return """# Phase 4 Reversible Delivery Evidence

Current direct readback in this run confirmed this note, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.

The tests-root guide should mirror this same current-head posture.

If `zigux/tests/README.md` is updated alongside the Phase 4 packet, keep it aligned with the directly readable rollback packet above and stop describing those present Phase 4 validator, lab-matrix, and local-only perf companions as missing on current `master`.
"""


def run_self_test() -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="phase4-tests-readme-"))
    try:
        note_text = make_note()

        corrected_root = temp_dir / "corrected"
        write_packet(corrected_root, make_corrected_readme(), note_text)
        corrected_failures = run_check(corrected_root)
        if corrected_failures:
            raise SystemExit(
                "corrected_fixture_failed:" + ",".join(corrected_failures)
            )

        stale_root = temp_dir / "stale"
        write_packet(stale_root, make_stale_readme(), note_text)
        stale_failures = run_check(stale_root)
        if not stale_failures:
            raise SystemExit("stale_fixture_unexpectedly_passed")
        if not any(item.startswith("stale_readme_marker:") for item in stale_failures):
            raise SystemExit(
                "stale_fixture_missing_stale_marker_failure:" + ",".join(stale_failures)
            )

        print(SELF_TEST_PASS_MARKER)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    failures = run_check(args.repo_root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
