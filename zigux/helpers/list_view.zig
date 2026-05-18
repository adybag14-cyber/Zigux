const std = @import("std");

fn ptrFromRaw(raw: usize) ?*const ListHead {
    if (raw == 0) return null;
    const node: *const ListHead = @ptrFromInt(raw);
    return node;
}

pub const ListHead = extern struct {
    next: usize,
    prev: usize,
};

pub const BackLinkBreak = struct {
    current_index: usize,
    expected_prev: usize,
    actual_prev: usize,
};

pub const CycleWitness = struct {
    slow_index: usize,
    fast_index: usize,
};

pub const Iterator = struct {
    head: *const ListHead,
    current: ?*const ListHead = null,
    started: bool = false,

    pub fn next(self: *Iterator) ?*const ListHead {
        const candidate = if (!self.started) blk: {
            self.started = true;
            break :blk ptrFromRaw(self.head.next) orelse return null;
        } else blk: {
            const node = self.current orelse return null;
            break :blk ptrFromRaw(node.next) orelse return null;
        };

        if (candidate == self.head) {
            self.current = null;
            return null;
        }

        self.current = candidate;
        return candidate;
    }
};

pub const ListView = struct {
    head: *const ListHead,

    pub fn init(head: *const ListHead) ListView {
        return .{ .head = head };
    }

    fn nextNode(self: ListView, node: *const ListHead) ?*const ListHead {
        const next = ptrFromRaw(node.next) orelse return null;
        return if (next == self.head) null else next;
    }

    fn lastUnchecked(self: ListView) ?*const ListHead {
        var tail: ?*const ListHead = null;
        var cursor = self.first();
        while (cursor) |node| {
            tail = node;
            cursor = self.nextNode(node);
        }
        return tail;
    }

    pub fn isEmpty(self: ListView) bool {
        const self_ptr = @intFromPtr(self.head);
        return self.head.next == self_ptr and self.head.prev == self_ptr;
    }

    pub fn first(self: ListView) ?*const ListHead {
        const node = ptrFromRaw(self.head.next) orelse return null;
        return if (node == self.head) null else node;
    }

    pub fn last(self: ListView) ?*const ListHead {
        if (self.hasCycle()) return null;
        return self.lastUnchecked();
    }

    pub fn iterator(self: ListView) Iterator {
        return .{ .head = self.head };
    }

    pub fn len(self: ListView) usize {
        if (self.hasCycle()) return 0;

        var count: usize = 0;
        var cursor = self.first();
        while (cursor) |node| {
            count += 1;
            cursor = self.nextNode(node);
        }
        return count;
    }

    pub fn firstCycleWitness(self: ListView) ?CycleWitness {
        var slow = self.first();
        var fast = self.first();
        var slow_index: usize = 0;
        var fast_index: usize = 0;

        while (fast) |fast_node| {
            fast = self.nextNode(fast_node);
            fast_index += 1;
            const fast_mid = fast orelse return null;

            fast = self.nextNode(fast_mid);
            fast_index += 1;
            slow = if (slow) |slow_node| self.nextNode(slow_node) else null;
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

    pub fn hasCycle(self: ListView) bool {
        return self.firstCycleWitness() != null;
    }

    pub fn hasConsistentBacklinks(self: ListView) bool {
        return self.firstBrokenBacklink() == null;
    }

    pub fn firstBrokenBacklink(self: ListView) ?BackLinkBreak {
        var expected_prev = @intFromPtr(self.head);
        var current_index: usize = 0;
        var cursor = ptrFromRaw(self.head.next) orelse {
            return .{
                .current_index = 0,
                .expected_prev = expected_prev,
                .actual_prev = 0,
            };
        };

        while (cursor != self.head) {
            if (cursor.prev != expected_prev) {
                return .{
                    .current_index = current_index,
                    .expected_prev = expected_prev,
                    .actual_prev = cursor.prev,
                };
            }

            expected_prev = @intFromPtr(cursor);
            current_index += 1;
            cursor = ptrFromRaw(cursor.next) orelse {
                return .{
                    .current_index = current_index,
                    .expected_prev = expected_prev,
                    .actual_prev = 0,
                };
            };
        }

        if (self.head.prev != expected_prev) {
            return .{
                .current_index = current_index,
                .expected_prev = expected_prev,
                .actual_prev = self.head.prev,
            };
        }

        return null;
    }
};

test "list view treats a sentinel-only list as empty" {
    var head = ListHead{ .next = 0, .prev = 0 };
    head.next = @intFromPtr(&head);
    head.prev = @intFromPtr(&head);

    const view = ListView.init(&head);
    try std.testing.expect(view.isEmpty());
    try std.testing.expectEqual(@as(usize, 0), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, null), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, null), view.last());
    try std.testing.expect(view.firstCycleWitness() == null);
    try std.testing.expect(!view.hasCycle());
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "list view does not treat a broken sentinel backlink as empty" {
    var head = ListHead{ .next = 0, .prev = 0 };
    head.next = @intFromPtr(&head);
    head.prev = 0;

    const view = ListView.init(&head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expect(view.firstCycleWitness() == null);
    try std.testing.expect(!view.hasCycle());

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, 0), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "list view walks a circular list_head chain in order" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var second = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&second);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&head);
    second.prev = @intFromPtr(&first);

    const view = ListView.init(&head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &second), view.last());
    try std.testing.expect(view.firstCycleWitness() == null);
    try std.testing.expect(!view.hasCycle());

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const ListHead, &first), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &second), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());
    try std.testing.expect(view.hasConsistentBacklinks());
}

test "list view reports the first broken backlink witness" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var second = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&second);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&head);
    second.prev = @intFromPtr(&head);

    const view = ListView.init(&head);
    try std.testing.expect(view.firstCycleWitness() == null);
    try std.testing.expect(!view.hasCycle());

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "list view fails closed for a node-only cycle that never returns to the head" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var second = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&second);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&first);
    second.prev = @intFromPtr(&first);

    const view = ListView.init(&head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 0), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, null), view.last());
    try std.testing.expect(view.hasCycle());

    const witness = view.firstCycleWitness().?;
    try std.testing.expectEqual(@as(usize, 2), witness.slow_index);
    try std.testing.expectEqual(@as(usize, 4), witness.fast_index);

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&second)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}
