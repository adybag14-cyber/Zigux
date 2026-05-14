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
    remaining_capacity,
    queue_shape_boundaries,
    helper_boundaries,
    reset_and_replay,
    ownership_and_lifetime,
};

pub const sample_review_focus = [_]SampleFocus{
    .bounded_fifo_order,
    .wraparound_requeue,
    .peek_and_skip,
    .non_destructive_snapshot,
    .preview_truncation,
    .remaining_capacity,
    .queue_shape_boundaries,
    .helper_boundaries,
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

pub const VisibleSpanSummary = struct {
    head_index: usize,
    tail_index: usize,
    total_visible: usize,
    first_window_len: usize,
    second_window_len: usize,
    wraps: bool,
};

pub const PreviewBoundarySummary = struct {
    snapshot_prefix: [4]u8,
    preview_prefix: [8]u8,
    preview_total_visible: usize,
    queue_len_after_preview: usize,
    available_after_preview: usize,
    visible_span_after_preview: VisibleSpanSummary,
};

pub const WrappedPreviewSummary = struct {
    drained_prefix: [4]u8,
    refill_values: [4]u8,
    snapshot_prefix: [12]u8,
    preview_prefix: [8]u8,
    preview_total_visible: usize,
    queue_len_after_preview: usize,
    available_after_preview: usize,
    visible_span_after_preview: VisibleSpanSummary,
};

pub const RemainingCapacitySummary = struct {
    drained_prefix: [8]u8,
    available_after_init: usize,
    available_after_hello: usize,
    available_when_full: usize,
    available_after_skip: usize,
    available_after_wrap_refill: usize,
    available_after_partial_drain: usize,
    queue_len_after_partial_drain: usize,
    visible_span_after_partial_drain: VisibleSpanSummary,
    wrapped_when_full: bool,
    wrapped_after_wrap_refill: bool,
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

pub const OccupancySummary = struct {
    used: usize,
    available: usize,
    empty: bool,
    full: bool,
    wrapped_window: bool,
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

    pub fn available(self: *const Self) usize {
        return capacity - self.len;
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

    pub fn occupancySummary(self: *const Self) OccupancySummary {
        const used = self.count();
        const free = self.available();
        return .{
            .used = used,
            .available = free,
            .empty = used == 0,
            .full = free == 0,
            .wrapped_window = self.usesWrappedStorageWindow(),
        };
    }

    pub fn visibleSpanSummary(self: *const Self) VisibleSpanSummary {
        const first_span_len = @min(self.len, capacity - self.head);
        const second_span_len = self.len - first_span_len;
        return .{
            .head_index = self.head,
            .tail_index = self.tailIndex(),
            .total_visible = self.len,
            .first_window_len = first_span_len,
            .second_window_len = second_span_len,
            .wraps = second_span_len != 0,
        };
    }

    pub fn usesWrappedStorageWindow(self: *const Self) bool {
        if (self.len == 0) return false;
        return self.head + self.len > capacity;
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

    pub fn runPreviewBoundaryReplay(self: *Self) !PreviewBoundarySummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;

        self.reset();

        if (self.enqueueSlice("hello") != 5) return error.UnexpectedInitialCopyCount;

        var value: u8 = 0;
        while (value < 10) : (value += 1) {
            if (!self.pushByte(value)) return error.UnexpectedInitialFillFailure;
        }

        var first_out: [5]u8 = undefined;
        if (self.dequeueSlice(first_out[0..]) != first_out.len) return error.UnexpectedFirstDrainCount;

        var second_out: [2]u8 = undefined;
        if (self.dequeueSlice(second_out[0..]) != second_out.len) return error.UnexpectedSecondDrainCount;
        if (self.enqueueSlice(second_out[0..]) != second_out.len) return error.UnexpectedRequeueCount;

        var snapshot_prefix: [4]u8 = [_]u8{0} ** 4;
        _ = self.snapshotInto(snapshot_prefix[0..]);

        var preview_prefix: [8]u8 = [_]u8{0} ** 8;
        const preview = self.previewInto(preview_prefix[0..]);

        return .{
            .snapshot_prefix = snapshot_prefix,
            .preview_prefix = preview_prefix,
            .preview_total_visible = preview.total_visible,
            .queue_len_after_preview = self.count(),
            .available_after_preview = self.available(),
            .visible_span_after_preview = self.visibleSpanSummary(),
        };
    }

    pub fn runWrappedPreviewReplay(self: *Self) !WrappedPreviewSummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;

        self.reset();

        if (self.enqueueSlice("hello") != 5) return error.UnexpectedInitialCopyCount;

        var value: u8 = 0;
        while (value <= 26) : (value += 1) {
            if (!self.pushByte(value)) return error.UnexpectedInitialFillFailure;
        }

        var drained_prefix: [4]u8 = undefined;
        if (self.dequeueSlice(drained_prefix[0..]) != drained_prefix.len) return error.UnexpectedFirstDrainCount;

        const refill_values = [4]u8{ 200, 201, 202, 203 };
        if (self.enqueueSlice(refill_values[0..]) != refill_values.len) return error.UnexpectedRequeueCount;

        var snapshot_prefix: [12]u8 = [_]u8{0} ** 12;
        _ = self.snapshotInto(snapshot_prefix[0..]);

        var preview_prefix: [8]u8 = [_]u8{0} ** 8;
        const preview = self.previewInto(preview_prefix[0..]);

        return .{
            .drained_prefix = drained_prefix,
            .refill_values = refill_values,
            .snapshot_prefix = snapshot_prefix,
            .preview_prefix = preview_prefix,
            .preview_total_visible = preview.total_visible,
            .queue_len_after_preview = self.count(),
            .available_after_preview = self.available(),
            .visible_span_after_preview = self.visibleSpanSummary(),
        };
    }

    pub fn runRemainingCapacityReplay(self: *Self) !RemainingCapacitySummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;

        self.reset();
        const available_after_init = self.available();

        if (self.enqueueSlice("hello") != 5) return error.UnexpectedInitialCopyCount;
        const available_after_hello = self.available();

        var fill_value: u8 = 0;
        while (self.pushByte(fill_value)) : (fill_value += 1) {}
        const available_when_full = self.available();
        const wrapped_when_full = self.usesWrappedStorageWindow();

        _ = self.skipByte() orelse return error.UnexpectedSkipOnEmpty;
        const available_after_skip = self.available();

        if (!self.pushByte(200)) return error.UnexpectedWrapRefillFailure;
        const available_after_wrap_refill = self.available();
        const wrapped_after_wrap_refill = self.usesWrappedStorageWindow();

        var drained_prefix: [8]u8 = undefined;
        if (self.dequeueSlice(drained_prefix[0..]) != drained_prefix.len) return error.UnexpectedDrainCount;

        return .{
            .drained_prefix = drained_prefix,
            .available_after_init = available_after_init,
            .available_after_hello = available_after_hello,
            .available_when_full = available_when_full,
            .available_after_skip = available_after_skip,
            .available_after_wrap_refill = available_after_wrap_refill,
            .available_after_partial_drain = self.available(),
            .queue_len_after_partial_drain = self.count(),
            .visible_span_after_partial_drain = self.visibleSpanSummary(),
            .wrapped_when_full = wrapped_when_full,
            .wrapped_after_wrap_refill = wrapped_after_wrap_refill,
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
    try std.testing.expectEqual(@as(usize, fifo_capacity), sample.available());
    try std.testing.expectEqual(@as(usize, 0), sample.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 0), sample.visibleSpanSummary().second_window_len);
    try std.testing.expect(!sample.usesWrappedStorageWindow());

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
    try std.testing.expectEqual(@as(usize, fifo_capacity), sample.available());
    try std.testing.expectEqual(@as(usize, 0), sample.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 0), sample.visibleSpanSummary().second_window_len);
    try std.testing.expect(!sample.usesWrappedStorageWindow());
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
    try std.testing.expectEqual(@as(usize, fifo_capacity), sample.available());
    try std.testing.expectEqual(@as(usize, 0), sample.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 0), sample.visibleSpanSummary().second_window_len);
    try std.testing.expect(!sample.usesWrappedStorageWindow());
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
    try std.testing.expectEqual(@as(usize, fifo_capacity), sample.available());
    try std.testing.expectEqual(@as(usize, 0), sample.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 0), sample.visibleSpanSummary().second_window_len);
    try std.testing.expect(!sample.usesWrappedStorageWindow());

    try sample.init();
    try std.testing.expect(sample.pushByte(7));
    try std.testing.expectEqual(@as(usize, 1), sample.count());
    sample.reset();
    try std.testing.expectEqual(SampleStage.initialized, sample.stage());
    try std.testing.expectEqual(@as(usize, 1), sample.init_runs);
    try std.testing.expectEqual(@as(usize, 0), sample.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), sample.count());

    try std.testing.expectEqual(@as(usize, 5), sample.enqueueSlice("hello"));
    try std.testing.expectEqual(@as(usize, 27), sample.available());
    try std.testing.expectEqual(@as(usize, 5), sample.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 0), sample.visibleSpanSummary().second_window_len);
    try std.testing.expect(!sample.usesWrappedStorageWindow());

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
    try std.testing.expectEqual(@as(usize, 22), sample.available());
    try std.testing.expectEqual(@as(usize, 10), sample.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 0), sample.visibleSpanSummary().second_window_len);
    try std.testing.expect(!sample.usesWrappedStorageWindow());

    sample.reset();
    var fill: u8 = 0;
    while (fill < fifo_capacity) : (fill += 1) {
        try std.testing.expect(sample.pushByte(fill));
    }
    try std.testing.expect(!sample.pushByte(255));
    try std.testing.expectEqual(@as(usize, fifo_capacity), sample.count());
    try std.testing.expectEqual(@as(usize, 0), sample.available());
    try std.testing.expectEqual(@as(?u8, 0), sample.peekByte());
    try std.testing.expectEqual(@as(usize, fifo_capacity), sample.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 0), sample.visibleSpanSummary().second_window_len);
    try std.testing.expect(!sample.usesWrappedStorageWindow());

    var full_preview: [fifo_capacity]u8 = [_]u8{0} ** fifo_capacity;
    const full_preview_result = sample.previewInto(full_preview[0..]);
    try std.testing.expectEqual(@as(usize, fifo_capacity), full_preview_result.copied);
    try std.testing.expectEqual(@as(usize, fifo_capacity), full_preview_result.total_visible);
    try std.testing.expect(!full_preview_result.truncated);

    try std.testing.expectEqual(@as(?u8, 0), sample.skipByte());
    try std.testing.expectEqual(@as(usize, 1), sample.available());
    try std.testing.expectEqual(@as(usize, fifo_capacity - 1), sample.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 0), sample.visibleSpanSummary().second_window_len);
    try std.testing.expect(!sample.usesWrappedStorageWindow());
    try std.testing.expect(sample.pushByte(200));
    try std.testing.expectEqual(@as(usize, 0), sample.available());
    try std.testing.expectEqual(@as(usize, fifo_capacity - 1), sample.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 1), sample.visibleSpanSummary().second_window_len);
    try std.testing.expect(sample.usesWrappedStorageWindow());

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

