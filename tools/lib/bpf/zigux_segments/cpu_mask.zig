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

pub const PossibleCpuSummary = struct {
    mask_bit_len: usize,
    possible_cpu_count: usize,
    highest_cpu_index: ?usize,

    pub fn deriveAutoCpuCount(self: PossibleCpuSummary, requested_cpu_count: usize) usize {
        return derivePerfBufferAutoCpuCount(self.possible_cpu_count, requested_cpu_count);
    }
};

pub const ParseCpuMaskError = error{
    EmptyCpuRange,
    InvalidCpuRange,
    EmptyReadBuffer,
    EmptyReadChunk,
    InvalidReadCount,
    OutOfMemory,
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

fn skipScanfWhitespace(text: []const u8, start: usize) usize {
    var idx = start;
    while (idx < text.len and std.ascii.isWhitespace(text[idx])) : (idx += 1) {}
    return idx;
}

fn parseUnsignedPrefix(text: []const u8) ParseCpuMaskError!ParsedUnsigned {
    if (text.len == 0) return error.InvalidCpuRange;

    var idx: usize = 0;
    if (text[idx] == '+') idx += 1;
    if (idx >= text.len or !std.ascii.isDigit(text[idx])) {
        return error.InvalidCpuRange;
    }

    var value: usize = 0;
    while (idx < text.len and std.ascii.isDigit(text[idx])) : (idx += 1) {
        value = std.math.mul(usize, value, 10) catch return error.InvalidCpuRange;
        value = std.math.add(usize, value, text[idx] - '0') catch return error.InvalidCpuRange;
    }

    return .{
        .value = value,
        .consumed = idx,
    };
}

fn parseRangePrefix(text: []const u8) ParseCpuMaskError!ParsedRange {
    var cursor = skipScanfWhitespace(text, 0);
    const start_prefix = try parseUnsignedPrefix(text[cursor..]);
    const start = start_prefix.value;
    const after_start = cursor + start_prefix.consumed;
    var end = start;

    if (after_start < text.len and text[after_start] == '-') {
        cursor = skipScanfWhitespace(text, after_start + 1);
        const end_prefix = try parseUnsignedPrefix(text[cursor..]);
        end = end_prefix.value;
        cursor += end_prefix.consumed;
        if (start > end) return error.InvalidCpuRange;
    } else {
        cursor = after_start;
    }

    return .{
        .start = start,
        .end = end,
        .consumed = cursor,
    };
}

pub fn parseCpuMaskString(allocator: std.mem.Allocator, input: []const u8) ParseCpuMaskError!CpuMask {
    var mask = std.ArrayList(bool).empty;
    errdefer mask.deinit(allocator);

    var saw_range = false;
    var cursor: usize = 0;
    while (cursor < input.len) {
        while (cursor < input.len and isDelimiter(input[cursor])) : (cursor += 1) {}
        if (cursor >= input.len) break;

        const range = try parseRangePrefix(input[cursor..]);
        if (range.consumed == 0) return error.InvalidCpuRange;
        const next_cursor = cursor + range.consumed;
        if (next_cursor < input.len and !isDelimiter(input[next_cursor])) {
            return error.InvalidCpuRange;
        }

        saw_range = true;
        const previous_len = mask.items.len;
        if (range.end + 1 > previous_len) {
            try mask.resize(allocator, range.end + 1);
            @memset(mask.items[previous_len..], false);
        }
        @memset(mask.items[range.start .. range.end + 1], true);
        cursor = next_cursor;
    }

    if (!saw_range) return error.EmptyCpuRange;
    return .{ .values = try mask.toOwnedSlice(allocator) };
}

pub fn parseCpuMaskFromReader(
    allocator: std.mem.Allocator,
    scratch: []u8,
    reader: ChunkReader,
) anyerror!CpuMask {
    if (scratch.len == 0) return error.EmptyReadBuffer;

    var collected = std.ArrayList(u8).empty;
    defer collected.deinit(allocator);

    while (true) {
        const maybe_count = try reader.readFn(reader.context, scratch);
        const count = maybe_count orelse break;
        if (count == 0) return error.EmptyReadChunk;
        if (count > scratch.len) return error.InvalidReadCount;

        try collected.appendSlice(allocator, scratch[0..count]);
    }

    return parseCpuMaskString(allocator, collected.items);
}

pub fn summarizePossibleCpus(mask: []const bool) PossibleCpuSummary {
    var possible_cpu_count: usize = 0;
    var highest_cpu_index: ?usize = null;
    for (mask, 0..) |present, index| {
        if (!present) continue;
        possible_cpu_count += 1;
        highest_cpu_index = index;
    }

    return .{
        .mask_bit_len = mask.len,
        .possible_cpu_count = possible_cpu_count,
        .highest_cpu_index = highest_cpu_index,
    };
}

pub fn summarizePossibleCpusFromReader(
    allocator: std.mem.Allocator,
    scratch: []u8,
    reader: ChunkReader,
) anyerror!PossibleCpuSummary {
    const parsed = try parseCpuMaskFromReader(allocator, scratch, reader);
    defer parsed.deinit(allocator);
    return summarizePossibleCpus(parsed.values);
}

pub fn countPossibleCpus(mask: []const bool) usize {
    return summarizePossibleCpus(mask).possible_cpu_count;
}

pub fn isOnlineCpuEligible(mask: []const bool, cpu_index: usize) bool {
    return cpu_index < mask.len and mask[cpu_index];
}

pub fn derivePerfBufferAutoCpuCount(total_possible_cpus: usize, requested_cpu_count: usize) usize {
    if (requested_cpu_count == 0 or requested_cpu_count > total_possible_cpus) {
        return total_possible_cpus;
    }
    return requested_cpu_count;
}

pub fn derivePerfBufferAutoCpuCountFromReader(
    allocator: std.mem.Allocator,
    scratch: []u8,
    reader: ChunkReader,
    requested_cpu_count: usize,
) anyerror!usize {
    const summary = try summarizePossibleCpusFromReader(allocator, scratch, reader);
    return summary.deriveAutoCpuCount(requested_cpu_count);
}

const ReaderContext = struct {
    input: []const u8,
    cursor: usize = 0,
};

fn readCpuMaskChunks(context: ?*anyopaque, buffer: []u8) anyerror!?usize {
    const typed_context: *ReaderContext = @ptrCast(@alignCast(context.?));
    if (typed_context.cursor >= typed_context.input.len) return null;

    const remaining = typed_context.input.len - typed_context.cursor;
    const count = @min(buffer.len, remaining);
    @memcpy(buffer[0..count], typed_context.input[typed_context.cursor .. typed_context.cursor + count]);
    typed_context.cursor += count;
    return count;
}

fn readZeroCpuMaskChunks(context: ?*anyopaque, buffer: []u8) anyerror!?usize {
    _ = context;
    _ = buffer;
    return 0;
}

fn readTooManyCpuMaskChunks(context: ?*anyopaque, buffer: []u8) anyerror!?usize {
    _ = context;
    return buffer.len + 1;
}

test "online cpu eligibility stays bounded to set bits" {
    const mask = [_]bool{ true, false, true, false };

    try std.testing.expect(isOnlineCpuEligible(&mask, 0));
    try std.testing.expect(!isOnlineCpuEligible(&mask, 1));
    try std.testing.expect(isOnlineCpuEligible(&mask, 2));
    try std.testing.expect(!isOnlineCpuEligible(&mask, 3));
}

test "online cpu eligibility keeps out-of-range probes non-claiming" {
    const mask = [_]bool{ false, true, true };

    try std.testing.expect(!isOnlineCpuEligible(&mask, 3));
    try std.testing.expect(!isOnlineCpuEligible(&mask, 9));
    try std.testing.expect(!isOnlineCpuEligible(&.{}, 0));
}

test "cpu-mask parser keeps stable direct summary outputs explicit" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    var parsed = try parseCpuMaskString(allocator, "0-2, 4\n");
    defer parsed.deinit(allocator);

    try std.testing.expectEqual(@as(usize, 4), parsed.countSet());
    try std.testing.expectEqualSlices(bool, &[_]bool{ true, true, true, false, true }, parsed.values);

    const summary = summarizePossibleCpus(parsed.values);
    try std.testing.expectEqual(@as(usize, 5), summary.mask_bit_len);
    try std.testing.expectEqual(@as(usize, 4), summary.possible_cpu_count);
    try std.testing.expectEqual(@as(?usize, 4), summary.highest_cpu_index);
    try std.testing.expectEqual(@as(usize, 4), summary.deriveAutoCpuCount(0));
    try std.testing.expectEqual(@as(usize, 2), derivePerfBufferAutoCpuCount(summary.possible_cpu_count, 2));
    try std.testing.expectEqual(@as(usize, 4), derivePerfBufferAutoCpuCount(summary.possible_cpu_count, 99));

    var spaced_plus = try parseCpuMaskString(allocator, " +0, 2- 3\n");
    defer spaced_plus.deinit(allocator);
    try std.testing.expectEqualSlices(bool, &[_]bool{ true, false, true, true }, spaced_plus.values);
    try std.testing.expectEqual(@as(usize, 3), countPossibleCpus(spaced_plus.values));

    const empty_summary = summarizePossibleCpus(&.{});
    try std.testing.expectEqual(@as(usize, 0), empty_summary.mask_bit_len);
    try std.testing.expectEqual(@as(usize, 0), empty_summary.possible_cpu_count);
    try std.testing.expectEqual(@as(?usize, null), empty_summary.highest_cpu_index);
    try std.testing.expectEqual(@as(usize, 0), empty_summary.deriveAutoCpuCount(3));
}

