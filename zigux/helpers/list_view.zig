const std = @import("std");
const abi = @import("list_hlist_binding");

fn pointerFromRaw(raw: usize) ?*const abi.ListHead {
    if (raw == 0) return null;
    const ptr: *const abi.ListHead = @ptrFromInt(raw);
    return ptr;
}

pub const Iterator = struct {
    head: *const abi.ListHead,
    current: ?*const abi.ListHead,

    pub fn next(self: *Iterator) ?*const abi.ListHead {
        const node = self.current orelse return null;
        const next_node = pointerFromRaw(node.next) orelse {
            self.current = null;
            return node;
        };
        self.current = if (next_node == self.head) null else next_node;
        return node;
    }
};

pub const ListView = struct {
    head: *const abi.ListHead,

    pub fn init(head: *const abi.ListHead) ListView {
        return .{ .head = head };
    }

    pub fn isEmpty(self: ListView) bool {
        const head_addr = @intFromPtr(self.head);
        return self.head.next == head_addr and self.head.prev == head_addr;
    }

    pub fn first(self: ListView) ?*const abi.ListHead {
        if (self.isEmpty()) return null;
        return pointerFromRaw(self.head.next);
    }

    pub fn last(self: ListView) ?*const abi.ListHead {
        if (self.isEmpty()) return null;
        return pointerFromRaw(self.head.prev);
    }

    pub fn iterator(self: ListView) Iterator {
        return .{
            .head = self.head,
            .current = self.first(),
        };
    }

    pub fn len(self: ListView) usize {
        var count: usize = 0;
        var it = self.iterator();
        while (it.next()) |_| {
            count += 1;
        }
        return count;
    }

    pub fn isCircular(self: ListView) bool {
        const head_addr = @intFromPtr(self.head);
        if (self.head.next == 0 or self.head.prev == 0) return false;
        if (self.isEmpty()) return true;

        const first_node = self.first() orelse return false;
        var current = first_node;
        var steps: usize = 0;

        while (true) {
            steps += 1;
            if (steps > 1024) return false;

            const next = pointerFromRaw(current.next) orelse return false;
            const prev = pointerFromRaw(current.prev) orelse return false;
            if (next.prev != @intFromPtr(current)) return false;
            if (prev.next != @intFromPtr(current)) return false;

            if (next == self.head) {
                return self.head.prev == @intFromPtr(current) and self.head.next == @intFromPtr(first_node);
            }

            if (@intFromPtr(next) == head_addr) return false;
            current = next;
        }
    }
};

test "list view walks bounded circular list entries" {
    var head = abi.ListHead{ .next = 0, .prev = 0 };
    var first = abi.ListHead{ .next = 0, .prev = 0 };
    var second = abi.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&second);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&head);
    second.prev = @intFromPtr(&first);

    const view = ListView.init(&head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expect(view.isCircular());
    try std.testing.expectEqual(@as(*const abi.ListHead, &first), view.first().?);
    try std.testing.expectEqual(@as(*const abi.ListHead, &second), view.last().?);

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const abi.ListHead, &first), it.next());
    try std.testing.expectEqual(@as(?*const abi.ListHead, &second), it.next());
    try std.testing.expectEqual(@as(?*const abi.ListHead, null), it.next());
}

test "list view keeps empty sentinel behavior explicit" {
    var head = abi.ListHead{ .next = 0, .prev = 0 };
    head.next = @intFromPtr(&head);
    head.prev = @intFromPtr(&head);

    const view = ListView.init(&head);
    try std.testing.expect(view.isEmpty());
    try std.testing.expectEqual(@as(usize, 0), view.len());
    try std.testing.expect(view.isCircular());
    try std.testing.expect(view.first() == null);
    try std.testing.expect(view.last() == null);
}
