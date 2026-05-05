const std = @import("std");

pub const fifo_capacity: usize = 32;

pub const SampleStage = enum(u8) {
    cold,
    initialized,
    replay_complete,
    exited,
};

pub const SampleFocus = enum {
    bounded_fifo_order,
    wraparound_requeue,
    peek_and_skip,
    non_destructive_snapshot,
    reset_and_replay,
    ownership_and_lifetime,
};

pub const SampleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    requires_runtime_substrate: bool,
    provides_selfcheck: bool,
};

pub const ReplaySummary = struct {
    anchor: []const u8,
    stage_before_replay: SampleStage,
    stage_after_replay: SampleStage,
    len_after_initial_fill: usize,
    first_out: [5]u8,
    second_out: [2]u8,
    skipped_byte: u8,
    peek_value: u8,
    fill_start: u8,
    fill_end: u8,
    snapshot_len: usize,
    snapshot_sequence: [fifo_capacity]u8,
    final_len: usize,
    final_sequence: [fifo_capacity]u8,
    checked_focus: []const SampleFocus,
};

pub const HelperBoundarySummary = struct {
    peek_before_fill: ?u8,
    skip_before_fill: ?u8,
    empty_enqueue_len: usize,
    count_at_capacity: usize,
    overflow_rejected: bool,
    peek_at_capacity: u8,
    skipped_at_capacity: u8,
    count_after_skip: usize,
    count_after_reset: usize,
    pop_after_reset: ?u8,
};

pub const BytestreamFifoSample = struct {
    const Self = @This();

    pub const capacity: usize = fifo_capacity;

    head: usize = 0,
    len: usize = 0,
    storage: [capacity]u8 = [_]u8{0} ** capacity,
    stage_state: SampleStage = .cold,
    init_runs: usize = 0,
    exit_runs: usize = 0,

    pub fn descriptor() SampleDescriptor {
        return .{
            .name = "bytestream_fifo",
            .anchor = "samples/kfifo/bytestream-example.c",
            .requires_runtime_substrate = false,
            .provides_selfcheck = true,
        };
    }

    pub fn count(self: *const Self) usize {
        return self.len;
    }

    pub fn stage(self: *const Self) SampleStage {
        return self.stage_state;
    }

    pub fn reset(self: *Self) void {
        self.head = 0;
        self.len = 0;
        @memset(self.storage[0..], 0);
    }

    pub fn init(self: *Self) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        self.reset();
        self.init_runs += 1;
        self.stage_state = .initialized;
    }

    fn tailIndex(self: *const Self) usize {
        return (self.head + self.len) % capacity;
    }

    pub fn pushByte(self: *Self, value: u8) bool {
        if (self.len == capacity) return false;

        self.storage[self.tailIndex()] = value;
        self.len += 1;
        return true;
    }

    pub fn enqueueSlice(self: *Self, values: []const u8) usize {
        var copied: usize = 0;
        for (values) |value| {
            if (!self.pushByte(value)) break;
            copied += 1;
        }
        return copied;
    }

    pub fn popByte(self: *Self) ?u8 {
        if (self.len == 0) return null;

        const value = self.storage[self.head];
        self.head = (self.head + 1) % capacity;
        self.len -= 1;
        return value;
    }

    pub fn dequeueSlice(self: *Self, dest: []u8) usize {
        var copied: usize = 0;
        while (copied < dest.len) : (copied += 1) {
            dest[copied] = self.popByte() orelse break;
        }
        return copied;
    }

    pub fn peekByte(self: *const Self) ?u8 {
        if (self.len == 0) return null;
        return self.storage[self.head];
    }

    pub fn skipByte(self: *Self) ?u8 {
        return self.popByte();
    }

    pub fn snapshotInto(self: *const Self, dest: []u8) usize {
        const copied = @min(self.len, dest.len);
        for (0..copied) |offset| {
            dest[offset] = self.storage[(self.head + offset) % capacity];
        }
        return copied;
    }

    pub fn drain(self: *Self, dest: []u8) usize {
        return self.dequeueSlice(dest);
    }

    pub fn runHelperBoundaryReplay(self: *Self) HelperBoundarySummary {
        const saved = self.*;
        defer self.* = saved;

        self.reset();

        const peek_before_fill = self.peekByte();
        const skip_before_fill = self.skipByte();
        const empty_enqueue_len = self.enqueueSlice(&.{});

        var value: u8 = 0;
        while (self.pushByte(value)) : (value +%= 1) {}
        const count_at_capacity = self.count();
        const overflow_rejected = !self.pushByte(255);
        const peek_at_capacity = self.peekByte() orelse unreachable;
        const skipped_at_capacity = self.skipByte() orelse unreachable;
        const count_after_skip = self.count();

        self.reset();
        const count_after_reset = self.count();
        const pop_after_reset = self.popByte();

        return .{
            .peek_before_fill = peek_before_fill,
            .skip_before_fill = skip_before_fill,
            .empty_enqueue_len = empty_enqueue_len,
            .count_at_capacity = count_at_capacity,
            .overflow_rejected = overflow_rejected,
            .peek_at_capacity = peek_at_capacity,
            .skipped_at_capacity = skipped_at_capacity,
            .count_after_skip = count_after_skip,
            .count_after_reset = count_after_reset,
            .pop_after_reset = pop_after_reset,
        };
    }

    fn runAnchorReplayInternal(self: *Self) !ReplaySummary {
        self.reset();

        const hello_len = self.enqueueSlice("hello");
        if (hello_len != 5) return error.UnexpectedInitialCopyCount;

        var value: u8 = 0;
        while (value < 10) : (value += 1) {
            if (!self.pushByte(value)) return error.UnexpectedInitialFillFailure;
        }
        const len_after_initial_fill = self.count();

        var first_out: [5]u8 = undefined;
        if (self.dequeueSlice(first_out[0..]) != first_out.len) return error.UnexpectedFirstDrainCount;

        var second_out: [2]u8 = undefined;
        if (self.dequeueSlice(second_out[0..]) != second_out.len) return error.UnexpectedSecondDrainCount;
        if (self.enqueueSlice(second_out[0..]) != second_out.len) return error.UnexpectedRequeueCount;

        const skipped = self.skipByte() orelse return error.UnexpectedSkipOnEmpty;

        var fill_value: u8 = 20;
        while (self.pushByte(fill_value)) : (fill_value +%= 1) {}
        const fill_end = fill_value - 1;

        const peek_value = self.peekByte() orelse return error.UnexpectedPeekOnEmpty;

        var snapshot_sequence: [capacity]u8 = [_]u8{0} ** capacity;
        const snapshot_len = self.snapshotInto(snapshot_sequence[0..]);

        var final_sequence: [capacity]u8 = undefined;
        const final_len = self.drain(final_sequence[0..]);
        if (final_len != capacity) return error.UnexpectedFinalLength;
        if (self.count() != 0) return error.UnexpectedResidualElements;

        return .{
            .anchor = descriptor().anchor,
            .stage_before_replay = .initialized,
            .stage_after_replay = .replay_complete,
            .len_after_initial_fill = len_after_initial_fill,
            .first_out = first_out,
            .second_out = second_out,
            .skipped_byte = skipped,
            .peek_value = peek_value,
            .fill_start = 20,
            .fill_end = fill_end,
            .snapshot_len = snapshot_len,
            .snapshot_sequence = snapshot_sequence,
            .final_len = final_len,
            .final_sequence = final_sequence,
            .checked_focus = &.{
                .bounded_fifo_order,
                .wraparound_requeue,
                .peek_and_skip,
                .non_destructive_snapshot,
                .reset_and_replay,
                .ownership_and_lifetime,
            },
        };
    }

    pub fn runAnchorReplay(self: *Self) !ReplaySummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;

        const replay = try self.runAnchorReplayInternal();
        self.stage_state = .replay_complete;
        return replay;
    }

    pub fn exit(self: *Self) !void {
        switch (self.stage()) {
            .initialized, .replay_complete => {},
            else => return error.InvalidLifecycleTransition,
        }

        self.reset();
        self.exit_runs += 1;
        self.stage_state = .exited;
    }
};

