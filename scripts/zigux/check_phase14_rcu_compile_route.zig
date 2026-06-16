const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_RCU_COMPILE_ROUTE_SELF_TEST=pass";

const NOTE_MARKERS = [_][]const u8{
    "- dedicated compile-route guard surface:",
    "  - `scripts/zigux/check_phase14_rcu_compile_route.zig`",
    "- packet-local rerun vocabulary that public fallback now corroborates, even though this lane still lacks a local exact-replay environment on current `master`:",
    "  - `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`",
    "  - `zig build test --build-file zigux/tests/phase14_build.zig --summary all`",
};

const BUILD_MARKERS = [_][]const u8{
    "const phase14_rcu_tree_survey_module = b.createModule(.{ .root_source_file = b.path(\"phase14_rcu_tree_survey.zig\"), .target = target, .optimize = optimize, });",
    "const phase14_rcu_tree_survey_tests = b.addTest(.{ .name = \"phase14-rcu-tree-survey-tests\", .root_module = phase14_rcu_tree_survey_module, });",
    "const run_phase14_rcu_tree_survey_tests = b.addRunArtifact(phase14_rcu_tree_survey_tests);",
    "test_step.dependOn(&run_phase14_rcu_tree_survey_tests.step);",
};

const REQUIRED_MANIFEST_VALUES = [_][]const u8{
    "smoke_shard_commands",
    "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig",
};

const REQUIRED_COMPILE_SHARD = [_][]const u8{
    "label",
    "phase14-rcu-tree-survey-tests",
    "root_source",
    "phase14_rcu_tree_survey.zig",
    "coverage",
    "full_bundle_only",
};

const REQUIRED_ANCHOR_FIELDS = [_][]const u8{
    "lane_key",
    "P14-L16",
    "anchor",
    "kernel/rcu/tree.c",
    "surveyed_commit",
    "manifest_path",
    "zigux/tests/phase14_rcu_tree_manifest.json",
    "survey_note_path",
    "Documentation/zigux/phase14-rcu-tree-survey.md",
    "blocked_gap",
    "phase14-rcu-tree-bridge-blocker",
};

const MARKER = [_][]const u8{
    "PHASE14_CHECK_PACKET=rcu_compile_route",
};

const CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase14_rcu_compile_route.zig",
};

const EXPECTED_SURVEYED_COMMIT = [_][]const u8{
    "4c889233d157960514b241bcd5aff7cac5fda312",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MANIFEST_VALUES) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_COMPILE_SHARD) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_ANCHOR_FIELDS) |marker| try guard.requireMarker(text, marker);
    for (MARKER) |marker| try guard.requireMarker(text, marker);
    for (CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_SURVEYED_COMMIT) |marker| try guard.requireMarker(text, marker);
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