test "bytestream fifo sample keeps occupancy review helper explicit" {
    var sample = BytestreamFifoSample{};

    const cold = sample.occupancySummary();
    try std.testing.expectEqual(@as(usize, 0), cold.used);
    try std.testing.expectEqual(@as(usize, fifo_capacity), cold.available);
    try std.testing.expect(cold.empty);
    try std.testing.expect(!cold.full);
    try std.testing.expect(!cold.wrapped_window);

    try sample.init();
    try std.testing.expectEqual(@as(usize, 5), sample.enqueueSlice("hello"));
    const partial = sample.occupancySummary();
    try std.testing.expectEqual(@as(usize, 5), partial.used);
    try std.testing.expectEqual(@as(usize, 27), partial.available);
    try std.testing.expect(!partial.empty);
    try std.testing.expect(!partial.full);
    try std.testing.expect(!partial.wrapped_window);

    var fill_value: u8 = 0;
    while (sample.pushByte(fill_value)) : (fill_value +%= 1) {}
    const full = sample.occupancySummary();
    try std.testing.expectEqual(@as(usize, fifo_capacity), full.used);
    try std.testing.expectEqual(@as(usize, 0), full.available);
    try std.testing.expect(!full.empty);
    try std.testing.expect(full.full);
    try std.testing.expect(!full.wrapped_window);

    try std.testing.expectEqual(@as(?u8, 'h'), sample.skipByte());
    try std.testing.expect(sample.pushByte(200));
    const wrapped_full = sample.occupancySummary();
    try std.testing.expectEqual(@as(usize, fifo_capacity), wrapped_full.used);
    try std.testing.expectEqual(@as(usize, 0), wrapped_full.available);
    try std.testing.expect(!wrapped_full.empty);
    try std.testing.expect(wrapped_full.full);
    try std.testing.expect(wrapped_full.wrapped_window);

    sample.reset();
    const after_reset = sample.occupancySummary();
    try std.testing.expectEqual(@as(usize, 0), after_reset.used);
    try std.testing.expectEqual(@as(usize, fifo_capacity), after_reset.available);
    try std.testing.expect(after_reset.empty);
    try std.testing.expect(!after_reset.full);
    try std.testing.expect(!after_reset.wrapped_window);

    try sample.exit();
    const after_exit = sample.occupancySummary();
    try std.testing.expectEqual(@as(usize, 0), after_exit.used);
    try std.testing.expectEqual(@as(usize, fifo_capacity), after_exit.available);
    try std.testing.expect(after_exit.empty);
    try std.testing.expect(!after_exit.full);
    try std.testing.expect(!after_exit.wrapped_window);
}

