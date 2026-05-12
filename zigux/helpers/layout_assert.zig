const std = @import("std");
const abi = @import("abi_bindings");

pub fn size(comptime T: type, expected: usize) !void {
    try std.testing.expectEqual(expected, @sizeOf(T));
}

pub fn alignment(comptime T: type, expected: usize) !void {
    try std.testing.expectEqual(expected, @alignOf(T));
}

pub const @"align" = alignment;

pub fn offset(comptime T: type, comptime field_name: []const u8, expected: usize) !void {
    try std.testing.expectEqual(expected, @offsetOf(T, field_name));
}

pub fn fieldType(comptime T: type, comptime field_name: []const u8, comptime Expected: type) void {
    comptime {
        const actual = @TypeOf(@field(@as(T, undefined), field_name));
        if (actual != Expected) {
            @compileError(std.fmt.comptimePrint(
                "{s} field {s} has unexpected type",
                .{ @typeName(T), field_name },
            ));
        }
    }
}

pub fn byteValue(comptime label: []const u8, comptime actual: u8, comptime expected: u8) void {
    comptime {
        if (actual != expected) {
            @compileError(std.fmt.comptimePrint(
                "{s} expected byte value {d}, found {d}",
                .{ label, expected, actual },
            ));
        }
    }
}

fn assertThreeU32FieldLayout(
    comptime T: type,
    comptime first: []const u8,
    comptime second: []const u8,
    comptime third: []const u8,
) !void {
    try size(T, 12);
    try alignment(T, 4);
    try offset(T, first, 0);
    try offset(T, second, 4);
    try offset(T, third, 8);
    fieldType(T, first, u32);
    fieldType(T, second, u32);
    fieldType(T, third, u32);
}

pub fn assertBoundaryHeaderLayout() !void {
    try size(abi.BoundaryHeader, 8);
    try alignment(abi.BoundaryHeader, 4);
    try offset(abi.BoundaryHeader, "size", 0);
    try offset(abi.BoundaryHeader, "abi_version", 4);
    try offset(abi.BoundaryHeader, "flags", 6);
    fieldType(abi.BoundaryHeader, "size", u32);
    fieldType(abi.BoundaryHeader, "abi_version", u16);
    fieldType(abi.BoundaryHeader, "flags", u16);
}

pub fn assertExportStatusLayout() !void {
    try size(abi.ExportStatus, 8);
    try alignment(abi.ExportStatus, 4);
    try offset(abi.ExportStatus, "code", 0);
    try offset(abi.ExportStatus, "facility", 4);
    try offset(abi.ExportStatus, "flags", 6);
    fieldType(abi.ExportStatus, "code", i32);
    fieldType(abi.ExportStatus, "facility", u16);
    fieldType(abi.ExportStatus, "flags", u16);
}

pub fn assertInteropPolicyLayout() !void {
    try size(abi.InteropPolicy, 4);
    try alignment(abi.InteropPolicy, 1);
    try offset(abi.InteropPolicy, "panic_mode", 0);
    try offset(abi.InteropPolicy, "allocator_mode", 1);
    try offset(abi.InteropPolicy, "unsafe_scope", 2);
    try offset(abi.InteropPolicy, "reserved", 3);
    fieldType(abi.InteropPolicy, "panic_mode", u8);
    fieldType(abi.InteropPolicy, "allocator_mode", u8);
    fieldType(abi.InteropPolicy, "unsafe_scope", u8);
    fieldType(abi.InteropPolicy, "reserved", u8);
}

pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowViewLayout() !void {
    try assertThreeU32FieldLayout(
        abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView,
        "ack_window",
        "delivery_window",
        "status",
    );
}

pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummaryLayout() !void {
    try assertThreeU32FieldLayout(
        abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary,
        "applied",
        "skipped",
        "delivered",
    );
}

pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetViewLayout() !void {
    try assertThreeU32FieldLayout(
        abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView,
        "budget",
        "window",
        "flags",
    );
}

pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummaryLayout() !void {
    try assertThreeU32FieldLayout(
        abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary,
        "attempted",
        "applied",
        "skipped",
    );
}

pub fn assertInteropPolicyModeValues() void {
    byteValue("panic_mode.abort", @intFromEnum(abi.PanicMode.abort), abi.PANIC_ABORT);
    byteValue("panic_mode.bug", @intFromEnum(abi.PanicMode.bug), abi.PANIC_BUG);
    byteValue("panic_mode.warn", @intFromEnum(abi.PanicMode.warn), abi.PANIC_WARN);
    byteValue(
        "allocator_mode.caller_provided",
        @intFromEnum(abi.AllocatorMode.caller_provided),
        abi.ALLOC_CALLER_PROVIDED,
    );
    byteValue("allocator_mode.kernel_heap", @intFromEnum(abi.AllocatorMode.kernel_heap), abi.ALLOC_KERNEL_HEAP);
    byteValue("allocator_mode.arena", @intFromEnum(abi.AllocatorMode.arena), abi.ALLOC_ARENA);
    byteValue("unsafe_scope.none", @intFromEnum(abi.UnsafeScope.none), abi.UNSAFE_NONE);
    byteValue(
        "unsafe_scope.volatile_mmio",
        @intFromEnum(abi.UnsafeScope.volatile_mmio),
        abi.UNSAFE_VOLATILE_MMIO,
    );
    byteValue(
        "unsafe_scope.raw_pointer_bridge",
        @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        abi.UNSAFE_RAW_POINTER_BRIDGE,
    );
}

test "phase3 layout assertions cover canonical bindings" {
    try assertBoundaryHeaderLayout();
    try assertExportStatusLayout();
    try assertInteropPolicyLayout();
    try assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowViewLayout();
    try assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummaryLayout();
    try assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetViewLayout();
    try assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummaryLayout();
    assertInteropPolicyModeValues();
}
