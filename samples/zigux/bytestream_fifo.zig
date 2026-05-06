const std = @import("std");

pub const fifo_capacity: usize = 32;

pub const SampleStage = enum(u8) {
    cold,
    initialized,
    replay_complete,
    exited,
};

pub const StorageBacking = enum {
    embedded_fixed_buffer,
};

pub const SampleFocus = enum {
    bounded_fifo_order,
    wraparound_requeue,
    peek_and_skip,
    non_destructive_snapshot,
    preview_truncation,
    reset_and_replay,
    ownership_and_lifetime,
};

const sample_review_focus = [_]SampleFocus{
    .bounded_fifo_order,
    .wraparound_requeue,
    .peek_and_skip,
    .non_destructive_snapshot,
    .preview_truncation,
    .reset_and_replay,
    .ownership_and_lifetime,
};

const preview_boundary_focus = [_]SampleFocus{
    .wraparound_requeue,
    .non_destructive_snapshot,
    .preview_truncation,
};

pub const sample_review_non_goals = [_][]const u8{
    "procfs parity",
    "kfifo_from_user or kfifo_to_user parity",
    "loadable module registration",
    "locking or blocking semantics",
};

pub const ReviewContract = struct {
    focus: []const SampleFocus,
    non_goals: []const []const u8,
};

pub const PreviewResult = struct {
    copied: usize,
    total_visible: usize,
    truncated: bool,
};

pub const SampleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    requires_runtime_substrate: bool,
    provides_selfcheck: bool,
    storage_backing: StorageBacking,
};

pub const ReplaySummary = struct {
    anchor: []const u8,
    stage_before_replay: SampleStage,
    stage_after_replay: SampleStage,
    initial_string_copy_count: usize,
    len_after_initial_fill: usize,
    first_out: [5]u8,
    first_drain_count: usize,
    second_out: [2]u8,
    second_drain_count: usize,
    requeue_count: usize,
    skipped_byte: u8,
    peek_value: u8,
    preview_len: usize,
    preview_truncated: bool,
    preview_prefix: [8]u8,
    snapshot_len: usize,
    snapshot_sequence: [fifo_capacity]u8,
    fill_start: u8,
    fill_end: u8,
    final_len: usize,
    final_sequence: [fifo_capacity]u8,
    checked_focus: []const SampleFocus,
    storage_backing: StorageBacking,
};

