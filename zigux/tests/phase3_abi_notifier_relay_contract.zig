const std = @import("std");

const abi = @import("abi_bindings");

test "phase3 abi exposes notifier result relay values" {
    try std.testing.expectEqual(@as(u32, abi.NOTIFIER_DONE), @intFromEnum(abi.NotifierResult.done));
    try std.testing.expectEqual(@as(u32, abi.NOTIFIER_OK), @intFromEnum(abi.NotifierResult.ok));
    try std.testing.expectEqual(@as(u32, abi.NOTIFIER_STOP), @intFromEnum(abi.NotifierResult.stop));

    try std.testing.expectEqual(@as(?abi.NotifierResult, .done), abi.notifierResultFromInt(abi.NOTIFIER_DONE));
    try std.testing.expectEqual(@as(?abi.NotifierResult, .ok), abi.notifierResultFromInt(abi.NOTIFIER_OK));
    try std.testing.expectEqual(@as(?abi.NotifierResult, .stop), abi.notifierResultFromInt(abi.NOTIFIER_STOP));
    try std.testing.expectEqual(@as(?abi.NotifierResult, null), abi.notifierResultFromInt(7));

    try std.testing.expect(!abi.notifierResultStopsChainValue(abi.NOTIFIER_DONE));
    try std.testing.expect(!abi.notifierResultStopsChainValue(abi.NOTIFIER_OK));
    try std.testing.expect(abi.notifierResultStopsChainValue(abi.NOTIFIER_STOP));
    try std.testing.expect(!abi.notifierResultStopsChainValue(7));
    try std.testing.expect(abi.notifierResultStopsChain(.stop));
}

test "phase3 abi exposes notifier chain priority increase witnesses" {
    const third = abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 9,
    };
    const second = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&third),
        .priority = 3,
    };
    const first = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&second),
        .priority = 8,
    };

    const increase = abi.firstChainPriorityIncrease(&first) orelse return error.TestUnexpectedResult;
    try std.testing.expect(!abi.chainHasNonincreasingPriority(&first));
    try std.testing.expectEqual(@as(usize, 1), increase.previous_index);
    try std.testing.expectEqual(@as(usize, 2), increase.current_index);
    try std.testing.expectEqual(@as(i32, 3), increase.previous_priority);
    try std.testing.expectEqual(@as(i32, 9), increase.current_priority);
}

test "phase3 abi exposes list backlink relay witnesses" {
    var head = abi.ListHead{ .next = 0, .prev = 0 };
    var first = abi.ListHead{ .next = 0, .prev = 0 };
    var second = abi.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&second);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&head);
    second.prev = @intFromPtr(&head);

    const breakage = abi.firstBrokenBacklink(&head) orelse return error.TestUnexpectedResult;
    try std.testing.expect(!abi.listHasConsistentBacklinks(&head));
    try std.testing.expect(!abi.listHasConsistentBacklinks(null));
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);
}

test "phase3 abi exposes hlist prev-link relay witnesses" {
    var head = abi.HListHead{ .first = 0 };
    var first = abi.HListNode{ .next = 0, .pprev = 0 };
    var second = abi.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = 0;
    second.pprev = @intFromPtr(&head.first);

    const breakage = abi.firstBrokenPrevLink(&head) orelse return error.TestUnexpectedResult;
    try std.testing.expect(!abi.hlistHasConsistentPrevLinks(&head));
    try std.testing.expect(!abi.hlistHasConsistentPrevLinks(null));
    try std.testing.expect(abi.hlistFirstPprevMatchesHead(&head));
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);
}
