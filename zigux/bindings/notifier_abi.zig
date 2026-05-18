const std = @import("std");

pub const NotifierResult = enum(u32) {
    done = 0,
    ok = 1,
    stop = 2,
};

pub const NotifierBlock = extern struct {
    notifier_call: usize,
    next: usize,
    priority: i32,
};

pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {
    var current = head orelse return true;
    var previous_priority = current.priority;

    while (current.next != 0) {
        const next: *const NotifierBlock = @ptrFromInt(current.next);
        if (next.priority > previous_priority) return false;
        previous_priority = next.priority;
        current = next;
    }

    return true;
}

test "notifier result constants stay aligned with the exported ABI values" {
    try std.testing.expectEqual(@as(u32, 0), @intFromEnum(NotifierResult.done));
    try std.testing.expectEqual(@as(u32, 1), @intFromEnum(NotifierResult.ok));
    try std.testing.expectEqual(@as(u32, 2), @intFromEnum(NotifierResult.stop));
}

test "notifier block layout stays aligned with the exported ABI header" {
    const expected_size = std.mem.alignForward(
        usize,
        (@sizeOf(usize) * 2) + @sizeOf(i32),
        @alignOf(NotifierBlock),
    );

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(NotifierBlock));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(NotifierBlock, "notifier_call"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(NotifierBlock, "next"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(NotifierBlock, "priority"));
    try std.testing.expectEqual(expected_size, @sizeOf(NotifierBlock));
}

test "notifier priority helper accepts empty chain" {
    try std.testing.expect(chainHasNonincreasingPriority(null));
}

test "notifier priority helper accepts single node chain" {
    const node = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 4,
    };

    try std.testing.expect(chainHasNonincreasingPriority(&node));
}

test "notifier priority helper accepts equal and descending priorities" {
    const third = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 3,
    };
    const second = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&third),
        .priority = 5,
    };
    const first = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&second),
        .priority = 5,
    };

    try std.testing.expect(chainHasNonincreasingPriority(&first));
}

test "notifier priority helper rejects increasing priority" {
    const third = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 6,
    };
    const second = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&third),
        .priority = 2,
    };
    const first = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&second),
        .priority = 4,
    };

    try std.testing.expect(!chainHasNonincreasingPriority(&first));
}
