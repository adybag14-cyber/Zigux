const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE9_TRACE_EVENTS_RUNTIME_PACKET=pass";
pub const self_test_pass_marker = "PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "`samples/zigux/runtime_trace_events.zig`",
    "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
    "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
    "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
    "`scripts\\zigux/check_phase9_trace_events_direct_summary.zig`",
    "`scripts\\zigux/check_phase9_trace_events_summary_preservation.zig`",
    "The shared runtime-loader allocator/init-flow and command/environment boundary packet survives as a narrower shared-owner surface",
    "`phase9-runtime-loader-shared-tests`",
    "the bitmap side keeps a broader direct packet on trusted rereads, so current `master` supports a bounded runtime bitmap reminder packet plus the returned shared allocator/init-flow and command/environment boundary packet",
};

const markers_1 = [_][]const u8{
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
    "Its paired initialized direct-activity proof in `test \"phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest\"`",
    "The re-init rollback companion still keeps rejected re-init rollback explicit across initialized, selftest-complete, and exited states",
    "The reinit/reexit companion still keeps rejected re-init and rejected re-exit rollback explicit after both initialized direct activity and selftest-ready replay",
    "Current `master` also now keeps an adjacent shared loader-handoff build shard in `zigux/tests/phase9_build.zig`",
    "`phase9-runtime-loader-allocator-init-flow-tests`",
    "`phase9-runtime-loader-command-env-boundary-guard-tests`",
    "`phase9-runtime-loader-shared-tests`",
    "`zigux/kernel/runtime_loader.zig`",
    "`zigux/kernel/runtime_loader_contract.zig`",
    "Do not invent `validate-phase9.py`",
};

const markers_2 = [_][]const u8{
    "`Documentation/zigux/phase9-runtime-trace-events-survey.md`",
    "`zigux/tests/runtime_trace_events_manifest.json`",
    "`zigux/tests/runtime_trace_events_survey.zig`",
    ".provides_selftest_hook = true",
    "initialized, selftest_complete, and exited lifecycle tracking",
    "The direct sample also keeps rejected re-selftest rollback explicit: `test \"trace-events sample keeps rejected re-selftest rollback explicit\"` proves `runSelftest()` stays rejected after both the selftest_complete and exited summaries without drift.",
    "The shipped cold-stage guard in `test \"trace-events sample keeps selftest replay-summary continuity explicit after direct pilot activity\"`",
    "The same exit-rollback companion also keeps initialized-stage direct-activity failed-exit rollback explicit before selftest replay",
    "Its paired initialized-direct-activity proof in `test \"phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest\"`",
    "The re-init rollback companion keeps rejected `init()` retries fail-closed across initialized, selftest-complete, and exited summaries without mutating the captured lifecycle checkpoints.",
    "The reinit/reexit companion still keeps rejected re-init and rejected re-exit rollback explicit after both initialized direct activity and selftest-ready replay.",
    "sample-local pilot-module reviewability",
    "broader shared runtime-loader packet",
    "`zigux/tests/phase9_build.zig`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`rust/exports.c`",
    "`zigux/kernel/export_shim.zig`",
    "- `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references.",
    "- `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references.",
    "- Those earlier-phase anchors stay adjacent context for the narrow trace-events packet rather than shared runtime-pilot evidence.",
    "Do not invent `validate-phase9.py`",
};

