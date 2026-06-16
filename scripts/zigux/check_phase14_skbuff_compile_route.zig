const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_SKBUFF_COMPILE_ROUTE_SELF_TEST=pass";

const NOTE_MARKERS = [_][]const u8{
    "- current `master` exposes `zigux/tests/phase14_skbuff_bridge.zig`",
    "- current `master` exposes `zigux/tests/phase14_build.zig`",
    "- current `master` exposes `net/core/skbuff_bridge.zig`",
    "- current `master` exposes `zigux/tests/phase14_skbuff_bridge_manifest.json`",
    "- `zigux/tests/phase14_build.zig` wires `../../net/core/skbuff_bridge.zig` and `phase14_skbuff_bridge.zig` into the dedicated Phase 14 build shard, so there is now a live skbuff-local review route on current `master`",
    "- that route is still evidence for a bounded boundary packet only; it must not be restated as a parity claim while `phase14-skbuff-live-ownership-blocker` stays open",
};

const BUILD_MARKERS = [_][]const u8{
    "const skbuff_bridge_module = b.createModule(.{ .root_source_file = b.path(\"../../net/core/skbuff_bridge.zig\"), .target = target, .optimize = optimize, });",
    "const phase14_skbuff_bridge_module = b.createModule(.{ .root_source_file = b.path(\"phase14_skbuff_bridge.zig\"), .target = target, .optimize = optimize, });",
    "phase14_skbuff_bridge_module.addImport(\"skbuff_bridge\", skbuff_bridge_module);",
    "const phase14_skbuff_bridge_tests = b.addTest(.{ .name = \"phase14-skbuff-bridge-tests\", .root_module = phase14_skbuff_bridge_module, });",
    "const run_phase14_skbuff_bridge_tests = b.addRunArtifact(phase14_skbuff_bridge_tests);",
    "test_step.dependOn(&run_phase14_skbuff_bridge_tests.step);",
};

const REQUIRED_SHARED_SMOKE_SURFACES = [_][]const u8{
    "CHECKER_PATH",
    "Documentation/zigux/phase14-skbuff-bridge-survey.md",
    "zigux/tests/phase14_build.zig",
};

const REQUIRED_MANIFEST_VALUES = [_][]const u8{
    "smoke_shard_commands",
    "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig",
};

const REQUIRED_SURVEY_SUMMARY_FLAGS = [_][]const u8{
    "shared_manifest_records_skbuff_compile_route_checker",
};

const MARKER = [_][]const u8{
    "PHASE14_CHECK_PACKET=skbuff_compile_route",
};

const CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase14_skbuff_compile_route.zig",
};

const EXPECTED_SURVEYED_COMMIT = [_][]const u8{
    "f05e02445443e7743c3675a6f8ca4f70f6e736fb",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_SHARED_SMOKE_SURFACES) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MANIFEST_VALUES) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_SURVEY_SUMMARY_FLAGS) |marker| try guard.requireMarker(text, marker);
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
