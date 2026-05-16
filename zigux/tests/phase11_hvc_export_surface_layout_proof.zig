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
    get_chars: ?*const fn (u32, [*]u8, usize) callconv(.c) isize,
    put_chars: ?*const fn (u32, [*]const u8, usize) callconv(.c) isize,
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

test "phase11 HVC exported helper proof keeps the exported helper surface layout explicit" {
    comptime {
        layout_assert.assertSize(HvcExportSurface, 72);
        layout_assert.assertAlign(HvcExportSurface, 8);
        layout_assert.assertOffset(HvcExportSurface, "hvc_instantiate", 0);
        layout_assert.assertOffset(HvcExportSurface, "hvc_alloc", 8);
        layout_assert.assertOffset(HvcExportSurface, "hvc_remove", 16);
        layout_assert.assertOffset(HvcExportSurface, "hvc_poll", 24);
        layout_assert.assertOffset(HvcExportSurface, "hvc_kick", 32);
        layout_assert.assertOffset(HvcExportSurface, "__hvc_resize", 40);
        layout_assert.assertOffset(HvcExportSurface, "notifier_add_irq", 48);
        layout_assert.assertOffset(HvcExportSurface, "notifier_del_irq", 56);
        layout_assert.assertOffset(HvcExportSurface, "notifier_hangup_irq", 64);
    }
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