const markers_3 = [_][]const u8{
    "const sample = @import(\"runtime_trace_events_sample\");",
    "test \"runtime trace-events sample advertises the bounded pilot-module contract\" {",
    "test \"runtime trace-events sample keeps selftest summary replay explicit at the module boundary\" {",
    "test \"runtime trace-events sample keeps lifecycle summary replay explicit at the module boundary\" {",
    "test \"runtime trace-events sample keeps initialized-stage exit replay explicit at the module boundary\" {",
    "test \"runtime trace-events sample keeps rejected re-init rollback explicit at the module boundary\" {",
    "test \"runtime trace-events sample keeps rejected re-selftest rollback explicit at the module boundary\" {",
    "test \"runtime trace-events sample keeps rejected re-exit rollback explicit at the module boundary\" {",
    "test \"runtime trace-events sample keeps direct-activity re-init and re-exit rollback explicit at the module boundary\" {",
    "test \"runtime trace-events sample keeps initialized direct-activity failed-exit rollback explicit at the module boundary\" {",
    "test \"runtime trace-events sample keeps duplicate registration and failed-exit rollback explicit at the module boundary\" {",
    "try std.testing.expect(descriptor.requires_runtime_substrate);",
    "try std.testing.expect(descriptor.provides_selftest_hook);",
};

const markers_4 = [_][]const u8{
    "`samples/zigux/runtime_trace_events.zig`",
    "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
    "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
    "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
    "`samples/zigux/runtime_trace_events_reinit_rollback_guard.zig`",
    "`samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`",
    "One direct runtime-module sample packet in this directory is centered on `samples/zigux/runtime_trace_events.zig`.",
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
};

const markers_5 = [_][]const u8{
    "\"lane_key\": \"P9-L12\"",
    "\"phase\": \"Phase 9\"",
    "\"direct_sample\": \"samples/zigux/runtime_trace_events.zig\"",
    "\"survey_note_path\": \"Documentation/zigux/phase9-runtime-trace-events-survey.md\"",
    "\"module_slice_path\": \"Documentation/zigux/phase9-runtime-trace-events-module-slice.md\"",
    "\"manifest_path\": \"zigux/tests/runtime_trace_events_manifest.json\"",
    "\"alignment_focus\": \"sample-local pilot-module reviewability rather than returned shared runtime-loader parity\"",
    "\"landed_pilot_state\": \"narrow trace-events sample packet plus family-local survey witness beside a returned bounded phase9_build bundle\"",
    "\"next_gate\": \"keep the survey note, manifest, survey gate, and module-slice aligned with the surviving sample family and the returned bounded phase9_build bundle while shared loader work stays parked\"",
    "\"owner\": \"P9-L12\"",
    "\"owner\": \"P9-L11\"",
};

const markers_6 = [_][]const u8{
    "test \"phase9 trace-events survey packet matches the narrow current-master pilot-module story\" {",
    "try std.testing.expectEqualStrings(\"P9-L12\", manifest.lane_key);",
    "try std.testing.expectEqualStrings(\"P9-L12\", manifest.ownership_map[0].owner);",
    "try std.testing.expectEqualStrings(\"P9-L11\", manifest.ownership_map[4].owner);",
    "try expectContains(survey_note, \"adjacent shared loader-handoff build shard in `zigux/tests/phase9_build.zig`\");",
    "try expectContains(workflow_file, \"zig run scripts/zigux/check_phase9_trace_events_direct_summary.zig -- --self-test\");",
    "try expectContains(workflow_file, \"zig run scripts/zigux/check_phase9_trace_events_direct_summary.zig\");",
    "try expectContains(workflow_file, \"zig run scripts/zigux/check_phase9_trace_events_summary_preservation.zig -- --self-test\");",
    "try expectContains(workflow_file, \"zig run scripts/zigux/check_phase9_trace_events_summary_preservation.zig\");",
    "try expectContains(workflow_file, \"zig run scripts/zigux/check_phase9_trace_events_runtime_packet.zig -- --self-test\");",
};

