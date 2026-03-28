const std = @import("std");
const abi = @import("abi_bindings");
const chrdev_notify_plan = @import("chrdev_notify_plan");

const allowed_policy_flags =
    abi.CHRDEV_NOTIFY_POLICY_FORCE_DEFERRED |
    abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE |
    abi.CHRDEV_NOTIFY_POLICY_COALESCE_COOKIE;

fn emptyNotifyView() abi.ChrdevNotifyView {
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
        .notify_mask = 0,
        .notify_cookie = 0,
        .notify_budget = 0,
        .reserved = 0,
    };
}

fn emptySummary() abi.ChrdevNotifyPolicySummary {
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
        .policy_flags = 0,
        .effective_policy_flags = 0,
        .effective_notify_cookie = 0,
        .policy_status = abi.CHRDEV_NOTIFY_POLICY_STATUS_NONE,
        .policy_notify_count = 0,
        .policy_deferred_count = 0,
        .policy_suppressed_count = 0,
        .policy_coalesced_count = 0,
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
    policy_flags: u32,
) abi.ChrdevNotifyPolicyView {
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
        .policy_flags = policy_flags,
        .policy_reserved = 0,
    };
}

pub fn asChrdevNotifyView(view: abi.ChrdevNotifyPolicyView) abi.ChrdevNotifyView {
    if (view.reserved != 0 or view.policy_reserved != 0) {
        return emptyNotifyView();
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
        .notify_mask = view.notify_mask,
        .notify_cookie = view.notify_cookie,
        .notify_budget = view.notify_budget,
        .reserved = 0,
    };
}

pub fn isValid(view: abi.ChrdevNotifyPolicyView) bool {
    if (view.reserved != 0 or view.policy_reserved != 0) return false;
    if ((view.policy_flags & ~allowed_policy_flags) != 0) return false;
    return chrdev_notify_plan.isValid(asChrdevNotifyView(view));
}

pub fn summarize(view: abi.ChrdevNotifyPolicyView) abi.ChrdevNotifyPolicySummary {
    if (!isValid(view)) {
        return emptySummary();
    }

    const notify_summary = chrdev_notify_plan.summarize(asChrdevNotifyView(view));
    var policy_status: u32 = abi.CHRDEV_NOTIFY_POLICY_STATUS_NONE;
    var policy_notify_count: u32 = 0;
    var policy_deferred_count: u32 = 0;
    var policy_suppressed_count: u32 = 0;
    var policy_coalesced_count: u32 = 0;
    var effective_policy_flags: u32 = 0;
    var effective_notify_cookie: u64 = 0;

    switch (notify_summary.notify_status) {
        abi.CHRDEV_NOTIFY_STATUS_NONE => {},
        abi.CHRDEV_NOTIFY_STATUS_DROPPED => {
            policy_status = abi.CHRDEV_NOTIFY_POLICY_STATUS_SUPPRESSED;
            policy_suppressed_count = 1;
        },
        abi.CHRDEV_NOTIFY_STATUS_DEFERRED => {
            policy_status = abi.CHRDEV_NOTIFY_POLICY_STATUS_DEFERRED;
            policy_deferred_count = 1;
            if ((view.policy_flags & abi.CHRDEV_NOTIFY_POLICY_FORCE_DEFERRED) != 0) {
                effective_policy_flags = abi.CHRDEV_NOTIFY_POLICY_FORCE_DEFERRED;
            }
            effective_notify_cookie = notify_summary.notify_cookie;
        },
        abi.CHRDEV_NOTIFY_STATUS_DELIVERED => {
            if (notify_summary.completion_status == abi.CHRDEV_COMPLETE_STATUS_FAILED and
                (view.policy_flags & abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE) != 0)
            {
                policy_status = abi.CHRDEV_NOTIFY_POLICY_STATUS_SUPPRESSED;
                policy_suppressed_count = 1;
                effective_policy_flags = abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE;
                effective_notify_cookie = 0;
            } else if ((view.policy_flags & abi.CHRDEV_NOTIFY_POLICY_COALESCE_COOKIE) != 0 and
                notify_summary.notify_cookie != 0 and
                notify_summary.notify_cookie == notify_summary.completion_cookie)
            {
                policy_status = abi.CHRDEV_NOTIFY_POLICY_STATUS_COALESCED;
                policy_coalesced_count = 1;
                effective_policy_flags = abi.CHRDEV_NOTIFY_POLICY_COALESCE_COOKIE;
                effective_notify_cookie = notify_summary.completion_cookie;
            } else if ((view.policy_flags & abi.CHRDEV_NOTIFY_POLICY_FORCE_DEFERRED) != 0) {
                policy_status = abi.CHRDEV_NOTIFY_POLICY_STATUS_DEFERRED;
                policy_deferred_count = 1;
                effective_policy_flags = abi.CHRDEV_NOTIFY_POLICY_FORCE_DEFERRED;
                effective_notify_cookie = notify_summary.notify_cookie;
            } else {
                policy_status = abi.CHRDEV_NOTIFY_POLICY_STATUS_DELIVERED;
                policy_notify_count = 1;
                effective_notify_cookie = notify_summary.notify_cookie;
            }
        },
        else => {},
    }

    return .{
        .major = notify_summary.major,
        .target_minor = notify_summary.target_minor,
        .selected_count = notify_summary.selected_count,
        .resolved_index = notify_summary.resolved_index,
        .resolved_dev = notify_summary.resolved_dev,
        .granted_mode = notify_summary.granted_mode,
        .io_op = notify_summary.io_op,
        .requested_bytes = notify_summary.requested_bytes,
        .start_offset = notify_summary.start_offset,
        .next_offset = notify_summary.next_offset,
        .initial_bytes_completed = notify_summary.initial_bytes_completed,
        .final_bytes_completed = notify_summary.final_bytes_completed,
        .pass_count = notify_summary.pass_count,
        .issued_bytes = notify_summary.issued_bytes,
        .remaining_bytes = notify_summary.remaining_bytes,
        .projected_remaining_bytes = notify_summary.projected_remaining_bytes,
        .entry_ops = notify_summary.entry_ops,
        .data_ops = notify_summary.data_ops,
        .exit_ops = notify_summary.exit_ops,
        .blocked_ops = notify_summary.blocked_ops,
        .retry_count = notify_summary.retry_count,
        .stall_count = notify_summary.stall_count,
        .requeue_count = notify_summary.requeue_count,
        .queue_depth_before = notify_summary.queue_depth_before,
        .queue_depth_after = notify_summary.queue_depth_after,
        .remaining_retry_budget = notify_summary.remaining_retry_budget,
        .remaining_requeue_budget = notify_summary.remaining_requeue_budget,
        .backoff_ticks = notify_summary.backoff_ticks,
        .completion_cookie = notify_summary.completion_cookie,
        .completion_status = notify_summary.completion_status,
        .completion_count = notify_summary.completion_count,
        .deferred_count = notify_summary.deferred_count,
        .failure_count = notify_summary.failure_count,
        .remaining_completion_budget = notify_summary.remaining_completion_budget,
        .notify_mask = notify_summary.notify_mask,
        .matched_notify_mask = notify_summary.matched_notify_mask,
        .notify_status = notify_summary.notify_status,
        .notify_count = notify_summary.notify_count,
        .deferred_notify_count = notify_summary.deferred_notify_count,
        .dropped_notify_count = notify_summary.dropped_notify_count,
        .remaining_notify_budget = notify_summary.remaining_notify_budget,
        .notify_cookie = notify_summary.notify_cookie,
        .flags = notify_summary.flags,
        .policy_flags = view.policy_flags,
        .effective_policy_flags = effective_policy_flags,
        .effective_notify_cookie = effective_notify_cookie,
        .policy_status = policy_status,
        .policy_notify_count = policy_notify_count,
        .policy_deferred_count = policy_deferred_count,
        .policy_suppressed_count = policy_suppressed_count,
        .policy_coalesced_count = policy_coalesced_count,
    };
}

