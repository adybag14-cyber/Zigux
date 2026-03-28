const std = @import("std");
const abi = @import("abi_bindings");
const chrdev_complete_plan = @import("chrdev_complete_plan");

fn mapCompleteFlags(complete_flags: u32) u32 {
    var flags: u32 = 0;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_TRUNCATED) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_TRUNCATED;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_FOUND) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_FOUND;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_EXHAUSTED) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_EXHAUSTED;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_HIT) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_HIT;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_PERMITTED) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_PERMITTED;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_DENIED) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_DENIED;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_ROUTABLE) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_ROUTABLE;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_BLOCKED) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_BLOCKED;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_DISPATCHABLE) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_DISPATCHABLE;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_RESUMED) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_RESUMED;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_CONTINUABLE) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_CONTINUABLE;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_COMPLETES) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_COMPLETES;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_PROGRESSED) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_PROGRESSED;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_STALLED) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_STALLED;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_COMPLETE_OK) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_COMPLETE_OK;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_RETRYABLE) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_RETRYABLE;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_RETRY_PLANNED) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_RETRY_PLANNED;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_RETRY_EXHAUSTED) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_RETRY_EXHAUSTED;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_BACKOFF_APPLIED) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_BACKOFF_APPLIED;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_FAILS) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_FAILS;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_REQUEUEABLE) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_REQUEUEABLE;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_REQUEUE_PLANNED) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_REQUEUE_PLANNED;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_DELAYED) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_DELAYED;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_SATURATED) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_SATURATED;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_DROPPED) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_DROPPED;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_COMPLETE) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_COMPLETE;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_COMPLETION_PLANNED) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_COMPLETION_PLANNED;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_DEFERRED_COMPLETION) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_DEFERRED_COMPLETION;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_FAILURE_COMPLETION) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_FAILURE_COMPLETION;
    if ((complete_flags & abi.CHRDEV_COMPLETE_FLAG_FINALIZED) != 0) flags |= abi.CHRDEV_NOTIFY_FLAG_FINALIZED;
    return flags;
}

fn statusMask(completion_status: u32) u32 {
    return switch (completion_status) {
        abi.CHRDEV_COMPLETE_STATUS_OK => abi.CHRDEV_NOTIFY_MASK_SUCCESS,
        abi.CHRDEV_COMPLETE_STATUS_DEFERRED => abi.CHRDEV_NOTIFY_MASK_DEFERRED,
        abi.CHRDEV_COMPLETE_STATUS_FAILED => abi.CHRDEV_NOTIFY_MASK_FAILURE,
        else => 0,
    };
}

pub fn viewFromBits(
    bits: []const usize,
    major: u32,
    first_minor: u32,
    minor_count: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    target_minor: u32,
    requested_mode: u32,
    supported_mode: u32,
    available_ops: u32,
    io_op: u32,
    requested_bytes: u32,
    max_chunk_bytes: u32,
    file_offset: u64,
    bytes_completed: u32,
    max_segments: u32,
    resume_passes: u32,
    retry_budget: u32,
    stall_budget: u32,
    backoff_quanta: u32,
    queue_depth: u32,
    queue_capacity: u32,
    requeue_budget: u32,
    completion_cookie: u64,
    completion_budget: u32,
    notify_mask: u32,
    notify_budget: u32,
    notify_cookie: u64,
) abi.ChrdevNotifyView {
    return .{
        .bits_addr = if (bits.len == 0) 0 else @intFromPtr(&bits[0]),
        .major = major,
        .first_minor = first_minor,
        .minor_count = minor_count,
        .max_scan = max_scan,
        .request_count = request_count,
        .policy = policy,
        .target_minor = target_minor,
        .requested_mode = requested_mode,
        .supported_mode = supported_mode,
        .available_ops = available_ops,
        .io_op = io_op,
        .requested_bytes = requested_bytes,
        .max_chunk_bytes = max_chunk_bytes,
        .file_offset = file_offset,
        .bytes_completed = bytes_completed,
        .max_segments = max_segments,
        .resume_passes = resume_passes,
        .retry_budget = retry_budget,
        .stall_budget = stall_budget,
        .backoff_quanta = backoff_quanta,
        .queue_depth = queue_depth,
        .queue_capacity = queue_capacity,
        .requeue_budget = requeue_budget,
        .completion_cookie = completion_cookie,
        .completion_budget = completion_budget,
        .notify_mask = notify_mask,
        .notify_cookie = notify_cookie,
        .notify_budget = notify_budget,
        .reserved = 0,
    };
}