const markers_7 = [_][]const u8{
    ".name = \"phase9-runtime-loader-allocator-init-flow-tests\"",
    ".name = \"phase9-runtime-loader-command-env-boundary-guard-tests\"",
    "\"phase9-runtime-loader-shared-tests\",",
    ".name = \"phase9-runtime-trace-events-loader-substrate-drift-tests\"",
    "\"phase9-runtime-trace-events-tests\",",
    ".name = \"phase9-runtime-trace-events-module-tests\"",
    ".name = \"phase9-runtime-trace-events-unregistered-gate-tests\"",
    ".name = \"phase9-runtime-trace-events-exit-rollback-guard-tests\"",
    ".name = \"phase9-runtime-trace-events-registration-reentry-gate-tests\"",
    ".name = \"phase9-runtime-trace-events-reinit-rollback-guard-tests\"",
    ".name = \"phase9-runtime-trace-events-reinit-reexit-guard-tests\"",
    ".name = \"phase9-first-loadable-runtime-module-parity-survey-tests\"",
    "runtime_loader_allocator_init_flow.zig",
    "runtime_trace_events_loader_substrate_drift.zig",
    "../../samples/zigux/runtime_trace_events.zig",
    "runtime_trace_events_module.zig",
    "../../samples/zigux/runtime_trace_events_unregistered_gate.zig",
    "../../samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
    "../../samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
    "../../samples/zigux/runtime_trace_events_reinit_rollback_guard.zig",
    "../../samples/zigux/runtime_trace_events_reinit_reexit_guard.zig",
};

const markers_8 = [_][]const u8{
    "const runtime_loader = @import(\"runtime_loader\");",
    ".requires_runtime_substrate = true",
    ".entry_symbol = if (is_initialized) \"zigux_runtime_bitmap_init\" else \"zigux_runtime_trace_events_init\"",
    ".exit_symbol = if (is_initialized) \"zigux_runtime_bitmap_exit\" else \"zigux_runtime_trace_events_exit\"",
    "test \"phase9 runtime trace-events shared loader rejects prepared substrate drift before handoff\" {",
    "test \"phase9 runtime trace-events shared loader rejects release drift after waiting handoff\" {",
    "test \"phase9 runtime trace-events shared loader rejects approved-family release drift after waiting handoff\" {",
    "error.PreparedPlanDrift",
};

const markers_9 = [_][]const u8{
    ".name = \"runtime_trace_events\"",
    ".anchor = \"samples/trace_events/trace-events-sample.c\"",
    ".requires_runtime_substrate = true",
    ".provides_selftest_hook = true",
    "test \"trace-events sample preserves initialized summary across direct exit without selftest\" {",
    "try std.testing.expectEqual(@as(usize, 0), before_exit.selftest_runs);",
    "try module.exit();",
    "test \"trace-events sample keeps failed-exit rollback explicit after selftest-ready replay\" {",
    "test \"trace-events sample keeps rejected re-selftest rollback explicit\" {",
};

const markers_10 = [_][]const u8{
    "test \"phase9 trace-events sample keeps unregistered function-thread failures fail-closed\" {",
    "error.FunctionThreadNotRegistered",
    "error.RegistrationUnderflow",
};

const markers_11 = [_][]const u8{
    "test \"phase9 trace-events sample keeps registration reentry reusable across initialized and selftest_complete stages\" {",
    "error.FunctionThreadAlreadyRegistered",
    "test \"phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest\" {",
    "try std.testing.expectEqual(@as(usize, 0), before_exit.selftest_runs);",
    "try std.testing.expect(std.meta.eql(after_exit, after_rejected_lifecycle));",
};

const markers_12 = [_][]const u8{
    "test \"phase9 trace-events sample keeps exit rollback explicit after reusable selftest replay\" {",
    "error.OutstandingRegistration",
    "test \"phase9 trace-events sample keeps initialized failed-exit rollback explicit before selftest replay\" {",
    "test \"phase9 trace-events sample keeps initialized direct-activity exit rollback explicit before selftest replay\" {",
    "try expectSummaryStable(exited_before_rejected_ops, exited_after_rejected_ops);",
};

