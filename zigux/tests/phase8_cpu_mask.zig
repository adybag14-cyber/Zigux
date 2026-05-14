const std = @import("std");
const cpu_mask = @import("cpu_mask");

test "phase 8 cpu mask module imports cleanly" {
    _ = cpu_mask;
}

test "phase 8 cpu mask starter slice parses dense masks and counts possible CPUs" {
    const parsed = try cpu_mask.parseCpuMaskString(std.testing.allocator, "0-3,5,7-8");
    defer parsed.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 9), parsed.values.len);
    try std.testing.expectEqual(@as(usize, 7), parsed.countSet());
    try std.testing.expect(parsed.values[0]);
    try std.testing.expect(parsed.values[3]);
    try std.testing.expect(!parsed.values[4]);
    try std.testing.expect(parsed.values[5]);
    try std.testing.expect(!parsed.values[6]);
    try std.testing.expect(parsed.values[7]);
    try std.testing.expect(parsed.values[8]);
}

test "phase 8 cpu mask starter slice keeps the C delimiter loop bounded while still allowing sscanf-style leading whitespace" {
    const parsed = try cpu_mask.parseCpuMaskString(std.testing.allocator, "\n 0-1,\r4\n6\n");
    defer parsed.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 4), cpu_mask.countPossibleCpus(parsed.values));
    try std.testing.expect(parsed.values[0]);
    try std.testing.expect(parsed.values[1]);
    try std.testing.expect(parsed.values[4]);
    try std.testing.expect(parsed.values[6]);
    try std.testing.expectError(error.EmptyCpuRange, cpu_mask.parseCpuMaskString(std.testing.allocator, ",\n"));
    try std.testing.expectError(error.InvalidCpuRange, cpu_mask.parseCpuMaskString(std.testing.allocator, ",\n\r"));
    try std.testing.expectError(error.InvalidCpuRange, cpu_mask.parseCpuMaskString(std.testing.allocator, "2-1"));
    try std.testing.expectError(error.InvalidCpuRange, cpu_mask.parseCpuMaskString(std.testing.allocator, "cpu0"));
    try std.testing.expectError(error.InvalidCpuRange, cpu_mask.parseCpuMaskString(std.testing.allocator, "0-1,4 \n"));
    try std.testing.expectError(error.InvalidCpuRange, cpu_mask.parseCpuMaskString(std.testing.allocator, "0-1,\t"));
}

test "phase 8 cpu mask starter slice accepts plus-prefixed CPU tokens like the live C helper" {
    const parsed = try cpu_mask.parseCpuMaskString(std.testing.allocator, "+0,+2-+3,+5\n");
    defer parsed.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 4), cpu_mask.countPossibleCpus(parsed.values));
    try std.testing.expect(parsed.values[0]);
    try std.testing.expect(!parsed.values[1]);
    try std.testing.expect(parsed.values[2]);
    try std.testing.expect(parsed.values[3]);
    try std.testing.expect(!parsed.values[4]);
    try std.testing.expect(parsed.values[5]);
    try std.testing.expectError(error.InvalidCpuRange, cpu_mask.parseCpuMaskString(std.testing.allocator, "-1"));
}

test "phase 8 cpu mask starter slice keeps sscanf-style whitespace after range dashes in parity with the live C helper" {
    const parsed = try cpu_mask.parseCpuMaskString(std.testing.allocator, "\x0b0-\x0c3,+5-\t6,+8-\n9\n");
    defer parsed.deinit(std.testing.allocator);

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
    try std.testing.expectError(error.InvalidCpuRange, cpu_mask.parseCpuMaskString(std.testing.allocator, "0 -3"));
    try std.testing.expectError(error.InvalidCpuRange, cpu_mask.parseCpuMaskString(std.testing.allocator, "+5 \t-6"));
}

test "phase 8 cpu mask reader interface accepts chunked sysfs-style input" {
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
        .chunks = &.{ "\x0b+0-\x0c3", ",\t+5", "\n +7-\n+8\n" },
    };
    var scratch: [16]u8 = undefined;
    const parsed = try cpu_mask.parseCpuMaskFromReader(std.testing.allocator, &scratch, .{
        .context = &state,
        .readFn = ReaderState.read,
    });
    defer parsed.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 9), parsed.values.len);
    try std.testing.expectEqual(@as(usize, 7), parsed.countSet());
    try std.testing.expect(parsed.values[0]);
    try std.testing.expect(parsed.values[3]);
    try std.testing.expect(!parsed.values[4]);
    try std.testing.expect(parsed.values[5]);
    try std.testing.expect(!parsed.values[6]);
    try std.testing.expect(parsed.values[7]);
    try std.testing.expect(parsed.values[8]);
}

