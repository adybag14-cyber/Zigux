const std = @import("std");
const layout_assert = @import("layout_assert");

const WinsizeLayout = extern struct {
    ws_row: u16,
    ws_col: u16,
    ws_xpixel: u16,
    ws_ypixel: u16,
};

const HvcStruct = opaque {};

const HvOpsLayout = extern struct {
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

const HvcInstantiateFn = *const fn (u32, c_int, *const HvOpsLayout) callconv(.c) c_int;
const HvcAllocFn = *const fn (u32, c_int, *const HvOpsLayout, c_int) callconv(.c) ?*HvcStruct;
const HvcRemoveFn = *const fn (*HvcStruct) callconv(.c) void;
const HvcPollFn = *const fn (*HvcStruct) callconv(.c) c_int;
const HvcKickFn = *const fn () callconv(.c) void;
const HvcResizeFn = *const fn (*HvcStruct, WinsizeLayout) callconv(.c) void;
const HvcNotifierAddIrqFn = *const fn (*HvcStruct, c_int) callconv(.c) c_int;
const HvcNotifierDelIrqFn = *const fn (*HvcStruct, c_int) callconv(.c) void;
const HvcNotifierHangupIrqFn = *const fn (*HvcStruct, c_int) callconv(.c) void;

const HvcExportSurface = extern struct {
    hvc_instantiate: HvcInstantiateFn,
    hvc_alloc: HvcAllocFn,
    hvc_remove: HvcRemoveFn,
    hvc_poll: HvcPollFn,
    hvc_kick: HvcKickFn,
    __hvc_resize: HvcResizeFn,
    notifier_add_irq: HvcNotifierAddIrqFn,
    notifier_del_irq: HvcNotifierDelIrqFn,
    notifier_hangup_irq: HvcNotifierHangupIrqFn,
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

test "phase11 HVC exported helper proof keeps winsize layout explicit" {
    try layout_assert.expectSize(WinsizeLayout, 8);
    try layout_assert.expectAlign(WinsizeLayout, 2);
    try layout_assert.expectOffset(WinsizeLayout, "ws_row", 0);
    try layout_assert.expectOffset(WinsizeLayout, "ws_col", 2);
    try layout_assert.expectOffset(WinsizeLayout, "ws_xpixel", 4);
    try layout_assert.expectOffset(WinsizeLayout, "ws_ypixel", 6);
}

test "phase11 HVC exported helper proof keeps hv_ops callback table layout explicit" {
    try layout_assert.expectSize(HvOpsLayout, 72);
    try layout_assert.expectAlign(HvOpsLayout, 8);
    try layout_assert.expectOffset(HvOpsLayout, "get_chars", 0);
    try layout_assert.expectOffset(HvOpsLayout, "put_chars", 8);
    try layout_assert.expectOffset(HvOpsLayout, "flush", 16);
    try layout_assert.expectOffset(HvOpsLayout, "notifier_add", 24);
    try layout_assert.expectOffset(HvOpsLayout, "notifier_del", 32);
    try layout_assert.expectOffset(HvOpsLayout, "notifier_hangup", 40);
    try layout_assert.expectOffset(HvOpsLayout, "tiocmget", 48);
    try layout_assert.expectOffset(HvOpsLayout, "tiocmset", 56);
    try layout_assert.expectOffset(HvOpsLayout, "dtr_rts", 64);
}

test "phase11 HVC exported helper proof keeps hv_ops callback signatures exact" {
    comptime {
        assertExactType(
            @FieldType(HvOpsLayout, "get_chars"),
            ?*const fn (u32, [*]c_char, c_int) callconv(.c) c_int,
        );
        assertExactType(
            @FieldType(HvOpsLayout, "put_chars"),
            ?*const fn (u32, [*]const c_char, c_int) callconv(.c) c_int,
        );
        assertExactType(
            @FieldType(HvOpsLayout, "flush"),
            ?*const fn (u32, bool) callconv(.c) c_int,
        );
        assertExactType(
            @FieldType(HvOpsLayout, "notifier_add"),
            ?*const fn (*HvcStruct, c_int) callconv(.c) c_int,
        );
        assertExactType(
            @FieldType(HvOpsLayout, "notifier_del"),
            ?*const fn (*HvcStruct, c_int) callconv(.c) void,
        );
        assertExactType(
            @FieldType(HvOpsLayout, "notifier_hangup"),
            ?*const fn (*HvcStruct, c_int) callconv(.c) void,
        );
        assertExactType(
            @FieldType(HvOpsLayout, "tiocmget"),
            ?*const fn (*HvcStruct) callconv(.c) c_int,
        );
        assertExactType(
            @FieldType(HvOpsLayout, "tiocmset"),
            ?*const fn (*HvcStruct, c_uint, c_uint) callconv(.c) c_int,
        );
        assertExactType(
            @FieldType(HvOpsLayout, "dtr_rts"),
            ?*const fn (*HvcStruct, bool) callconv(.c) void,
        );
    }
}

test "phase11 HVC exported helper proof keeps the exported helper surface layout explicit" {
    try layout_assert.expectSize(HvcExportSurface, 72);
    try layout_assert.expectAlign(HvcExportSurface, 8);
    try layout_assert.expectOffset(HvcExportSurface, "hvc_instantiate", 0);
    try layout_assert.expectOffset(HvcExportSurface, "hvc_alloc", 8);
    try layout_assert.expectOffset(HvcExportSurface, "hvc_remove", 16);
    try layout_assert.expectOffset(HvcExportSurface, "hvc_poll", 24);
    try layout_assert.expectOffset(HvcExportSurface, "hvc_kick", 32);
    try layout_assert.expectOffset(HvcExportSurface, "__hvc_resize", 40);
    try layout_assert.expectOffset(HvcExportSurface, "notifier_add_irq", 48);
    try layout_assert.expectOffset(HvcExportSurface, "notifier_del_irq", 56);
    try layout_assert.expectOffset(HvcExportSurface, "notifier_hangup_irq", 64);
}

test "phase11 HVC exported helper proof keeps exported helper signatures exact" {
    comptime {
        assertExactType(@FieldType(HvcExportSurface, "hvc_instantiate"), HvcInstantiateFn);
        assertExactType(@FieldType(HvcExportSurface, "hvc_alloc"), HvcAllocFn);
        assertExactType(@FieldType(HvcExportSurface, "hvc_remove"), HvcRemoveFn);
        assertExactType(@FieldType(HvcExportSurface, "hvc_poll"), HvcPollFn);
        assertExactType(@FieldType(HvcExportSurface, "hvc_kick"), HvcKickFn);
        assertExactType(@FieldType(HvcExportSurface, "__hvc_resize"), HvcResizeFn);
        assertExactType(@FieldType(HvcExportSurface, "notifier_add_irq"), HvcNotifierAddIrqFn);
        assertExactType(@FieldType(HvcExportSurface, "notifier_del_irq"), HvcNotifierDelIrqFn);
        assertExactType(@FieldType(HvcExportSurface, "notifier_hangup_irq"), HvcNotifierHangupIrqFn);
    }
}

test "phase11 HVC exported helper proof stays tied to the exported header signatures" {
    const hvc_header = try readFileAlloc(std.testing.allocator, "drivers/tty/hvc/hvc_console.h", 32 * 1024);
    defer std.testing.allocator.free(hvc_header);

    try expectContains(hvc_header, "int (*get_chars)(uint32_t vtermno, char *buf, int count);");
    try expectContains(hvc_header, "int (*put_chars)(uint32_t vtermno, const char *buf, int count);");
    try expectContains(hvc_header, "int hvc_instantiate(uint32_t vtermno, int index, const struct hv_ops *ops);");
    try expectContains(hvc_header, "struct hvc_struct *hvc_alloc(uint32_t vtermno, int data, const struct hv_ops *ops, int outbuf_size);");
    try expectContains(hvc_header, "void notifier_hangup_irq(struct hvc_struct *hp, int irq);");
}