pub const expected_anchor_result = [_]u8{
    3,  4,  5,  6,  7,  8,  9,  0,
    1,  20, 21, 22, 23, 24, 25, 26,
    27, 28, 29, 30, 31, 32, 33, 34,
    35, 36, 37, 38, 39, 40, 41, 42,
};

test "bytestream fifo sample replays the Linux anchor result sequence" {
    var sample = BytestreamFifoSample{};
    try sample.init();
    const replay = try sample.runAnchorReplay();

    try std.testing.expectEqual(SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(SampleStage.replay_complete, replay.stage_after_replay);
    try std.testing.expectEqual(@as(usize, 15), replay.len_after_initial_fill);
    try std.testing.expectEqualStrings("hello", replay.first_out[0..]);
    try std.testing.expectEqualSlices(u8, &.{ 0, 1 }, replay.second_out[0..]);
    try std.testing.expectEqual(@as(u8, 2), replay.skipped_byte);
    try std.testing.expectEqual(@as(u8, 3), replay.peek_value);
    try std.testing.expectEqual(@as(u8, 20), replay.fill_start);
    try std.testing.expectEqual(@as(u8, 42), replay.fill_end);
    try std.testing.expectEqual(@as(usize, fifo_capacity), replay.snapshot_len);
    try std.testing.expectEqualSlices(u8, expected_anchor_result[0..], replay.snapshot_sequence[0..]);
    try std.testing.expectEqual(@as(usize, fifo_capacity), replay.final_len);
    try std.testing.expectEqualSlices(u8, expected_anchor_result[0..], replay.final_sequence[0..]);
    try std.testing.expectEqual(SampleStage.replay_complete, sample.stage());
    try std.testing.expectEqual(@as(usize, 1), sample.init_runs);

    try sample.exit();
    try std.testing.expectEqual(SampleStage.exited, sample.stage());
    try std.testing.expectEqual(@as(usize, 0), sample.count());
    try std.testing.expectEqual(@as(usize, 1), sample.exit_runs);
}

test "bytestream fifo sample replays bounded helper behavior without runtime claims" {
    var sample = BytestreamFifoSample{};
    const replay = sample.runHelperBoundaryReplay();

    try std.testing.expectEqual(@as(?u8, null), replay.peek_before_fill);
    try std.testing.expectEqual(@as(?u8, null), replay.skip_before_fill);
    try std.testing.expectEqual(@as(usize, 0), replay.empty_enqueue_len);
    try std.testing.expectEqual(@as(usize, fifo_capacity), replay.count_at_capacity);
    try std.testing.expect(replay.overflow_rejected);
    try std.testing.expectEqual(@as(u8, 0), replay.peek_at_capacity);
    try std.testing.expectEqual(@as(u8, 0), replay.skipped_at_capacity);
    try std.testing.expectEqual(@as(usize, fifo_capacity - 1), replay.count_after_skip);
    try std.testing.expectEqual(@as(usize, 0), replay.count_after_reset);
    try std.testing.expectEqual(@as(?u8, null), replay.pop_after_reset);
    try std.testing.expectEqual(@as(usize, 0), sample.count());
    try std.testing.expectEqual(SampleStage.cold, sample.stage());
}
