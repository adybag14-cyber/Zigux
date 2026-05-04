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

pub const PerfBufferExplicitTarget = struct {
    cpu: usize,
    map_key: usize,
};

pub const ParseCpuMaskError = error{
    EmptyCpuRange,
    InvalidCpuRange,
    InputTooLarge,
};

pub const PlanPerfBufferExplicitTargetError = std.mem.Allocator.Error || error{
    CpuCountMismatch,
    InvalidCpuIndex,
    InvalidMapKey,
};

pub const cpu_mask_file_read_limit: usize = 127;

pub const ChunkReader = struct {
    context: ?*anyopaque,
    readFn: *const fn (context: ?*anyopaque, buffer: []u8) anyerror!?usize,
};

fn isDelimiter(byte: u8) bool {
    return byte == ',' or byte == '\n';
}

fn isLeadingWhitespace(byte: u8) bool {
    return byte == ' ' or byte == '\t' or byte == '\x0b' or byte == '\x0c' or byte == '\r';
}

fn trimLeadingTokenWhitespace(token: []const u8) []const u8 {
    var start: usize = 0;
    while (start < token.len and isLeadingWhitespace(token[start])) : (start += 1) {}
    return token[start..];
}

fn parseCpuIndex(token: []const u8) ParseCpuMaskError!usize {
    const parsed = std.fmt.parseInt(isize, token, 10) catch return error.InvalidCpuRange;
    if (parsed < 0) {
        return error.InvalidCpuRange;
    }

    return std.math.cast(usize, parsed) orelse return error.InvalidCpuRange;
}

fn parseRangeToken(token: []const u8) ParseCpuMaskError!struct { start: usize, end: usize } {
    if (token.len == 0) {
        return error.InvalidCpuRange;
    }

    if (std.mem.indexOfScalar(u8, token, '-')) |dash_index| {
        const start_text = trimLeadingTokenWhitespace(token[0..dash_index]);
        const end_text = trimLeadingTokenWhitespace(token[dash_index + 1 ..]);
        if (start_text.len == 0 or end_text.len == 0) {
            return error.InvalidCpuRange;
        }

        const start = try parseCpuIndex(start_text);
        const end = try parseCpuIndex(end_text);
        if (start > end) {
            return error.InvalidCpuRange;
        }

        return .{ .start = start, .end = end };
    }

    const cpu = try parseCpuIndex(trimLeadingTokenWhitespace(token));
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

        while (cursor < input.len and isLeadingWhitespace(input[cursor])) : (cursor += 1) {}
        if (cursor >= input.len) {
            return error.InvalidCpuRange;
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
        if (collected.items.len + count > cpu_mask_file_read_limit) {
            return error.InputTooLarge;
        }

        try collected.appendSlice(allocator, scratch[0..count]);
    }

    return parseCpuMaskString(allocator, collected.items);
}

pub fn derivePerfBufferAutoCpuCount(possible_cpu_count: usize, map_max_entries: u32) usize {
    if (map_max_entries != 0 and map_max_entries < possible_cpu_count) {
        return @as(usize, map_max_entries);
    }

    return possible_cpu_count;
}

pub fn isPerfBufferCpuOnlineEligible(cpu_index: usize, requested_cpu_count: i32, online_mask: []const bool) bool {
    if (requested_cpu_count > 0) {
        return true;
    }

    return cpu_index < online_mask.len and online_mask[cpu_index];
}

pub fn planPerfBufferAutoCpuIndices(
    allocator: std.mem.Allocator,
    possible_mask: []const bool,
    online_mask: []const bool,
    map_max_entries: u32,
) ![]usize {
    var planned = std.ArrayList(usize).empty;
    errdefer planned.deinit(allocator);

    const budget = derivePerfBufferAutoCpuCount(countPossibleCpus(possible_mask), map_max_entries);
    if (budget == 0) {
        return planned.toOwnedSlice(allocator);
    }

    for (possible_mask, 0..) |possible, cpu_index| {
        if (!possible) {
            continue;
        }
        if (!isPerfBufferCpuOnlineEligible(cpu_index, 0, online_mask)) {
            continue;
        }

        try planned.append(allocator, cpu_index);
        if (planned.items.len == budget) {
            break;
        }
    }

    return planned.toOwnedSlice(allocator);
}

