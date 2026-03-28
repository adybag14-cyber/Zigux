const std = @import("std");
const abi = @import("abi_bindings");
const chrdev_notify_policy_plan = @import("chrdev_notify_policy_plan");

const allowed_policy_flags =
    abi.CHRDEV_NOTIFY_POLICY_FORCE_DEFERRED |
    abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE |
    abi.CHRDEV_NOTIFY_POLICY_COALESCE_COOKIE;

fn emptyPolicyView() abi.ChrdevNotifyPolicyView {
    return std.mem.zeroInit(abi.ChrdevNotifyPolicyView, .{});
}

fn emptySummary() abi.ChrdevNotifyBudgetSummary {
    return std.mem.zeroInit(abi.ChrdevNotifyBudgetSummary, .{
        .resolved_index = abi.CHRDEV_NOTIFY_INDEX_NONE,
        .completion_status = abi.CHRDEV_COMPLETE_STATUS_NONE,
        .notify_status = abi.CHRDEV_NOTIFY_STATUS_NONE,
        .policy_status = abi.CHRDEV_NOTIFY_POLICY_STATUS_NONE,
        .budget_status = abi.CHRDEV_NOTIFY_BUDGET_STATUS_NONE,
    });
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
    delivery_budget: u32,
    deferred_budget: u32,
) abi.ChrdevNotifyBudgetView {
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
        .delivery_budget = delivery_budget,
        .deferred_budget = deferred_budget,
    };
}

pub fn asChrdevNotifyPolicyView(view: abi.ChrdevNotifyBudgetView) abi.ChrdevNotifyPolicyView {
    if (view.reserved != 0 or view.policy_reserved != 0) {
        return emptyPolicyView();
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
        .policy_flags = view.policy_flags,
        .policy_reserved = 0,
    };
}

pub fn isValid(view: abi.ChrdevNotifyBudgetView) bool {
    if (view.reserved != 0 or view.policy_reserved != 0) return false;
    if ((view.policy_flags & ~allowed_policy_flags) != 0) return false;
    return chrdev_notify_policy_plan.isValid(asChrdevNotifyPolicyView(view));
}

pub fn summarize(view: abi.ChrdevNotifyBudgetView) abi.ChrdevNotifyBudgetSummary {
    if (!isValid(view)) {
        return emptySummary();
    }

    const policy_summary = chrdev_notify_policy_plan.summarize(asChrdevNotifyPolicyView(view));

    var summary = abi.ChrdevNotifyBudgetSummary{
        .major = policy_summary.major,
        .target_minor = policy_summary.target_minor,
        .selected_count = policy_summary.selected_count,
        .resolved_index = policy_summary.resolved_index,
        .resolved_dev = policy_summary.resolved_dev,
        .granted_mode = policy_summary.granted_mode,
        .io_op = policy_summary.io_op,
        .requested_bytes = policy_summary.requested_bytes,
        .start_offset = policy_summary.start_offset,
        .next_offset = policy_summary.next_offset,
        .initial_bytes_completed = policy_summary.initial_bytes_completed,
        .final_bytes_completed = policy_summary.final_bytes_completed,
        .pass_count = policy_summary.pass_count,
        .issued_bytes = policy_summary.issued_bytes,
        .remaining_bytes = policy_summary.remaining_bytes,
        .projected_remaining_bytes = policy_summary.projected_remaining_bytes,
        .entry_ops = policy_summary.entry_ops,
        .data_ops = policy_summary.data_ops,
        .exit_ops = policy_summary.exit_ops,
        .blocked_ops = policy_summary.blocked_ops,
        .retry_count = policy_summary.retry_count,
        .stall_count = policy_summary.stall_count,
        .requeue_count = policy_summary.requeue_count,
        .queue_depth_before = policy_summary.queue_depth_before,
        .queue_depth_after = policy_summary.queue_depth_after,
        .remaining_retry_budget = policy_summary.remaining_retry_budget,
        .remaining_requeue_budget = policy_summary.remaining_requeue_budget,
        .backoff_ticks = policy_summary.backoff_ticks,
        .completion_cookie = policy_summary.completion_cookie,
        .completion_status = policy_summary.completion_status,
        .completion_count = policy_summary.completion_count,
        .deferred_count = policy_summary.deferred_count,
        .failure_count = policy_summary.failure_count,
        .remaining_completion_budget = policy_summary.remaining_completion_budget,
        .notify_mask = policy_summary.notify_mask,
        .matched_notify_mask = policy_summary.matched_notify_mask,
        .notify_status = policy_summary.notify_status,
        .notify_count = policy_summary.notify_count,
        .deferred_notify_count = policy_summary.deferred_notify_count,
        .dropped_notify_count = policy_summary.dropped_notify_count,
        .remaining_notify_budget = policy_summary.remaining_notify_budget,
        .notify_cookie = policy_summary.notify_cookie,
        .flags = policy_summary.flags,
        .policy_flags = policy_summary.policy_flags,
        .effective_policy_flags = policy_summary.effective_policy_flags,
        .effective_notify_cookie = policy_summary.effective_notify_cookie,
        .policy_status = policy_summary.policy_status,
        .policy_notify_count = policy_summary.policy_notify_count,
        .policy_deferred_count = policy_summary.policy_deferred_count,
        .policy_suppressed_count = policy_summary.policy_suppressed_count,
        .policy_coalesced_count = policy_summary.policy_coalesced_count,
        .budget_flags = 0,
        .delivery_budget_before = view.delivery_budget,
        .delivery_budget_after = view.delivery_budget,
        .deferred_budget_before = view.deferred_budget,
        .deferred_budget_after = view.deferred_budget,
        .budget_status = abi.CHRDEV_NOTIFY_BUDGET_STATUS_NONE,
        .budget_notify_count = 0,
        .budget_deferred_count = 0,
        .budget_dropped_count = 0,
        .budget_suppressed_count = 0,
    };

    switch (policy_summary.policy_status) {
        abi.CHRDEV_NOTIFY_POLICY_STATUS_NONE => {},
        abi.CHRDEV_NOTIFY_POLICY_STATUS_SUPPRESSED => {
            summary.budget_status = abi.CHRDEV_NOTIFY_BUDGET_STATUS_SUPPRESSED;
            summary.budget_suppressed_count = 1;
        },
        abi.CHRDEV_NOTIFY_POLICY_STATUS_DEFERRED => {
            summary.budget_flags |= abi.CHRDEV_NOTIFY_BUDGET_FLAG_BUDGET_APPLIED;
            if (summary.deferred_budget_after > 0) {
                summary.deferred_budget_after -= 1;
                summary.budget_flags |= abi.CHRDEV_NOTIFY_BUDGET_FLAG_DEFERRED_BUDGET_USED;
                summary.budget_status = abi.CHRDEV_NOTIFY_BUDGET_STATUS_DEFERRED;
                summary.budget_deferred_count = 1;
            } else {
                summary.budget_flags |= abi.CHRDEV_NOTIFY_BUDGET_FLAG_DEFERRED_BUDGET_EXHAUSTED;
                summary.budget_status = abi.CHRDEV_NOTIFY_BUDGET_STATUS_DROPPED;
                summary.budget_dropped_count = 1;
            }
        },
        abi.CHRDEV_NOTIFY_POLICY_STATUS_DELIVERED,
        abi.CHRDEV_NOTIFY_POLICY_STATUS_COALESCED,
        => {
            summary.budget_flags |= abi.CHRDEV_NOTIFY_BUDGET_FLAG_BUDGET_APPLIED;
            if (summary.delivery_budget_after > 0) {
                summary.delivery_budget_after -= 1;
                summary.budget_flags |= abi.CHRDEV_NOTIFY_BUDGET_FLAG_DELIVERY_BUDGET_USED;
                summary.budget_status = abi.CHRDEV_NOTIFY_BUDGET_STATUS_ISSUED;
                summary.budget_notify_count = 1;
            } else {
                summary.budget_flags |= abi.CHRDEV_NOTIFY_BUDGET_FLAG_DELIVERY_BUDGET_EXHAUSTED;
                if (summary.deferred_budget_after > 0) {
                    summary.deferred_budget_after -= 1;
                    summary.budget_flags |= abi.CHRDEV_NOTIFY_BUDGET_FLAG_DEFERRED_BUDGET_USED;
                    summary.budget_status = abi.CHRDEV_NOTIFY_BUDGET_STATUS_DEFERRED;
                    summary.budget_deferred_count = 1;
                } else {
                    summary.budget_flags |= abi.CHRDEV_NOTIFY_BUDGET_FLAG_DEFERRED_BUDGET_EXHAUSTED;
                    summary.budget_status = abi.CHRDEV_NOTIFY_BUDGET_STATUS_DROPPED;
                    summary.budget_dropped_count = 1;
                }
            }
        },
        else => {},
    }

    return summary;
}

