#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile

SELF_PATH = Path(__file__).resolve()
SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
SURVEY_NOTE_PATH = "Documentation/zigux/phase9-runtime-trace-events-survey.md"
MODULE_SLICE_PATH = "Documentation/zigux/phase9-runtime-trace-events-module-slice.md"
SAMPLES_README_PATH = "samples/zigux/README.md"
MANIFEST_PATH = "zigux/tests/runtime_trace_events_manifest.json"
SURVEY_GATE_PATH = "zigux/tests/runtime_trace_events_survey.zig"
SAMPLE_PATH = "samples/zigux/runtime_trace_events.zig"
UNREGISTERED_GATE_SAMPLE_PATH = "samples/zigux/runtime_trace_events_unregistered_gate.zig"
REENTRY_GATE_SAMPLE_PATH = "samples/zigux/runtime_trace_events_registration_reentry_gate.zig"
EXIT_ROLLBACK_GUARD_SAMPLE_PATH = "samples/zigux/runtime_trace_events_exit_rollback_guard.zig"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / SEQUENCING_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

FILE_MARKERS: dict[str, list[str]] = {
    SEQUENCING_PATH: [
        "`samples/zigux/runtime_trace_events.zig`",
        "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
        "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
        "does not currently expose the broader shared runtime-loader packet",
        "`zigux/tests/phase9_build.zig`",
    ],
    SURVEY_NOTE_PATH: [
        "`samples/zigux/runtime_trace_events.zig`",
        "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
        "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
        "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
        "`zigux/tests/runtime_trace_events_manifest.json`",
        "`zigux/tests/runtime_trace_events_survey.zig`",
        "`Documentation/zigux/phase9-runtime-trace-events-module-slice.md`",
        ".provides_selftest_hook = true",
        "initialized, selftest_complete, and exited lifecycle tracking",
        "sample-local pilot-module reviewability",
        "`zigux/tests/phase9_build.zig`",
        "`zigux/kernel/runtime_loader.zig`",
        "Do not invent `validate-phase9.py`",
    ],
    MODULE_SLICE_PATH: [
        "`samples/zigux/runtime_trace_events.zig`",
        "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
        "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
        "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
        "`Documentation/zigux/phase9-runtime-trace-events-survey.md`",
        "`zigux/tests/runtime_trace_events_manifest.json`",
        "`zigux/tests/runtime_trace_events_survey.zig`",
        ".provides_selftest_hook = true",
        "initialized, selftest_complete, and exited lifecycle tracking",
        "broader shared runtime-loader packet",
        "`zigux/tests/phase9_build.zig`",
        "Do not invent `validate-phase9.py`",
    ],
    SAMPLES_README_PATH: [
        "`samples/zigux/runtime_trace_events.zig`",
        "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
        "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
        "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
        "`scripts/zigux/check-phase9-trace-events-runtime-packet.py`",
        ".provides_selftest_hook = true",
        "initialized, selftest_complete, and exited lifecycle tracking",
        "unregistered function-thread failures fail-closed",
        "balanced function-thread registration reusable before and after selftest",
        "failed-exit rollback explicit after reusable selftest replay",
        "does not currently expose the broader shared runtime-loader packet",
    ],
    MANIFEST_PATH: [
        '"lane_key": "P9-L12"',
        '"phase": "Phase 9"',
        '"direct_sample": "samples/zigux/runtime_trace_events.zig"',
        '"survey_note_path": "Documentation/zigux/phase9-runtime-trace-events-survey.md"',
        '"module_slice_path": "Documentation/zigux/phase9-runtime-trace-events-module-slice.md"',
        '"manifest_path": "zigux/tests/runtime_trace_events_manifest.json"',
        '"alignment_focus": "sample-local pilot-module reviewability rather than returned shared runtime-loader parity"',
        '"landed_pilot_state": "narrow trace-events sample packet plus family-local survey witness beside a returned bounded phase9_build bundle"',
        '"next_gate": "keep the survey note, manifest, survey gate, and module-slice aligned with the surviving sample family and the returned bounded phase9_build bundle while shared loader work stays parked"',
        '"owner": "P9-L12"',
        '"owner": "P9-L11"',
    ],
    SURVEY_GATE_PATH: [
        'test "phase9 trace-events survey packet matches the narrow current-master pilot-module story" {',
        'try std.testing.expectEqualStrings("P9-L12", manifest.lane_key);',
        'try std.testing.expectEqualStrings("P9-L12", manifest.ownership_map[0].owner);',
        'try std.testing.expectEqualStrings("P9-L12", manifest.ownership_map[1].owner);',
        'try std.testing.expectEqualStrings("P9-L12", manifest.ownership_map[2].owner);',
        'try std.testing.expectEqualStrings("P9-L12", manifest.ownership_map[3].owner);',
        'try expectContains(survey_note, "`zigux/tests/phase9_build.zig`");',
        'try expectContains(workflow_file, "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test");',
    ],
    SAMPLE_PATH: [
        '.name = "runtime_trace_events"',
        '.anchor = "samples/trace_events/trace-events-sample.c"',
        '.requires_runtime_substrate = true',
        '.provides_selftest_hook = true',
        'test "trace-events sample rejects duplicate function-thread registration" {',
        'test "trace-events sample keeps selftest replay-summary continuity explicit after direct pilot activity" {',
        'test "trace-events sample keeps failed-exit rollback explicit after selftest-ready replay" {',
        'test "trace-events sample keeps rejected re-selftest rollback explicit" {',
    ],
    UNREGISTERED_GATE_SAMPLE_PATH: [
        'test "phase9 trace-events sample keeps unregistered function-thread failures fail-closed" {',
        "error.FunctionThreadNotRegistered",
        "error.RegistrationUnderflow",
    ],
    REENTRY_GATE_SAMPLE_PATH: [
        'test "phase9 trace-events sample keeps registration reentry reusable across initialized and selftest_complete stages" {',
        "error.FunctionThreadAlreadyRegistered",
        'test "phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest" {',
    ],
    EXIT_ROLLBACK_GUARD_SAMPLE_PATH: [
        'test "phase9 trace-events sample keeps exit rollback explicit after reusable selftest replay" {',
        'test "phase9 trace-events sample keeps initialized failed-exit rollback explicit before selftest replay" {',
        'test "phase9 trace-events sample keeps initialized direct-activity exit rollback explicit before selftest replay" {',
        "error.OutstandingRegistration",
        "try expectSummaryStable(exited_before_rejected_ops, exited_after_rejected_ops);",
    ],
    WORKFLOW_PATH: [
        "python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test",
        "python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py",
        "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test",
        "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py",
        "zig test samples/zigux/runtime_trace_events.zig",
        "zig test samples/zigux/runtime_trace_events_unregistered_gate.zig",
        "zig test samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
        "zig test samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
        "zig test zigux/tests/runtime_trace_events_survey.zig",
    ],
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def break_marker(marker: str) -> str:
    if len(marker) == 1:
        return "_"
    replacement_tail = "_" if marker[-1] != "_" else "-"
    return marker[:-1] + replacement_tail


def tamper_marker_occurrences(content: str, marker: str) -> str:
    return content.replace(marker, break_marker(marker))


def build_fixture_text(rel_path: str, markers: list[str]) -> str:
    if rel_path.endswith(".md"):
        return "\n".join(["# fixture", "", *markers, ""])
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
    base = Path(tempfile.mkdtemp(prefix="phase9-trace-events-runtime-packet-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, markers in FILE_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = read_text(base, rel_path)
                write_text(base / rel_path, tamper_marker_occurrences(current, marker))
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for rel_path in FILE_MARKERS:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        print("PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SELF_TEST=pass")
        print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_FILE_COUNT={len(FILE_MARKERS)}")
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

    print("PHASE9_TRACE_EVENTS_RUNTIME_PACKET=pass")
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_FILE_COUNT={len(FILE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())