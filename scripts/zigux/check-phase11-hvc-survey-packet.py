#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

SURVEY_NOTE_PATH = "Documentation/zigux/phase11-hvc-console-survey.md"
SLICE_NOTE_PATH = "Documentation/zigux/phase11-hvc-console-slice.md"
TEARDOWN_NOTE_PATH = "Documentation/zigux/phase11-hvc-console-teardown-note.md"
VALIDATION_MATRIX_PATH = "Documentation/zigux/phase11-hvc-console-validation-matrix.md"
SHARED_REPLAY_CONTRACT_PATH = "Documentation/zigux/phase11-shared-replay-contract.md"
VERIFY_REPLAY_PATH = "drivers/tty/hvc/hvc_console_verify.zig"
CLEANUP_REPLAY_PATH = "zigux/tests/phase11_hvc_cleanup.zig"
MANIFEST_PATH = "zigux/tests/phase11_hvc_console_manifest.json"
BUILD_PATH = "zigux/tests/phase11_build.zig"
MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
SCRIPT_PATH = "scripts/zigux/check-phase11-hvc-survey-packet.py"

REQUIRED_SURVEY_NOTE_MARKERS = [
    "lane `P11-L16`",
    "`zigux/tests/phase11_hvc_console_survey.zig`",
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
    "`zigux/Makefile`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`drivers/tty/hvc/hvc_console.zig`",
    "direct-port driver starter",
    "hardware validation matrix",
    "teardown and failure-mode parity",
    "repo reality now carries one bounded starter for each Phase 11 simple-production-driver roadmap anchor",
    "khvcd polling-contract follow-through",
    "`hvc_hangup()` disconnect boundary",
    "stale hangup short-circuit",
]

REQUIRED_SLICE_NOTE_MARKERS = [
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
    "tiny cleanup handoff summary",
    "tiny remove-path handoff summary",
    "tiny khvcd polling-contract summary",
    "tiny `hvc_hangup()` disconnect summary",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
    "shared-versus-dedicated HVC review packet",
]

REQUIRED_TEARDOWN_NOTE_MARKERS = [
    "summarizeCloseBoundary()",
    "summarizeCleanupHandoff()",
    "summarizeRemoveHandoff()",
    "tty_port_put()",
    "tty_vhangup()",
    "tty_kref_put()",
    "do not treat this note as evidence of live notifier callbacks",
]

REQUIRED_VALIDATION_MATRIX_MARKERS = [
    "lane: `P11-L16`",
    "`zigux/tests/phase11_hvc_console_survey.zig`",
    "`zigux/tests/phase11_build.zig`",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
    "`drivers/tty/hvc/hvc_console_verify.zig`",
    "`zigux/tests/phase11_hvc_cleanup.zig`",
    "`zigux/tests/phase11_hvc_console_manifest.json`",
    "cleanup-prerequisite failure replays in `drivers/tty/hvc/hvc_console_verify.zig`",
    "targetless-dispatch and no-dispatch notifier-deferral replays in `drivers/tty/hvc/hvc_console_verify.zig`",
    "notifier prerequisite, never-registered, targetless, and targetless-sysrq failure-mode replays in `drivers/tty/hvc/hvc_console_verify.zig`",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
    "`zigux/Makefile`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`make -C zigux phase11-hvc-survey`",
    "remaining Phase 11 gap is live integration depth, not missing starter coverage",
    "khvcd polling contract boundary",
    "notifier-driven versus polling-driven wakeups",
    "bounded reschedule intent",
    "`hvc_hangup()` disconnect boundary",
    "stale-count short-circuiting",
    "preserving buffered-write state when the stale port-count guard wins",
]

