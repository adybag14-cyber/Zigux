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
DOCS_ROOT_README_PATH = "Documentation/zigux/README.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
VERIFY_REPLAY_PATH = "drivers/tty/hvc/hvc_console_verify.zig"
SURVEY_REPLAY_PATH = "zigux/tests/phase11_hvc_console_survey.zig"
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
    "write-to-hangup",
    "retry-after-`-EAGAIN`",
    "partial-write carryover",
    "stale-hangup buffered-byte preservation",
    "resize-work cancellation",
    "stale-count short-circuiting",
    "notifier-hangup ownership",
    "buffered-write clearing",
    "kept console binding",
    "stale hangup short-circuit",
    "targetless-sysrq",
    "notifier-prerequisite failure-mode replays",
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
    "summarizeWriteTeardownHandoff()",
    "summarizeHangupDisconnect()",
    "tty_port_put()",
    "tty_vhangup()",
    "tty_kref_put()",
    "retry-after-`-EAGAIN`",
    "fatal-drop with no invented buffered bytes",
    "partial-write carryover",
    "stale-hangup buffered-byte preservation",
    "resize-work cancellation",
    "stale-count short-circuiting",
    "tty detachment",
    "buffered-write clearing",
    "notifier-hangup ownership",
    "kept console binding",
    "oversized buffered-write rejection",
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
    "minimum-timeout flooring, maximum-timeout clamping",
    "worker-entry sleep, kick, poll-mask, timeout-backoff, and invalid-open-count replays in `drivers/tty/hvc/hvc_console_verify.zig`",
    "`hvc_hangup()` disconnect boundary",
    "stale-count short-circuiting",
    "preserving buffered-write state when the stale port-count guard wins",
    "compile-local impossible buffered-write failure replay in `drivers/tty/hvc/hvc_console_verify.zig`",
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
    "no-dispatch sysrq notifier-deferral",
    "minimum-timeout flooring, maximum-timeout clamping",
    "The same verifier also keeps the impossible hangup buffered-write failure-mode replay explicit beside that shared packet.",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md` keeps the close, cleanup, remove, write-to-hangup, and hangup-disconnect ownership split explicit in one driver-local note",
]

REQUIRED_DOCS_ROOT_README_MARKERS = [
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`Documentation/zigux/phase11-hvc-console-survey.md`",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
    "`make -C zigux phase11-hvc-survey`",
]

REQUIRED_SCRIPTS_README_MARKERS = [
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
    "`zigux/tests/phase11_hvc_console_survey.zig`",
    "`make -C zigux phase11-hvc-survey`",
]

REQUIRED_TESTS_README_MARKERS = [
    "`Documentation/zigux/phase11-hvc-console-survey.md`",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
    "`zigux/tests/phase11_hvc_console_survey.zig`",
    "`make -C zigux phase11-hvc-survey`",
]

REQUIRED_REVIEW_CHECKLIST_MARKERS = [
    "`Documentation/zigux/phase11-hvc-console-survey.md`",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
    "`zigux/tests/phase11_hvc_console_survey.zig`",
    "`make -C zigux phase11-hvc-survey`",
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
    'test "hvc_console verify keeps khvcd worker-entry sleep, kick, and poll-mask boundaries explicit"',
    "try std.testing.expectEqual(hvc_console.min_timeout_ms, active_worker.timeout_ms_before_sleep);",
    "try std.testing.expectEqual(hvc_console.max_timeout_ms, idle_worker.timeout_ms_after_backoff);",
    'try std.testing.expectError(error.InvalidOpenCount, console.summarizeKhvcdWorkerEntry(.{',
    'test "hvc_console verify rejects impossible hangup buffered-write state"',
]

REQUIRED_SURVEY_REPLAY_MARKERS = [
    'test "phase11 hvc console survey keeps a bounded winsize layout proof"',
    'test "phase11 hvc console survey keeps a bounded hv_ops layout proof"',
    'try expectContains(note, "close, cleanup, remove, write-to-hangup, and hangup-disconnect ownership split");',
    'try expectContains(note, "retry-after-`-EAGAIN`");',
    'try expectContains(note, "partial-write carryover");',
    'try expectContains(note, "stale-hangup buffered-byte preservation");',
    'try expectContains(teardown_note, "summarizeWriteTeardownHandoff()");',
    'try expectContains(teardown_note, "fatal-drop with no invented buffered bytes");',
    'try expectContains(teardown_note, "partial-write carryover");',
    'try expectContains(teardown_note, "stale-hangup buffered-byte preservation");',
    "layout_assert.assertSize(WinSize, 8);",
    'layout_assert.assertOffset(WinSize, "ws_ypixel", 6);',
    "layout_assert.assertSize(HvOps, 72);",
    "layout_assert.assertAlign(HvOps, 8);",
    'layout_assert.assertFieldType(HvOps, "notifier_hangup", HvOpsNotifierHangup);',
    'layout_assert.assertOffset(HvOps, "dtr_rts", 64);',
]

REQUIRED_CLEANUP_REPLAY_MARKERS = [
    'test "phase11 hvc console keeps hvc_cleanup tty-port release boundaries reviewable"',
    'test "phase11 hvc console keeps write-teardown hangup buffering split reviewable"',
    "final_cleanup.tty_port_put_requested",
    "hangup_cleanup.close_skipped",
    "try std.testing.expectEqual(hvc_console.FlushIntent.retry_after_eagain, active_hangup.flush_intent);",
    "try std.testing.expectEqual(@as(usize, 2), stale_hangup.buffered_write_len_after_hangup);",
    "try std.testing.expectEqual(hvc_console.FlushProgress.dropped_on_error, fatal_write.flush_progress);",
    "error.CleanupRequiresFinalCloseOrHangup",
    "error.CleanupRequiresTtyPortReference",
    "try std.testing.expectError(error.ConsoleUnavailable, console.summarizeWriteTeardownHandoff(.{",
    "error.ConsoleUnavailable",
]

REQUIRED_MANIFEST_MARKERS = [
    '"lane_key": "P11-L16"',
    '"winsize_layout_assert_present": true',
    '"hv_ops_layout_assert_present": true',
    '"id": "phase11-hvc-console-winsize-layout-assert"',
    '"id": "phase11-hvc-console-hv-ops-layout-assert"',
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

MARKER_GROUPS = {
    "survey_note": (SURVEY_NOTE_PATH, REQUIRED_SURVEY_NOTE_MARKERS),
    "slice_note": (SLICE_NOTE_PATH, REQUIRED_SLICE_NOTE_MARKERS),
    "teardown_note": (TEARDOWN_NOTE_PATH, REQUIRED_TEARDOWN_NOTE_MARKERS),
    "validation_matrix": (VALIDATION_MATRIX_PATH, REQUIRED_VALIDATION_MATRIX_MARKERS),
    "shared_replay_contract": (SHARED_REPLAY_CONTRACT_PATH, REQUIRED_SHARED_REPLAY_CONTRACT_MARKERS),
    "docs_root_readme": (DOCS_ROOT_README_PATH, REQUIRED_DOCS_ROOT_README_MARKERS),
    "scripts_readme": (SCRIPTS_README_PATH, REQUIRED_SCRIPTS_README_MARKERS),
    "tests_readme": (TESTS_README_PATH, REQUIRED_TESTS_README_MARKERS),
    "review_checklist": (REVIEW_CHECKLIST_PATH, REQUIRED_REVIEW_CHECKLIST_MARKERS),
    "verify_replay": (VERIFY_REPLAY_PATH, REQUIRED_VERIFY_REPLAY_MARKERS),
    "survey_replay": (SURVEY_REPLAY_PATH, REQUIRED_SURVEY_REPLAY_MARKERS),
    "cleanup_replay": (CLEANUP_REPLAY_PATH, REQUIRED_CLEANUP_REPLAY_MARKERS),
    "manifest": (MANIFEST_PATH, REQUIRED_MANIFEST_MARKERS),
    "build": (BUILD_PATH, REQUIRED_BUILD_MARKERS),
    "makefile": (MAKEFILE_PATH, REQUIRED_MAKEFILE_MARKERS),
    "workflow": (WORKFLOW_PATH, REQUIRED_WORKFLOW_MARKERS),
}

REQUIRED_EXISTING_PATHS = [
    SURVEY_NOTE_PATH,
    SLICE_NOTE_PATH,
    TEARDOWN_NOTE_PATH,
    VALIDATION_MATRIX_PATH,
    SHARED_REPLAY_CONTRACT_PATH,
    DOCS_ROOT_README_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    REVIEW_CHECKLIST_PATH,
    VERIFY_REPLAY_PATH,
    SURVEY_REPLAY_PATH,
    CLEANUP_REPLAY_PATH,
    MANIFEST_PATH,
    BUILD_PATH,
    MAKEFILE_PATH,
    WORKFLOW_PATH,
    SCRIPT_PATH,
]

SELF_TEST_CASE_COUNT = 23


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    for rel_path in REQUIRED_EXISTING_PATHS:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")

    if failures:
        return failures

    for label, (rel_path, markers) in MARKER_GROUPS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"{label}:{marker}")

    return failures


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)

    for _, (rel_path, markers) in MARKER_GROUPS.items():
        write_text(root / rel_path, "\n".join(markers) + "\n")

    write_text(
        root / SCRIPT_PATH,
        "#!/usr/bin/env python3\nprint('fixture')\n",
    )


def expect_failure(root: Path, rel_path: str, marker: str, expected_failure: str) -> None:
    target = root / rel_path
    original = target.read_text(encoding="utf-8")
    if marker not in original:
        raise AssertionError(f"fixture for {rel_path} does not include marker {marker!r}")
    target.write_text(original.replace(marker, "", 1), encoding="utf-8")
    failures = validate(root)
    if expected_failure not in failures:
        raise AssertionError(f"expected {expected_failure!r}, saw {failures!r}")
    target.write_text(original, encoding="utf-8")


def expect_missing_file(root: Path, rel_path: str) -> None:
    target = root / rel_path
    target.unlink()
    failures = validate(root)
    expected_failure = f"missing_file:{rel_path}"
    if expected_failure not in failures:
        raise AssertionError(f"expected {expected_failure!r}, saw {failures!r}")
    write_text(target, "restored\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase11_hvc_survey_packet_") as tmpdir:
        root = Path(tmpdir)
        fixture_root = root / "repo"
        write_fixture_tree(fixture_root)

        failures = validate(fixture_root)
        if failures:
            for failure in failures:
                print(failure, file=sys.stderr)
            return 1

        try:
            expect_failure(
                fixture_root,
                SURVEY_NOTE_PATH,
                "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
                "survey_note:`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
            )
            expect_failure(
                fixture_root,
                DOCS_ROOT_README_PATH,
                "`make -C zigux phase11-hvc-survey`",
                "docs_root_readme:`make -C zigux phase11-hvc-survey`",
            )
            expect_failure(
                fixture_root,
                SCRIPTS_README_PATH,
                "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
                "scripts_readme:`scripts/zigux/check-phase11-hvc-survey-packet.py`",
            )
            expect_failure(
                fixture_root,
                TESTS_README_PATH,
                "`zigux/tests/phase11_hvc_console_survey.zig`",
                "tests_readme:`zigux/tests/phase11_hvc_console_survey.zig`",
            )
            expect_failure(
                fixture_root,
                REVIEW_CHECKLIST_PATH,
                "`Documentation/zigux/phase11-hvc-console-survey.md`",
                "review_checklist:`Documentation/zigux/phase11-hvc-console-survey.md`",
            )
            expect_failure(
                fixture_root,
                MAKEFILE_PATH,
                "$(PYTHON) scripts/zigux/check-phase11-hvc-survey-packet.py",
                "makefile:$(PYTHON) scripts/zigux/check-phase11-hvc-survey-packet.py",
            )
            expect_failure(
                fixture_root,
                WORKFLOW_PATH,
                "make -C zigux phase11-hvc-survey",
                "workflow:make -C zigux phase11-hvc-survey",
            )
            expect_failure(
                fixture_root,
                SHARED_REPLAY_CONTRACT_PATH,
                "`make -C zigux phase11-hvc-survey`",
                "shared_replay_contract:`make -C zigux phase11-hvc-survey`",
            )
            expect_failure(
                fixture_root,
                SHARED_REPLAY_CONTRACT_PATH,
                "no-dispatch sysrq notifier-deferral",
                "shared_replay_contract:no-dispatch sysrq notifier-deferral",
            )
            expect_failure(
                fixture_root,
                SHARED_REPLAY_CONTRACT_PATH,
                "minimum-timeout flooring, maximum-timeout clamping",
                "shared_replay_contract:minimum-timeout flooring, maximum-timeout clamping",
            )
            expect_failure(
                fixture_root,
                SHARED_REPLAY_CONTRACT_PATH,
                "The same verifier also keeps the impossible hangup buffered-write failure-mode replay explicit beside that shared packet.",
                "shared_replay_contract:The same verifier also keeps the impossible hangup buffered-write failure-mode replay explicit beside that shared packet.",
            )
            expect_failure(
                fixture_root,
                VALIDATION_MATRIX_PATH,
                "`make -C zigux phase11-hvc-survey`",
                "validation_matrix:`make -C zigux phase11-hvc-survey`",
            )
            expect_failure(
                fixture_root,
                VALIDATION_MATRIX_PATH,
                "minimum-timeout flooring, maximum-timeout clamping",
                "validation_matrix:minimum-timeout flooring, maximum-timeout clamping",
            )
            expect_failure(
                fixture_root,
                VALIDATION_MATRIX_PATH,
                "worker-entry sleep, kick, poll-mask, timeout-backoff, and invalid-open-count replays in `drivers/tty/hvc/hvc_console_verify.zig`",
                "validation_matrix:worker-entry sleep, kick, poll-mask, timeout-backoff, and invalid-open-count replays in `drivers/tty/hvc/hvc_console_verify.zig`",
            )
            expect_failure(
                fixture_root,
                VERIFY_REPLAY_PATH,
                "try std.testing.expectEqual(hvc_console.min_timeout_ms, active_worker.timeout_ms_before_sleep);",
                "verify_replay:try std.testing.expectEqual(hvc_console.min_timeout_ms, active_worker.timeout_ms_before_sleep);",
            )
            expect_failure(
                fixture_root,
                VERIFY_REPLAY_PATH,
                "try std.testing.expectEqual(hvc_console.max_timeout_ms, idle_worker.timeout_ms_after_backoff);",
                "verify_replay:try std.testing.expectEqual(hvc_console.max_timeout_ms, idle_worker.timeout_ms_after_backoff);",
            )
            expect_failure(
                fixture_root,
                VERIFY_REPLAY_PATH,
                "try std.testing.expectError(error.InvalidOpenCount, console.summarizeKhvcdWorkerEntry(.{",
                "verify_replay:try std.testing.expectError(error.InvalidOpenCount, console.summarizeKhvcdWorkerEntry(.{",
            )
            expect_failure(
                fixture_root,
                CLEANUP_REPLAY_PATH,
                'test "phase11 hvc console keeps write-teardown hangup buffering split reviewable"',
                'cleanup_replay:test "phase11 hvc console keeps write-teardown hangup buffering split reviewable"',
            )
            expect_failure(
                fixture_root,
                CLEANUP_REPLAY_PATH,
                "try std.testing.expectEqual(hvc_console.FlushIntent.retry_after_eagain, active_hangup.flush_intent);",
                "cleanup_replay:try std.testing.expectEqual(hvc_console.FlushIntent.retry_after_eagain, active_hangup.flush_intent);",
            )
            expect_failure(
                fixture_root,
                CLEANUP_REPLAY_PATH,
                "try std.testing.expectEqual(@as(usize, 2), stale_hangup.buffered_write_len_after_hangup);",
                "cleanup_replay:try std.testing.expectEqual(@as(usize, 2), stale_hangup.buffered_write_len_after_hangup);",
            )
            expect_failure(
                fixture_root,
                CLEANUP_REPLAY_PATH,
                "try std.testing.expectEqual(hvc_console.FlushProgress.dropped_on_error, fatal_write.flush_progress);",
                "cleanup_replay:try std.testing.expectEqual(hvc_console.FlushProgress.dropped_on_error, fatal_write.flush_progress);",
            )
            expect_failure(
                fixture_root,
                CLEANUP_REPLAY_PATH,
                "try std.testing.expectError(error.ConsoleUnavailable, console.summarizeWriteTeardownHandoff(.{",
                "cleanup_replay:try std.testing.expectError(error.ConsoleUnavailable, console.summarizeWriteTeardownHandoff(.{",
            )
            expect_missing_file(fixture_root, SCRIPT_PATH)
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