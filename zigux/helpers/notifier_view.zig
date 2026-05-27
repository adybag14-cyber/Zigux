const std = @import("std");
const notifier_abi = @import("notifier_abi");

pub const NotifierBlock = notifier_abi.NotifierBlock;
pub const PriorityIncrease = notifier_abi.NotifierChainPriorityIncrease;

fn nodeFromRaw(raw: usize) ?*const NotifierBlock {
    if (raw == 0) return null;
    const node: *const NotifierBlock = @ptrFromInt(raw);
    return node;
}

pub const Iterator = struct {
    current: ?*const NotifierBlock = null,

    pub fn next(self: *Iterator) ?*const NotifierBlock {
        const node = self.current orelse return null;
        self.current = nodeFromRaw(node.next);
        return node;
    }
};

pub const NotifierView = struct {
    head: ?*const NotifierBlock,

    pub fn init(head: ?*const NotifierBlock) NotifierView {
        return .{ .head = head };
    }

    pub fn isEmpty(self: NotifierView) bool {
        return self.head == null;
    }

    pub fn first(self: NotifierView) ?*const NotifierBlock {
        return self.head;
    }

    pub fn iterator(self: NotifierView) Iterator {
        return .{ .current = self.head };
    }

    pub fn len(self: NotifierView) usize {
        var count: usize = 0;
        var it = self.iterator();
        while (it.next()) |_| {
            count += 1;
        }
        return count;
    }

    pub fn last(self: NotifierView) ?*const NotifierBlock {
        var tail: ?*const NotifierBlock = null;
        var it = self.iterator();
        while (it.next()) |node| {
            tail = node;
        }
        return tail;
    }

    pub fn allCallbacksPresent(self: NotifierView) bool {
        return self.firstNullCallbackIndex() == null;
    }

    pub fn firstNullCallbackIndex(self: NotifierView) ?usize {
        var index: usize = 0;
        var it = self.iterator();
        while (it.next()) |node| : (index += 1) {
            if (node.notifier_call == 0) return index;
        }
        return null;
    }

    pub fn hasNonincreasingPriority(self: NotifierView) bool {
        return self.firstPriorityIncrease() == null;
    }

    pub fn firstPriorityIncrease(self: NotifierView) ?PriorityIncrease {
        var current = self.head orelse return null;
        var previous_index: usize = 0;
        var previous_priority = current.priority;

        while (current.next != 0) {
            const next = nodeFromRaw(current.next) orelse return null;
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

test "notifier view treats a null head as empty" {
    const view = NotifierView.init(null);

    try std.testing.expect(view.isEmpty());
    try std.testing.expectEqual(@as(usize, 0), view.len());
    try std.testing.expectEqual(@as(?*const NotifierBlock, null), view.first());
    try std.testing.expectEqual(@as(?*const NotifierBlock, null), view.last());
    try std.testing.expect(view.hasNonincreasingPriority());
    try std.testing.expect(view.allCallbacksPresent());
    try std.testing.expectEqual(@as(?usize, null), view.firstNullCallbackIndex());
    try std.testing.expectEqual(@as(?PriorityIncrease, null), view.firstPriorityIncrease());
}

test "notifier view walks a bounded chain in order" {
    const third = NotifierBlock{
        .notifier_call = 0x3000,
        .next = 0,
        .priority = 2,
    };
    const second = NotifierBlock{
        .notifier_call = 0x2000,
        .next = @intFromPtr(&third),
        .priority = 5,
    };
    const first = NotifierBlock{
        .notifier_call = 0x1000,
        .next = @intFromPtr(&second),
        .priority = 5,
    };

    const view = NotifierView.init(&first);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const NotifierBlock, &first), view.first());
    try std.testing.expectEqual(@as(?*const NotifierBlock, &third), view.last());
    try std.testing.expect(view.hasNonincreasingPriority());
    try std.testing.expect(view.allCallbacksPresent());

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const NotifierBlock, &first), it.next());
    try std.testing.expectEqual(@as(?*const NotifierBlock, &second), it.next());
    try std.testing.expectEqual(@as(?*const NotifierBlock, &third), it.next());
    try std.testing.expectEqual(@as(?*const NotifierBlock, null), it.next());
}

test "notifier view reports the first null callback witness" {
    const tail = NotifierBlock{
        .notifier_call = 0x3000,
        .next = 0,
        .priority = 1,
    };
    const middle = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&tail),
        .priority = 2,
    };
    const head = NotifierBlock{
        .notifier_call = 0x1000,
        .next = @intFromPtr(&middle),
        .priority = 3,
    };

    const view = NotifierView.init(&head);
    try std.testing.expect(!view.allCallbacksPresent());
    try std.testing.expectEqual(@as(?usize, 1), view.firstNullCallbackIndex());
}

test "notifier view reports the first priority increase witness" {
    const tail = NotifierBlock{
        .notifier_call = 0x3000,
        .next = 0,
        .priority = 7,
    };
    const middle = NotifierBlock{
        .notifier_call = 0x2000,
        .next = @intFromPtr(&tail),
        .priority = 2,
    };
    const head = NotifierBlock{
        .notifier_call = 0x1000,
        .next = @intFromPtr(&middle),
        .priority = 4,
    };

    const increase = NotifierView.init(&head).firstPriorityIncrease().?;
    try std.testing.expect(!NotifierView.init(&head).hasNonincreasingPriority());
    try std.testing.expectEqual(@as(usize, 1), increase.previous_index);
    try std.testing.expectEqual(@as(usize, 2), increase.current_index);
    try std.testing.expectEqual(@as(i32, 2), increase.previous_priority);
    try std.testing.expectEqual(@as(i32, 7), increase.current_priority);
}
