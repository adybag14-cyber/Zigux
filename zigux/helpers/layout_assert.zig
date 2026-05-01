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

pub fn assertBoundaryHeaderLayout() void {
    assertSize(abi.BoundaryHeader, 8);
    assertAlign(abi.BoundaryHeader, 4);
    assertOffset(abi.BoundaryHeader, "size", 0);
    assertOffset(abi.BoundaryHeader, "abi_version", 4);
    assertOffset(abi.BoundaryHeader, "flags", 6);
}

pub fn assertExportStatusLayout() void {
    assertSize(abi.ExportStatus, 8);
    assertAlign(abi.ExportStatus, 4);
    assertOffset(abi.ExportStatus, "code", 0);
    assertOffset(abi.ExportStatus, "facility", 4);
    assertOffset(abi.ExportStatus, "flags", 6);
}

pub fn assertInteropPolicyLayout() void {
    assertSize(abi.InteropPolicy, 4);
    assertAlign(abi.InteropPolicy, 1);
    assertOffset(abi.InteropPolicy, "panic_mode", 0);
    assertOffset(abi.InteropPolicy, "allocator_mode", 1);
    assertOffset(abi.InteropPolicy, "unsafe_scope", 2);
    assertOffset(abi.InteropPolicy, "reserved", 3);
}

pub fn assertMmioRangeLayout() void {
    assertSize(abi.MmioRange, @sizeOf(usize) + 8);
    assertAlign(abi.MmioRange, @alignOf(usize));
    assertOffset(abi.MmioRange, "base_addr", 0);
    assertOffset(abi.MmioRange, "length", @sizeOf(usize));
    assertOffset(abi.MmioRange, "stride", @sizeOf(usize) + 4);
}

pub fn assertBitmapViewLayout() void {
    assertSize(abi.BitmapView, @sizeOf(usize) + 8);
    assertAlign(abi.BitmapView, @alignOf(usize));
    assertOffset(abi.BitmapView, "words_addr", 0);
    assertOffset(abi.BitmapView, "nbits", @sizeOf(usize));
    assertOffset(abi.BitmapView, "word_count", @sizeOf(usize) + 4);
}

pub fn assertCpuMaskViewLayout() void {
    assertSize(abi.CpuMaskView, @sizeOf(usize) + 8);
    assertAlign(abi.CpuMaskView, @alignOf(usize));
    assertOffset(abi.CpuMaskView, "bits_addr", 0);
    assertOffset(abi.CpuMaskView, "nr_cpu_ids", @sizeOf(usize));
    assertOffset(abi.CpuMaskView, "reserved", @sizeOf(usize) + 4);
}

test "phase3 layout assertions cover canonical bindings" {
    comptime {
        assertBoundaryHeaderLayout();
        assertExportStatusLayout();
        assertInteropPolicyLayout();
        assertMmioRangeLayout();
        assertBitmapViewLayout();
        assertCpuMaskViewLayout();
    }
}
