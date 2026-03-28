const std = @import("std");
const abi = @import("abi_bindings");
const chrdev_requeue_plan = @import("chrdev_requeue_plan");

fn mapRequeueFlags(requeue_flags: u32) u32 {
    var flags: u32 = 0;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_TRUNCATED) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_TRUNCATED;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_FOUND) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_FOUND;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_EXHAUSTED) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_EXHAUSTED;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_HIT) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_HIT;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_PERMITTED) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_PERMITTED;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_DENIED) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_DENIED;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_ROUTABLE) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_ROUTABLE;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_BLOCKED) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_BLOCKED;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_DISPATCHABLE) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_DISPATCHABLE;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_RESUMED) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_RESUMED;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_CONTINUABLE) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_CONTINUABLE;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_COMPLETES) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_COMPLETES;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_PROGRESSED) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_PROGRESSED;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_STALLED) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_STALLED;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_COMPLETE_OK) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_COMPLETE_OK;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_RETRYABLE) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_RETRYABLE;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_RETRY_PLANNED) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_RETRY_PLANNED;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_RETRY_EXHAUSTED) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_RETRY_EXHAUSTED;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_BACKOFF_APPLIED) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_BACKOFF_APPLIED;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_FAILS) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_FAILS;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_REQUEUEABLE) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_REQUEUEABLE;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_REQUEUE_PLANNED) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_REQUEUE_PLANNED;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_DELAYED) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_DELAYED;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_SATURATED) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_SATURATED;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_DROPPED) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_DROPPED;
    if ((requeue_flags & abi.CHRDEV_REQUEUE_FLAG_COMPLETE) != 0) flags |= abi.CHRDEV_COMPLETE_FLAG_COMPLETE;
    return flags;
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
) abi.ChrdevCompleteView {
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
        .reserved = 0,
    };
}

pub fn asChrdevRequeueView(view: abi.ChrdevCompleteView) abi.ChrdevRequeueView {
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
        .reserved = 0,
    };
}

pub fn isValid(view: abi.ChrdevCompleteView) bool {
    if (view.reserved != 0) return false;
    return chrdev_requeue_plan.isValid(asChrdevRequeueView(view));
}

