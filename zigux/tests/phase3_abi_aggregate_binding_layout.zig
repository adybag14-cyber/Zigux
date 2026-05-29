const std = @import("std");
const abi = @import("../bindings/abi.zig");

fn expectLayout(comptime T: type, size: usize, align: usize) !void {
    try std.testing.expectEqual(size, @sizeOf(T));
    try std.testing.expectEqual(align, @alignOf(T));
}

test "aggregate ABI binding exposes notifier/list/hlist layout records" {
    const ptr_align = @alignOf(usize);

    const notifier_raw_size = (@sizeOf(usize) * 2) + @sizeOf(i32);
    const notifier_size = std.mem.alignForward(usize, notifier_raw_size, ptr_align);
    try expectLayout(abi.NotifierBlock, notifier_size, ptr_align);
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.NotifierBlock, "notifier_call"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(abi.NotifierBlock, "next"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(abi.NotifierBlock, "priority"));

    const increase_raw_size = (@sizeOf(usize) * 2) + (@sizeOf(i32) * 2);
    const increase_size = std.mem.alignForward(usize, increase_raw_size, ptr_align);
    try expectLayout(abi.NotifierChainPriorityIncrease, increase_size, ptr_align);
    try expectLayout(abi.ChainPriorityIncrease, increase_size, ptr_align);
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.ChainPriorityIncrease, "previous_index"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(abi.ChainPriorityIncrease, "current_index"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(abi.ChainPriorityIncrease, "previous_priority"));
    try std.testing.expectEqual(
        @as(usize, (@sizeOf(usize) * 2) + @sizeOf(i32)),
        @offsetOf(abi.ChainPriorityIncrease, "current_priority"),
    );

    try expectLayout(abi.ListHead, @sizeOf(usize) * 2, ptr_align);
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.ListHead, "next"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(abi.ListHead, "prev"));

    try expectLayout(abi.HListHead, @sizeOf(usize), ptr_align);
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.HListHead, "first"));

    try expectLayout(abi.HListNode, @sizeOf(usize) * 2, ptr_align);
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.HListNode, "next"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(abi.HListNode, "pprev"));

    try expectLayout(abi.ListBackLinkBreak, @sizeOf(usize) * 3, ptr_align);
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.ListBackLinkBreak, "current_index"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(abi.ListBackLinkBreak, "expected_prev"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(abi.ListBackLinkBreak, "actual_prev"));

    try expectLayout(abi.HListPrevLinkBreak, @sizeOf(usize) * 3, ptr_align);
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.HListPrevLinkBreak, "current_index"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(abi.HListPrevLinkBreak, "expected_pprev"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(abi.HListPrevLinkBreak, "actual_pprev"));
}

test "aggregate ABI binding relays notifier and list helpers" {
    const tail = abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 9,
    };
    const middle = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&tail),
        .priority = 4,
    };
    const head = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&middle),
        .priority = 6,
    };

    try std.testing.expect(!abi.chainHasNonincreasingPriority(&head));
    const increase = abi.firstChainPriorityIncrease(&head) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 1), increase.previous_index);
    try std.testing.expectEqual(@as(usize, 2), increase.current_index);
    try std.testing.expectEqual(@as(i32, 4), increase.previous_priority);
    try std.testing.expectEqual(@as(i32, 9), increase.current_priority);

    var list_head = abi.ListHead{ .next = 0, .prev = 0 };
    list_head.next = @intFromPtr(&list_head);
    list_head.prev = @intFromPtr(&list_head);
    try std.testing.expect(abi.listHasConsistentBacklinks(&list_head));
    try std.testing.expectEqual(@as(?abi.ListBackLinkBreak, null), abi.firstBrokenBacklink(&list_head));

    const hlist_head = abi.HListHead{ .first = 0 };
    try std.testing.expect(abi.hlistFirstPprevMatchesHead(&hlist_head));
    try std.testing.expect(abi.hlistHasConsistentPrevLinks(&hlist_head));
    try std.testing.expectEqual(@as(?abi.HListPrevLinkBreak, null), abi.firstBrokenPrevLink(&hlist_head));
}
