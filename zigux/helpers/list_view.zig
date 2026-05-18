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

    pub fn isEmpty(self: ListView) bool {
        const self_ptr = @intFromPtr(self.head);
        return self.head.next == self_ptr and self.head.prev == self_ptr;
    }

    pub fn first(self: ListView) ?*const ListHead {
        const node = ptrFromRaw(self.head.next) orelse return null;
        return if (node == self.head) null else node;
    }

    fn lastUnchecked(self: ListView) ?*const ListHead {
        var tail: ?*const ListHead = null;
        var it = self.iterator();
        while (it.next()) |node| {
            tail = node;
        }
        return tail;
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
        var it = self.iterator();
        while (it.next()) |_| {
            count += 1;
        }
        return count;
    }

    pub fn firstCycleWitness(self: ListView) ?CycleWitness {
        var slow = self.first();
        var fast = self.first();
        var slow_index: usize = 0;
        var fast_index: usize = 0;

        while (fast) |fast_node| {
            const fast_mid = ptrFromRaw(fast_node.next) orelse return null;
            fast_index += 1;
            if (fast_mid == self.head) return null;

            const fast_end = ptrFromRaw(fast_mid.next) orelse return null;
            fast_index += 1;
            if (fast_end == self.head) return null;

            slow = if (slow) |slow_node| ptrFromRaw(slow_node.next) else null;
            slow_index += 1;
            const slow_node = slow orelse return null;
            if (slow_node == self.head) return null;

            fast = fast_end;
            if (slow_node == fast_end) {
                return .{
                    .slow_index = slow_index,
                    .fast_index = fast_index,
                };
            }
        }

        return null;
    }

    fn firstCycleEntry(self: ListView) ?*const ListHead {
        var slow = self.first();
        var fast = self.first();

        while (fast) |fast_node| {
            const fast_mid = ptrFromRaw(fast_node.next) orelse return null;
            if (fast_mid == self.head) return null;

            const fast_end = ptrFromRaw(fast_mid.next) orelse return null;
            if (fast_end == self.head) return null;

            slow = if (slow) |slow_node| ptrFromRaw(slow_node.next) else null;
            const slow_node = slow orelse return null;
            if (slow_node == self.head) return null;

            fast = fast_end;
            if (slow_node == fast_end) {
                var entry = self.first() orelse return null;
                var cycle_cursor = slow_node;
                while (entry != cycle_cursor) {
                    entry = ptrFromRaw(entry.next) orelse return null;
                    cycle_cursor = ptrFromRaw(cycle_cursor.next) orelse return null;
                }
                return entry;
            }
        }

        return null;
    }

    pub fn hasCycle(self: ListView) bool {
        return self.firstCycleWitness() != null;
    }

    pub fn hasConsistentBacklinks(self: ListView) bool {
        if (self.hasCycle()) return false;
        return self.firstBrokenBacklink() == null;
    }

    pub fn firstBrokenBacklink(self: ListView) ?BackLinkBreak {
        const cycle_entry = self.firstCycleEntry();
        var revisited_cycle_entry = false;
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
            if (cycle_entry) |entry| {
                if (cursor == entry) {
                    if (revisited_cycle_entry) {
                        return .{
                            .current_index = current_index,
                            .expected_prev = expected_prev,
                            .actual_prev = cursor.prev,
                        };
                    }
                    revisited_cycle_entry = true;
                }
            }

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

    pub fn tailNextIsHead(self: ListView) bool {
        if (self.hasCycle()) return false;
        return if (self.lastUnchecked()) |node| node.next == @intFromPtr(self.head) else true;
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
    try std.testing.expect(view.tailNextIsHead());
}

test "list view does not treat a broken sentinel backlink as empty" {
    var head = ListHead{ .next = 0, .prev = 0 };
    head.next = @intFromPtr(&head);
    head.prev = 0;

    const view = ListView.init(&head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expect(view.firstCycleWitness() == null);
    try std.testing.expect(!view.hasCycle());
    try std.testing.expect(view.tailNextIsHead());

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
    try std.testing.expect(view.tailNextIsHead());

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const ListHead, &first), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &second), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());
    try std.testing.expect(view.hasConsistentBacklinks());
}

test "list view reports a cycle witness and fails aggregate helpers closed" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var second = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&head);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&first);
    second.prev = @intFromPtr(&first);

    const view = ListView.init(&head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(?*const ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, null), view.last());
    try std.testing.expectEqual(@as(usize, 0), view.len());
    try std.testing.expect(!view.hasConsistentBacklinks());
    try std.testing.expect(!view.tailNextIsHead());
    try std.testing.expect(view.hasCycle());

    const witness = view.firstCycleWitness().?;
    try std.testing.expectEqual(@as(usize, 2), witness.slow_index);
    try std.testing.expectEqual(@as(usize, 4), witness.fast_index);

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&second)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);
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
    try std.testing.expect(view.tailNextIsHead());

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "list view derives the tail from the forward chain when head.prev is stale" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var second = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = 0;
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&head);
    second.prev = @intFromPtr(&first);

    const view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &second), view.last());
    try std.testing.expect(view.tailNextIsHead());
    try std.testing.expect(!view.hasConsistentBacklinks());

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&second)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, 0), breakage.actual_prev);
}

test "list view detects a broken tail next link without a cycle" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var second = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&second);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = 0;
    second.prev = @intFromPtr(&first);

    const view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &second), view.last());
    try std.testing.expect(!view.tailNextIsHead());
    try std.testing.expect(!view.hasCycle());
    try std.testing.expect(!view.hasConsistentBacklinks());

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&second)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, 0), breakage.actual_prev);
}
