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

pub const CycleWitness = struct {
    slow_index: usize,
    fast_index: usize,
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

    fn lastUnchecked(self: HListView) ?*const HListNode {
        var tail: ?*const HListNode = null;
        var it = self.iterator();
        while (it.next()) |node| {
            tail = node;
        }
        return tail;
    }

    pub fn last(self: HListView) ?*const HListNode {
        if (self.hasCycle()) return null;
        return self.lastUnchecked();
    }

    pub fn iterator(self: HListView) Iterator {
        return .{ .current = self.first() };
    }

    pub fn len(self: HListView) usize {
        if (self.hasCycle()) return 0;

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

    pub fn hasConsistentPrevLinks(self: HListView) bool {
        return self.firstBrokenPrevLink() == null;
    }

    fn firstCycleEntry(self: HListView) ?*const HListNode {
        var slow = self.first();
        var fast = self.first();

        while (fast) |fast_node| {
            const fast_mid = nodeFromRaw(fast_node.next) orelse return null;
            const fast_end = nodeFromRaw(fast_mid.next) orelse return null;

            slow = if (slow) |slow_node| nodeFromRaw(slow_node.next) else null;
            const slow_node = slow orelse return null;

            fast = fast_end;
            if (slow_node == fast_end) {
                var entry = self.first() orelse return null;
                var cycle_cursor = slow_node;
                while (entry != cycle_cursor) {
                    entry = nodeFromRaw(entry.next) orelse return null;
                    cycle_cursor = nodeFromRaw(cycle_cursor.next) orelse return null;
                }
                return entry;
            }
        }

        return null;
    }

    pub fn firstBrokenPrevLink(self: HListView) ?PrevLinkBreak {
        const cycle_entry = self.firstCycleEntry();
        var revisited_cycle_entry = false;
        var expected_pprev = @intFromPtr(&self.head.first);
        var current_index: usize = 0;
        var cursor = self.first();

        while (cursor) |node| {
            if (cycle_entry) |entry| {
                if (node == entry) {
                    if (revisited_cycle_entry) {
                        return .{
                            .current_index = current_index,
                            .expected_pprev = expected_pprev,
                            .actual_pprev = node.pprev,
                        };
                    }
                    revisited_cycle_entry = true;
                }
            }

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

    pub fn firstCycleWitness(self: HListView) ?CycleWitness {
        var slow = self.first();
        var fast = self.first();
        var slow_index: usize = 0;
        var fast_index: usize = 0;

        while (fast) |fast_node| {
            fast = nodeFromRaw(fast_node.next);
            fast_index += 1;
            const fast_mid = fast orelse return null;

            fast = nodeFromRaw(fast_mid.next);
            fast_index += 1;
            slow = if (slow) |slow_node| nodeFromRaw(slow_node.next) else null;
            slow_index += 1;

            if (slow != null and slow == fast) {
                return .{
                    .slow_index = slow_index,
                    .fast_index = fast_index,
                };
            }
        }

        return null;
    }

    pub fn hasCycle(self: HListView) bool {
        return self.firstCycleWitness() != null;
    }

    pub fn tailNextIsNull(self: HListView) bool {
        if (self.hasCycle()) return false;
        return if (self.lastUnchecked()) |node| node.next == 0 else true;
    }
};

test "hlist view treats an empty head as empty" {
    const head = HListHead{ .first = 0 };
    const view = HListView.init(&head);

    try std.testing.expect(view.isEmpty());
    try std.testing.expectEqual(@as(usize, 0), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, null), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, null), view.last());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try std.testing.expect(view.firstCycleWitness() == null);
    try std.testing.expect(!view.hasCycle());
    try std.testing.expect(view.tailNextIsNull());
}

test "hlist view walks a singly linked hlist chain in order" {
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
    try std.testing.expectEqual(@as(?*const HListNode, &first), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, &second), view.last());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.firstCycleWitness() == null);
    try std.testing.expect(!view.hasCycle());

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const HListNode, &first), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &second), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, null), it.next());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
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

    const view = HListView.init(&head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &first), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, &second), view.last());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.firstCycleWitness() == null);
    try std.testing.expect(!view.hasCycle());
    try std.testing.expect(!view.hasConsistentPrevLinks());

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);
    try std.testing.expect(view.tailNextIsNull());
}

