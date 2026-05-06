const std = @import("std");
const abi = @import("abi_bindings");

pub fn assertSize(comptime T: type, comptime expected: usize) void {
    if (@sizeOf(T) != expected) {
        @compileError(std.fmt.comptimePrint(
            "layout size mismatch for {s}: expected {d}, got {d}",
            .{ @typeName(T), expected, @sizeOf(T) },
        ));
    }
}

pub fn assertAlign(comptime T: type, comptime expected: usize) void {
    if (@alignOf(T) != expected) {
        @compileError(std.fmt.comptimePrint(
            "layout align mismatch for {s}: expected {d}, got {d}",
            .{ @typeName(T), expected, @alignOf(T) },
        ));
    }
}

pub fn assertFieldType(comptime T: type, comptime field_name: []const u8, comptime expected: type) void {
    const actual = @FieldType(T, field_name);
    if (actual != expected) {
        @compileError(std.fmt.comptimePrint(
            "layout field type mismatch for {s}.{s}: expected {s}, got {s}",
            .{ @typeName(T), field_name, @typeName(expected), @typeName(actual) },
        ));
    }
}

pub fn assertOffset(comptime T: type, comptime field_name: []const u8, comptime expected: usize) void {
    const actual = @offsetOf(T, field_name);
    if (actual != expected) {
        @compileError(std.fmt.comptimePrint(
            "layout offset mismatch for {s}.{s}: expected {d}, got {d}",
            .{ @typeName(T), field_name, expected, actual },
        ));
    }
}

fn assertInteropPolicyByteValue(comptime label: []const u8, comptime actual: anytype, comptime expected: u8) void {
    if (actual != expected) {
        @compileError(std.fmt.comptimePrint(
            "interop policy byte mismatch for {s}: expected {d}, got {d}",
            .{ label, expected, actual },
        ));
    }
}

fn assertInteropPolicyEnumLayouts() void {
    assertSize(abi.PanicMode, 1);
    assertAlign(abi.PanicMode, 1);
    assertSize(abi.AllocatorMode, 1);
    assertAlign(abi.AllocatorMode, 1);
    assertSize(abi.UnsafeScope, 1);
    assertAlign(abi.UnsafeScope, 1);
}

fn assertInteropPolicyModeValues() void {
    assertInteropPolicyByteValue("panic_mode.abort", @intFromEnum(abi.PanicMode.abort), 0);
    assertInteropPolicyByteValue("panic_mode.bug", @intFromEnum(abi.PanicMode.bug), 1);
    assertInteropPolicyByteValue("panic_mode.warn", @intFromEnum(abi.PanicMode.warn), 2);
    assertInteropPolicyByteValue("allocator_mode.caller_provided", @intFromEnum(abi.AllocatorMode.caller_provided), 0);
    assertInteropPolicyByteValue("allocator_mode.kernel_heap", @intFromEnum(abi.AllocatorMode.kernel_heap), 1);
    assertInteropPolicyByteValue("allocator_mode.arena", @intFromEnum(abi.AllocatorMode.arena), 2);
    assertInteropPolicyByteValue("unsafe_scope.none", @intFromEnum(abi.UnsafeScope.none), 0);
    assertInteropPolicyByteValue("unsafe_scope.volatile_mmio", @intFromEnum(abi.UnsafeScope.volatile_mmio), 1);
    assertInteropPolicyByteValue("unsafe_scope.raw_pointer_bridge", @intFromEnum(abi.UnsafeScope.raw_pointer_bridge), 2);
}

pub fn assertRbtreeRootViewLayout() void {
    assertSize(abi.RbtreeRootView, @sizeOf(usize) * 2 + 8);
    assertAlign(abi.RbtreeRootView, @alignOf(usize));
    assertFieldType(abi.RbtreeRootView, "root_addr", usize);
    assertFieldType(abi.RbtreeRootView, "leftmost_addr", usize);
    assertFieldType(abi.RbtreeRootView, "flags", u32);
    assertFieldType(abi.RbtreeRootView, "reserved", u32);
    assertOffset(abi.RbtreeRootView, "root_addr", 0);
    assertOffset(abi.RbtreeRootView, "leftmost_addr", @sizeOf(usize));
    assertOffset(abi.RbtreeRootView, "flags", @sizeOf(usize) * 2);
    assertOffset(abi.RbtreeRootView, "reserved", @sizeOf(usize) * 2 + 4);
}

test "phase3 layout assertions cover canonical bindings" {
    comptime {
        assertSize(abi.BoundaryHeader, 8);
        assertAlign(abi.BoundaryHeader, 4);
        assertFieldType(abi.BoundaryHeader, "size", u32);
        assertFieldType(abi.BoundaryHeader, "abi_version", u16);
        assertFieldType(abi.BoundaryHeader, "flags", u16);
        assertOffset(abi.BoundaryHeader, "abi_version", 4);
        assertOffset(abi.BoundaryHeader, "flags", 6);

        assertFieldType(abi.ExportStatus, "code", i32);
        assertFieldType(abi.ExportStatus, "facility", u16);
        assertFieldType(abi.ExportStatus, "flags", u16);
        assertOffset(abi.ExportStatus, "facility", 4);
        assertOffset(abi.ExportStatus, "flags", 6);

        assertInteropPolicyEnumLayouts();
        assertSize(abi.InteropPolicy, 4);
        assertFieldType(abi.InteropPolicy, "panic_mode", u8);
        assertFieldType(abi.InteropPolicy, "allocator_mode", u8);
        assertFieldType(abi.InteropPolicy, "unsafe_scope", u8);
        assertFieldType(abi.InteropPolicy, "reserved", u8);
        assertOffset(abi.InteropPolicy, "allocator_mode", 1);
        assertOffset(abi.InteropPolicy, "unsafe_scope", 2);
        assertInteropPolicyModeValues();
        assertRbtreeRootViewLayout();
    }
}
