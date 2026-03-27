const std = @import("std");
const abi = @import("abi_bindings");
const narrow = @import("narrow_unsafe");

pub fn viewFromHead(head: *const abi.ListHeadRef, max_nodes: u32) abi.ListView {
    return .{
        .head_addr = narrow.addressOf(head),
        .max_nodes = max_nodes,
        .reserved = 0,
    };
}

pub fn isValid(view: abi.ListView) bool {
    if (view.reserved != 0) return false;
    return view.head_addr != 0 and view.max_nodes != 0;
}

fn headPtr(view: abi.ListView) *const abi.ListHeadRef {
    std.debug.assert(isValid(view));
    return narrow.constPointerAt(abi.ListHeadRef, view.head_addr);
}

fn nodePtr(addr: usize) *const abi.ListHeadRef {
    return narrow.constPointerAt(abi.ListHeadRef, addr);
}

pub fn isEmpty(view: abi.ListView) bool {
    if (!isValid(view)) return false;
    const head = headPtr(view);
    return head.next_addr == view.head_addr and head.prev_addr == view.head_addr;
}

pub fn isSingular(view: abi.ListView) bool {
    if (!isValid(view) or isEmpty(view)) return false;
    const head = headPtr(view);
    if (head.next_addr != head.prev_addr) return false;
    const node = nodePtr(head.next_addr);
    return node.next_addr == view.head_addr and node.prev_addr == view.head_addr;
}

pub fn length(view: abi.ListView) u32 {
    if (!isValid(view)) return 0;

    const head = headPtr(view);
    var current = head.next_addr;
    var count: u32 = 0;
    while (count < view.max_nodes and current != 0 and current != view.head_addr) : (count += 1) {
        current = nodePtr(current).next_addr;
    }
    return count;
}

pub fn summarize(view: abi.ListView) abi.ListSummary {
    if (!isValid(view)) return .{ .length = 0, .flags = 0 };
    if (isEmpty(view)) {
        return .{ .length = 0, .flags = abi.LIST_FLAG_EMPTY | abi.LIST_FLAG_CIRCULAR };
    }

    const head = headPtr(view);
    var current = head.next_addr;
    var count: u32 = 0;
    var flags: u32 = 0;
    while (count < view.max_nodes and current != 0 and current != view.head_addr) : (count += 1) {
        current = nodePtr(current).next_addr;
    }

    if (isSingular(view)) flags |= abi.LIST_FLAG_SINGULAR;
    if (current == view.head_addr) {
        flags |= abi.LIST_FLAG_CIRCULAR;
    } else {
        flags |= abi.LIST_FLAG_TRUNCATED;
    }
    return .{ .length = count, .flags = flags };
}

test "phase3 list view helpers stay bounded and predictable" {
    var head = abi.ListHeadRef{ .next_addr = undefined, .prev_addr = undefined };
    var node_a = abi.ListHeadRef{ .next_addr = undefined, .prev_addr = undefined };
    var node_b = abi.ListHeadRef{ .next_addr = undefined, .prev_addr = undefined };
    const head_addr = narrow.addressOf(&head);
    const node_a_addr = narrow.addressOf(&node_a);
    const node_b_addr = narrow.addressOf(&node_b);

    head.next_addr = node_a_addr;
    head.prev_addr = node_b_addr;
    node_a.next_addr = node_b_addr;
    node_a.prev_addr = head_addr;
    node_b.next_addr = head_addr;
    node_b.prev_addr = node_a_addr;

    const view = viewFromHead(&head, 8);
    const summary = summarize(view);
    try std.testing.expect(isValid(view));
    try std.testing.expect(!isEmpty(view));
    try std.testing.expect(!isSingular(view));
    try std.testing.expectEqual(@as(u32, 2), length(view));
    try std.testing.expectEqual(@as(u32, 2), summary.length);
    try std.testing.expectEqual(@as(u32, abi.LIST_FLAG_CIRCULAR), summary.flags);
}

test "phase3 list view empty sentinel stays explicit" {
    var head = abi.ListHeadRef{ .next_addr = undefined, .prev_addr = undefined };
    const head_addr = narrow.addressOf(&head);
    head.next_addr = head_addr;
    head.prev_addr = head_addr;

    const view = viewFromHead(&head, 4);
    const summary = summarize(view);
    try std.testing.expect(isValid(view));
    try std.testing.expect(isEmpty(view));
    try std.testing.expectEqual(@as(u32, 0), summary.length);
    try std.testing.expectEqual(@as(u32, abi.LIST_FLAG_EMPTY | abi.LIST_FLAG_CIRCULAR), summary.flags);
}