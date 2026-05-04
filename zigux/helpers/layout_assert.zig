const std = @import("std");
const abi = @import("abi_bindings");
const narrow = @import("narrow_unsafe");

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

pub fn assertUnsafeScopeTagParity() void {
    assertInteropPolicyByteValue("unsafe_scope_tag.none", @intFromEnum(narrow.UnsafeScopeTag.none), @intFromEnum(abi.UnsafeScope.none));
    assertInteropPolicyByteValue("unsafe_scope_tag.volatile_mmio", @intFromEnum(narrow.UnsafeScopeTag.volatile_mmio), @intFromEnum(abi.UnsafeScope.volatile_mmio));
    assertInteropPolicyByteValue("unsafe_scope_tag.raw_pointer_bridge", @intFromEnum(narrow.UnsafeScopeTag.raw_pointer_bridge), @intFromEnum(abi.UnsafeScope.raw_pointer_bridge));
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

pub fn assertInteropPolicyModeValues() void {
    assertInteropPolicyByteValue("panic_mode.abort", @intFromEnum(abi.PanicMode.abort), 0);
    assertInteropPolicyByteValue("panic_mode.bug", @intFromEnum(abi.PanicMode.bug), 1);
    assertInteropPolicyByteValue("panic_mode.warn", @intFromEnum(abi.PanicMode.warn), 2);
    assertInteropPolicyByteValue("allocator_mode.caller_provided", @intFromEnum(abi.AllocatorMode.caller_provided), 0);
    assertInteropPolicyByteValue("allocator_mode.kernel_heap", @intFromEnum(abi.AllocatorMode.kernel_heap), 1);
    assertInteropPolicyByteValue("allocator_mode.arena", @intFromEnum(abi.AllocatorMode.arena), 2);
    assertInteropPolicyByteValue("unsafe_scope.none", @intFromEnum(abi.UnsafeScope.none), 0);
    assertInteropPolicyByteValue("unsafe_scope.volatile_mmio", @intFromEnum(abi.UnsafeScope.volatile_mmio), 1);
    assertInteropPolicyByteValue("unsafe_scope.raw_pointer_bridge", @intFromEnum(abi.UnsafeScope.raw_pointer_bridge), 2);
    assertUnsafeScopeTagParity();
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
    assertInteropPolicyModeValues();
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

pub fn assertListHeadRefLayout() void {
    assertSize(abi.ListHeadRef, @sizeOf(usize) * 2);
    assertAlign(abi.ListHeadRef, @alignOf(usize));
    assertFieldType(abi.ListHeadRef, "next_addr", usize);
    assertFieldType(abi.ListHeadRef, "prev_addr", usize);
    assertOffset(abi.ListHeadRef, "next_addr", 0);
    assertOffset(abi.ListHeadRef, "prev_addr", @sizeOf(usize));
}

pub fn assertListViewLayout() void {
    assertSize(abi.ListView, @sizeOf(usize) + 8);
    assertAlign(abi.ListView, @alignOf(usize));
    assertFieldType(abi.ListView, "head_addr", usize);
    assertFieldType(abi.ListView, "max_nodes", u32);
    assertFieldType(abi.ListView, "reserved", u32);
    assertOffset(abi.ListView, "head_addr", 0);
    assertOffset(abi.ListView, "max_nodes", @sizeOf(usize));
    assertOffset(abi.ListView, "reserved", @sizeOf(usize) + 4);
}

pub fn assertListSummaryLayout() void {
    assertSize(abi.ListSummary, 8);
    assertAlign(abi.ListSummary, 4);
    assertFieldType(abi.ListSummary, "length", u32);
    assertFieldType(abi.ListSummary, "flags", u32);
    assertOffset(abi.ListSummary, "length", 0);
    assertOffset(abi.ListSummary, "flags", 4);
}

pub fn assertHListHeadRefLayout() void {
    assertSize(abi.HListHeadRef, @sizeOf(usize));
    assertAlign(abi.HListHeadRef, @alignOf(usize));
    assertFieldType(abi.HListHeadRef, "first_addr", usize);
    assertOffset(abi.HListHeadRef, "first_addr", 0);
}

pub fn assertHListNodeRefLayout() void {
    assertSize(abi.HListNodeRef, @sizeOf(usize) * 2);
    assertAlign(abi.HListNodeRef, @alignOf(usize));
    assertFieldType(abi.HListNodeRef, "next_addr", usize);
    assertFieldType(abi.HListNodeRef, "pprev_addr", usize);
    assertOffset(abi.HListNodeRef, "next_addr", 0);
    assertOffset(abi.HListNodeRef, "pprev_addr", @sizeOf(usize));
}

pub fn assertHListViewLayout() void {
    assertSize(abi.HListView, @sizeOf(usize) + 8);
    assertAlign(abi.HListView, @alignOf(usize));
    assertFieldType(abi.HListView, "head_addr", usize);
    assertFieldType(abi.HListView, "max_nodes", u32);
    assertFieldType(abi.HListView, "reserved", u32);
    assertOffset(abi.HListView, "head_addr", 0);
    assertOffset(abi.HListView, "max_nodes", @sizeOf(usize));
    assertOffset(abi.HListView, "reserved", @sizeOf(usize) + 4);
}

pub fn assertHListSummaryLayout() void {
    assertSize(abi.HListSummary, 8);
    assertAlign(abi.HListSummary, 4);
    assertFieldType(abi.HListSummary, "length", u32);
    assertFieldType(abi.HListSummary, "flags", u32);
    assertOffset(abi.HListSummary, "length", 0);
    assertOffset(abi.HListSummary, "flags", 4);
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
        assertBoundaryHeaderLayout();
        assertExportStatusLayout();
        assertInteropPolicyLayout();
        assertMmioRangeLayout();
        assertBitmapViewLayout();
        assertCpuMaskViewLayout();
        assertListHeadRefLayout();
        assertListViewLayout();
        assertListSummaryLayout();
        assertHListHeadRefLayout();
        assertHListNodeRefLayout();
        assertHListViewLayout();
        assertHListSummaryLayout();
        assertRbtreeRootViewLayout();
    }
}
