const std = @import("std");
const layout_assert = @import("layout_assert");

const HvcStruct = opaque {};

const HvOps = extern struct {
    get_chars: ?*const fn (u32, [*]c_char, c_int) callconv(.c) c_int,
    put_chars: ?*const fn (u32, [*]const c_char, c_int) callconv(.c) c_int,
    flush: ?*const fn (u32, bool) callconv(.c) c_int,
    notifier_add: ?*const fn (*HvcStruct, c_int) callconv(.c) c_int,
    notifier_del: ?*const fn (*HvcStruct, c_int) callconv(.c) void,
    notifier_hangup: ?*const fn (*HvcStruct, c_int) callconv(.c) void,
    tiocmget: ?*const fn (*HvcStruct) callconv(.c) c_int,
    tiocmset: ?*const fn (*HvcStruct, c_uint, c_uint) callconv(.c) c_int,
    dtr_rts: ?*const fn (*HvcStruct, bool) callconv(.c) void,
};

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

test "phase11 hvc hv_ops layout proof keeps callback signatures exact" {
    comptime {
        assertExactType(
            @FieldType(HvOps, "get_chars"),
            ?*const fn (u32, [*]c_char, c_int) callconv(.c) c_int,
        );
        assertExactType(
            @FieldType(HvOps, "put_chars"),
            ?*const fn (u32, [*]const c_char, c_int) callconv(.c) c_int,
        );
        assertExactType(
            @FieldType(HvOps, "flush"),
            ?*const fn (u32, bool) callconv(.c) c_int,
        );
        assertExactType(
            @FieldType(HvOps, "notifier_add"),
            ?*const fn (*HvcStruct, c_int) callconv(.c) c_int,
        );
        assertExactType(
            @FieldType(HvOps, "notifier_del"),
            ?*const fn (*HvcStruct, c_int) callconv(.c) void,
        );
        assertExactType(
            @FieldType(HvOps, "notifier_hangup"),
            ?*const fn (*HvcStruct, c_int) callconv(.c) void,
        );
        assertExactType(
            @FieldType(HvOps, "tiocmget"),
            ?*const fn (*HvcStruct) callconv(.c) c_int,
        );
        assertExactType(
            @FieldType(HvOps, "tiocmset"),
            ?*const fn (*HvcStruct, c_uint, c_uint) callconv(.c) c_int,
        );
        assertExactType(
            @FieldType(HvOps, "dtr_rts"),
            ?*const fn (*HvcStruct, bool) callconv(.c) void,
        );
    }
}

test "phase11 hvc hv_ops layout proof stays tied to the exported header" {
    const hvc_header = try readFileAlloc(std.testing.allocator, "drivers/tty/hvc/hvc_console.h", 32 * 1024);
    defer std.testing.allocator.free(hvc_header);

    try expectContains(hvc_header, "struct hv_ops {");
    try expectContains(hvc_header, "int (*get_chars)(uint32_t vtermno, char *buf, int count);");
    try expectContains(hvc_header, "int (*put_chars)(uint32_t vtermno, const char *buf, int count);");
    try expectContains(hvc_header, "int (*flush)(uint32_t vtermno, bool wait);");
    try expectContains(hvc_header, "int (*notifier_add)(struct hvc_struct *hp, int irq);");
    try expectContains(hvc_header, "void (*notifier_del)(struct hvc_struct *hp, int irq);");
    try expectContains(hvc_header, "void (*notifier_hangup)(struct hvc_struct *hp, int irq);");
    try expectContains(hvc_header, "int (*tiocmget)(struct hvc_struct *hp);");
    try expectContains(hvc_header, "int (*tiocmset)(struct hvc_struct *hp, unsigned int set, unsigned int clear);");
    try expectContains(hvc_header, "void (*dtr_rts)(struct hvc_struct *hp, bool active);");
}
