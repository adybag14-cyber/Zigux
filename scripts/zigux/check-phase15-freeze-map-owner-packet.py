#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_README_PATH = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")
STUDY_ONLY_NOTE_PATH = Path("Documentation/zigux/phase15-study-only-anchor-accounting.md")

DOCS_REQUIRED_MARKERS = (
    "Phase 9 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues, and any shared reminder surface that summarizes them must route back through those two owner notes.",
    "Phase 14 notes - `Documentation/zigux/phase14-end-to-end-smoke-survey.md`",
    "- `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
)

CHECKLIST_REQUIRED_MARKERS = (
    "if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence?",
)

FREEZE_MAP_REQUIRED_MARKERS = (
    "shared reminder surfaces that summarize freeze posture, especially `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md`, must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md` when they summarize that boundary set",
    "study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md` so the `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` inventory does not drift from this file",
)

STUDY_ONLY_REQUIRED_MARKERS = (
    "The roadmap keeps two deep-core areas in a narrower posture than the four freeze-in-C anchors: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only until years of narrower evidence justify anything stronger.",
    "- `kernel/workqueue.c`",
    "- `kernel/trace/ring_buffer.c`",
    "- this note is an inventory and handoff surface, not an approval record",
    "- no Architecture Council approval is currently recorded for a deep-core status change",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for rel in (
        DOCS_README_PATH,
        REVIEW_CHECKLIST_PATH,
        FREEZE_MAP_PATH,
        STUDY_ONLY_NOTE_PATH,
    ):
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    docs_readme = _read(root / DOCS_README_PATH)
    review_checklist = _read(root / REVIEW_CHECKLIST_PATH)
    freeze_map = _read(root / FREEZE_MAP_PATH)
    study_only_note = _read(root / STUDY_ONLY_NOTE_PATH)

    for marker in DOCS_REQUIRED_MARKERS:
        if marker not in docs_readme:
            failures.append(f"docs_readme:missing:{marker}")

    for marker in CHECKLIST_REQUIRED_MARKERS:
        if marker not in review_checklist:
            failures.append(f"review_checklist:missing:{marker}")

    for marker in FREEZE_MAP_REQUIRED_MARKERS:
        if marker not in freeze_map:
            failures.append(f"freeze_map:missing:{marker}")

    for marker in STUDY_ONLY_REQUIRED_MARKERS:
        if marker not in study_only_note:
            failures.append(f"study_only_note:missing:{marker}")

    return failures


def _sample_docs_readme() -> str:
    return "\n".join(
        (
            "# Zigux Documentation",
            "",
            "Phase 9 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
            "keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues, and any shared reminder surface that summarizes them must route back through those two owner notes.",
            "",
            "Phase 14 notes - `Documentation/zigux/phase14-end-to-end-smoke-survey.md`",
            "- `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
            "",
        )
    )


def _sample_review_checklist() -> str:
    return "\n".join(
        (
            "# Zigux Review Checklist",
            "",
            "- if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
            "- so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence?",
            "",
        )
    )


def _sample_freeze_map() -> str:
    return "\n".join(
        (
            "# Zigux Freeze Map",
            "",
            "- shared reminder surfaces that summarize freeze posture, especially `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md`, must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md` when they summarize that boundary set",
            "- study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md` so the `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` inventory does not drift from this file",
            "",
        )
    )


def _sample_study_only_note() -> str:
    return "\n".join(
        (
            "# Phase 15 Study-Only Anchor Accounting",
            "",
            "The roadmap keeps two deep-core areas in a narrower posture than the four freeze-in-C anchors: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only until years of narrower evidence justify anything stronger.",
            "",
            "- `kernel/workqueue.c`",
            "- `kernel/trace/ring_buffer.c`",
            "- this note is an inventory and handoff surface, not an approval record",
            "- no Architecture Council approval is currently recorded for a deep-core status change",
            "",
        )
    )


def _seed(root: Path) -> None:
    _write(root / DOCS_README_PATH, _sample_docs_readme())
    _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
    _write(root / FREEZE_MAP_PATH, _sample_freeze_map())
    _write(root / STUDY_ONLY_NOTE_PATH, _sample_study_only_note())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_freeze_map_owner_") as tmp_dir:
        root = Path(tmp_dir)
        _seed(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        missing_docs_marker_root = root / "missing_docs_marker"
        _seed(missing_docs_marker_root)
        _write(
            missing_docs_marker_root / DOCS_README_PATH,
            _sample_docs_readme().replace(DOCS_REQUIRED_MARKERS[1] + "\n", "", 1),
        )
        failures = collect_failures(missing_docs_marker_root)
        expected = [f"docs_readme:missing:{DOCS_REQUIRED_MARKERS[1]}"]
        if failures != expected:
            raise AssertionError(f"unexpected docs marker failure: {failures}")
        case_count += 1

        missing_checklist_marker_root = root / "missing_checklist_marker"
        _seed(missing_checklist_marker_root)
        _write(
            missing_checklist_marker_root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace(CHECKLIST_REQUIRED_MARKERS[0] + "\n", "", 1),
        )
        failures = collect_failures(missing_checklist_marker_root)
        expected = [f"review_checklist:missing:{CHECKLIST_REQUIRED_MARKERS[0]}"]
        if failures != expected:
            raise AssertionError(f"unexpected checklist failure: {failures}")
        case_count += 1

        missing_freeze_marker_root = root / "missing_freeze_marker"
        _seed(missing_freeze_marker_root)
        _write(
            missing_freeze_marker_root / FREEZE_MAP_PATH,
            _sample_freeze_map().replace(FREEZE_MAP_REQUIRED_MARKERS[1] + "\n", "", 1),
        )
        failures = collect_failures(missing_freeze_marker_root)
        expected = [f"freeze_map:missing:{FREEZE_MAP_REQUIRED_MARKERS[1]}"]
        if failures != expected:
            raise AssertionError(f"unexpected freeze-map failure: {failures}")
        case_count += 1

        missing_study_only_marker_root = root / "missing_study_only_marker"
        _seed(missing_study_only_marker_root)
        _write(
            missing_study_only_marker_root / STUDY_ONLY_NOTE_PATH,
            _sample_study_only_note().replace(STUDY_ONLY_REQUIRED_MARKERS[3] + "\n", "", 1),
        )
        failures = collect_failures(missing_study_only_marker_root)
        expected = [f"study_only_note:missing:{STUDY_ONLY_REQUIRED_MARKERS[3]}"]
        if failures != expected:
            raise AssertionError(f"unexpected study-only failure: {failures}")
        case_count += 1

    print("PHASE15_FREEZE_MAP_OWNER_PACKET_SELF_TEST=pass")
    print(f"PHASE15_FREEZE_MAP_OWNER_PACKET_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the shared Phase 15 freeze-map owner packet stays aligned across the docs root, review checklist, freeze map, and study-only accounting note."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 freeze-map owner packet check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
