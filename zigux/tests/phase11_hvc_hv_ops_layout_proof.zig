const std = @import("std");
const layout_assert = @import("layout_assert");

const HvcStruct = opaque {};

const HvOps = extern struct {
    get_chars: ?*const fn (u32, [*]u8, c_int) callconv(.c) c_int,
    put_chars: ?*const fn (u32, [*]const u8, c_int) callconv(.c) c_int,
    flush: ?*const fn (u32, bool) callconv(.c) c_int,
    notifier_add: ?*const fn (*HvcStruct, c_int) callconv(.c) c_int,
    notifier_del: ?*const fn (*HvcStruct, c_int) callconv(.c) void,
    notifier_hangup: ?*const fn (*HvcStruct, c_int) callconv(.c) void,
    tiocmget: ?*const fn (*HvcStruct) callconv(.c) c_int,
    tiocmset: ?*const fn (*HvcStruct, c_uint, c_uint) callconv(.c) c_int,
    dtr_rts: ?*const fn (*HvcStruct, bool) callconv(.c) void,
};

fn readFileAlloc(allocator: std.mem.Allocator, path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase11 hvc hv_ops layout proof keeps callback table explicit" {
    try layout_assert.expectSize(HvOps, 72);
    try layout_assert.expectAlign(HvOps, 8);
    try layout_assert.expectOffset(HvOps, "get_chars", 0);
    try layout_assert.expectOffset(HvOps, "put_chars", 8);
    try layout_assert.expectOffset(HvOps, "flush", 16);
    try layout_assert.expectOffset(HvOps, "notifier_add", 24);
    try layout_assert.expectOffset(HvOps, "notifier_del", 32);
    try layout_assert.expectOffset(HvOps, "notifier_hangup", 40);
    try layout_assert.expectOffset(HvOps, "tiocmget", 48);
    try layout_assert.expectOffset(HvOps, "tiocmset", 56);
    try layout_assert.expectOffset(HvOps, "dtr_rts", 64);
}

test "phase11 hvc hv_ops layout proof stays tied to the exported header" {
    const hvc_header = try readFileAlloc(std.testing.allocator, "drivers/tty/hvc/hvc_console.h", 32 * 1024);
    defer std.testing.allocator.free(hvc_header);

    try expectContains(hvc_header, "struct hv_ops {");
    try expectContains(hvc_header, "(*get_chars)");
    try expectContains(hvc_header, "(*put_chars)");
    try expectContains(hvc_header, "(*flush)");
    try expectContains(hvc_header, "(*notifier_add)");
    try expectContains(hvc_header, "(*notifier_del)");
    try expectContains(hvc_header, "(*notifier_hangup)");
    try expectContains(hvc_header, "(*tiocmget)");
    try expectContains(hvc_header, "(*tiocmset)");
    try expectContains(hvc_header, "(*dtr_rts)");
}
