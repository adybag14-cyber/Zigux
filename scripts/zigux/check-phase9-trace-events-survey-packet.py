#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()

SURVEY_NOTE_PATH = "Documentation/zigux/phase9-runtime-trace-events-survey.md"
MODULE_SLICE_PATH = "Documentation/zigux/phase9-runtime-trace-events-module-slice.md"
MANIFEST_PATH = "zigux/tests/runtime_trace_events_manifest.json"
SURVEY_GATE_PATH = "zigux/tests/runtime_trace_events_survey.zig"

SURVEYED_COMMIT_MARKER = "PHASE9_SURVEYED_COMMIT=70542337d15e9f26941f6a247da00077dddcebe8"
TRACE_EVENTS_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events.zig`"
UNREGISTERED_GATE_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events_unregistered_gate.zig`"
EXIT_ROLLBACK_GUARD_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`"
REENTRY_GATE_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`"
MANIFEST_REFERENCE_MARKER = "`zigux/tests/runtime_trace_events_manifest.json`"
SURVEY_GATE_REFERENCE_MARKER = "`zigux/tests/runtime_trace_events_survey.zig`"
MODULE_SLICE_REFERENCE_MARKER = "`Documentation/zigux/phase9-runtime-trace-events-module-slice.md`"
SELFTEST_HOOK_MARKER = "`.provides_selftest_hook = true`"
LIFECYCLE_MARKER = "initialized, selftest_complete, and exited lifecycle tracking"
FAMILY_LOCAL_WITNESS_MARKER = "direct family-local `zigux/tests/runtime_*` witness"
ABSENT_SHARED_LOADER_MARKER = "does not currently expose the broader shared runtime-loader packet"
ABSENT_PHASE9_BUILD_MARKER = "`zigux/tests/phase9_build.zig`"
ABSENT_RUNTIME_LOADER_MARKER = "`zigux/kernel/runtime_loader.zig`"
ABSENT_RUNTIME_LOADER_CONTRACT_MARKER = "`zigux/kernel/runtime_loader_contract.zig`"
NO_VALIDATE_PHASE9_MARKER = "Do not invent `validate-phase9.py`"

MANIFEST_LANE_KEY_MARKER = '"lane_key": "P9-L09"'
MANIFEST_PHASE_MARKER = '"phase": "Phase 9"'
MANIFEST_SURVEYED_COMMIT_MARKER = '"surveyed_commit": "70542337d15e9f26941f6a247da00077dddcebe8"'
MANIFEST_DIRECT_TEST_FILES_MARKER = '"direct_runtime_trace_events_test_files": 2'
MANIFEST_SAMPLE_FAMILY_COUNT_MARKER = '"surviving_sample_family_files": 4'
MANIFEST_SURVEY_NOTE_PRESENT_MARKER = '"survey_note_present": true'
MANIFEST_MODULE_SLICE_PRESENT_MARKER = '"module_slice_present": true'
MANIFEST_MODULE_SLICE_PATH_MARKER = '"module_slice_path": "Documentation/zigux/phase9-runtime-trace-events-module-slice.md"'
MANIFEST_SURVEY_NOTE_PATH_MARKER = '"survey_note_path": "Documentation/zigux/phase9-runtime-trace-events-survey.md"'
MANIFEST_PATH_MARKER = '"manifest_path": "zigux/tests/runtime_trace_events_manifest.json"'
MANIFEST_ALIGNMENT_FOCUS_MARKER = (
    '"alignment_focus": "sample-local pilot-module reviewability rather than returned shared runtime-loader parity"'
)
MANIFEST_LANDED_PILOT_STATE_MARKER = '"landed_pilot_state": "narrow trace-events sample packet plus family-local survey witness"'
MANIFEST_NEXT_GATE_MARKER = (
    '"next_gate": "keep the survey note, manifest, survey gate, and module-slice aligned with the surviving sample family while shared loader work stays parked"'
)
MANIFEST_SURVEY_GATE_OWNER_MARKER = '"surface": "zigux/tests/runtime_trace_events_survey.zig"'
MANIFEST_SURVEY_GATE_ROLE_MARKER = '"role": "survey_gate"'

