const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_HVC_VERIFY_HELPER_BOUNDARY_SELF_TEST=pass";

const REQUIRED_NOTE_MARKERS = [_][]const u8{
    "`CleanupTrigger.hangup_only` and `CleanupTrigger.final_close_and_hangup`",
    "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized`",
    "`NotifierUnregisterTimingState.targeted_unregister_request`",
    "`targetless_dispatch_without_notifier`",
    "non-kernel sysrq literal fallback",
};

const REQUIRED_VERIFY_MARKERS = [_][]const u8{
    "CleanupTrigger.hangup_only",
    "CleanupTrigger.final_close_and_hangup",
    "NotifierUnregisterTimingState.targetless_unregister_request_sanitized",
    "NotifierUnregisterTimingState.targeted_unregister_request",
    "targetless_dispatch_without_notifier",
    "non-kernel sysrq literal fallback",
};

const REQUIRED_SURVEY_NOTE_MARKERS = [_][]const u8{
    "drivers/tty/hvc/hvc_console_verify.zig",
    "verify-side helper boundaries",
    "targetless notifier no-unregister edge",
};

const REQUIRED_VALIDATION_MATRIX_MARKERS = [_][]const u8{
    "drivers/tty/hvc/hvc_console_verify.zig",
    "cleanup prerequisite failures",
    "targetless sysrq dispatch from implying notifier callbacks",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_VERIFY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_SURVEY_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_VALIDATION_MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
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