pub const PreviewBoundarySummary = struct {
    stage_before_replay: SampleStage,
    stage_after_replay: SampleStage,
    snapshot_len: usize,
    snapshot_prefix: [4]u8,
    preview_len: usize,
    preview_total_visible: usize,
    preview_truncated: bool,
    preview_prefix: [8]u8,
    queue_len_after_preview: usize,
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

pub const ShortDrainSummary = struct {
    initial_copy_count: usize,
    first_drain: [3]u8,
    first_drain_count: usize,
    remaining_snapshot: [2]u8,
    remaining_snapshot_len: usize,
    remaining_drain: [2]u8,
    remaining_drain_count: usize,
    empty_follow_up_drain_count: usize,
};

pub const LifecycleSummary = struct {
    stage: SampleStage,
    init_run_count: usize,
    exit_run_count: usize,
    queue_len: usize,
    storage_backing: StorageBacking,
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
            .storage_backing = .embedded_fixed_buffer,
        };
    }

    pub fn reviewContract() ReviewContract {
        return .{
            .focus = &sample_review_focus,
            .non_goals = &sample_review_non_goals,
        };
    }

    pub fn count(self: *const Self) usize {
        return self.len;
    }

    pub fn available(self: *const Self) usize {
        return capacity - self.len;
    }

    pub fn stage(self: *const Self) SampleStage {
        return self.stage_state;
    }

    pub fn isEmpty(self: *const Self) bool {
        return self.len == 0;
    }

    pub fn isFull(self: *const Self) bool {
        return self.len == capacity;
    }

    pub fn lifecycleSummary(self: *const Self) LifecycleSummary {
        return .{
            .stage = self.stage(),
            .init_run_count = self.init_runs,
            .exit_run_count = self.exit_runs,
            .queue_len = self.count(),
            .storage_backing = .embedded_fixed_buffer,
        };
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

    pub fn previewInto(self: *const Self, dest: []u8) PreviewResult {
        const copied = self.snapshotInto(dest);
        return .{
            .copied = copied,
            .total_visible = self.len,
            .truncated = copied < self.len,
        };
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

    pub fn runShortDrainReplay(self: *Self) ShortDrainSummary {
        const saved = self.*;
        defer self.* = saved;

        self.reset();

        const initial_copy_count = self.enqueueSlice("hello");

        var first_drain: [3]u8 = undefined;
        const first_drain_count = self.dequeueSlice(first_drain[0..]);

        var remaining_snapshot: [2]u8 = [_]u8{0} ** 2;
        const remaining_snapshot_len = self.snapshotInto(remaining_snapshot[0..]);

        var remaining_drain: [2]u8 = [_]u8{0} ** 2;
        const remaining_drain_count = self.dequeueSlice(remaining_drain[0..]);

        var empty_follow_up: [1]u8 = [_]u8{0};
        const empty_follow_up_drain_count = self.dequeueSlice(empty_follow_up[0..]);

        return .{
            .initial_copy_count = initial_copy_count,
            .first_drain = first_drain,
            .first_drain_count = first_drain_count,
            .remaining_snapshot = remaining_snapshot,
            .remaining_snapshot_len = remaining_snapshot_len,
            .remaining_drain = remaining_drain,
            .remaining_drain_count = remaining_drain_count,
            .empty_follow_up_drain_count = empty_follow_up_drain_count,
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
        const first_drain_count = self.dequeueSlice(first_out[0..]);
        if (first_drain_count != first_out.len) return error.UnexpectedFirstDrainCount;

        var second_out: [2]u8 = undefined;
        const second_drain_count = self.dequeueSlice(second_out[0..]);
        if (second_drain_count != second_out.len) return error.UnexpectedSecondDrainCount;

        const requeue_count = self.enqueueSlice(second_out[0..]);
        if (requeue_count != second_out.len) return error.UnexpectedRequeueCount;

        const skipped = self.skipByte() orelse return error.UnexpectedSkipOnEmpty;

        var fill_value: u8 = 20;
        while (self.pushByte(fill_value)) : (fill_value +%= 1) {}
        const fill_end = fill_value - 1;

        const peek_value = self.peekByte() orelse return error.UnexpectedPeekOnEmpty;

        var preview_prefix: [8]u8 = [_]u8{0} ** 8;
        const preview = self.previewInto(preview_prefix[0..]);

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
            .initial_string_copy_count = hello_len,
            .len_after_initial_fill = len_after_initial_fill,
            .first_out = first_out,
            .first_drain_count = first_drain_count,
            .second_out = second_out,
            .second_drain_count = second_drain_count,
            .requeue_count = requeue_count,
            .skipped_byte = skipped,
            .peek_value = peek_value,
            .preview_len = preview.copied,
            .preview_truncated = preview.truncated,
            .preview_prefix = preview_prefix,
            .snapshot_len = snapshot_len,
            .snapshot_sequence = snapshot_sequence,
            .fill_start = 20,
            .fill_end = fill_end,
            .final_len = final_len,
            .final_sequence = final_sequence,
            .checked_focus = &sample_review_focus,
            .storage_backing = .embedded_fixed_buffer,
        };
    }

    pub fn runAnchorReplay(self: *Self) !ReplaySummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;

        const replay = try self.runAnchorReplayInternal();
        self.stage_state = .replay_complete;
        return replay;
    }

    pub fn runPreviewBoundaryReplay(self: *Self) !PreviewBoundarySummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;

        self.reset();

        const hello_len = self.enqueueSlice("hello");
        if (hello_len != 5) return error.UnexpectedInitialCopyCount;

        var value: u8 = 0;
        while (value < 10) : (value += 1) {
            if (!self.pushByte(value)) return error.UnexpectedInitialFillFailure;
        }

        var discard: [7]u8 = undefined;
        const discard_count = self.dequeueSlice(discard[0..]);
        if (discard_count != discard.len) return error.UnexpectedBoundaryDiscardCount;

        const requeue_count = self.enqueueSlice(&.{ 0, 1 });
        if (requeue_count != 2) return error.UnexpectedRequeueCount;

        var snapshot_prefix: [4]u8 = undefined;
        const snapshot_len = self.snapshotInto(snapshot_prefix[0..]);

        var preview_prefix: [8]u8 = [_]u8{0} ** 8;
        const preview = self.previewInto(preview_prefix[0..]);

        return .{
            .stage_before_replay = .initialized,
            .stage_after_replay = .initialized,
            .snapshot_len = snapshot_len,
            .snapshot_prefix = snapshot_prefix,
            .preview_len = preview.copied,
            .preview_total_visible = preview.total_visible,
            .preview_truncated = preview.truncated,
            .preview_prefix = preview_prefix,
            .queue_len_after_preview = self.count(),
            .checked_focus = &preview_boundary_focus,
        };
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
    const descriptor = BytestreamFifoSample.descriptor();
    const review_contract = BytestreamFifoSample.reviewContract();
    try std.testing.expectEqualStrings("samples/kfifo/bytestream-example.c", descriptor.anchor);
    try std.testing.expectEqual(StorageBacking.embedded_fixed_buffer, descriptor.storage_backing);
    try std.testing.expectEqual(@as(usize, 7), review_contract.focus.len);
    try std.testing.expectEqual(@as(usize, fifo_capacity), sample.available());

    try sample.init();
    try std.testing.expect(sample.isEmpty());
    try std.testing.expect(!sample.isFull());
    try std.testing.expectEqual(@as(usize, fifo_capacity), sample.available());
    const replay = try sample.runAnchorReplay();

    try std.testing.expectEqual(SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(SampleStage.replay_complete, replay.stage_after_replay);
    try std.testing.expectEqual(@as(usize, 5), replay.initial_string_copy_count);
    try std.testing.expectEqual(@as(usize, 15), replay.len_after_initial_fill);
    try std.testing.expectEqualStrings("hello", replay.first_out[0..]);
    try std.testing.expectEqual(@as(usize, 5), replay.first_drain_count);
    try std.testing.expectEqualSlices(u8, &.{ 0, 1 }, replay.second_out[0..]);
    try std.testing.expectEqual(@as(usize, 2), replay.second_drain_count);
    try std.testing.expectEqual(@as(usize, 2), replay.requeue_count);
    try std.testing.expectEqual(@as(u8, 2), replay.skipped_byte);
    try std.testing.expectEqual(@as(u8, 3), replay.peek_value);
    try std.testing.expectEqual(@as(usize, 8), replay.preview_len);
    try std.testing.expect(replay.preview_truncated);
    try std.testing.expectEqualSlices(u8, expected_anchor_result[0..8], replay.preview_prefix[0..]);
    try std.testing.expectEqual(@as(usize, fifo_capacity), replay.snapshot_len);
    try std.testing.expectEqualSlices(u8, expected_anchor_result[0..], replay.snapshot_sequence[0..]);
    try std.testing.expectEqual(@as(usize, fifo_capacity), replay.final_len);
    try std.testing.expectEqual(StorageBacking.embedded_fixed_buffer, replay.storage_backing);
    try std.testing.expectEqual(@as(usize, 7), replay.checked_focus.len);
    try std.testing.expectEqualSlices(u8, expected_anchor_result[0..], replay.final_sequence[0..]);
    try std.testing.expectEqual(SampleStage.replay_complete, sample.stage());
    try std.testing.expectEqual(@as(usize, fifo_capacity), sample.available());

    try sample.exit();
    try std.testing.expectEqual(SampleStage.exited, sample.stage());
    try std.testing.expectEqual(@as(usize, 0), sample.count());
    try std.testing.expectEqual(@as(usize, 1), sample.init_runs);
    try std.testing.expectEqual(@as(usize, 1), sample.exit_runs);
    try std.testing.expect(sample.isEmpty());
    try std.testing.expect(!sample.isFull());
    try std.testing.expectEqual(@as(usize, fifo_capacity), sample.available());
}

test "bytestream fifo sample keeps bounded helper behavior without runtime claims" {
    var sample = BytestreamFifoSample{};
    var preview_buf: [4]u8 = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    const empty_preview = sample.previewInto(preview_buf[0..]);
    try std.testing.expectEqual(@as(usize, 0), empty_preview.copied);
    try std.testing.expectEqual(@as(usize, 0), empty_preview.total_visible);
    try std.testing.expect(!empty_preview.truncated);
    try std.testing.expectEqualSlices(u8, &.{ 0xaa, 0xaa, 0xaa, 0xaa }, preview_buf[0..]);
    try std.testing.expectEqual(@as(usize, fifo_capacity), sample.available());

    const helper_replay = sample.runHelperBoundaryReplay();

    try std.testing.expectEqual(@as(?u8, null), helper_replay.peek_before_fill);
    try std.testing.expectEqual(@as(?u8, null), helper_replay.skip_before_fill);
    try std.testing.expectEqual(@as(usize, 0), helper_replay.empty_enqueue_len);
    try std.testing.expectEqual(@as(usize, fifo_capacity), helper_replay.count_at_capacity);
    try std.testing.expect(helper_replay.overflow_rejected);
    try std.testing.expectEqual(@as(u8, 0), helper_replay.peek_at_capacity);
    try std.testing.expectEqual(@as(u8, 0), helper_replay.skipped_at_capacity);
    try std.testing.expectEqual(@as(usize, fifo_capacity - 1), helper_replay.count_after_skip);
    try std.testing.expectEqual(@as(usize, 0), helper_replay.count_after_reset);
    try std.testing.expectEqual(@as(?u8, null), helper_replay.pop_after_reset);

    const short_drain = sample.runShortDrainReplay();
    try std.testing.expectEqual(@as(usize, 5), short_drain.initial_copy_count);
    try std.testing.expectEqual(@as(usize, 3), short_drain.first_drain_count);
    try std.testing.expectEqualSlices(u8, "hel", short_drain.first_drain[0..]);
    try std.testing.expectEqual(@as(usize, 2), short_drain.remaining_snapshot_len);
    try std.testing.expectEqualSlices(u8, "lo", short_drain.remaining_snapshot[0..]);
    try std.testing.expectEqual(@as(usize, 2), short_drain.remaining_drain_count);
    try std.testing.expectEqualSlices(u8, "lo", short_drain.remaining_drain[0..]);
    try std.testing.expectEqual(@as(usize, 0), short_drain.empty_follow_up_drain_count);
    try std.testing.expectEqual(@as(usize, 0), sample.count());
    try std.testing.expectEqual(SampleStage.cold, sample.stage());
    try std.testing.expectEqual(@as(usize, fifo_capacity), sample.available());
}

test "bytestream fifo sample keeps preview truncation explicit" {
    var sample = BytestreamFifoSample{};
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.runPreviewBoundaryReplay());

    try sample.init();
    const preview = try sample.runPreviewBoundaryReplay();

    try std.testing.expectEqual(SampleStage.initialized, preview.stage_before_replay);
    try std.testing.expectEqual(SampleStage.initialized, preview.stage_after_replay);
    try std.testing.expectEqual(@as(usize, 4), preview.snapshot_len);
    try std.testing.expectEqualSlices(u8, &.{ 2, 3, 4, 5 }, preview.snapshot_prefix[0..]);
    try std.testing.expectEqual(@as(usize, 8), preview.preview_len);
    try std.testing.expectEqual(@as(usize, 10), preview.preview_total_visible);
    try std.testing.expect(preview.preview_truncated);
    try std.testing.expectEqualSlices(u8, &.{ 2, 3, 4, 5, 6, 7, 8, 9 }, preview.preview_prefix[0..]);
    try std.testing.expectEqual(@as(usize, 10), preview.queue_len_after_preview);
    try std.testing.expectEqual(@as(usize, 3), preview.checked_focus.len);
    try std.testing.expectEqual(SampleFocus.wraparound_requeue, preview.checked_focus[0]);
    try std.testing.expectEqual(SampleFocus.non_destructive_snapshot, preview.checked_focus[1]);
    try std.testing.expectEqual(SampleFocus.preview_truncation, preview.checked_focus[2]);
    try std.testing.expectEqual(SampleStage.initialized, sample.stage());
    try std.testing.expectEqual(@as(usize, fifo_capacity - 10), sample.available());
}