MODULE_SLICE_SURVEY_NOTE_MARKER = "`Documentation/zigux/phase9-runtime-trace-events-survey.md`"
MODULE_SLICE_MANIFEST_MARKER = "`zigux/tests/runtime_trace_events_manifest.json`"
MODULE_SLICE_SURVEY_GATE_MARKER = "`zigux/tests/runtime_trace_events_survey.zig`"
MODULE_SLICE_ALIGNMENT_MARKER = "sample-local pilot-module reviewability"
MODULE_SLICE_ABSENT_SHARED_LOADER_MARKER = "broader shared runtime-loader packet"

SURVEY_GATE_TEST_NAME_MARKER = (
    'test "phase9 trace-events survey packet matches the narrow current-master pilot-module story" {'
)
SURVEY_GATE_SURVEYED_COMMIT_HELPER_MARKER = "fn expectSurveyedCommitMarker(note: []const u8, surveyed_commit: []const u8) !void {"
SURVEY_GATE_SURVEY_NOTE_PATH_MARKER = '"Documentation/zigux/phase9-runtime-trace-events-survey.md"'
SURVEY_GATE_MODULE_SLICE_PATH_MARKER = '"Documentation/zigux/phase9-runtime-trace-events-module-slice.md"'
SURVEY_GATE_MANIFEST_PATH_MARKER = '"zigux/tests/runtime_trace_events_manifest.json"'
SURVEY_GATE_SURVEY_GATE_PATH_MARKER = '"zigux/tests/runtime_trace_events_survey.zig"'
SURVEY_GATE_LANE_KEY_MARKER = 'try std.testing.expectEqualStrings("P9-L09", manifest.lane_key);'
SURVEY_GATE_LANDED_PILOT_STATE_MARKER = '"narrow trace-events sample packet plus family-local survey witness"'
SURVEY_GATE_ALIGNMENT_BOUNDARY_MARKER = (
    "Fail-closes on drift between the survey note, module-slice note, manifest, sequencing note, and surviving sample family."
)

FILE_MARKERS = {
    SURVEY_NOTE_PATH: [
        SURVEYED_COMMIT_MARKER,
        TRACE_EVENTS_SAMPLE_MARKER,
        UNREGISTERED_GATE_SAMPLE_MARKER,
        EXIT_ROLLBACK_GUARD_SAMPLE_MARKER,
        REENTRY_GATE_SAMPLE_MARKER,
        MANIFEST_REFERENCE_MARKER,
        SURVEY_GATE_REFERENCE_MARKER,
        MODULE_SLICE_REFERENCE_MARKER,
        SELFTEST_HOOK_MARKER,
        LIFECYCLE_MARKER,
        FAMILY_LOCAL_WITNESS_MARKER,
        ABSENT_SHARED_LOADER_MARKER,
        ABSENT_PHASE9_BUILD_MARKER,
        ABSENT_RUNTIME_LOADER_MARKER,
        ABSENT_RUNTIME_LOADER_CONTRACT_MARKER,
        NO_VALIDATE_PHASE9_MARKER,
    ],
    MODULE_SLICE_PATH: [
        SURVEYED_COMMIT_MARKER,
        MODULE_SLICE_SURVEY_NOTE_MARKER,
        MODULE_SLICE_MANIFEST_MARKER,
        MODULE_SLICE_SURVEY_GATE_MARKER,
        SELFTEST_HOOK_MARKER,
        LIFECYCLE_MARKER,
        MODULE_SLICE_ALIGNMENT_MARKER,
        MODULE_SLICE_ABSENT_SHARED_LOADER_MARKER,
        ABSENT_PHASE9_BUILD_MARKER,
        NO_VALIDATE_PHASE9_MARKER,
    ],
    MANIFEST_PATH: [
        MANIFEST_LANE_KEY_MARKER,
        MANIFEST_PHASE_MARKER,
        MANIFEST_SURVEYED_COMMIT_MARKER,
        MANIFEST_DIRECT_TEST_FILES_MARKER,
        MANIFEST_SAMPLE_FAMILY_COUNT_MARKER,
        MANIFEST_SURVEY_NOTE_PRESENT_MARKER,
        MANIFEST_MODULE_SLICE_PRESENT_MARKER,
        MANIFEST_MODULE_SLICE_PATH_MARKER,
        MANIFEST_SURVEY_NOTE_PATH_MARKER,
        MANIFEST_PATH_MARKER,
        MANIFEST_ALIGNMENT_FOCUS_MARKER,
        MANIFEST_LANDED_PILOT_STATE_MARKER,
        MANIFEST_NEXT_GATE_MARKER,
        MANIFEST_SURVEY_GATE_OWNER_MARKER,
        MANIFEST_SURVEY_GATE_ROLE_MARKER,
    ],
    SURVEY_GATE_PATH: [
        SURVEY_GATE_TEST_NAME_MARKER,
        SURVEY_GATE_SURVEYED_COMMIT_HELPER_MARKER,
        SURVEY_GATE_SURVEY_NOTE_PATH_MARKER,
        SURVEY_GATE_MODULE_SLICE_PATH_MARKER,
        SURVEY_GATE_MANIFEST_PATH_MARKER,
        SURVEY_GATE_SURVEY_GATE_PATH_MARKER,
        SURVEY_GATE_LANE_KEY_MARKER,
        SURVEY_GATE_LANDED_PILOT_STATE_MARKER,
        SURVEY_GATE_ALIGNMENT_BOUNDARY_MARKER,
        TRACE_EVENTS_SAMPLE_MARKER,
        UNREGISTERED_GATE_SAMPLE_MARKER,
        EXIT_ROLLBACK_GUARD_SAMPLE_MARKER,
        REENTRY_GATE_SAMPLE_MARKER,
        SELFTEST_HOOK_MARKER,
        LIFECYCLE_MARKER,
    ],
}


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / SURVEY_NOTE_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_fixture_text(rel_path: str, markers: list[str]) -> str:
    if rel_path.endswith(".md"):
        return "\n".join(["# fixture", "", *markers, ""])
    if rel_path.endswith(".json"):
        return "{\n" + ",\n".join(f'  "__fixture_{index}": "{marker}"' for index, marker in enumerate(markers)) + "\n}\n"
    return "\n".join(markers) + "\n"


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in FILE_MARKERS:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in FILE_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")
    return failures


