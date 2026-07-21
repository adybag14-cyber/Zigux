const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE9_FREEZE_MAP_STUDY_BOUNDARIES=pass";
pub const self_test_pass_marker = "PHASE9_FREEZE_MAP_STUDY_BOUNDARIES_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const roadmap_study_only_anchors = [_][]const u8{
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
};

const markers_0 = [_][]const u8{
    "# Zigux Freeze Map",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
    "`Documentation/zigux/README.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/README.md`",
    "`samples/zigux/README.md`",
    "`zigux/tests/README.md`",
    "`scripts\\zigux/check_phase9_review_checklist_phase_boundaries.zig`",
    "`scripts\\zigux/check_phase9_trace_events_runtime_packet.zig`",
    "`scripts\\zigux/check_phase9_freeze_map_study_boundaries.zig`",
    "`samples/zigux/runtime_trace_events.zig`",
    "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
    "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
    "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
    "`samples/zigux/runtime_trace_events_reinit_rollback_guard.zig`",
    "`samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`",
    "`Documentation/zigux/phase9-runtime-loader-gap-survey.md`",
    "`zigux/tests/runtime_loader_gap_manifest.json`",
    "`zigux/tests/runtime_loader_gap_survey.zig`",
    "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
    "`zigux/tests/phase9_build.zig`",
    "`zigux/kernel/runtime_loader.zig`",
    "`zigux/kernel/runtime_loader_contract.zig`",
    "`zigux/kernel/runtime_loader_command_env_boundary_guard.zig`",
    "`samples/zigux/runtime_bitmap_loader.zig`",
    "`samples/zigux/runtime_trace_events_loader.zig`",
    "`zigux/Makefile` explicit only as a readable non-owner surface whose live body now exposes bounded `phase9-runtime-atomic64-test`, `phase9-runtime-bitmap-test`, `phase9-runtime-loader-shared-test`, `phase9-runtime-loader-command-env-boundary-guard-test`, `phase9-runtime-trace-events-test`, `phase9-runtime-kretprobe-test`, and `phase9-test` routes",
};

const markers_1 = [_][]const u8{
    "# Phase 15 Study-Only Anchor Accounting",
    "PHASE15_STATUS=study_only_accounting_slice_landed",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "`study_only`",
    "tracked outside the freeze-in-C scorecard",
    "this note is an inventory and handoff surface, not an approval record",
    "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
    "the freeze-map governance note, the parity scorecard, the handoff-next-steps survey, and the shared-summary gap note",
    "boundary-study target first, not a rewrite target",
    "remain future-only and not current product claims",
    "no Architecture Council approval is currently recorded for a deep-core status change",
    "a direct Zigux bridge for `kernel/workqueue.c`",
    "a direct Zigux bridge for `kernel/trace/ring_buffer.c`",
    "any future status-bucket change for either anchor must update the freeze map, the Phase 15 governance note, the parity scorecard, and this study-only accounting note together",
};

const markers_2 = [_][]const u8{
    "if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence?",
};

const markers_3 = [_][]const u8{
    "Phase 9 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md` - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` - `Documentation/zigux/review-checklist.md` - `Documentation/zigux/README.md` - `scripts/zigux/README.md` - `samples/zigux/README.md` - `zigux/tests/README.md` - `scripts\\zigux/check_phase9_review_checklist_phase_boundaries.zig` - `scripts\\zigux/check_phase9_trace_events_runtime_packet.zig` - `scripts\\zigux/check_phase9_freeze_map_study_boundaries.zig` keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.",
    "keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues, and any shared reminder surface that summarizes them must route back through those two owner notes.",
    "keep the narrow trace-events packet distinct too: `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` remain the current shipped runtime-pilot proof, while the study-only anchors stay non-owner governance context only.",
    "keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata surfaces are complete.",
};

const markers_4 = [_][]const u8{
    "keep the freeze-map study-only anchors explicit through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain cautionary non-owner context rather than proof of runtime-substrate or bridge readiness",
};

const markers_5 = [_][]const u8{
    "scripts\\zigux/validate_phase9.zig",
    "zig run scripts/zigux/validate_phase9.zig -- --self-test",
    "zig run scripts/zigux/validate_phase9.zig --",
    "keep the freeze-map boundary explicit too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues",
};

