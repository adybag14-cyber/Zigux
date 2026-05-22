const std = @import("std");

const cpu_mask = @import("cpu_mask.zig");

const ReaderContext = struct {
    input: []const u8,
    cursor: usize = 0,
};

const InjectedReadError = error{InjectedReadFailure};

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

fn readInjectedCpuMaskError(context: ?*anyopaque, buffer: []u8) InjectedReadError!?usize {
    _ = context;
    _ = buffer;
    return error.InjectedReadFailure;
}

test "phase8 cpu-mask helper entrypoints stay explicit" {
    try std.testing.expect(@hasDecl(cpu_mask, "CpuMask"));
    try std.testing.expect(@hasDecl(cpu_mask, "PossibleCpuSummary"));
    try std.testing.expect(@hasDecl(cpu_mask, "ParseCpuMaskError"));
    try std.testing.expect(@hasDecl(cpu_mask, "ChunkReader"));
    try std.testing.expect(@hasDecl(cpu_mask, "parseCpuMaskString"));
    try std.testing.expect(@hasDecl(cpu_mask, "parseCpuMaskFromReader"));
    try std.testing.expect(@hasDecl(cpu_mask, "summarizePossibleCpus"));
    try std.testing.expect(@hasDecl(cpu_mask, "summarizePossibleCpusFromString"));
    try std.testing.expect(@hasDecl(cpu_mask, "summarizePossibleCpusFromReader"));
    try std.testing.expect(@hasDecl(cpu_mask, "countPossibleCpus"));
    try std.testing.expect(@hasDecl(cpu_mask, "isOnlineCpuEligible"));
    try std.testing.expect(@hasDecl(cpu_mask, "derivePerfBufferAutoCpuCount"));
    try std.testing.expect(@hasDecl(cpu_mask, "derivePerfBufferAutoCpuCountFromString"));
    try std.testing.expect(@hasDecl(cpu_mask, "derivePerfBufferAutoCpuCountFromReader"));
}

test "phase8 cpu-mask helpers keep direct parse and summary outputs stable" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    var parsed = try cpu_mask.parseCpuMaskString(allocator, "0-2, 4\n");
    defer parsed.deinit(allocator);

    try std.testing.expectEqual(@as(usize, 4), parsed.countSet());
    try std.testing.expectEqualSlices(bool, &[_]bool{ true, true, true, false, true }, parsed.values);

    const summary = cpu_mask.summarizePossibleCpus(parsed.values);
    try std.testing.expectEqual(@as(usize, 5), summary.mask_bit_len);
    try std.testing.expectEqual(@as(usize, 4), summary.possible_cpu_count);
    try std.testing.expectEqual(@as(?usize, 4), summary.highest_cpu_index);
    try std.testing.expectEqual(@as(usize, 4), summary.deriveAutoCpuCount(0));
    try std.testing.expectEqual(@as(usize, 2), cpu_mask.derivePerfBufferAutoCpuCount(summary.possible_cpu_count, 2));
    try std.testing.expectEqual(@as(usize, 4), cpu_mask.derivePerfBufferAutoCpuCount(summary.possible_cpu_count, 99));

    try std.testing.expect(cpu_mask.isOnlineCpuEligible(parsed.values, 0));
    try std.testing.expect(!cpu_mask.isOnlineCpuEligible(parsed.values, 3));
    try std.testing.expect(!cpu_mask.isOnlineCpuEligible(parsed.values, 9));
}

test "phase8 cpu-mask helpers keep signed-token and dash-whitespace parity explicit" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    var parsed = try cpu_mask.parseCpuMaskString(allocator, "\x0b0-\x0c3,+5-\t6,+8-\n9\n");
    defer parsed.deinit(allocator);
    try std.testing.expectEqual(@as(usize, 8), cpu_mask.countPossibleCpus(parsed.values));
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

    try std.testing.expectError(error.InvalidCpuRange, cpu_mask.parseCpuMaskString(allocator, "0 -3"));
    try std.testing.expectError(error.InvalidCpuRange, cpu_mask.parseCpuMaskString(allocator, "+5 \t-6"));
}

test "phase8 cpu-mask helpers keep string-backed summaries and auto-count outputs stable" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    const summary = try cpu_mask.summarizePossibleCpusFromString(allocator, " 1-2, 5\n");
    try std.testing.expectEqual(@as(usize, 6), summary.mask_bit_len);
    try std.testing.expectEqual(@as(usize, 3), summary.possible_cpu_count);
    try std.testing.expectEqual(@as(?usize, 5), summary.highest_cpu_index);

    try std.testing.expectEqual(
        @as(usize, 2),
        try cpu_mask.derivePerfBufferAutoCpuCountFromString(allocator, "1-2, 5\n", 2),
    );
    try std.testing.expectEqual(
        @as(usize, 3),
        try cpu_mask.derivePerfBufferAutoCpuCountFromString(allocator, "1-2, 5\n", 9),
    );
}

