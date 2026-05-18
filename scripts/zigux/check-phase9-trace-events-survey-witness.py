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
SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
SAMPLE_PATH = "samples/zigux/runtime_trace_events.zig"
UNREGISTERED_GATE_PATH = "samples/zigux/runtime_trace_events_unregistered_gate.zig"
EXIT_ROLLBACK_GUARD_PATH = "samples/zigux/runtime_trace_events_exit_rollback_guard.zig"
REENTRY_GATE_PATH = "samples/zigux/runtime_trace_events_registration_reentry_gate.zig"


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / SURVEY_NOTE_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

SURVEYED_COMMIT_MARKER = "PHASE9_SURVEYED_COMMIT=70542337d15e9f26941f6a247da00077dddcebe8"
TRACE_EVENTS_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events.zig`"
UNREGISTERED_GATE_MARKER = "`samples/zigux/runtime_trace_events_unregistered_gate.zig`"
EXIT_ROLLBACK_GUARD_MARKER = "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`"
REENTRY_GATE_MARKER = "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`"
MANIFEST_FILE_MARKER = "`zigux/tests/runtime_trace_events_manifest.json`"
SURVEY_GATE_MARKER = "`zigux/tests/runtime_trace_events_survey.zig`"
MODULE_SLICE_FILE_MARKER = "`Documentation/zigux/phase9-runtime-trace-events-module-slice.md`"
SEQUENCING_NOTE_MARKER = "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`"
WORKFLOW_FILE_MARKER = "`.github/workflows/zigux-bootstrap.yml`"
SELFTEST_HOOK_MARKER = "`.provides_selftest_hook = true`"
LIFECYCLE_MARKER = "initialized, selftest_complete, and exited lifecycle tracking"
WITNESS_MARKER = "direct family-local `zigux/tests/runtime_*` witness"
SAMPLE_LOCAL_ALIGNMENT_MARKER = "sample-local pilot-module reviewability rather than returned shared runtime-loader parity"
INITIALIZED_EXIT_MARKER = (
    'test "trace-events sample preserves initialized summary across direct exit without selftest"'
)
FAIL_CLOSED_MARKER = "unregistered function-thread failures fail-closed"
EXIT_ROLLBACK_MARKER = "failed-exit rollback explicit after reusable selftest replay"
REENTRY_MARKER = "balanced function-thread registration reusable before and after selftest"
ABSENT_SHARED_LOADER_MARKER = "does not currently expose the broader shared runtime-loader packet"
ABSENT_PHASE9_BUILD_MARKER = "`zigux/tests/phase9_build.zig`"
ABSENT_RUNTIME_LOADER_MARKER = "`zigux/kernel/runtime_loader.zig`"
ABSENT_RUNTIME_LOADER_CONTRACT_MARKER = "`zigux/kernel/runtime_loader_contract.zig`"
ABSENT_RUNTIME_LOADER_SCAFFOLD_MARKER = "`samples/zigux/runtime_*_loader.zig` scaffolds"
WORKFLOW_SELF_TEST_MARKER = "Self-test current Phase 9 trace-events runtime packet checker"
WORKFLOW_LIVE_MARKER = "Check current Phase 9 trace-events runtime packet"
WORKFLOW_SAMPLE_MARKER = "zig test samples/zigux/runtime_trace_events.zig"
WORKFLOW_UNREGISTERED_MARKER = "zig test samples/zigux/runtime_trace_events_unregistered_gate.zig"
WORKFLOW_EXIT_GUARD_MARKER = "zig test samples/zigux/runtime_trace_events_exit_rollback_guard.zig"
WORKFLOW_REENTRY_MARKER = "zig test samples/zigux/runtime_trace_events_registration_reentry_gate.zig"
WORKFLOW_SURVEY_GATE_MARKER = "zig test zigux/tests/runtime_trace_events_survey.zig"
MANIFEST_ALIGNMENT_MARKER = (
    '"alignment_focus": "sample-local pilot-module reviewability rather than returned shared runtime-loader parity"'
)
MANIFEST_NEXT_GATE_MARKER = (
    '"next_gate": "keep the survey note, manifest, survey gate, and module-slice aligned with the surviving sample family while shared loader work stays parked"'
)
SURVEY_GATE_ASSERTION_MARKER = 'try expectContains(survey_note, "direct family-local `zigux/tests/runtime_*` witness");'