pub fn asChrdevCompleteView(view: abi.ChrdevNotifyView) abi.ChrdevCompleteView {
    if (view.reserved != 0) {
        return .{
            .bits_addr = 0,
            .major = 0,
            .first_minor = 0,
            .minor_count = 0,
            .max_scan = 0,
            .request_count = 0,
            .policy = 0,
            .target_minor = 0,
            .requested_mode = 0,
            .supported_mode = 0,
            .available_ops = 0,
            .io_op = 0,
            .requested_bytes = 0,
            .max_chunk_bytes = 0,
            .file_offset = 0,
            .bytes_completed = 0,
            .max_segments = 0,
            .resume_passes = 0,
            .retry_budget = 0,
            .stall_budget = 0,
            .backoff_quanta = 0,
            .queue_depth = 0,
            .queue_capacity = 0,
            .requeue_budget = 0,
            .completion_cookie = 0,
            .completion_budget = 0,
            .reserved = 0,
        };
    }

    return .{
        .bits_addr = view.bits_addr,
        .major = view.major,
        .first_minor = view.first_minor,
        .minor_count = view.minor_count,
        .max_scan = view.max_scan,
        .request_count = view.request_count,
        .policy = view.policy,
        .target_minor = view.target_minor,
        .requested_mode = view.requested_mode,
        .supported_mode = view.supported_mode,
        .available_ops = view.available_ops,
        .io_op = view.io_op,
        .requested_bytes = view.requested_bytes,
        .max_chunk_bytes = view.max_chunk_bytes,
        .file_offset = view.file_offset,
        .bytes_completed = view.bytes_completed,
        .max_segments = view.max_segments,
        .resume_passes = view.resume_passes,
        .retry_budget = view.retry_budget,
        .stall_budget = view.stall_budget,
        .backoff_quanta = view.backoff_quanta,
        .queue_depth = view.queue_depth,
        .queue_capacity = view.queue_capacity,
        .requeue_budget = view.requeue_budget,
        .completion_cookie = view.completion_cookie,
        .completion_budget = view.completion_budget,
        .reserved = 0,
    };
}

pub fn isValid(view: abi.ChrdevNotifyView) bool {
    if (view.reserved != 0) return false;
    if ((view.notify_mask & ~(abi.CHRDEV_NOTIFY_MASK_SUCCESS | abi.CHRDEV_NOTIFY_MASK_DEFERRED | abi.CHRDEV_NOTIFY_MASK_FAILURE)) != 0) return false;
    return chrdev_complete_plan.isValid(asChrdevCompleteView(view));
}

