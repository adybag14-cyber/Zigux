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

test "phase 8 cpu mask starter slice keeps delimiter skipping bounded and rejects malformed ranges" {
    const parsed = try cpu_mask.parseCpuMaskString(std.testing.allocator, "\n0-1,,4\n6\n");
    defer parsed.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 4), cpu_mask.countPossibleCpus(parsed.values));
    try std.testing.expect(parsed.values[0]);
    try std.testing.expect(parsed.values[1]);
    try std.testing.expect(parsed.values[4]);
    try std.testing.expect(parsed.values[6]);

    try std.testing.expectError(error.EmptyCpuRange, cpu_mask.parseCpuMaskString(std.testing.allocator, ",\n"));
    try std.testing.expectError(error.InvalidCpuRange, cpu_mask.parseCpuMaskString(std.testing.allocator, "2-1"));
    try std.testing.expectError(error.InvalidCpuRange, cpu_mask.parseCpuMaskString(std.testing.allocator, "cpu0"));
    try std.testing.expectError(error.InvalidCpuRange, cpu_mask.parseCpuMaskString(std.testing.allocator, ",\r,"));
}

test "phase 8 cpu mask starter slice keeps libbpf whitespace parity" {
    const parsed = try cpu_mask.parseCpuMaskString(std.testing.allocator, "\r0-1,\t4\n6-7");
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
        .chunks = &.{ "0-3", ",5", "\n7-8\n" },
    };
    var scratch: [8]u8 = undefined;
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

test "phase 8 cpu mask reader interface keeps libbpf whitespace parity" {
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
        .chunks = &.{ "0-3,\r", "5\n", "\t7-8\n" },
    };
    var scratch: [8]u8 = undefined;
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

test "phase 8 cpu mask count helpers keep possible-cpu reporting explicit" {
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

    try std.testing.expectEqual(
        @as(usize, 5),
        try cpu_mask.possibleCpuCountFromString(std.testing.allocator, "\r0-1,\t4\n6-7"),
    );

    var state = ReaderState{
        .chunks = &.{ "0-1,", "4\n", "\t6-7\n" },
    };
    var scratch: [8]u8 = undefined;
    try std.testing.expectEqual(
        @as(usize, 5),
        try cpu_mask.possibleCpuCountFromReader(std.testing.allocator, &scratch, .{
            .context = &state,
            .readFn = ReaderState.read,
        }),
    );
}

test "phase 8 cpu mask count helpers keep failures explicit" {
    const ReaderState = struct {
        mode: enum { empty_chunk, injected_error, oversized_chunk },

        fn read(context: ?*anyopaque, _: []u8) error{InjectedReadFailure}!?usize {
            const self: *@This() = @ptrCast(@alignCast(context.?));
            return switch (self.mode) {
                .empty_chunk => 0,
                .injected_error => error.InjectedReadFailure,
                .oversized_chunk => 12,
            };
        }
    };

    var empty_chunk_state = ReaderState{ .mode = .empty_chunk };
    var injected_error_state = ReaderState{ .mode = .injected_error };
    var oversized_chunk_state = ReaderState{ .mode = .oversized_chunk };
    var scratch: [8]u8 = undefined;

    try std.testing.expectError(
        error.InvalidCpuRange,
        cpu_mask.possibleCpuCountFromString(std.testing.allocator, "cpu0"),
    );
    try std.testing.expectError(
        error.EmptyReadChunk,
        cpu_mask.possibleCpuCountFromReader(std.testing.allocator, &scratch, .{
            .context = &empty_chunk_state,
            .readFn = ReaderState.read,
        }),
    );
    try std.testing.expectError(
        error.InjectedReadFailure,
        cpu_mask.possibleCpuCountFromReader(std.testing.allocator, &scratch, .{
            .context = &injected_error_state,
            .readFn = ReaderState.read,
        }),
    );
    try std.testing.expectError(
        error.InvalidReadCount,
        cpu_mask.possibleCpuCountFromReader(std.testing.allocator, &scratch, .{
            .context = &oversized_chunk_state,
            .readFn = ReaderState.read,
        }),
    );
    try std.testing.expectError(
        error.EmptyReadBuffer,
        cpu_mask.possibleCpuCountFromReader(std.testing.allocator, &.{}, .{
            .context = &empty_chunk_state,
            .readFn = ReaderState.read,
        }),
    );
}

test "phase 8 cpu mask reader interface keeps failures explicit" {
    const ReaderError = error{InjectedReadFailure};
    const ReaderState = struct {
        mode: enum { empty_chunk, injected_error, oversized_chunk },

        fn read(context: ?*anyopaque, _: []u8) ReaderError!?usize {
            const self: *@This() = @ptrCast(@alignCast(context.?));
            return switch (self.mode) {
                .empty_chunk => 0,
                .injected_error => error.InjectedReadFailure,
                .oversized_chunk => 12,
            };
        }
    };

    var empty_chunk_state = ReaderState{ .mode = .empty_chunk };
    var injected_error_state = ReaderState{ .mode = .injected_error };
    var oversized_chunk_state = ReaderState{ .mode = .oversized_chunk };
    var scratch: [8]u8 = undefined;

    try std.testing.expectError(error.EmptyReadChunk, cpu_mask.parseCpuMaskFromReader(std.testing.allocator, &scratch, .{
        .context = &empty_chunk_state,
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
    try std.testing.expectError(error.EmptyReadBuffer, cpu_mask.parseCpuMaskFromReader(std.testing.allocator, &.{}, .{
        .context = &empty_chunk_state,
        .readFn = ReaderState.read,
    }));
}

test "phase 8 cpu mask highest-index helpers keep failures explicit" {
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
        cpu_mask.highestPossibleCpuIndexFromString(std.testing.allocator, "x"),
    );
    try std.testing.expectError(
        error.EmptyReadChunk,
        cpu_mask.highestPossibleCpuIndexFromReader(std.testing.allocator, &scratch, .{
            .context = &empty_state,
            .readFn = ReaderState.read,
        }),
    );
    try std.testing.expectError(
        error.InvalidReadCount,
        cpu_mask.highestPossibleCpuIndexFromReader(std.testing.allocator, &scratch, .{
            .context = &oversize_state,
            .readFn = ReaderState.read,
        }),
    );
    try std.testing.expectError(
        error.EmptyReadBuffer,
        cpu_mask.highestPossibleCpuIndexFromReader(std.testing.allocator, &.{}, .{
            .context = &empty_state,
            .readFn = ReaderState.read,
        }),
    );
}