test "bytestream fifo sample exposes empty and full state boundaries explicitly" {
    var sample = BytestreamFifoSample{};

    try std.testing.expect(sample.isEmpty());
    try std.testing.expect(!sample.isFull());
    try std.testing.expectEqual(@as(usize, fifo_capacity), sample.available());

    try sample.init();
    try std.testing.expect(sample.isEmpty());
    try std.testing.expect(!sample.isFull());
    try std.testing.expectEqual(@as(usize, fifo_capacity), sample.available());

    try std.testing.expectEqual(@as(usize, 5), sample.enqueueSlice("hello"));
    try std.testing.expect(!sample.isEmpty());
    try std.testing.expect(!sample.isFull());
    try std.testing.expectEqual(@as(usize, fifo_capacity - 5), sample.available());

    var value: u8 = 0;
    while (!sample.isFull()) : (value +%= 1) {
        try std.testing.expect(sample.pushByte(value));
    }
    try std.testing.expect(sample.isFull());
    try std.testing.expect(!sample.isEmpty());
    try std.testing.expect(!sample.pushByte(255));
    try std.testing.expectEqual(@as(usize, 0), sample.available());

    _ = sample.skipByte() orelse unreachable;
    try std.testing.expect(!sample.isFull());
    try std.testing.expect(!sample.isEmpty());
    try std.testing.expectEqual(@as(usize, 1), sample.available());

    sample.reset();
    try std.testing.expect(sample.isEmpty());
    try std.testing.expect(!sample.isFull());
    try std.testing.expectEqual(@as(usize, fifo_capacity), sample.available());

    try sample.exit();
    try std.testing.expect(sample.isEmpty());
    try std.testing.expect(!sample.isFull());
    try std.testing.expectEqual(@as(usize, fifo_capacity), sample.available());
}

