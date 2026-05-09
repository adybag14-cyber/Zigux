const std = @import("std");

pub const CpuMask = struct {
    values: []bool,

    pub fn deinit(self: CpuMask, allocator: std.mem.Allocator) void {
        allocator.free(self.values);
    }

    pub fn countSet(self: CpuMask) usize {
        return countPossibleCpus(self.values);
    }

    pub fn highestSet(self: CpuMask) ?usize {
        return highestPossibleCpuIndex(self.values);
    }
};

pub const ParseCpuMaskError = error{
    EmptyCpuRange,
    InvalidCpuRange,
};

pub const ChunkReader = struct {
    context: ?*anyopaque,
    readFn: *const fn (context: ?*anyopaque, buffer: []u8) anyerror!?usize,
};

const ParsedUnsigned = struct {
    value: usize,
    consumed: usize,
};

const ParsedRange = struct {
    start: usize,
    end: usize,
    consumed: usize,
};

fn isDelimiter(byte: u8) bool {
    return byte == ',' or byte == '\n';
}

fn parseUnsignedPrefix(input: []const u8) ?ParsedUnsigned {
    var cursor: usize = 0;
    while (cursor < input.len and std.ascii.isDigit(input[cursor])) : (cursor += 1) {}
    if (cursor == 0) {
        return null;
    }

    const value = std.fmt.parseUnsigned(usize, input[0..cursor], 10) catch return null;
    return .{ .value = value, .consumed = cursor };
}

fn parseRangePrefix(input: []const u8) ParseCpuMaskError!ParsedRange {
    var cursor: usize = 0;
    while (cursor < input.len and std.ascii.isWhitespace(input[cursor])) : (cursor += 1) {}
    if (cursor >= input.len) {
        return error.InvalidCpuRange;
    }

    const parsed_start = parseUnsignedPrefix(input[cursor..]) orelse return error.InvalidCpuRange;
    const start = parsed_start.value;
    cursor += parsed_start.consumed;

    var end = start;
    if (cursor < input.len and input[cursor] == '-') {
        cursor += 1;
        while (cursor < input.len and std.ascii.isWhitespace(input[cursor])) : (cursor += 1) {}
        const parsed_end = parseUnsignedPrefix(input[cursor..]) orelse return error.InvalidCpuRange;
        end = parsed_end.value;
        cursor += parsed_end.consumed;
    }

    if (start > end) {
        return error.InvalidCpuRange;
    }

    return .{
        .start = start,
        .end = end,
        .consumed = cursor,
    };
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

        const range = try parseRangePrefix(input[cursor..]);
        cursor += range.consumed;
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

pub fn parseCpuMaskFromReader(
    allocator: std.mem.Allocator,
    scratch: []u8,
    reader: ChunkReader,
) anyerror!CpuMask {
    if (scratch.len == 0) {
        return error.EmptyReadBuffer;
    }

    var collected = std.ArrayList(u8).empty;
    defer collected.deinit(allocator);

    while (true) {
        const maybe_count = try reader.readFn(reader.context, scratch);
        const count = maybe_count orelse break;
        if (count == 0) {
            return error.EmptyReadChunk;
        }
        if (count > scratch.len) {
            return error.InvalidReadCount;
        }

        try collected.appendSlice(allocator, scratch[0..count]);
    }

    return parseCpuMaskString(allocator, collected.items);
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

pub fn highestPossibleCpuIndex(mask: []const bool) ?usize {
    var cursor = mask.len;
    while (cursor > 0) {
        cursor -= 1;
        if (mask[cursor]) {
            return cursor;
        }
    }
    return null;
}

pub fn possibleCpuCountFromString(allocator: std.mem.Allocator, input: []const u8) !usize {
    const parsed = try parseCpuMaskString(allocator, input);
    defer parsed.deinit(allocator);
    return parsed.countSet();
}

pub fn possibleCpuCountFromReader(
    allocator: std.mem.Allocator,
    scratch: []u8,
    reader: ChunkReader,
) anyerror!usize {
    const parsed = try parseCpuMaskFromReader(allocator, scratch, reader);
    defer parsed.deinit(allocator);
    return parsed.countSet();
}

pub fn highestPossibleCpuIndexFromString(
    allocator: std.mem.Allocator,
    input: []const u8,
) !?usize {
    const parsed = try parseCpuMaskString(allocator, input);
    defer parsed.deinit(allocator);
    return parsed.highestSet();
}

pub fn highestPossibleCpuIndexFromReader(
    allocator: std.mem.Allocator,
    scratch: []u8,
    reader: ChunkReader,
) anyerror!?usize {
    const parsed = try parseCpuMaskFromReader(allocator, scratch, reader);
    defer parsed.deinit(allocator);
    return parsed.highestSet();
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
    try std.testing.expectEqual(@as(?usize, 8), parsed.highestSet());
}

test "parseCpuMaskString tolerates repeated delimiters and newline-terminated masks" {
    const parsed = try parseCpuMaskString(std.testing.allocator, "\n0-1,,4\n6\n");
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

test "parseCpuMaskString keeps libbpf whitespace parity for direct input" {
    const parsed = try parseCpuMaskString(std.testing.allocator, "\r0-1,\t4\n6-7");
    defer parsed.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 8), parsed.values.len);
    try std.testing.expectEqual(@as(usize, 5), parsed.countSet());
    try std.testing.expect(parsed.values[0]);
    try std.testing.expect(parsed.values[1]);
    try std.testing.expect(!parsed.values[2]);
    try std.testing.expect(!parsed.values[3]);
    try std.testing.expect(parsed.values[4]);
    try std.testing.expect(!parsed.values[5]);
    try std.testing.expect(parsed.values[6]);
    try std.testing.expect(parsed.values[7]);
    try std.testing.expectEqual(@as(?usize, 7), parsed.highestSet());
}

test "parseCpuMaskString rejects empty and malformed ranges" {
    try std.testing.expectError(error.EmptyCpuRange, parseCpuMaskString(std.testing.allocator, ",\n"));
    try std.testing.expectError(error.InvalidCpuRange, parseCpuMaskString(std.testing.allocator, "3-1"));
    try std.testing.expectError(error.InvalidCpuRange, parseCpuMaskString(std.testing.allocator, "x"));
    try std.testing.expectError(error.InvalidCpuRange, parseCpuMaskString(std.testing.allocator, "1-"));
    try std.testing.expectError(error.InvalidCpuRange, parseCpuMaskString(std.testing.allocator, ",\r,"));
}

test "parseCpuMaskFromReader accepts chunked sysfs-style input" {
    const ReaderState = struct {
        chunks: []const []const u8,
        index: usize = 0,

        fn read(context: ?*anyopaque, buffer: []u8) !?usize {
            const self: *@This() = @ptrCast(@alignCast(context.?));
            if (self.index >= self.chunks.len) {
                return null;
            }

            const chunk = self.chunks[self.index];
            self.index += 1;
            std.mem.copyForwards(u8, buffer[0..chunk.len], chunk);
            return chunk.len;
        }
    };

    var state = ReaderState{
        .chunks = &.{ "0-2,", "4\n", "6\n" },
    };
    var scratch: [8]u8 = undefined;
    const parsed = try parseCpuMaskFromReader(std.testing.allocator, &scratch, .{
        .context = &state,
        .readFn = ReaderState.read,
    });
    defer parsed.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 7), parsed.values.len);
    try std.testing.expectEqual(@as(usize, 5), parsed.countSet());
    try std.testing.expect(parsed.values[0]);
    try std.testing.expect(parsed.values[1]);
    try std.testing.expect(parsed.values[2]);
    try std.testing.expect(!parsed.values[3]);
    try std.testing.expect(parsed.values[4]);
    try std.testing.expect(!parsed.values[5]);
    try std.testing.expect(parsed.values[6]);
}

