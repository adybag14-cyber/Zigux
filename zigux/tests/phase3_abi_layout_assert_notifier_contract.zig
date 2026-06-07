const std = @import("std");
const testing = std.testing;

const abi = @import("abi_bindings");
const layout_assert = @import("layout_assert_helpers");

test "layout assert notifier block mirrors ABI constants" {
    try layout_assert.assertNotifierBlockLayout();

    const raw_size = (@sizeOf(usize) * 2) + @sizeOf(i32);
    const expected_size = std.mem.alignForward(usize, raw_size, @alignOf(abi.NotifierBlock));

    try testing.expectEqual(expected_size, abi.notifier_block_size);
    try testing.expectEqual(@as(usize, @alignOf(usize)), abi.notifier_block_align);
    try testing.expectEqual(@as(usize, 0), abi.notifier_block_notifier_call_offset);
    try testing.expectEqual(@as(usize, @sizeOf(usize)), abi.notifier_block_next_offset);
    try testing.expectEqual(@as(usize, @sizeOf(usize) * 2), abi.notifier_block_priority_offset);

    try testing.expectEqual(abi.notifier_block_size, @sizeOf(abi.NotifierBlock));
    try testing.expectEqual(abi.notifier_block_align, @alignOf(abi.NotifierBlock));
    try testing.expectEqual(abi.notifier_block_notifier_call_offset, @offsetOf(abi.NotifierBlock, "notifier_call"));
    try testing.expectEqual(abi.notifier_block_next_offset, @offsetOf(abi.NotifierBlock, "next"));
    try testing.expectEqual(abi.notifier_block_priority_offset, @offsetOf(abi.NotifierBlock, "priority"));
}

test "layout assert notifier priority increase keeps pointer then priority order" {
    try layout_assert.assertNotifierChainPriorityIncreaseLayout();

    const expected_size = std.mem.alignForward(
        usize,
        (@sizeOf(usize) * 2) + (@sizeOf(i32) * 2),
        @alignOf(abi.ChainPriorityIncrease),
    );

    try testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(abi.ChainPriorityIncrease));
    try testing.expectEqual(@as(usize, 0), @offsetOf(abi.ChainPriorityIncrease, "previous_index"));
    try testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(abi.ChainPriorityIncrease, "current_index"));
    try testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(abi.ChainPriorityIncrease, "previous_priority"));
    try testing.expectEqual(
        @as(usize, (@sizeOf(usize) * 2) + @sizeOf(i32)),
        @offsetOf(abi.ChainPriorityIncrease, "current_priority"),
    );
    try testing.expectEqual(expected_size, @sizeOf(abi.ChainPriorityIncrease));
}

test "layout assert list and hlist node surfaces stay pointer-width aligned" {
    try layout_assert.assertListHeadLayout();
    try layout_assert.assertHListHeadLayout();
    try layout_assert.assertHListNodeLayout();

    try testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(abi.ListHead));
    try testing.expectEqual(@as(usize, 0), @offsetOf(abi.ListHead, "next"));
    try testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(abi.ListHead, "prev"));
    try testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @sizeOf(abi.ListHead));

    try testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(abi.HListHead));
    try testing.expectEqual(@as(usize, 0), @offsetOf(abi.HListHead, "first"));
    try testing.expectEqual(@as(usize, @sizeOf(usize)), @sizeOf(abi.HListHead));

    try testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(abi.HListNode));
    try testing.expectEqual(@as(usize, 0), @offsetOf(abi.HListNode, "next"));
    try testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(abi.HListNode, "pprev"));
    try testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @sizeOf(abi.HListNode));
}

test "layout assert break records keep index expected actual order" {
    try layout_assert.assertListBackLinkBreakLayout();
    try layout_assert.assertHListPrevLinkBreakLayout();

    try testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(abi.ListBackLinkBreak));
    try testing.expectEqual(@as(usize, 0), @offsetOf(abi.ListBackLinkBreak, "current_index"));
    try testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(abi.ListBackLinkBreak, "expected_prev"));
    try testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(abi.ListBackLinkBreak, "actual_prev"));
    try testing.expectEqual(@as(usize, @sizeOf(usize) * 3), @sizeOf(abi.ListBackLinkBreak));

    try testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(abi.HListPrevLinkBreak));
    try testing.expectEqual(@as(usize, 0), @offsetOf(abi.HListPrevLinkBreak, "current_index"));
    try testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(abi.HListPrevLinkBreak, "expected_pprev"));
    try testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(abi.HListPrevLinkBreak, "actual_pprev"));
    try testing.expectEqual(@as(usize, @sizeOf(usize) * 3), @sizeOf(abi.HListPrevLinkBreak));
}