test "bytestream fifo sample makes ownership and lifetime boundaries explicit" {
    var sample = BytestreamFifoSample{};

    try std.testing.expectEqual(SampleStage.cold, sample.stage());
    try std.testing.expectEqual(@as(usize, fifo_capacity), sample.available());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.runAnchorReplay());

    try sample.init();
    try std.testing.expectEqual(SampleStage.initialized, sample.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.init());

    _ = try sample.runPreviewBoundaryReplay();
    try std.testing.expectEqual(SampleStage.initialized, sample.stage());
    try std.testing.expectEqual(@as(usize, fifo_capacity - 10), sample.available());

    _ = try sample.runAnchorReplay();
    try std.testing.expectEqual(SampleStage.replay_complete, sample.stage());
    const replay_lifecycle = sample.lifecycleSummary();
    try std.testing.expectEqual(SampleStage.replay_complete, replay_lifecycle.stage);
    try std.testing.expectEqual(@as(usize, 1), replay_lifecycle.init_run_count);
    try std.testing.expectEqual(@as(usize, 0), replay_lifecycle.exit_run_count);
    try std.testing.expectEqual(@as(usize, 0), replay_lifecycle.queue_len);
    try std.testing.expectEqual(StorageBacking.embedded_fixed_buffer, replay_lifecycle.storage_backing);
    try std.testing.expectEqual(@as(usize, fifo_capacity), sample.available());

    try sample.exit();
    try std.testing.expectEqual(SampleStage.exited, sample.stage());
    try std.testing.expectEqual(@as(usize, 0), sample.count());
    try std.testing.expectEqual(@as(usize, 1), sample.init_runs);
    try std.testing.expectEqual(@as(usize, 1), sample.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.runPreviewBoundaryReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.exit());
    try std.testing.expectEqual(@as(usize, fifo_capacity), sample.available());
}
