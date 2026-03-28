const std = @import("std");
const abi = @import("abi_bindings");
const chrdev_notify_budget_plan = @import("chrdev_notify_budget_plan");

fn emptyBudgetView() abi.ChrdevNotifyBudgetView {
    return std.mem.zeroInit(abi.ChrdevNotifyBudgetView, .{});
}

fn emptySummary() abi.ChrdevNotifyAckSummary {
    return std.mem.zeroInit(abi.ChrdevNotifyAckSummary, .{
        .resolved_index = abi.CHRDEV_NOTIFY_INDEX_NONE,
        .completion_status = abi.CHRDEV_COMPLETE_STATUS_NONE,
        .notify_status = abi.CHRDEV_NOTIFY_STATUS_NONE,
        .policy_status = abi.CHRDEV_NOTIFY_POLICY_STATUS_NONE,
        .budget_status = abi.CHRDEV_NOTIFY_BUDGET_STATUS_NONE,
        .ack_status = abi.CHRDEV_NOTIFY_ACK_STATUS_NONE,
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
    ack_mask: u32,
    ack_window: u32,
    ack_cookie: u64,
    ack_observed: u32,
) abi.ChrdevNotifyAckView {
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
        .ack_mask = ack_mask,
        .ack_window = ack_window,
        .ack_cookie = ack_cookie,
        .ack_observed = ack_observed,
        .ack_reserved = 0,
    };
}

pub fn asChrdevNotifyBudgetView(view: abi.ChrdevNotifyAckView) abi.ChrdevNotifyBudgetView {
    if (view.reserved != 0 or view.policy_reserved != 0 or view.ack_reserved != 0) {
        return emptyBudgetView();
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
        .delivery_budget = view.delivery_budget,
        .deferred_budget = view.deferred_budget,
    };
}

pub fn isValid(view: abi.ChrdevNotifyAckView) bool {
    if (view.ack_reserved != 0) return false;
    return chrdev_notify_budget_plan.isValid(asChrdevNotifyBudgetView(view));
}

fn matchedAckMask(summary: abi.ChrdevNotifyBudgetSummary, ack_mask: u32) u32 {
    const status_mask = switch (summary.budget_status) {
        abi.CHRDEV_NOTIFY_BUDGET_STATUS_ISSUED => abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED,
        abi.CHRDEV_NOTIFY_BUDGET_STATUS_DEFERRED => abi.CHRDEV_NOTIFY_ACK_MASK_DEFERRED,
        abi.CHRDEV_NOTIFY_BUDGET_STATUS_DROPPED => abi.CHRDEV_NOTIFY_ACK_MASK_DROPPED,
        abi.CHRDEV_NOTIFY_BUDGET_STATUS_SUPPRESSED => abi.CHRDEV_NOTIFY_ACK_MASK_SUPPRESSED,
        else => 0,
    };
    return ack_mask & status_mask;
}

pub fn summarize(view: abi.ChrdevNotifyAckView) abi.ChrdevNotifyAckSummary {
    if (!isValid(view)) return emptySummary();

    const budget_summary = chrdev_notify_budget_plan.summarize(asChrdevNotifyBudgetView(view));
    const matched_ack_mask = matchedAckMask(budget_summary, view.ack_mask);

    var summary = abi.ChrdevNotifyAckSummary{
        .major = budget_summary.major,
        .target_minor = budget_summary.target_minor,
        .selected_count = budget_summary.selected_count,
        .resolved_index = budget_summary.resolved_index,
        .resolved_dev = budget_summary.resolved_dev,
        .granted_mode = budget_summary.granted_mode,
        .io_op = budget_summary.io_op,
        .requested_bytes = budget_summary.requested_bytes,
        .start_offset = budget_summary.start_offset,
        .next_offset = budget_summary.next_offset,
        .initial_bytes_completed = budget_summary.initial_bytes_completed,
        .final_bytes_completed = budget_summary.final_bytes_completed,
        .pass_count = budget_summary.pass_count,
        .issued_bytes = budget_summary.issued_bytes,
        .remaining_bytes = budget_summary.remaining_bytes,
        .projected_remaining_bytes = budget_summary.projected_remaining_bytes,
        .entry_ops = budget_summary.entry_ops,
        .data_ops = budget_summary.data_ops,
        .exit_ops = budget_summary.exit_ops,
        .blocked_ops = budget_summary.blocked_ops,
        .retry_count = budget_summary.retry_count,
        .stall_count = budget_summary.stall_count,
        .requeue_count = budget_summary.requeue_count,
        .queue_depth_before = budget_summary.queue_depth_before,
        .queue_depth_after = budget_summary.queue_depth_after,
        .remaining_retry_budget = budget_summary.remaining_retry_budget,
        .remaining_requeue_budget = budget_summary.remaining_requeue_budget,
        .backoff_ticks = budget_summary.backoff_ticks,
        .completion_cookie = budget_summary.completion_cookie,
        .completion_status = budget_summary.completion_status,
        .completion_count = budget_summary.completion_count,
        .deferred_count = budget_summary.deferred_count,
        .failure_count = budget_summary.failure_count,
        .remaining_completion_budget = budget_summary.remaining_completion_budget,
        .notify_mask = budget_summary.notify_mask,
        .matched_notify_mask = budget_summary.matched_notify_mask,
        .notify_status = budget_summary.notify_status,
        .notify_count = budget_summary.notify_count,
        .deferred_notify_count = budget_summary.deferred_notify_count,
        .dropped_notify_count = budget_summary.dropped_notify_count,
        .remaining_notify_budget = budget_summary.remaining_notify_budget,
        .notify_cookie = budget_summary.notify_cookie,
        .flags = budget_summary.flags,
        .policy_flags = budget_summary.policy_flags,
        .effective_policy_flags = budget_summary.effective_policy_flags,
        .effective_notify_cookie = budget_summary.effective_notify_cookie,
        .policy_status = budget_summary.policy_status,
        .policy_notify_count = budget_summary.policy_notify_count,
        .policy_deferred_count = budget_summary.policy_deferred_count,
        .policy_suppressed_count = budget_summary.policy_suppressed_count,
        .policy_coalesced_count = budget_summary.policy_coalesced_count,
        .budget_flags = budget_summary.budget_flags,
        .delivery_budget_before = budget_summary.delivery_budget_before,
        .delivery_budget_after = budget_summary.delivery_budget_after,
        .deferred_budget_before = budget_summary.deferred_budget_before,
        .deferred_budget_after = budget_summary.deferred_budget_after,
        .budget_status = budget_summary.budget_status,
        .budget_notify_count = budget_summary.budget_notify_count,
        .budget_deferred_count = budget_summary.budget_deferred_count,
        .budget_dropped_count = budget_summary.budget_dropped_count,
        .budget_suppressed_count = budget_summary.budget_suppressed_count,
        .ack_mask = view.ack_mask,
        .matched_ack_mask = matched_ack_mask,
        .ack_status = abi.CHRDEV_NOTIFY_ACK_STATUS_NONE,
        .ack_count = 0,
        .deferred_ack_count = 0,
        .expired_ack_count = 0,
        .skipped_ack_count = 0,
        .ack_window_before = view.ack_window,
        .ack_window_after = view.ack_window,
        .ack_cookie = view.ack_cookie,
        .ack_flags = 0,
    };

    if (budget_summary.budget_status != abi.CHRDEV_NOTIFY_BUDGET_STATUS_NONE) {
        summary.ack_flags |= abi.CHRDEV_NOTIFY_ACK_FLAG_APPLICABLE;
    }

    if (matched_ack_mask == 0) {
        if (budget_summary.budget_status != abi.CHRDEV_NOTIFY_BUDGET_STATUS_NONE) {
            summary.ack_status = abi.CHRDEV_NOTIFY_ACK_STATUS_SKIPPED;
            summary.ack_flags |= abi.CHRDEV_NOTIFY_ACK_FLAG_SKIPPED;
            summary.skipped_ack_count = 1;
        }
        return summary;
    }

    if (view.ack_observed != 0) {
        summary.ack_status = abi.CHRDEV_NOTIFY_ACK_STATUS_ACKED;
        summary.ack_flags |= abi.CHRDEV_NOTIFY_ACK_FLAG_ACKED;
        summary.ack_count = 1;
        return summary;
    }

    if (summary.ack_window_after > 0) {
        summary.ack_window_after -= 1;
        summary.ack_status = abi.CHRDEV_NOTIFY_ACK_STATUS_DEFERRED;
        summary.ack_flags |= abi.CHRDEV_NOTIFY_ACK_FLAG_DEFERRED | abi.CHRDEV_NOTIFY_ACK_FLAG_WINDOW_USED;
        summary.deferred_ack_count = 1;
        return summary;
    }

    summary.ack_status = abi.CHRDEV_NOTIFY_ACK_STATUS_EXPIRED;
    summary.ack_flags |= abi.CHRDEV_NOTIFY_ACK_FLAG_EXPIRED | abi.CHRDEV_NOTIFY_ACK_FLAG_WINDOW_EXHAUSTED;
    summary.expired_ack_count = 1;
    return summary;
}
