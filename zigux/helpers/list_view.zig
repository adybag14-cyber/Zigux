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

    pub fn isSingular(self: ListView) bool {
        return self.first() != null and self.head.next == self.head.prev;
    }

    pub fn first(self: ListView) ?*const ListHead {
        const node = ptrFromRaw(self.head.next) orelse return null;
        return if (node == self.head) null else node;
    }

    pub fn last(self: ListView) ?*const ListHead {
        const node = ptrFromRaw(self.head.prev) orelse return null;
        return if (node == self.head) null else node;
    }

    pub fn iterator(self: ListView) Iterator {
        return .{ .head = self.head };
    }

    pub fn len(self: ListView) usize {
        var count: usize = 0;
        var it = self.iterator();
        while (it.next()) |_| {
            count += 1;
        }
        return count;
    }

    pub fn contains(self: ListView, target: *const ListHead) bool {
        var it = self.iterator();
        while (it.next()) |node| {
            if (node == target) return true;
        }
        return false;
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
    try std.testing.expect(!view.isSingular());
    try std.testing.expectEqual(@as(usize, 0), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, null), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, null), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "list view does not treat a broken sentinel backlink as empty" {
    var head = ListHead{ .next = 0, .prev = 0 };
    head.next = @intFromPtr(&head);
    head.prev = 0;

    const view = ListView.init(&head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expect(!view.isSingular());

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, 0), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "list view recognizes a singular list_head chain" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var only = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&only);
    head.prev = @intFromPtr(&only);
    only.next = @intFromPtr(&head);
    only.prev = @intFromPtr(&head);

    const view = ListView.init(&head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expect(view.isSingular());
    try std.testing.expectEqual(@as(usize, 1), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &only), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &only), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
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
    try std.testing.expect(!view.isSingular());
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &second), view.last());

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const ListHead, &first), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &second), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());
    try std.testing.expect(view.hasConsistentBacklinks());
}

test "list view reports visible-node membership" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var second = ListHead{ .next = 0, .prev = 0 };
    var detached = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&second);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&head);
    second.prev = @intFromPtr(&first);
    detached.next = @intFromPtr(&detached);
    detached.prev = @intFromPtr(&detached);

    const view = ListView.init(&head);
    try std.testing.expect(view.contains(&first));
    try std.testing.expect(view.contains(&second));
    try std.testing.expect(!view.contains(&head));
    try std.testing.expect(!view.contains(&detached));
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

    const breakage = ListView.init(&head).firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);
    try std.testing.expect(!ListView.init(&head).hasConsistentBacklinks());
}