test "parseCpuMaskFromReader keeps libbpf whitespace parity for chunked input" {
    const ReaderState = struct {
        chunks: []const []const u8,
        index: usize = 0,

        fn read(context: ?*anyopaque, buffer: []u8) !?usize {
            const self: *@This() = @ptrCast(@alignCast(context.?));
            if (self.index >= self.chunks.len) {
                return null;
            }

            const chunk = self.chunks[self.index];
            self.index += 1;
            std.mem.copyForwards(u8, buffer[0..chunk.len], chunk);
            return chunk.len;
        }
    };

    var state = ReaderState{
        .chunks = &.{ "0-2,\r", "4\n", "\t6\n" },
    };
    var scratch: [8]u8 = undefined;
    const parsed = try parseCpuMaskFromReader(std.testing.allocator, &scratch, .{
        .context = &state,
        .readFn = ReaderState.read,
    });
    defer parsed.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 7), parsed.values.len);
    try std.testing.expectEqual(@as(usize, 5), parsed.countSet());
    try std.testing.expect(parsed.values[0]);
    try std.testing.expect(parsed.values[1]);
    try std.testing.expect(parsed.values[2]);
    try std.testing.expect(!parsed.values[3]);
    try std.testing.expect(parsed.values[4]);
    try std.testing.expect(!parsed.values[5]);
    try std.testing.expect(parsed.values[6]);
}

test "possibleCpuCountFromString keeps libbpf_num_possible_cpus counting helper-only" {
    try std.testing.expectEqual(
        @as(usize, 6),
        try possibleCpuCountFromString(std.testing.allocator, "0-2,4,7-8"),
    );
    try std.testing.expectEqual(
        @as(usize, 5),
        try possibleCpuCountFromString(std.testing.allocator, "\r0-1,\t4\n6-7"),
    );
}

