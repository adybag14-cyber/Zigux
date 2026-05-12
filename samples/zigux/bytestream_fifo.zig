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

pub const sample_review_focus = [_]SampleFocus{
    .bounded_fifo_order,
    .wraparound_requeue,
    .peek_and_skip,
    .non_destructive_snapshot,
    .preview_truncation,
    .reset_and_replay,
    .ownership_and_lifetime,
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
    preview_total_visible: usize,
    preview_truncated: bool,
    preview_prefix: [8]u8,
    snapshot_len: usize,
    snapshot_before_final_drain: [fifo_capacity]u8,
    fill_start: u8,
    fill_end: u8,
    final_len: usize,
    final_sequence: [fifo_capacity]u8,
    checked_focus: []const SampleFocus,
    storage_backing: StorageBacking,
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

    // Keep the contributor-facing review packet discoverable in the sample so
    // code edits do not drift away from the bounded Phase 5 docs and manifest.
    pub fn reviewContract() ReviewContract {
        return .{
            .focus = &sample_review_focus,
            .non_goals = &sample_review_non_goals,
        };
    }

    pub fn count(self: *const Self) usize {
        return self.len;
    }

    pub fn stage(self: *const Self) SampleStage {
        return self.stage_state;
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

    pub fn snapshotInto(self: *const Self, dest: []u8) usize {
        const copied = @min(self.len, dest.len);
        var index: usize = 0;
        while (index < copied) : (index += 1) {
            dest[index] = self.storage[(self.head + index) % capacity];
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

    pub fn skipByte(self: *Self) ?u8 {
        return self.popByte();
    }

    pub fn drain(self: *Self, dest: []u8) usize {
        return self.dequeueSlice(dest);
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

        var snapshot_before_final_drain: [capacity]u8 = [_]u8{0} ** capacity;
        const snapshot_len = self.snapshotInto(snapshot_before_final_drain[0..]);
        if (snapshot_len != self.count()) return error.UnexpectedSnapshotLength;

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
            .preview_total_visible = preview.total_visible,
            .preview_truncated = preview.truncated,
            .preview_prefix = preview_prefix,
            .snapshot_len = snapshot_len,
            .snapshot_before_final_drain = snapshot_before_final_drain,
            .fill_start = 20,
            .fill_end = fill_end,
            .final_len = final_len,
            .final_sequence = final_sequence,
            .checked_focus = reviewContract().focus,
            .storage_backing = .embedded_fixed_buffer,
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
    const expected_focus = sample_review_focus;
    const expected_non_goals = sample_review_non_goals;
    const descriptor = BytestreamFifoSample.descriptor();
    const contract = BytestreamFifoSample.reviewContract();

    var sample = BytestreamFifoSample{};
    try sample.init();
    const replay = try sample.runAnchorReplay();

    try std.testing.expectEqualStrings("bytestream_fifo", descriptor.name);
    try std.testing.expectEqualStrings("samples/kfifo/bytestream-example.c", descriptor.anchor);
    try std.testing.expect(!descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selfcheck);
    try std.testing.expectEqual(StorageBacking.embedded_fixed_buffer, descriptor.storage_backing);
    try std.testing.expectEqualStrings(descriptor.anchor, replay.anchor);
    try std.testing.expectEqual(@as(usize, expected_focus.len), contract.focus.len);
    for (expected_focus, contract.focus) |expected, actual| {
        try std.testing.expectEqual(expected, actual);
    }
    try std.testing.expectEqual(@as(usize, expected_non_goals.len), contract.non_goals.len);
    for (expected_non_goals, contract.non_goals) |expected, actual| {
        try std.testing.expectEqualStrings(expected, actual);
    }
    try std.testing.expectEqual(@as(usize, expected_focus.len), replay.checked_focus.len);
    for (expected_focus, replay.checked_focus) |expected, actual| {
        try std.testing.expectEqual(expected, actual);
    }
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
    try std.testing.expectEqual(@as(usize, fifo_capacity), replay.preview_total_visible);
    try std.testing.expect(replay.preview_truncated);
    try std.testing.expectEqualSlices(u8, expected_anchor_result[0..8], replay.preview_prefix[0..]);
    try std.testing.expectEqual(@as(usize, fifo_capacity), replay.snapshot_len);
    try std.testing.expectEqual(replay.snapshot_len, replay.preview_total_visible);
    try std.testing.expectEqualSlices(u8, expected_anchor_result[0..], replay.snapshot_before_final_drain[0..]);
    try std.testing.expectEqual(@as(u8, 20), replay.fill_start);
    try std.testing.expectEqual(@as(u8, 42), replay.fill_end);
    try std.testing.expectEqual(@as(usize, fifo_capacity), replay.final_len);
    try std.testing.expectEqualSlices(u8, expected_anchor_result[0..], replay.final_sequence[0..]);
    try std.testing.expectEqual(StorageBacking.embedded_fixed_buffer, replay.storage_backing);
    try std.testing.expectEqual(SampleStage.replay_complete, sample.stage());
    try std.testing.expectEqual(@as(usize, 1), sample.init_runs);
    const replay_lifecycle = sample.lifecycleSummary();
    try std.testing.expectEqual(SampleStage.replay_complete, replay_lifecycle.stage);
    try std.testing.expectEqual(@as(usize, 1), replay_lifecycle.init_run_count);
    try std.testing.expectEqual(@as(usize, 0), replay_lifecycle.exit_run_count);
    try std.testing.expectEqual(@as(usize, 0), replay_lifecycle.queue_len);
    try std.testing.expectEqual(StorageBacking.embedded_fixed_buffer, replay_lifecycle.storage_backing);

    try sample.exit();
    try std.testing.expectEqual(SampleStage.exited, sample.stage());
    try std.testing.expectEqual(@as(usize, 0), sample.count());
    try std.testing.expectEqual(@as(usize, 1), sample.exit_runs);
    const exited_lifecycle = sample.lifecycleSummary();
    try std.testing.expectEqual(SampleStage.exited, exited_lifecycle.stage);
    try std.testing.expectEqual(@as(usize, 1), exited_lifecycle.init_run_count);
    try std.testing.expectEqual(@as(usize, 1), exited_lifecycle.exit_run_count);
    try std.testing.expectEqual(@as(usize, 0), exited_lifecycle.queue_len);
    try std.testing.expectEqual(StorageBacking.embedded_fixed_buffer, exited_lifecycle.storage_backing);
}

test "bytestream fifo sample keeps helper boundaries explicit" {
    var sample = BytestreamFifoSample{};

    try std.testing.expectEqual(@as(?u8, null), sample.peekByte());
    try std.testing.expectEqual(@as(?u8, null), sample.skipByte());
    try std.testing.expectEqual(@as(usize, 0), sample.enqueueSlice(&.{}));

    var preview: [4]u8 = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    const empty_preview = sample.previewInto(preview[0..]);
    try std.testing.expectEqual(@as(usize, 0), empty_preview.copied);
    try std.testing.expectEqual(@as(usize, 0), empty_preview.total_visible);
    try std.testing.expect(!empty_preview.truncated);
    try std.testing.expectEqualSlices(u8, &.{ 0xaa, 0xaa, 0xaa, 0xaa }, preview[0..]);

    try sample.init();
    try std.testing.expect(sample.pushByte(7));
    try std.testing.expectEqual(@as(usize, 1), sample.count());
    sample.reset();
    try std.testing.expectEqual(SampleStage.initialized, sample.stage());
    try std.testing.expectEqual(@as(usize, 1), sample.init_runs);
    try std.testing.expectEqual(@as(usize, 0), sample.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), sample.count());

    try std.testing.expectEqual(@as(usize, 5), sample.enqueueSlice("hello"));
    var value: u8 = 0;
    while (value < 10) : (value += 1) {
        try std.testing.expect(sample.pushByte(value));
    }
    var discard: [7]u8 = undefined;
    try std.testing.expectEqual(@as(usize, discard.len), sample.dequeueSlice(discard[0..]));
    try std.testing.expectEqual(@as(usize, 2), sample.enqueueSlice(&.{ 0, 1 }));

    var wraparound_preview: [8]u8 = [_]u8{0} ** 8;
    const preview_result = sample.previewInto(wraparound_preview[0..]);
    try std.testing.expectEqual(@as(usize, wraparound_preview.len), preview_result.copied);
    try std.testing.expectEqual(@as(usize, 10), preview_result.total_visible);
    try std.testing.expect(preview_result.truncated);
    try std.testing.expectEqualSlices(u8, &.{ 2, 3, 4, 5, 6, 7, 8, 9 }, wraparound_preview[0..]);
    try std.testing.expectEqual(@as(usize, 10), sample.count());

    sample.reset();
    var fill: u8 = 0;
    while (fill < fifo_capacity) : (fill += 1) {
        try std.testing.expect(sample.pushByte(fill));
    }
    try std.testing.expect(!sample.pushByte(255));
    try std.testing.expectEqual(@as(usize, fifo_capacity), sample.count());
    try std.testing.expectEqual(@as(?u8, 0), sample.peekByte());

    var full_preview: [fifo_capacity]u8 = [_]u8{0} ** fifo_capacity;
    const full_preview_result = sample.previewInto(full_preview[0..]);
    try std.testing.expectEqual(@as(usize, fifo_capacity), full_preview_result.copied);
    try std.testing.expectEqual(@as(usize, fifo_capacity), full_preview_result.total_visible);
    try std.testing.expect(!full_preview_result.truncated);

    sample.reset();
    try std.testing.expectEqual(@as(usize, 5), sample.enqueueSlice("hello"));
    var short_drain: [3]u8 = undefined;
    try std.testing.expectEqual(@as(usize, short_drain.len), sample.drain(short_drain[0..]));
    try std.testing.expectEqualSlices(u8, "hel", short_drain[0..]);
    try std.testing.expectEqual(@as(usize, 2), sample.count());
    try std.testing.expectEqual(@as(?u8, 'l'), sample.peekByte());

    var remainder: [2]u8 = undefined;
    try std.testing.expectEqual(@as(usize, remainder.len), sample.dequeueSlice(remainder[0..]));
    try std.testing.expectEqualSlices(u8, "lo", remainder[0..]);
    try std.testing.expectEqual(@as(usize, 0), sample.count());
    try std.testing.expectEqual(@as(usize, 0), sample.drain(short_drain[0..]));

    try sample.exit();
    try std.testing.expectEqual(SampleStage.exited, sample.stage());
    try std.testing.expectEqual(@as(usize, 0), sample.count());
    try std.testing.expectEqual(@as(usize, 1), sample.exit_runs);
}

test "bytestream fifo sample keeps ownership and lifetime guards explicit" {
    var sample = BytestreamFifoSample{};

    try std.testing.expectEqual(SampleStage.cold, sample.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.runAnchorReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.exit());

    try sample.init();
    try std.testing.expectEqual(SampleStage.initialized, sample.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.init());

    _ = try sample.runAnchorReplay();
    try std.testing.expectEqual(SampleStage.replay_complete, sample.stage());

    try sample.exit();
    try std.testing.expectEqual(SampleStage.exited, sample.stage());
    try std.testing.expectEqual(@as(usize, 0), sample.count());
    try std.testing.expectEqual(@as(usize, 1), sample.init_runs);
    try std.testing.expectEqual(@as(usize, 1), sample.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.runAnchorReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.exit());
}

test "bytestream fifo sample reset clears queue state without rewinding lifecycle bookkeeping" {
    var sample = BytestreamFifoSample{};

    try sample.init();
    try std.testing.expect(sample.pushByte(7));
    sample.reset();
    try std.testing.expectEqual(SampleStage.initialized, sample.stage());
    try std.testing.expectEqual(@as(usize, 1), sample.init_runs);
    try std.testing.expectEqual(@as(usize, 0), sample.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), sample.count());
    try std.testing.expectEqual(@as(?u8, null), sample.peekByte());

    _ = try sample.runAnchorReplay();
    sample.reset();
    try std.testing.expectEqual(SampleStage.replay_complete, sample.stage());
    try std.testing.expectEqual(@as(usize, 1), sample.init_runs);
    try std.testing.expectEqual(@as(usize, 0), sample.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), sample.count());

    try sample.exit();
    sample.reset();
    try std.testing.expectEqual(SampleStage.exited, sample.stage());
    try std.testing.expectEqual(@as(usize, 1), sample.init_runs);
    try std.testing.expectEqual(@as(usize, 1), sample.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), sample.count());
}