SURVEY_NOTE_REQUIRED_MARKERS = [
    SURVEYED_COMMIT_MARKER,
    TRACE_EVENTS_SAMPLE_MARKER,
    UNREGISTERED_GATE_MARKER,
    EXIT_ROLLBACK_GUARD_MARKER,
    REENTRY_GATE_MARKER,
    MANIFEST_FILE_MARKER,
    SURVEY_GATE_MARKER,
    MODULE_SLICE_FILE_MARKER,
    SELFTEST_HOOK_MARKER,
    LIFECYCLE_MARKER,
    WITNESS_MARKER,
    INITIALIZED_EXIT_MARKER,
    FAIL_CLOSED_MARKER,
    EXIT_ROLLBACK_MARKER,
    REENTRY_MARKER,
    ABSENT_PHASE9_BUILD_MARKER,
    ABSENT_RUNTIME_LOADER_MARKER,
    ABSENT_RUNTIME_LOADER_CONTRACT_MARKER,
]

MODULE_SLICE_REQUIRED_MARKERS = [
    SURVEYED_COMMIT_MARKER,
    TRACE_EVENTS_SAMPLE_MARKER,
    UNREGISTERED_GATE_MARKER,
    EXIT_ROLLBACK_GUARD_MARKER,
    REENTRY_GATE_MARKER,
    MANIFEST_FILE_MARKER,
    SURVEY_GATE_MARKER,
    SELFTEST_HOOK_MARKER,
    LIFECYCLE_MARKER,
    SAMPLE_LOCAL_ALIGNMENT_MARKER,
    INITIALIZED_EXIT_MARKER,
    ABSENT_SHARED_LOADER_MARKER,
    ABSENT_PHASE9_BUILD_MARKER,
]

MANIFEST_REQUIRED_MARKERS = [
    MANIFEST_ALIGNMENT_MARKER,
    MANIFEST_NEXT_GATE_MARKER,
    '"surface": "Documentation/zigux/phase9-runtime-trace-events-survey.md"',
    '"surface": "zigux/tests/runtime_trace_events_manifest.json"',
    '"surface": "zigux/tests/runtime_trace_events_survey.zig"',
    '"surface": "Documentation/zigux/phase9-runtime-trace-events-module-slice.md"',
    '"surface": "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"',
    '"surface": ".github/workflows/zigux-bootstrap.yml"',
]

SURVEY_GATE_REQUIRED_MARKERS = [
    SURVEY_GATE_ASSERTION_MARKER,
    'try expectContains(survey_note, "test \\\"trace-events sample preserves initialized summary across direct exit without selftest\\\"");',
    'try expectContains(module_slice_note, "sample-local pilot-module reviewability");',
    'try expectContains(sequencing_note, "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`");',
    'try expectContains(workflow_file, "zig test zigux/tests/runtime_trace_events_survey.zig");',
]

SEQUENCING_REQUIRED_MARKERS = [
    TRACE_EVENTS_SAMPLE_MARKER,
    UNREGISTERED_GATE_MARKER,
    EXIT_ROLLBACK_GUARD_MARKER,
    REENTRY_GATE_MARKER,
    MANIFEST_FILE_MARKER,
    SURVEY_GATE_MARKER,
    SELFTEST_HOOK_MARKER,
    LIFECYCLE_MARKER,
    ABSENT_SHARED_LOADER_MARKER,
    WORKFLOW_FILE_MARKER,
]

WORKFLOW_REQUIRED_MARKERS = [
    WORKFLOW_SELF_TEST_MARKER,
    WORKFLOW_LIVE_MARKER,
    WORKFLOW_SAMPLE_MARKER,
    WORKFLOW_UNREGISTERED_MARKER,
    WORKFLOW_EXIT_GUARD_MARKER,
    WORKFLOW_REENTRY_MARKER,
    WORKFLOW_SURVEY_GATE_MARKER,
]

SAMPLE_REQUIRED_MARKERS = [
    SELFTEST_HOOK_MARKER,
    INITIALIZED_EXIT_MARKER,
]

UNREGISTERED_REQUIRED_MARKERS = [
    'phase9 trace-events sample keeps unregistered function-thread failures fail-closed',
]

EXIT_GUARD_REQUIRED_MARKERS = [
    'phase9 trace-events sample keeps exit rollback explicit after reusable selftest replay',
]