def seed_fixture_tree(base: Path) -> None:
    for rel_path, markers in FILE_MARKERS.items():
        write_text(base / rel_path, build_fixture_text(rel_path, markers))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-trace-events-survey-packet-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, markers in FILE_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                write_text(base / rel_path, "missing target marker fixture\n")
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for rel_path in FILE_MARKERS:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        print("PHASE9_TRACE_EVENTS_SURVEY_PACKET_SELF_TEST=pass")
        print(f"PHASE9_TRACE_EVENTS_SURVEY_PACKET_SURVEY_NOTE_MARKER_COUNT={len(FILE_MARKERS[SURVEY_NOTE_PATH])}")
        print(f"PHASE9_TRACE_EVENTS_SURVEY_PACKET_MODULE_SLICE_MARKER_COUNT={len(FILE_MARKERS[MODULE_SLICE_PATH])}")
        print(f"PHASE9_TRACE_EVENTS_SURVEY_PACKET_MANIFEST_MARKER_COUNT={len(FILE_MARKERS[MANIFEST_PATH])}")
        print(f"PHASE9_TRACE_EVENTS_SURVEY_PACKET_SURVEY_GATE_MARKER_COUNT={len(FILE_MARKERS[SURVEY_GATE_PATH])}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE9_TRACE_EVENTS_SURVEY_PACKET=pass")
    print(f"PHASE9_TRACE_EVENTS_SURVEY_PACKET_SURVEY_NOTE_MARKER_COUNT={len(FILE_MARKERS[SURVEY_NOTE_PATH])}")
    print(f"PHASE9_TRACE_EVENTS_SURVEY_PACKET_MODULE_SLICE_MARKER_COUNT={len(FILE_MARKERS[MODULE_SLICE_PATH])}")
    print(f"PHASE9_TRACE_EVENTS_SURVEY_PACKET_MANIFEST_MARKER_COUNT={len(FILE_MARKERS[MANIFEST_PATH])}")
    print(f"PHASE9_TRACE_EVENTS_SURVEY_PACKET_SURVEY_GATE_MARKER_COUNT={len(FILE_MARKERS[SURVEY_GATE_PATH])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