test "hlist view last returns the tail across a longer chain" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var second = HListNode{ .next = 0, .pprev = 0 };
    var third = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&third);
    second.pprev = @intFromPtr(&first.next);
    third.next = 0;
    third.pprev = @intFromPtr(&second.next);

    const view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &third), view.last());
    try std.testing.expect(view.firstCycleWitness() == null);
    try std.testing.expect(!view.hasCycle());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "hlist view reports a broken head prev-link witness without losing tail access" {
    var head = HListHead{ .first = 0 };
    var node = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&node);
    node.next = 0;
    node.pprev = @intFromPtr(&node.next);

    const view = HListView.init(&head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 1), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &node), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, &node), view.last());
    try std.testing.expect(!view.firstPprevMatchesHead());
    try std.testing.expect(view.firstCycleWitness() == null);
    try std.testing.expect(!view.hasCycle());
    try std.testing.expect(!view.hasConsistentPrevLinks());

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&node.next)), breakage.actual_pprev);
    try std.testing.expect(view.tailNextIsNull());
}

test "hlist view reports a cycle witness and fails tail checks closed" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var second = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&first);
    second.pprev = @intFromPtr(&first.next);

    const view = HListView.init(&head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 0), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &first), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, null), view.last());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(!view.tailNextIsNull());
    try std.testing.expect(view.hasCycle());

    const witness = view.firstCycleWitness().?;
    try std.testing.expectEqual(@as(usize, 2), witness.slow_index);
    try std.testing.expectEqual(@as(usize, 4), witness.fast_index);

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&second.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
}

test "hlist view handles a one-node hlist without losing tail access" {
    var head = HListHead{ .first = 0 };
    var node = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&node);
    node.next = 0;
    node.pprev = @intFromPtr(&head.first);

    const view = HListView.init(&head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 1), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &node), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, &node), view.last());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.firstCycleWitness() == null);
    try std.testing.expect(!view.hasCycle());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "hlist view fails closed for a self-looped first node" {
    var head = HListHead{ .first = 0 };
    var node = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&node);
    node.next = @intFromPtr(&node);
    node.pprev = @intFromPtr(&head.first);

    const view = HListView.init(&head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 0), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &node), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, null), view.last());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(!view.tailNextIsNull());
    try std.testing.expect(view.hasCycle());

    const witness = view.firstCycleWitness().?;
    try std.testing.expectEqual(@as(usize, 1), witness.slow_index);
    try std.testing.expectEqual(@as(usize, 2), witness.fast_index);

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&node.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
}

test "hlist view first prev-link witness fails closed on a consistent malformed cycle" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var second = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&first);
    second.pprev = @intFromPtr(&first.next);

    const view = HListView.init(&head);
    try std.testing.expect(view.hasCycle());

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&second.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
}

test "hlist view first prev-link witness fails closed on a non-head cycle entry" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var second = HListNode{ .next = 0, .pprev = 0 };
    var third = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&third);
    second.pprev = @intFromPtr(&first.next);
    third.next = @intFromPtr(&second);
    third.pprev = @intFromPtr(&second.next);

    const view = HListView.init(&head);
    try std.testing.expect(view.hasCycle());
    try std.testing.expectEqual(@as(usize, 0), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, null), view.last());
    try std.testing.expect(!view.tailNextIsNull());

    const witness = view.firstCycleWitness().?;
    try std.testing.expectEqual(@as(usize, 2), witness.slow_index);
    try std.testing.expectEqual(@as(usize, 4), witness.fast_index);

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 3), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&third.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
}
