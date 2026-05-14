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

pub fn prioritiesNonincreasing(blocks: []const NotifierBlock) bool {
    if (blocks.len < 2) return true;

    var previous_priority = blocks[0].priority;
    for (blocks[1..]) |block| {
        if (block.priority > previous_priority) return false;
        previous_priority = block.priority;
    }

    return true;
}

test "notifier abi keeps nonincreasing priority order reviewable" {
    const ordered = [_]NotifierBlock{
        .{ .notifier_call = 1, .next = 2, .priority = 8 },
        .{ .notifier_call = 2, .next = 3, .priority = 8 },
        .{ .notifier_call = 3, .next = 0, .priority = -4 },
    };
    const rising = [_]NotifierBlock{
        .{ .notifier_call = 1, .next = 2, .priority = 3 },
        .{ .notifier_call = 2, .next = 0, .priority = 5 },
    };

    try std.testing.expect(prioritiesNonincreasing(&ordered));
    try std.testing.expect(!prioritiesNonincreasing(&rising));
}

test "notifier abi accepts empty and singleton priority samples" {
    const single = [_]NotifierBlock{
        .{ .notifier_call = 1, .next = 0, .priority = 7 },
    };

    try std.testing.expect(prioritiesNonincreasing(&.{}));
    try std.testing.expect(prioritiesNonincreasing(&single));
}

test "notifier abi keeps result codes and block layout explicit" {
    try std.testing.expectEqual(@as(u32, 0), @intFromEnum(NotifierResult.done));
    try std.testing.expectEqual(@as(u32, 1), @intFromEnum(NotifierResult.ok));
    try std.testing.expectEqual(@as(u32, 2), @intFromEnum(NotifierResult.stop));

    try std.testing.expectEqual(@as(usize, 24), @sizeOf(NotifierBlock));
    try std.testing.expectEqual(@as(usize, 8), @alignOf(NotifierBlock));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(NotifierBlock, "notifier_call"));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(NotifierBlock, "next"));
    try std.testing.expectEqual(@as(usize, 16), @offsetOf(NotifierBlock, "priority"));
}
