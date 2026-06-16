const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_SHARED_SUMMARY_GAP_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "`PHASE11_SHARED_SUMMARY_GAP=phase11_broad_reminders_missing`",
    "`Documentation/zigux/phase11-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase11-validation-matrix-gap-survey.md`",
    "`Documentation/zigux/phase11-hvc-console-survey.md`",
    "`Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`",
    "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`",
    "`Documentation/zigux/README.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/README.md`",
    "`zigux/tests/README.md`",
    "Current broad shared reminders do not currently materialize",
    "`scripts/zigux/check_phase11_shared_summary_surfaces.zig`",
    "`zigux/tests/phase11_build.zig`",
    "`make -C zigux phase11-contract`",
    "`drivers/tty/hvc/hvc_console_verify.zig`",
    "`zigux/tests/phase11_hvc_console_manifest.json`",
    "Do not use the broad shared reminders listed above as Phase 11 authority",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "whole simple-driver tranche is closed",
    "shipped Phase 11 shared-summary checker",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
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
