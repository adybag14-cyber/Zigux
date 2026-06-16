const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_HVC_HV_OPS_SIGNATURE_GAP_SELF_TEST=pass";

const NOTE_MARKERS = [_][]const u8{
    "`PHASE11_HVC_HV_OPS_SIGNATURE_GAP=current_head_mismatch_visible`",
    "`drivers/tty/hvc/hvc_console.zig`",
    "`drivers/tty/hvc/hvc_console.h`",
    "`HvOps.get_chars`",
    "`HvOps.put_chars`",
    "`usize` count and `isize` return types",
    "exported `int` count and `int` return contract",
    "realign `HvOps.get_chars` and",
};

const HEADER_MARKERS = [_][]const u8{
    "int (*get_chars)(uint32_t vtermno, char *buf, int count);",
    "int (*put_chars)(uint32_t vtermno, const char *buf, int count);",
};

const ZIG_MARKERS = [_][]const u8{
    "get_chars: ?*const fn (u32, [*]u8, usize) callconv(.c) isize = null,",
    "put_chars: ?*const fn (u32, [*]const u8, usize) callconv(.c) isize = null,",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (HEADER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (ZIG_MARKERS) |marker| try guard.requireMarker(text, marker);
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
