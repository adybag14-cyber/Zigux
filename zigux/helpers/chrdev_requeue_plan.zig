const std = @import("std");
const abi = @import("abi_bindings");
const chrdev_retry_plan = @import("chrdev_retry_plan");

fn mapRetryFlags(retry_flags: u32) u32 {
    var flags: u32 = 0;
    if ((retry_flags & abi.CHRDEV_RETRY_FLAG_TRUNCATED) != 0) flags |= abi.CHRDEV_REQUEUE_FLAG_TRUNCATED;
    if ((retry_flags & abi.CHRDEV_RETRY_FLAG_FOUND) != 0) flags |= abi.CHRDEV_REQUEUE_FLAG_FOUND;
    if ((retry_flags & abi.CHRDEV_RETRY_FLAG_EXHAUSTED) != 0) flags |= abi.CHRDEV_REQUEUE_FLAG_EXHAUSTED;
    if ((retry_flags & abi.CHRDEV_RETRY_FLAG_HIT) != 0) flags |= abi.CHRDEV_REQUEUE_FLAG_HIT;
    if ((retry_flags & abi.CHRDEV_RETRY_FLAG_PERMITTED) != 0) flags |= abi.CHRDEV_REQUEUE_FLAG_PERMITTED;
    if ((retry_flags & abi.CHRDEV_RETRY_FLAG_DENIED) != 0) flags |= abi.CHRDEV_REQUEUE_FLAG_DENIED;
    if ((retry_flags & abi.CHRDEV_RETRY_FLAG_ROUTABLE) != 0) flags |= abi.CHRDEV_REQUEUE_FLAG_ROUTABLE;
    if ((retry_flags & abi.CHRDEV_RETRY_FLAG_BLOCKED) != 0) flags |= abi.CHRDEV_REQUEUE_FLAG_BLOCKED;
    if ((retry_flags & abi.CHRDEV_RETRY_FLAG_DISPATCHABLE) != 0) flags |= abi.CHRDEV_REQUEUE_FLAG_DISPATCHABLE;
    if ((retry_flags & abi.CHRDEV_RETRY_FLAG_RESUMED) != 0) flags |= abi.CHRDEV_REQUEUE_FLAG_RESUMED;
    if ((retry_flags & abi.CHRDEV_RETRY_FLAG_CONTINUABLE) != 0) flags |= abi.CHRDEV_REQUEUE_FLAG_CONTINUABLE;
    if ((retry_flags & abi.CHRDEV_RETRY_FLAG_COMPLETES) != 0) flags |= abi.CHRDEV_REQUEUE_FLAG_COMPLETES;
    if ((retry_flags & abi.CHRDEV_RETRY_FLAG_PROGRESSED) != 0) flags |= abi.CHRDEV_REQUEUE_FLAG_PROGRESSED;
    if ((retry_flags & abi.CHRDEV_RETRY_FLAG_STALLED) != 0) flags |= abi.CHRDEV_REQUEUE_FLAG_STALLED;
    if ((retry_flags & abi.CHRDEV_RETRY_FLAG_COMPLETE_OK) != 0) flags |= abi.CHRDEV_REQUEUE_FLAG_COMPLETE_OK;
    if ((retry_flags & abi.CHRDEV_RETRY_FLAG_RETRYABLE) != 0) flags |= abi.CHRDEV_REQUEUE_FLAG_RETRYABLE;
    if ((retry_flags & abi.CHRDEV_RETRY_FLAG_RETRY_PLANNED) != 0) flags |= abi.CHRDEV_REQUEUE_FLAG_RETRY_PLANNED;
    if ((retry_flags & abi.CHRDEV_RETRY_FLAG_RETRY_EXHAUSTED) != 0) flags |= abi.CHRDEV_REQUEUE_FLAG_RETRY_EXHAUSTED;
    if ((retry_flags & abi.CHRDEV_RETRY_FLAG_BACKOFF_APPLIED) != 0) flags |= abi.CHRDEV_REQUEUE_FLAG_BACKOFF_APPLIED;
    if ((retry_flags & abi.CHRDEV_RETRY_FLAG_FAILS) != 0) flags |= abi.CHRDEV_REQUEUE_FLAG_FAILS;
    return flags;
}

fn ceilDiv(value: u32, step: u32) u32 {
    if (value == 0) return 0;
    return 1 + ((value - 1) / step);
}

fn progressQuantum(summary: abi.ChrdevRetrySummary) u32 {
    if (summary.pass_count == 0 or summary.issued_bytes == 0) return 0;
    return ceilDiv(summary.issued_bytes, summary.pass_count);
}

fn projectedRemaining(summary: abi.ChrdevRetrySummary) u32 {
    if (summary.remaining_bytes == 0) return 0;
    if (summary.retry_count == 0) return summary.remaining_bytes;

    const quantum = progressQuantum(summary);
    if (quantum == 0) return summary.remaining_bytes;

    const projected_progress = @min(summary.remaining_bytes, summary.retry_count * quantum);
    return summary.remaining_bytes - projected_progress;
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
) abi.ChrdevRequeueView {
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
        .reserved = 0,
    };
}