test "phase 8 cpu mask helper summarizes reader-backed possible CPUs without stepping into routing" {
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

    var state = ReaderState{ .chunks = &.{ "+0-1", ",4,\n7-8\n" } };
    var scratch: [16]u8 = undefined;
    const summary = try cpu_mask.summarizePossibleCpusFromReader(std.testing.allocator, &scratch, .{
        .context = &state,
        .readFn = ReaderState.read,
    });

    try std.testing.expectEqual(@as(usize, 9), summary.mask_bit_len);
    try std.testing.expectEqual(@as(usize, 5), summary.possible_cpu_count);
    try std.testing.expectEqual(@as(?usize, 8), summary.highest_cpu_index);
}

test "phase 8 cpu mask helper keeps empty summaries explicit for follow-on planner code" {
    const summary = cpu_mask.summarizePossibleCpus(&.{});

    try std.testing.expectEqual(@as(usize, 0), summary.mask_bit_len);
    try std.testing.expectEqual(@as(usize, 0), summary.possible_cpu_count);
    try std.testing.expectEqual(@as(?usize, null), summary.highest_cpu_index);
}

test "phase 8 cpu mask helper derives perf-buffer auto CPU sizing from reader-backed possible CPU counts" {
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

    var scratch: [16]u8 = undefined;
    const chunks = &.{ "0-2", ",5\n" };

    var default_state = ReaderState{ .chunks = chunks };
    try std.testing.expectEqual(@as(usize, 4), try cpu_mask.derivePerfBufferAutoCpuCountFromReader(
        std.testing.allocator,
        &scratch,
        .{ .context = &default_state, .readFn = ReaderState.read },
        0,
    ));

    var bounded_state = ReaderState{ .chunks = chunks };
    try std.testing.expectEqual(@as(usize, 2), try cpu_mask.derivePerfBufferAutoCpuCountFromReader(
        std.testing.allocator,
        &scratch,
        .{ .context = &bounded_state, .readFn = ReaderState.read },
        2,
    ));

    var clamped_state = ReaderState{ .chunks = chunks };
    try std.testing.expectEqual(@as(usize, 4), try cpu_mask.derivePerfBufferAutoCpuCountFromReader(
        std.testing.allocator,
        &scratch,
        .{ .context = &clamped_state, .readFn = ReaderState.read },
        9,
    ));
}

test "phase 8 cpu mask starter slice keeps perf-buffer auto CPU sizing bounded without claiming routing parity" {
    try std.testing.expectEqual(@as(usize, 8), cpu_mask.derivePerfBufferAutoCpuCount(8, 0));
    try std.testing.expectEqual(@as(usize, 4), cpu_mask.derivePerfBufferAutoCpuCount(8, 4));
    try std.testing.expectEqual(@as(usize, 8), cpu_mask.derivePerfBufferAutoCpuCount(8, 16));
}

test "phase 8 cpu mask reader interface keeps failures explicit" {
    const ReaderError = error{InjectedReadFailure};
    const ReaderState = struct {
        mode: enum { injected_error, oversized_chunk, empty_chunk },

        fn read(context: ?*anyopaque, _: []u8) ReaderError!?usize {
            const self: *@This() = @ptrCast(@alignCast(context.?));
            return switch (self.mode) {
                .injected_error => error.InjectedReadFailure,
                .oversized_chunk => 12,
                .empty_chunk => 0,
            };
        }
    };

    var injected_error_state = ReaderState{ .mode = .injected_error };
    var oversized_chunk_state = ReaderState{ .mode = .oversized_chunk };
    var empty_chunk_state = ReaderState{ .mode = .empty_chunk };
    var scratch: [8]u8 = undefined;
    var empty_scratch = [_]u8{};

    try std.testing.expectError(error.EmptyReadBuffer, cpu_mask.parseCpuMaskFromReader(std.testing.allocator, empty_scratch[0..], .{
        .context = &injected_error_state,
        .readFn = ReaderState.read,
    }));
    try std.testing.expectError(error.InjectedReadFailure, cpu_mask.parseCpuMaskFromReader(std.testing.allocator, &scratch, .{
        .context = &injected_error_state,
        .readFn = ReaderState.read,
    }));
    try std.testing.expectError(error.InvalidReadCount, cpu_mask.parseCpuMaskFromReader(std.testing.allocator, &scratch, .{
        .context = &oversized_chunk_state,
        .readFn = ReaderState.read,
    }));
    try std.testing.expectError(error.EmptyReadChunk, cpu_mask.parseCpuMaskFromReader(std.testing.allocator, &scratch, .{
        .context = &empty_chunk_state,
        .readFn = ReaderState.read,
    }));
}