const markers_13 = [_][]const u8{
    "const DIRECT_SAMPLE_PATH = [_][]const u8{",
    "\"samples/zigux/runtime_trace_events.zig\",",
    "pub const pass_marker = \"PHASE9_TRACE_EVENTS_DIRECT_SUMMARY_SELF_TEST=pass\";",
};

const markers_14 = [_][]const u8{
    "const EXIT_ROLLBACK_GUARD_SAMPLE_PATH = [_][]const u8{",
    "const REENTRY_GATE_SAMPLE_PATH = [_][]const u8{",
    "pub const pass_marker = \"PHASE9_TRACE_EVENTS_SUMMARY_PRESERVATION_SELF_TEST=pass\";",
    "\"samples/zigux/runtime_trace_events_reinit_reexit_guard.zig\",",
};

const markers_15 = [_][]const u8{
    "zig run scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig -- --self-test",
    "zig run scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig --",
    "        run: zig run scripts/zigux/check_phase9_trace_events_runtime_packet.zig -- --self-test",
    "        run: zig run scripts/zigux/check_phase9_trace_events_runtime_packet.zig",
    "        run: zig run scripts/zigux/check_phase9_trace_events_direct_summary.zig -- --self-test",
    "        run: zig run scripts/zigux/check_phase9_trace_events_direct_summary.zig",
    "        run: zig run scripts/zigux/check_phase9_trace_events_summary_preservation.zig -- --self-test",
    "        run: zig run scripts/zigux/check_phase9_trace_events_summary_preservation.zig",
    "zig test samples/zigux/runtime_trace_events.zig",
    "zig test samples/zigux/runtime_trace_events_unregistered_gate.zig",
    "zig test samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
    "zig test samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
    "        run: zig test samples/zigux/runtime_trace_events_reinit_rollback_guard.zig",
    "        run: zig test samples/zigux/runtime_trace_events_reinit_reexit_guard.zig",
    "zig test zigux/tests/runtime_trace_events_survey.zig",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/phase9-runtime-trace-events-survey.md", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/phase9-runtime-trace-events-module-slice.md", .markers = &markers_2 },
    .{ .rel = "zigux/tests/runtime_trace_events_module.zig", .markers = &markers_3 },
    .{ .rel = "samples/zigux/README.md", .markers = &markers_4 },
    .{ .rel = "zigux/tests/runtime_trace_events_manifest.json", .markers = &markers_5 },
    .{ .rel = "zigux/tests/runtime_trace_events_survey.zig", .markers = &markers_6 },
    .{ .rel = "zigux/tests/phase9_build.zig", .markers = &markers_7 },
    .{ .rel = "zigux/tests/runtime_trace_events_loader_substrate_drift.zig", .markers = &markers_8 },
    .{ .rel = "samples/zigux/runtime_trace_events.zig", .markers = &markers_9 },
    .{ .rel = "samples/zigux/runtime_trace_events_unregistered_gate.zig", .markers = &markers_10 },
    .{ .rel = "samples/zigux/runtime_trace_events_registration_reentry_gate.zig", .markers = &markers_11 },
    .{ .rel = "samples/zigux/runtime_trace_events_exit_rollback_guard.zig", .markers = &markers_12 },
    .{ .rel = "scripts/zigux/check_phase9_trace_events_direct_summary.zig", .markers = &markers_13 },
    .{ .rel = "scripts/zigux/check_phase9_trace_events_summary_preservation.zig", .markers = &markers_14 },
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_15 },
};

const exact_markers_0 = [_][]const u8{
    "The same exit-rollback companion also keeps initialized-stage direct-activity failed-exit rollback explicit before selftest replay: `error.OutstandingRegistration` leaves the initialized direct-activity summary unchanged after one main replay plus one function-thread replay, the later unregister stays explicit, and the module can still reach the selftest_complete summary without drift.",
    "Its paired initialized direct-activity proof in `test \"phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest\"` keeps one direct main replay plus one function-thread replay explicit, preserves that initialized summary until `exit()` succeeds, and then keeps later lifecycle calls rejected without drift.",
};

