const std = @import("std");
const abi = @import("abi_bindings");
const rbtree = @import("rbtree_bindings");

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

pub fn assertBoundaryHeaderLayout() void {
    assertSize(abi.BoundaryHeader, 8);
    assertAlign(abi.BoundaryHeader, 4);
    assertFieldType(abi.BoundaryHeader, "size", u32);
    assertFieldType(abi.BoundaryHeader, "abi_version", u16);
    assertFieldType(abi.BoundaryHeader, "flags", u16);
    assertOffset(abi.BoundaryHeader, "size", 0);
    assertOffset(abi.BoundaryHeader, "abi_version", 4);
    assertOffset(abi.BoundaryHeader, "flags", 6);
}

pub fn assertExportStatusLayout() void {
    assertSize(abi.ExportStatus, 8);
    assertAlign(abi.ExportStatus, 4);
    assertFieldType(abi.ExportStatus, "code", i32);
    assertFieldType(abi.ExportStatus, "facility", u16);
    assertFieldType(abi.ExportStatus, "flags", u16);
    assertOffset(abi.ExportStatus, "code", 0);
    assertOffset(abi.ExportStatus, "facility", 4);
    assertOffset(abi.ExportStatus, "flags", 6);
}

pub fn assertInteropPolicyLayout() void {
    assertSize(abi.InteropPolicy, 4);
    assertAlign(abi.InteropPolicy, 1);
    assertFieldType(abi.InteropPolicy, "panic_mode", u8);
    assertFieldType(abi.InteropPolicy, "allocator_mode", u8);
    assertFieldType(abi.InteropPolicy, "unsafe_scope", u8);
    assertFieldType(abi.InteropPolicy, "reserved", u8);
    assertOffset(abi.InteropPolicy, "panic_mode", 0);
    assertOffset(abi.InteropPolicy, "allocator_mode", 1);
    assertOffset(abi.InteropPolicy, "unsafe_scope", 2);
    assertOffset(abi.InteropPolicy, "reserved", 3);
}

pub fn assertMmioRangeLayout() void {
    assertSize(abi.MmioRange, @sizeOf(usize) + 8);
    assertAlign(abi.MmioRange, @alignOf(usize));
    assertFieldType(abi.MmioRange, "base_addr", usize);
    assertFieldType(abi.MmioRange, "length", u32);
    assertFieldType(abi.MmioRange, "stride", u32);
    assertOffset(abi.MmioRange, "base_addr", 0);
    assertOffset(abi.MmioRange, "length", @sizeOf(usize));
    assertOffset(abi.MmioRange, "stride", @sizeOf(usize) + 4);
}

pub fn assertBitmapViewLayout() void {
    assertSize(abi.BitmapView, @sizeOf(usize) + 8);
    assertAlign(abi.BitmapView, @alignOf(usize));
    assertFieldType(abi.BitmapView, "words_addr", usize);
    assertFieldType(abi.BitmapView, "nbits", u32);
    assertFieldType(abi.BitmapView, "word_count", u32);
    assertOffset(abi.BitmapView, "words_addr", 0);
    assertOffset(abi.BitmapView, "nbits", @sizeOf(usize));
    assertOffset(abi.BitmapView, "word_count", @sizeOf(usize) + 4);
}

pub fn assertCpuMaskViewLayout() void {
    assertSize(abi.CpuMaskView, @sizeOf(usize) + 8);
    assertAlign(abi.CpuMaskView, @alignOf(usize));
    assertFieldType(abi.CpuMaskView, "bits_addr", usize);
    assertFieldType(abi.CpuMaskView, "nr_cpu_ids", u32);
    assertFieldType(abi.CpuMaskView, "reserved", u32);
    assertOffset(abi.CpuMaskView, "bits_addr", 0);
    assertOffset(abi.CpuMaskView, "nr_cpu_ids", @sizeOf(usize));
    assertOffset(abi.CpuMaskView, "reserved", @sizeOf(usize) + 4);
}

pub fn assertRbtreeRootViewLayout() void {
    assertSize(rbtree.RootView, @sizeOf(usize) * 2 + 8);
    assertAlign(rbtree.RootView, @alignOf(usize));
    assertFieldType(rbtree.RootView, "root_addr", usize);
    assertFieldType(rbtree.RootView, "leftmost_addr", usize);
    assertFieldType(rbtree.RootView, "flags", u32);
    assertFieldType(rbtree.RootView, "reserved", u32);
    assertOffset(rbtree.RootView, "root_addr", 0);
    assertOffset(rbtree.RootView, "leftmost_addr", @sizeOf(usize));
    assertOffset(rbtree.RootView, "flags", @sizeOf(usize) * 2);
    assertOffset(rbtree.RootView, "reserved", @sizeOf(usize) * 2 + 4);
}

test "phase3 layout assertions cover canonical bindings" {
    comptime {
        assertBoundaryHeaderLayout();
        assertExportStatusLayout();
        assertInteropPolicyLayout();
        assertMmioRangeLayout();
        assertBitmapViewLayout();
        assertCpuMaskViewLayout();
        assertRbtreeRootViewLayout();
    }
}