const markers_6 = [_][]const u8{
    "Keep `samples/zigux/runtime_trace_events_reinit_rollback_guard.zig` explicit as the rejected re-init rollback companion for initialized, selftest-complete, and exited lifecycle checkpoints in the same direct runtime packet.",
    "Keep `samples/zigux/runtime_trace_events_reinit_reexit_guard.zig` explicit as the paired rejected re-init plus rejected re-exit rollback companion after initialized direct activity and selftest-ready replay in the same direct runtime packet.",
    "Current `master` also keeps a narrower returned runtime kretprobe sample-side packet explicit through `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`, `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, `zigux/tests/runtime_first_loadable_parity_behavior.zig`, and the dedicated `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-loader-tests`, `phase9-runtime-kretprobe-initialized-snapshot-guard-tests`, `phase9-runtime-kretprobe-registration-reentry-gate-tests`, `phase9-runtime-kretprobe-survey-tests`, `phase9-runtime-kretprobe-module-tests`, `phase9-runtime-kretprobe-tests`, and `phase9-first-loadable-runtime-module-parity-behavior-tests` routes in `zigux/tests/phase9_build.zig`.",
    "Keep `samples/zigux/runtime_bitmap_direct_init_contract.zig` explicit as the returned direct-init normalization companion proof for the same runtime bitmap starter, covering unsorted duplicate input collapse, nth-set ordering, formatted sparse-summary stability, and lifecycle-summary stability through selftest and exit.",
    "Keep that bitmap packet framed as a separate Phase 9 runtime reminder rather than as proof that the broader shared runtime-loader packet returned or as evidence that a fifth approved Phase 5 sample family landed here.",
};

const markers_7 = [_][]const u8{
    "  * Keep the current bounded Phase 9 reminder packet explicit through `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `scripts\\zigux/check_phase9_review_checklist_phase_boundaries.zig`, `scripts\\zigux/check_phase9_trace_events_runtime_packet.zig`, and `scripts\\zigux/check_phase9_freeze_map_study_boundaries.zig`.",
    "keep the narrow trace-events packet distinct too: `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`, `samples/zigux/runtime_trace_events_reinit_rollback_guard.zig`, `samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` remain the current shipped runtime-pilot proof rather than a claim that broader runtime-loader or publication boundaries are solved",
    "keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-shared-tests`, and `phase9-runtime-loader-command-env-boundary-guard-tests` routes, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata surfaces are complete",
    "keep the returned runtime kretprobe pilot packet distinct from those shared loader and bitmap reminders too: `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`, `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_first_loadable_parity_behavior.zig`, and the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-loader-tests`, `phase9-runtime-kretprobe-initialized-snapshot-guard-tests`, `phase9-runtime-kretprobe-registration-reentry-gate-tests`, `phase9-runtime-kretprobe-survey-tests`, `phase9-runtime-kretprobe-module-tests`, `phase9-runtime-kretprobe-tests`, and `phase9-first-loadable-runtime-module-parity-behavior-tests` routes are current family-local pilot evidence, but they still must not be used to imply that the broader shared runtime-loader packet, blocked publication boundaries, or install-root surfaces are complete",
    "without implying any Architecture Council approval for a freeze-map status change",
};

const markers_8 = [_][]const u8{
    "zig run scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig -- --self-test",
    "zig run scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig --",
    "zig run scripts/zigux/check_phase9_freeze_map_study_boundaries.zig -- --self-test",
    "zig run scripts/zigux/check_phase9_freeze_map_study_boundaries.zig --",
    "zig run scripts/zigux/check_phase9_trace_events_runtime_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase9_trace_events_runtime_packet.zig --",
    "zig build phase9-runtime-loader-command-env-boundary-guard-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig",
    "zig test samples/zigux/runtime_trace_events.zig",
    "zig test zigux/tests/runtime_trace_events_survey.zig",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/freeze-map.md", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/phase15-study-only-anchor-accounting.md", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/review-checklist.md", .markers = &markers_2 },
    .{ .rel = "Documentation/zigux/README.md", .markers = &markers_3 },
    .{ .rel = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md", .markers = &markers_4 },
    .{ .rel = "scripts/zigux/README.md", .markers = &markers_5 },
    .{ .rel = "samples/zigux/README.md", .markers = &markers_6 },
    .{ .rel = "zigux/tests/README.md", .markers = &markers_7 },
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_8 },
};

const forbidden_markers_0 = [_][]const u8{
    "there is still no dedicated shared `validate-phase9.py` rerun path",
};

const forbidden_contracts = [_]FileContract{
    .{ .rel = "scripts/zigux/README.md", .markers = &forbidden_markers_0 },
};