pub fn asChrdevRetryView(view: abi.ChrdevRequeueView) abi.ChrdevRetryView {
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
        .reserved = 0,
    };
}

pub fn isValid(view: abi.ChrdevRequeueView) bool {
    if (view.reserved != 0) return false;
    if (view.queue_depth > view.queue_capacity) return false;
    return chrdev_retry_plan.isValid(asChrdevRetryView(view));
}

pub fn summarize(view: abi.ChrdevRequeueView) abi.ChrdevRequeueSummary {
    if (!isValid(view)) {
        return .{
            .major = 0,
            .target_minor = 0,
            .selected_count = 0,
            .resolved_index = abi.CHRDEV_REQUEUE_INDEX_NONE,
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
            .flags = 0,
        };
    }

    const retry_summary = chrdev_retry_plan.summarize(asChrdevRetryView(view));
    var flags = mapRetryFlags(retry_summary.flags);
    const projected_remaining_bytes = projectedRemaining(retry_summary);
    const queue_depth_before = view.queue_depth;
    var queue_depth_after = queue_depth_before;
    var requeue_count: u32 = 0;
    var remaining_requeue_budget = view.requeue_budget;

    if (projected_remaining_bytes == 0) {
        flags |= abi.CHRDEV_REQUEUE_FLAG_COMPLETE;
    } else if ((flags & abi.CHRDEV_REQUEUE_FLAG_DENIED) != 0 or (flags & abi.CHRDEV_REQUEUE_FLAG_EXHAUSTED) != 0) {
        flags |= abi.CHRDEV_REQUEUE_FLAG_DROPPED;
    } else {
        flags |= abi.CHRDEV_REQUEUE_FLAG_REQUEUEABLE;
        if (view.requeue_budget == 0) {
            remaining_requeue_budget = 0;
            flags |= abi.CHRDEV_REQUEUE_FLAG_DROPPED;
        } else if (view.queue_depth >= view.queue_capacity) {
            flags |= abi.CHRDEV_REQUEUE_FLAG_SATURATED | abi.CHRDEV_REQUEUE_FLAG_DROPPED;
        } else {
            requeue_count = 1;
            queue_depth_after = queue_depth_before + 1;
            remaining_requeue_budget = view.requeue_budget - 1;
            flags |= abi.CHRDEV_REQUEUE_FLAG_REQUEUE_PLANNED;
            if (retry_summary.backoff_ticks != 0 or retry_summary.stall_count != 0) {
                flags |= abi.CHRDEV_REQUEUE_FLAG_DELAYED;
            }
        }
    }

    return .{
        .major = retry_summary.major,
        .target_minor = retry_summary.target_minor,
        .selected_count = retry_summary.selected_count,
        .resolved_index = if (retry_summary.resolved_index == abi.CHRDEV_RETRY_INDEX_NONE) abi.CHRDEV_REQUEUE_INDEX_NONE else retry_summary.resolved_index,
        .resolved_dev = retry_summary.resolved_dev,
        .granted_mode = retry_summary.granted_mode,
        .io_op = retry_summary.io_op,
        .requested_bytes = retry_summary.requested_bytes,
        .start_offset = retry_summary.start_offset,
        .next_offset = retry_summary.next_offset,
        .initial_bytes_completed = retry_summary.initial_bytes_completed,
        .final_bytes_completed = retry_summary.final_bytes_completed,
        .pass_count = retry_summary.pass_count,
        .issued_bytes = retry_summary.issued_bytes,
        .remaining_bytes = retry_summary.remaining_bytes,
        .projected_remaining_bytes = projected_remaining_bytes,
        .entry_ops = retry_summary.entry_ops,
        .data_ops = retry_summary.data_ops,
        .exit_ops = retry_summary.exit_ops,
        .blocked_ops = retry_summary.blocked_ops,
        .retry_count = retry_summary.retry_count,
        .stall_count = retry_summary.stall_count,
        .requeue_count = requeue_count,
        .queue_depth_before = queue_depth_before,
        .queue_depth_after = queue_depth_after,
        .remaining_retry_budget = retry_summary.remaining_retry_budget,
        .remaining_requeue_budget = remaining_requeue_budget,
        .backoff_ticks = retry_summary.backoff_ticks,
        .flags = flags,
    };
}