pub fn summarize(view: abi.ChrdevNotifyView) abi.ChrdevNotifySummary {
    if (!isValid(view)) {
        return .{
            .major = 0,
            .target_minor = 0,
            .selected_count = 0,
            .resolved_index = abi.CHRDEV_NOTIFY_INDEX_NONE,
            .resolved_dev = 0,
            .granted_mode = 0,
            .io_op = 0,
            .requested_bytes = 0,
            .start_offset = 0,
            .next_offset = 0,
            .initial_bytes_completed = 0,
            .final_bytes_completed = 0,
            .pass_count = 0,
            .issued_bytes = 0,
            .remaining_bytes = 0,
            .projected_remaining_bytes = 0,
            .entry_ops = 0,
            .data_ops = 0,
            .exit_ops = 0,
            .blocked_ops = 0,
            .retry_count = 0,
            .stall_count = 0,
            .requeue_count = 0,
            .queue_depth_before = 0,
            .queue_depth_after = 0,
            .remaining_retry_budget = 0,
            .remaining_requeue_budget = 0,
            .backoff_ticks = 0,
            .completion_cookie = 0,
            .completion_status = abi.CHRDEV_COMPLETE_STATUS_NONE,
            .completion_count = 0,
            .deferred_count = 0,
            .failure_count = 0,
            .remaining_completion_budget = 0,
            .notify_mask = 0,
            .matched_notify_mask = 0,
            .notify_status = abi.CHRDEV_NOTIFY_STATUS_NONE,
            .notify_count = 0,
            .deferred_notify_count = 0,
            .dropped_notify_count = 0,
            .remaining_notify_budget = 0,
            .notify_cookie = 0,
            .flags = 0,
        };
    }

    const complete_summary = chrdev_complete_plan.summarize(asChrdevCompleteView(view));
    var flags = mapCompleteFlags(complete_summary.flags);
    const matched_notify_mask = view.notify_mask & statusMask(complete_summary.completion_status);
    var notify_status: u32 = abi.CHRDEV_NOTIFY_STATUS_NONE;
    var notify_count: u32 = 0;
    var deferred_notify_count: u32 = 0;
    var dropped_notify_count: u32 = 0;
    var remaining_notify_budget = view.notify_budget;

    if (matched_notify_mask != 0) {
        flags |= abi.CHRDEV_NOTIFY_FLAG_MATCHED_NOTIFY;
        switch (complete_summary.completion_status) {
            abi.CHRDEV_COMPLETE_STATUS_DEFERRED => {
                notify_status = abi.CHRDEV_NOTIFY_STATUS_DEFERRED;
                deferred_notify_count = 1;
            },
            abi.CHRDEV_COMPLETE_STATUS_OK, abi.CHRDEV_COMPLETE_STATUS_FAILED => {
                if (view.notify_budget != 0) {
                    notify_status = abi.CHRDEV_NOTIFY_STATUS_DELIVERED;
                    notify_count = 1;
                    remaining_notify_budget = view.notify_budget - 1;
                    flags |= abi.CHRDEV_NOTIFY_FLAG_NOTIFY_PLANNED;
                } else {
                    notify_status = abi.CHRDEV_NOTIFY_STATUS_DROPPED;
                    dropped_notify_count = 1;
                }
            },
            else => {},
        }
    }

    return .{
        .major = complete_summary.major,
        .target_minor = complete_summary.target_minor,
        .selected_count = complete_summary.selected_count,
        .resolved_index = if (complete_summary.resolved_index == abi.CHRDEV_COMPLETE_INDEX_NONE) abi.CHRDEV_NOTIFY_INDEX_NONE else complete_summary.resolved_index,
        .resolved_dev = complete_summary.resolved_dev,
        .granted_mode = complete_summary.granted_mode,
        .io_op = complete_summary.io_op,
        .requested_bytes = complete_summary.requested_bytes,
        .start_offset = complete_summary.start_offset,
        .next_offset = complete_summary.next_offset,
        .initial_bytes_completed = complete_summary.initial_bytes_completed,
        .final_bytes_completed = complete_summary.final_bytes_completed,
        .pass_count = complete_summary.pass_count,
        .issued_bytes = complete_summary.issued_bytes,
        .remaining_bytes = complete_summary.remaining_bytes,
        .projected_remaining_bytes = complete_summary.projected_remaining_bytes,
        .entry_ops = complete_summary.entry_ops,
        .data_ops = complete_summary.data_ops,
        .exit_ops = complete_summary.exit_ops,
        .blocked_ops = complete_summary.blocked_ops,
        .retry_count = complete_summary.retry_count,
        .stall_count = complete_summary.stall_count,
        .requeue_count = complete_summary.requeue_count,
        .queue_depth_before = complete_summary.queue_depth_before,
        .queue_depth_after = complete_summary.queue_depth_after,
        .remaining_retry_budget = complete_summary.remaining_retry_budget,
        .remaining_requeue_budget = complete_summary.remaining_requeue_budget,
        .backoff_ticks = complete_summary.backoff_ticks,
        .completion_cookie = complete_summary.completion_cookie,
        .completion_status = complete_summary.completion_status,
        .completion_count = complete_summary.completion_count,
        .deferred_count = complete_summary.deferred_count,
        .failure_count = complete_summary.failure_count,
        .remaining_completion_budget = complete_summary.remaining_completion_budget,
        .notify_mask = view.notify_mask,
        .matched_notify_mask = matched_notify_mask,
        .notify_status = notify_status,
        .notify_count = notify_count,
        .deferred_notify_count = deferred_notify_count,
        .dropped_notify_count = dropped_notify_count,
        .remaining_notify_budget = remaining_notify_budget,
        .notify_cookie = view.notify_cookie,
        .flags = flags,
    };
}

