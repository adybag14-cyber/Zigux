const std = @import("std");
const abi = @import("../bindings/notifier_abi.zig");

pub fn viewFromHead(head: *const abi.RawNotifierHeadRef, max_nodes: u32) abi.NotifierChainView {
    return .{
        .head = head,
        .max_nodes = max_nodes,
    };
}

pub fn isValid(view: abi.NotifierChainView) bool {
    return view.head != null and view.max_nodes > 0;
}

pub fn isEmpty(view: abi.NotifierChainView) bool {
    return summarize(view).flags & abi.NOTIFIER_CHAIN_FLAG_EMPTY != 0;
}

pub fn length(view: abi.NotifierChainView) u32 {
    return summarize(view).length;
}

pub fn hasNonincreasingPriorityOrder(view: abi.NotifierChainView) bool {
    return summarize(view).flags & abi.NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING != 0;
}

pub fn summarize(view: abi.NotifierChainView) abi.NotifierChainSummary {
    if (!isValid(view)) {
        return .{
            .length = 0,
            .highest_priority = 0,
            .lowest_priority = 0,
            .flags = 0,
        };
    }

    const head = view.head.?;
    var cursor = head.head;
    if (cursor == null) {
        return .{
            .length = 0,
            .highest_priority = 0,
            .lowest_priority = 0,
            .flags = abi.NOTIFIER_CHAIN_FLAG_EMPTY | abi.NOTIFIER_CHAIN_FLAG_TERMINATED | abi.NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING,
        };
    }

    var count: u32 = 0;
    var highest: i32 = std.math.minInt(i32);
    var lowest: i32 = std.math.maxInt(i32);
    var flags: u32 = 0;
    var previous_priority: ?i32 = null;
    var saw_node = false;
    var priorities_nonincreasing = true;

    while (cursor != null and count < view.max_nodes) : (count += 1) {
        saw_node = true;
        const node = cursor.?;
        highest = @max(highest, node.priority);
        lowest = @min(lowest, node.priority);

        if (previous_priority) |prev| {
            // Keep the flag only while priorities never rise as the chain advances.
            if (node.priority > prev) priorities_nonincreasing = false;
        }
        previous_priority = node.priority;

        const next = node.next;
        if (next == node) {
            flags |= abi.NOTIFIER_CHAIN_FLAG_SELF_LOOP;
            break;
        }
        if (next == null) {
            flags |= abi.NOTIFIER_CHAIN_FLAG_TERMINATED;
            break;
        }

        cursor = next;
    } else {
        if (cursor != null) flags |= abi.NOTIFIER_CHAIN_FLAG_TRUNCATED;
    }

    if (saw_node and priorities_nonincreasing) {
        flags |= abi.NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING;
    }

    return .{
        .length = count + @intFromBool(flags & abi.NOTIFIER_CHAIN_FLAG_SELF_LOOP != 0 or flags & abi.NOTIFIER_CHAIN_FLAG_TERMINATED != 0),
        .highest_priority = if (saw_node) highest else 0,
        .lowest_priority = if (saw_node) lowest else 0,
        .flags = flags,
    };
}

test "summarize keeps ordered terminated chains marked as nonincreasing priority" {
    const n3 = abi.NotifierBlockRef{ .notifier_call = null, .next = null, .priority = 10 };
    const n2 = abi.NotifierBlockRef{ .notifier_call = null, .next = &n3, .priority = 20 };
    const n1 = abi.NotifierBlockRef{ .notifier_call = null, .next = &n2, .priority = 30 };
    const head = abi.RawNotifierHeadRef{ .head = &n1 };
    const summary = summarize(viewFromHead(&head, 8));
    try std.testing.expectEqual(@as(u32, 3), summary.length);
    try std.testing.expect(summary.flags & abi.NOTIFIER_CHAIN_FLAG_TERMINATED != 0);
    try std.testing.expect(summary.flags & abi.NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING != 0);
    try std.testing.expectEqual(@as(i32, 30), summary.highest_priority);
    try std.testing.expectEqual(@as(i32, 10), summary.lowest_priority);
}

test "summarize marks truncated chains" {
    const n3 = abi.NotifierBlockRef{ .notifier_call = null, .next = null, .priority = 10 };
    const n2 = abi.NotifierBlockRef{ .notifier_call = null, .next = &n3, .priority = 20 };
    const n1 = abi.NotifierBlockRef{ .notifier_call = null, .next = &n2, .priority = 30 };
    const head = abi.RawNotifierHeadRef{ .head = &n1 };
    const summary = summarize(viewFromHead(&head, 2));
    try std.testing.expectEqual(@as(u32, 2), summary.length);
    try std.testing.expect(summary.flags & abi.NOTIFIER_CHAIN_FLAG_TRUNCATED != 0);
}

test "summarize marks self loops while preserving the ordering signal" {
    var node = abi.NotifierBlockRef{ .notifier_call = null, .next = undefined, .priority = 7 };
    node.next = &node;
    const head = abi.RawNotifierHeadRef{ .head = &node };
    const summary = summarize(viewFromHead(&head, 4));
    try std.testing.expectEqual(@as(u32, 1), summary.length);
    try std.testing.expect(summary.flags & abi.NOTIFIER_CHAIN_FLAG_SELF_LOOP != 0);
    try std.testing.expect(summary.flags & abi.NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING != 0);
}

test "summarize clears the priority-order flag when priorities rise" {
    const n3 = abi.NotifierBlockRef{ .notifier_call = null, .next = null, .priority = 30 };
    const n2 = abi.NotifierBlockRef{ .notifier_call = null, .next = &n3, .priority = 10 };
    const n1 = abi.NotifierBlockRef{ .notifier_call = null, .next = &n2, .priority = 20 };
    const head = abi.RawNotifierHeadRef{ .head = &n1 };
    const summary = summarize(viewFromHead(&head, 8));
    try std.testing.expect(summary.flags & abi.NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING == 0);
}
