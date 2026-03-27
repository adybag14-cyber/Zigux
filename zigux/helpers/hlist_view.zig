const std = @import("std");
const abi = @import("abi_bindings");
const narrow = @import("narrow_unsafe");

pub fn viewFromHead(head: *const abi.HListHeadRef, max_nodes: u32) abi.HListView {
    return .{
        .head_addr = narrow.addressOf(head),
        .max_nodes = max_nodes,
        .reserved = 0,
    };
}

pub fn isValid(view: abi.HListView) bool {
    if (view.reserved != 0) return false;
    return view.head_addr != 0 and view.max_nodes != 0;
}

fn headPtr(view: abi.HListView) *const abi.HListHeadRef {
    std.debug.assert(isValid(view));
    return narrow.constPointerAt(abi.HListHeadRef, view.head_addr);
}

fn nodePtr(addr: usize) *const abi.HListNodeRef {
    return narrow.constPointerAt(abi.HListNodeRef, addr);
}

pub fn isEmpty(view: abi.HListView) bool {
    if (!isValid(view)) return false;
    return headPtr(view).first_addr == 0;
}

pub fn isSingular(view: abi.HListView) bool {
    if (!isValid(view) or isEmpty(view)) return false;
    return nodePtr(headPtr(view).first_addr).next_addr == 0;
}

pub fn length(view: abi.HListView) u32 {
    if (!isValid(view)) return 0;

    var current = headPtr(view).first_addr;
    var count: u32 = 0;
    while (count < view.max_nodes and current != 0) : (count += 1) {
        current = nodePtr(current).next_addr;
    }
    return count;
}

pub fn summarize(view: abi.HListView) abi.HListSummary {
    if (!isValid(view)) return .{ .length = 0, .flags = 0 };
    if (isEmpty(view)) {
        return .{ .length = 0, .flags = abi.HLIST_FLAG_EMPTY | abi.HLIST_FLAG_TERMINATED };
    }

    var current = headPtr(view).first_addr;
    var count: u32 = 0;
    var flags: u32 = 0;
    while (count < view.max_nodes and current != 0) : (count += 1) {
        current = nodePtr(current).next_addr;
    }

    if (isSingular(view)) flags |= abi.HLIST_FLAG_SINGULAR;
    if (current == 0) {
        flags |= abi.HLIST_FLAG_TERMINATED;
    } else {
        flags |= abi.HLIST_FLAG_TRUNCATED;
    }
    return .{ .length = count, .flags = flags };
}

test "phase3 hlist view helpers stay bounded and predictable" {
    var head = abi.HListHeadRef{ .first_addr = undefined };
    var node_a = abi.HListNodeRef{ .next_addr = undefined, .pprev_addr = undefined };
    var node_b = abi.HListNodeRef{ .next_addr = undefined, .pprev_addr = undefined };
    const node_a_addr = narrow.addressOf(&node_a);
    const node_b_addr = narrow.addressOf(&node_b);

    head.first_addr = node_a_addr;
    node_a.next_addr = node_b_addr;
    node_a.pprev_addr = narrow.addressOf(&head.first_addr);
    node_b.next_addr = 0;
    node_b.pprev_addr = narrow.addressOf(&node_a.next_addr);

    const view = viewFromHead(&head, 8);
    const summary = summarize(view);
    try std.testing.expect(isValid(view));
    try std.testing.expect(!isEmpty(view));
    try std.testing.expect(!isSingular(view));
    try std.testing.expectEqual(@as(u32, 2), length(view));
    try std.testing.expectEqual(@as(u32, 2), summary.length);
    try std.testing.expectEqual(@as(u32, abi.HLIST_FLAG_TERMINATED), summary.flags);
}

test "phase3 hlist view empty sentinel stays explicit" {
    var head = abi.HListHeadRef{ .first_addr = 0 };
    const view = viewFromHead(&head, 4);
    const summary = summarize(view);
    try std.testing.expect(isValid(view));
    try std.testing.expect(isEmpty(view));
    try std.testing.expectEqual(@as(u32, 0), summary.length);
    try std.testing.expectEqual(@as(u32, abi.HLIST_FLAG_EMPTY | abi.HLIST_FLAG_TERMINATED), summary.flags);
}