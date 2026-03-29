const std = @import("std");
const Io = std.Io;
const abi = @import("abi_bindings");
const parent_plan = @import("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan");
const guard_plan = @import("chrdev_notify_ack_delivery_budget_guard_plan");
const guard_window_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_plan");
const policy_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_policy_plan");
const budget_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan");
const budget_window_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_plan");

fn writeSummary(writer: anytype, summary: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowSummary) !void {
    try writer.writeAll("{\"parent_budget_status\":");
    try writer.print("{d}", .{summary.parent.budget_status});
    try writer.writeAll(",\"budget_window_flags\":");
    try writer.print("{d}", .{summary.budget_window_flags});
    try writer.writeAll(",\"budget_window_before\":");
    try writer.print("{d}", .{summary.budget_window_before});
    try writer.writeAll(",\"budget_window_after\":");
    try writer.print("{d}", .{summary.budget_window_after});
    try writer.writeAll(",\"budget_window_floor\":");
    try writer.print("{d}", .{summary.budget_window_floor});
    try writer.writeAll(",\"budget_window_status\":");
    try writer.print("{d}", .{summary.budget_window_status});
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
    const skipped_policy = policy_plan.viewFromParent(skipped_window, 0);

    const empty_view = std.mem.zeroInit(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowView, .{});

    try writer.writeAll("{\"constants\":{\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_flag_window_applied\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_FLAG_WINDOW_APPLIED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_flag_window_used\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_FLAG_WINDOW_USED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_flag_floor_held\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_FLAG_FLOOR_HELD});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_flag_floor_blocked\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_FLAG_FLOOR_BLOCKED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_flag_window_exhausted\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_FLAG_WINDOW_EXHAUSTED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_status_none\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_NONE});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_status_acked\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_ACKED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_status_deferred\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_DEFERRED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_status_suppressed\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_SUPPRESSED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_status_coalesced\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_COALESCED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_status_dropped\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_DROPPED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_status_skipped\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_SKIPPED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_status_held\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_HELD});
    try writer.writeAll("}");

    const cases = [_]struct { name: []const u8, view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowView }{
        .{ .name = "acked", .view = budget_window_plan.viewFromParent(budget_plan.viewFromParent(acked_policy, 1, 1), 2, 0) },
        .{ .name = "policy_deferred", .view = budget_window_plan.viewFromParent(budget_plan.viewFromParent(forced_deferred_policy, 1, 1), 2, 0) },
        .{ .name = "floor_held", .view = budget_window_plan.viewFromParent(budget_plan.viewFromParent(acked_policy, 1, 1), 1, 1) },
        .{ .name = "held", .view = budget_window_plan.viewFromParent(budget_plan.viewFromParent(held_policy, 1, 1), 2, 0) },
        .{ .name = "suppressed_held", .view = budget_window_plan.viewFromParent(budget_plan.viewFromParent(suppressed_held_policy, 1, 1), 2, 0) },
        .{ .name = "dropped", .view = budget_window_plan.viewFromParent(budget_plan.viewFromParent(dropped_policy, 0, 0), 2, 0) },
        .{ .name = "skipped", .view = budget_window_plan.viewFromParent(budget_plan.viewFromParent(skipped_policy, 1, 1), 2, 0) },
    };

    for (cases) |case| {
        try writer.writeAll(",\"");
        try writer.writeAll(case.name);
        try writer.writeAll("\":{\"summary\":");
        try writeSummary(writer, budget_window_plan.summarize(case.view));
        try writer.writeAll("}");
    }

    try writer.writeAll(",\"empty\":{\"is_valid\":");
    try writer.writeAll(if (budget_window_plan.isValid(empty_view)) "true" else "false");
    try writer.writeAll(",\"summary\":");
    try writeSummary(writer, budget_window_plan.summarize(empty_view));
    try writer.writeAll("}}\n");
    try stdout_writer.interface.flush();
}