test "phase3 chrdev notify delivered and deferred summaries stay bounded" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};

    const delivered_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA);
    const delivered_summary = summarize(delivered_view);
    try std.testing.expect(isValid(delivered_view));
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_STATUS_DELIVERED), delivered_summary.notify_status);
    try std.testing.expectEqual(@as(u32, 1), delivered_summary.notify_count);
    try std.testing.expectEqual(@as(u32, 0), delivered_summary.remaining_notify_budget);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_MASK_SUCCESS), delivered_summary.matched_notify_mask);
    try std.testing.expect((delivered_summary.flags & abi.CHRDEV_NOTIFY_FLAG_MATCHED_NOTIFY) != 0);
    try std.testing.expect((delivered_summary.flags & abi.CHRDEV_NOTIFY_FLAG_NOTIFY_PLANNED) != 0);

    const deferred_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 36, 8, 1024, 4, 1, 1, 1, 1, 0, 1, 4, 2, 0x3333, 1, abi.CHRDEV_NOTIFY_MASK_DEFERRED, 0, 0xBBBB);
    const deferred_summary = summarize(deferred_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_STATUS_DEFERRED), deferred_summary.notify_status);
    try std.testing.expectEqual(@as(u32, 1), deferred_summary.deferred_notify_count);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_MASK_DEFERRED), deferred_summary.matched_notify_mask);
    try std.testing.expect((deferred_summary.flags & abi.CHRDEV_NOTIFY_FLAG_MATCHED_NOTIFY) != 0);
    try std.testing.expect((deferred_summary.flags & abi.CHRDEV_NOTIFY_FLAG_NOTIFY_PLANNED) == 0);
}

test "phase3 chrdev notify dropped and unmatched summaries stay explicit" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const dropped_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 0, 0xCCCC);
    const dropped_summary = summarize(dropped_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_STATUS_DROPPED), dropped_summary.notify_status);
    try std.testing.expectEqual(@as(u32, 1), dropped_summary.dropped_notify_count);
    try std.testing.expectEqual(@as(u32, 0), dropped_summary.remaining_notify_budget);

    const failed_view = viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, abi.CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xDDDD);
    const failed_summary = summarize(failed_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_STATUS_DELIVERED), failed_summary.notify_status);
    try std.testing.expectEqual(@as(u32, 1), failed_summary.notify_count);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_MASK_FAILURE), failed_summary.matched_notify_mask);

    const unmatched_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xEEEE);
    const unmatched_summary = summarize(unmatched_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_STATUS_NONE), unmatched_summary.notify_status);
    try std.testing.expectEqual(@as(u32, 0), unmatched_summary.matched_notify_mask);
    try std.testing.expect((unmatched_summary.flags & abi.CHRDEV_NOTIFY_FLAG_MATCHED_NOTIFY) == 0);
}

