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

pub const PriorityIncrease = struct {
    previous: *const abi.NotifierBlock,
    current: *const abi.NotifierBlock,
    previous_index: usize,
    current_index: usize,
    previous_priority: i32,
    current_priority: i32,
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

    pub fn firstPriorityIncrease(self: ChainView) ?PriorityIncrease {
        var it = self.iterator();
        const first_node = it.next() orelse return null;
        var previous = first_node;
        var index: usize = 1;

        while (it.next()) |node| : (index += 1) {
            if (node.priority > previous.priority) {
                return .{
                    .previous = previous,
                    .current = node,
                    .previous_index = index - 1,
                    .current_index = index,
                    .previous_priority = previous.priority,
                    .current_priority = node.priority,
                };
            }
            previous = node;
        }
        return null;
    }

    pub fn hasNonincreasingPriority(self: ChainView) bool {
        return self.firstPriorityIncrease() == null;
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

test "chain view reports the first priority increase" {
    var tail = abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 9,
    };
    var middle = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&tail),
        .priority = 3,
    };
    var head = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&middle),
        .priority = 5,
    };

    const increase = ChainView.init(&head).firstPriorityIncrease().?;
    try std.testing.expectEqual(@as(usize, 1), increase.previous_index);
    try std.testing.expectEqual(@as(usize, 2), increase.current_index);
    try std.testing.expectEqual(@as(i32, 3), increase.previous_priority);
    try std.testing.expectEqual(@as(i32, 9), increase.current_priority);
    try std.testing.expectEqual(@as(*const abi.NotifierBlock, &middle), increase.previous);
    try std.testing.expectEqual(@as(*const abi.NotifierBlock, &tail), increase.current);
}

test "chain view checks nonincreasing notifier priority" {
    try std.testing.expect(ChainView.init(null).hasNonincreasingPriority());
    try std.testing.expect(ChainView.init(null).firstPriorityIncrease() == null);

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
    try std.testing.expect(ChainView.init(&head).firstPriorityIncrease() == null);

    head.priority = 0;
    const increase = ChainView.init(&head).firstPriorityIncrease().?;
    try std.testing.expectEqual(@as(usize, 0), increase.previous_index);
    try std.testing.expectEqual(@as(usize, 1), increase.current_index);
    try std.testing.expectEqual(@as(i32, 0), increase.previous_priority);
    try std.testing.expectEqual(@as(i32, 1), increase.current_priority);
    try std.testing.expect(!ChainView.init(&head).hasNonincreasingPriority());
}