test "phase3 chrdev notify budget summaries stay bounded" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const issued_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0);
    const issued_summary = summarize(issued_view);
    try std.testing.expect(isValid(issued_view));
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_BUDGET_STATUS_ISSUED), issued_summary.budget_status);
    try std.testing.expectEqual(@as(u32, 1), issued_summary.budget_notify_count);
    try std.testing.expectEqual(@as(u32, 0), issued_summary.delivery_budget_after);

    const fallback_deferred_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xBBBB, 0, 0, 1);
    const fallback_deferred_summary = summarize(fallback_deferred_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_BUDGET_STATUS_DEFERRED), fallback_deferred_summary.budget_status);
    try std.testing.expectEqual(@as(u32, 1), fallback_deferred_summary.budget_deferred_count);
    try std.testing.expectEqual(@as(u32, 0), fallback_deferred_summary.deferred_budget_after);

    const policy_deferred_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xCCCC, abi.CHRDEV_NOTIFY_POLICY_FORCE_DEFERRED, 0, 1);
    const policy_deferred_summary = summarize(policy_deferred_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_BUDGET_STATUS_DEFERRED), policy_deferred_summary.budget_status);
    try std.testing.expectEqual(@as(u32, 1), policy_deferred_summary.budget_deferred_count);

    const dropped_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xDDDD, 0, 0, 0);
    const dropped_summary = summarize(dropped_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_BUDGET_STATUS_DROPPED), dropped_summary.budget_status);
    try std.testing.expectEqual(@as(u32, 1), dropped_summary.budget_dropped_count);

    const suppressed_view = viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, abi.CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xEEEE, abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE, 3, 4);
    const suppressed_summary = summarize(suppressed_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_BUDGET_STATUS_SUPPRESSED), suppressed_summary.budget_status);
    try std.testing.expectEqual(@as(u32, 1), suppressed_summary.budget_suppressed_count);
    try std.testing.expectEqual(@as(u32, 3), suppressed_summary.delivery_budget_after);
    try std.testing.expectEqual(@as(u32, 4), suppressed_summary.deferred_budget_after);

    const empty_view = abi.ChrdevNotifyBudgetView{
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
        .delivery_budget = 0,
        .deferred_budget = 0,
    };
    const empty_summary = summarize(empty_view);
    try std.testing.expect(isValid(empty_view));
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_BUDGET_STATUS_NONE), empty_summary.budget_status);
    try std.testing.expectEqual(@as(u32, 0), empty_summary.budget_notify_count);
}
