const std = @import("std");

pub const NOTIFIER_CHAIN_FLAG_EMPTY: u32 = 1;
pub const NOTIFIER_CHAIN_FLAG_TERMINATED: u32 = 2;
pub const NOTIFIER_CHAIN_FLAG_TRUNCATED: u32 = 4;
pub const NOTIFIER_CHAIN_FLAG_SELF_LOOP: u32 = 8;
pub const NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING: u32 = 16;

pub const NotifierBlockRef = extern struct {
    notifier_call: ?*const anyopaque,
    next: ?*const NotifierBlockRef,
    priority: i32,
};

pub const RawNotifierHeadRef = extern struct {
    head: ?*const NotifierBlockRef,
};

pub const NotifierChainView = extern struct {
    head: ?*const RawNotifierHeadRef,
    max_nodes: u32,
    reserved: u32 = 0,
};

pub const NotifierChainSummary = extern struct {
    length: u32,
    highest_priority: i32,
    lowest_priority: i32,
    flags: u32,
};

pub const SummarizeError = error{InvalidView};

pub fn chainViewValid(view: *const NotifierChainView) bool {
    return view.head != null and view.max_nodes != 0 and view.reserved == 0;
}

pub fn trySummarizeChain(view: *const NotifierChainView) SummarizeError!NotifierChainSummary {
    if (!chainViewValid(view)) {
        return error.InvalidView;
    }
    return summarizeChain(view);
}

pub fn summarizeChain(view: *const NotifierChainView) NotifierChainSummary {
    var summary = NotifierChainSummary{
        .length = 0,
        .highest_priority = 0,
        .lowest_priority = 0,
        .flags = 0,
    };

    if (!chainViewValid(view)) {
        return summary;
    }

    var current = view.head.?.head;
    if (current == null) {
        summary.flags = NOTIFIER_CHAIN_FLAG_EMPTY | NOTIFIER_CHAIN_FLAG_TERMINATED;
        return summary;
    }

    var previous_priority: i32 = 0;
    var have_previous = false;
    var priorities_nonincreasing = true;

    while (current) |node| {
        if (summary.length == view.max_nodes) {
            summary.flags |= NOTIFIER_CHAIN_FLAG_TRUNCATED;
            break;
        }

        if (summary.length == 0) {
            summary.highest_priority = node.priority;
            summary.lowest_priority = node.priority;
        } else {
            summary.highest_priority = @max(summary.highest_priority, node.priority);
            summary.lowest_priority = @min(summary.lowest_priority, node.priority);
        }

        if (have_previous and node.priority > previous_priority) {
            priorities_nonincreasing = false;
        }

        previous_priority = node.priority;
        have_previous = true;
        summary.length += 1;

        if (node.next == node) {
            summary.flags |= NOTIFIER_CHAIN_FLAG_SELF_LOOP;
            break;
        }

        current = node.next;
    }

    if (current == null) {
        summary.flags |= NOTIFIER_CHAIN_FLAG_TERMINATED;
    }
    if (priorities_nonincreasing) {
        summary.flags |= NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING;
    }

    return summary;
}

test "notifier summary reports an empty terminated chain" {
    const head = RawNotifierHeadRef{ .head = null };
    const view = NotifierChainView{
        .head = &head,
        .max_nodes = 4,
    };

    const summary = summarizeChain(&view);
    try std.testing.expectEqual(@as(u32, 0), summary.length);
    try std.testing.expectEqual(
        @as(u32, NOTIFIER_CHAIN_FLAG_EMPTY | NOTIFIER_CHAIN_FLAG_TERMINATED),
        summary.flags,
    );
}

test "trySummarizeChain rejects invalid notifier views explicitly" {
    const dummy_head = RawNotifierHeadRef{ .head = null };
    const invalid_headless = NotifierChainView{
        .head = null,
        .max_nodes = 4,
    };
    const invalid_zero_nodes = NotifierChainView{
        .head = &dummy_head,
        .max_nodes = 0,
    };
    const invalid_reserved = NotifierChainView{
        .head = &dummy_head,
        .max_nodes = 4,
        .reserved = 1,
    };

    try std.testing.expectError(error.InvalidView, trySummarizeChain(&invalid_headless));
    try std.testing.expectError(error.InvalidView, trySummarizeChain(&invalid_zero_nodes));
    try std.testing.expectError(error.InvalidView, trySummarizeChain(&invalid_reserved));
}

