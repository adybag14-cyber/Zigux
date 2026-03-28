const std = @import("std");
const abi = @import("abi_bindings");
const chrdev_notify_ack_plan = @import("chrdev_notify_ack_plan");

const allowed_ack_policy_flags =
    abi.CHRDEV_NOTIFY_ACK_POLICY_FORCE_DEFERRED |
    abi.CHRDEV_NOTIFY_ACK_POLICY_SUPPRESS_EXPIRED |
    abi.CHRDEV_NOTIFY_ACK_POLICY_COALESCE_COOKIE;

fn emptyAckView() abi.ChrdevNotifyAckView {
    return std.mem.zeroInit(abi.ChrdevNotifyAckView, .{});
}

fn emptySummary() abi.ChrdevNotifyAckPolicySummary {
    return std.mem.zeroInit(abi.ChrdevNotifyAckPolicySummary, .{
        .resolved_index = abi.CHRDEV_NOTIFY_INDEX_NONE,
        .completion_status = abi.CHRDEV_COMPLETE_STATUS_NONE,
        .notify_status = abi.CHRDEV_NOTIFY_STATUS_NONE,
        .policy_status = abi.CHRDEV_NOTIFY_POLICY_STATUS_NONE,
        .budget_status = abi.CHRDEV_NOTIFY_BUDGET_STATUS_NONE,
        .ack_status = abi.CHRDEV_NOTIFY_ACK_STATUS_NONE,
        .ack_policy_status = abi.CHRDEV_NOTIFY_ACK_POLICY_STATUS_NONE,
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
) abi.ChrdevNotifyAckPolicyView {
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
    };
}

pub fn asChrdevNotifyAckView(view: abi.ChrdevNotifyAckPolicyView) abi.ChrdevNotifyAckView {
    if (view.reserved != 0 or view.policy_reserved != 0 or view.ack_reserved != 0 or view.ack_policy_reserved != 0) {
        return emptyAckView();
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
        .ack_mask = view.ack_mask,
        .ack_window = view.ack_window,
        .ack_cookie = view.ack_cookie,
        .ack_observed = view.ack_observed,
        .ack_reserved = 0,
    };
}

pub fn isValid(view: abi.ChrdevNotifyAckPolicyView) bool {
    if (view.ack_policy_reserved != 0) return false;
    if ((view.ack_policy_flags & ~allowed_ack_policy_flags) != 0) return false;
    return chrdev_notify_ack_plan.isValid(asChrdevNotifyAckView(view));
}

pub fn summarize(view: abi.ChrdevNotifyAckPolicyView) abi.ChrdevNotifyAckPolicySummary {
    if (!isValid(view)) return emptySummary();

    const ack_summary = chrdev_notify_ack_plan.summarize(asChrdevNotifyAckView(view));
    var summary = emptySummary();
    @memcpy(std.mem.asBytes(&summary)[0..@sizeOf(abi.ChrdevNotifyAckSummary)], std.mem.asBytes(&ack_summary));
    summary.ack_policy_flags = view.ack_policy_flags;

    switch (ack_summary.ack_status) {
        abi.CHRDEV_NOTIFY_ACK_STATUS_NONE => {},
        abi.CHRDEV_NOTIFY_ACK_STATUS_SKIPPED => {
            summary.ack_policy_status = abi.CHRDEV_NOTIFY_ACK_POLICY_STATUS_SKIPPED;
            summary.policy_skipped_ack_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_STATUS_EXPIRED => {
            if ((view.ack_policy_flags & abi.CHRDEV_NOTIFY_ACK_POLICY_SUPPRESS_EXPIRED) != 0) {
                summary.effective_ack_policy_flags = abi.CHRDEV_NOTIFY_ACK_POLICY_SUPPRESS_EXPIRED;
                summary.ack_policy_status = abi.CHRDEV_NOTIFY_ACK_POLICY_STATUS_SUPPRESSED;
                summary.policy_suppressed_ack_count = 1;
            } else if ((view.ack_policy_flags & abi.CHRDEV_NOTIFY_ACK_POLICY_FORCE_DEFERRED) != 0) {
                summary.effective_ack_policy_flags = abi.CHRDEV_NOTIFY_ACK_POLICY_FORCE_DEFERRED;
                summary.effective_ack_cookie = ack_summary.ack_cookie;
                summary.ack_policy_status = abi.CHRDEV_NOTIFY_ACK_POLICY_STATUS_DEFERRED;
                summary.policy_deferred_ack_count = 1;
            } else {
                summary.effective_ack_cookie = ack_summary.ack_cookie;
                summary.ack_policy_status = abi.CHRDEV_NOTIFY_ACK_POLICY_STATUS_EXPIRED;
                summary.policy_expired_ack_count = 1;
            }
        },
        abi.CHRDEV_NOTIFY_ACK_STATUS_DEFERRED => {
            if ((view.ack_policy_flags & abi.CHRDEV_NOTIFY_ACK_POLICY_FORCE_DEFERRED) != 0) {
                summary.effective_ack_policy_flags = abi.CHRDEV_NOTIFY_ACK_POLICY_FORCE_DEFERRED;
            }
            summary.effective_ack_cookie = ack_summary.ack_cookie;
            summary.ack_policy_status = abi.CHRDEV_NOTIFY_ACK_POLICY_STATUS_DEFERRED;
            summary.policy_deferred_ack_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_STATUS_ACKED => {
            if ((view.ack_policy_flags & abi.CHRDEV_NOTIFY_ACK_POLICY_COALESCE_COOKIE) != 0 and
                ack_summary.ack_cookie != 0 and
                (ack_summary.ack_cookie == ack_summary.notify_cookie or ack_summary.ack_cookie == ack_summary.completion_cookie))
            {
                summary.effective_ack_policy_flags = abi.CHRDEV_NOTIFY_ACK_POLICY_COALESCE_COOKIE;
                summary.effective_ack_cookie = ack_summary.ack_cookie;
                summary.ack_policy_status = abi.CHRDEV_NOTIFY_ACK_POLICY_STATUS_COALESCED;
                summary.policy_coalesced_ack_count = 1;
            } else if ((view.ack_policy_flags & abi.CHRDEV_NOTIFY_ACK_POLICY_FORCE_DEFERRED) != 0) {
                summary.effective_ack_policy_flags = abi.CHRDEV_NOTIFY_ACK_POLICY_FORCE_DEFERRED;
                summary.effective_ack_cookie = ack_summary.ack_cookie;
                summary.ack_policy_status = abi.CHRDEV_NOTIFY_ACK_POLICY_STATUS_DEFERRED;
                summary.policy_deferred_ack_count = 1;
            } else {
                summary.effective_ack_cookie = ack_summary.ack_cookie;
                summary.ack_policy_status = abi.CHRDEV_NOTIFY_ACK_POLICY_STATUS_ACKED;
                summary.policy_acked_count = 1;
            }
        },
        else => {},
    }

    return summary;
}
