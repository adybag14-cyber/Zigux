const std = @import("std");
const abi = @import("notifier_abi_bindings");
const narrow = @import("narrow_unsafe");

pub fn viewFromHead(head: *const abi.RawNotifierHeadRef, max_nodes: u32) abi.NotifierChainView {
    return .{
        .head_addr = narrow.addressOf(head),
        .max_nodes = max_nodes,
        .reserved = 0,
    };
}

pub fn isValid(view: abi.NotifierChainView) bool {
    if (view.reserved != 0) return false;
    return view.head_addr != 0 and view.max_nodes != 0;
}

fn headPtr(view: abi.NotifierChainView) *const abi.RawNotifierHeadRef {
    std.debug.assert(isValid(view));
    return narrow.constPointerAt(abi.RawNotifierHeadRef, .raw_pointer_bridge, view.head_addr) catch unreachable;
}

fn nodePtr(addr: usize) *const abi.NotifierBlockRef {
    return narrow.constPointerAt(abi.NotifierBlockRef, .raw_pointer_bridge, addr) catch unreachable;
}

pub fn isEmpty(view: abi.NotifierChainView) bool {
    if (!isValid(view)) return false;
    return headPtr(view).head_addr == 0;
}

pub fn length(view: abi.NotifierChainView) u32 {
    return summarize(view).length;
}

pub fn hasNonincreasingPriorityOrder(view: abi.NotifierChainView) bool {
    return (summarize(view).flags & abi.NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING) != 0;
}

pub fn summarize(view: abi.NotifierChainView) abi.NotifierChainSummary {
    if (!isValid(view)) {
        return .{ .length = 0, .flags = 0, .highest_priority = 0, .lowest_priority = 0 };
    }
    if (isEmpty(view)) {
        return .{
            .length = 0,
            .flags = abi.NOTIFIER_CHAIN_FLAG_EMPTY | abi.NOTIFIER_CHAIN_FLAG_TERMINATED,
            .highest_priority = 0,
            .lowest_priority = 0,
        };
    }

    var current = headPtr(view).head_addr;
    var count: u32 = 0;
    var flags: u32 = 0;
    var highest_priority: i32 = std.math.minInt(i32);
    var lowest_priority: i32 = std.math.maxInt(i32);
    var previous_priority: ?i32 = null;
    var priority_nonincreasing = true;

    while (count < view.max_nodes and current != 0) : (count += 1) {
        const node = nodePtr(current);
        if (previous_priority) |previous| {
            if (node.priority > previous) priority_nonincreasing = false;
        }
        previous_priority = node.priority;
        if (node.priority > highest_priority) highest_priority = node.priority;
        if (node.priority < lowest_priority) lowest_priority = node.priority;

        const next_addr = node.next_addr;
        if (next_addr == current) {
            flags |= abi.NOTIFIER_CHAIN_FLAG_SELF_LOOP;
            current = next_addr;
            break;
        }
        current = next_addr;
    }

    if (previous_priority != null and priority_nonincreasing) {
        flags |= abi.NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING;
    }
    if ((flags & abi.NOTIFIER_CHAIN_FLAG_SELF_LOOP) != 0) {
        return .{
            .length = count + 1,
            .flags = flags,
            .highest_priority = highest_priority,
            .lowest_priority = lowest_priority,
        };
    }
    if (current == 0) {
        flags |= abi.NOTIFIER_CHAIN_FLAG_TERMINATED;
    } else {
        flags |= abi.NOTIFIER_CHAIN_FLAG_TRUNCATED;
    }
    return .{
        .length = count,
        .flags = flags,
        .highest_priority = highest_priority,
        .lowest_priority = lowest_priority,
    };
}

