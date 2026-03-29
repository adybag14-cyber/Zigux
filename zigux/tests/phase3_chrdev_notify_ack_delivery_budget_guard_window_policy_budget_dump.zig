const std = @import("std");
const Io = std.Io;
const abi = @import("abi_bindings");
const parent_plan = @import("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan");
const guard_plan = @import("chrdev_notify_ack_delivery_budget_guard_plan");
const guard_window_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_plan");
const policy_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_policy_plan");
const budget_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan");

fn writeSummary(writer: anytype, summary: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetSummary) !void {
    try writer.writeAll("{\"parent_policy_status\":");
    try writer.print("{d}", .{summary.parent.policy_status});
    try writer.writeAll(",\"budget_flags\":");
    try writer.print("{d}", .{summary.budget_flags});
    try writer.writeAll(",\"primary_budget_before\":");
    try writer.print("{d}", .{summary.primary_budget_before});
    try writer.writeAll(",\"primary_budget_after\":");
    try writer.print("{d}", .{summary.primary_budget_after});
    try writer.writeAll(",\"deferred_budget_before\":");
    try writer.print("{d}", .{summary.deferred_budget_before});
    try writer.writeAll(",\"deferred_budget_after\":");
    try writer.print("{d}", .{summary.deferred_budget_after});
    try writer.writeAll(",\"budget_status\":");
    try writer.print("{d}", .{summary.budget_status});
    try writer.writeAll(",\"acked_count\":");
    try writer.print("{d}", .{summary.acked_count});
    try writer.writeAll(",\"deferred_count\":");
    try writer.print("{d}", .{summary.deferred_count});
    try writer.writeAll(",\"suppressed_count\":");
    try writer.print("{d}", .{summary.suppressed_count});
    try writer.writeAll(",\"coalesced_count\":");
    try writer.print("{d}", .{summary.coalesced_count});
    try writer.writeAll(",\"dropped_count\":");
    try writer.print("{d}", .{summary.dropped_count});
    try writer.writeAll(",\"skipped_count\":");
    try writer.print("{d}", .{summary.skipped_count});
    try writer.writeAll(",\"held_count\":");
    try writer.print("{d}", .{summary.held_count});
    try writer.writeAll("}");
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [32768]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout_writer.interface;

    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const acked_window = guard_window_plan.viewFromParent(
        guard_plan.viewFromParent(
            parent_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 1, 0, 3, 0, 2, 1, 2, 0, 1, 0, 3, 0, 2, 1),
            1,
            0,
        ),
        2,
        1,
        0,
    );
    const held_window = guard_window_plan.viewFromParent(
        guard_plan.viewFromParent(
            parent_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 1, 0, 3, 0, 2, 1, 2, 0, 1, 0, 3, 0, 2, 1),
            1,
            0,
        ),
        1,
        1,
        1,
    );
    const dropped_window = guard_window_plan.viewFromParent(
        guard_plan.viewFromParent(
            parent_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0xDDDD, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xDDDD, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xD4D4, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0),
            0,
            0,
        ),
        0,
        0,
        0,
    );
    const skipped_window = guard_window_plan.viewFromParent(
        guard_plan.viewFromParent(
            parent_plan.viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, abi.CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xF6F6, abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE, 3, 4, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xF6F6, 0, 0, 1, 1, 0, 0, 1, 1, 2, 0, 1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 2, 1, 2, 1),
            1,
            1,
        ),
        2,
        2,
        1,
    );

    const acked_policy = policy_plan.viewFromParent(acked_window, 0);
    const forced_deferred_policy = policy_plan.viewFromParent(acked_window, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_FORCE_DEFERRED);
    const held_policy = policy_plan.viewFromParent(held_window, 0);
    const suppressed_held_policy = policy_plan.viewFromParent(held_window, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_SUPPRESS_HELD);
    const dropped_policy = policy_plan.viewFromParent(dropped_window, 0);
    const suppressed_dropped_policy = policy_plan.viewFromParent(dropped_window, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_SUPPRESS_DROPPED);
    const skipped_policy = policy_plan.viewFromParent(skipped_window, 0);

    var empty_parent = std.mem.zeroInit(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetView, .{});
    empty_parent.major = 240;
    empty_parent.request_count = 2;
    empty_parent.policy = abi.IDA_POLICY_FIRST_FIT;
    empty_parent.requested_mode = abi.CHRDEV_MODE_READ;
    empty_parent.supported_mode = abi.CHRDEV_MODE_READ;
    empty_parent.available_ops = abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ;
    empty_parent.io_op = abi.CHRDEV_IO_OP_READ;
    empty_parent.requested_bytes = 8;
    empty_parent.max_chunk_bytes = 8;
    empty_parent.max_segments = 1;
    empty_parent.resume_passes = 2;
    empty_parent.retry_budget = 1;
    empty_parent.stall_budget = 1;
    empty_parent.backoff_quanta = 5;
    empty_parent.queue_capacity = 2;
    empty_parent.requeue_budget = 1;
    empty_parent.completion_cookie = 0x9999;
    empty_parent.notify_mask = abi.CHRDEV_NOTIFY_MASK_SUCCESS;
    empty_parent.notify_cookie = 0xFFFF;
    empty_parent.ack_mask = abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED;
    empty_parent.ack_cookie = 0xABCD;
    empty_parent.ack_budget = 1;
    empty_parent.deferred_ack_budget = 1;
    const empty_guard = guard_plan.viewFromParent(empty_parent, 0, 0);
    const empty_window = guard_window_plan.viewFromParent(empty_guard, 0, 0, 0);
    const empty_policy = policy_plan.viewFromParent(empty_window, 0);
    const empty_view = budget_plan.viewFromParent(empty_policy, 0, 0);

    try writer.writeAll("{\"constants\":{\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_flag_budget_applied\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_FLAG_BUDGET_APPLIED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_flag_primary_budget_used\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_FLAG_PRIMARY_BUDGET_USED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_flag_deferred_budget_used\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_FLAG_DEFERRED_BUDGET_USED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_flag_primary_budget_exhausted\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_FLAG_PRIMARY_BUDGET_EXHAUSTED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_flag_deferred_budget_exhausted\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_FLAG_DEFERRED_BUDGET_EXHAUSTED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_status_none\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_NONE});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_status_acked\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_ACKED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_status_deferred\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_DEFERRED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_status_suppressed\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_SUPPRESSED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_status_coalesced\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_COALESCED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_status_dropped\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_DROPPED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_status_skipped\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_SKIPPED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_status_held\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_HELD});
    try writer.writeAll("}");

    const cases = [_]struct { name: []const u8, view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetView }{
        .{ .name = "acked", .view = budget_plan.viewFromParent(acked_policy, 1, 1) },
        .{ .name = "fallback_deferred", .view = budget_plan.viewFromParent(acked_policy, 0, 1) },
        .{ .name = "policy_deferred", .view = budget_plan.viewFromParent(forced_deferred_policy, 1, 1) },
        .{ .name = "held", .view = budget_plan.viewFromParent(held_policy, 1, 1) },
        .{ .name = "suppressed_held", .view = budget_plan.viewFromParent(suppressed_held_policy, 1, 1) },
        .{ .name = "dropped", .view = budget_plan.viewFromParent(dropped_policy, 0, 0) },
        .{ .name = "suppressed_dropped", .view = budget_plan.viewFromParent(suppressed_dropped_policy, 1, 1) },
        .{ .name = "skipped", .view = budget_plan.viewFromParent(skipped_policy, 1, 1) },
    };

    for (cases) |case| {
        try writer.writeAll(",\"");
        try writer.writeAll(case.name);
        try writer.writeAll("\":{\"summary\":");
        try writeSummary(writer, budget_plan.summarize(case.view));
        try writer.writeAll("}");
    }

    try writer.writeAll(",\"empty\":{\"is_valid\":");
    try writer.writeAll(if (budget_plan.isValid(empty_view)) "true" else "false");
    try writer.writeAll(",\"summary\":");
    try writeSummary(writer, budget_plan.summarize(empty_view));
    try writer.writeAll("}}\n");
    try stdout_writer.interface.flush();
}
