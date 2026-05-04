#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "scripts/zigux/check-phase5-review-checklist.py",
    "Documentation/zigux/review-checklist.md",
]

REQUIRED_MARKERS = [
    "if the change updates the landed Phase 5 `kobject` sample packet, does the manifest-backed survey still pin the exact inspected `master` head",
    "with `ownershipSummary()` and the `cold`/`initialized`/`registered`/`exited` lifecycle snapshot still explicit for reviewers?",
    "if the change updates the landed Phase 5 `kretprobe` or `trace-events` sample packet, does the manifest-backed survey still pin an exact surveyed commit for the inspected `master` head while keeping that Phase 5 sample visibly separate from the later Phase 9 runtime starter or pilot?",
    "if the change updates the landed Phase 5 `kretprobe` sample packet, do the note, shared checklist text, and paired focused replays keep pre-init retargeting, the fixed `maxactiveBudget()` cue, timestamp-order rejection and recovery, and post-exit handler rejection explicit instead of leaving those probe-lifecycle boundaries implied?",
    "if the change updates the landed Phase 5 `trace-events` sample packet, do the note, shared checklist text, and paired focused replays keep `lifecycleSummary()`, the exact `checked_focus` order, single-live callback registration, `unregisterFunctionCallback()` underflow plus `OutstandingRegistration` rejection, and post-exit replay rejection explicit instead of leaving those callback-boundary cues implicit?",
    "if the change updates a landed Phase 5 sample that keeps a Linux concurrency or private-data cue only for reviewability, does the note or checklist still say clearly what remains in-memory-only and what runtime parity is still out of scope?",
]


def read_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            missing_files.append(rel)

    if missing_files:
        return missing_files, []

    checklist = read_text(root, "Documentation/zigux/review-checklist.md")
    missing_markers = [marker for marker in REQUIRED_MARKERS if marker not in checklist]
    return missing_files, missing_markers


def report(root: Path) -> int:
    missing_files, missing_markers = validate(root)
    if missing_files:
        print("PHASE5_REVIEW_CHECKLIST=fail")
        print("MISSING_PHASE5_REVIEW_CHECKLIST_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE5_REVIEW_CHECKLIST_FILES_END")
        return 1
    if missing_markers:
        print("PHASE5_REVIEW_CHECKLIST=fail")
        print("MISSING_PHASE5_REVIEW_CHECKLIST_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE5_REVIEW_CHECKLIST_MARKERS_END")
        return 1
    print("PHASE5_REVIEW_CHECKLIST=pass")
    print(f"PHASE5_REVIEW_CHECKLIST_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE5_REVIEW_CHECKLIST_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


def copy_fixture_tree(dst_root: Path) -> None:
    for rel in REQUIRED_FILES:
        dst = dst_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(read_text(ROOT, rel), encoding="utf-8")


def mutate_once(root: Path, old: str, new: str) -> None:
    checklist_path = root / "Documentation/zigux/review-checklist.md"
    text = checklist_path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"missing live marker for self-test: {old}")
    checklist_path.write_text(text.replace(old, new, 1), encoding="utf-8")


def run_self_test() -> int:
    if report(ROOT) != 0:
        print("PHASE5_REVIEW_CHECKLIST_SELF_TEST=fail")
        print("PHASE5_REVIEW_CHECKLIST_SELF_TEST_REASON=live-tree-validation-failed")
        return 1

    cases = [
        (
            "with `ownershipSummary()` and the `cold`/`initialized`/`registered`/`exited` lifecycle snapshot still explicit for reviewers?",
            "with the lifecycle summary still explicit for reviewers?",
            "kobject-lifecycle-marker-gap",
        ),
        (
            "if the change updates the landed Phase 5 `kretprobe` or `trace-events` sample packet, does the manifest-backed survey still pin an exact surveyed commit for the inspected `master` head while keeping that Phase 5 sample visibly separate from the later Phase 9 runtime starter or pilot?",
            "if the change updates the landed Phase 5 `kretprobe` or `trace-events` sample packet, do the survey note and checklist keep the runtime follow-on boundary explicit?",
            "surveyed-commit-boundary-gap",
        ),
        (
            "if the change updates the landed Phase 5 `kretprobe` sample packet, do the note, shared checklist text, and paired focused replays keep pre-init retargeting, the fixed `maxactiveBudget()` cue, timestamp-order rejection and recovery, and post-exit handler rejection explicit instead of leaving those probe-lifecycle boundaries implied?",
            "if the change updates the landed Phase 5 `kretprobe` sample packet, do the note and checklist keep the probe-lifecycle cues explicit?",
            "kretprobe-reviewability-gap",
        ),
        (
            "if the change updates the landed Phase 5 `trace-events` sample packet, do the note, shared checklist text, and paired focused replays keep `lifecycleSummary()`, the exact `checked_focus` order, single-live callback registration, `unregisterFunctionCallback()` underflow plus `OutstandingRegistration` rejection, and post-exit replay rejection explicit instead of leaving those callback-boundary cues implicit?",
            "if the change updates the landed Phase 5 `trace-events` sample packet, do the note and checklist keep the callback boundary cues explicit?",
            "trace-events-reviewability-gap",
        ),
        (
            "if the change updates a landed Phase 5 sample that keeps a Linux concurrency or private-data cue only for reviewability, does the note or checklist still say clearly what remains in-memory-only and what runtime parity is still out of scope?",
            "if the change updates a landed Phase 5 sample, does it still describe what remains out of scope?",
            "runtime-boundary-gap",
        ),
    ]

    for old, new, reason in cases:
        with tempfile.TemporaryDirectory(prefix="phase5_review_checklist_") as tmp:
            tmp_root = Path(tmp)
            copy_fixture_tree(tmp_root)
            mutate_once(tmp_root, old, new)
            missing_files, missing_markers = validate(tmp_root)
            if missing_files or not missing_markers:
                print("PHASE5_REVIEW_CHECKLIST_SELF_TEST=fail")
                print(f"PHASE5_REVIEW_CHECKLIST_SELF_TEST_REASON={reason}")
                return 1

    print("PHASE5_REVIEW_CHECKLIST_SELF_TEST=pass")
    print(f"PHASE5_REVIEW_CHECKLIST_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed if the Phase 5 review checklist loses the shipped sample-specific contributor prompts."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in drift checks against a temporary checklist fixture.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    return report(ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