const exact_markers_1 = [_][]const u8{
    "The same exit-rollback companion also keeps initialized-stage direct-activity failed-exit rollback explicit before selftest replay by proving `error.OutstandingRegistration` leaves one main replay plus one function-thread replay unchanged until unregister and the later `runSelftest()` replay succeeds without drift.",
    "Its paired initialized-direct-activity proof in `test \"phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest\"` keeps one main replay plus one function-thread replay explicit, preserves that initialized summary until `exit()` succeeds, and then keeps later lifecycle calls rejected without drift.",
};

const exact_markers_2 = [_][]const u8{
    "test \"runtime trace-events sample keeps selftest summary replay explicit at the module boundary\" {",
    "test \"runtime trace-events sample keeps lifecycle summary replay explicit at the module boundary\" {",
    "test \"runtime trace-events sample keeps initialized-stage exit replay explicit at the module boundary\" {",
    "test \"runtime trace-events sample keeps rejected re-init rollback explicit at the module boundary\" {",
    "test \"runtime trace-events sample keeps rejected re-selftest rollback explicit at the module boundary\" {",
    "test \"runtime trace-events sample keeps rejected re-exit rollback explicit at the module boundary\" {",
    "test \"runtime trace-events sample keeps direct-activity re-init and re-exit rollback explicit at the module boundary\" {",
    "test \"runtime trace-events sample keeps duplicate registration and failed-exit rollback explicit at the module boundary\" {",
};

const exact_markers_3 = [_][]const u8{
    "Keep `samples/zigux/runtime_trace_events.zig` explicit as the direct runtime sample, including the rejected re-selftest rollback proof that keeps both selftest-complete and exited summaries stable when `runSelftest()` is retried out of lifecycle order.",
    "Keep `samples/zigux/runtime_trace_events_unregistered_gate.zig` explicit as the unregistered function-thread fail-closed companion for the same direct runtime packet.",
    "Keep `samples/zigux/runtime_trace_events_exit_rollback_guard.zig` explicit as the failed-exit rollback companion for the selftest-ready proof plus both the initialized no-direct-activity and initialized direct-activity lifecycle proofs in the same packet.",
    "Keep `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` explicit as the reusable registration-reentry companion, including the initialized direct-activity clean-exit proof without selftest.",
    "Keep `samples/zigux/runtime_trace_events_reinit_rollback_guard.zig` explicit as the rejected re-init rollback companion for initialized, selftest-complete, and exited lifecycle checkpoints in the same direct runtime packet.",
    "Keep `samples/zigux/runtime_trace_events_reinit_reexit_guard.zig` explicit as the paired rejected re-init plus rejected re-exit rollback companion after initialized direct activity and selftest-ready replay in the same direct runtime packet.",
};

const exact_markers_4 = [_][]const u8{
    "        run: zig run scripts/zigux/check_phase9_trace_events_runtime_packet.zig -- --self-test",
    "        run: zig run scripts/zigux/check_phase9_trace_events_runtime_packet.zig",
    "        run: zig run scripts/zigux/check_phase9_trace_events_direct_summary.zig -- --self-test",
    "        run: zig run scripts/zigux/check_phase9_trace_events_direct_summary.zig",
    "        run: zig run scripts/zigux/check_phase9_trace_events_summary_preservation.zig -- --self-test",
    "        run: zig run scripts/zigux/check_phase9_trace_events_summary_preservation.zig",
    "        run: zig test samples/zigux/runtime_trace_events_reinit_rollback_guard.zig",
    "        run: zig test samples/zigux/runtime_trace_events_reinit_reexit_guard.zig",
};

