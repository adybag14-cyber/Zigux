const std = @import("std");
const options = @import("build_options");

const mmio_source = @embedFile(options.mmio_source_path);

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, mmio_source, needle) != null);
}

fn expectBefore(first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, mmio_source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, mmio_source, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "phase3 mmio zero-length ranges are valid metadata only" {
    try expectContains(
        \\fn validateRangeWindow(base_addr: usize, length: u32) PolicyError!void {
    );
    try expectContains("if (byte_len == 0) return;");
    try expectContains("rangeInteropPolicyByte(std.math.maxInt(usize), 0, 0, mmio_scope)");
    try expectContains("try std.testing.expectEqual(@as(u32, 0), empty.length);");
    try expectContains("try std.testing.expectEqual(@as(u32, 0), empty.stride);");
}

test "phase3 mmio range-bound accessors pass through the typed access gate" {
    try expectBefore(
        \\pub fn constPointerAt(comptime T: type, range: MmioRange, byte_offset: usize) PolicyError!*const volatile T {
    ,
        "try validateRangeTypedAccess(T, range, byte_offset);",
    );
    try expectContains(
        \\pub fn pointerAt(comptime T: type, range: MmioRange, byte_offset: usize) PolicyError!*volatile T {
        \\    try validateRangeTypedAccess(T, range, byte_offset);
        \\    return @ptrFromInt(try byteOffsetAddress(range.base_addr, byte_offset));
        \\}
    );
    try expectContains("return read(T, try constPointerAt(T, range, byte_offset));");
    try expectContains("write(T, try pointerAt(T, range, byte_offset), value);");
    try expectContains("return exchange(T, try pointerAt(T, range, byte_offset), value);");
    try expectContains("return writeMasked(T, try pointerAt(T, range, byte_offset), clear_mask, set_mask);");
}

test "phase3 mmio access windows reject non-empty access beyond range length" {
    try expectContains(
        \\fn rangeContainsAccessBytes(range: MmioRange, byte_offset: usize, byte_len: usize) bool {
    );
    try expectContains("const access_end = std.math.add(usize, byte_offset, byte_len) catch return false;");
    try expectContains("return access_end <= range_len;");
    try expectContains("try std.testing.expect(!rangeContainsAccessBytes(strided, 13, @sizeOf(u32)));");
    try expectContains("try std.testing.expect(!rangeContainsAccessBytes(strided, std.math.maxInt(usize), 4));");
}

test "phase3 mmio range test roster keeps denied accessors reviewable" {
    try expectContains(
        \\test "phase3 mmio helper keeps range-bound accessors inside the blessed MMIO window" {
    );
    try expectContains("try std.testing.expectError(error.InvalidInteropPolicy, constPointerAt(u16, range, 2));");
    try expectContains("try std.testing.expectError(error.InvalidInteropPolicy, writeAt(u32, range, 2, 1));");
    try expectContains("try std.testing.expectError(error.InvalidInteropPolicy, exchangeAt(u32, range, 14, 1));");
    try expectContains("try std.testing.expectError(error.InvalidInteropPolicy, writeMaskedAt(u32, range, 13, 0, 1));");
}