REQUIRED_SHARED_REPLAY_CONTRACT_MARKERS = [
    "The dedicated archival HVC evidence still stays explicit beside that shared route:",
    "`zigux/tests/phase11_hvc_console_manifest.json`",
    "`zigux/tests/phase11_hvc_console_survey.zig`",
    "`Documentation/zigux/phase11-hvc-console-survey.md`",
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
    "`make -C zigux phase11-hvc-survey`",
    "`zigux/tests/phase11_hvc_cleanup.zig` keeps the bounded `hvc_cleanup()` tty-port release handoff",
    "`drivers/tty/hvc/hvc_console_verify.zig` keeps compile-local final-close, hung-up or detached teardown, cleanup-prerequisite, notifierless-open, targetless-sysrq, never-registered notifier, targetless notifier, and notifier-prerequisite failure-mode replays beside the shared packet",
]

REQUIRED_VERIFY_REPLAY_MARKERS = [
    'test "hvc_console verify keeps final-close teardown handoff ordering explicit"',
    'test "hvc_console verify keeps hung-up and detached teardown matrix truthful"',
    'test "hvc_console verify keeps remove handoff explicit when tty teardown outlives console binding"',
    'test "hvc_console verify keeps remove handoff explicit when tty is already absent"',
    'test "hvc_console verify keeps cleanup prerequisite failures explicit"',
    'test "hvc_console verify keeps open notifier-state failures explicit"',
    'test "hvc_console verify keeps notifier prerequisite failures explicit"',
    'test "hvc_console verify keeps notifier unregister timing false for never-registered and targetless surfaces"',
    'test "hvc_console verify keeps targetless sysrq dispatch from implying notifier callbacks"',
    'test "hvc_console verify keeps sysrq notifier deferral false without dispatch"',
]

REQUIRED_MANIFEST_MARKERS = [
    '"lane_key": "P11-L16"',
    '"id": "phase11-hvc-console-driver-starter"',
    "direct-port-or-dual-impl driver-template requirement",
    '"id": "phase11-hvc-console-validation-matrix"',
    "hardware validation matrix requirement",
    '"id": "phase11-hvc-console-tty-and-teardown-parity"',
    "teardown and failure-mode parity requirement",
]

REQUIRED_BUILD_MARKERS = [
    '.name = "phase11-hvc-console-survey-tests"',
    'const hvc_console_survey_step = b.step("hvc-console-survey", "Run the dedicated Phase 11 hvc_console archival survey");',
    "hvc_console_survey_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
]

REQUIRED_MAKEFILE_MARKERS = [
    "PHONY += phase11-contract phase11-test phase11-hvc-survey phase11",
    "phase11-hvc-survey:",
    "$(PYTHON) scripts/zigux/check-phase11-hvc-survey-packet.py",
    "$(ZIG) build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all",
]

REQUIRED_WORKFLOW_MARKERS = [
    "Run dedicated Phase 11 hvc survey replay",
    "make -C zigux phase11-hvc-survey",
]

