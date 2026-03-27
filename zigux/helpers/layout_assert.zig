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

pub fn assertOffset(comptime T: type, comptime field_name: []const u8, comptime expected: usize) void {
    const actual = @offsetOf(T, field_name);
    if (actual != expected) {
        @compileError(std.fmt.comptimePrint(
            "layout offset mismatch for {s}.{s}: expected {d}, got {d}",
            .{ @typeName(T), field_name, expected, actual },
        ));
    }
}

test "phase3 layout assertions cover canonical bindings" {
    comptime {
        assertSize(abi.BoundaryHeader, 8);
        assertAlign(abi.BoundaryHeader, 4);
        assertOffset(abi.BoundaryHeader, "abi_version", 4);
        assertOffset(abi.BoundaryHeader, "flags", 6);
        assertOffset(abi.ExportStatus, "facility", 4);
        assertOffset(abi.ExportStatus, "flags", 6);
        assertSize(abi.InteropPolicy, 4);
        assertOffset(abi.InteropPolicy, "allocator_mode", 1);
        assertOffset(abi.InteropPolicy, "unsafe_scope", 2);
    }
}