fn parseExplicitPerfBufferCpu(value: i32) PlanPerfBufferExplicitTargetError!usize {
    if (value < 0) {
        return error.InvalidCpuIndex;
    }

    return @intCast(value);
}

fn parseExplicitPerfBufferMapKey(value: i32) PlanPerfBufferExplicitTargetError!usize {
    if (value < 0) {
        return error.InvalidMapKey;
    }

    return @intCast(value);
}

pub fn planPerfBufferExplicitTargets(
    allocator: std.mem.Allocator,
    cpus: []const i32,
    map_keys: []const i32,
) PlanPerfBufferExplicitTargetError![]PerfBufferExplicitTarget {
    if (cpus.len != map_keys.len) {
        return error.CpuCountMismatch;
    }

    var planned = std.ArrayList(PerfBufferExplicitTarget).empty;
    errdefer planned.deinit(allocator);

    try planned.ensureTotalCapacity(allocator, cpus.len);
    for (cpus, map_keys) |cpu, map_key| {
        planned.appendAssumeCapacity(.{
            .cpu = try parseExplicitPerfBufferCpu(cpu),
            .map_key = try parseExplicitPerfBufferMapKey(map_key),
        });
    }

    return planned.toOwnedSlice(allocator);
}

pub fn planPerfBufferCpuIndices(
    allocator: std.mem.Allocator,
    possible_mask: []const bool,
    online_mask: []const bool,
    requested_cpu_count: i32,
    map_max_entries: u32,
) ![]usize {
    if (requested_cpu_count > 0) {
        var planned = std.ArrayList(usize).empty;
        errdefer planned.deinit(allocator);

        const requested = @as(usize, @intCast(requested_cpu_count));
        try planned.ensureTotalCapacity(allocator, requested);
        for (0..requested) |cpu_index| {
            planned.appendAssumeCapacity(cpu_index);
        }
        return planned.toOwnedSlice(allocator);
    }

    return planPerfBufferAutoCpuIndices(allocator, possible_mask, online_mask, map_max_entries);
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

test "parseCpuMaskString follows the C helper's delimiter loop and sscanf-style token-leading whitespace" {
    const parsed = try parseCpuMaskString(std.testing.allocator, " \t0-1,,\x0b4\n\x0c6,\r8\n");
    defer parsed.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 9), parsed.values.len);
    try std.testing.expect(parsed.values[0]);
    try std.testing.expect(parsed.values[1]);
    try std.testing.expect(!parsed.values[2]);
    try std.testing.expect(!parsed.values[3]);
    try std.testing.expect(parsed.values[4]);
    try std.testing.expect(!parsed.values[5]);
    try std.testing.expect(parsed.values[6]);
    try std.testing.expect(!parsed.values[7]);
    try std.testing.expect(parsed.values[8]);
}

test "parseCpuMaskString accepts the C helper's signed decimal token syntax when values stay non-negative" {
    const parsed = try parseCpuMaskString(std.testing.allocator, "+0,+2-+3,+5\n");
    defer parsed.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 6), parsed.values.len);
    try std.testing.expect(parsed.values[0]);
    try std.testing.expect(!parsed.values[1]);
    try std.testing.expect(parsed.values[2]);
    try std.testing.expect(parsed.values[3]);
    try std.testing.expect(!parsed.values[4]);
    try std.testing.expect(parsed.values[5]);
}

