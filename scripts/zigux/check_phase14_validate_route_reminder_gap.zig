const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_VALIDATE_ROUTE_REMINDER_GAP_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "GAP_NOTE_PATH",
    "MAKEFILE_PATH",
    "ROUTE_CHECKER_PATH",
    "TESTS_README_PATH",
    "SCRIPTS_README_PATH",
    "CHECKLIST_PATH",
};

const NOTE_MARKERS = [_][]const u8{
    "- `zigux/Makefile` now ships `phase14-validate`",
    "- `scripts/zigux/check_phase14_shared_smoke_route.zig` already fail-closes on that dedicated `phase14-validate` route and still rejects `phase14-smoke` and `phase14-test` as active workflow proof",
    "- `zigux/tests/README.md` still says the readable Makefile has no `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets",
    "- `scripts/zigux/README.md` still says there are no `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets",
    "- `Documentation/zigux/review-checklist.md` still frames `phase14-validate`, `phase14-smoke`, `phase14-test`, and `phase14` together as packet-local or repo-reality-gap vocabulary",
};

const MAKEFILE_MARKERS = [_][]const u8{
    "phase14-validate:",
    "scripts/zigux/check_phase14_shared_smoke_route.zig --self-test",
    "scripts/zigux/check_phase14_shared_smoke_route.zig",
    "scripts\zigux/validate_phase14.zig --self-test",
    "scripts\zigux/validate_phase14.zig",
    "scripts/zigux/check_phase14_release_boundary_exact_counts.zig --self-test",
    "scripts/zigux/check_phase14_release_boundary_exact_counts.zig",
};

const ROUTE_CHECKER_MARKERS = [_][]const u8{
    "phase14-validate",
    "run: make -C zigux phase14-validate",
};

const TESTS_README_MARKERS = [_][]const u8{
    "and no `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets",
};

const SCRIPTS_README_MARKERS = [_][]const u8{
    "there are still no `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets",
};

const CHECKLIST_MARKERS = [_][]const u8{
    "while `phase14-validate`, `phase14-smoke`, `phase14-test`, and `phase14` stay packet-local or repo-reality-gap vocabulary",
};

const MARKER = [_][]const u8{
    "PHASE14_CHECK_PACKET=validate_route_reminder_gap",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (ROUTE_CHECKER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (TESTS_README_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SCRIPTS_README_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (CHECKLIST_MARKERS) |marker| try guard.requireMarker(text, marker);
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