test "phase3 chrdev requeue complete and planned summaries stay bounded" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};

    const complete_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2);
    const complete_summary = summarize(complete_view);
    try std.testing.expect(isValid(complete_view));
    try std.testing.expectEqual(@as(u32, 0), complete_summary.projected_remaining_bytes);
    try std.testing.expectEqual(@as(u32, 0), complete_summary.requeue_count);
    try std.testing.expectEqual(@as(u32, 1), complete_summary.queue_depth_before);
    try std.testing.expectEqual(@as(u32, 1), complete_summary.queue_depth_after);
    try std.testing.expectEqual(@as(u32, 2), complete_summary.remaining_requeue_budget);
    try std.testing.expect((complete_summary.flags & abi.CHRDEV_REQUEUE_FLAG_COMPLETE) != 0);
    try std.testing.expect((complete_summary.flags & abi.CHRDEV_REQUEUE_FLAG_REQUEUE_PLANNED) == 0);

    const planned_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 36, 8, 1024, 4, 1, 1, 1, 1, 0, 1, 4, 2);
    const planned_summary = summarize(planned_view);
    try std.testing.expectEqual(@as(u32, 16), planned_summary.projected_remaining_bytes);
    try std.testing.expectEqual(@as(u32, 1), planned_summary.requeue_count);
    try std.testing.expectEqual(@as(u32, 1), planned_summary.retry_count);
    try std.testing.expectEqual(@as(u32, 1), planned_summary.queue_depth_before);
    try std.testing.expectEqual(@as(u32, 2), planned_summary.queue_depth_after);
    try std.testing.expectEqual(@as(u32, 1), planned_summary.remaining_requeue_budget);
    try std.testing.expect((planned_summary.flags & abi.CHRDEV_REQUEUE_FLAG_REQUEUEABLE) != 0);
    try std.testing.expect((planned_summary.flags & abi.CHRDEV_REQUEUE_FLAG_REQUEUE_PLANNED) != 0);
    try std.testing.expect((planned_summary.flags & abi.CHRDEV_REQUEUE_FLAG_DELAYED) == 0);
}

test "phase3 chrdev requeue delayed and saturated summaries stay explicit" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};

    const delayed_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_READ, 12, 32, 2048, 4, 2, 3, 2, 1, 5, 2, 4, 3);
    const delayed_summary = summarize(delayed_view);
    try std.testing.expectEqual(@as(u32, 8), delayed_summary.projected_remaining_bytes);
    try std.testing.expectEqual(@as(u32, 1), delayed_summary.requeue_count);
    try std.testing.expectEqual(@as(u32, 2), delayed_summary.queue_depth_before);
    try std.testing.expectEqual(@as(u32, 3), delayed_summary.queue_depth_after);
    try std.testing.expectEqual(@as(u32, 2), delayed_summary.remaining_requeue_budget);
    try std.testing.expect((delayed_summary.flags & abi.CHRDEV_REQUEUE_FLAG_REQUEUE_PLANNED) != 0);
    try std.testing.expect((delayed_summary.flags & abi.CHRDEV_REQUEUE_FLAG_DELAYED) != 0);

    const saturated_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 36, 8, 1024, 4, 1, 1, 1, 1, 0, 4, 4, 2);
    const saturated_summary = summarize(saturated_view);
    try std.testing.expectEqual(@as(u32, 16), saturated_summary.projected_remaining_bytes);
    try std.testing.expectEqual(@as(u32, 0), saturated_summary.requeue_count);
    try std.testing.expectEqual(@as(u32, 4), saturated_summary.queue_depth_before);
    try std.testing.expectEqual(@as(u32, 4), saturated_summary.queue_depth_after);
    try std.testing.expectEqual(@as(u32, 2), saturated_summary.remaining_requeue_budget);
    try std.testing.expect((saturated_summary.flags & abi.CHRDEV_REQUEUE_FLAG_SATURATED) != 0);
    try std.testing.expect((saturated_summary.flags & abi.CHRDEV_REQUEUE_FLAG_DROPPED) != 0);
}

test "phase3 chrdev requeue denied and exhausted summaries stay explicit" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const denied_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 12, 8, 512, 0, 2, 2, 2, 1, 5, 1, 4, 2);
    const denied_summary = summarize(denied_view);
    try std.testing.expectEqual(@as(u32, 8), denied_summary.projected_remaining_bytes);
    try std.testing.expectEqual(@as(u32, 0), denied_summary.requeue_count);
    try std.testing.expect((denied_summary.flags & abi.CHRDEV_REQUEUE_FLAG_DENIED) != 0);
    try std.testing.expect((denied_summary.flags & abi.CHRDEV_REQUEUE_FLAG_DROPPED) != 0);
    try std.testing.expect((denied_summary.flags & abi.CHRDEV_REQUEUE_FLAG_REQUEUEABLE) == 0);

    const exhausted_view = viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2);
    const exhausted_summary = summarize(exhausted_view);
    try std.testing.expectEqual(@as(u32, 12), exhausted_summary.projected_remaining_bytes);
    try std.testing.expectEqual(@as(u32, 0), exhausted_summary.requeue_count);
    try std.testing.expect((exhausted_summary.flags & abi.CHRDEV_REQUEUE_FLAG_EXHAUSTED) != 0);
    try std.testing.expect((exhausted_summary.flags & abi.CHRDEV_REQUEUE_FLAG_DROPPED) != 0);

    const empty_view = abi.ChrdevRequeueView{
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
        .reserved = 0,
    };
    const empty_summary = summarize(empty_view);
    try std.testing.expect(isValid(empty_view));
    try std.testing.expectEqual(@as(u32, 0), empty_summary.requeue_count);
    try std.testing.expectEqual(@as(u32, 0), empty_summary.queue_depth_before);
    try std.testing.expectEqual(@as(u32, 0), empty_summary.queue_depth_after);
}
