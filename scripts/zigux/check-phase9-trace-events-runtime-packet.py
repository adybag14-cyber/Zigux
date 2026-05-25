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
PHASE9_BUILD_PATH = "zigux/tests/phase9_build.zig"
LOADER_SUBSTRATE_DRIFT_PATH = "zigux/tests/runtime_trace_events_loader_substrate_drift.zig"
SAMPLE_PATH = "samples/zigux/runtime_trace_events.zig"
UNREGISTERED_GATE_SAMPLE_PATH = "samples/zigux/runtime_trace_events_unregistered_gate.zig"
REENTRY_GATE_SAMPLE_PATH = "samples/zigux/runtime_trace_events_registration_reentry_gate.zig"
EXIT_ROLLBACK_GUARD_SAMPLE_PATH = "samples/zigux/runtime_trace_events_exit_rollback_guard.zig"
REINIT_ROLLBACK_GUARD_SAMPLE_PATH = "samples/zigux/runtime_trace_events_reinit_rollback_guard.zig"
REINIT_REEXIT_GUARD_SAMPLE_PATH = "samples/zigux/runtime_trace_events_reinit_reexit_guard.zig"
DIRECT_SUMMARY_CHECKER_PATH = "scripts/zigux/check-phase9-trace-events-direct-summary.py"
SUMMARY_PRESERVATION_CHECKER_PATH = "scripts/zigux/check-phase9-trace-events-summary-preservation.py"
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
        "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
        "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
        "`scripts/zigux/check-phase9-trace-events-direct-summary.py`",
        "`scripts/zigux/check-phase9-trace-events-summary-preservation.py`",
        "The shared runtime-loader allocator/init-flow and command/environment boundary packet now survives as a narrower direct-readback shared-owner surface",
        "`phase9-runtime-loader-shared-tests`",
        "current `master` therefore supports a partial runtime bitmap reminder packet plus the returned shared allocator/init-flow and command/environment boundary packet",
    ],
    SURVEY_NOTE_PATH: [
        "`samples/zigux/runtime_trace_events.zig`",
        "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
        "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
        "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
        "`samples/zigux/runtime_trace_events_reinit_rollback_guard.zig`",
        "`samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`",
        "`zigux/tests/runtime_trace_events_manifest.json`",
        "`zigux/tests/runtime_trace_events_survey.zig`",
        "`Documentation/zigux/phase9-runtime-trace-events-module-slice.md`",
        ".provides_selftest_hook = true",
        "initialized, selftest_complete, and exited lifecycle tracking",
        "The direct sample also now keeps initialized-stage clean exit explicit",
        "The direct sample also keeps rejected re-selftest rollback explicit",
        "The same exit-rollback companion also keeps initialized-stage direct-activity failed-exit rollback explicit before selftest replay",
        "Its paired initialized direct-activity proof in `test \\\"phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest\\\"`",
        "The re-init rollback companion still keeps rejected re-init rollback explicit across initialized, selftest-complete, and exited states",
        "The reinit/reexit companion still keeps rejected re-init and rejected re-exit rollback explicit after both initialized direct activity and selftest-ready replay",
        "Current `master` also now keeps an adjacent shared loader-handoff build shard in `zigux/tests/phase9_build.zig`",
        "`phase9-runtime-loader-allocator-init-flow-tests`",
        "`phase9-runtime-loader-command-env-boundary-guard-tests`",
        "`phase9-runtime-loader-shared-tests`",
        "`zigux/kernel/runtime_loader.zig`",
        "`zigux/kernel/runtime_loader_contract.zig`",
        "Do not invent `validate-phase9.py`",
    ],
    MODULE_SLICE_PATH: [
        "`Documentation/zigux/phase9-runtime-trace-events-survey.md`",
        "`zigux/tests/runtime_trace_events_manifest.json`",
        "`zigux/tests/runtime_trace_events_survey.zig`",
        ".provides_selftest_hook = true",
        "initialized, selftest_complete, and exited lifecycle tracking",
        "The direct sample also keeps rejected re-selftest rollback explicit: `test \\\"trace-events sample keeps rejected re-selftest rollback explicit\\\"` proves `runSelftest()` stays rejected after both the selftest_complete and exited summaries without drift.",
        "The shipped cold-stage guard in `test \\\"trace-events sample keeps selftest replay-summary continuity explicit after direct pilot activity\\\"`",
        "The same exit-rollback companion also keeps initialized-stage direct-activity failed-exit rollback explicit before selftest replay",
        "Its paired initialized-direct-activity proof in `test \\\"phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest\\\"`",
        "The re-init rollback companion keeps rejected `init()` retries fail-closed across initialized, selftest-complete, and exited summaries without mutating the captured lifecycle checkpoints.",
        "The reinit/reexit companion still keeps rejected re-init and rejected re-exit rollback explicit after both initialized direct activity and selftest-ready replay.",
        "sample-local pilot-module reviewability",
        "broader shared runtime-loader packet",
        "`zigux/tests/phase9_build.zig`",
        "Do not invent `validate-phase9.py`",
    ],
    SAMPLES_README_PATH: [
        "`samples/zigux/runtime_trace_events.zig`",
        "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
        "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
        "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
        "`samples/zigux/runtime_trace_events_reinit_rollback_guard.zig`",
        "`samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`",
        "The surviving direct runtime-module sample packet in this directory is still centered on `samples/zigux/runtime_trace_events.zig`.",
        "Keep `samples/zigux/runtime_trace_events_unregistered_gate.zig` explicit as the unregistered function-thread fail-closed companion for the same direct runtime packet.",
        "Keep `samples/zigux/runtime_trace_events.zig` explicit as the direct runtime sample, including the rejected re-selftest rollback proof that keeps both selftest-complete and exited summaries stable when `runSelftest()` is retried out of lifecycle order.",
        "Keep `samples/zigux/runtime_trace_events_exit_rollback_guard.zig` explicit as the failed-exit rollback companion for the selftest-ready proof plus both the initialized no-direct-activity and initialized direct-activity lifecycle proofs in the same packet.",
        "Keep `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` explicit as the reusable registration-reentry companion, including the initialized direct-activity clean-exit proof without selftest.",
        "Keep `samples/zigux/runtime_trace_events_reinit_rollback_guard.zig` explicit as the rejected re-init rollback companion for initialized, selftest-complete, and exited lifecycle checkpoints in the same direct runtime packet.",
        "Keep `samples/zigux/runtime_trace_events_reinit_reexit_guard.zig` explicit as the paired rejected re-init plus rejected re-exit rollback companion after initialized direct activity and selftest-ready replay in the same direct runtime packet.",
        "Fresh trusted mixed reread on 2026-05-23 also confirms a broader runtime bitmap sample-side packet on current `master`",
        "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
        "`zigux/tests/runtime_bitmap_module.zig`",
        "`zigux/tests/runtime_bitmap_diff.zig`",
        "Keep `samples/zigux/runtime_bitmap.zig` explicit as the bounded two-word in-memory bitmap starter proof with selftest-hook metadata, sparse iteration, parse-and-print replay, range mutation, copy behavior, and direct exit guards.",
        "Keep `samples/zigux/runtime_bitmap_cold_stage_guard.zig` explicit as the returned cold-stage selftest, exit, mutation, and source-lifecycle guard companion proof for the same runtime bitmap starter.",
        "Keep `samples/zigux/runtime_bitmap_loader.zig` explicit as the returned loader-input companion proof for the same runtime bitmap starter.",
        "Keep `samples/zigux/runtime_bitmap_top_bit_contract.zig` explicit as the returned highest-valid-bit companion proof for the same runtime bitmap starter.",
        "Keep `zigux/tests/runtime_bitmap_manifest.json` explicit as the manifest-backed ownership packet for the same runtime bitmap reminder family.",
        "Keep `zigux/tests/runtime_bitmap_module.zig` explicit as the module-side descriptor and lifecycle replay packet for the same runtime bitmap starter.",
        "Keep `zigux/tests/runtime_bitmap_diff.zig` explicit as the bounded diff-side summary replay packet for the same runtime bitmap starter.",
        "Keep that broader bitmap-side visibility from being used to imply that the broader shared runtime-loader packet returned or that blocked publication boundaries are complete.",
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
        'try std.testing.expectEqualStrings("P9-L11", manifest.ownership_map[4].owner);',
        'try expectContains(survey_note, "adjacent shared loader-handoff build shard in `zigux/tests/phase9_build.zig`");',
        'try expectContains(workflow_file, "python3 scripts/zigux/check-phase9-trace-events-direct-summary.py --self-test");',
        'try expectContains(workflow_file, "python3 scripts/zigux/check-phase9-trace-events-direct-summary.py");',
        'try expectContains(workflow_file, "python3 scripts/zigux/check-phase9-trace-events-summary-preservation.py --self-test");',
        'try expectContains(workflow_file, "python3 scripts/zigux/check-phase9-trace-events-summary-preservation.py");',
        'try expectContains(workflow_file, "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test");',
    ],
    PHASE9_BUILD_PATH: [
        '.name = "phase9-runtime-loader-allocator-init-flow-tests"',
        '.name = "phase9-runtime-loader-command-env-boundary-guard-tests"',
        '.name = "phase9-runtime-loader-shared-tests"',
        '.name = "phase9-runtime-trace-events-loader-substrate-drift-tests"',
        '.name = "phase9-runtime-trace-events-tests"',
        '.name = "phase9-runtime-trace-events-module-tests"',
        '.name = "phase9-runtime-trace-events-unregistered-gate-tests"',
        '.name = "phase9-runtime-trace-events-exit-rollback-guard-tests"',
        '.name = "phase9-runtime-trace-events-registration-reentry-gate-tests"',
        '.name = "phase9-runtime-trace-events-reinit-rollback-guard-tests"',
        '.name = "phase9-runtime-trace-events-reinit-reexit-guard-tests"',
        '.name = "phase9-first-loadable-runtime-module-parity-survey-tests"',
        "runtime_loader_allocator_init_flow.zig",
        "runtime_trace_events_loader_substrate_drift.zig",
        "../../samples/zigux/runtime_trace_events.zig",
        "../../samples/zigux/runtime_trace_events_unregistered_gate.zig",
        "../../samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
        "../../samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
        "../../samples/zigux/runtime_trace_events_reinit_rollback_guard.zig",
        "../../samples/zigux/runtime_trace_events_reinit_reexit_guard.zig",
    ],
    LOADER_SUBSTRATE_DRIFT_PATH: [
        'const runtime_loader = @import("runtime_loader");',
        ".requires_runtime_substrate = true",
        '.entry_symbol = "zigux_runtime_trace_events_init"',
        '.exit_symbol = "zigux_runtime_trace_events_exit"',
        'test "phase9 runtime trace-events shared loader rejects prepared substrate drift before handoff" {',
        'test "phase9 runtime trace-events shared loader rejects release drift after waiting handoff" {',
        'test "phase9 runtime trace-events shared loader rejects approved-family release drift after waiting handoff" {',
        "error.PreparedPlanDrift",
    ],
    SAMPLE_PATH: [
        '.name = "runtime_trace_events"',
        '.anchor = "samples/trace_events/trace-events-sample.c"',
        ".requires_runtime_substrate = true",
        ".provides_selftest_hook = true",
        'test "trace-events sample preserves initialized summary across direct exit without selftest" {',
        "try std.testing.expectEqual(@as(usize, 0), before_exit.selftest_runs);",
        "try module.exit();",
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
        "try std.testing.expectEqual(@as(usize, 0), before_exit.selftest_runs);",
        "try std.testing.expect(std.meta.eql(after_exit, after_rejected_lifecycle));",
    ],
    EXIT_ROLLBACK_GUARD_SAMPLE_PATH: [
        'test "phase9 trace-events sample keeps exit rollback explicit after reusable selftest replay" {',
        "error.OutstandingRegistration",
        'test "phase9 trace-events sample keeps initialized failed-exit rollback explicit before selftest replay" {',
        'test "phase9 trace-events sample keeps initialized direct-activity exit rollback explicit before selftest replay" {',
        "try expectSummaryStable(exited_before_rejected_ops, exited_after_rejected_ops);",
    ],
    DIRECT_SUMMARY_CHECKER_PATH: [
        'DIRECT_SAMPLE_PATH = "samples/zigux/runtime_trace_events.zig"',
        'print("PHASE9_TRACE_EVENTS_DIRECT_SUMMARY_SELF_TEST=pass")',
        'print("PHASE9_TRACE_EVENTS_DIRECT_SUMMARY=pass")',
    ],
    SUMMARY_PRESERVATION_CHECKER_PATH: [
        'EXIT_ROLLBACK_GUARD_SAMPLE_PATH = "samples/zigux/runtime_trace_events_exit_rollback_guard.zig"',
        'REENTRY_GATE_SAMPLE_PATH = "samples/zigux/runtime_trace_events_registration_reentry_gate.zig"',
        'print("PHASE9_TRACE_EVENTS_SUMMARY_PRESERVATION_SELF_TEST=pass")',
        'print("PHASE9_TRACE_EVENTS_SUMMARY_PRESERVATION=pass")',
    ],
    WORKFLOW_PATH: [
        "python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test",
        "python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py",
        "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test",
        "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py",
        "python3 scripts/zigux/check-phase9-trace-events-direct-summary.py --self-test",
        "python3 scripts/zigux/check-phase9-trace-events-direct-summary.py",
        "python3 scripts/zigux/check-phase9-trace-events-summary-preservation.py --self-test",
        "python3 scripts/zigux/check-phase9-trace-events-summary-preservation.py",
        "zig test samples/zigux/runtime_trace_events.zig",
        "zig test samples/zigux/runtime_trace_events_unregistered_gate.zig",
        "zig test samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
        "zig test samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
        "zig test samples/zigux/runtime_trace_events_reinit_rollback_guard.zig",
        "zig test samples/zigux/runtime_trace_events_reinit_reexit_guard.zig",
        "zig test zigux/tests/runtime_trace_events_survey.zig",
    ],
}

