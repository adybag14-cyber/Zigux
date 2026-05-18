const std = @import("std");

pub const ParseIntArrayResult = struct {
    storage: []i32,

    pub fn deinit(self: *ParseIntArrayResult, allocator: std.mem.Allocator) void {
        if (self.storage.len != 0) {
            allocator.free(self.storage);
        }
        self.* = .{ .storage = &.{} };
    }

    pub fn count(self: *const ParseIntArrayResult) usize {
        return if (self.storage.len == 0) 0 else @intCast(self.storage[0]);
    }

    pub fn values(self: *const ParseIntArrayResult) []const i32 {
        return if (self.storage.len <= 1) &.{} else self.storage[1..];
    }
};

fn cStringPrefix(text: []const u8) []const u8 {
    return text[0 .. std.mem.indexOfScalar(u8, text, 0) orelse text.len];
}

const RangeParse = struct {
    lower: i32,
    upper: i32,
    is_range: bool,
};

fn parseLeadingInt(text: []const u8) ?struct { value: i32, consumed: usize } {
    if (text.len == 0) return null;

    var index: usize = 0;
    if (text[index] == '+' or text[index] == '-') {
        index += 1;
    }

    if (index >= text.len) return null;

    var base: u8 = 10;
    if (text[index] == '0') {
        if (index + 1 < text.len and (text[index + 1] == 'x' or text[index + 1] == 'X')) {
            base = 16;
            index += 2;
        } else {
            base = 8;
        }
    }

    const digits_start = index;
    while (index < text.len) : (index += 1) {
        _ = std.fmt.charToDigit(text[index], base) catch break;
    }
    if (index == digits_start) return null;

    const value = std.fmt.parseInt(i32, text[0..index], 0) catch return null;
    return .{ .value = value, .consumed = index };
}

fn parseTokenOrRange(token: []const u8) ?RangeParse {
    const first = parseLeadingInt(token) orelse return null;

    if (first.value >= 0 and first.consumed < token.len and token[first.consumed] == '-') {
        const upper = parseLeadingInt(token[first.consumed + 1 ..]) orelse return .{
            .lower = first.value,
            .upper = first.value,
            .is_range = false,
        };
        if (upper.consumed != token.len - first.consumed - 1) {
            return .{
                .lower = first.value,
                .upper = first.value,
                .is_range = false,
            };
        }
        if (upper.value < first.value) return null;
        return .{
            .lower = first.value,
            .upper = upper.value,
            .is_range = true,
        };
    }

    return .{
        .lower = first.value,
        .upper = first.value,
        .is_range = false,
    };
}

fn countTokenValues(token: []const u8) ?usize {
    const parsed = parseTokenOrRange(token) orelse return null;
    if (!parsed.is_range) return 1;
    return @as(usize, @intCast(parsed.upper - parsed.lower)) + 1;
}

fn fillTokenValues(token: []const u8, dest: []i32) ?usize {
    const parsed = parseTokenOrRange(token) orelse return null;
    if (!parsed.is_range) {
        dest[0] = parsed.lower;
        return 1;
    }

    var written: usize = 0;
    var value = parsed.lower;
    while (value <= parsed.upper) : (value += 1) {
        dest[written] = value;
        written += 1;
    }
    return written;
}

pub fn parseIntArray(
    allocator: std.mem.Allocator,
    text: []const u8,
    count: usize,
) !ParseIntArrayResult {
    _ = count;
    const current = cStringPrefix(text);
    var cursor = std.mem.tokenizeScalar(u8, current, ',');
    var parsed_count: usize = 0;

    while (cursor.next()) |token| {
        const trimmed = std.mem.trim(u8, token, " \t\r\n");
        const len = countTokenValues(trimmed) orelse break;
        parsed_count += len;
    }

    if (parsed_count == 0) return error.NotFound;

    const storage_len = try std.math.add(usize, parsed_count, 1);
    var storage = try allocator.alloc(i32, storage_len);
    errdefer allocator.free(storage);
    storage[0] = @intCast(parsed_count);

    var writer: usize = 1;
    cursor = std.mem.tokenizeScalar(u8, current, ',');
    while (cursor.next()) |token| {
        const trimmed = std.mem.trim(u8, token, " \t\r\n");
        const written = fillTokenValues(trimmed, storage[writer..]) orelse break;
        writer += written;
    }

    std.debug.assert(writer == storage_len);
    return .{ .storage = storage };
}

pub fn parse_int_array(
    allocator: std.mem.Allocator,
    text: []const u8,
    count: usize,
) !ParseIntArrayResult {
    return parseIntArray(allocator, text, count);
}

test "parseIntArray counts values first and preserves caller-owned storage" {
    var result = try parseIntArray(std.testing.allocator, "1,3-5,-7,0x10", 0);
    defer result.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 6), result.count());
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 3, 4, 5, -7, 16 }, result.values());
    try std.testing.expectEqual(@as(i32, 6), result.storage[0]);
}

test "parseIntArray stops at invalid trailing content but keeps parsed prefix" {
    var result = try parse_int_array(std.testing.allocator, "2,4-5,broken", 999);
    defer result.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 3), result.count());
    try std.testing.expectEqualSlices(i32, &[_]i32{ 2, 4, 5 }, result.values());
}

test "parseIntArray keeps the first NUL as the exported boundary" {
    const input = [_]u8{ '7', ',', '9', 0, ',', '1', '1' };
    var result = try parseIntArray(std.testing.allocator, &input, input.len);
    defer result.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 2), result.count());
    try std.testing.expectEqualSlices(i32, &[_]i32{ 7, 9 }, result.values());
}

test "parseIntArray reports no entry when nothing parseable is present" {
    try std.testing.expectError(error.NotFound, parseIntArray(std.testing.allocator, "broken", 0));
    try std.testing.expectError(error.NotFound, parseIntArray(std.testing.allocator, "", 0));
}

test "parseIntArray keeps teardown idempotent" {
    var result = try parseIntArray(std.testing.allocator, "8,10-11", 0);
    result.deinit(std.testing.allocator);
    result.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 0), result.count());
    try std.testing.expectEqual(@as(usize, 0), result.storage.len);
}
