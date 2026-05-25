const std = @import("std");
const hvc_console = @import("hvc_console");

fn assertExactType(comptime Actual: type, comptime Expected: type) void {
    if (Actual != Expected) {
        @compileError(std.fmt.comptimePrint(
            "type mismatch: expected {s}, found {s}",
            .{ @typeName(Expected), @typeName(Actual) },
        ));
    }
}

fn readFileAlloc(allocator: std.mem.Allocator, path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase11 hvc header constant proof keeps exported module constants exact" {
    try std.testing.expectEqual(@as(u32, 16), hvc_console.MAX_NR_HVC_CONSOLES);
    try std.testing.expectEqual(@as(u32, 0x01), hvc_console.HVC_ALLOC_TTY_ADAPTERS);
}

test "phase11 hvc header constant proof keeps exported module constant types exact" {
    comptime {
        assertExactType(@TypeOf(hvc_console.MAX_NR_HVC_CONSOLES), u32);
        assertExactType(@TypeOf(hvc_console.HVC_ALLOC_TTY_ADAPTERS), u32);
    }
}

test "phase11 hvc header constant proof stays tied to current header and zig surfaces" {
    const hvc_header = try readFileAlloc(std.testing.allocator, "../../drivers/tty/hvc/hvc_console.h", 32 * 1024);
    defer std.testing.allocator.free(hvc_header);

    const hvc_module = try readFileAlloc(std.testing.allocator, "../../drivers/tty/hvc/hvc_console.zig", 64 * 1024);
    defer std.testing.allocator.free(hvc_module);

    try expectContains(hvc_header, "#define MAX_NR_HVC_CONSOLES 16");
    try expectContains(hvc_header, "#define HVC_ALLOC_TTY_ADAPTERS 1");
    try expectContains(hvc_module, "pub const MAX_NR_HVC_CONSOLES: u32 = 16;");
    try expectContains(hvc_module, "pub const HVC_ALLOC_TTY_ADAPTERS: u32 = 0x01;");
}
