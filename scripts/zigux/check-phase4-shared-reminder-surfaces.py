#!/usr/bin/env python3
"""Guard the shared Phase 4 reminder surfaces."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
DOCS_README = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")

EXPECTED_SELF_TEST_CASES = 12

NOTE_MARKERS = (
    "Current direct readback in this run confirmed this note, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
    "Current direct contents reads in this run also confirmed the roadmap-backed differential-gate pair `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` on current `master`.",
    "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`",
    "public raw fallback rereads now return those files on current `master`",
    "The remaining shared reminder follow-up from the older mixed-readback packet is now narrower: `zigux/tests/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `scripts/zigux/README.md` should align",
)

DOCS_README_MARKERS = (
    "Phase 4 notes - `Documentation/zigux/phase4-reversible-delivery-evidence.md`",
    "`scripts/zigux/check-phase4-workflow-route-counts.py`",
    "`scripts/zigux/check-phase4-perf-baseline-packet.py`",
    "`scripts/zigux/validate-phase4.py`",
    "`zigux/tests/phase4_build.zig`",
    "`zigux/tests/bitmap_diff.zig`",
    "`zigux/tests/phase4_bitmap_live_helper_replay.zig`",
    "keep the bounded Phase 4 docs-root packet explicit through the shared release-order, readiness, closure, coordination, fallback, and driver-local reminder notes plus the shipped validator-side support bundle",
)

CHECKLIST_MARKERS = (
    "`Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase4-repo-reality-warning.py` and `scripts/zigux/check-phase4-reversible-delivery-pins.py` still agree on the current direct-readback packet",
    "keep the directly readable local-only perf packet explicit",
    "keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, and `scripts/zigux/check-phase4-remaining-gap-matrix.py`",
    "keep the repo-reality warning explicit for the broader Phase 4 validator, build, and bitmap-diff companions still needing raw-fallback proof or fresh authenticated blob capture",
    "keep the roadmap-backed `atomic64_diff` pair explicit as direct current-head evidence",
    "keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion",
    "keep the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call",
    "keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval",
)

SCRIPTS_README_MARKERS = (
    "`scripts/zigux/check-phase4-artifact-diff-validator-replays.py`",
    "`scripts/zigux/check-phase4-perf-baseline-packet.py`",
    "`scripts/zigux/check-phase4-remaining-gap-matrix.py`",
    "`scripts/zigux/check-phase4-workflow-route-counts.py`",
    "`scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` still flap in authenticated contents reads in this runtime, but public raw fallback rereads return those files on current `master`",
    "keep them explicit as now-returned companions while exact authenticated blob-pin refresh remains pending",
    "keep Phase 4 follow-through narrowed to one reminder-surface, contract, checker, rollback-owner, or local-only perf-governance truthfulness repair at a time",
)

TESTS_README_MARKERS = (
    "Keep the current bounded Phase 4 reminder packet explicit through `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, and `zigux/tests/README.md`.",
    "Keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, and `scripts/zigux/check-phase4-remaining-gap-matrix.py`",
    "Current direct-readback dedicated local-only perf checker: `scripts/zigux/check-phase4-perf-baseline-packet.py`",
    "Current direct-readback dedicated local-only perf companion members: `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run built-in fixture checks")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_markers(text: str, markers: tuple[str, ...], label: str, missing: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def validate_root(root: Path) -> list[str]:
    missing: list[str] = []
    files = (
        NOTE,
        DOCS_README,
        REVIEW_CHECKLIST,
        SCRIPTS_README,
        TESTS_README,
    )
    for rel in files:
        if not (root / rel).is_file():
            missing.append(f"file:{rel.as_posix()}")
    if missing:
        return missing

    require_markers(read_text(root / NOTE), NOTE_MARKERS, "note", missing)
    require_markers(read_text(root / DOCS_README), DOCS_README_MARKERS, "docs_readme", missing)
    require_markers(read_text(root / REVIEW_CHECKLIST), CHECKLIST_MARKERS, "review_checklist", missing)
    require_markers(read_text(root / SCRIPTS_README), SCRIPTS_README_MARKERS, "scripts_readme", missing)
    require_markers(read_text(root / TESTS_README), TESTS_README_MARKERS, "tests_readme", missing)
    return missing


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing replacement target: {old!r}")
    return text.replace(old, new, 1)


def write_fixture_tree(root: Path) -> None:
    write_text(root / NOTE, "\n".join((
        "Current direct readback in this run confirmed this note, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
        "Current direct contents reads in this run also confirmed the roadmap-backed differential-gate pair `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` on current `master`.",
        "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`.",
        "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff. Authenticated contents reads in this runtime still flap on `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig`, but public raw fallback rereads now return those files on current `master`, matching the broader review packet's recovered note-and-checker companions.",
        "The remaining shared reminder follow-up from the older mixed-readback packet is now narrower: `zigux/tests/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `scripts/zigux/README.md` should align on the recovered note pair, the returned helper-contract and checker packet, the direct local-only perf packet, the roadmap-backed `atomic64_diff` pair, and the now-returned validator, build, and bitmap replay companions, while exact blob-pin refresh for those broader companions remains the remaining authenticated-readback gap in this handoff.",
    )) + "\n")
    write_text(root / DOCS_README, "\n".join((
        "Phase 4 notes - `Documentation/zigux/phase4-reversible-delivery-evidence.md` - `Documentation/zigux/review-checklist.md` - `scripts/zigux/check-phase4-workflow-route-counts.py` - `scripts/zigux/check-phase4-perf-baseline-packet.py` - `scripts/zigux/validate-phase4.py` - `zigux/tests/phase4_build.zig` - `zigux/tests/bitmap_diff.zig` - `zigux/tests/phase4_bitmap_live_helper_replay.zig`",
        "keep the bounded Phase 4 docs-root packet explicit through the shared release-order, readiness, closure, coordination, fallback, and driver-local reminder notes plus the shipped validator-side support bundle",
    )) + "\n")
    write_text(root / REVIEW_CHECKLIST, "\n".join((
        "`Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase4-repo-reality-warning.py` and `scripts/zigux/check-phase4-reversible-delivery-pins.py` still agree on the current direct-readback packet",
        "keep the directly readable local-only perf packet explicit",
        "keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, and `scripts/zigux/check-phase4-remaining-gap-matrix.py`",
        "keep the repo-reality warning explicit for the broader Phase 4 validator, build, and bitmap-diff companions still needing raw-fallback proof or fresh authenticated blob capture",
        "keep the roadmap-backed `atomic64_diff` pair explicit as direct current-head evidence",
        "keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion",
        "keep the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call",
        "keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval",
    )) + "\n")
    write_text(root / SCRIPTS_README, "\n".join((
        "`scripts/zigux/check-phase4-artifact-diff-validator-replays.py`",
        "`scripts/zigux/check-phase4-perf-baseline-packet.py`",
        "`scripts/zigux/check-phase4-remaining-gap-matrix.py`",
        "`scripts/zigux/check-phase4-workflow-route-counts.py`",
        "`scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` still flap in authenticated contents reads in this runtime, but public raw fallback rereads return those files on current `master`, so keep them explicit as now-returned companions while exact authenticated blob-pin refresh remains pending",
        "keep Phase 4 follow-through narrowed to one reminder-surface, contract, checker, rollback-owner, or local-only perf-governance truthfulness repair at a time",
    )) + "\n")
    write_text(root / TESTS_README, "\n".join((
        "Keep the current bounded Phase 4 reminder packet explicit through `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, and `zigux/tests/README.md`.",
        "Keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, and `scripts/zigux/check-phase4-remaining-gap-matrix.py`",
        "Current direct-readback dedicated local-only perf checker: `scripts/zigux/check-phase4-perf-baseline-packet.py`",
        "Current direct-readback dedicated local-only perf companion members: `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`",
    )) + "\n")


def expect_failure(root: Path, expected_prefix: str) -> bool:
    return any(item.startswith(expected_prefix) for item in validate_root(root))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase4-shared-reminder-surfaces-") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_tree(root)
        if validate_root(root):
            print("PHASE4_SHARED_REMINDER_SURFACES_SELF_TEST=fail")
            print("baseline fixture did not validate cleanly")
            return 1

        cases = 1
        variants = (
            (NOTE, "public raw fallback rereads now return those files on current `master`", "public raw fallback rereads sometimes return those files", "note:"),
            (NOTE, "`zigux/tests/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `scripts/zigux/README.md` should align", "`zigux/tests/README.md` should align", "note:"),
            (DOCS_README, "`scripts/zigux/check-phase4-perf-baseline-packet.py`", "`scripts/zigux/check-phase4-perf-baseline.py`", "docs_readme:"),
            (DOCS_README, "`zigux/tests/phase4_bitmap_live_helper_replay.zig`", "`zigux/tests/phase4_bitmap_replay.zig`", "docs_readme:"),
            (REVIEW_CHECKLIST, "keep the roadmap-backed `atomic64_diff` pair explicit as direct current-head evidence", "keep the roadmap-backed Phase 4 note explicit", "review_checklist:"),
            (REVIEW_CHECKLIST, "keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion", "keep the ABI and Runtime Team as the decision owner for any broader shared-CI perf promotion", "review_checklist:"),
            (SCRIPTS_README, "`scripts/zigux/check-phase4-workflow-route-counts.py`", "`scripts/zigux/check-phase4-route-counts.py`", "scripts_readme:"),
            (SCRIPTS_README, "keep them explicit as now-returned companions while exact authenticated blob-pin refresh remains pending", "keep them archived until later", "scripts_readme:"),
            (TESTS_README, "Current direct-readback dedicated local-only perf checker: `scripts/zigux/check-phase4-perf-baseline-packet.py`", "Current direct-readback dedicated local-only perf checker: `scripts/zigux/check-phase4-perf-baseline.py`", "tests_readme:"),
            (TESTS_README, "Keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, and `scripts/zigux/check-phase4-remaining-gap-matrix.py`", "Keep the broader packet explicit through docs only", "tests_readme:"),
        )
        for rel, old, new, expected_prefix in variants:
            write_fixture_tree(root)
            target = root / rel
            write_text(target, replace_once(read_text(target), old, new))
            if not expect_failure(root, expected_prefix):
                print("PHASE4_SHARED_REMINDER_SURFACES_SELF_TEST=fail")
                print(f"missing expected failure prefix: {expected_prefix}")
                return 1
            cases += 1

        write_fixture_tree(root)
        (root / SCRIPTS_README).unlink()
        if not expect_failure(root, f"file:{SCRIPTS_README.as_posix()}"):
            print("PHASE4_SHARED_REMINDER_SURFACES_SELF_TEST=fail")
            print("missing scripts README case did not fail closed")
            return 1
        cases += 1

        if cases != EXPECTED_SELF_TEST_CASES:
            print("PHASE4_SHARED_REMINDER_SURFACES_SELF_TEST=fail")
            print(f"expected {EXPECTED_SELF_TEST_CASES} self-test cases, saw {cases}")
            return 1

    print("PHASE4_SHARED_REMINDER_SURFACES_SELF_TEST=pass")
    print(f"PHASE4_SHARED_REMINDER_SURFACES_SELF_TEST_CASE_COUNT={EXPECTED_SELF_TEST_CASES}")
    return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    missing = validate_root(Path(args.root).resolve())
    if missing:
        print("PHASE4_SHARED_REMINDER_SURFACES_CHECK=fail")
        for item in missing:
            print(item)
        return 1

    print("PHASE4_SHARED_REMINDER_SURFACES_CHECK=pass")
    print("PHASE4_SHARED_REMINDER_SURFACES_FILE_COUNT=5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
