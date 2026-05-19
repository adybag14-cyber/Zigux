const std = @import("std");

pub const fifo_capacity: u8 = 32;

pub const expected_anchor_result = [_]u8{
    3,  4,  5,  6,  7,  8,  9,  0,  1,  20, 21, 22, 23, 24, 25, 26,
    27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
};

pub const StorageBacking = enum {
    embedded_fixed_buffer,
};

pub const SampleStage = enum {
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
    preview_truncation,
    remaining_capacity,
    queue_shape_boundaries,
    helper_boundaries,
    reset_and_replay,
    ownership_and_lifetime,
};

pub const SampleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    requires_runtime_substrate: bool,
    provides_selfcheck: bool,
    storage_backing: StorageBacking,
};

pub const ReviewContract = struct {
    focus: []const SampleFocus,
    non_goals: []const []const u8,
};

pub const VisibleSpanSummary = struct {
    head_index: usize,
    tail_index: usize,
    total_visible: usize,
    first_window_len: usize,
    second_window_len: usize,
    wraps: bool,
};

pub const WritableSpanSummary = struct {
    tail_index: usize,
    writable_count: usize,
    first_window_len: usize,
    second_window_len: usize,
    wraps: bool,
};

pub const OccupancySummary = struct {
    queue_len: usize,
    used: usize,
    available: usize,
    empty: bool,
    full: bool,
    wrapped: bool,
    wrapped_window: bool,
};

pub const PreviewResult = struct {
    copied: usize,
    total_visible: usize,
    truncated: bool,
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
    storage_backing: StorageBacking,
    checked_focus: [sample_review_focus.len]SampleFocus,
};

pub const PreviewBoundaryReplay = struct {
    stage_before_replay: SampleStage,
    stage_after_replay: SampleStage,
    snapshot_prefix: [4]u8,
    preview_prefix: [8]u8,
    preview_total_visible: usize,
    queue_len_after_preview: usize,
    available_after_preview: usize,
    visible_span_after_preview: VisibleSpanSummary,
};

pub const WrappedPreviewReplay = struct {
    stage_before_replay: SampleStage,
    stage_after_replay: SampleStage,
    drained_prefix: [4]u8,
    refill_values: [4]u8,
    snapshot_prefix: [12]u8,
    preview_prefix: [8]u8,
    preview_total_visible: usize,
    queue_len_after_preview: usize,
    available_after_preview: usize,
    visible_span_after_preview: VisibleSpanSummary,
};

