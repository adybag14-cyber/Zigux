const std = @import("std");

pub const CpuMask = struct {
    values: []bool,

    pub fn deinit(self: CpuMask, allocator: std.mem.Allocator) void {
        allocator.free(self.values);
    }

    pub fn countSet(self: CpuMask) usize {
        return countPossibleCpus(self.values);
    }
};

pub const ParseCpuMaskError = error{
    EmptyCpuRange,
    InvalidCpuRange,
};

fn isDelimiter(byte: u8) bool {
    return byte == ',' or byte == '\n' or byte == '\r';
}

fn parseRangeToken(token: []const u8) ParseCpuMaskError!struct { start: usize, end: usize } {
    if (token.len == 0) {
        return error.InvalidCpuRange;
    }

    if (std.mem.indexOfScalar(u8, token, '-')) |dash_index| {
        const start_text = token[0..dash_index];
        const end_text = token[dash_index + 1 ..];
        if (start_text.len == 0 or end_text.len == 0) {
            return error.InvalidCpuRange;
        }

        const start = std.fmt.parseUnsigned(usize, start_text, 10) catch return error.InvalidCpuRange;
        const end = std.fmt.parseUnsigned(usize, end_text, 10) catch return error.InvalidCpuRange;
        if (start > end) {
            return error.InvalidCpuRange;
        }

        return .{ .start = start, .end = end };
    }

    const cpu = std.fmt.parseUnsigned(usize, token, 10) catch return error.InvalidCpuRange;
    return .{ .start = cpu, .end = cpu };
}

pub fn parseCpuMaskString(allocator: std.mem.Allocator, input: []const u8) !CpuMask {
    var mask = std.ArrayList(bool).empty;
    errdefer mask.deinit(allocator);

    var saw_range = false;
    var cursor: usize = 0;
    while (cursor < input.len) {
        while (cursor < input.len and isDelimiter(input[cursor])) : (cursor += 1) {}
        if (cursor >= input.len) {
            break;
        }

        const token_start = cursor;
        while (cursor < input.len and !isDelimiter(input[cursor])) : (cursor += 1) {}
        const token = input[token_start..cursor];
        const range = try parseRangeToken(token);
        saw_range = true;

        const previous_len = mask.items.len;
        if (range.end + 1 > previous_len) {
            try mask.resize(allocator, range.end + 1);
            @memset(mask.items[previous_len..], false);
        }
        @memset(mask.items[range.start .. range.end + 1], true);
    }

    if (!saw_range) {
        return error.EmptyCpuRange;
    }

    return .{
        .values = try mask.toOwnedSlice(allocator),
    };
}

pub fn countPossibleCpus(mask: []const bool) usize {
    var count: usize = 0;
    for (mask) |present| {
        if (present) {
            count += 1;
        }
    }
    return count;
}

test "parseCpuMaskString expands single CPUs and ranges into a dense bool mask" {
    const parsed = try parseCpuMaskString(std.testing.allocator, "0-2,4,7-8");
    defer parsed.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 9), parsed.values.len);
    try std.testing.expect(parsed.values[0]);
    try std.testing.expect(parsed.values[1]);
    try std.testing.expect(parsed.values[2]);
    try std.testing.expect(!parsed.values[3]);
    try std.testing.expect(parsed.values[4]);
    try std.testing.expect(!parsed.values[5]);
    try std.testing.expect(!parsed.values[6]);
    try std.testing.expect(parsed.values[7]);
    try std.testing.expect(parsed.values[8]);
    try std.testing.expectEqual(@as(usize, 6), parsed.countSet());
}

test "parseCpuMaskString tolerates repeated delimiters and newline-terminated masks" {
    const parsed = try parseCpuMaskString(std.testing.allocator, "\n0-1,,4\r\n6\n");
    defer parsed.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 7), parsed.values.len);
    try std.testing.expect(parsed.values[0]);
    try std.testing.expect(parsed.values[1]);
    try std.testing.expect(!parsed.values[2]);
    try std.testing.expect(!parsed.values[3]);
    try std.testing.expect(parsed.values[4]);
    try std.testing.expect(!parsed.values[5]);
    try std.testing.expect(parsed.values[6]);
}

test "parseCpuMaskString rejects empty and malformed ranges" {
    try std.testing.expectError(error.EmptyCpuRange, parseCpuMaskString(std.testing.allocator, ",\n\r"));
    try std.testing.expectError(error.InvalidCpuRange, parseCpuMaskString(std.testing.allocator, "3-1"));
    try std.testing.expectError(error.InvalidCpuRange, parseCpuMaskString(std.testing.allocator, "x"));
    try std.testing.expectError(error.InvalidCpuRange, parseCpuMaskString(std.testing.allocator, "1-"));
}