SELF_TEST_CASE_COUNT = 40


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    for rel_path in [
        SURVEY_NOTE_PATH,
        SLICE_NOTE_PATH,
        TEARDOWN_NOTE_PATH,
        VALIDATION_MATRIX_PATH,
        SHARED_REPLAY_CONTRACT_PATH,
        VERIFY_REPLAY_PATH,
        CLEANUP_REPLAY_PATH,
        MANIFEST_PATH,
        BUILD_PATH,
        MAKEFILE_PATH,
        WORKFLOW_PATH,
        SCRIPT_PATH,
    ]:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")

    if failures:
        return failures

    survey_note = read_text(root, SURVEY_NOTE_PATH)
    slice_note = read_text(root, SLICE_NOTE_PATH)
    teardown_note = read_text(root, TEARDOWN_NOTE_PATH)
    validation_matrix = read_text(root, VALIDATION_MATRIX_PATH)
    shared_replay_contract = read_text(root, SHARED_REPLAY_CONTRACT_PATH)
    verify_replay = read_text(root, VERIFY_REPLAY_PATH)
    manifest = read_text(root, MANIFEST_PATH)
    build_file = read_text(root, BUILD_PATH)
    makefile = read_text(root, MAKEFILE_PATH)
    workflow = read_text(root, WORKFLOW_PATH)

    for marker in REQUIRED_SURVEY_NOTE_MARKERS:
        if marker not in survey_note:
            failures.append(f"survey_note:{marker}")
    for marker in REQUIRED_SLICE_NOTE_MARKERS:
        if marker not in slice_note:
            failures.append(f"slice_note:{marker}")
    for marker in REQUIRED_TEARDOWN_NOTE_MARKERS:
        if marker not in teardown_note:
            failures.append(f"teardown_note:{marker}")
    for marker in REQUIRED_VALIDATION_MATRIX_MARKERS:
        if marker not in validation_matrix:
            failures.append(f"validation_matrix:{marker}")
    for marker in REQUIRED_SHARED_REPLAY_CONTRACT_MARKERS:
        if marker not in shared_replay_contract:
            failures.append(f"shared_replay_contract:{marker}")
    for marker in REQUIRED_VERIFY_REPLAY_MARKERS:
        if marker not in verify_replay:
            failures.append(f"verify_replay:{marker}")
    for marker in REQUIRED_MANIFEST_MARKERS:
        if marker not in manifest:
            failures.append(f"manifest:{marker}")
    for marker in REQUIRED_BUILD_MARKERS:
        if marker not in build_file:
            failures.append(f"build:{marker}")
    for marker in REQUIRED_MAKEFILE_MARKERS:
        if marker not in makefile:
            failures.append(f"makefile:{marker}")
    for marker in REQUIRED_WORKFLOW_MARKERS:
        if marker not in workflow:
            failures.append(f"workflow:{marker}")

    return failures


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)

    write_text(
        root / SURVEY_NOTE_PATH,
        """# Phase 11 HVC Console Survey

The live archival packet now belongs to lane `P11-L16`.

- `zigux/tests/phase11_hvc_console_survey.zig` now keeps a bounded driver-local layout checkpoint
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md` names the current shared gate
- `Documentation/zigux/phase11-hvc-console-teardown-note.md` keeps the close, cleanup, and remove ownership split explicit
- `scripts/zigux/check-phase11-hvc-survey-packet.py` keeps the dedicated archival survey note, validation matrix, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` aligned around the same delivery route
- `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml` keep those HVC review surfaces coupled to the wider Phase 11 replay route
- the bounded archival checkpoint keeps `drivers/tty/hvc/hvc_console.zig` framed as a direct-port driver starter with a hardware validation matrix and teardown and failure-mode parity kept host-free
- repo reality now carries one bounded starter for each Phase 11 simple-production-driver roadmap anchor
- current `master` now also carries the bounded khvcd polling-contract follow-through
- current `master` also keeps the bounded `hvc_hangup()` disconnect boundary explicit beside the same archival packet
- the archived note still names the stale hangup short-circuit so buffered-write state does not get overstated when port count is already zero
""",
    )
    write_text(
        root / SLICE_NOTE_PATH,
        """# Phase 11 HVC Console Slice

- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-teardown-note.md`
- adds a tiny cleanup handoff summary
- adds a tiny remove-path handoff summary
- adds a tiny khvcd polling-contract summary
- adds a tiny `hvc_hangup()` disconnect summary
- `scripts/zigux/check-phase11-hvc-survey-packet.py`
- keep that shared-versus-dedicated HVC review packet explicit
""",
    )
    write_text(
        root / TEARDOWN_NOTE_PATH,
        """# Phase 11 HVC Console Teardown Note

- `summarizeCloseBoundary()`
- `summarizeCleanupHandoff()`
- `summarizeRemoveHandoff()`
- `tty_port_put()`
- `tty_vhangup()`
- `tty_kref_put()`
- do not treat this note as evidence of live notifier callbacks
""",
    )
    write_text(
        root / VALIDATION_MATRIX_PATH,
        """# Phase 11 HVC Console Validation Matrix

- lane: `P11-L16`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `zigux/tests/phase11_build.zig`
- `Documentation/zigux/phase11-hvc-console-teardown-note.md`
- `drivers/tty/hvc/hvc_console_verify.zig`
- `zigux/tests/phase11_hvc_cleanup.zig`
- `zigux/tests/phase11_hvc_console_manifest.json`
- keeps the compile-local final-close, hung-up cleanup, and cleanup-prerequisite failure replays in `drivers/tty/hvc/hvc_console_verify.zig` explicit inside the shared packet
- keeps the compile-local targetless-dispatch and no-dispatch notifier-deferral replays in `drivers/tty/hvc/hvc_console_verify.zig` explicit inside the shared packet
- keeps the compile-local notifier prerequisite, never-registered, targetless, and targetless-sysrq failure-mode replays in `drivers/tty/hvc/hvc_console_verify.zig` explicit inside the shared packet
- `scripts/zigux/check-phase11-hvc-survey-packet.py`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`
- keep `zigux/tests/phase11_build.zig` as the shared replay path for the current starter while the dedicated archival `make -C zigux phase11-hvc-survey` bootstrap replay remains the only extra CI step for the separate survey route
- remaining Phase 11 gap is live integration depth, not missing starter coverage
- khvcd polling contract boundary
- notifier-driven versus polling-driven wakeups
- bounded reschedule intent
- `hvc_hangup()` disconnect boundary
- stale-count short-circuiting
- preserving buffered-write state when the stale port-count guard wins
""",
    )
    write_text(
        root / SHARED_REPLAY_CONTRACT_PATH,
        """# Phase 11 Shared Replay Contract

The dedicated archival HVC evidence still stays explicit beside that shared route:

- `zigux/tests/phase11_hvc_console_manifest.json`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-teardown-note.md`
- `scripts/zigux/check-phase11-hvc-survey-packet.py`
- `make -C zigux phase11-hvc-survey`

`zigux/tests/phase11_hvc_cleanup.zig` keeps the bounded `hvc_cleanup()` tty-port release handoff reviewable without implying live tty teardown.
`drivers/tty/hvc/hvc_console_verify.zig` keeps compile-local final-close, hung-up or detached teardown, cleanup-prerequisite, notifierless-open, targetless-sysrq, never-registered notifier, targetless notifier, and notifier-prerequisite failure-mode replays beside the shared packet.
""",
    )
    write_text(
        root / VERIFY_REPLAY_PATH,
        """const std = @import("std");
test "hvc_console verify keeps final-close teardown handoff ordering explicit" {
    try std.testing.expect(true);
}
test "hvc_console verify keeps hung-up and detached teardown matrix truthful" {
    try std.testing.expect(true);
}
test "hvc_console verify keeps remove handoff explicit when tty teardown outlives console binding" {
    try std.testing.expect(true);
}
test "hvc_console verify keeps remove handoff explicit when tty is already absent" {
    try std.testing.expect(true);
}
test "hvc_console verify keeps cleanup prerequisite failures explicit" {
    try std.testing.expect(true);
}
test "hvc_console verify keeps open notifier-state failures explicit" {
    try std.testing.expect(true);
}
test "hvc_console verify keeps notifier prerequisite failures explicit" {
    try std.testing.expect(true);
}
test "hvc_console verify keeps notifier unregister timing false for never-registered and targetless surfaces" {
    try std.testing.expect(true);
}
test "hvc_console verify keeps targetless sysrq dispatch from implying notifier callbacks" {
    try std.testing.expect(true);
}
test "hvc_console verify keeps sysrq notifier deferral false without dispatch" {
    try std.testing.expect(true);
}
""",
    )
    write_text(
        root / CLEANUP_REPLAY_PATH,
        """const std = @import("std");
test "synthetic hvc cleanup replay" {
    try std.testing.expect(true);
}
""",
    )
    write_text(
        root / MANIFEST_PATH,
        """{
  "lane_key": "P11-L16",
  "gaps": [
    {
      "id": "phase11-hvc-console-driver-starter",
      "why_now": "The bounded starter now satisfies the roadmap's direct-port-or-dual-impl driver-template requirement in reviewable form."
    },
    {
      "id": "phase11-hvc-console-validation-matrix",
      "why_now": "The first kernel-integration validation matrix now satisfies the roadmap's hardware validation matrix requirement without widening into host-backed I/O."
    },
    {
      "id": "phase11-hvc-console-tty-and-teardown-parity",
      "why_now": "The tiny handoff summaries keep the roadmap's teardown and failure-mode parity requirement host-free and reviewable."
    }
  ]
}
""",
    )
    write_text(
        root / BUILD_PATH,
        """const phase11_hvc_console_survey_tests = b.addTest(.{
    .name = "phase11-hvc-console-survey-tests",
});

const hvc_console_survey_step = b.step("hvc-console-survey", "Run the dedicated Phase 11 hvc_console archival survey");
hvc_console_survey_step.dependOn(&run_phase11_hvc_console_survey_tests.step);
""",
    )
    write_text(
        root / MAKEFILE_PATH,
        """PHONY += phase11-contract phase11-test phase11-hvc-survey phase11

phase11-hvc-survey:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-survey-packet.py
	cd $(ZIGUX_ROOT) && $(ZIG) build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all
""",
    )
    write_text(
        root / WORKFLOW_PATH,
        """name: zigux-bootstrap

jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - name: Run dedicated Phase 11 hvc survey replay
        run: make -C zigux phase11-hvc-survey
""",
    )
    write_text(
        root / SCRIPT_PATH,
        """#!/usr/bin/env python3
print("synthetic survey packet checker")
""",
    )