REENTRY_REQUIRED_MARKERS = [
    'phase9 trace-events sample keeps registration reentry reusable across initialized and selftest_complete stages',
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    required_paths = [
        SURVEY_NOTE_PATH,
        MODULE_SLICE_PATH,
        MANIFEST_PATH,
        SURVEY_GATE_PATH,
        SEQUENCING_PATH,
        WORKFLOW_PATH,
        SAMPLE_PATH,
        UNREGISTERED_GATE_PATH,
        EXIT_ROLLBACK_GUARD_PATH,
        REENTRY_GATE_PATH,
    ]
    for rel_path in required_paths:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    checks = {
        SURVEY_NOTE_PATH: SURVEY_NOTE_REQUIRED_MARKERS,
        MODULE_SLICE_PATH: MODULE_SLICE_REQUIRED_MARKERS,
        MANIFEST_PATH: MANIFEST_REQUIRED_MARKERS,
        SURVEY_GATE_PATH: SURVEY_GATE_REQUIRED_MARKERS,
        SEQUENCING_PATH: SEQUENCING_REQUIRED_MARKERS,
        WORKFLOW_PATH: WORKFLOW_REQUIRED_MARKERS,
        SAMPLE_PATH: SAMPLE_REQUIRED_MARKERS,
        UNREGISTERED_GATE_PATH: UNREGISTERED_REQUIRED_MARKERS,
        EXIT_ROLLBACK_GUARD_PATH: EXIT_GUARD_REQUIRED_MARKERS,
        REENTRY_GATE_PATH: REENTRY_REQUIRED_MARKERS,
    }
    for rel_path, markers in checks.items():
        body = read_text(root, rel_path)
        for marker in markers:
            if marker not in body:
                failures.append(f"missing_marker:{rel_path}:{marker}")
    return failures


def build_survey_note_fixture() -> str:
    return f"""# Phase 9 Runtime Trace-Events Survey

{SURVEYED_COMMIT_MARKER}

- {TRACE_EVENTS_SAMPLE_MARKER}
- {UNREGISTERED_GATE_MARKER}
- {EXIT_ROLLBACK_GUARD_MARKER}
- {REENTRY_GATE_MARKER}
- {MANIFEST_FILE_MARKER}
- {SURVEY_GATE_MARKER}
- {MODULE_SLICE_FILE_MARKER}

The direct sample still exposes {SELFTEST_HOOK_MARKER} together with {LIFECYCLE_MARKER}.
Current `master` also now keeps one {WITNESS_MARKER} for that same packet.
The direct sample also now keeps initialized-stage clean exit explicit: {INITIALIZED_EXIT_MARKER} proves zero selftest runs stay explicit.
The fail-closed companion still keeps {FAIL_CLOSED_MARKER}.
The exit-rollback companion still keeps {EXIT_ROLLBACK_MARKER}.
The registration-reentry companion still keeps {REENTRY_MARKER}.

Current `master` still does not expose:
- {ABSENT_PHASE9_BUILD_MARKER}
- {ABSENT_RUNTIME_LOADER_MARKER}
- {ABSENT_RUNTIME_LOADER_CONTRACT_MARKER}
"""


def build_module_slice_fixture() -> str:
    return f"""# Phase 9 Runtime Trace-Events Module Slice

{SURVEYED_COMMIT_MARKER}

- {TRACE_EVENTS_SAMPLE_MARKER}
- {UNREGISTERED_GATE_MARKER}
- {EXIT_ROLLBACK_GUARD_MARKER}
- {REENTRY_GATE_MARKER}
- {MANIFEST_FILE_MARKER}
- {SURVEY_GATE_MARKER}

The direct sample still exposes {SELFTEST_HOOK_MARKER} together with {LIFECYCLE_MARKER}.
This packet stays {SAMPLE_LOCAL_ALIGNMENT_MARKER}.
The direct sample also now keeps initialized-stage clean exit explicit: {INITIALIZED_EXIT_MARKER} proves zero selftest runs stay explicit.
Current `master` {ABSENT_SHARED_LOADER_MARKER}.
- {ABSENT_PHASE9_BUILD_MARKER}
"""


def build_manifest_fixture() -> str:
    return """{
  "module_slice_alignment": {
    "alignment_focus": "sample-local pilot-module reviewability rather than returned shared runtime-loader parity"
  },
  "roadmap_gap_summary": {
    "next_gate": "keep the survey note, manifest, survey gate, and module-slice aligned with the surviving sample family while shared loader work stays parked"
  },
  "ownership_map": [
    { "surface": "Documentation/zigux/phase9-runtime-trace-events-survey.md" },
    { "surface": "zigux/tests/runtime_trace_events_manifest.json" },
    { "surface": "zigux/tests/runtime_trace_events_survey.zig" },
    { "surface": "Documentation/zigux/phase9-runtime-trace-events-module-slice.md" },
    { "surface": "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md" },
    { "surface": ".github/workflows/zigux-bootstrap.yml" }
  ]
}
"""


def build_survey_gate_fixture() -> str:
    return """const std = @import(\"std\");

test \"phase9 trace-events survey packet matches the narrow current-master pilot-module story\" {
    try expectContains(survey_note, \"direct family-local `zigux/tests/runtime_*` witness\");
    try expectContains(survey_note, \"test \\\"trace-events sample preserves initialized summary across direct exit without selftest\\\"\");
    try expectContains(module_slice_note, \"sample-local pilot-module reviewability\");
    try expectContains(sequencing_note, \"`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`\");
    try expectContains(workflow_file, \"zig test zigux/tests/runtime_trace_events_survey.zig\");
}
"""


def build_sequencing_fixture() -> str:
    return f"""# Phase 9 Runtime Pilot Lane Sequencing

- {TRACE_EVENTS_SAMPLE_MARKER}
- {UNREGISTERED_GATE_MARKER}
- {EXIT_ROLLBACK_GUARD_MARKER}
- {REENTRY_GATE_MARKER}
- {MANIFEST_FILE_MARKER}
- {SURVEY_GATE_MARKER}
- {WORKFLOW_FILE_MARKER}

The direct sample still exposes {SELFTEST_HOOK_MARKER} together with {LIFECYCLE_MARKER}.
Current `master` {ABSENT_SHARED_LOADER_MARKER}.
"""


def build_workflow_fixture() -> str:
    return f"""name: zigux-bootstrap

- {WORKFLOW_SELF_TEST_MARKER}
- {WORKFLOW_LIVE_MARKER}
- {WORKFLOW_SAMPLE_MARKER}
- {WORKFLOW_UNREGISTERED_MARKER}
- {WORKFLOW_EXIT_GUARD_MARKER}
- {WORKFLOW_REENTRY_MARKER}
- {WORKFLOW_SURVEY_GATE_MARKER}
"""


def build_sample_fixture() -> str:
    return f"""const std = @import(\"std\");

pub const ModuleDescriptor = struct {{
    provides_selftest_hook: bool,
}};

test \"trace-events sample preserves initialized summary across direct exit without selftest\" {{
    _ = \"{SELFTEST_HOOK_MARKER}\";
}}
"""


def build_unregistered_fixture() -> str:
    return f'test "phase9 trace-events sample keeps unregistered function-thread failures fail-closed" {{ _ = "{FAIL_CLOSED_MARKER}"; }}\n'


def build_exit_guard_fixture() -> str:
    return f'test "phase9 trace-events sample keeps exit rollback explicit after reusable selftest replay" {{ _ = "{EXIT_ROLLBACK_MARKER}"; }}\n'


def build_reentry_fixture() -> str:
    return f'test "phase9 trace-events sample keeps registration reentry reusable across initialized and selftest_complete stages" {{ _ = "{REENTRY_MARKER}"; }}\n'


def seed_fixture_tree(base: Path) -> None:
    write_text(base / SURVEY_NOTE_PATH, build_survey_note_fixture())
    write_text(base / MODULE_SLICE_PATH, build_module_slice_fixture())
    write_text(base / MANIFEST_PATH, build_manifest_fixture())
    write_text(base / SURVEY_GATE_PATH, build_survey_gate_fixture())
    write_text(base / SEQUENCING_PATH, build_sequencing_fixture())
    write_text(base / WORKFLOW_PATH, build_workflow_fixture())
    write_text(base / SAMPLE_PATH, build_sample_fixture())
    write_text(base / UNREGISTERED_GATE_PATH, build_unregistered_fixture())
    write_text(base / EXIT_ROLLBACK_GUARD_PATH, build_exit_guard_fixture())
    write_text(base / REENTRY_GATE_PATH, build_reentry_fixture())


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-trace-events-survey-witness-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, markers in {
            SURVEY_NOTE_PATH: SURVEY_NOTE_REQUIRED_MARKERS,
            MODULE_SLICE_PATH: MODULE_SLICE_REQUIRED_MARKERS,
            MANIFEST_PATH: MANIFEST_REQUIRED_MARKERS,
            SURVEY_GATE_PATH: SURVEY_GATE_REQUIRED_MARKERS,
            SEQUENCING_PATH: SEQUENCING_REQUIRED_MARKERS,
            WORKFLOW_PATH: WORKFLOW_REQUIRED_MARKERS,
            SAMPLE_PATH: SAMPLE_REQUIRED_MARKERS,
            UNREGISTERED_GATE_PATH: UNREGISTERED_REQUIRED_MARKERS,
            EXIT_ROLLBACK_GUARD_PATH: EXIT_GUARD_REQUIRED_MARKERS,
            REENTRY_GATE_PATH: REENTRY_REQUIRED_MARKERS,
        }.items():
            for marker in markers:
                seed_fixture_tree(base)
                body = read_text(base, rel_path).replace(marker, "", 1)
                write_text(base / rel_path, body)
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for rel_path in [
            SURVEY_NOTE_PATH,
            MODULE_SLICE_PATH,
            MANIFEST_PATH,
            SURVEY_GATE_PATH,
            SEQUENCING_PATH,
            WORKFLOW_PATH,
            SAMPLE_PATH,
            UNREGISTERED_GATE_PATH,
            EXIT_ROLLBACK_GUARD_PATH,
            REENTRY_GATE_PATH,
        ]:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_TRACE_EVENTS_SURVEY_WITNESS_SELF_TEST=pass")
    print(f"PHASE9_TRACE_EVENTS_SURVEY_WITNESS_SURVEY_NOTE_MARKER_COUNT={len(SURVEY_NOTE_REQUIRED_MARKERS)}")
    print(f"PHASE9_TRACE_EVENTS_SURVEY_WITNESS_MODULE_SLICE_MARKER_COUNT={len(MODULE_SLICE_REQUIRED_MARKERS)}")
    print(f"PHASE9_TRACE_EVENTS_SURVEY_WITNESS_MANIFEST_MARKER_COUNT={len(MANIFEST_REQUIRED_MARKERS)}")
    print(f"PHASE9_TRACE_EVENTS_SURVEY_WITNESS_SURVEY_GATE_MARKER_COUNT={len(SURVEY_GATE_REQUIRED_MARKERS)}")
    print(f"PHASE9_TRACE_EVENTS_SURVEY_WITNESS_SEQUENCING_MARKER_COUNT={len(SEQUENCING_REQUIRED_MARKERS)}")
    print(f"PHASE9_TRACE_EVENTS_SURVEY_WITNESS_WORKFLOW_MARKER_COUNT={len(WORKFLOW_REQUIRED_MARKERS)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the returned Phase 9 trace-events survey witness, its paired module-slice note, the adjacent sequencing note and workflow rerun guard, and the surviving sample family stay aligned on the narrow current-master packet."
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE9_TRACE_EVENTS_SURVEY_WITNESS_ERROR={failure}")
        return 1

    print(f"PHASE9_TRACE_EVENTS_SURVEY_WITNESS_SURVEY_NOTE_MARKER_COUNT={len(SURVEY_NOTE_REQUIRED_MARKERS)}")
    print(f"PHASE9_TRACE_EVENTS_SURVEY_WITNESS_MODULE_SLICE_MARKER_COUNT={len(MODULE_SLICE_REQUIRED_MARKERS)}")
    print(f"PHASE9_TRACE_EVENTS_SURVEY_WITNESS_MANIFEST_MARKER_COUNT={len(MANIFEST_REQUIRED_MARKERS)}")
    print(f"PHASE9_TRACE_EVENTS_SURVEY_WITNESS_SURVEY_GATE_MARKER_COUNT={len(SURVEY_GATE_REQUIRED_MARKERS)}")
    print(f"PHASE9_TRACE_EVENTS_SURVEY_WITNESS_SEQUENCING_MARKER_COUNT={len(SEQUENCING_REQUIRED_MARKERS)}")
    print(f"PHASE9_TRACE_EVENTS_SURVEY_WITNESS_WORKFLOW_MARKER_COUNT={len(WORKFLOW_REQUIRED_MARKERS)}")
    print("PHASE9_TRACE_EVENTS_SURVEY_WITNESS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