test "possibleCpuCountFromReader keeps chunked counting coupled to the existing parser" {
    const ReaderState = struct {
        chunks: []const []const u8,
        index: usize = 0,

        fn read(context: ?*anyopaque, buffer: []u8) !?usize {
            const self: *@This() = @ptrCast(@alignCast(context.?));
            if (self.index >= self.chunks.len) {
                return null;
            }

            const chunk = self.chunks[self.index];
            self.index += 1;
            std.mem.copyForwards(u8, buffer[0..chunk.len], chunk);
            return chunk.len;
        }
    };

    var state = ReaderState{
        .chunks = &.{ "0-1,", "4\n", "6-7\n" },
    };
    var scratch: [8]u8 = undefined;
    try std.testing.expectEqual(
        @as(usize, 5),
        try possibleCpuCountFromReader(std.testing.allocator, &scratch, .{
            .context = &state,
            .readFn = ReaderState.read,
        }),
    );
}

test "highestPossibleCpuIndex keeps sparse and empty masks explicit" {
    try std.testing.expectEqual(
        @as(?usize, 5),
        highestPossibleCpuIndex(&.{ false, true, false, true, false, true }),
    );
    try std.testing.expectEqual(@as(?usize, null), highestPossibleCpuIndex(&.{}));
}

test "highestPossibleCpuIndexFromString keeps highest active cpu lookup helper-only" {
    try std.testing.expectEqual(
        @as(?usize, 8),
        try highestPossibleCpuIndexFromString(std.testing.allocator, "0-2,4,7-8"),
    );
    try std.testing.expectEqual(
        @as(?usize, 7),
        try highestPossibleCpuIndexFromString(std.testing.allocator, "\r0-1,\t4\n6-7"),
    );
}

test "highestPossibleCpuIndexFromReader keeps chunked highest cpu lookup coupled to the parser" {
    const ReaderState = struct {
        chunks: []const []const u8,
        index: usize = 0,

        fn read(context: ?*anyopaque, buffer: []u8) !?usize {
            const self: *@This() = @ptrCast(@alignCast(context.?));
            if (self.index >= self.chunks.len) {
                return null;
            }

            const chunk = self.chunks[self.index];
            self.index += 1;
            std.mem.copyForwards(u8, buffer[0..chunk.len], chunk);
            return chunk.len;
        }
    };

    var state = ReaderState{
        .chunks = &.{ "0-1,", "4\n", "6-7\n" },
    };
    var scratch: [8]u8 = undefined;
    try std.testing.expectEqual(
        @as(?usize, 7),
        try highestPossibleCpuIndexFromReader(std.testing.allocator, &scratch, .{
            .context = &state,
            .readFn = ReaderState.read,
        }),
    );
}

test "possibleCpuCount helpers keep parser and reader contract failures explicit" {
    const ReaderState = struct {
        mode: enum { empty_chunk, oversized_chunk },

        fn read(context: ?*anyopaque, _: []u8) !?usize {
            const self: *@This() = @ptrCast(@alignCast(context.?));
            return switch (self.mode) {
                .empty_chunk => 0,
                .oversized_chunk => 9,
            };
        }
    };

    var empty_state = ReaderState{ .mode = .empty_chunk };
    var oversize_state = ReaderState{ .mode = .oversized_chunk };
    var scratch: [8]u8 = undefined;

    try std.testing.expectError(
        error.InvalidCpuRange,
        possibleCpuCountFromString(std.testing.allocator, "x"),
    );
    try std.testing.expectError(
        error.EmptyReadChunk,
        possibleCpuCountFromReader(std.testing.allocator, &scratch, .{
            .context = &empty_state,
            .readFn = ReaderState.read,
        }),
    );
    try std.testing.expectError(
        error.InvalidReadCount,
        possibleCpuCountFromReader(std.testing.allocator, &scratch, .{
            .context = &oversize_state,
            .readFn = ReaderState.read,
        }),
    );
    try std.testing.expectError(
        error.EmptyReadBuffer,
        possibleCpuCountFromReader(std.testing.allocator, &.{}, .{
            .context = &empty_state,
            .readFn = ReaderState.read,
        }),
    );
}

test "parseCpuMaskFromReader rejects invalid reader contracts" {
    const ReaderState = struct {
        mode: enum { empty_chunk, oversized_chunk },

        fn read(context: ?*anyopaque, _: []u8) !?usize {
            const self: *@This() = @ptrCast(@alignCast(context.?));
            return switch (self.mode) {
                .empty_chunk => 0,
                .oversized_chunk => 9,
            };
        }
    };

    var empty_state = ReaderState{ .mode = .empty_chunk };
    var oversize_state = ReaderState{ .mode = .oversized_chunk };
    var scratch: [8]u8 = undefined;

    try std.testing.expectError(error.EmptyReadChunk, parseCpuMaskFromReader(std.testing.allocator, &scratch, .{
        .context = &empty_state,
        .readFn = ReaderState.read,
    }));
    try std.testing.expectError(error.InvalidReadCount, parseCpuMaskFromReader(std.testing.allocator, &scratch, .{
        .context = &oversize_state,
        .readFn = ReaderState.read,
    }));
    try std.testing.expectError(error.EmptyReadBuffer, parseCpuMaskFromReader(std.testing.allocator, &.{}, .{
        .context = &empty_state,
        .readFn = ReaderState.read,
    }));
}
