#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()

FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
LANE_NOTE_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
TRACE_SURVEY_NOTE_PATH = "Documentation/zigux/phase9-runtime-trace-events-survey.md"
TRACE_MANIFEST_PATH = "zigux/tests/runtime_trace_events_manifest.json"
TRACE_SURVEY_GATE_PATH = "zigux/tests/runtime_trace_events_survey.zig"

FREEZE_MAP_MARKER = (
    "the shared Phase 9 runtime-loader packet stays review-only beside `kernel/workqueue.c` and "
    "`kernel/trace/ring_buffer.c`"
)
REVIEW_CHECKLIST_MARKER = (
    "if the change touches a freeze-map anchor, is the parity scorecard evidence or blocker state explicit?"
)
LANE_RULE_MARKER = (
    "Do not describe the shared runtime-loader lane as loadable-runtime evidence; keep it explicit that the "
    "shared loader family is a review-only handoff packet until the runtime substrate exists."
)
LANE_TRACE_BOUNDARY_MARKER = (
    "If a shared reminder surface or a family-local note cites the `kernel/trace/ring_buffer.c` study-only "
    "boundary through the trace-events packet, keep the survey-gate proof manifest-backed and literal"
)
TRACE_SURVEY_BOUNDARY_MARKER = "The remaining blocker is the broader Phase 9 runtime substrate."
TRACE_SURVEY_STUDY_MARKER = (
    "runtime task ownership, polling and event-loop substrate, and polling-backed wake or dispatch behavior"
)
TRACE_SURVEY_NO_STATUS_CHANGE_MARKER = (
    "The trace-events sample, loader scaffold, direct module and diff tests, dedicated survey gate, "
    "manifest-backed ownership packet, and paired notes are all visible on current `master`"
)
TRACE_MANIFEST_LIVE_BLOCKER_MARKER = '"live_registration_parity": "blocked_on_runtime_substrate"'
TRACE_MANIFEST_OWNER_MAP_MARKER = '"path": "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"'
TRACE_SURVEY_GATE_BOUNDARY_MARKER = (
    "phase 9 runtime trace-events survey packet matches the current manifest and notes"
)
TRACE_SURVEY_GATE_MANIFEST_MARKER = "zigux/tests/runtime_trace_events_manifest.json"
TRACE_SURVEY_GATE_NOTE_MARKER = "Documentation/zigux/phase9-runtime-trace-events-survey.md"


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / FREEZE_MAP_PATH).exists() and (candidate / LANE_NOTE_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def ensure_contains(failures: list[str], label: str, text: str, marker: str) -> None:
    if marker not in text:
        failures.append(f"{label}:{marker}")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    required_paths = [
        FREEZE_MAP_PATH,
        REVIEW_CHECKLIST_PATH,
        LANE_NOTE_PATH,
        TRACE_SURVEY_NOTE_PATH,
        TRACE_MANIFEST_PATH,
        TRACE_SURVEY_GATE_PATH,
    ]
    for rel_path in required_paths:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    freeze_map = read_text(root, FREEZE_MAP_PATH)
    review_checklist = read_text(root, REVIEW_CHECKLIST_PATH)
    lane_note = read_text(root, LANE_NOTE_PATH)
    trace_survey = read_text(root, TRACE_SURVEY_NOTE_PATH)
    trace_manifest = read_text(root, TRACE_MANIFEST_PATH)
    trace_survey_gate = read_text(root, TRACE_SURVEY_GATE_PATH)

    ensure_contains(failures, "freeze_map", freeze_map, FREEZE_MAP_MARKER)
    ensure_contains(failures, "review_checklist", review_checklist, REVIEW_CHECKLIST_MARKER)
    ensure_contains(failures, "lane_note", lane_note, LANE_RULE_MARKER)
    ensure_contains(failures, "lane_note", lane_note, LANE_TRACE_BOUNDARY_MARKER)
    ensure_contains(failures, "trace_survey", trace_survey, TRACE_SURVEY_BOUNDARY_MARKER)
    ensure_contains(failures, "trace_survey", trace_survey, TRACE_SURVEY_STUDY_MARKER)
    ensure_contains(failures, "trace_survey", trace_survey, TRACE_SURVEY_NO_STATUS_CHANGE_MARKER)
    ensure_contains(failures, "trace_manifest", trace_manifest, TRACE_MANIFEST_LIVE_BLOCKER_MARKER)
    ensure_contains(failures, "trace_manifest", trace_manifest, TRACE_MANIFEST_OWNER_MAP_MARKER)
    ensure_contains(failures, "trace_survey_gate", trace_survey_gate, TRACE_SURVEY_GATE_BOUNDARY_MARKER)
    ensure_contains(failures, "trace_survey_gate", trace_survey_gate, TRACE_SURVEY_GATE_MANIFEST_MARKER)
    ensure_contains(failures, "trace_survey_gate", trace_survey_gate, TRACE_SURVEY_GATE_NOTE_MARKER)
    return failures


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)

    write_text(root / FREEZE_MAP_PATH, FREEZE_MAP_MARKER + "\n")
    write_text(root / REVIEW_CHECKLIST_PATH, REVIEW_CHECKLIST_MARKER + "\n")
    write_text(root / LANE_NOTE_PATH, LANE_RULE_MARKER + "\n" + LANE_TRACE_BOUNDARY_MARKER + "\n")
    write_text(
        root / TRACE_SURVEY_NOTE_PATH,
        "\n".join(
            [
                TRACE_SURVEY_BOUNDARY_MARKER,
                TRACE_SURVEY_STUDY_MARKER,
                TRACE_SURVEY_NO_STATUS_CHANGE_MARKER,
                "",
            ]
        ),
    )
    write_text(
        root / TRACE_MANIFEST_PATH,
        "\n".join([TRACE_MANIFEST_LIVE_BLOCKER_MARKER, TRACE_MANIFEST_OWNER_MAP_MARKER, ""]),
    )
    write_text(
        root / TRACE_SURVEY_GATE_PATH,
        "\n".join(
            [
                TRACE_SURVEY_GATE_BOUNDARY_MARKER,
                TRACE_SURVEY_GATE_MANIFEST_MARKER,
                TRACE_SURVEY_GATE_NOTE_MARKER,
                "",
            ]
        ),
    )


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-freeze-boundary-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        write_fixture_tree(base)
        freeze_map_path = base / FREEZE_MAP_PATH
        freeze_map_path.write_text("", encoding="utf-8")
        expect_failure(base, f"freeze_map:{FREEZE_MAP_MARKER}")

        write_fixture_tree(base)
        lane_note_path = base / LANE_NOTE_PATH
        lane_note_path.write_text(LANE_RULE_MARKER + "\n", encoding="utf-8")
        expect_failure(base, f"lane_note:{LANE_TRACE_BOUNDARY_MARKER}")

        write_fixture_tree(base)
        trace_manifest_path = base / TRACE_MANIFEST_PATH
        trace_manifest_path.write_text(TRACE_MANIFEST_OWNER_MAP_MARKER + "\n", encoding="utf-8")
        expect_failure(base, f"trace_manifest:{TRACE_MANIFEST_LIVE_BLOCKER_MARKER}")

        write_fixture_tree(base)
        trace_survey_gate_path = base / TRACE_SURVEY_GATE_PATH
        trace_survey_gate_path.write_text(
            TRACE_SURVEY_GATE_BOUNDARY_MARKER + "\n" + TRACE_SURVEY_GATE_MANIFEST_MARKER + "\n",
            encoding="utf-8",
        )
        expect_failure(base, f"trace_survey_gate:{TRACE_SURVEY_GATE_NOTE_MARKER}")
    finally:
        shutil.rmtree(base, ignore_errors=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when Phase 9 shared reminder surfaces drift away from freeze-map study boundaries."
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    failures = validate(args.repo_root.resolve())
    if failures:
        for failure in failures:
            print(f"phase9-freeze-boundary failure: {failure}", file=sys.stderr)
        return 1

    print("phase9-freeze-boundary: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
