#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "Documentation/zigux/review-checklist.md").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
LANE_SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
LOADER_GAP_NOTE_PATH = "Documentation/zigux/phase9-runtime-loader-gap-survey.md"
LOADER_GAP_MANIFEST_PATH = "zigux/tests/runtime_loader_gap_manifest.json"
TRACE_EVENTS_MANIFEST_PATH = "zigux/tests/runtime_trace_events_manifest.json"

CHECKLIST_OWNER_MAP_MARKER = (
    "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` remain the owner of the exact shared-loader target list, convenience-target names, and repo-reality blocker posture"
)
CHECKLIST_TRACE_LOADER_MARKER = (
    "with `samples/zigux/runtime_trace_events_loader.zig` kept explicit as a shipped shared-loader scaffold while `samples/zigux/runtime_trace_events.zig` plus `zigux/tests/runtime_trace_events_manifest.json` remain the sample-only blocked pilot boundary"
)
CHECKLIST_PHASE8_BOUNDARY_MARKER = (
    "while the older Phase 8 command and environment control cues stay with `tools/lib/subcmd/exec-cmd.zig` and `tools/lib/subcmd/help.zig`"
)
CHECKLIST_PUBLICATION_BOUNDARY_MARKER = (
    "the shared module-metadata and depmod-publication boundary still blocked in the live loader packet so `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, module install-root, and `depmod` script or manifest state remain review-only boundary references rather than shipped publication surfaces"
)
CHECKLIST_SHARED_CHECKER_MARKER = "`scripts/zigux/check-phase9-build-only-surface.py`"

LANE_SEQUENCING_CHECKLIST_MARKER = (
    "direct readback now shows `Documentation/zigux/review-checklist.md` and `scripts/zigux/README.md` already defer the exact shared owner map back to this sequencing note"
)
LANE_SEQUENCING_REVIEWER_SPLIT_MARKER = (
    "`Documentation/zigux/review-checklist.md` now keeps the shared-loader split visible"
)

LOADER_GAP_STATUS_MARKER = "PHASE9_SLICE=runtime-loader-gap-survey"
LOADER_GAP_REVIEWER_REREAD_MARKER = (
    "then re-read `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and\n`zigux/tests/README.md` before reopening any broader shared reminder pass."
)
LOADER_GAP_TESTS_ROOT_STEP_MARKER = (
    "Start with `zigux/tests/README.md` so\nits shared Phase 9 packet listing names\n`Documentation/zigux/phase9-runtime-loader-gap-survey.md` and\n`zigux/tests/runtime_loader_gap_manifest.json` beside the shared loader-facing\nsurfaces"
)

LOADER_GAP_MANIFEST_GATE_MARKER = '"current_honest_gate": "make -C zigux phase9-runtime-loader-shared-tests"'
LOADER_GAP_MANIFEST_BOUNDARY_MARKER = '"id": "runtime-loader-publication-metadata"'

TRACE_EVENTS_MANIFEST_LOADER_MARKER = '"preexisting_runtime_trace_events_loader_present": true'
TRACE_EVENTS_MANIFEST_BLOCKER_MARKER = '"live_registration_parity": "blocked_on_runtime_substrate"'

REQUIRED_FILES = [
    REVIEW_CHECKLIST_PATH,
    LANE_SEQUENCING_PATH,
    LOADER_GAP_NOTE_PATH,
    LOADER_GAP_MANIFEST_PATH,
    TRACE_EVENTS_MANIFEST_PATH,
]