const required_routes = [_][]const u8{
    "phase9-runtime-atomic64-test",
    "phase9-runtime-bitmap-test",
    "phase9-runtime-loader-shared-test",
    "phase9-runtime-loader-command-env-boundary-guard-test",
    "phase9-runtime-trace-events-test",
    "phase9-runtime-kretprobe-test",
    "phase9-first-loadable-runtime-module-parity-test",
    "phase9-test",
};

const forbidden_routes = [_][]const u8{
    "phase9",
    "phase9-validate",
    "phase9-runtime-trace-events-sample-tests",
};

fn lineDefinesTarget(line_raw: []const u8, route: []const u8) bool {
    const line = std.mem.trimEnd(u8, line_raw, "\r");
    if (line.len == 0 or line[0] == ' ' or line[0] == '\t' or line[0] == '#') return false;
    const colon = std.mem.indexOfScalar(u8, line, ':') orelse return false;
    if (std.mem.eql(u8, std.mem.trim(u8, line[0..colon], " \t"), ".PHONY")) return false;
    var targets = std.mem.tokenizeAny(u8, line[0..colon], " \t");
    while (targets.next()) |target| if (std.mem.eql(u8, target, route)) return true;
    return false;
}

fn makefileHasTarget(text: []const u8, route: []const u8) bool {
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| if (lineDefinesTarget(line, route)) return true;
    return false;
}

fn expectMakefileRoutes(text: []const u8) !void {
    for (required_routes) |route| try std.testing.expect(makefileHasTarget(text, route));
    for (forbidden_routes) |route| try std.testing.expect(!makefileHasTarget(text, route));
}

fn sectionSlice(text: []const u8, heading: []const u8) ![]const u8 {
    const start = std.mem.indexOf(u8, text, heading) orelse return error.MissingAnchorSection;
    const after_heading = start + heading.len;
    const end = std.mem.indexOfPos(u8, text, after_heading, "\n## ") orelse text.len;
    return text[after_heading..end];
}

