const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_COMPILE_SHARD_MATRIX_SELF_TEST=pass";

const EXPECTED_SMOKE_COMMANDS = [_][]const u8{
    "make -C zigux phase14-validate",
};

const EXPECTED_SMOKE_SHARD_COMMANDS = [_][]const u8{
    "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig",
};

const EXPECTED_ANCHOR_ROWS = [_][]const u8{
    "kernel/workqueue.cP14-L04phase14-workqueue-bridge-testsphase14-workqueue-reviewability-tests",
    "kernel/trace/ring_buffer.cP14-L08phase14-ring-buffer-survey-tests",
    "net/core/skbuff.cP14-L11phase14-skbuff-bridge-tests",
    "kernel/rcu/tree.cP14-L16phase14-rcu-tree-survey-tests",
};

const EXPECTED_COMPILE_SHARDS = [_][]const u8{
    "phase14-workqueue-bridge-testsphase14_workqueue_bridge.zigfull_bundle_only",
    "phase14-workqueue-reviewability-testsphase14_workqueue_reviewability.zigfull_bundle_only",
    "phase14-skbuff-bridge-testsphase14_skbuff_bridge.zigfull_bundle_only",
    "phase14-ring-buffer-survey-testsphase14_ring_buffer_survey.zigfull_bundle_only",
    "phase14-rcu-tree-survey-testsphase14_rcu_tree_survey.zigfull_bundle_only",
    "phase14-end-to-end-smoke-testsphase14_end_to_end_smoke_survey.zigfocused_and_full_bundle",
};

const EXPECTED_BUILD_MARKERS = [_][]const u8{
    "b.step(\"phase14-smoke\", \"Run the focused Phase 14 smoke shard\")",
    "b.step(\"test\", \"Run the full Phase 14 bounded bridge and survey bundle\")",
    "b.path(\"phase14_end_to_end_smoke_survey.zig\")",
    "b.path(\"phase14_ring_buffer_survey.zig\")",
    "b.path(\"phase14_rcu_tree_survey.zig\")",
    "b.path(\"../../kernel/workqueue_bridge.zig\")",
    "b.path(\"../../net/core/skbuff_bridge.zig\")",
    "b.path(\"phase14_workqueue_bridge.zig\")",
    "b.path(\"phase14_workqueue_reviewability.zig\")",
    "b.path(\"phase14_skbuff_bridge.zig\")",
};

const FORBIDDEN_MAKEFILE_MARKERS = [_][]const u8{
    "phase14-smoke:",
    "phase14-test:",
    "phase14: phase14-validate phase14-smoke phase14-test",
};

const REQUIRED_SURVEY_MARKERS = [_][]const u8{
    "- `PHASE14_COMPILE_SHARD_TOTAL=6`",
    "- `PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1`",
    "- `PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=5`",
    "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`",
    "- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`",
    "- shared gate: `make -C zigux phase14-validate`",
    "- broader wrapper gaps: `phase14-smoke`, `phase14-test`, and `phase14` remain absent from the readable current `zigux/Makefile` body",
    "- focused build shard command: `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`",
    "- machine-readable source: `zigux/tests/phase14_end_to_end_smoke_manifest.json`",
    "- shared survey shard: `phase14-end-to-end-smoke-tests` (`focused_and_full_bundle`)",
};

const REQUIRED_RELEASE_BOUNDARY_MARKERS = [_][]const u8{
    "- `PHASE14_COMPILE_SHARD_TOTAL=6`",
    "- `PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1`",
    "- `PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=5`",
    "publishes the exact six-row compile-shard matrix",
};

const EXPECTED_COUNTS = [_][]const u8{
    "total",
    "focused_and_full_bundle",
    "full_bundle_only",
};

const MARKER = [_][]const u8{
    "PHASE14_CHECK_PACKET=compile_shard_matrix",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (EXPECTED_SMOKE_COMMANDS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_SMOKE_SHARD_COMMANDS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_ANCHOR_ROWS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_COMPILE_SHARDS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_RELEASE_BOUNDARY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_COUNTS) |marker| try guard.requireMarker(text, marker);
    for (MARKER) |marker| try guard.requireMarker(text, marker);
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
