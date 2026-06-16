const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_HVC_VERIFY_HELPER_PACKET_SELF_TEST=pass";

const VERIFY_HELPER_MARKERS = [_][]const u8{
    "test \"hvc_console verify keeps final-close teardown handoff ordering explicit\" {",
    "test \"hvc_console verify keeps hung-up and detached teardown matrix truthful\" {",
    "test \"hvc_console verify keeps remove handoff explicit when tty teardown outlives console binding\" {",
    "test \"hvc_console verify keeps remove handoff explicit when tty is already absent\" {",
    "test \"hvc_console verify keeps cleanup prerequisite failures explicit\" {",
    "try std.testing.expect(remove.clears_console_slot_binding);",
    "try std.testing.expect(remove.keeps_irq_for_followup_hangup);",
    "try std.testing.expect(remove.teardown_via_hangup_pending);",
    "try std.testing.expect(!tty_gone_remove.tty_vhangup_requested);",
    "try std.testing.expect(!tty_gone_remove.host_io_pending);",
    "try std.testing.expectError(error.CleanupRequiresFinalCloseOrHangup, console.summarizeCleanupHandoff(.{",
    "try std.testing.expectError(error.CleanupRequiresTtyPortReference, console.summarizeCleanupHandoff(.{",
    "try std.testing.expectError(error.ConsoleUnavailable, console.summarizeCleanupHandoff(.{}));",
    "try std.testing.expectError(error.ConsoleUnavailable, console.summarizeRemoveHandoff(.{}));",
};

const CLEANUP_REPLAY_MARKERS = [_][]const u8{
    "test \"phase11 hvc console keeps hvc_cleanup tty-port release boundaries reviewable\" {",
    "const final_cleanup = try console.summarizeCleanupHandoff(.{});",
    "try std.testing.expect(final_cleanup.tty_port_put_requested);",
    "try std.testing.expect(final_cleanup.drops_tty_port_reference);",
    "const hangup_cleanup = try console.summarizeCleanupHandoff(.{",
    ".hung_up = true,",
    "try std.testing.expect(hangup_cleanup.close_skipped);",
    "try std.testing.expect(!hangup_cleanup.final_close);",
    "try std.testing.expectError(error.CleanupRequiresFinalCloseOrHangup, console.summarizeCleanupHandoff(.{",
    "try std.testing.expectError(error.CleanupRequiresTtyPortReference, console.summarizeCleanupHandoff(.{",
    "_ = console.teardown();",
    "try std.testing.expectError(error.ConsoleUnavailable, console.summarizeCleanupHandoff(.{}));",
};

const FILES = [_][]const u8{
    "verify_helper",
    "drivers/tty/hvc/hvc_console_verify.zig",
    "cleanup_replay",
    "zigux/tests/phase11_hvc_cleanup.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (VERIFY_HELPER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (CLEANUP_REPLAY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FILES) |marker| try guard.requireMarker(text, marker);
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
