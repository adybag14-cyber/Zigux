const std = @import("std");

pub const LayoutError = error{
    SizeMismatch,
    AlignMismatch,
    OffsetMismatch,
};

pub fn expectSize(comptime T: type, expected: usize) LayoutError!void {
    if (@sizeOf(T) != expected) return error.SizeMismatch;
}

pub fn expectAlign(comptime T: type, expected: usize) LayoutError!void {
    if (@alignOf(T) != expected) return error.AlignMismatch;
}

pub fn expectOffset(comptime T: type, comptime field_name: []const u8, expected: usize) LayoutError!void {
    if (@offsetOf(T, field_name) != expected) return error.OffsetMismatch;
}

pub fn expectLayout(comptime T: type, size: usize, alignment: usize) LayoutError!void {
    try expectSize(T, size);
    try expectAlign(T, alignment);
}

pub fn expectFieldLayout(
    comptime T: type,
    comptime field_name: []const u8,
    expected_offset: usize,
) LayoutError!void {
    try expectOffset(T, field_name, expected_offset);
}

test "layout assert keeps starter header layouts explicit" {
    const BoundaryHeader = extern struct {
        size: u32,
        abi_version: u16,
        flags: u16,
    };

    const InteropPolicy = extern struct {
        panic_mode: u8,
        allocator_mode: u8,
        unsafe_scope: u8,
        reserved: u8,
    };

    try expectLayout(BoundaryHeader, 8, 4);
    try expectFieldLayout(BoundaryHeader, "size", 0);
    try expectFieldLayout(BoundaryHeader, "abi_version", 4);
    try expectFieldLayout(BoundaryHeader, "flags", 6);

    try expectLayout(InteropPolicy, 4, 1);
    try expectFieldLayout(InteropPolicy, "panic_mode", 0);
    try expectFieldLayout(InteropPolicy, "allocator_mode", 1);
    try expectFieldLayout(InteropPolicy, "unsafe_scope", 2);
    try expectFieldLayout(InteropPolicy, "reserved", 3);
}

test "layout assert reports mismatches without widening the call site" {
    const ExportStatus = extern struct {
        code: i32,
        facility: u16,
        flags: u16,
    };

    try expectLayout(ExportStatus, 8, 4);
    try std.testing.expectError(error.SizeMismatch, expectSize(ExportStatus, 12));
    try std.testing.expectError(error.AlignMismatch, expectAlign(ExportStatus, 2));
    try std.testing.expectError(error.OffsetMismatch, expectOffset(ExportStatus, "flags", 4));
}