test "parseCpuMaskString keeps sscanf-style whitespace after range dashes in parity with the C helper" {
    const parsed = try parseCpuMaskString(std.testing.allocator, "0- 3,+5-\t6,+8-\r9,+11-\x0c12\n");
    defer parsed.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 13), parsed.values.len);
    try std.testing.expect(parsed.values[0]);
    try std.testing.expect(parsed.values[1]);
    try std.testing.expect(parsed.values[2]);
    try std.testing.expect(parsed.values[3]);
    try std.testing.expect(!parsed.values[4]);
    try std.testing.expect(parsed.values[5]);
    try std.testing.expect(parsed.values[6]);
    try std.testing.expect(!parsed.values[7]);
    try std.testing.expect(parsed.values[8]);
    try std.testing.expect(parsed.values[9]);
    try std.testing.expect(!parsed.values[10]);
    try std.testing.expect(parsed.values[11]);
    try std.testing.expect(parsed.values[12]);
}

test "parseCpuMaskString rejects empty and malformed ranges" {
    try std.testing.expectError(error.EmptyCpuRange, parseCpuMaskString(std.testing.allocator, ",\n"));
    try std.testing.expectError(error.InvalidCpuRange, parseCpuMaskString(std.testing.allocator, ",\n\r"));
    try std.testing.expectError(error.InvalidCpuRange, parseCpuMaskString(std.testing.allocator, "3-1"));
    try std.testing.expectError(error.InvalidCpuRange, parseCpuMaskString(std.testing.allocator, "-1"));
    try std.testing.expectError(error.InvalidCpuRange, parseCpuMaskString(std.testing.allocator, "x"));
    try std.testing.expectError(error.InvalidCpuRange, parseCpuMaskString(std.testing.allocator, "1-"));
    try std.testing.expectError(error.InvalidCpuRange, parseCpuMaskString(std.testing.allocator, "0-1,4 \n"));
    try std.testing.expectError(error.InvalidCpuRange, parseCpuMaskString(std.testing.allocator, "0-1,\t"));
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
        .chunks = &.{ "+0-\t2,", "\n+4", ",6-\r7\n" },
    };
    var scratch: [8]u8 = undefined;
    const parsed = try parseCpuMaskFromReader(std.testing.allocator, &scratch, .{
        .context = &state,
        .readFn = ReaderState.read,
    });
    defer parsed.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 8), parsed.values.len);
    try std.testing.expectEqual(@as(usize, 6), parsed.countSet());
    try std.testing.expect(parsed.values[0]);
    try std.testing.expect(parsed.values[1]);
    try std.testing.expect(parsed.values[2]);
    try std.testing.expect(!parsed.values[3]);
    try std.testing.expect(parsed.values[4]);
    try std.testing.expect(!parsed.values[5]);
    try std.testing.expect(parsed.values[6]);
    try std.testing.expect(parsed.values[7]);
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

test "parseCpuMaskFromReader keeps the libbpf fixed-width cpu-mask ceiling explicit" {
    const ReaderState = struct {
        returned: bool = false,

        fn read(context: ?*anyopaque, buffer: []u8) !?usize {
            const self: *@This() = @ptrCast(@alignCast(context.?));
            if (self.returned) {
                return null;
            }

            self.returned = true;
            @memset(buffer, '1');
            return buffer.len;
        }
    };

    var state = ReaderState{};
    var scratch: [cpu_mask_file_read_limit + 1]u8 = undefined;

    try std.testing.expectError(error.InputTooLarge, parseCpuMaskFromReader(std.testing.allocator, &scratch, .{
        .context = &state,
        .readFn = ReaderState.read,
    }));
}

test "derivePerfBufferAutoCpuCount keeps perf-buffer auto sizing within the map budget" {
    try std.testing.expectEqual(@as(usize, 8), derivePerfBufferAutoCpuCount(8, 0));
    try std.testing.expectEqual(@as(usize, 4), derivePerfBufferAutoCpuCount(8, 4));
    try std.testing.expectEqual(@as(usize, 8), derivePerfBufferAutoCpuCount(8, 16));
}

test "isPerfBufferCpuOnlineEligible keeps the bounded online CPU predicate explicit" {
    const online = [_]bool{ true, false, true };

    try std.testing.expect(isPerfBufferCpuOnlineEligible(0, 0, &online));
    try std.testing.expect(!isPerfBufferCpuOnlineEligible(1, 0, &online));
    try std.testing.expect(isPerfBufferCpuOnlineEligible(2, -1, &online));
    try std.testing.expect(!isPerfBufferCpuOnlineEligible(3, 0, &online));
}

