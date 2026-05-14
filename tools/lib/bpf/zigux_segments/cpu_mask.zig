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

fn isTokenWhitespace(byte: u8) bool {
    return byte == ' ' or byte == '\t' or byte == '\r';
}

fn skipTokenWhitespace(text: []const u8, start: usize) usize {
    var idx = start;
    while (idx < text.len and isTokenWhitespace(text[idx])) : (idx += 1) {}
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
    var cursor = skipTokenWhitespace(text, 0);
    const start_prefix = try parseUnsignedPrefix(text[cursor..]);
    const start = start_prefix.value;
    const after_start = cursor + start_prefix.consumed;

    var end = start;
    const cursor_after_token = skipTokenWhitespace(text, after_start);
    if (cursor_after_token < text.len and text[cursor_after_token] == '-') {
        cursor = cursor_after_token + 1;
        cursor = skipTokenWhitespace(text, cursor);

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
