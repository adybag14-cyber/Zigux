const std = @import("std");
const testing = std.testing;

const abi = @import("abi_bindings");
const layout_assert = @import("layout_assert");

test "notifier binding keeps shared result values aligned" {
    try testing.expectEqual(@as(u32, abi.NOTIFIER_DONE), @intFromEnum(abi.NotifierResult.done));
    try testing.expectEqual(@as(u32, abi.NOTIFIER_OK), @intFromEnum(abi.NotifierResult.ok));
    try testing.expectEqual(@as(u32, abi.NOTIFIER_STOP), @intFromEnum(abi.NotifierResult.stop));
}

test "notifier binding keeps published layout explicit" {
    const raw_size = (@sizeOf(usize) * 2) + @sizeOf(i32);
    const expected_size = std.mem.alignForward(usize, raw_size, @alignOf(usize));

    try layout_assert.expectLayout(abi.NotifierBlock, expected_size, @alignOf(usize));
    try layout_assert.expectFieldLayout(abi.NotifierBlock, "notifier_call", 0);
    try layout_assert.expectFieldLayout(abi.NotifierBlock, "next", @sizeOf(usize));
    try layout_assert.expectFieldLayout(abi.NotifierBlock, "priority", @sizeOf(usize) * 2);
}

test "notifier binding chain helper stays aligned with shared abi helper" {
    const tail = abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 3,
    };
    const middle = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&tail),
        .priority = 5,
    };
    const head = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&middle),
        .priority = 5,
    };

    try testing.expect(abi.chainHasNonincreasingPriority(&head));

    const increasing_tail = abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 8,
    };
    const increasing_head = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&increasing_tail),
        .priority = 2,
    };

    try testing.expect(!abi.chainHasNonincreasingPriority(&increasing_head));
}

test "notifier binding preserves pointer-width links" {
    const tail = abi.NotifierBlock{
        .notifier_call = 0x33,
        .next = 0,
        .priority = -2,
    };
    const middle = abi.NotifierBlock{
        .notifier_call = 0x22,
        .next = @intFromPtr(&tail),
        .priority = 7,
    };
    const head = abi.NotifierBlock{
        .notifier_call = 0x11,
        .next = @intFromPtr(&middle),
        .priority = 12,
    };

    const middle_ptr: *const abi.NotifierBlock = @ptrFromInt(head.next);
    const tail_ptr: *const abi.NotifierBlock = @ptrFromInt(middle_ptr.next);

    try testing.expectEqual(@as(usize, @intFromPtr(&middle)), head.next);
    try testing.expectEqual(@as(usize, @intFromPtr(&tail)), middle_ptr.next);
    try testing.expectEqual(@as(usize, 0), tail_ptr.next);
    try testing.expectEqual(@as(i32, 12), head.priority);
    try testing.expectEqual(@as(i32, 7), middle_ptr.priority);
    try testing.expectEqual(@as(i32, -2), tail_ptr.priority);
}