def expect_failure(root: Path, rel_path: str, marker: str, expected_failure: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace(marker, "", 1), encoding="utf-8")
    failures = validate(root)
    if expected_failure not in failures:
        raise AssertionError(f"missing expected failure {expected_failure!r}; got {failures!r}")


def expect_missing_file(root: Path, rel_path: str) -> None:
    path = root / rel_path
    path.unlink()
    failures = validate(root)
    expected_failure = f"missing_file:{rel_path}"
    if expected_failure not in failures:
        raise AssertionError(f"missing expected failure {expected_failure!r}; got {failures!r}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase11_hvc_survey_", dir=None) as tmpdir:
        root = Path(tmpdir)

        write_fixture_tree(root)
        failures = validate(root)
        if failures:
            for failure in failures:
                print(failure, file=sys.stderr)
            return 1

        write_fixture_tree(root)
        try:
            expect_failure(
                root,
                SURVEY_NOTE_PATH,
                "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
                "survey_note:`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
            )
            expect_failure(
                root,
                SURVEY_NOTE_PATH,
                "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
                "survey_note:`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
            )
            expect_failure(
                root,
                SURVEY_NOTE_PATH,
                "repo reality now carries one bounded starter for each Phase 11 simple-production-driver roadmap anchor",
                "survey_note:repo reality now carries one bounded starter for each Phase 11 simple-production-driver roadmap anchor",
            )
            expect_failure(
                root,
                SURVEY_NOTE_PATH,
                "khvcd polling-contract follow-through",
                "survey_note:khvcd polling-contract follow-through",
            )
            expect_failure(
                root,
                SURVEY_NOTE_PATH,
                "`hvc_hangup()` disconnect boundary",
                "survey_note:`hvc_hangup()` disconnect boundary",
            )
            expect_failure(
                root,
                SURVEY_NOTE_PATH,
                "stale hangup short-circuit",
                "survey_note:stale hangup short-circuit",
            )
            expect_failure(
                root,
                SLICE_NOTE_PATH,
                "tiny cleanup handoff summary",
                "slice_note:tiny cleanup handoff summary",
            )
            expect_failure(
                root,
                SLICE_NOTE_PATH,
                "tiny khvcd polling-contract summary",
                "slice_note:tiny khvcd polling-contract summary",
            )
            expect_failure(
                root,
                SLICE_NOTE_PATH,
                "shared-versus-dedicated HVC review packet",
                "slice_note:shared-versus-dedicated HVC review packet",
            )
            expect_failure(
                root,
                TEARDOWN_NOTE_PATH,
                "`tty_port_put()`",
                "teardown_note:tty_port_put()",
            )
            expect_failure(
                root,
                TEARDOWN_NOTE_PATH,
                "`tty_vhangup()`",
                "teardown_note:tty_vhangup()",
            )
            expect_failure(
                root,
                TEARDOWN_NOTE_PATH,
                "`tty_kref_put()`",
                "teardown_note:tty_kref_put()",
            )
            expect_failure(
                root,
                TEARDOWN_NOTE_PATH,
                "do not treat this note as evidence of live notifier callbacks",
                "teardown_note:do not treat this note as evidence of live notifier callbacks",
            )
            expect_failure(
                root,
                VALIDATION_MATRIX_PATH,
                "cleanup-prerequisite failure replays in `drivers/tty/hvc/hvc_console_verify.zig`",
                "validation_matrix:cleanup-prerequisite failure replays in `drivers/tty/hvc/hvc_console_verify.zig`",
            )
            expect_failure(
                root,
                VALIDATION_MATRIX_PATH,
                "targetless-dispatch and no-dispatch notifier-deferral replays in `drivers/tty/hvc/hvc_console_verify.zig`",
                "validation_matrix:targetless-dispatch and no-dispatch notifier-deferral replays in `drivers/tty/hvc/hvc_console_verify.zig`",
            )
            expect_failure(
                root,
                VALIDATION_MATRIX_PATH,
                "notifier prerequisite, never-registered, targetless, and targetless-sysrq failure-mode replays in `drivers/tty/hvc/hvc_console_verify.zig`",
                "validation_matrix:notifier prerequisite, never-registered, targetless, and targetless-sysrq failure-mode replays in `drivers/tty/hvc/hvc_console_verify.zig`",
            )
            expect_failure(
                root,
                VALIDATION_MATRIX_PATH,
                "`make -C zigux phase11-hvc-survey`",
                "validation_matrix:`make -C zigux phase11-hvc-survey`",
            )
            expect_failure(
                root,
                VALIDATION_MATRIX_PATH,
                "remaining Phase 11 gap is live integration depth, not missing starter coverage",
                "validation_matrix:remaining Phase 11 gap is live integration depth, not missing starter coverage",
            )
            expect_failure(
                root,
                VALIDATION_MATRIX_PATH,
                "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
                "validation_matrix:`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
            )
            expect_failure(
                root,
                VALIDATION_MATRIX_PATH,
                "`drivers/tty/hvc/hvc_console_verify.zig`",
                "validation_matrix:`drivers/tty/hvc/hvc_console_verify.zig`",
            )
            expect_failure(
                root,
                VALIDATION_MATRIX_PATH,
                "`zigux/tests/phase11_hvc_cleanup.zig`",
                "validation_matrix:`zigux/tests/phase11_hvc_cleanup.zig`",
            )
            expect_failure(
                root,
                VALIDATION_MATRIX_PATH,
                "khvcd polling contract boundary",
                "validation_matrix:khvcd polling contract boundary",
            )
            expect_failure(
                root,
                VALIDATION_MATRIX_PATH,
                "`hvc_hangup()` disconnect boundary",
                "validation_matrix:`hvc_hangup()` disconnect boundary",
            )
            expect_failure(
                root,
                VALIDATION_MATRIX_PATH,
                "stale-count short-circuiting",
                "validation_matrix:stale-count short-circuiting",
            )
            expect_failure(
                root,
                VALIDATION_MATRIX_PATH,
                "preserving buffered-write state when the stale port-count guard wins",
                "validation_matrix:preserving buffered-write state when the stale port-count guard wins",
            )
            expect_failure(
                root,
                SHARED_REPLAY_CONTRACT_PATH,
                "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
                "shared_replay_contract:`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
            )
            expect_failure(
                root,
                SHARED_REPLAY_CONTRACT_PATH,
                "`make -C zigux phase11-hvc-survey`",
                "shared_replay_contract:`make -C zigux phase11-hvc-survey`",
            )
            expect_failure(
                root,
                SHARED_REPLAY_CONTRACT_PATH,
                "`zigux/tests/phase11_hvc_cleanup.zig` keeps the bounded `hvc_cleanup()` tty-port release handoff",
                "shared_replay_contract:`zigux/tests/phase11_hvc_cleanup.zig` keeps the bounded `hvc_cleanup()` tty-port release handoff",
            )
            expect_failure(
                root,
                SHARED_REPLAY_CONTRACT_PATH,
                "`drivers/tty/hvc/hvc_console_verify.zig` keeps compile-local final-close, hung-up or detached teardown, cleanup-prerequisite, notifierless-open, targetless-sysrq, never-registered notifier, targetless notifier, and notifier-prerequisite failure-mode replays beside the shared packet",
                "shared_replay_contract:`drivers/tty/hvc/hvc_console_verify.zig` keeps compile-local final-close, hung-up or detached teardown, cleanup-prerequisite, notifierless-open, targetless-sysrq, never-registered notifier, targetless notifier, and notifier-prerequisite failure-mode replays beside the shared packet",
            )
            expect_failure(
                root,
                VERIFY_REPLAY_PATH,
                'test "hvc_console verify keeps final-close teardown handoff ordering explicit"',
                'verify_replay:test "hvc_console verify keeps final-close teardown handoff ordering explicit"',
            )
            expect_failure(
                root,
                VERIFY_REPLAY_PATH,
                'test "hvc_console verify keeps hung-up and detached teardown matrix truthful"',
                'verify_replay:test "hvc_console verify keeps hung-up and detached teardown matrix truthful"',
            )
            expect_failure(
                root,
                VERIFY_REPLAY_PATH,
                'test "hvc_console verify keeps remove handoff explicit when tty teardown outlives console binding"',
                'verify_replay:test "hvc_console verify keeps remove handoff explicit when tty teardown outlives console binding"',
            )
            expect_failure(
                root,
                VERIFY_REPLAY_PATH,
                'test "hvc_console verify keeps remove handoff explicit when tty is already absent"',
                'verify_replay:test "hvc_console verify keeps remove handoff explicit when tty is already absent"',
            )
            expect_failure(
                root,
                VERIFY_REPLAY_PATH,
                'test "hvc_console verify keeps notifier unregister timing false for never-registered and targetless surfaces"',
                'verify_replay:test "hvc_console verify keeps notifier unregister timing false for never-registered and targetless surfaces"',
            )
            expect_failure(
                root,
                VERIFY_REPLAY_PATH,
                'test "hvc_console verify keeps targetless sysrq dispatch from implying notifier callbacks"',
                'verify_replay:test "hvc_console verify keeps targetless sysrq dispatch from implying notifier callbacks"',
            )
            expect_failure(
                root,
                VERIFY_REPLAY_PATH,
                'test "hvc_console verify keeps sysrq notifier deferral false without dispatch"',
                'verify_replay:test "hvc_console verify keeps sysrq notifier deferral false without dispatch"',
            )
            expect_failure(
                root,
                MANIFEST_PATH,
                "direct-port-or-dual-impl driver-template requirement",
                "manifest:direct-port-or-dual-impl driver-template requirement",
            )
            expect_failure(
                root,
                MAKEFILE_PATH,
                "$(PYTHON) scripts/zigux/check-phase11-hvc-survey-packet.py",
                "makefile:$(PYTHON) scripts/zigux/check-phase11-hvc-survey-packet.py",
            )
            expect_missing_file(root, SLICE_NOTE_PATH)
            expect_missing_file(root, VERIFY_REPLAY_PATH)
            expect_missing_file(root, CLEANUP_REPLAY_PATH)
            expect_missing_file(root, MANIFEST_PATH)
        except AssertionError as exc:
            print(str(exc), file=sys.stderr)
            return 1

    print("PHASE11_HVC_SURVEY_PACKET_SELFTEST=pass")
    print(f"PHASE11_HVC_SURVEY_PACKET_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the dedicated Phase 11 hvc survey packet stays aligned."
    )
    parser.add_argument("--self-test", action="store_true", help="exercise the checker against a synthetic fixture tree")
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to validate")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("PHASE11_HVC_SURVEY_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())