pub const RemainingCapacityReplay = struct {
    stage_before_replay: SampleStage,
    stage_after_replay: SampleStage,
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

pub const LifecycleSummary = struct {
    stage: SampleStage,
    init_run_count: usize,
    exit_run_count: usize,
    queue_len: usize,
    storage_backing: StorageBacking,
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

pub const BytestreamFifoSample = struct {
    pub const capacity: usize = fifo_capacity;

    buf: [fifo_capacity]u8 = [_]u8{0} ** fifo_capacity,
    head: usize = 0,
    len: usize = 0,
    sample_stage: SampleStage = .cold,
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
            .focus = sample_review_focus[0..],
            .non_goals = sample_review_non_goals[0..],
        };
    }

    pub fn stage(self: *const BytestreamFifoSample) SampleStage {
        return self.sample_stage;
    }

    pub fn count(self: *const BytestreamFifoSample) usize {
        return self.len;
    }

    pub fn available(self: *const BytestreamFifoSample) usize {
        return capacity - self.len;
    }

    pub fn init(self: *BytestreamFifoSample) !void {
        if (self.sample_stage != .cold and self.sample_stage != .exited) {
            return error.InvalidLifecycleTransition;
        }
        self.reset();
        self.sample_stage = .initialized;
        self.init_runs += 1;
    }

    pub fn exit(self: *BytestreamFifoSample) !void {
        if (self.sample_stage != .initialized and self.sample_stage != .replay_complete) {
            return error.InvalidLifecycleTransition;
        }
        self.reset();
        self.sample_stage = .exited;
        self.exit_runs += 1;
    }

    pub fn reset(self: *BytestreamFifoSample) void {
        self.head = 0;
        self.len = 0;
        self.buf = [_]u8{0} ** fifo_capacity;
    }

    pub fn pushByte(self: *BytestreamFifoSample, value: u8) bool {
        if (self.len == capacity) return false;
        const tail = (self.head + self.len) % capacity;
        self.buf[tail] = value;
        self.len += 1;
        return true;
    }

    pub fn enqueueSlice(self: *BytestreamFifoSample, values: []const u8) usize {
        var copied: usize = 0;
        for (values) |value| {
            if (!self.pushByte(value)) break;
            copied += 1;
        }
        return copied;
    }

    pub fn dequeueSlice(self: *BytestreamFifoSample, out: []u8) usize {
        var copied: usize = 0;
        while (copied < out.len and self.len > 0) : (copied += 1) {
            out[copied] = self.buf[self.head];
            self.head = (self.head + 1) % capacity;
            self.len -= 1;
        }
        return copied;
    }

    pub fn drain(self: *BytestreamFifoSample, out: []u8) usize {
        return self.dequeueSlice(out);
    }

    pub fn peekByte(self: *const BytestreamFifoSample) ?u8 {
        if (self.len == 0) return null;
        return self.buf[self.head];
    }

    pub fn skipByte(self: *BytestreamFifoSample) ?u8 {
        if (self.len == 0) return null;
        const value = self.buf[self.head];
        self.head = (self.head + 1) % capacity;
        self.len -= 1;
        return value;
    }

    pub fn snapshotInto(self: *const BytestreamFifoSample, out: []u8) usize {
        const to_copy = @min(out.len, self.len);
        var i: usize = 0;
        while (i < to_copy) : (i += 1) {
            out[i] = self.buf[(self.head + i) % capacity];
        }
        return to_copy;
    }

    pub fn previewInto(self: *const BytestreamFifoSample, out: []u8) PreviewResult {
        const copied = self.snapshotInto(out);
        return .{
            .copied = copied,
            .total_visible = self.len,
            .truncated = copied < self.len,
        };
    }

    pub fn visibleSpanSummary(self: *const BytestreamFifoSample) VisibleSpanSummary {
        if (self.len == 0) {
            return .{
                .head_index = self.head,
                .tail_index = self.head,
                .total_visible = 0,
                .first_window_len = 0,
                .second_window_len = 0,
                .wraps = false,
            };
        }
        const tail = (self.head + self.len) % capacity;
        if (self.head < tail) {
            return .{
                .head_index = self.head,
                .tail_index = tail,
                .total_visible = self.len,
                .first_window_len = self.len,
                .second_window_len = 0,
                .wraps = false,
            };
        }
        if (tail == 0) {
            return .{
                .head_index = self.head,
                .tail_index = tail,
                .total_visible = self.len,
                .first_window_len = capacity - self.head,
                .second_window_len = 0,
                .wraps = false,
            };
        }
        return .{
            .head_index = self.head,
            .tail_index = tail,
            .total_visible = self.len,
            .first_window_len = capacity - self.head,
            .second_window_len = tail,
            .wraps = true,
        };
    }

    pub fn writableSpanSummary(self: *const BytestreamFifoSample) WritableSpanSummary {
        const tail = (self.head + self.len) % capacity;
        const avail = self.available();
        if (avail == 0) {
            return .{
                .tail_index = tail,
                .writable_count = 0,
                .first_window_len = 0,
                .second_window_len = 0,
                .wraps = false,
            };
        }
        if (tail < self.head) {
            return .{
                .tail_index = tail,
                .writable_count = avail,
                .first_window_len = self.head - tail,
                .second_window_len = 0,
                .wraps = false,
            };
        }
        const first = capacity - tail;
        if (self.head == 0) {
            return .{
                .tail_index = tail,
                .writable_count = avail,
                .first_window_len = avail,
                .second_window_len = 0,
                .wraps = false,
            };
        }
        return .{
            .tail_index = tail,
            .writable_count = avail,
            .first_window_len = first,
            .second_window_len = self.head,
            .wraps = true,
        };
    }

    pub fn occupancySummary(self: *const BytestreamFifoSample) OccupancySummary {
        const avail = self.available();
        const wrapped = self.usesWrappedStorageWindow();
        return .{
            .queue_len = self.len,
            .used = self.len,
            .available = avail,
            .empty = self.len == 0,
            .full = avail == 0,
            .wrapped = wrapped,
            .wrapped_window = wrapped,
        };
    }

    pub fn usesWrappedStorageWindow(self: *const BytestreamFifoSample) bool {
        return self.visibleSpanSummary().wraps;
    }

    pub fn lifecycleSummary(self: *const BytestreamFifoSample) LifecycleSummary {
        return .{
            .stage = self.sample_stage,
            .init_run_count = self.init_runs,
            .exit_run_count = self.exit_runs,
            .queue_len = self.len,
            .storage_backing = .embedded_fixed_buffer,
        };
    }

    pub fn runPreviewBoundaryReplay(self: *BytestreamFifoSample) !PreviewBoundaryReplay {
        if (self.sample_stage != .initialized) return error.InvalidLifecycleTransition;
        const stage_before = self.sample_stage;
        self.reset();
        _ = self.enqueueSlice("hello");
        var value: u8 = 0;
        while (value < 10) : (value += 1) {
            _ = self.pushByte(value);
        }
        var discard: [7]u8 = undefined;
        _ = self.dequeueSlice(discard[0..]);
        _ = self.enqueueSlice(&.{ 0, 1 });

        var snapshot: [4]u8 = [_]u8{0} ** 4;
        _ = self.snapshotInto(snapshot[0..]);
        var preview: [8]u8 = [_]u8{0} ** 8;
        const preview_result = self.previewInto(preview[0..]);

        return .{
            .stage_before_replay = stage_before,
            .stage_after_replay = self.sample_stage,
            .snapshot_prefix = snapshot,
            .preview_prefix = preview,
            .preview_total_visible = preview_result.total_visible,
            .queue_len_after_preview = self.len,
            .available_after_preview = self.available(),
            .visible_span_after_preview = self.visibleSpanSummary(),
        };
    }

    pub fn runWrappedPreviewReplay(self: *BytestreamFifoSample) !WrappedPreviewReplay {
        if (self.sample_stage != .initialized) return error.InvalidLifecycleTransition;
        const stage_before = self.sample_stage;
        self.reset();
        _ = self.enqueueSlice("hello");
        var fill: u8 = 0;
        while (fill < 28) : (fill += 1) {
            _ = self.pushByte(fill);
        }
        var drained: [4]u8 = undefined;
        _ = self.dequeueSlice(drained[0..]);
        const refill_values = [_]u8{ 200, 201, 202, 203 };
        _ = self.enqueueSlice(refill_values[0..]);

        var snapshot: [12]u8 = [_]u8{0} ** 12;
        _ = self.snapshotInto(snapshot[0..]);
        var preview: [8]u8 = [_]u8{0} ** 8;
        const preview_result = self.previewInto(preview[0..]);

        return .{
            .stage_before_replay = stage_before,
            .stage_after_replay = self.sample_stage,
            .drained_prefix = drained,
            .refill_values = refill_values,
            .snapshot_prefix = snapshot,
            .preview_prefix = preview,
            .preview_total_visible = preview_result.total_visible,
            .queue_len_after_preview = self.len,
            .available_after_preview = self.available(),
            .visible_span_after_preview = self.visibleSpanSummary(),
        };
    }

    pub fn runRemainingCapacityReplay(self: *BytestreamFifoSample) !RemainingCapacityReplay {
        if (self.sample_stage != .initialized) return error.InvalidLifecycleTransition;
        const stage_before = self.sample_stage;
        self.reset();
        const available_after_init = self.available();
        _ = self.enqueueSlice("hello");
        const available_after_hello = self.available();
        var fill: u8 = 0;
        while (self.pushByte(fill)) : (fill += 1) {}
        const available_when_full = self.available();
        const wrapped_when_full = self.usesWrappedStorageWindow();
        _ = self.skipByte();
        const available_after_skip = self.available();
        _ = self.pushByte(200);
        const available_after_wrap_refill = self.available();
        const wrapped_after_wrap_refill = self.usesWrappedStorageWindow();
        var drained: [8]u8 = undefined;
        _ = self.dequeueSlice(drained[0..]);

        return .{
            .stage_before_replay = stage_before,
            .stage_after_replay = self.sample_stage,
            .drained_prefix = drained,
            .available_after_init = available_after_init,
            .available_after_hello = available_after_hello,
            .available_when_full = available_when_full,
            .available_after_skip = available_after_skip,
            .available_after_wrap_refill = available_after_wrap_refill,
            .available_after_partial_drain = self.available(),
            .queue_len_after_partial_drain = self.len,
            .visible_span_after_partial_drain = self.visibleSpanSummary(),
            .wrapped_when_full = wrapped_when_full,
            .wrapped_after_wrap_refill = wrapped_after_wrap_refill,
        };
    }

    pub fn runAnchorReplay(self: *BytestreamFifoSample) !ReplaySummary {
        if (self.sample_stage != .initialized) return error.InvalidLifecycleTransition;
        self.reset();
        const stage_before = self.sample_stage;
        const initial_string_copy_count = self.enqueueSlice("hello");
        var value: u8 = 0;
        while (value < 10) : (value += 1) {
            _ = self.pushByte(value);
        }
        const len_after_initial_fill = self.len;

        var first_out: [5]u8 = [_]u8{0} ** 5;
        const first_drain_count = self.dequeueSlice(first_out[0..]);

        var second_out: [2]u8 = [_]u8{0} ** 2;
        const second_drain_count = self.dequeueSlice(second_out[0..]);
        const requeue_count = self.enqueueSlice(second_out[0..]);
        const skipped_byte = self.skipByte() orelse return error.UnexpectedEmptyQueue;
        const peek_value = self.peekByte() orelse return error.UnexpectedEmptyQueue;

        const fill_start: u8 = 20;
        var fill_value: u8 = fill_start;
        while (fill_value <= 42) : (fill_value += 1) {
            _ = self.pushByte(fill_value);
        }
        const fill_end: u8 = 42;

        var preview_prefix: [8]u8 = [_]u8{0} ** 8;
        const preview_result = self.previewInto(preview_prefix[0..]);

        var snapshot: [fifo_capacity]u8 = [_]u8{0} ** fifo_capacity;
        const snapshot_len = self.snapshotInto(snapshot[0..]);

        var final_sequence: [fifo_capacity]u8 = [_]u8{0} ** fifo_capacity;
        const final_len = self.dequeueSlice(final_sequence[0..]);
        self.sample_stage = .replay_complete;

        return .{
            .anchor = descriptor().anchor,
            .stage_before_replay = stage_before,
            .stage_after_replay = self.sample_stage,
            .initial_string_copy_count = initial_string_copy_count,
            .len_after_initial_fill = len_after_initial_fill,
            .first_out = first_out,
            .first_drain_count = first_drain_count,
            .second_out = second_out,
            .second_drain_count = second_drain_count,
            .requeue_count = requeue_count,
            .skipped_byte = skipped_byte,
            .peek_value = peek_value,
            .preview_len = preview_result.copied,
            .preview_total_visible = preview_result.total_visible,
            .preview_truncated = preview_result.truncated,
            .preview_prefix = preview_prefix,
            .snapshot_len = snapshot_len,
            .snapshot_before_final_drain = snapshot,
            .fill_start = fill_start,
            .fill_end = fill_end,
            .final_len = final_len,
            .final_sequence = final_sequence,
            .storage_backing = .embedded_fixed_buffer,
            .checked_focus = sample_review_focus,
        };
    }
};