pub fn summarize(view: abi.ChrdevCompleteView) abi.ChrdevCompleteSummary {
    if (!isValid(view)) {
        return .{
            .major = 0,
            .target_minor = 0,
            .selected_count = 0,
            .resolved_index = abi.CHRDEV_COMPLETE_INDEX_NONE,
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
            .flags = 0,
        };
    }

    const requeue_summary = chrdev_requeue_plan.summarize(asChrdevRequeueView(view));
    var flags = mapRequeueFlags(requeue_summary.flags);
    var completion_status: u32 = abi.CHRDEV_COMPLETE_STATUS_NONE;
    var completion_count: u32 = 0;
    var deferred_count: u32 = 0;
    var failure_count: u32 = 0;
    var remaining_completion_budget = view.completion_budget;

    if ((flags & abi.CHRDEV_COMPLETE_FLAG_COMPLETE) != 0) {
        completion_status = abi.CHRDEV_COMPLETE_STATUS_OK;
        if (view.completion_budget != 0) {
            completion_count = 1;
            remaining_completion_budget = view.completion_budget - 1;
            flags |= abi.CHRDEV_COMPLETE_FLAG_COMPLETION_PLANNED | abi.CHRDEV_COMPLETE_FLAG_FINALIZED;
        } else {
            deferred_count = 1;
            flags |= abi.CHRDEV_COMPLETE_FLAG_DEFERRED_COMPLETION;
        }
    } else if ((flags & abi.CHRDEV_COMPLETE_FLAG_REQUEUE_PLANNED) != 0) {
        completion_status = abi.CHRDEV_COMPLETE_STATUS_DEFERRED;
        deferred_count = 1;
        flags |= abi.CHRDEV_COMPLETE_FLAG_DEFERRED_COMPLETION;
    } else if ((flags & (abi.CHRDEV_COMPLETE_FLAG_DENIED | abi.CHRDEV_COMPLETE_FLAG_EXHAUSTED | abi.CHRDEV_COMPLETE_FLAG_DROPPED | abi.CHRDEV_COMPLETE_FLAG_SATURATED | abi.CHRDEV_COMPLETE_FLAG_FAILS)) != 0) {
        completion_status = abi.CHRDEV_COMPLETE_STATUS_FAILED;
        failure_count = 1;
        flags |= abi.CHRDEV_COMPLETE_FLAG_FAILURE_COMPLETION;
        if (view.completion_budget != 0) {
            completion_count = 1;
            remaining_completion_budget = view.completion_budget - 1;
            flags |= abi.CHRDEV_COMPLETE_FLAG_COMPLETION_PLANNED | abi.CHRDEV_COMPLETE_FLAG_FINALIZED;
        }
    }

    return .{
        .major = requeue_summary.major,
        .target_minor = requeue_summary.target_minor,
        .selected_count = requeue_summary.selected_count,
        .resolved_index = if (requeue_summary.resolved_index == abi.CHRDEV_REQUEUE_INDEX_NONE) abi.CHRDEV_COMPLETE_INDEX_NONE else requeue_summary.resolved_index,
        .resolved_dev = requeue_summary.resolved_dev,
        .granted_mode = requeue_summary.granted_mode,
        .io_op = requeue_summary.io_op,
        .requested_bytes = requeue_summary.requested_bytes,
        .start_offset = requeue_summary.start_offset,
        .next_offset = requeue_summary.next_offset,
        .initial_bytes_completed = requeue_summary.initial_bytes_completed,
        .final_bytes_completed = requeue_summary.final_bytes_completed,
        .pass_count = requeue_summary.pass_count,
        .issued_bytes = requeue_summary.issued_bytes,
        .remaining_bytes = requeue_summary.remaining_bytes,
        .projected_remaining_bytes = requeue_summary.projected_remaining_bytes,
        .entry_ops = requeue_summary.entry_ops,
        .data_ops = requeue_summary.data_ops,
        .exit_ops = requeue_summary.exit_ops,
        .blocked_ops = requeue_summary.blocked_ops,
        .retry_count = requeue_summary.retry_count,
        .stall_count = requeue_summary.stall_count,
        .requeue_count = requeue_summary.requeue_count,
        .queue_depth_before = requeue_summary.queue_depth_before,
        .queue_depth_after = requeue_summary.queue_depth_after,
        .remaining_retry_budget = requeue_summary.remaining_retry_budget,
        .remaining_requeue_budget = requeue_summary.remaining_requeue_budget,
        .backoff_ticks = requeue_summary.backoff_ticks,
        .completion_cookie = view.completion_cookie,
        .completion_status = completion_status,
        .completion_count = completion_count,
        .deferred_count = deferred_count,
        .failure_count = failure_count,
        .remaining_completion_budget = remaining_completion_budget,
        .flags = flags,
    };
}

test "phase3 chrdev complete complete and deferred summaries stay bounded" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};

    const complete_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1);
    const complete_summary = summarize(complete_view);
    try std.testing.expect(isValid(complete_view));
    try std.testing.expectEqual(@as(u64, 0x1111), complete_summary.completion_cookie);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_COMPLETE_STATUS_OK), complete_summary.completion_status);
    try std.testing.expectEqual(@as(u32, 1), complete_summary.completion_count);
    try std.testing.expectEqual(@as(u32, 0), complete_summary.deferred_count);
    try std.testing.expectEqual(@as(u32, 0), complete_summary.failure_count);
    try std.testing.expectEqual(@as(u32, 0), complete_summary.remaining_completion_budget);
    try std.testing.expect((complete_summary.flags & abi.CHRDEV_COMPLETE_FLAG_COMPLETION_PLANNED) != 0);
    try std.testing.expect((complete_summary.flags & abi.CHRDEV_COMPLETE_FLAG_FINALIZED) != 0);

    const complete_deferred_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x2222, 0);
    const complete_deferred_summary = summarize(complete_deferred_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_COMPLETE_STATUS_OK), complete_deferred_summary.completion_status);
    try std.testing.expectEqual(@as(u32, 0), complete_deferred_summary.completion_count);
    try std.testing.expectEqual(@as(u32, 1), complete_deferred_summary.deferred_count);
    try std.testing.expect((complete_deferred_summary.flags & abi.CHRDEV_COMPLETE_FLAG_DEFERRED_COMPLETION) != 0);
}

