const std = @import("std");
const abi = @import("abi_bindings");
const chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_plan = @import("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_plan");

fn emptyParentView() abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryView {
    return std.mem.zeroInit(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryView, .{});
}

fn emptySummary() abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowSummary {
    return std.mem.zeroInit(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowSummary, .{
        .resolved_index = abi.CHRDEV_NOTIFY_INDEX_NONE,
        .completion_status = abi.CHRDEV_COMPLETE_STATUS_NONE,
        .notify_status = abi.CHRDEV_NOTIFY_STATUS_NONE,
        .policy_status = abi.CHRDEV_NOTIFY_POLICY_STATUS_NONE,
        .budget_status = abi.CHRDEV_NOTIFY_BUDGET_STATUS_NONE,
        .ack_status = abi.CHRDEV_NOTIFY_ACK_STATUS_NONE,
        .ack_policy_status = abi.CHRDEV_NOTIFY_ACK_POLICY_STATUS_NONE,
        .ack_budget_status = abi.CHRDEV_NOTIFY_ACK_BUDGET_STATUS_NONE,
        .window_status = abi.CHRDEV_NOTIFY_ACK_WINDOW_STATUS_NONE,
        .window_policy_status = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_NONE,
        .window_policy_budget_status = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_NONE,
        .window_policy_budget_window_status = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_NONE,
        .window_policy_budget_window_delivery_status = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_NONE,
        .window_policy_budget_window_delivery_window_status = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_NONE,
        .window_policy_budget_window_delivery_window_budget_status = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_NONE,
        .window_policy_budget_window_delivery_window_budget_window_status = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_NONE,
        .window_policy_budget_window_delivery_window_budget_window_delivery_status = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_NONE,
        .window_policy_budget_window_delivery_window_budget_window_delivery_window_status = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_NONE,
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
    ack_policy_flags: u32,
    ack_budget: u32,
    deferred_ack_budget: u32,
    window_floor: u32,
    window_policy_flags: u32,
    window_policy_budget: u32,
    deferred_window_policy_budget: u32,
    window_policy_budget_window: u32,
    window_policy_budget_window_floor: u32,
    window_policy_budget_window_delivery_budget: u32,
    deferred_window_policy_budget_window_delivery_budget: u32,
    window_policy_budget_window_delivery_window: u32,
    window_policy_budget_window_delivery_window_floor: u32,
    window_policy_budget_window_delivery_window_budget: u32,
    deferred_window_policy_budget_window_delivery_window_budget: u32,
    window_policy_budget_window_delivery_window_budget_window: u32,
    window_policy_budget_window_delivery_window_budget_window_floor: u32,
    window_policy_budget_window_delivery_window_budget_window_delivery_budget: u32,
    deferred_window_policy_budget_window_delivery_window_budget_window_delivery_budget: u32,
    window_policy_budget_window_delivery_window_budget_window_delivery_window: u32,
    window_policy_budget_window_delivery_window_budget_window_delivery_window_floor: u32,
) abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowView {
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
        .ack_policy_flags = ack_policy_flags,
        .ack_policy_reserved = 0,
        .ack_budget = ack_budget,
        .deferred_ack_budget = deferred_ack_budget,
        .ack_budget_reserved = 0,
        .window_floor = window_floor,
        .window_reserved = 0,
        .window_policy_flags = window_policy_flags,
        .window_policy_reserved = 0,
        .window_policy_budget = window_policy_budget,
        .deferred_window_policy_budget = deferred_window_policy_budget,
        .window_policy_budget_reserved = 0,
        .window_policy_budget_window = window_policy_budget_window,
        .window_policy_budget_window_floor = window_policy_budget_window_floor,
        .window_policy_budget_window_reserved = 0,
        .window_policy_budget_window_delivery_budget = window_policy_budget_window_delivery_budget,
        .deferred_window_policy_budget_window_delivery_budget = deferred_window_policy_budget_window_delivery_budget,
        .window_policy_budget_window_delivery_reserved = 0,
        .window_policy_budget_window_delivery_window = window_policy_budget_window_delivery_window,
        .window_policy_budget_window_delivery_window_floor = window_policy_budget_window_delivery_window_floor,
        .window_policy_budget_window_delivery_window_reserved = 0,
        .window_policy_budget_window_delivery_window_budget = window_policy_budget_window_delivery_window_budget,
        .deferred_window_policy_budget_window_delivery_window_budget = deferred_window_policy_budget_window_delivery_window_budget,
        .window_policy_budget_window_delivery_window_budget_reserved = 0,
        .window_policy_budget_window_delivery_window_budget_window = window_policy_budget_window_delivery_window_budget_window,
        .window_policy_budget_window_delivery_window_budget_window_floor = window_policy_budget_window_delivery_window_budget_window_floor,
        .window_policy_budget_window_delivery_window_budget_window_reserved = 0,
        .window_policy_budget_window_delivery_window_budget_window_delivery_budget = window_policy_budget_window_delivery_window_budget_window_delivery_budget,
        .deferred_window_policy_budget_window_delivery_window_budget_window_delivery_budget = deferred_window_policy_budget_window_delivery_window_budget_window_delivery_budget,
        .window_policy_budget_window_delivery_window_budget_window_delivery_reserved = 0,
        .window_policy_budget_window_delivery_window_budget_window_delivery_window = window_policy_budget_window_delivery_window_budget_window_delivery_window,
        .window_policy_budget_window_delivery_window_budget_window_delivery_window_floor = window_policy_budget_window_delivery_window_budget_window_delivery_window_floor,
        .window_policy_budget_window_delivery_window_budget_window_delivery_window_reserved = 0,
    };
}

pub fn asParentView(view: abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowView) abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryView {
    if (view.window_policy_budget_window_delivery_window_budget_window_delivery_window_reserved != 0) {
        return emptyParentView();
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
        .reserved = view.reserved,
        .policy_flags = view.policy_flags,
        .policy_reserved = view.policy_reserved,
        .delivery_budget = view.delivery_budget,
        .deferred_budget = view.deferred_budget,
        .ack_mask = view.ack_mask,
        .ack_window = view.ack_window,
        .ack_cookie = view.ack_cookie,
        .ack_observed = view.ack_observed,
        .ack_reserved = view.ack_reserved,
        .ack_policy_flags = view.ack_policy_flags,
        .ack_policy_reserved = view.ack_policy_reserved,
        .ack_budget = view.ack_budget,
        .deferred_ack_budget = view.deferred_ack_budget,
        .ack_budget_reserved = view.ack_budget_reserved,
        .window_floor = view.window_floor,
        .window_reserved = view.window_reserved,
        .window_policy_flags = view.window_policy_flags,
        .window_policy_reserved = view.window_policy_reserved,
        .window_policy_budget = view.window_policy_budget,
        .deferred_window_policy_budget = view.deferred_window_policy_budget,
        .window_policy_budget_reserved = view.window_policy_budget_reserved,
        .window_policy_budget_window = view.window_policy_budget_window,
        .window_policy_budget_window_floor = view.window_policy_budget_window_floor,
        .window_policy_budget_window_reserved = view.window_policy_budget_window_reserved,
        .window_policy_budget_window_delivery_budget = view.window_policy_budget_window_delivery_budget,
        .deferred_window_policy_budget_window_delivery_budget = view.deferred_window_policy_budget_window_delivery_budget,
        .window_policy_budget_window_delivery_reserved = view.window_policy_budget_window_delivery_reserved,
        .window_policy_budget_window_delivery_window = view.window_policy_budget_window_delivery_window,
        .window_policy_budget_window_delivery_window_floor = view.window_policy_budget_window_delivery_window_floor,
        .window_policy_budget_window_delivery_window_reserved = view.window_policy_budget_window_delivery_window_reserved,
        .window_policy_budget_window_delivery_window_budget = view.window_policy_budget_window_delivery_window_budget,
        .deferred_window_policy_budget_window_delivery_window_budget = view.deferred_window_policy_budget_window_delivery_window_budget,
        .window_policy_budget_window_delivery_window_budget_reserved = view.window_policy_budget_window_delivery_window_budget_reserved,
        .window_policy_budget_window_delivery_window_budget_window = view.window_policy_budget_window_delivery_window_budget_window,
        .window_policy_budget_window_delivery_window_budget_window_floor = view.window_policy_budget_window_delivery_window_budget_window_floor,
        .window_policy_budget_window_delivery_window_budget_window_reserved = view.window_policy_budget_window_delivery_window_budget_window_reserved,
        .window_policy_budget_window_delivery_window_budget_window_delivery_budget = view.window_policy_budget_window_delivery_window_budget_window_delivery_budget,
        .deferred_window_policy_budget_window_delivery_window_budget_window_delivery_budget = view.deferred_window_policy_budget_window_delivery_window_budget_window_delivery_budget,
        .window_policy_budget_window_delivery_window_budget_window_delivery_reserved = view.window_policy_budget_window_delivery_window_budget_window_delivery_reserved,
    };
}

pub fn isValid(view: abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowView) bool {
    if (view.window_policy_budget_window_delivery_window_budget_window_delivery_window_reserved != 0) return false;
    return chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_plan.isValid(asParentView(view));
}

pub fn summarize(view: abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowView) abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowSummary {
    if (!isValid(view)) return emptySummary();

    const parent_summary = chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_plan.summarize(asParentView(view));
    var summary = emptySummary();
    @memcpy(
        std.mem.asBytes(&summary)[0..@sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliverySummary)],
        std.mem.asBytes(&parent_summary),
    );

    summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_flags = 0;
    summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_before = view.window_policy_budget_window_delivery_window_budget_window_delivery_window;
    summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_after = view.window_policy_budget_window_delivery_window_budget_window_delivery_window;
    summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_floor = view.window_policy_budget_window_delivery_window_budget_window_delivery_window_floor;
    summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_status = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_NONE;
    summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_acked_count = 0;
    summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_deferred_count = 0;
    summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_suppressed_count = 0;
    summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_coalesced_count = 0;
    summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_dropped_count = 0;
    summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_skipped_count = 0;

    switch (parent_summary.window_policy_budget_window_delivery_window_budget_window_delivery_status) {
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_NONE => {},
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_SUPPRESSED => {
            summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_status = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SUPPRESSED;
            summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_suppressed_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_SKIPPED => {
            summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_status = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED;
            summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_skipped_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_DROPPED => {
            summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_status = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DROPPED;
            summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_dropped_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_ACKED,
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_DEFERRED,
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_COALESCED,
        => {
            summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_flags |= abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_WINDOW_APPLIED;
            if (summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_before == 0) {
                summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_flags |= abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_WINDOW_EXHAUSTED;
                summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_status = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DROPPED;
                summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_dropped_count = 1;
            } else if (summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_before <= view.window_policy_budget_window_delivery_window_budget_window_delivery_window_floor) {
                summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_flags |= abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_FLOOR_HELD | abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_FLOOR_BLOCKED;
                summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_status = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DEFERRED;
                summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_deferred_count = 1;
            } else {
                summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_after = summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_before - 1;
                summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_flags |= abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_WINDOW_USED;
                switch (parent_summary.window_policy_budget_window_delivery_window_budget_window_delivery_status) {
                    abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_ACKED => {
                        summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_status = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_ACKED;
                        summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_acked_count = 1;
                    },
                    abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_COALESCED => {
                        summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_status = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_COALESCED;
                        summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_coalesced_count = 1;
                    },
                    else => {
                        summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_status = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DEFERRED;
                        summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_deferred_count = 1;
                    },
                }
            }
        },
        else => {},
    }

    return summary;
}