test "bytestream fifo sample keeps remaining-capacity replay explicit" {
    var sample = BytestreamFifoSample{};

    try sample.init();
    const summary = try sample.runRemainingCapacityReplay();

    try std.testing.expectEqualSlices(u8, &.{ 'e', 'l', 'l', 'o', 0, 1, 2, 3 }, summary.drained_prefix[0..]);
    try std.testing.expectEqual(@as(usize, fifo_capacity), summary.available_after_init);
    try std.testing.expectEqual(@as(usize, 27), summary.available_after_hello);
    try std.testing.expectEqual(@as(usize, 0), summary.available_when_full);
    try std.testing.expect(!summary.wrapped_when_full);
    try std.testing.expectEqual(@as(usize, 1), summary.available_after_skip);
    try std.testing.expectEqual(@as(usize, 0), summary.available_after_wrap_refill);
    try std.testing.expect(summary.wrapped_after_wrap_refill);
    try std.testing.expectEqual(@as(usize, 8), summary.available_after_partial_drain);
    try std.testing.expectEqual(@as(usize, 24), summary.queue_len_after_partial_drain);
    try std.testing.expectEqual(@as(usize, 9), summary.visible_span_after_partial_drain.head_index);
    try std.testing.expectEqual(@as(usize, 1), summary.visible_span_after_partial_drain.tail_index);
    try std.testing.expectEqual(@as(usize, 24), summary.visible_span_after_partial_drain.total_visible);
    try std.testing.expectEqual(@as(usize, 23), summary.visible_span_after_partial_drain.first_window_len);
    try std.testing.expectEqual(@as(usize, 1), summary.visible_span_after_partial_drain.second_window_len);
    try std.testing.expect(summary.visible_span_after_partial_drain.wraps);
    try std.testing.expectEqual(@as(usize, 24), sample.count());
    try std.testing.expectEqual(@as(usize, 8), sample.available());
    try std.testing.expect(sample.usesWrappedStorageWindow());
}

