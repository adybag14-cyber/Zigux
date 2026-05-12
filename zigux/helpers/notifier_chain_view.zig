const std = @import("std");
const abi = @import("notifier_abi_bindings");

fn nextPtr(raw: usize) ?*const abi.NotifierBlock {
    if (raw == 0) return null;
    const next: *const abi.NotifierBlock = @ptrFromInt(raw);
    return next;
}

pub const Iterator = struct {
    current: ?*const abi.NotifierBlock,

    pub fn next(self: *Iterator) ?*const abi.NotifierBlock {
        const node = self.current orelse return null;
        self.current = nextPtr(node.next);
        return node;
    }
};

pub const ChainView = struct {
    head: ?*const abi.NotifierBlock,

    pub fn init(head: ?*const abi.NotifierBlock) ChainView {
        return .{ .head = head };
    }

    pub fn first(self: ChainView) ?*const abi.NotifierBlock {
        return self.head;
    }

    pub fn iterator(self: ChainView) Iterator {
        return .{ .current = self.head };
    }

    pub fn len(self: ChainView) usize {
        var count: usize = 0;
        var it = self.iterator();
        while (it.next()) |_| {
            count += 1;
        }
        return count;
    }

    pub fn hasNonincreasingPriority(self: ChainView) bool {
        var it = self.iterator();
        const first_node = it.next() orelse return true;
        var previous_priority = first_node.priority;

        while (it.next()) |node| {
            if (node.priority > previous_priority) return false;
            previous_priority = node.priority;
        }
        return true;
    }
};

test "chain view walks nodes in notifier order" {
    var tail = abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = -10,
    };
    var middle = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&tail),
        .priority = 0,
    };
    var head = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&middle),
        .priority = 10,
    };

    var it = ChainView.init(&head).iterator();
    try std.testing.expectEqual(@as(i32, 10), it.next().?.priority);
    try std.testing.expectEqual(@as(i32, 0), it.next().?.priority);
    try std.testing.expectEqual(@as(i32, -10), it.next().?.priority);
    try std.testing.expectEqual(@as(?*const abi.NotifierBlock, null), it.next());
}

test "chain view counts empty and populated notifier chains" {
    try std.testing.expectEqual(@as(usize, 0), ChainView.init(null).len());

    var tail = abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 2,
    };
    var head = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&tail),
        .priority = 4,
    };

    try std.testing.expectEqual(@as(usize, 2), ChainView.init(&head).len());
}

test "chain view checks nonincreasing notifier priority" {
    try std.testing.expect(ChainView.init(null).hasNonincreasingPriority());

    var tail = abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 1,
    };
    var head = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&tail),
        .priority = 3,
    };
    try std.testing.expect(ChainView.init(&head).hasNonincreasingPriority());

    head.priority = 0;
    try std.testing.expect(!ChainView.init(&head).hasNonincreasingPriority());
}
