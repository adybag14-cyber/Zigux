const std = @import("std");
const Io = std.Io;
const abi = @import("abi_bindings");
const parent_plan = @import("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan");
const guard_plan = @import("chrdev_notify_ack_delivery_budget_guard_plan");
const guard_window_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_plan");

fn writeSummary(writer: anytype, summary: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowSummary) !void {
    try writer.writeAll("{\"parent_guard_status\":");
    try writer.print("{d}", .{summary.parent.guard_status});
    try writer.writeAll(",\"window_flags\":");
    try writer.print("{d}", .{summary.window_flags});
    try writer.writeAll(",\"primary_window_before\":");
    try writer.print("{d}", .{summary.primary_window_before});
    try writer.writeAll(",\"primary_window_after\":");
    try writer.print("{d}", .{summary.primary_window_after});
    try writer.writeAll(",\"deferred_window_before\":");
    try writer.print("{d}", .{summary.deferred_window_before});
    try writer.writeAll(",\"deferred_window_after\":");
    try writer.print("{d}", .{summary.deferred_window_after});
    try writer.writeAll(",\"window_floor\":");
    try writer.print("{d}", .{summary.window_floor});
    try writer.writeAll(",\"window_status\":");
    try writer.print("{d}", .{summary.window_status});
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

    const parent_acked = parent_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 1, 0, 3, 0, 2, 1, 2, 0, 1, 0, 3, 0, 2, 1);
    const parent_policy_deferred = parent_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xCCCC, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xC3C3, 1, 0, 1, 0, 0, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_FORCE_DEFERRED, 1, 1, 3, 0, 1, 1, 3, 0, 2, 1, 2, 0, 1, 1, 3, 0, 2, 1);
    const parent_suppressed = parent_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xE5E5, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 0, 0xE5E5, 1, 0, 1, 0, 0, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_SUPPRESS_DROPPED, 1, 1, 2, 0, 1, 1, 3, 0, 2, 1, 2, 1, 1, 1, 3, 0, 2, 1);
    const parent_dropped = parent_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0xDDDD, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xDDDD, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xD4D4, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0);
    const parent_skipped = parent_plan.viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, abi.CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xF6F6, abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE, 3, 4, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xF6F6, 0, 0, 1, 1, 0, 0, 1, 1, 2, 0, 1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 2, 1, 2, 1);
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
    const empty_view = guard_window_plan.viewFromParent(guard_plan.viewFromParent(empty_parent, 0, 0), 0, 0, 0);

    try writer.writeAll("{\"constants\":{\"chrdev_notify_ack_delivery_budget_guard_window_flag_applied\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_APPLIED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_flag_primary_window_used\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_PRIMARY_WINDOW_USED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_flag_deferred_window_used\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_DEFERRED_WINDOW_USED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_flag_primary_held\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_PRIMARY_HELD});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_flag_deferred_held\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_DEFERRED_HELD});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_flag_window_exhausted\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_WINDOW_EXHAUSTED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_flag_passthrough\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_PASSTHROUGH});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_status_none\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_NONE});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_status_acked\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_ACKED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_status_deferred\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_DEFERRED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_status_suppressed\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_SUPPRESSED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_status_coalesced\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_COALESCED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_status_dropped\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_DROPPED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_status_skipped\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_SKIPPED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_status_held\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_HELD});
    try writer.writeAll("}");

    const cases = [_]struct { name: []const u8, view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowView }{
        .{ .name = "acked", .view = guard_window_plan.viewFromParent(guard_plan.viewFromParent(parent_acked, 1, 0), 2, 1, 0) },
        .{ .name = "fallback_deferred", .view = guard_window_plan.viewFromParent(guard_plan.viewFromParent(parent_acked, 1, 0), 0, 2, 0) },
        .{ .name = "primary_held", .view = guard_window_plan.viewFromParent(guard_plan.viewFromParent(parent_acked, 1, 0), 1, 1, 1) },
        .{ .name = "policy_deferred", .view = guard_window_plan.viewFromParent(guard_plan.viewFromParent(parent_policy_deferred, 0, 0), 1, 2, 0) },
        .{ .name = "suppressed", .view = guard_window_plan.viewFromParent(guard_plan.viewFromParent(parent_suppressed, 1, 0), 2, 1, 0) },
        .{ .name = "dropped", .view = guard_window_plan.viewFromParent(guard_plan.viewFromParent(parent_dropped, 0, 0), 0, 0, 0) },
        .{ .name = "skipped", .view = guard_window_plan.viewFromParent(guard_plan.viewFromParent(parent_skipped, 1, 1), 2, 2, 1) },
    };

    for (cases) |case| {
        try writer.writeAll(",\"");
        try writer.writeAll(case.name);
        try writer.writeAll("\":{\"summary\":");
        try writeSummary(writer, guard_window_plan.summarize(case.view));
        try writer.writeAll("}");
    }

    try writer.writeAll(",\"empty\":{\"is_valid\":");
    try writer.writeAll(if (guard_window_plan.isValid(empty_view)) "true" else "false");
    try writer.writeAll(",\"summary\":");
    try writeSummary(writer, guard_window_plan.summarize(empty_view));
    try writer.writeAll("}}\n");
    try stdout_writer.interface.flush();
}