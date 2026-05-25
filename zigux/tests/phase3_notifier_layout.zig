const std = @import("std");
const testing = std.testing;

const abi = @import("abi_bindings");
const notifier = @import("notifier_binding");

test "phase3 notifier layout keeps published result constants aligned" {
    try testing.expectEqual(@as(u32, abi.NOTIFIER_DONE), @intFromEnum(notifier.NotifierResult.done));
    try testing.expectEqual(@as(u32, abi.NOTIFIER_OK), @intFromEnum(notifier.NotifierResult.ok));
    try testing.expectEqual(@as(u32, abi.NOTIFIER_STOP), @intFromEnum(notifier.NotifierResult.stop));
    try testing.expectEqual(@as(?notifier.NotifierResult, .done), notifier.resultFromInt(abi.NOTIFIER_DONE));
    try testing.expectEqual(@as(?notifier.NotifierResult, .ok), notifier.resultFromInt(abi.NOTIFIER_OK));
    try testing.expectEqual(@as(?notifier.NotifierResult, .stop), notifier.resultFromInt(abi.NOTIFIER_STOP));
    try testing.expectEqual(@as(?notifier.NotifierResult, null), notifier.resultFromInt(7));
}

test "phase3 notifier layout keeps notifier and list layouts aligned with the shared ABI surface" {
    try testing.expectEqual(@sizeOf(abi.NotifierBlock), @sizeOf(notifier.NotifierBlock));
    try testing.expectEqual(@alignOf(abi.NotifierBlock), @alignOf(notifier.NotifierBlock));
    try testing.expectEqual(@offsetOf(abi.NotifierBlock, "notifier_call"), @offsetOf(notifier.NotifierBlock, "notifier_call"));
    try testing.expectEqual(@offsetOf(abi.NotifierBlock, "next"), @offsetOf(notifier.NotifierBlock, "next"));
    try testing.expectEqual(@offsetOf(abi.NotifierBlock, "priority"), @offsetOf(notifier.NotifierBlock, "priority"));

    try testing.expectEqual(@sizeOf(abi.NotifierChainPriorityIncrease), @sizeOf(notifier.NotifierChainPriorityIncrease));
    try testing.expectEqual(@alignOf(abi.NotifierChainPriorityIncrease), @alignOf(notifier.NotifierChainPriorityIncrease));
    try testing.expectEqual(@offsetOf(abi.NotifierChainPriorityIncrease, "previous_index"), @offsetOf(notifier.NotifierChainPriorityIncrease, "previous_index"));
    try testing.expectEqual(@offsetOf(abi.NotifierChainPriorityIncrease, "current_index"), @offsetOf(notifier.NotifierChainPriorityIncrease, "current_index"));
    try testing.expectEqual(@offsetOf(abi.NotifierChainPriorityIncrease, "previous_priority"), @offsetOf(notifier.NotifierChainPriorityIncrease, "previous_priority"));
    try testing.expectEqual(@offsetOf(abi.NotifierChainPriorityIncrease, "current_priority"), @offsetOf(notifier.NotifierChainPriorityIncrease, "current_priority"));

    try testing.expectEqual(@sizeOf(abi.ListHead), @sizeOf(notifier.ListHead));
    try testing.expectEqual(@alignOf(abi.ListHead), @alignOf(notifier.ListHead));
    try testing.expectEqual(@offsetOf(abi.ListHead, "next"), @offsetOf(notifier.ListHead, "next"));
    try testing.expectEqual(@offsetOf(abi.ListHead, "prev"), @offsetOf(notifier.ListHead, "prev"));

    try testing.expectEqual(@sizeOf(abi.HListHead), @sizeOf(notifier.HListHead));
    try testing.expectEqual(@alignOf(abi.HListHead), @alignOf(notifier.HListHead));
    try testing.expectEqual(@offsetOf(abi.HListHead, "first"), @offsetOf(notifier.HListHead, "first"));

    try testing.expectEqual(@sizeOf(abi.HListNode), @sizeOf(notifier.HListNode));
    try testing.expectEqual(@alignOf(abi.HListNode), @alignOf(notifier.HListNode));
    try testing.expectEqual(@offsetOf(abi.HListNode, "next"), @offsetOf(notifier.HListNode, "next"));
    try testing.expectEqual(@offsetOf(abi.HListNode, "pprev"), @offsetOf(notifier.HListNode, "pprev"));
}