test "phase13 notifier chain view tracks terminated chains" {
    var head = abi.RawNotifierHeadRef{ .head_addr = 0 };
    var node_a = abi.NotifierBlockRef{ .notifier_call_addr = 0x1111, .next_addr = 0, .priority = 50, .reserved = 0 };
    var node_b = abi.NotifierBlockRef{ .notifier_call_addr = 0x2222, .next_addr = 0, .priority = 10, .reserved = 0 };

    node_a.next_addr = narrow.addressOf(&node_b);
    head.head_addr = narrow.addressOf(&node_a);

    const view = viewFromHead(&head, 8);
    const summary = summarize(view);
    try std.testing.expect(isValid(view));
    try std.testing.expect(!isEmpty(view));
    try std.testing.expectEqual(@as(u32, 2), length(view));
    try std.testing.expectEqual(@as(u32, 2), summary.length);
    try std.testing.expectEqual(@as(u32, abi.NOTIFIER_CHAIN_FLAG_TERMINATED | abi.NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING), summary.flags);
    try std.testing.expect(hasNonincreasingPriorityOrder(view));
    try std.testing.expectEqual(@as(i32, 50), summary.highest_priority);
    try std.testing.expectEqual(@as(i32, 10), summary.lowest_priority);
}

test "phase13 notifier chain view keeps the empty sentinel explicit" {
    var head = abi.RawNotifierHeadRef{ .head_addr = 0 };
    const view = viewFromHead(&head, 4);
    const summary = summarize(view);
    try std.testing.expect(isValid(view));
    try std.testing.expect(isEmpty(view));
    try std.testing.expectEqual(@as(u32, 0), summary.length);
    try std.testing.expectEqual(@as(u32, abi.NOTIFIER_CHAIN_FLAG_EMPTY | abi.NOTIFIER_CHAIN_FLAG_TERMINATED), summary.flags);
    try std.testing.expect(!hasNonincreasingPriorityOrder(view));
}

test "phase13 notifier chain view marks truncation and self loops" {
    var head = abi.RawNotifierHeadRef{ .head_addr = 0 };
    var node_a = abi.NotifierBlockRef{ .notifier_call_addr = 0x1111, .next_addr = 0, .priority = 7, .reserved = 0 };
    var node_b = abi.NotifierBlockRef{ .notifier_call_addr = 0x2222, .next_addr = 0, .priority = 3, .reserved = 0 };
    node_a.next_addr = narrow.addressOf(&node_b);
    head.head_addr = narrow.addressOf(&node_a);

    const truncated_view = viewFromHead(&head, 1);
    const truncated = summarize(truncated_view);
    try std.testing.expectEqual(@as(u32, 1), truncated.length);
    try std.testing.expectEqual(@as(u32, abi.NOTIFIER_CHAIN_FLAG_TRUNCATED | abi.NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING), truncated.flags);
    try std.testing.expect(hasNonincreasingPriorityOrder(truncated_view));

    var loop = abi.NotifierBlockRef{ .notifier_call_addr = 0x3333, .next_addr = 0, .priority = 9, .reserved = 0 };
    loop.next_addr = narrow.addressOf(&loop);
    head.head_addr = narrow.addressOf(&loop);
    const self_loop_view = viewFromHead(&head, 8);
    const self_loop = summarize(self_loop_view);
    try std.testing.expectEqual(@as(u32, 1), self_loop.length);
    try std.testing.expectEqual(@as(u32, abi.NOTIFIER_CHAIN_FLAG_SELF_LOOP | abi.NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING), self_loop.flags);
    try std.testing.expect(hasNonincreasingPriorityOrder(self_loop_view));
    try std.testing.expectEqual(@as(i32, 9), self_loop.highest_priority);
    try std.testing.expectEqual(@as(i32, 9), self_loop.lowest_priority);
}

test "phase13 notifier chain view clears the priority-order flag when priorities rise" {
    var head = abi.RawNotifierHeadRef{ .head_addr = 0 };
    var node_a = abi.NotifierBlockRef{ .notifier_call_addr = 0x1111, .next_addr = 0, .priority = 1, .reserved = 0 };
    var node_b = abi.NotifierBlockRef{ .notifier_call_addr = 0x2222, .next_addr = 0, .priority = 9, .reserved = 0 };

    node_a.next_addr = narrow.addressOf(&node_b);
    head.head_addr = narrow.addressOf(&node_a);

    const view = viewFromHead(&head, 8);
    const summary = summarize(view);
    try std.testing.expectEqual(@as(u32, 2), summary.length);
    try std.testing.expectEqual(@as(u32, abi.NOTIFIER_CHAIN_FLAG_TERMINATED), summary.flags);
    try std.testing.expect(!hasNonincreasingPriorityOrder(view));
    try std.testing.expectEqual(@as(i32, 9), summary.highest_priority);
    try std.testing.expectEqual(@as(i32, 1), summary.lowest_priority);
}
