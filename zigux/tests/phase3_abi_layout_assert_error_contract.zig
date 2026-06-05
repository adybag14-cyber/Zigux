const std = @import("std");

fn readLayoutAssertSource(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        "zigux/helpers/layout_assert.zig",
        allocator,
        .limited(256 * 1024),
    );
}

fn requireContains(source: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn requireOrdered(source: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, source, before) orelse return error.TestUnexpectedResult;
    const after_index = std.mem.indexOf(u8, source, after) orelse return error.TestUnexpectedResult;
    try std.testing.expect(before_index < after_index);
}

test "phase3 layout assert helpers expose fail-closed error tags" {
    const source = try readLayoutAssertSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try requireContains(source, "pub const LayoutError = error{");
    try requireContains(source, "SizeMismatch");
    try requireContains(source, "AlignMismatch");
    try requireContains(source, "OffsetMismatch");

    try requireOrdered(source, "SizeMismatch", "AlignMismatch");
    try requireOrdered(source, "AlignMismatch", "OffsetMismatch");
}

test "phase3 layout assert primitive checks return stable mismatch errors" {
    const source = try readLayoutAssertSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try requireContains(source, "pub fn expectSize(comptime T: type, expected: usize) LayoutError!void");
    try requireContains(source, "if (@sizeOf(T) != expected) return error.SizeMismatch;");
    try requireContains(source, "pub fn expectAlign(comptime T: type, expected: usize) LayoutError!void");
    try requireContains(source, "if (@alignOf(T) != expected) return error.AlignMismatch;");
    try requireContains(source, "pub fn expectOffset(comptime T: type, comptime field_name: []const u8, expected: usize) LayoutError!void");
    try requireContains(source, "if (@offsetOf(T, field_name) != expected) return error.OffsetMismatch;");
}

test "phase3 layout assert aggregate helpers preserve size-align-field ordering" {
    const source = try readLayoutAssertSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try requireContains(source, "pub fn expectLayout(comptime T: type, size: usize, alignment: usize) LayoutError!void");
    try requireContains(source, "pub fn expectFieldLayout(");
    try requireOrdered(source, "try expectSize(T, size);", "try expectAlign(T, alignment);");
    try requireOrdered(source, "try expectSize(T, size);", "pub fn expectFieldLayout(");
    try requireOrdered(source, "try expectAlign(T, alignment);", "pub fn expectFieldLayout(");
    try requireContains(source, "try expectOffset(T, field_name, expected_offset);");
}

test "phase3 published ABI layout packet keeps broad substrate assertions wired" {
    const source = try readLayoutAssertSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try requireContains(source, "pub fn assertPublishedAbiLayouts() LayoutError!void");
    try requireOrdered(source, "try assertBoundaryHeaderLayout();", "try assertExportStatusLayout();");
    try requireOrdered(source, "try assertExportStatusLayout();", "try assertInteropPolicyLayout();");
    try requireOrdered(source, "try assertInteropPolicyLayout();", "try assertMmioRangeLayout();");
    try requireOrdered(source, "try assertMmioRangeLayout();", "try assertRbtreeRootViewLayout();");
    try requireOrdered(source, "try assertRbtreeRootViewLayout();", "try assertNotifierBlockLayout();");
    try requireOrdered(source, "try assertNotifierBlockLayout();", "try assertListHeadLayout();");
    try requireOrdered(source, "try assertListHeadLayout();", "try assertHListHeadLayout();");
    try requireOrdered(
        source,
        "try assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowViewLayout();",
        "try assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummaryLayout();",
    );
}