FILE_EXACT_ONCE_MARKERS: dict[str, list[str]] = {
    SURVEY_NOTE_PATH: [
        "The same exit-rollback companion also keeps initialized-stage direct-activity failed-exit rollback explicit before selftest replay: `error.OutstandingRegistration` leaves the initialized direct-activity summary unchanged after one main replay plus one function-thread replay, the later unregister stays explicit, and the module can still reach the selftest_complete summary without drift.",
        'Its paired initialized direct-activity proof in `test "phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest"` keeps one direct main replay plus one later function-thread replay explicit, preserves that initialized summary until `exit()` succeeds, and then keeps later lifecycle calls rejected without drift.',
    ],
    MODULE_SLICE_PATH: [
        "The same exit-rollback companion also keeps initialized-stage direct-activity failed-exit rollback explicit before selftest replay by proving `error.OutstandingRegistration` leaves one main replay plus one function-thread replay unchanged until unregister and the later `runSelftest()` replay succeeds without drift.",
        'Its paired initialized-direct-activity proof in `test "phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest"` keeps one main replay plus one function-thread replay explicit, preserves that initialized summary until `exit()` succeeds, and then keeps later lifecycle calls rejected without drift.',
    ],
    SAMPLES_README_PATH: [
        "Keep `samples/zigux/runtime_trace_events.zig` explicit as the direct runtime sample, including the rejected re-selftest rollback proof that keeps both selftest-complete and exited summaries stable when `runSelftest()` is retried out of lifecycle order.",
        "Keep `samples/zigux/runtime_trace_events_unregistered_gate.zig` explicit as the unregistered function-thread fail-closed companion for the same direct runtime packet.",
        "Keep `samples/zigux/runtime_trace_events_exit_rollback_guard.zig` explicit as the failed-exit rollback companion for the selftest-ready proof plus both the initialized no-direct-activity and initialized direct-activity lifecycle proofs in the same packet.",
        "Keep `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` explicit as the reusable registration-reentry companion, including the initialized direct-activity clean-exit proof without selftest.",
        "Keep `samples/zigux/runtime_trace_events_reinit_rollback_guard.zig` explicit as the rejected re-init rollback companion for initialized, selftest-complete, and exited lifecycle checkpoints in the same direct runtime packet.",
        "Keep `samples/zigux/runtime_trace_events_reinit_reexit_guard.zig` explicit as the paired rejected re-init plus rejected re-exit rollback companion after initialized direct activity and selftest-ready replay in the same direct runtime packet.",
    ],
    WORKFLOW_PATH: [
        "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test",
        "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py",
        "python3 scripts/zigux/check-phase9-trace-events-direct-summary.py --self-test",
        "python3 scripts/zigux/check-phase9-trace-events-direct-summary.py",
        "python3 scripts/zigux/check-phase9-trace-events-summary-preservation.py --self-test",
        "python3 scripts/zigux/check-phase9-trace-events-summary-preservation.py",
        "zig test samples/zigux/runtime_trace_events_reinit_rollback_guard.zig",
        "zig test samples/zigux/runtime_trace_events_reinit_reexit_guard.zig",
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


def duplicate_marker_occurrence(content: str, marker: str) -> str:
    return content.replace(marker, f"{marker}\n{marker}", 1)


def count_exact_line_occurrences(content: str, marker: str) -> int:
    return sum(1 for line in content.splitlines() if line == marker)


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

    for rel_path, markers in FILE_EXACT_ONCE_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            count = count_exact_line_occurrences(text, marker)
            if count != 1:
                failures.append(f"expected_exact_once:{rel_path}:{marker}:count={count}")

    return failures


def seed_fixture_tree(base: Path) -> None:
    fixture_paths = set(FILE_MARKERS) | set(FILE_EXACT_ONCE_MARKERS)
    for rel_path in fixture_paths:
        markers = list(FILE_MARKERS.get(rel_path, []))
        for marker in FILE_EXACT_ONCE_MARKERS.get(rel_path, []):
            if marker not in markers:
                markers.append(marker)
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

        for rel_path, markers in FILE_EXACT_ONCE_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = read_text(base, rel_path)
                write_text(base / rel_path, duplicate_marker_occurrence(current, marker))
                expect_failure(base, f"expected_exact_once:{rel_path}:{marker}:count=2")

        for rel_path in FILE_MARKERS:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        print("PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SELF_TEST=pass")
        print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_FILE_COUNT={len(FILE_MARKERS)}")
        print(
            "PHASE9_TRACE_EVENTS_RUNTIME_PACKET_EXACT_ONCE_MARKER_COUNT="
            f"{sum(len(markers) for markers in FILE_EXACT_ONCE_MARKERS.values())}"
        )
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
    print(
        "PHASE9_TRACE_EVENTS_RUNTIME_PACKET_EXACT_ONCE_MARKER_COUNT="
        f"{sum(len(markers) for markers in FILE_EXACT_ONCE_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())