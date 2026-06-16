const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_HVC_REMOVE_HANDOFF_SELF_TEST=pass";

const ORDERED_MARKERS = [_][]const u8{
    "test \"hvc_console verify keeps remove handoff explicit when tty teardown outlives console binding\" {",
    "try std.testing.expect(detached_binding.keeps_irq_for_followup_hangup);",
    "try std.testing.expect(detached_binding.tty_vhangup_requested);",
    "try std.testing.expect(detached_binding.tty_kref_put_after_vhangup);",
    "try std.testing.expect(detached_binding.teardown_via_hangup_pending);",
    "try std.testing.expect(detached_binding.host_io_pending);",
    "test \"hvc_console verify keeps remove handoff explicit when tty is already absent\" {",
    "try std.testing.expect(tty_gone_remove.clears_console_slot_binding);",
    "try std.testing.expect(!tty_gone_remove.keeps_irq_for_followup_hangup);",
    "try std.testing.expect(!tty_gone_remove.tty_vhangup_requested);",
    "try std.testing.expect(!tty_gone_remove.tty_kref_put_after_vhangup);",
    "try std.testing.expect(!tty_gone_remove.teardown_via_hangup_pending);",
    "try std.testing.expect(!tty_gone_remove.host_io_pending);",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (ORDERED_MARKERS) |marker| try guard.requireMarker(text, marker);
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
