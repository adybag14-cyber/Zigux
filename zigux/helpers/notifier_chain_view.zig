const std = @import("std");

fn notifierBlockFromRaw(raw: usize) ?*const NotifierBlock {
    if (raw == 0) return null;
    const node: *const NotifierBlock = @ptrFromInt(raw);
    return node;
}

pub const NotifierBlock = extern struct {
    notifier_call: usize,
    next: usize,
    priority: i32,
};

pub const PriorityIncrease = struct {
    previous_index: usize,
    current_index: usize,
    previous_priority: i32,
    current_priority: i32,
};

pub const Iterator = struct {
    current: ?*const NotifierBlock = null,

    pub fn next(self: *Iterator) ?*const NotifierBlock {
        const node = self.current orelse return null;
        self.current = notifierBlockFromRaw(node.next);
        return node;
    }
};

pub const NotifierChainView = struct {
    head: ?*const NotifierBlock,

    pub fn init(head: ?*const NotifierBlock) NotifierChainView {
        return .{ .head = head };
    }

    pub fn isEmpty(self: NotifierChainView) bool {
        return self.head == null;
    }

    pub fn first(self: NotifierChainView) ?*const NotifierBlock {
        return self.head;
    }

    pub fn iterator(self: NotifierChainView) Iterator {
        return .{ .current = self.head };
    }

    pub fn len(self: NotifierChainView) usize {
        var count: usize = 0;
        var it = self.iterator();
        while (it.next()) |_| {
            count += 1;
        }
        return count;
    }

    pub fn hasNonincreasingPriority(self: NotifierChainView) bool {
        var current = self.head orelse return true;
        var previous_priority = current.priority;

        while (notifierBlockFromRaw(current.next)) |next| {
            if (next.priority > previous_priority) return false;
            previous_priority = next.priority;
            current = next;
        }

        return true;
    }

    pub fn firstPriorityIncrease(self: NotifierChainView) ?PriorityIncrease {
        var current = self.head orelse return null;
        var previous_index: usize = 0;
        var previous_priority = current.priority;

        while (notifierBlockFromRaw(current.next)) |next| {
            const current_index = previous_index + 1;
            if (next.priority > previous_priority) {
                return .{
                    .previous_index = previous_index,
                    .current_index = current_index,
                    .previous_priority = previous_priority,
                    .current_priority = next.priority,
                };
            }

            previous_index = current_index;
            previous_priority = next.priority;
            current = next;
        }

        return null;
    }
};

test "notifier chain view treats a null head as empty" {
    const view = NotifierChainView.init(null);

    try std.testing.expect(view.isEmpty());
    try std.testing.expectEqual(@as(usize, 0), view.len());
    try std.testing.expectEqual(@as(?*const NotifierBlock, null), view.first());
    try std.testing.expect(view.hasNonincreasingPriority());
    try std.testing.expectEqual(@as(?PriorityIncrease, null), view.firstPriorityIncrease());
}

test "notifier chain view walks a single-node chain" {
    const first = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 7,
    };
    const view = NotifierChainView.init(&first);

    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 1), view.len());
    try std.testing.expectEqual(@as(?*const NotifierBlock, &first), view.first());
    try std.testing.expect(view.hasNonincreasingPriority());
    try std.testing.expectEqual(@as(?PriorityIncrease, null), view.firstPriorityIncrease());

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const NotifierBlock, &first), it.next());
    try std.testing.expectEqual(@as(?*const NotifierBlock, null), it.next());
}

test "notifier chain view accepts equal and descending priorities" {
    const third = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 4,
    };
    const second = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&third),
        .priority = 6,
    };
    const first = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&second),
        .priority = 6,
    };
    const view = NotifierChainView.init(&first);

    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expect(view.hasNonincreasingPriority());
    try std.testing.expectEqual(@as(?PriorityIncrease, null), view.firstPriorityIncrease());
}

test "notifier chain view reports the first priority increase witness" {
    const fourth = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 5,
    };
    const third = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&fourth),
        .priority = 2,
    };
    const second = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&third),
        .priority = 3,
    };
    const first = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&second),
        .priority = 6,
    };
    const view = NotifierChainView.init(&first);

    try std.testing.expect(!view.hasNonincreasingPriority());

    const increase = view.firstPriorityIncrease().?;
    try std.testing.expectEqual(@as(usize, 2), increase.previous_index);
    try std.testing.expectEqual(@as(usize, 3), increase.current_index);
    try std.testing.expectEqual(@as(i32, 2), increase.previous_priority);
    try std.testing.expectEqual(@as(i32, 5), increase.current_priority);
}
