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

pub const preview_boundary_focus = [_]SampleFocus{
    .wraparound_requeue,
    .non_destructive_snapshot,
    .preview_truncation,
};

pub const helper_boundary_focus = [_]SampleFocus{
    .peek_and_skip,
    .preview_truncation,
    .reset_and_replay,
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
    snapshot_before_final_drain: [fifo_capacity]u8,
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
    stage_before_replay: SampleStage,
    stage_after_replay: SampleStage,
    full_preview_len: usize,
    full_preview_total_visible: usize,
    full_preview_truncated: bool,
    full_preview_prefix: [8]u8,
    skipped_byte: u8,
    queue_len_after_skip: usize,
    short_drain_prefix: [3]u8,
    remaining_prefix: [2]u8,
    final_empty_drain_count: usize,
    queue_len_after_final_drain: usize,
    checked_focus: []const SampleFocus,
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

    pub fn isEmpty(self: *const Self) bool {
        return self.len == 0;
    }

    pub fn isFull(self: *const Self) bool {
        return self.len == capacity;
    }

    pub fn isWrapped(self: *const Self) bool {
        return self.len != 0 and self.head + self.len > capacity;
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
        if (self.isEmpty()) return error.UnexpectedEmptyQueueState;
        if (self.isFull()) return error.UnexpectedPrematureFullQueue;
        if (self.isWrapped()) return error.UnexpectedWrappedInitialFill;
        if (self.available() != capacity - len_after_initial_fill) return error.UnexpectedInitialAvailableCount;

        var first_out: [5]u8 = undefined;
        const first_drain_count = self.dequeueSlice(first_out[0..]);
        if (first_drain_count != first_out.len) return error.UnexpectedFirstDrainCount;

        var second_out: [2]u8 = undefined;
        const second_drain_count = self.dequeueSlice(second_out[0..]);
        if (second_drain_count != second_out.len) return error.UnexpectedSecondDrainCount;
        const requeue_count = self.enqueueSlice(second_out[0..]);
        if (requeue_count != second_out.len) return error.UnexpectedRequeueCount;
        if (self.isWrapped()) return error.UnexpectedPreFillWrapState;

        const skipped = self.skipByte() orelse return error.UnexpectedSkipOnEmpty;

        var fill_value: u8 = 20;
        while (self.pushByte(fill_value)) : (fill_value +%= 1) {}
        if (!self.isFull()) return error.UnexpectedNonFullQueue;
        if (!self.isWrapped()) return error.UnexpectedWraparoundState;
        if (self.isEmpty()) return error.UnexpectedEmptyFullQueue;
        if (self.count() != capacity) return error.UnexpectedFullQueueCount;
        if (self.available() != 0) return error.UnexpectedFullQueueAvailability;
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
        if (!self.isEmpty()) return error.UnexpectedResidualElements;
        if (self.isWrapped()) return error.UnexpectedResidualWrapState;
        if (self.isFull()) return error.UnexpectedFullQueueAfterDrain;
        if (self.available() != capacity) return error.UnexpectedFinalAvailableCount;

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
            .snapshot_before_final_drain = snapshot_before_final_drain,
            .fill_start = 20,
            .fill_end = fill_end,
            .final_len = final_len,
            .final_sequence = final_sequence,
            .checked_focus = reviewContract().focus,
            .storage_backing = .embedded_fixed_buffer,
        };
    }

    fn runPreviewBoundaryReplayInternal(self: *Self) !PreviewBoundarySummary {
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
        if (self.isWrapped()) return error.UnexpectedPreviewWrapState;

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

    fn runHelperBoundaryReplayInternal(self: *Self) !HelperBoundarySummary {
        self.reset();

        var fill: u8 = 0;
        while (fill < capacity) : (fill += 1) {
            if (!self.pushByte(fill)) return error.UnexpectedFullQueueFillFailure;
        }

        var full_preview_prefix: [8]u8 = [_]u8{0} ** 8;
        const full_preview = self.previewInto(full_preview_prefix[0..]);
        const skipped = self.skipByte() orelse return error.UnexpectedSkipOnEmpty;
        const queue_len_after_skip = self.count();

        self.reset();
        const hello_len = self.enqueueSlice("hello");
        if (hello_len != 5) return error.UnexpectedInitialCopyCount;

        var short_drain_prefix: [3]u8 = undefined;
        const short_drain_count = self.drain(short_drain_prefix[0..]);
        if (short_drain_count != short_drain_prefix.len) return error.UnexpectedShortDrainCount;

        var remaining_prefix: [2]u8 = undefined;
        const remaining_count = self.dequeueSlice(remaining_prefix[0..]);
        if (remaining_count != remaining_prefix.len) return error.UnexpectedRemainderDrainCount;

        const final_empty_drain_count = self.drain(short_drain_prefix[0..]);

        return .{
            .stage_before_replay = .initialized,
            .stage_after_replay = .initialized,
            .full_preview_len = full_preview.copied,
            .full_preview_total_visible = full_preview.total_visible,
            .full_preview_truncated = full_preview.truncated,
            .full_preview_prefix = full_preview_prefix,
            .skipped_byte = skipped,
            .queue_len_after_skip = queue_len_after_skip,
            .short_drain_prefix = short_drain_prefix,
            .remaining_prefix = remaining_prefix,
            .final_empty_drain_count = final_empty_drain_count,
            .queue_len_after_final_drain = self.count(),
            .checked_focus = &helper_boundary_focus,
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
        return self.runPreviewBoundaryReplayInternal();
    }

    pub fn runHelperBoundaryReplay(self: *Self) !HelperBoundarySummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;
        return self.runHelperBoundaryReplayInternal();
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