test "isPerfBufferCpuOnlineEligible bypasses the online mask when the caller pins a positive CPU budget" {
    const online = [_]bool{ false, false };

    try std.testing.expect(isPerfBufferCpuOnlineEligible(0, 2, &online));
    try std.testing.expect(isPerfBufferCpuOnlineEligible(3, 2, &online));
}

test "planPerfBufferAutoCpuIndices keeps auto-selected CPU routing pure and budget-bounded" {
    const possible = [_]bool{ true, true, false, true, true };
    const online = [_]bool{ false, true, true, false, true };

    const planned = try planPerfBufferAutoCpuIndices(std.testing.allocator, &possible, &online, 2);
    defer std.testing.allocator.free(planned);

    try std.testing.expectEqualSlices(usize, &.{ 1, 4 }, planned);
}

test "planPerfBufferAutoCpuIndices skips offline or truncated online candidates without widening into sysfs io" {
    const possible = [_]bool{ true, false, true, true };
    const short_online = [_]bool{ true, false };

    const planned = try planPerfBufferAutoCpuIndices(std.testing.allocator, &possible, &short_online, 0);
    defer std.testing.allocator.free(planned);

    try std.testing.expectEqualSlices(usize, &.{0}, planned);
}

test "planPerfBufferExplicitTargets keeps caller-supplied CPUs and map keys aligned without widening into perf FD routing" {
    const planned = try planPerfBufferExplicitTargets(std.testing.allocator, &.{ 4, 1, 7 }, &.{ 0, 2, 5 });
    defer std.testing.allocator.free(planned);

    try std.testing.expectEqual(@as(usize, 3), planned.len);
    try std.testing.expectEqual(@as(usize, 4), planned[0].cpu);
    try std.testing.expectEqual(@as(usize, 0), planned[0].map_key);
    try std.testing.expectEqual(@as(usize, 1), planned[1].cpu);
    try std.testing.expectEqual(@as(usize, 2), planned[1].map_key);
    try std.testing.expectEqual(@as(usize, 7), planned[2].cpu);
    try std.testing.expectEqual(@as(usize, 5), planned[2].map_key);
}

test "planPerfBufferExplicitTargets keeps mismatched and negative caller-supplied targets explicit" {
    try std.testing.expectError(
        error.CpuCountMismatch,
        planPerfBufferExplicitTargets(std.testing.allocator, &.{ 0, 1 }, &.{0}),
    );
    try std.testing.expectError(
        error.InvalidCpuIndex,
        planPerfBufferExplicitTargets(std.testing.allocator, &.{-1}, &.{0}),
    );
    try std.testing.expectError(
        error.InvalidMapKey,
        planPerfBufferExplicitTargets(std.testing.allocator, &.{0}, &.{-3}),
    );
}

test "planPerfBufferCpuIndices keeps caller-pinned positive CPU counts sequential without widening into routing parity" {
    const planned = try planPerfBufferCpuIndices(
        std.testing.allocator,
        &.{ false, false },
        &.{ false },
        3,
        1,
    );
    defer std.testing.allocator.free(planned);

    try std.testing.expectEqualSlices(usize, &.{ 0, 1, 2 }, planned);
}

test "planPerfBufferCpuIndices reuses bounded auto planning for zero or negative requested CPU counts" {
    const possible = [_]bool{ true, true, false, true, true };
    const online = [_]bool{ false, true, true, false, true };

    const zero_requested = try planPerfBufferCpuIndices(std.testing.allocator, &possible, &online, 0, 2);
    defer std.testing.allocator.free(zero_requested);
    try std.testing.expectEqualSlices(usize, &.{ 1, 4 }, zero_requested);

    const negative_requested = try planPerfBufferCpuIndices(std.testing.allocator, &possible, &online, -1, 2);
    defer std.testing.allocator.free(negative_requested);
    try std.testing.expectEqualSlices(usize, &.{ 1, 4 }, negative_requested);
}