test "phase3 chrdev notify policy summaries stay bounded" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const delivered_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0);
    const delivered_summary = summarize(delivered_view);
    try std.testing.expect(isValid(delivered_view));
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_POLICY_STATUS_DELIVERED), delivered_summary.policy_status);
    try std.testing.expectEqual(@as(u32, 1), delivered_summary.policy_notify_count);
    try std.testing.expectEqual(@as(u32, 0), delivered_summary.effective_policy_flags);
    try std.testing.expectEqual(@as(u64, 0xAAAA), delivered_summary.effective_notify_cookie);

    const forced_deferred_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xBBBB, abi.CHRDEV_NOTIFY_POLICY_FORCE_DEFERRED);
    const forced_deferred_summary = summarize(forced_deferred_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_POLICY_STATUS_DEFERRED), forced_deferred_summary.policy_status);
    try std.testing.expectEqual(@as(u32, 1), forced_deferred_summary.policy_deferred_count);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_POLICY_FORCE_DEFERRED), forced_deferred_summary.effective_policy_flags);

    const suppressed_failure_view = viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, abi.CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xCCCC, abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE);
    const suppressed_failure_summary = summarize(suppressed_failure_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_POLICY_STATUS_SUPPRESSED), suppressed_failure_summary.policy_status);
    try std.testing.expectEqual(@as(u32, 1), suppressed_failure_summary.policy_suppressed_count);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE), suppressed_failure_summary.effective_policy_flags);
    try std.testing.expectEqual(@as(u64, 0), suppressed_failure_summary.effective_notify_cookie);

    const coalesced_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0xDEAD, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xDEAD, abi.CHRDEV_NOTIFY_POLICY_COALESCE_COOKIE);
    const coalesced_summary = summarize(coalesced_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_POLICY_STATUS_COALESCED), coalesced_summary.policy_status);
    try std.testing.expectEqual(@as(u32, 1), coalesced_summary.policy_coalesced_count);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_POLICY_COALESCE_COOKIE), coalesced_summary.effective_policy_flags);
    try std.testing.expectEqual(@as(u64, 0xDEAD), coalesced_summary.effective_notify_cookie);

    const dropped_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 0, 0xEEEE, 0);
    const dropped_summary = summarize(dropped_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_POLICY_STATUS_SUPPRESSED), dropped_summary.policy_status);
    try std.testing.expectEqual(@as(u32, 1), dropped_summary.policy_suppressed_count);

    const empty_view = abi.ChrdevNotifyPolicyView{
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
        .completion_cookie = 0x9999,
        .completion_budget = 0,
        .notify_mask = abi.CHRDEV_NOTIFY_MASK_SUCCESS,
        .notify_cookie = 0xFFFF,
        .notify_budget = 0,
        .reserved = 0,
        .policy_flags = 0,
        .policy_reserved = 0,
    };
    const empty_summary = summarize(empty_view);
    try std.testing.expect(chrdev_notify_plan.isValid(asChrdevNotifyView(empty_view)));
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_POLICY_STATUS_NONE), empty_summary.policy_status);
    try std.testing.expectEqual(@as(u32, 0), empty_summary.policy_notify_count);
}