REQUIRED_MARKERS = {
    REVIEW_CHECKLIST_PATH: [
        CHECKLIST_OWNER_MAP_MARKER,
        CHECKLIST_TRACE_LOADER_MARKER,
        CHECKLIST_PHASE8_BOUNDARY_MARKER,
        CHECKLIST_PUBLICATION_BOUNDARY_MARKER,
        CHECKLIST_SHARED_CHECKER_MARKER,
    ],
    LANE_SEQUENCING_PATH: [
        LANE_SEQUENCING_CHECKLIST_MARKER,
        LANE_SEQUENCING_REVIEWER_SPLIT_MARKER,
        CHECKLIST_TRACE_LOADER_MARKER,
    ],
    LOADER_GAP_NOTE_PATH: [
        LOADER_GAP_STATUS_MARKER,
        LOADER_GAP_REVIEWER_REREAD_MARKER,
        LOADER_GAP_TESTS_ROOT_STEP_MARKER,
        CHECKLIST_TRACE_LOADER_MARKER,
    ],
    LOADER_GAP_MANIFEST_PATH: [
        LOADER_GAP_MANIFEST_GATE_MARKER,
        LOADER_GAP_MANIFEST_BOUNDARY_MARKER,
    ],
    TRACE_EVENTS_MANIFEST_PATH: [
        TRACE_EVENTS_MANIFEST_LOADER_MARKER,
        TRACE_EVENTS_MANIFEST_BLOCKER_MARKER,
    ],
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")

    if failures:
        return failures

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")

    return failures


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)

    for rel_path in REQUIRED_FILES:
        title = Path(rel_path).name
        prefix = f"# {title}" if rel_path.endswith((".md", ".json", ".py")) else f"// {title}"
        content = "\n".join([prefix, *REQUIRED_MARKERS[rel_path], ""])
        write_text(root / rel_path, content)


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-review-checklist-packet-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        checklist_path = base / REVIEW_CHECKLIST_PATH
        checklist = checklist_path.read_text(encoding="utf-8")
        checklist_path.write_text(checklist.replace(CHECKLIST_OWNER_MAP_MARKER, "", 1), encoding="utf-8")
        expect_failure(base, f"missing_marker:{REVIEW_CHECKLIST_PATH}:{CHECKLIST_OWNER_MAP_MARKER}")

        write_fixture_tree(base)
        checklist_path = base / REVIEW_CHECKLIST_PATH
        checklist = checklist_path.read_text(encoding="utf-8")
        checklist_path.write_text(checklist.replace(CHECKLIST_TRACE_LOADER_MARKER, "", 1), encoding="utf-8")
        expect_failure(base, f"missing_marker:{REVIEW_CHECKLIST_PATH}:{CHECKLIST_TRACE_LOADER_MARKER}")

        write_fixture_tree(base)
        lane_path = base / LANE_SEQUENCING_PATH
        lane = lane_path.read_text(encoding="utf-8")
        lane_path.write_text(lane.replace(LANE_SEQUENCING_CHECKLIST_MARKER, "", 1), encoding="utf-8")
        expect_failure(base, f"missing_marker:{LANE_SEQUENCING_PATH}:{LANE_SEQUENCING_CHECKLIST_MARKER}")

        write_fixture_tree(base)
        note_path = base / LOADER_GAP_NOTE_PATH
        note = note_path.read_text(encoding="utf-8")
        note_path.write_text(note.replace(LOADER_GAP_REVIEWER_REREAD_MARKER, "", 1), encoding="utf-8")
        expect_failure(base, f"missing_marker:{LOADER_GAP_NOTE_PATH}:{LOADER_GAP_REVIEWER_REREAD_MARKER}")

        write_fixture_tree(base)
        manifest_path = base / TRACE_EVENTS_MANIFEST_PATH
        manifest = manifest_path.read_text(encoding="utf-8")
        manifest_path.write_text(manifest.replace(TRACE_EVENTS_MANIFEST_LOADER_MARKER, "", 1), encoding="utf-8")
        expect_failure(base, f"missing_marker:{TRACE_EVENTS_MANIFEST_PATH}:{TRACE_EVENTS_MANIFEST_LOADER_MARKER}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_REVIEW_CHECKLIST_PACKET_SELF_TEST=pass")
    print("PHASE9_REVIEW_CHECKLIST_PACKET_SELF_TEST_CASE_COUNT=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the shared Phase 9 review-checklist release-discipline packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="repository root to inspect",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the built-in checker self-test and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE9_REVIEW_CHECKLIST_PACKET_ERROR={failure}")
        return 1

    print(f"PHASE9_REVIEW_CHECKLIST_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PACKET_REQUIRED_SURFACE_COUNT={len(REQUIRED_MARKERS)}")
    print("PHASE9_REVIEW_CHECKLIST_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