test "phase3 chrdev complete requeued and delayed summaries stay explicit" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};

    const requeued_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 36, 8, 1024, 4, 1, 1, 1, 1, 0, 1, 4, 2, 0x3333, 1);
    const requeued_summary = summarize(requeued_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_COMPLETE_STATUS_DEFERRED), requeued_summary.completion_status);
    try std.testing.expectEqual(@as(u32, 0), requeued_summary.completion_count);
    try std.testing.expectEqual(@as(u32, 1), requeued_summary.deferred_count);
    try std.testing.expect((requeued_summary.flags & abi.CHRDEV_COMPLETE_FLAG_REQUEUE_PLANNED) != 0);
    try std.testing.expect((requeued_summary.flags & abi.CHRDEV_COMPLETE_FLAG_DEFERRED_COMPLETION) != 0);

    const delayed_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_READ, 12, 32, 2048, 4, 2, 3, 2, 1, 5, 2, 4, 3, 0x4444, 2);
    const delayed_summary = summarize(delayed_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_COMPLETE_STATUS_DEFERRED), delayed_summary.completion_status);
    try std.testing.expectEqual(@as(u32, 1), delayed_summary.deferred_count);
    try std.testing.expect((delayed_summary.flags & abi.CHRDEV_COMPLETE_FLAG_DELAYED) != 0);
    try std.testing.expect((delayed_summary.flags & abi.CHRDEV_COMPLETE_FLAG_DEFERRED_COMPLETION) != 0);
}

test "phase3 chrdev complete failed summaries stay explicit" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const saturated_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 36, 8, 1024, 4, 1, 1, 1, 1, 0, 4, 4, 2, 0x5555, 1);
    const saturated_summary = summarize(saturated_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_COMPLETE_STATUS_FAILED), saturated_summary.completion_status);
    try std.testing.expectEqual(@as(u32, 1), saturated_summary.completion_count);
    try std.testing.expectEqual(@as(u32, 1), saturated_summary.failure_count);
    try std.testing.expect((saturated_summary.flags & abi.CHRDEV_COMPLETE_FLAG_FAILURE_COMPLETION) != 0);
    try std.testing.expect((saturated_summary.flags & abi.CHRDEV_COMPLETE_FLAG_FINALIZED) != 0);

    const denied_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 12, 8, 512, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x6666, 1);
    const denied_summary = summarize(denied_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_COMPLETE_STATUS_FAILED), denied_summary.completion_status);
    try std.testing.expectEqual(@as(u32, 1), denied_summary.failure_count);
    try std.testing.expect((denied_summary.flags & abi.CHRDEV_COMPLETE_FLAG_DENIED) != 0);

    const exhausted_view = viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0);
    const exhausted_summary = summarize(exhausted_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_COMPLETE_STATUS_FAILED), exhausted_summary.completion_status);
    try std.testing.expectEqual(@as(u32, 0), exhausted_summary.completion_count);
    try std.testing.expectEqual(@as(u32, 1), exhausted_summary.failure_count);
    try std.testing.expect((exhausted_summary.flags & abi.CHRDEV_COMPLETE_FLAG_FAILURE_COMPLETION) != 0);

    const empty_view = abi.ChrdevCompleteView{
        .bits_addr = 0,
        .major = 240,
        .first_minor = 0,
        .minor_count = 0,
        .max_scan = 0,
        .request_count = 2,
        .policy = abi.IDA_POLICY_FIRST_FIT,
        .target_minor = 0,
        .requested_mode = abi.CHRDEV_MODE_READ,
        .supported_mode = abi.CHRDEV_MODE_READ,
        .available_ops = abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ,
        .io_op = abi.CHRDEV_IO_OP_READ,
        .requested_bytes = 8,
        .max_chunk_bytes = 8,
        .file_offset = 0,
        .bytes_completed = 0,
        .max_segments = 1,
        .resume_passes = 2,
        .retry_budget = 1,
        .stall_budget = 1,
        .backoff_quanta = 5,
        .queue_depth = 0,
        .queue_capacity = 2,
        .requeue_budget = 1,
        .completion_cookie = 0x8888,
        .completion_budget = 0,
        .reserved = 0,
    };
    const empty_summary = summarize(empty_view);
    try std.testing.expect(isValid(empty_view));
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_COMPLETE_STATUS_FAILED), empty_summary.completion_status);
    try std.testing.expectEqual(@as(u32, 0), empty_summary.completion_count);
    try std.testing.expectEqual(@as(u32, 1), empty_summary.failure_count);
}