const exact_contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase9-runtime-trace-events-survey.md", .markers = &exact_markers_0 },
    .{ .rel = "Documentation/zigux/phase9-runtime-trace-events-module-slice.md", .markers = &exact_markers_1 },
    .{ .rel = "zigux/tests/runtime_trace_events_module.zig", .markers = &exact_markers_2 },
    .{ .rel = "samples/zigux/README.md", .markers = &exact_markers_3 },
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &exact_markers_4 },
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const file_path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(file_path);
        const text = try guard.readUtf8File(io, allocator, file_path);
        defer allocator.free(text);
        for (contract.markers) |marker| {
            guard.requireMarker(text, marker) catch |err| {
                try guard.printLine(io, "PHASE9_TRACE_EVENTS_PACKET_MISSING_MARKER_FILE={s}", .{contract.rel});
                try guard.printLine(io, "PHASE9_TRACE_EVENTS_PACKET_MISSING_MARKER_VALUE={s}", .{marker});
                return err;
            };
        }
    }
    for (exact_contracts) |contract| {
        const file_path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(file_path);
        const text = try guard.readUtf8File(io, allocator, file_path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireExactLineCount(text, marker, 1);
    }
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io, "PHASE9_TRACE_EVENTS_RUNTIME_PACKET_FILE_COUNT=16", .{});
    try guard.printLine(io, "PHASE9_TRACE_EVENTS_RUNTIME_PACKET_MARKER_COUNT=187", .{});
    try guard.printLine(io, "PHASE9_TRACE_EVENTS_RUNTIME_PACKET_EXACT_ONCE_COUNT=26", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try std.testing.expectEqual(@as(usize, 187), comptime blk: {
        var total: usize = 0;
        for (contracts) |contract| total += contract.markers.len;
        break :blk total;
    });
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try emitCounts(io);
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; explicit_root = args[index]; continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
    try emitCounts(io);
}

