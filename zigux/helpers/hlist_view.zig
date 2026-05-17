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
