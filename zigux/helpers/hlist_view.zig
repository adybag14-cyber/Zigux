const std = @import("std");

fn nodeFromRaw(raw: usize) ?*const HListNode {
    if (raw == 0) return null;
    const node: *const HListNode = @ptrFromInt(raw);
    return node;
}

pub const HListHead = extern struct {
    first: usize,
};

pub const HListNode = extern struct {
    next: usize,
    pprev: usize,
};

pub const PrevLinkBreak = struct {
    current_index: usize,
    expected_pprev: usize,
    actual_pprev: usize,
};

pub const Iterator = struct {
    current: ?*const HListNode = null,

    pub fn next(self: *Iterator) ?*const HListNode {
        const node = self.current orelse return null;
        self.current = nodeFromRaw(node.next);
        return node;
    }
};

pub const HListView = struct {
    head: *const HListHead,

    pub fn init(head: *const HListHead) HListView {
        return .{ .head = head };
    }

    pub fn isEmpty(self: HListView) bool {
        return self.head.first == 0;
    }

    pub fn first(self: HListView) ?*const HListNode {
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

    pub fn lenBounded(self: HListView, max_nodes: usize) ?usize {
        var count: usize = 0;
        var it = self.iterator();
        while (it.next()) |_| {
            if (count == max_nodes) return null;
            count += 1;
        }
        return count;
    }

    pub fn firstPprevMatchesHead(self: HListView) bool {
        const first_node = self.first() orelse return true;
        return first_node.pprev == @intFromPtr(&self.head.first);
    }

    pub fn hasConsistentPrevLinks(self: HListView) bool {
        return self.firstBrokenPrevLink() == null;
    }

    pub fn firstBrokenPrevLink(self: HListView) ?PrevLinkBreak {
        var expected_pprev = @intFromPtr(&self.head.first);
        var current_index: usize = 0;
        var cursor = self.first();

        while (cursor) |node| {
            if (node.pprev != expected_pprev) {
                return .{
                    .current_index = current_index,
                    .expected_pprev = expected_pprev,
                    .actual_pprev = node.pprev,
                };
            }

            expected_pprev = @intFromPtr(&node.next);
            current_index += 1;
            cursor = nodeFromRaw(node.next);
        }

        return null;
    }

    pub fn tailNextIsNull(self: HListView) bool {
        var tail: ?*const HListNode = null;
        var it = self.iterator();
        while (it.next()) |node| {
            tail = node;
        }
        return if (tail) |node| node.next == 0 else true;
    }
};

test "hlist view treats an empty head as empty" {
    const head = HListHead{ .first = 0 };
    const view = HListView.init(&head);

    try std.testing.expect(view.isEmpty());
    try std.testing.expectEqual(@as(usize, 0), view.len());
    try std.testing.expectEqual(@as(?usize, 0), view.lenBounded(0));
    try std.testing.expectEqual(@as(?*const HListNode, null), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try std.testing.expect(view.tailNextIsNull());
}

test "hlist view walks a bounded chain in order" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var second = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = 0;
    second.pprev = @intFromPtr(&first.next);

    const view = HListView.init(&head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?usize, 2), view.lenBounded(2));
    try std.testing.expectEqual(@as(?usize, null), view.lenBounded(1));
    try std.testing.expectEqual(@as(?*const HListNode, &first), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const HListNode, &first), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &second), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, null), it.next());
}

test "hlist view reports the first broken prev-link witness" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var second = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = 0;
    second.pprev = @intFromPtr(&head.first);

    const breakage = HListView.init(&head).firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);
    try std.testing.expect(!HListView.init(&head).hasConsistentPrevLinks());
}

test "hlist view bounded length fails closed before a malformed cycle can spin" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var second = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&first);
    second.pprev = @intFromPtr(&first.next);

    const view = HListView.init(&head);
    try std.testing.expectEqual(@as(?usize, null), view.lenBounded(0));
    try std.testing.expectEqual(@as(?usize, null), view.lenBounded(2));
    try std.testing.expectEqual(@as(?usize, null), view.lenBounded(4));
}
