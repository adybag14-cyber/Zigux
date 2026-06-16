const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_COMPILE_SHARD_ROADMAP_COVERAGE_SELF_TEST=pass";

const EXPECTED_COMPILE_SHARDS = [_][]const u8{
    "{label:phase14-workqueue-bridge-tests",
    "root_source:phase14_workqueue_bridge.zig",
    "coverage:full_bundle_only",
    "}",
    "{label:phase14-workqueue-reviewability-tests",
    "root_source:phase14_workqueue_reviewability.zig",
    "coverage:full_bundle_only",
    "}",
    "{label:phase14-skbuff-bridge-tests",
    "root_source:phase14_skbuff_bridge.zig",
    "coverage:full_bundle_only",
    "}",
    "{label:phase14-ring-buffer-survey-tests",
    "root_source:phase14_ring_buffer_survey.zig",
    "coverage:full_bundle_only",
    "}",
    "{label:phase14-rcu-tree-survey-tests",
    "root_source:phase14_rcu_tree_survey.zig",
    "coverage:full_bundle_only",
    "}",
    "{label:phase14-end-to-end-smoke-tests",
    "root_source:phase14_end_to_end_smoke_survey.zig",
    "coverage:focused_and_full_bundle",
    "}",
};

const EXPECTED_MATRIX_ROWS = [_][]const u8{
    "    * `phase14-workqueue-bridge-tests` -> `phase14_workqueue_bridge.zig` -> `full_bundle_only`",
    "    * `phase14-workqueue-reviewability-tests` -> `phase14_workqueue_reviewability.zig` -> `full_bundle_only`",
    "    * `phase14-skbuff-bridge-tests` -> `phase14_skbuff_bridge.zig` -> `full_bundle_only`",
    "    * `phase14-ring-buffer-survey-tests` -> `phase14_ring_buffer_survey.zig` -> `full_bundle_only`",
    "    * `phase14-rcu-tree-survey-tests` -> `phase14_rcu_tree_survey.zig` -> `full_bundle_only`",
    "    * `phase14-end-to-end-smoke-tests` -> `phase14_end_to_end_smoke_survey.zig` -> `focused_and_full_bundle`",
};

const EXPECTED_ROADMAP_DESTINATION_LINE = [_][]const u8{
    "  * the same packet also keeps the two landed bridge-backed roadmap destinations explicit by tying `phase14-workqueue-bridge-tests` to `../../kernel/workqueue_bridge.zig` and `phase14-skbuff-bridge-tests` to `../../net/core/skbuff_bridge.zig`, instead of letting the matrix collapse to test-root names alone.",
};

const EXPECTED_BUILD_MARKERS = [_][]const u8{
    "const workqueue_bridge_module = b.createModule(.{ .root_source_file = b.path(\"../../kernel/workqueue_bridge.zig\")",
    "const skbuff_bridge_module = b.createModule(.{ .root_source_file = b.path(\"../../net/core/skbuff_bridge.zig\")",
    "const phase14_workqueue_bridge_module = b.createModule(.{ .root_source_file = b.path(\"phase14_workqueue_bridge.zig\")",
    "const phase14_skbuff_bridge_module = b.createModule(.{ .root_source_file = b.path(\"phase14_skbuff_bridge.zig\")",
    "phase14_workqueue_bridge_module.addImport(\"workqueue_bridge\", workqueue_bridge_module);",
    "phase14_skbuff_bridge_module.addImport(\"skbuff_bridge\", skbuff_bridge_module);",
    ".name = \"phase14-workqueue-bridge-tests\"",
    ".name = \"phase14-skbuff-bridge-tests\"",
};

const EXPECTED_COMPILE_SHARD_COUNTS = [_][]const u8{
    "total",
    "focused_and_full_bundle",
    "full_bundle_only",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (EXPECTED_COMPILE_SHARDS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_MATRIX_ROWS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_ROADMAP_DESTINATION_LINE) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_COMPILE_SHARD_COUNTS) |marker| try guard.requireMarker(text, marker);
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