test "bytestream fifo sample replays the Linux anchor result sequence" {
    const expected_focus = [_]SampleFocus{
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

    var sample = BytestreamFifoSample{};
    try sample.init();
    const replay = try sample.runAnchorReplay();

    try std.testing.expectEqualStrings(BytestreamFifoSample.descriptor().anchor, replay.anchor);
    try std.testing.expectEqual(@as(usize, expected_focus.len), replay.checked_focus.len);
    for (expected_focus, replay.checked_focus) |expected, actual| {
        try std.testing.expectEqual(expected, actual);
    }
    try std.testing.expectEqual(SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(SampleStage.replay_complete, replay.stage_after_replay);
    try std.testing.expectEqual(@as(usize, 15), replay.len_after_initial_fill);
    try std.testing.expectEqualStrings("hello", replay.first_out[0..]);
    try std.testing.expectEqualSlices(u8, &.{ 0, 1 }, replay.second_out[0..]);
    try std.testing.expectEqual(@as(usize, fifo_capacity), replay.final_len);
    try std.testing.expectEqualSlices(u8, expected_anchor_result[0..], replay.final_sequence[0..]);
}

test "bytestream fifo sample keeps preview and wrapped-span boundaries reviewable at sample root" {
    var sample = BytestreamFifoSample{};

    try std.testing.expectError(error.InvalidLifecycleTransition, sample.runPreviewBoundaryReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.runWrappedPreviewReplay());

    try sample.init();
    const preview = try sample.runPreviewBoundaryReplay();
    try std.testing.expectEqual(SampleStage.initialized, preview.stage_before_replay);
    try std.testing.expectEqual(SampleStage.initialized, preview.stage_after_replay);
    try std.testing.expectEqual(SampleStage.initialized, sample.stage());
    try std.testing.expectEqualSlices(u8, &.{ 2, 3, 4, 5 }, preview.snapshot_prefix[0..]);
    try std.testing.expectEqualSlices(u8, &.{ 2, 3, 4, 5, 6, 7, 8, 9 }, preview.preview_prefix[0..]);
    try std.testing.expectEqual(@as(usize, 10), preview.preview_total_visible);
    try std.testing.expectEqual(@as(usize, 10), preview.queue_len_after_preview);
    try std.testing.expectEqual(@as(usize, 22), preview.available_after_preview);
    try std.testing.expectEqual(@as(usize, 7), preview.visible_span_after_preview.head_index);
    try std.testing.expectEqual(@as(usize, 17), preview.visible_span_after_preview.tail_index);
    try std.testing.expectEqual(@as(usize, 10), preview.visible_span_after_preview.total_visible);
    try std.testing.expectEqual(@as(usize, 10), preview.visible_span_after_preview.first_window_len);
    try std.testing.expectEqual(@as(usize, 0), preview.visible_span_after_preview.second_window_len);
    try std.testing.expect(!preview.visible_span_after_preview.wraps);
    const preview_occupancy = sample.occupancySummary();
    try std.testing.expectEqual(@as(usize, 10), preview_occupancy.queue_len);
    try std.testing.expectEqual(@as(usize, 10), preview_occupancy.used);
    try std.testing.expectEqual(@as(usize, 22), preview_occupancy.available);
    try std.testing.expect(!preview_occupancy.empty);
    try std.testing.expect(!preview_occupancy.full);
    try std.testing.expect(!preview_occupancy.wrapped);
    try std.testing.expect(!preview_occupancy.wrapped_window);
    const preview_writable = sample.writableSpanSummary();
    try std.testing.expectEqual(@as(usize, 17), preview_writable.tail_index);
    try std.testing.expectEqual(@as(usize, 22), preview_writable.writable_count);
    try std.testing.expectEqual(@as(usize, 15), preview_writable.first_window_len);
    try std.testing.expectEqual(@as(usize, 7), preview_writable.second_window_len);
    try std.testing.expect(preview_writable.wraps);

    const wrapped = try sample.runWrappedPreviewReplay();
    try std.testing.expectEqual(SampleStage.initialized, wrapped.stage_before_replay);
    try std.testing.expectEqual(SampleStage.initialized, wrapped.stage_after_replay);
    try std.testing.expectEqual(SampleStage.initialized, sample.stage());
    try std.testing.expectEqualSlices(u8, "hell", wrapped.drained_prefix[0..]);
    try std.testing.expectEqualSlices(u8, &.{ 200, 201, 202, 203 }, wrapped.refill_values[0..]);
    try std.testing.expectEqualSlices(u8, &.{ 'o', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 }, wrapped.snapshot_prefix[0..]);
    try std.testing.expectEqualSlices(u8, &.{ 'o', 0, 1, 2, 3, 4, 5, 6 }, wrapped.preview_prefix[0..]);
    try std.testing.expectEqual(@as(usize, fifo_capacity), wrapped.preview_total_visible);
    try std.testing.expectEqual(@as(usize, fifo_capacity), wrapped.queue_len_after_preview);
    try std.testing.expectEqual(@as(usize, 0), wrapped.available_after_preview);
    try std.testing.expectEqual(@as(usize, 4), wrapped.visible_span_after_preview.head_index);
    try std.testing.expectEqual(@as(usize, 4), wrapped.visible_span_after_preview.tail_index);
    try std.testing.expectEqual(@as(usize, fifo_capacity), wrapped.visible_span_after_preview.total_visible);
    try std.testing.expectEqual(@as(usize, 28), wrapped.visible_span_after_preview.first_window_len);
    try std.testing.expectEqual(@as(usize, 4), wrapped.visible_span_after_preview.second_window_len);
    try std.testing.expect(wrapped.visible_span_after_preview.wraps);
    const wrapped_occupancy = sample.occupancySummary();
    try std.testing.expectEqual(@as(usize, fifo_capacity), wrapped_occupancy.queue_len);
    try std.testing.expectEqual(@as(usize, fifo_capacity), wrapped_occupancy.used);
    try std.testing.expectEqual(@as(usize, 0), wrapped_occupancy.available);
    try std.testing.expect(!wrapped_occupancy.empty);
    try std.testing.expect(wrapped_occupancy.full);
    try std.testing.expect(wrapped_occupancy.wrapped);
    try std.testing.expect(wrapped_occupancy.wrapped_window);
    try std.testing.expect(sample.usesWrappedStorageWindow());
}

test "bytestream fifo sample keeps helper, capacity, and lifecycle boundaries reviewable at sample root" {
    var sample = BytestreamFifoSample{};

    try std.testing.expectEqual(@as(?u8, null), sample.peekByte());
    try std.testing.expectEqual(@as(?u8, null), sample.skipByte());
    try std.testing.expectEqual(@as(usize, 0), sample.enqueueSlice(&.{}));
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.exit());
    const cold_occupancy = sample.occupancySummary();
    try std.testing.expectEqual(@as(usize, 0), cold_occupancy.queue_len);
    try std.testing.expectEqual(@as(usize, 0), cold_occupancy.used);
    try std.testing.expectEqual(@as(usize, fifo_capacity), cold_occupancy.available);
    try std.testing.expect(cold_occupancy.empty);
    try std.testing.expect(!cold_occupancy.full);
    try std.testing.expect(!cold_occupancy.wrapped);
    try std.testing.expect(!cold_occupancy.wrapped_window);

    try sample.init();
    const initialized_occupancy = sample.occupancySummary();
    try std.testing.expectEqual(@as(usize, 0), initialized_occupancy.queue_len);
    try std.testing.expectEqual(@as(usize, 0), initialized_occupancy.used);
    try std.testing.expectEqual(@as(usize, fifo_capacity), initialized_occupancy.available);
    try std.testing.expect(initialized_occupancy.empty);
    try std.testing.expect(!initialized_occupancy.full);
    try std.testing.expect(!initialized_occupancy.wrapped);
    try std.testing.expect(!initialized_occupancy.wrapped_window);

    const capacity_replay = try sample.runRemainingCapacityReplay();
    try std.testing.expectEqual(SampleStage.initialized, capacity_replay.stage_before_replay);
    try std.testing.expectEqual(SampleStage.initialized, capacity_replay.stage_after_replay);
    try std.testing.expectEqual(SampleStage.initialized, sample.stage());
    try std.testing.expectEqual(@as(usize, fifo_capacity), capacity_replay.available_after_init);
    try std.testing.expectEqual(@as(usize, fifo_capacity - 5), capacity_replay.available_after_hello);
    try std.testing.expectEqual(@as(usize, 0), capacity_replay.available_when_full);
    try std.testing.expectEqual(@as(usize, 1), capacity_replay.available_after_skip);
    try std.testing.expectEqual(@as(usize, 0), capacity_replay.available_after_wrap_refill);
    try std.testing.expectEqual(@as(usize, 8), capacity_replay.available_after_partial_drain);
    try std.testing.expectEqual(@as(usize, 24), capacity_replay.queue_len_after_partial_drain);
    try std.testing.expect(!capacity_replay.wrapped_when_full);
    try std.testing.expect(capacity_replay.wrapped_after_wrap_refill);
    try std.testing.expectEqualSlices(u8, "ello", capacity_replay.drained_prefix[0..4]);
    try std.testing.expectEqualSlices(u8, &.{ 0, 1, 2, 3 }, capacity_replay.drained_prefix[4..]);
    try std.testing.expectEqual(@as(usize, 9), capacity_replay.visible_span_after_partial_drain.head_index);
    try std.testing.expectEqual(@as(usize, 1), capacity_replay.visible_span_after_partial_drain.tail_index);
    try std.testing.expectEqual(@as(usize, 23), capacity_replay.visible_span_after_partial_drain.first_window_len);
    try std.testing.expectEqual(@as(usize, 1), capacity_replay.visible_span_after_partial_drain.second_window_len);
    try std.testing.expect(capacity_replay.visible_span_after_partial_drain.wraps);
    const partial_drain_occupancy = sample.occupancySummary();
    try std.testing.expectEqual(@as(usize, 24), partial_drain_occupancy.queue_len);
    try std.testing.expectEqual(@as(usize, 24), partial_drain_occupancy.used);
    try std.testing.expectEqual(@as(usize, 8), partial_drain_occupancy.available);
    try std.testing.expect(!partial_drain_occupancy.empty);
    try std.testing.expect(!partial_drain_occupancy.full);
    try std.testing.expect(partial_drain_occupancy.wrapped);
    try std.testing.expect(partial_drain_occupancy.wrapped_window);
    const partial_drain_writable = sample.writableSpanSummary();
    try std.testing.expectEqual(@as(usize, 1), partial_drain_writable.tail_index);
    try std.testing.expectEqual(@as(usize, 8), partial_drain_writable.writable_count);
    try std.testing.expectEqual(@as(usize, 8), partial_drain_writable.first_window_len);
    try std.testing.expectEqual(@as(usize, 0), partial_drain_writable.second_window_len);
    try std.testing.expect(!partial_drain_writable.wraps);

    sample.reset();
    try std.testing.expectEqual(@as(usize, 5), sample.enqueueSlice("hello"));
    var short_drain: [3]u8 = undefined;
    try std.testing.expectEqual(@as(usize, short_drain.len), sample.drain(short_drain[0..]));
    try std.testing.expectEqualSlices(u8, "hel", short_drain[0..]);
    try std.testing.expectEqual(@as(?u8, 'l'), sample.peekByte());

    var remainder: [2]u8 = undefined;
    try std.testing.expectEqual(@as(usize, remainder.len), sample.dequeueSlice(remainder[0..]));
    try std.testing.expectEqualSlices(u8, "lo", remainder[0..]);
    try std.testing.expectEqual(@as(usize, 0), sample.drain(short_drain[0..]));

    _ = try sample.runAnchorReplay();
    const lifecycle = sample.lifecycleSummary();
    try std.testing.expectEqual(SampleStage.replay_complete, lifecycle.stage);
    try std.testing.expectEqual(@as(usize, 1), lifecycle.init_run_count);
    try std.testing.expectEqual(@as(usize, 0), lifecycle.exit_run_count);
    try std.testing.expectEqual(@as(usize, 0), lifecycle.queue_len);
    try std.testing.expectEqual(StorageBacking.embedded_fixed_buffer, lifecycle.storage_backing);
    const replay_complete_occupancy = sample.occupancySummary();
    try std.testing.expectEqual(@as(usize, 0), replay_complete_occupancy.queue_len);
    try std.testing.expectEqual(@as(usize, 0), replay_complete_occupancy.used);
    try std.testing.expectEqual(@as(usize, fifo_capacity), replay_complete_occupancy.available);
    try std.testing.expect(replay_complete_occupancy.empty);
    try std.testing.expect(!replay_complete_occupancy.full);
    try std.testing.expect(!replay_complete_occupancy.wrapped);
    try std.testing.expect(!replay_complete_occupancy.wrapped_window);

    try sample.exit();
    try std.testing.expectEqual(SampleStage.exited, sample.stage());
    try std.testing.expectEqual(@as(usize, 1), sample.exit_runs);
    try std.testing.expectEqual(@as(usize, fifo_capacity), sample.available());
    const exited_occupancy = sample.occupancySummary();
    try std.testing.expectEqual(@as(usize, 0), exited_occupancy.queue_len);
    try std.testing.expectEqual(@as(usize, 0), exited_occupancy.used);
    try std.testing.expectEqual(@as(usize, fifo_capacity), exited_occupancy.available);
    try std.testing.expect(exited_occupancy.empty);
    try std.testing.expect(!exited_occupancy.full);
    try std.testing.expect(!exited_occupancy.wrapped);
    try std.testing.expect(!exited_occupancy.wrapped_window);
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.runAnchorReplay());
}