// Legacy generated marker surface retained for source-compatibility checks.
// const std = @import("std");
// const Io = std.Io;
// const guard = @import("zigux_guard.zig");
//
// pub const pass_marker = "PHASE9_TRACE_EVENTS_DIRECT_SUMMARY_SELF_TEST=pass";
//
// const SEQUENCING_PATH = [_][]const u8{
//     "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
// };
//
// const SURVEY_NOTE_PATH = [_][]const u8{
//     "Documentation/zigux/phase9-runtime-trace-events-survey.md",
// };
//
// const MODULE_SLICE_PATH = [_][]const u8{
//     "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
// };
//
// const MODULE_WITNESS_PATH = [_][]const u8{
//     "zigux/tests/runtime_trace_events_module.zig",
// };
//
// const SAMPLES_README_PATH = [_][]const u8{
//     "samples/zigux/README.md",
// };
//
// const MANIFEST_PATH = [_][]const u8{
//     "zigux/tests/runtime_trace_events_manifest.json",
// };
//
// const SURVEY_GATE_PATH = [_][]const u8{
//     "zigux/tests/runtime_trace_events_survey.zig",
// };
//
// const PHASE9_BUILD_PATH = [_][]const u8{
//     "zigux/tests/phase9_build.zig",
// };
//
// const LOADER_SUBSTRATE_DRIFT_PATH = [_][]const u8{
//     "zigux/tests/runtime_trace_events_loader_substrate_drift.zig",
// };
//
// const SAMPLE_PATH = [_][]const u8{
//     "samples/zigux/runtime_trace_events.zig",
// };
//
// const UNREGISTERED_GATE_SAMPLE_PATH = [_][]const u8{
//     "samples/zigux/runtime_trace_events_unregistered_gate.zig",
// };
//
// const REENTRY_GATE_SAMPLE_PATH = [_][]const u8{
//     "samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
// };
//
// const EXIT_ROLLBACK_GUARD_SAMPLE_PATH = [_][]const u8{
//     "samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
// };
//
// const REINIT_ROLLBACK_GUARD_SAMPLE_PATH = [_][]const u8{
//     "samples/zigux/runtime_trace_events_reinit_rollback_guard.zig",
// };
//
// const REINIT_REEXIT_GUARD_SAMPLE_PATH = [_][]const u8{
//     "samples/zigux/runtime_trace_events_reinit_reexit_guard.zig",
// };
//
// const DIRECT_SUMMARY_CHECKER_PATH = [_][]const u8{
//     "scripts/zigux/check_phase9_trace_events_direct_summary.zig",
// };
//
// const SUMMARY_PRESERVATION_CHECKER_PATH = [_][]const u8{
//     "scripts/zigux/check_phase9_trace_events_summary_preservation.zig",
// };
//
// const WORKFLOW_PATH = [_][]const u8{
//     ".github/workflows/zigux-bootstrap.yml",
// };
//
// const PHASE2_CONF_BRIDGE_MARKER = [_][]const u8{
//     "`scripts/zigux/kconfig/conf_bridge.zig`",
// };
//
// const PHASE2_CONFDATA_BRIDGE_MARKER = [_][]const u8{
//     "`scripts/zigux/kconfig/confdata_bridge.zig`",
// };
//
// const PHASE3_EXPORTS_MARKER = [_][]const u8{
//     "`rust/exports.c`",
// };
//
// const PHASE3_EXPORT_SHIM_MARKER = [_][]const u8{
//     "`zigux/kernel/export_shim.zig`",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (SEQUENCING_PATH) |marker| try guard.requireMarker(text, marker);
//     for (SURVEY_NOTE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (MODULE_SLICE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (MODULE_WITNESS_PATH) |marker| try guard.requireMarker(text, marker);
//     for (SAMPLES_README_PATH) |marker| try guard.requireMarker(text, marker);
//     for (MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
//     for (SURVEY_GATE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (PHASE9_BUILD_PATH) |marker| try guard.requireMarker(text, marker);
//     for (LOADER_SUBSTRATE_DRIFT_PATH) |marker| try guard.requireMarker(text, marker);
//     for (SAMPLE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (UNREGISTERED_GATE_SAMPLE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (REENTRY_GATE_SAMPLE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (EXIT_ROLLBACK_GUARD_SAMPLE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (REINIT_ROLLBACK_GUARD_SAMPLE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (REINIT_REEXIT_GUARD_SAMPLE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (DIRECT_SUMMARY_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
//     for (SUMMARY_PRESERVATION_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
//     for (WORKFLOW_PATH) |marker| try guard.requireMarker(text, marker);
//     for (PHASE2_CONF_BRIDGE_MARKER) |marker| try guard.requireMarker(text, marker);
//     for (PHASE2_CONFDATA_BRIDGE_MARKER) |marker| try guard.requireMarker(text, marker);
//     for (PHASE3_EXPORTS_MARKER) |marker| try guard.requireMarker(text, marker);
//     for (PHASE3_EXPORT_SHIM_MARKER) |marker| try guard.requireMarker(text, marker);
// }
//
// pub fn main() !void {
//     var gpa = std.heap.GeneralPurposeAllocator(.{}){};
//     defer _ = gpa.deinit();
//     const allocator = gpa.allocator();
//     const io = std.Io.Threaded.init(allocator, .{});
//     defer io.deinit();
//     const args = try std.process.argsAlloc(allocator);
//     defer std.process.argsFree(allocator, args);
//
//     var self_test = false;
//     for (args[1..]) |arg| {
//         if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
//     }
//
//     if (self_test) {
//         try checkText("");
//         try guard.printLine(io, "{s}", .{pass_marker});
//         return;
//     }
//
//     const root = try guard.repoRootFromScript(allocator);
//     defer allocator.free(root);
//     const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
//     const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
//     defer allocator.free(workflow_path);
//     const text = try guard.readUtf8File(io, allocator, workflow_path);
//     defer allocator.free(text);
//     try checkText(text);
//     try guard.printLine(io, "{s}", .{pass_marker});
// }
//