test "trySummarizeChain matches summarizeChain for a valid notifier view" {
    const tail = NotifierBlockRef{
        .notifier_call = null,
        .next = null,
        .priority = 5,
    };
    const head_node = NotifierBlockRef{
        .notifier_call = null,
        .next = &tail,
        .priority = 9,
    };
    const head = RawNotifierHeadRef{ .head = &head_node };
    const view = NotifierChainView{
        .head = &head,
        .max_nodes = 4,
    };

    const summary = summarizeChain(&view);
    const explicit_summary = try trySummarizeChain(&view);
    try std.testing.expectEqual(summary.length, explicit_summary.length);
    try std.testing.expectEqual(summary.highest_priority, explicit_summary.highest_priority);
    try std.testing.expectEqual(summary.lowest_priority, explicit_summary.lowest_priority);
    try std.testing.expectEqual(summary.flags, explicit_summary.flags);
}

test "notifier summary keeps terminated nonincreasing priorities reviewable" {
    const tail = NotifierBlockRef{
        .notifier_call = null,
        .next = null,
        .priority = 5,
    };
    const head_node = NotifierBlockRef{
        .notifier_call = null,
        .next = &tail,
        .priority = 9,
    };
    const head = RawNotifierHeadRef{ .head = &head_node };
    const view = NotifierChainView{
        .head = &head,
        .max_nodes = 4,
    };

    const summary = summarizeChain(&view);
    try std.testing.expectEqual(@as(u32, 2), summary.length);
    try std.testing.expectEqual(@as(i32, 9), summary.highest_priority);
    try std.testing.expectEqual(@as(i32, 5), summary.lowest_priority);
    try std.testing.expect((summary.flags & NOTIFIER_CHAIN_FLAG_TERMINATED) != 0);
    try std.testing.expect((summary.flags & NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING) != 0);
}

test "notifier summary flags self loops and truncation without inventing termination" {
    var loop = NotifierBlockRef{
        .notifier_call = null,
        .next = undefined,
        .priority = 7,
    };
    loop.next = &loop;
    const loop_head = RawNotifierHeadRef{ .head = &loop };
    const loop_view = NotifierChainView{
        .head = &loop_head,
        .max_nodes = 4,
    };

    const loop_summary = summarizeChain(&loop_view);
    try std.testing.expectEqual(@as(u32, 1), loop_summary.length);
    try std.testing.expect((loop_summary.flags & NOTIFIER_CHAIN_FLAG_SELF_LOOP) != 0);
    try std.testing.expect((loop_summary.flags & NOTIFIER_CHAIN_FLAG_TERMINATED) == 0);

    const tail = NotifierBlockRef{
        .notifier_call = null,
        .next = null,
        .priority = 11,
    };
    const head_node = NotifierBlockRef{
        .notifier_call = null,
        .next = &tail,
        .priority = 9,
    };
    const capped_head = RawNotifierHeadRef{ .head = &head_node };
    const capped_view = NotifierChainView{
        .head = &capped_head,
        .max_nodes = 1,
    };

    const capped_summary = summarizeChain(&capped_view);
    try std.testing.expectEqual(@as(u32, 1), capped_summary.length);
    try std.testing.expect((capped_summary.flags & NOTIFIER_CHAIN_FLAG_TRUNCATED) != 0);
    try std.testing.expect((capped_summary.flags & NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING) != 0);
}

test "notifier summary omits the priority-order flag when the chain rises" {
    const tail = NotifierBlockRef{
        .notifier_call = null,
        .next = null,
        .priority = 12,
    };
    const head_node = NotifierBlockRef{
        .notifier_call = null,
        .next = &tail,
        .priority = 8,
    };
    const head = RawNotifierHeadRef{ .head = &head_node };
    const view = NotifierChainView{
        .head = &head,
        .max_nodes = 4,
    };

    const summary = summarizeChain(&view);
    try std.testing.expect((summary.flags & NOTIFIER_CHAIN_FLAG_TERMINATED) != 0);
    try std.testing.expect((summary.flags & NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING) == 0);
}
