const std = @import("std");
const abi = @import("list_hlist_binding");

fn nodeFromRaw(raw: usize) ?*const abi.HListNode {
    if (raw == 0) return null;
    const ptr: *const abi.HListNode = @ptrFromInt(raw);
    return ptr;
}

pub const Iterator = struct {
    current: ?*const abi.HListNode,

    pub fn next(self: *Iterator) ?*const abi.HListNode {
        const node = self.current orelse return null;
        self.current = nodeFromRaw(node.next);
        return node;
    }
};

pub const HListView = struct {
    head: *const abi.HListHead,

    pub fn init(head: *const abi.HListHead) HListView {
        return .{ .head = head };
    }

    pub fn isEmpty(self: HListView) bool {
        return self.head.first == 0;
    }

    pub fn first(self: HListView) ?*const abi.HListNode {
        return nodeFromRaw(self.head.first);
    }

    pub fn iterator(self: HListView) Iterator {
        return .{ .current = self.first() };
    }

    pub fn len(self: HListView) usize {
        var count: usize = 0;
        var it = self.iterator();
        while (it.next()) |_| {
            count += 1;
        }
        return count;
    }

    pub fn firstPprevMatchesHead(self: HListView) bool {
        const first_node = self.first() orelse return true;
        return first_node.pprev == @intFromPtr(&self.head.first);
    }

    pub fn linksBackToPrevious(self: HListView) bool {
        var expected_pprev = @intFromPtr(&self.head.first);
        var it = self.iterator();
        while (it.next()) |node| {
            if (node.pprev != expected_pprev) return false;
            expected_pprev = @intFromPtr(&node.next);
        }
        return true;
    }

    pub fn tailNextIsNull(self: HListView) bool {
        var tail: ?*const abi.HListNode = null;
        var it = self.iterator();
        while (it.next()) |node| {
            tail = node;
        }
        return if (tail) |node| node.next == 0 else true;
    }
};

test "hlist view walks a small bounded chain" {
    var head = abi.HListHead{ .first = 0 };
    var first = abi.HListNode{ .next = 0, .pprev = 0 };
    var second = abi.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = 0;
    second.pprev = @intFromPtr(&first.next);

    const view = HListView.init(&head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.linksBackToPrevious());
    try std.testing.expect(view.tailNextIsNull());
    try std.testing.expectEqual(@as(*const abi.HListNode, &first), view.first().?);

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const abi.HListNode, &first), it.next());
    try std.testing.expectEqual(@as(?*const abi.HListNode, &second), it.next());
    try std.testing.expectEqual(@as(?*const abi.HListNode, null), it.next());
}

test "hlist view keeps empty sentinel behavior explicit" {
    const head = abi.HListHead{ .first = 0 };
    const view = HListView.init(&head);

    try std.testing.expect(view.isEmpty());
    try std.testing.expectEqual(@as(usize, 0), view.len());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.linksBackToPrevious());
    try std.testing.expect(view.tailNextIsNull());
    try std.testing.expect(view.first() == null);
}
