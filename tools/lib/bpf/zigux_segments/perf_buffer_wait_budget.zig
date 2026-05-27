const std = @import("std");
const perf_buffer_poll = @import("perf_buffer_poll");

pub const WaitBudgetSummary = struct {
    timeout_ms: i32,
    wait_class: perf_buffer_poll.WaitClass,
    bounded_timeout_ms: ?u32,
    bounded_timeout_ns: ?u64,
};

pub fn summarizeWaitBudget(timeout_ms: i32) perf_buffer_poll.PollError!WaitBudgetSummary {
    const wait_class = try perf_buffer_poll.classifyWaitClass(timeout_ms);
    const bounded_timeout_ms: ?u32 = switch (wait_class) {
        .bounded => @intCast(timeout_ms),
        .nonblocking, .indefinite => null,
    };

    return .{
        .timeout_ms = timeout_ms,
        .wait_class = wait_class,
        .bounded_timeout_ms = bounded_timeout_ms,
        .bounded_timeout_ns = if (bounded_timeout_ms) |budget_ms|
            @as(u64, budget_ms) * std.time.ns_per_ms
        else
            null,
    };
}

pub fn summarizeWaitBudgetFromPollSummary(summary: perf_buffer_poll.PollSummary) WaitBudgetSummary {
    return .{
        .timeout_ms = switch (summary.wait_class) {
            .nonblocking => 0,
            .indefinite => -1,
            .bounded => 1,
        },
        .wait_class = summary.wait_class,
        .bounded_timeout_ms = switch (summary.wait_class) {
            .bounded => 1,
            .nonblocking, .indefinite => null,
        },
        .bounded_timeout_ns = switch (summary.wait_class) {
            .bounded => std.time.ns_per_ms,
            .nonblocking, .indefinite => null,
        },
    };
}

test "phase8 perf-buffer wait budget keeps nonblocking waits budgetless" {
    const summary = try summarizeWaitBudget(0);

    try std.testing.expectEqual(perf_buffer_poll.WaitClass.nonblocking, summary.wait_class);
    try std.testing.expectEqual(@as(?u32, null), summary.bounded_timeout_ms);
    try std.testing.expectEqual(@as(?u64, null), summary.bounded_timeout_ns);
}

test "phase8 perf-buffer wait budget keeps indefinite waits budgetless" {
    const summary = try summarizeWaitBudget(-1);

    try std.testing.expectEqual(perf_buffer_poll.WaitClass.indefinite, summary.wait_class);
    try std.testing.expectEqual(@as(?u32, null), summary.bounded_timeout_ms);
    try std.testing.expectEqual(@as(?u64, null), summary.bounded_timeout_ns);
}

test "phase8 perf-buffer wait budget normalizes bounded waits into ms and ns budgets" {
    const summary = try summarizeWaitBudget(37);

    try std.testing.expectEqual(perf_buffer_poll.WaitClass.bounded, summary.wait_class);
    try std.testing.expectEqual(@as(?u32, 37), summary.bounded_timeout_ms);
    try std.testing.expectEqual(@as(?u64, 37 * std.time.ns_per_ms), summary.bounded_timeout_ns);
}

test "phase8 perf-buffer wait budget preserves large bounded waits without overflow" {
    const summary = try summarizeWaitBudget(std.math.maxInt(i32));

    try std.testing.expectEqual(perf_buffer_poll.WaitClass.bounded, summary.wait_class);
    try std.testing.expectEqual(@as(?u32, std.math.maxInt(i32)), summary.bounded_timeout_ms);
    try std.testing.expectEqual(
        @as(?u64, @as(u64, std.math.maxInt(i32)) * std.time.ns_per_ms),
        summary.bounded_timeout_ns,
    );
}

test "phase8 perf-buffer wait budget rejects invalid negative waits" {
    try std.testing.expectError(
        perf_buffer_poll.PollError.InvalidTimeout,
        summarizeWaitBudget(-2),
    );
}
