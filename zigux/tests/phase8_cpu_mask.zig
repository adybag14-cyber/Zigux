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

test "phase 8 cpu mask starter slice keeps the C delimiter loop bounded while still allowing sscanf-style token-leading whitespace" {
    const parsed = try cpu_mask.parseCpuMaskString(std.testing.allocator, "\n 0-1,\x0b4\n\x0c6,\r8\n");
    defer parsed.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 5), cpu_mask.countPossibleCpus(parsed.values));
    try std.testing.expect(parsed.values[0]);
    try std.testing.expect(parsed.values[1]);
    try std.testing.expect(parsed.values[4]);
    try std.testing.expect(parsed.values[6]);
    try std.testing.expect(parsed.values[8]);

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
    const parsed = try cpu_mask.parseCpuMaskString(std.testing.allocator, "0- 3,+5-\t6,+8-\r9,+11-\x0c12\n");
    defer parsed.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 10), cpu_mask.countPossibleCpus(parsed.values));
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
        .chunks = &.{ "+0-\t3", ",\t+5", "\n +7-", "\r+8\n" },
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

test "phase 8 cpu mask reader interface keeps the fixed-width libbpf ceiling explicit" {
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
    var scratch: [cpu_mask.cpu_mask_file_read_limit + 1]u8 = undefined;

    try std.testing.expectError(error.InputTooLarge, cpu_mask.parseCpuMaskFromReader(std.testing.allocator, &scratch, .{
        .context = &state,
        .readFn = ReaderState.read,
    }));
}

test "phase 8 cpu mask starter slice keeps perf-buffer auto CPU sizing bounded without claiming routing parity" {
    try std.testing.expectEqual(@as(usize, 8), cpu_mask.derivePerfBufferAutoCpuCount(8, 0));
    try std.testing.expectEqual(@as(usize, 4), cpu_mask.derivePerfBufferAutoCpuCount(8, 4));
    try std.testing.expectEqual(@as(usize, 8), cpu_mask.derivePerfBufferAutoCpuCount(8, 16));
}

test "phase 8 cpu mask starter slice keeps the online CPU eligibility predicate helper-first" {
    const online = [_]bool{ true, false, true };

    try std.testing.expect(cpu_mask.isPerfBufferCpuOnlineEligible(0, 0, &online));
    try std.testing.expect(!cpu_mask.isPerfBufferCpuOnlineEligible(1, 0, &online));
    try std.testing.expect(cpu_mask.isPerfBufferCpuOnlineEligible(2, -1, &online));
    try std.testing.expect(!cpu_mask.isPerfBufferCpuOnlineEligible(3, 0, &online));
    try std.testing.expect(cpu_mask.isPerfBufferCpuOnlineEligible(3, 2, &online));
}

test "phase 8 cpu mask starter slice plans auto-selected CPU indices below the deferred routing boundary" {
    const possible = [_]bool{ true, true, false, true, true };
    const online = [_]bool{ false, true, true, false, true };

    const planned = try cpu_mask.planPerfBufferAutoCpuIndices(std.testing.allocator, &possible, &online, 2);
    defer std.testing.allocator.free(planned);

    try std.testing.expectEqualSlices(usize, &.{ 1, 4 }, planned);
}

test "phase 8 cpu mask starter slice keeps truncated online masks explicit in auto mode" {
    const possible = [_]bool{ true, false, true, true };
    const short_online = [_]bool{ true, false };

    const planned = try cpu_mask.planPerfBufferAutoCpuIndices(std.testing.allocator, &possible, &short_online, 0);
    defer std.testing.allocator.free(planned);

    try std.testing.expectEqualSlices(usize, &.{0}, planned);
}

test "phase 8 cpu mask starter slice plans caller-pinned CPU indices without widening into routing parity" {
    const planned = try cpu_mask.planPerfBufferCpuIndices(
        std.testing.allocator,
        &.{ false, false },
        &.{ false },
        3,
        1,
    );
    defer std.testing.allocator.free(planned);

    try std.testing.expectEqualSlices(usize, &.{ 0, 1, 2 }, planned);
}

test "phase 8 cpu mask starter slice keeps zero or negative requested CPU counts on the bounded auto planner" {
    const possible = [_]bool{ true, true, false, true, true };
    const online = [_]bool{ false, true, true, false, true };

    const zero_requested = try cpu_mask.planPerfBufferCpuIndices(std.testing.allocator, &possible, &online, 0, 2);
    defer std.testing.allocator.free(zero_requested);
    try std.testing.expectEqualSlices(usize, &.{ 1, 4 }, zero_requested);

    const negative_requested = try cpu_mask.planPerfBufferCpuIndices(std.testing.allocator, &possible, &online, -1, 2);
    defer std.testing.allocator.free(negative_requested);
    try std.testing.expectEqualSlices(usize, &.{ 1, 4 }, negative_requested);
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