test "bytestream fifo sample keeps queue-shape review helpers explicit" {
    var sample = BytestreamFifoSample{};

    try std.testing.expectEqual(@as(usize, fifo_capacity), sample.available());
    try std.testing.expectEqual(@as(usize, 0), sample.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 0), sample.visibleSpanSummary().second_window_len);
    try std.testing.expect(!sample.usesWrappedStorageWindow());

    try sample.init();
    try std.testing.expectEqual(@as(usize, fifo_capacity), sample.available());
    try std.testing.expectEqual(@as(usize, 0), sample.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 0), sample.visibleSpanSummary().second_window_len);
    try std.testing.expect(!sample.usesWrappedStorageWindow());

    const preview_boundary = try sample.runPreviewBoundaryReplay();
    try std.testing.expectEqualSlices(u8, &.{ 2, 3, 4, 5 }, preview_boundary.snapshot_prefix[0..]);
    try std.testing.expectEqualSlices(u8, &.{ 2, 3, 4, 5, 6, 7, 8, 9 }, preview_boundary.preview_prefix[0..]);
    try std.testing.expectEqual(@as(usize, 10), preview_boundary.preview_total_visible);
    try std.testing.expectEqual(@as(usize, 10), preview_boundary.queue_len_after_preview);
    try std.testing.expectEqual(@as(usize, 22), preview_boundary.available_after_preview);
    try std.testing.expectEqual(@as(usize, 7), preview_boundary.visible_span_after_preview.head_index);
    try std.testing.expectEqual(@as(usize, 17), preview_boundary.visible_span_after_preview.tail_index);
    try std.testing.expectEqual(@as(usize, 10), preview_boundary.visible_span_after_preview.total_visible);
    try std.testing.expectEqual(@as(usize, 10), preview_boundary.visible_span_after_preview.first_window_len);
    try std.testing.expectEqual(@as(usize, 0), preview_boundary.visible_span_after_preview.second_window_len);
    try std.testing.expect(!preview_boundary.visible_span_after_preview.wraps);
    try std.testing.expectEqual(@as(usize, 22), sample.available());
    try std.testing.expectEqual(@as(usize, 10), sample.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 0), sample.visibleSpanSummary().second_window_len);
    try std.testing.expect(!sample.usesWrappedStorageWindow());

    const wrapped_preview = try sample.runWrappedPreviewReplay();
    try std.testing.expectEqualSlices(u8, "hell", wrapped_preview.drained_prefix[0..]);
    try std.testing.expectEqualSlices(u8, &.{ 200, 201, 202, 203 }, wrapped_preview.refill_values[0..]);
    try std.testing.expectEqualSlices(u8, &.{ 'o', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 }, wrapped_preview.snapshot_prefix[0..]);
    try std.testing.expectEqualSlices(u8, &.{ 'o', 0, 1, 2, 3, 4, 5, 6 }, wrapped_preview.preview_prefix[0..]);
    try std.testing.expectEqual(@as(usize, fifo_capacity), wrapped_preview.preview_total_visible);
    try std.testing.expectEqual(@as(usize, fifo_capacity), wrapped_preview.queue_len_after_preview);
    try std.testing.expectEqual(@as(usize, 0), wrapped_preview.available_after_preview);
    try std.testing.expectEqual(@as(usize, 4), wrapped_preview.visible_span_after_preview.head_index);
    try std.testing.expectEqual(@as(usize, 4), wrapped_preview.visible_span_after_preview.tail_index);
    try std.testing.expectEqual(@as(usize, fifo_capacity), wrapped_preview.visible_span_after_preview.total_visible);
    try std.testing.expectEqual(@as(usize, 28), wrapped_preview.visible_span_after_preview.first_window_len);
    try std.testing.expectEqual(@as(usize, 4), wrapped_preview.visible_span_after_preview.second_window_len);
    try std.testing.expect(wrapped_preview.visible_span_after_preview.wraps);
    try std.testing.expectEqual(@as(usize, 0), sample.available());
    try std.testing.expectEqual(@as(usize, 28), sample.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 4), sample.visibleSpanSummary().second_window_len);
    try std.testing.expect(sample.usesWrappedStorageWindow());
}

test "bytestream fifo sample keeps ownership and lifetime guards explicit" {
    var sample = BytestreamFifoSample{};

    try std.testing.expectEqual(SampleStage.cold, sample.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.runAnchorReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.runPreviewBoundaryReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.runWrappedPreviewReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.exit());

    try sample.init();
    try std.testing.expectEqual(SampleStage.initialized, sample.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.init());

    _ = try sample.runAnchorReplay();
    try std.testing.expectEqual(SampleStage.replay_complete, sample.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.runPreviewBoundaryReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.runWrappedPreviewReplay());

    try sample.exit();
    try std.testing.expectEqual(SampleStage.exited, sample.stage());
    try std.testing.expectEqual(@as(usize, 0), sample.count());
    try std.testing.expectEqual(@as(usize, 1), sample.init_runs);
    try std.testing.expectEqual(@as(usize, 1), sample.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.runAnchorReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.runPreviewBoundaryReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.runWrappedPreviewReplay());
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
    try std.testing.expectEqual(@as(usize, fifo_capacity), sample.available());
    try std.testing.expectEqual(@as(usize, 0), sample.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 0), sample.visibleSpanSummary().second_window_len);
    try std.testing.expect(!sample.usesWrappedStorageWindow());

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
