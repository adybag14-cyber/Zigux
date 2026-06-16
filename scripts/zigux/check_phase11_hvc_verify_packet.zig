const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_HVC_VERIFY_PACKET=pass";

const FILE_EXPECTATIONS = [_][]const u8{
    "FileExpectationdrivers/tty/hvc/hvc_console_verify.zigpub const CleanupTrigger = enumfinal_close_onlyhangup_onlyfinal_close_and_hanguppub const CleanupPrerequisiteSummary = structtrigger: CleanupTriggertest \"hvc_console verify keeps hangup-only cleanup prerequisites explicit\"test \"hvc_console verify keeps cleanup prerequisite failures explicit\"test \"hvc_console verify keeps attached remove handoff explicit before tty detach\"test \"hvc_console verify keeps remove handoff explicit when tty is already absent\"test \"hvc_console verify keeps non-kernel sysrq literal fallback from implying notifier callbacks\"",
    "FileExpectationzigux/tests/phase11_hvc_cleanup.zigpub const CleanupTrigger = enumfinal_close_onlyhangup_onlyfinal_close_and_hanguptrigger: CleanupTriggersummary.triggersummary.trigger == .final_close_onlysummary.trigger == .hangup_onlysummary.trigger == .final_close_and_hangup",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (FILE_EXPECTATIONS) |marker| try guard.requireMarker(text, marker);
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