test "phase8 cpu-mask helpers keep reader-backed summaries and auto-count outputs stable" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    var scratch: [3]u8 = undefined;

    var summary_context = ReaderContext{ .input = "1,3-4\n" };
    const summary_reader = cpu_mask.ChunkReader{
        .context = &summary_context,
        .readFn = readCpuMaskChunks,
    };
    const summary = try cpu_mask.summarizePossibleCpusFromReader(allocator, scratch[0..], summary_reader);
    try std.testing.expectEqual(@as(usize, 5), summary.mask_bit_len);
    try std.testing.expectEqual(@as(usize, 3), summary.possible_cpu_count);
    try std.testing.expectEqual(@as(?usize, 4), summary.highest_cpu_index);

    var auto_context = ReaderContext{ .input = "0-1,4\n" };
    const auto_reader = cpu_mask.ChunkReader{
        .context = &auto_context,
        .readFn = readCpuMaskChunks,
    };
    try std.testing.expectEqual(
        @as(usize, 3),
        try cpu_mask.derivePerfBufferAutoCpuCountFromReader(allocator, scratch[0..], auto_reader, 0),
    );
}

test "phase8 cpu-mask helpers keep delimiter-heavy reader inputs and injected read errors explicit" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    var direct = try cpu_mask.parseCpuMaskString(allocator, ",,\n\t0,\r\n2-3\n");
    defer direct.deinit(allocator);
    try std.testing.expectEqualSlices(bool, &[_]bool{ true, false, true, true }, direct.values);

    var scratch: [2]u8 = undefined;
    var chunked_context = ReaderContext{ .input = ",,\n\t0,\r\n2-3\n" };
    const chunked_reader = cpu_mask.ChunkReader{
        .context = &chunked_context,
        .readFn = readCpuMaskChunks,
    };
    var chunked = try cpu_mask.parseCpuMaskFromReader(allocator, scratch[0..], chunked_reader);
    defer chunked.deinit(allocator);
    try std.testing.expectEqualSlices(bool, direct.values, chunked.values);

    var summary_context = ReaderContext{ .input = ",,\n\t0,\r\n2-3\n" };
    const summary_reader = cpu_mask.ChunkReader{
        .context = &summary_context,
        .readFn = readCpuMaskChunks,
    };
    const summary = try cpu_mask.summarizePossibleCpusFromReader(allocator, scratch[0..], summary_reader);
    try std.testing.expectEqual(@as(usize, 4), summary.mask_bit_len);
    try std.testing.expectEqual(@as(usize, 3), summary.possible_cpu_count);
    try std.testing.expectEqual(@as(?usize, 3), summary.highest_cpu_index);

    const failing_reader = cpu_mask.ChunkReader{
        .context = null,
        .readFn = readInjectedCpuMaskError,
    };
    try std.testing.expectError(
        error.InjectedReadFailure,
        cpu_mask.parseCpuMaskFromReader(allocator, scratch[0..], failing_reader),
    );
    try std.testing.expectError(
        error.InjectedReadFailure,
        cpu_mask.summarizePossibleCpusFromReader(allocator, scratch[0..], failing_reader),
    );
    try std.testing.expectError(
        error.InjectedReadFailure,
        cpu_mask.derivePerfBufferAutoCpuCountFromReader(allocator, scratch[0..], failing_reader, 1),
    );
}

test "phase8 cpu-mask helpers keep invalid direct and reader-backed inputs fail-closed" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    try std.testing.expectError(error.InvalidCpuRange, cpu_mask.parseCpuMaskString(allocator, "4-2"));
    try std.testing.expectError(error.InvalidCpuRange, cpu_mask.parseCpuMaskString(allocator, "+"));
    try std.testing.expectError(error.InvalidCpuRange, cpu_mask.summarizePossibleCpusFromString(allocator, "0,+\n"));
    try std.testing.expectError(
        error.InvalidCpuRange,
        cpu_mask.derivePerfBufferAutoCpuCountFromString(allocator, "0,+\n", 1),
    );

    var scratch: [3]u8 = undefined;

    var malformed_context = ReaderContext{ .input = "0,+\n" };
    const malformed_reader = cpu_mask.ChunkReader{
        .context = &malformed_context,
        .readFn = readCpuMaskChunks,
    };
    try std.testing.expectError(
        error.InvalidCpuRange,
        cpu_mask.parseCpuMaskFromReader(allocator, scratch[0..], malformed_reader),
    );

    const empty_reader = cpu_mask.ChunkReader{
        .context = null,
        .readFn = readZeroCpuMaskChunks,
    };
    try std.testing.expectError(
        error.EmptyReadBuffer,
        cpu_mask.parseCpuMaskFromReader(allocator, scratch[0..0], empty_reader),
    );
    try std.testing.expectError(
        error.EmptyReadChunk,
        cpu_mask.parseCpuMaskFromReader(allocator, scratch[0..], empty_reader),
    );

    const invalid_count_reader = cpu_mask.ChunkReader{
        .context = null,
        .readFn = readTooManyCpuMaskChunks,
    };
    try std.testing.expectError(
        error.InvalidReadCount,
        cpu_mask.parseCpuMaskFromReader(allocator, scratch[0..], invalid_count_reader),
    );
}