test "cpu-mask reader-backed helpers keep chunked summary outputs stable" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    var scratch: [3]u8 = undefined;

    var reader_context = ReaderContext{ .input = "1,3-4\n" };
    const reader = ChunkReader{
        .context = &reader_context,
        .readFn = readCpuMaskChunks,
    };
    const reader_summary = try summarizePossibleCpusFromReader(allocator, scratch[0..], reader);
    try std.testing.expectEqual(@as(usize, 5), reader_summary.mask_bit_len);
    try std.testing.expectEqual(@as(usize, 3), reader_summary.possible_cpu_count);
    try std.testing.expectEqual(@as(?usize, 4), reader_summary.highest_cpu_index);

    var auto_context = ReaderContext{ .input = "0-1,4\n" };
    const auto_reader = ChunkReader{
        .context = &auto_context,
        .readFn = readCpuMaskChunks,
    };
    try std.testing.expectEqual(
        @as(usize, 3),
        try derivePerfBufferAutoCpuCountFromReader(allocator, scratch[0..], auto_reader, 0),
    );

    var clamped_auto_context = ReaderContext{ .input = "2-4\n" };
    const clamped_auto_reader = ChunkReader{
        .context = &clamped_auto_context,
        .readFn = readCpuMaskChunks,
    };
    try std.testing.expectEqual(
        @as(usize, 3),
        try derivePerfBufferAutoCpuCountFromReader(allocator, scratch[0..], clamped_auto_reader, 9),
    );
}

test "cpu-mask parsing rejects invalid direct and reader-backed inputs" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    try std.testing.expectError(error.InvalidCpuRange, parseCpuMaskString(allocator, "4-2"));

    var scratch: [3]u8 = undefined;
    const empty_reader = ChunkReader{
        .context = null,
        .readFn = readZeroCpuMaskChunks,
    };
    try std.testing.expectError(
        error.EmptyReadBuffer,
        parseCpuMaskFromReader(allocator, scratch[0..0], empty_reader),
    );
    try std.testing.expectError(
        error.EmptyReadChunk,
        parseCpuMaskFromReader(allocator, scratch[0..], empty_reader),
    );

    const invalid_count_reader = ChunkReader{
        .context = null,
        .readFn = readTooManyCpuMaskChunks,
    };
    try std.testing.expectError(
        error.InvalidReadCount,
        parseCpuMaskFromReader(allocator, scratch[0..], invalid_count_reader),
    );
}