fn expectSectionAnchorInventory(
    text: []const u8,
    heading: []const u8,
    prefix: []const u8,
    suffix: []const u8,
) !void {
    const section = try sectionSlice(text, heading);
    var index: usize = 0;
    var lines = std.mem.splitScalar(u8, section, '\n');
    while (lines.next()) |raw_line| {
        const line = std.mem.trim(u8, raw_line, " \t\r");
        if (!std.mem.startsWith(u8, line, prefix) or !std.mem.endsWith(u8, line, suffix)) continue;
        if (line.len < prefix.len + suffix.len) return error.InvalidAnchorLine;
        if (index >= roadmap_study_only_anchors.len) return error.TooManyStudyOnlyAnchors;
        const anchor = line[prefix.len .. line.len - suffix.len];
        try std.testing.expectEqualStrings(roadmap_study_only_anchors[index], anchor);
        index += 1;
    }
    try std.testing.expectEqual(roadmap_study_only_anchors.len, index);
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const file_path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(file_path);
        const text = try guard.readUtf8File(io, allocator, file_path);
        defer allocator.free(text);
        for (contract.markers) |marker| {
            guard.requireMarker(text, marker) catch |err| {
                try guard.printLine(io, "PHASE9_FREEZE_MAP_MISSING_MARKER_FILE={s}", .{contract.rel});
                try guard.printLine(io, "PHASE9_FREEZE_MAP_MISSING_MARKER_VALUE={s}", .{marker});
                return err;
            };
        }
    }
    for (forbidden_contracts) |contract| {
        const file_path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(file_path);
        const text = try guard.readUtf8File(io, allocator, file_path);
        defer allocator.free(text);
        for (contract.markers) |marker| try std.testing.expect(std.mem.indexOf(u8, text, marker) == null);
    }
    const freeze_path = try guard.joinPath(allocator, root, "Documentation/zigux/freeze-map.md");
    defer allocator.free(freeze_path);
    const freeze_text = try guard.readUtf8File(io, allocator, freeze_path);
    defer allocator.free(freeze_text);
    try expectSectionAnchorInventory(freeze_text, "## Study / Boundary Only", "- `", "`");
    const accounting_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    defer allocator.free(accounting_path);
    const accounting_text = try guard.readUtf8File(io, allocator, accounting_path);
    defer allocator.free(accounting_text);
    try expectSectionAnchorInventory(accounting_text, "## Study-Only Anchor Inventory", "### `", "`");
    const makefile_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(makefile_path);
    const makefile = try guard.readUtf8File(io, allocator, makefile_path);
    defer allocator.free(makefile);
    try expectMakefileRoutes(makefile);
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io, "PHASE9_ROADMAP_STUDY_ONLY_ANCHOR_COUNT=2", .{});
    try guard.printLine(io, "PHASE9_REQUIRED_PATH_COUNT=10", .{});
    try guard.printLine(io, "PHASE9_FORBIDDEN_PATH_MARKER_COUNT=1", .{});
    try guard.printLine(io, "PHASE9_REQUIRED_MAKE_ROUTE_COUNT=8", .{});
    try guard.printLine(io, "PHASE9_FORBIDDEN_MAKE_ROUTE_COUNT=3", .{});
    try guard.printLine(io, "PHASE9_SAMPLES_README_MARKER_COUNT=5", .{});
    try guard.printLine(io, "PHASE9_TESTS_README_MARKER_COUNT=5", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try std.testing.expectEqual(@as(usize, 76), comptime blk: {
        var total: usize = 0;
        for (contracts) |contract| total += contract.markers.len;
        break :blk total;
    });
    const synthetic_freeze = "## Study / Boundary Only\n- `kernel/workqueue.c`\n- `kernel/trace/ring_buffer.c`\n\n## Next";
    try expectSectionAnchorInventory(synthetic_freeze, "## Study / Boundary Only", "- `", "`");
    const synthetic_accounting = "## Study-Only Anchor Inventory\n### `kernel/workqueue.c`\n### `kernel/trace/ring_buffer.c`\n\n## Next";
    try expectSectionAnchorInventory(synthetic_accounting, "## Study-Only Anchor Inventory", "### `", "`");
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
// pub const pass_marker = "PHASE9_FREEZE_MAP_STUDY_BOUNDARIES_SELF_TEST=pass";
//
// const ROADMAP_STUDY_ONLY_ANCHORS = [_][]const u8{
//     "kernel/workqueue.c",
//     "kernel/trace/ring_buffer.c",
// };
//
// const PHASE9_SHARED_VALIDATOR_MARKERS = [_][]const u8{
//     "scripts\zigux/validate_phase9.zig",
//     "zig run scripts/zigux/validate_phase9.zig -- --self-test",
//     "zig run scripts/zigux/validate_phase9.zig",
// };
//
// const STALE_PHASE9_VALIDATOR_DENIAL = [_][]const u8{
//     "there is still no dedicated shared `validate-phase9.py` rerun path",
// };
//
// const CURRENT_PHASE9_MAKE_ROUTES = [_][]const u8{
//     "phase9-runtime-atomic64-test",
//     "phase9-runtime-bitmap-test",
//     "phase9-runtime-loader-shared-test",
//     "phase9-runtime-loader-command-env-boundary-guard-test",
//     "phase9-runtime-trace-events-test",
//     "phase9-runtime-kretprobe-test",
//     "phase9-first-loadable-runtime-module-parity-test",
//     "phase9-test",
// };
//
// const FORBIDDEN_PHASE9_MAKE_ROUTES = [_][]const u8{
//     "phase9",
//     "phase9-validate",
//     "phase9-runtime-trace-events-sample-tests",
// };
//
// const PATH_REQUIREMENTS = [_][]const u8{
//     "# Zigux Freeze Map",
//     "`kernel/workqueue.c`",
//     "`kernel/trace/ring_buffer.c`",
//     "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
//     "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
//     "`Documentation/zigux/README.md`",
//     "`Documentation/zigux/review-checklist.md`",
//     "`scripts/zigux/README.md`",
//     "`samples/zigux/README.md`",
//     "`zigux/tests/README.md`",
//     "`scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig`",
//     "`scripts/zigux/check_phase9_trace_events_runtime_packet.zig`",
//     "`scripts/zigux/check_phase9_freeze_map_study_boundaries.zig`",
//     "`samples/zigux/runtime_trace_events.zig`",
//     "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
//     "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
//     "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
//     "`samples/zigux/runtime_trace_events_reinit_rollback_guard.zig`",
//     "`samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`",
//     "`Documentation/zigux/phase9-runtime-loader-gap-survey.md`",
//     "`zigux/tests/runtime_loader_gap_manifest.json`",
//     "`zigux/tests/runtime_loader_gap_survey.zig`",
//     "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
//     "`zigux/tests/phase9_build.zig`",
//     "`zigux/kernel/runtime_loader.zig`",
//     "`zigux/kernel/runtime_loader_contract.zig`",
//     "`zigux/kernel/runtime_loader_command_env_boundary_guard.zig`",
//     "`samples/zigux/runtime_bitmap_loader.zig`",
//     "`samples/zigux/runtime_trace_events_loader.zig`",
//     "`zigux/Makefile` explicit only as a readable non-owner surface whose live body now exposes bounded `phase9-runtime-atomic64-test`, `phase9-runtime-bitmap-test`, `phase9-runtime-loader-shared-test`, `phase9-runtime-loader-command-env-boundary-guard-test`, `phase9-runtime-trace-events-test`, `phase9-runtime-kretprobe-test`, and `phase9-test` routes",
//     "# Phase 15 Study-Only Anchor Accounting",
//     "PHASE15_STATUS=study_only_accounting_slice_landed",
//     "PHASE15_PROVENANCE_MODE=dated_master_readback",
//     "`kernel/workqueue.c`",
//     "`kernel/trace/ring_buffer.c`",
//     "`study_only`",
//     "tracked outside the freeze-in-C scorecard",
//     "this note is an inventory and handoff surface, not an approval record",
//     "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
//     "the freeze-map governance note, the parity scorecard, the handoff-next-steps survey, and the shared-summary gap note",
//     "boundary-study target first, not a rewrite target",
//     "remain future-only and not current product claims",
//     "no Architecture Council approval is currently recorded for a deep-core status change",
//     "a direct Zigux bridge for `kernel/workqueue.c`",
//     "a direct Zigux bridge for `kernel/trace/ring_buffer.c`",
//     "any future status-bucket change for either anchor must update the freeze map, the Phase 15 governance note, the parity scorecard, and this study-only accounting note together",
//     "if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence?",
//     "Phase 9 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md` - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` - `Documentation/zigux/review-checklist.md` - `Documentation/zigux/README.md` - `scripts/zigux/README.md` - `samples/zigux/README.md` - `zigux/tests/README.md` - `scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig` - `scripts/zigux/check_phase9_trace_events_runtime_packet.zig` - `scripts/zigux/check_phase9_freeze_map_study_boundaries.zig` keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.",
//     "keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues, and any shared reminder surface that summarizes them must route back through those two owner notes.",
//     "keep the narrow trace-events packet distinct too: `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` remain the current shipped runtime-pilot proof, while the study-only anchors stay non-owner governance context only.",
//     "keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata surfaces are complete.",
//     "keep the freeze-map study-only anchors explicit through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain cautionary non-owner context rather than proof of runtime-substrate or bridge readiness",
//     "keep the freeze-map boundary explicit too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues",
//     "Keep `samples/zigux/runtime_trace_events_reinit_rollback_guard.zig` explicit as the rejected re-init rollback companion for initialized, selftest-complete, and exited lifecycle checkpoints in the same direct runtime packet.",
//     "Keep `samples/zigux/runtime_trace_events_reinit_reexit_guard.zig` explicit as the paired rejected re-init plus rejected re-exit rollback companion after initialized direct activity and selftest-ready replay in the same direct runtime packet.",
//     "Current `master` also keeps a narrower returned runtime kretprobe sample-side packet explicit through `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`, `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, `zigux/tests/runtime_first_loadable_parity_behavior.zig`, and the dedicated `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-loader-tests`, `phase9-runtime-kretprobe-initialized-snapshot-guard-tests`, `phase9-runtime-kretprobe-registration-reentry-gate-tests`, `phase9-runtime-kretprobe-survey-tests`, `phase9-runtime-kretprobe-module-tests`, `phase9-runtime-kretprobe-tests`, and `phase9-first-loadable-runtime-module-parity-behavior-tests` routes in `zigux/tests/phase9_build.zig`.",
//     "Keep `samples/zigux/runtime_bitmap_direct_init_contract.zig` explicit as the returned direct-init normalization companion proof for the same runtime bitmap starter, covering unsorted duplicate input collapse, nth-set ordering, formatted sparse-summary stability, and lifecycle-summary stability through selftest and exit.",
//     "Keep that bitmap packet framed as a separate Phase 9 runtime reminder rather than as proof that the broader shared runtime-loader packet returned or as evidence that a fifth approved Phase 5 sample family landed here.",
//     "Keep the current bounded Phase 9 reminder packet explicit through `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig`, `scripts/zigux/check_phase9_trace_events_runtime_packet.zig`, and `scripts/zigux/check_phase9_freeze_map_study_boundaries.zig`.",
//     "keep the narrow trace-events packet distinct too: `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`, `samples/zigux/runtime_trace_events_reinit_rollback_guard.zig`, `samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` remain the current shipped runtime-pilot proof rather than a claim that broader runtime-loader or publication boundaries are solved",
//     "keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-shared-tests`, and `phase9-runtime-loader-command-env-boundary-guard-tests` routes, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata surfaces are complete",
//     "keep the returned runtime kretprobe pilot packet distinct from those shared loader and bitmap reminders too: `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`, `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_first_loadable_parity_behavior.zig`, and the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-loader-tests`, `phase9-runtime-kretprobe-initialized-snapshot-guard-tests`, `phase9-runtime-kretprobe-registration-reentry-gate-tests`, `phase9-runtime-kretprobe-survey-tests`, `phase9-runtime-kretprobe-module-tests`, `phase9-runtime-kretprobe-tests`, and `phase9-first-loadable-runtime-module-parity-behavior-tests` routes are current family-local pilot evidence, but they still must not be used to imply that the broader shared runtime-loader packet, blocked publication boundaries, or install-root surfaces are complete",
//     "without implying any Architecture Council approval for a freeze-map status change",
//     "zig run scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig -- --self-test",
//     "zig run scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig --",
//     "zig run scripts/zigux/check_phase9_freeze_map_study_boundaries.zig -- --self-test",
//     "zig run scripts/zigux/check_phase9_freeze_map_study_boundaries.zig --",
//     "zig run scripts/zigux/check_phase9_trace_events_runtime_packet.zig -- --self-test",
//     "zig run scripts/zigux/check_phase9_trace_events_runtime_packet.zig --",
//     "zig build phase9-runtime-loader-command-env-boundary-guard-tests --build-file zigux/tests/phase9_build.zig",
//     "zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig",
//     "zig test samples/zigux/runtime_trace_events.zig",
//     "zig test zigux/tests/runtime_trace_events_survey.zig",
// };
//
// const FREEZE_MAP_PATH = [_][]const u8{
//     "Documentation/zigux/freeze-map.md",
// };
//
// const STUDY_ONLY_ACCOUNTING_PATH = [_][]const u8{
//     "Documentation/zigux/phase15-study-only-anchor-accounting.md",
// };
//
// const REVIEW_CHECKLIST_PATH = [_][]const u8{
//     "Documentation/zigux/review-checklist.md",
// };
//
// const DOCS_README_PATH = [_][]const u8{
//     "Documentation/zigux/README.md",
// };
//
// const LANE_SEQUENCING_PATH = [_][]const u8{
//     "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
// };
//
// const SCRIPTS_README_PATH = [_][]const u8{
//     "scripts/zigux/README.md",
// };
//
// const SAMPLES_README_PATH = [_][]const u8{
//     "samples/zigux/README.md",
// };
//
// const TESTS_README_PATH = [_][]const u8{
//     "zigux/tests/README.md",
// };
//
// const MAKEFILE_PATH = [_][]const u8{
//     "zigux/Makefile",
// };
//
// const WORKFLOW_PATH = [_][]const u8{
//     ".github/workflows/zigux-bootstrap.yml",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (ROADMAP_STUDY_ONLY_ANCHORS) |marker| try guard.requireMarker(text, marker);
//     for (PHASE9_SHARED_VALIDATOR_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (STALE_PHASE9_VALIDATOR_DENIAL) |marker| try guard.requireMarker(text, marker);
//     for (CURRENT_PHASE9_MAKE_ROUTES) |marker| try guard.requireMarker(text, marker);
//     for (FORBIDDEN_PHASE9_MAKE_ROUTES) |marker| try guard.requireMarker(text, marker);
//     for (PATH_REQUIREMENTS) |marker| try guard.requireMarker(text, marker);
//     for (FREEZE_MAP_PATH) |marker| try guard.requireMarker(text, marker);
//     for (STUDY_ONLY_ACCOUNTING_PATH) |marker| try guard.requireMarker(text, marker);
//     for (REVIEW_CHECKLIST_PATH) |marker| try guard.requireMarker(text, marker);
//     for (DOCS_README_PATH) |marker| try guard.requireMarker(text, marker);
//     for (LANE_SEQUENCING_PATH) |marker| try guard.requireMarker(text, marker);
//     for (SCRIPTS_README_PATH) |marker| try guard.requireMarker(text, marker);
//     for (SAMPLES_README_PATH) |marker| try guard.requireMarker(text, marker);
//     for (TESTS_README_PATH) |marker| try guard.requireMarker(text, marker);
//     for (MAKEFILE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (WORKFLOW_PATH) |marker| try guard.requireMarker(text, marker);
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
