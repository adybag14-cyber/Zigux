const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_LANE_SEQUENCING_FREEZE_BOUNDARY_SELF_TEST=pass";

const EXPECTED_STUDY_ONLY_ANCHORS = [_][]const u8{
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
};

const FREEZE_MAP_REQUIRED_MARKERS = [_][]const u8{
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "shared Phase 9 runtime-pilot freeze-boundary packet must keep",
    "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig`",
    "`scripts/zigux/check_phase9_trace_events_runtime_packet.zig`",
    "`scripts/zigux/check_phase9_freeze_map_study_boundaries.zig`",
};

const STUDY_ONLY_ACCOUNTING_REQUIRED_MARKERS = [_][]const u8{
    "PHASE15_STATUS=study_only_accounting_slice_landed",
    "current-master-readback-2026-05-25",
    "boundary-study target first, not a rewrite target",
    "this note is an inventory and handoff surface, not an approval record",
    "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
    "any future status-bucket change for either anchor must update the freeze map",
};

const LANE_SEQUENCING_REQUIRED_MARKERS = [_][]const u8{
    "Trusted mixed rereads on 2026-05-25 confirm four distinct current-master Phase 9 postures.",
    "the returned shared runtime-loader allocator/init-flow and command/environment boundary packet stay neighboring shared-owner evidence",
    "the bitmap side keeps a broader direct packet on trusted rereads",
    "the kretprobe side now keeps a returned family-local pilot packet on trusted rereads",
    "keep the freeze-map study-only anchors explicit through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "Treat stale shared-owner undercount or overclaim as the active blocker before reopening checker-local or runtime-behavior work.",
    "do not treat `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-pilot expansion evidence",
};

const CURRENT_PHASE9_MAKE_ROUTES = [_][]const u8{
    "phase9-runtime-atomic64-test",
    "phase9-runtime-bitmap-test",
    "phase9-runtime-loader-shared-test",
    "phase9-runtime-loader-command-env-boundary-guard-test",
    "phase9-runtime-trace-events-test",
    "phase9-runtime-kretprobe-test",
    "phase9-first-loadable-runtime-module-parity-test",
    "phase9-test",
};

const FORBIDDEN_PHASE9_MAKE_ROUTES = [_][]const u8{
    "phase9",
    "phase9-validate",
    "phase9-runtime-trace-events-sample-tests",
};

const FREEZE_MAP_PATH = [_][]const u8{
    "Documentation/zigux/freeze-map.md",
};

const STUDY_ONLY_ACCOUNTING_PATH = [_][]const u8{
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
};

const LANE_SEQUENCING_PATH = [_][]const u8{
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
};

const MAKEFILE_PATH = [_][]const u8{
    "zigux/Makefile",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (EXPECTED_STUDY_ONLY_ANCHORS) |marker| try guard.requireMarker(text, marker);
    for (FREEZE_MAP_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (STUDY_ONLY_ACCOUNTING_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (LANE_SEQUENCING_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (CURRENT_PHASE9_MAKE_ROUTES) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_PHASE9_MAKE_ROUTES) |marker| try guard.requireMarker(text, marker);
    for (FREEZE_MAP_PATH) |marker| try guard.requireMarker(text, marker);
    for (STUDY_ONLY_ACCOUNTING_PATH) |marker| try guard.requireMarker(text, marker);
    for (LANE_SEQUENCING_PATH) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_PATH) |marker| try guard.requireMarker(text, marker);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    const io = std.Io.Threaded.init(allocator, .{});
    defer io.deinit();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }

    if (self_test) {
        try checkText("");
        try guard.printLine(io, "{s}", .{pass_marker});
        return;
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
    const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
    defer allocator.free(workflow_path);
    const text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(text);
    try checkText(text);
    try guard.printLine(io, "{s}", .{pass_marker});
}
