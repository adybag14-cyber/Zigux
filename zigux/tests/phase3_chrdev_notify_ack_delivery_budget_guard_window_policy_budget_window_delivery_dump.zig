const std = @import("std");
const Io = std.Io;
const abi = @import("abi_bindings");
const parent_plan = @import("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan");
const guard_plan = @import("chrdev_notify_ack_delivery_budget_guard_plan");
const guard_window_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_plan");
const policy_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_policy_plan");
const budget_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan");
const budget_window_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_plan");
const delivery_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_plan");

fn writeSummary(writer: anytype, summary: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliverySummary) !void {
    try writer.writeAll("{\"parent_budget_window_status\":");
    try writer.print("{d}", .{summary.parent.budget_window_status});
    try writer.writeAll(",\"delivery_flags\":");
    try writer.print("{d}", .{summary.delivery_flags});
    try writer.writeAll(",\"primary_delivery_budget_before\":");
    try writer.print("{d}", .{summary.primary_delivery_budget_before});
    try writer.writeAll(",\"primary_delivery_budget_after\":");
    try writer.print("{d}", .{summary.primary_delivery_budget_after});
    try writer.writeAll(",\"deferred_delivery_budget_before\":");
    try writer.print("{d}", .{summary.deferred_delivery_budget_before});
    try writer.writeAll(",\"deferred_delivery_budget_after\":");
    try writer.print("{d}", .{summary.deferred_delivery_budget_after});
    try writer.writeAll(",\"delivery_status\":");
    try writer.print("{d}", .{summary.delivery_status});
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

fn makeParentAcked(words: []const usize) abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetView {
    return parent_plan.viewFromBits(words, 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 1, 0, 3, 0, 2, 1, 2, 0, 1, 0, 3, 0, 2, 1);
}

fn makeParentCoalesced(words: []const usize) abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetView {
    return parent_plan.viewFromBits(words, 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0xE5E5, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xE5E5, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xE5E5, 1, 0, 1, 0, 0, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_COALESCE_COOKIE, 1, 0, 3, 0, 1, 0, 2, 1, 1, 0, 1, 0, 1, 0, 3, 0, 0, 0);
}

fn makeParentDropped(words: []const usize) abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetView {
    return parent_plan.viewFromBits(words, 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0xDDDD, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xDDDD, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xD4D4, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0);
}

fn makeParentSkipped(words: []const usize) abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetView {
    return parent_plan.viewFromBits(words, 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, abi.CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xF6F6, abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE, 3, 4, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xF6F6, 0, 0, 1, 1, 0, 0, 1, 1, 2, 0, 1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 2, 1, 2, 1);
}

fn makeDeliveryParent(
    parent_bits: abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetView,
    primary_guard: u32,
    deferred_guard: u32,
    primary_window: u32,
    deferred_window: u32,
    window_floor: u32,
    policy_flags: u32,
    primary_budget: u32,
    deferred_budget: u32,
    budget_window: u32,
    budget_window_floor: u32,
) abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowView {
    const guard = guard_plan.viewFromParent(parent_bits, primary_guard, deferred_guard);
    const window = guard_window_plan.viewFromParent(guard, primary_window, deferred_window, window_floor);
    const policy = policy_plan.viewFromParent(window, policy_flags);
    const budget = budget_plan.viewFromParent(policy, primary_budget, deferred_budget);
    return budget_window_plan.viewFromParent(budget, budget_window, budget_window_floor);
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [32768]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout_writer.interface;

    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const acked_parent = makeDeliveryParent(makeParentAcked(words[0..]), 1, 0, 2, 1, 0, 0, 1, 1, 2, 0);
    const fallback_deferred_parent = makeDeliveryParent(makeParentAcked(words[0..]), 1, 0, 2, 1, 0, 0, 1, 1, 2, 0);
    const policy_deferred_parent = makeDeliveryParent(makeParentAcked(words[0..]), 1, 0, 2, 1, 0, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_FORCE_DEFERRED, 1, 1, 2, 0);
    const coalesced_parent = makeDeliveryParent(makeParentCoalesced(words[0..]), 1, 0, 2, 1, 0, 0, 1, 0, 2, 0);
    const held_parent = makeDeliveryParent(makeParentAcked(words[0..]), 1, 0, 1, 1, 1, 0, 1, 1, 2, 0);
    const suppressed_held_parent = makeDeliveryParent(makeParentAcked(words[0..]), 1, 0, 1, 1, 1, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_SUPPRESS_HELD, 1, 1, 2, 0);
    const dropped_parent = makeDeliveryParent(makeParentDropped(words[0..]), 0, 0, 0, 0, 0, 0, 0, 0, 2, 0);
    const skipped_parent = makeDeliveryParent(makeParentSkipped(exhausted_words[0..]), 1, 1, 2, 2, 1, 0, 1, 1, 2, 0);

    const empty_view = std.mem.zeroInit(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryView, .{});

    try writer.writeAll("{\"constants\":{"
        ++ "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_flag_budget_applied\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_FLAG_BUDGET_APPLIED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_flag_primary_delivery_budget_used\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_FLAG_PRIMARY_DELIVERY_BUDGET_USED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_flag_deferred_delivery_budget_used\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_FLAG_DEFERRED_DELIVERY_BUDGET_USED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_flag_primary_delivery_budget_exhausted\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_FLAG_PRIMARY_DELIVERY_BUDGET_EXHAUSTED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_flag_deferred_delivery_budget_exhausted\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_FLAG_DEFERRED_DELIVERY_BUDGET_EXHAUSTED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_status_none\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_NONE});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_status_acked\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_ACKED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_status_deferred\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_DEFERRED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_status_suppressed\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_SUPPRESSED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_status_coalesced\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_COALESCED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_status_dropped\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_DROPPED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_status_skipped\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_SKIPPED});
    try writer.writeAll(",\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_status_held\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_HELD});
    try writer.writeAll("}");

    const cases = [_]struct {
        name: []const u8,
        view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryView,
    }{
        .{ .name = "acked", .view = delivery_plan.viewFromParent(acked_parent, 1, 0) },
        .{ .name = "fallback_deferred", .view = delivery_plan.viewFromParent(fallback_deferred_parent, 0, 1) },
        .{ .name = "policy_deferred", .view = delivery_plan.viewFromParent(policy_deferred_parent, 1, 1) },
        .{ .name = "coalesced", .view = delivery_plan.viewFromParent(coalesced_parent, 1, 0) },
        .{ .name = "held", .view = delivery_plan.viewFromParent(held_parent, 1, 1) },
        .{ .name = "suppressed_held", .view = delivery_plan.viewFromParent(suppressed_held_parent, 1, 1) },
        .{ .name = "dropped", .view = delivery_plan.viewFromParent(dropped_parent, 0, 0) },
        .{ .name = "skipped", .view = delivery_plan.viewFromParent(skipped_parent, 1, 1) },
    };

    for (cases) |case| {
        try writer.writeAll(",\"");
        try writer.writeAll(case.name);
        try writer.writeAll("\":{\"summary\":");
        try writeSummary(writer, delivery_plan.summarize(case.view));
        try writer.writeAll("}");
    }

    try writer.writeAll(",\"empty\":{\"is_valid\":");
    try writer.writeAll(if (delivery_plan.isValid(empty_view)) "true" else "false");
    try writer.writeAll(",\"summary\":");
    try writeSummary(writer, delivery_plan.summarize(empty_view));
    try writer.writeAll("}}\n");
    try stdout_writer.interface.flush();
}