test "phase3 notifier layout keeps priority-increase helpers aligned with the shared ABI relays" {
    const rising_tail = notifier.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 7,
    };
    const middle = notifier.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&rising_tail),
        .priority = 4,
    };
    const head = notifier.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&middle),
        .priority = 5,
    };
    const flat_tail = notifier.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 2,
    };
    const flat_head = notifier.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&flat_tail),
        .priority = 2,
    };

    const direct = notifier.firstChainPriorityIncrease(&head) orelse return error.TestUnexpectedResult;
    const relayed = abi.firstChainPriorityIncrease(@ptrCast(&head)) orelse return error.TestUnexpectedResult;

    try testing.expect(!notifier.chainHasNonincreasingPriority(&head));
    try testing.expect(!abi.chainHasNonincreasingPriority(@ptrCast(&head)));
    try testing.expectEqual(direct.previous_index, relayed.previous_index);
    try testing.expectEqual(direct.current_index, relayed.current_index);
    try testing.expectEqual(direct.previous_priority, relayed.previous_priority);
    try testing.expectEqual(direct.current_priority, relayed.current_priority);

    try testing.expect(notifier.chainHasNonincreasingPriority(&flat_head));
    try testing.expect(abi.chainHasNonincreasingPriority(@ptrCast(&flat_head)));
    try testing.expectEqual(@as(?notifier.NotifierChainPriorityIncrease, null), notifier.firstChainPriorityIncrease(&flat_head));
    try testing.expectEqual(@as(?abi.NotifierChainPriorityIncrease, null), abi.firstChainPriorityIncrease(@ptrCast(&flat_head)));
}

test "phase3 notifier layout keeps backlink and prev-link break witnesses aligned" {
    var list_head = notifier.ListHead{ .next = 0, .prev = 0 };
    var list_first = notifier.ListHead{ .next = 0, .prev = 0 };
    var list_second = notifier.ListHead{ .next = 0, .prev = 0 };
    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_second);
    list_first.next = @intFromPtr(&list_second);
    list_first.prev = @intFromPtr(&list_head);
    list_second.next = @intFromPtr(&list_head);
    list_second.prev = @intFromPtr(&list_head);

    const list_direct = notifier.firstBrokenBacklink(&list_head) orelse return error.TestUnexpectedResult;
    const list_relayed = abi.firstBrokenBacklink(@ptrCast(&list_head)) orelse return error.TestUnexpectedResult;
    try testing.expect(!notifier.listHasConsistentBacklinks(&list_head));
    try testing.expect(!abi.listHasConsistentBacklinks(@ptrCast(&list_head)));
    try testing.expectEqual(list_direct.current_index, list_relayed.current_index);
    try testing.expectEqual(list_direct.expected_prev, list_relayed.expected_prev);
    try testing.expectEqual(list_direct.actual_prev, list_relayed.actual_prev);

    var hlist_head = notifier.HListHead{ .first = 0 };
    var hlist_first = notifier.HListNode{ .next = 0, .pprev = 0 };
    var hlist_second = notifier.HListNode{ .next = 0, .pprev = 0 };
    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_second);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_second.next = 0;
    hlist_second.pprev = @intFromPtr(&hlist_head.first);

    const hlist_direct = notifier.firstBrokenPrevLink(&hlist_head) orelse return error.TestUnexpectedResult;
    const hlist_relayed = abi.firstBrokenPrevLink(@ptrCast(&hlist_head)) orelse return error.TestUnexpectedResult;
    try testing.expect(!notifier.hlistHasConsistentPrevLinks(&hlist_head));
    try testing.expect(!abi.hlistHasConsistentPrevLinks(@ptrCast(&hlist_head)));
    try testing.expectEqual(hlist_direct.current_index, hlist_relayed.current_index);
    try testing.expectEqual(hlist_direct.expected_pprev, hlist_relayed.expected_pprev);
    try testing.expectEqual(hlist_direct.actual_pprev, hlist_relayed.actual_pprev);
}
