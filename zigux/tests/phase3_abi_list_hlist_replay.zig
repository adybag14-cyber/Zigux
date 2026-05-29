const std = @import("std");

const abi = @import("abi_bindings");

test "phase3 abi replays list and hlist relay edge cases through shared bindings" {
    var list_head = abi.ListHead{ .next = 0, .prev = 0 };
    var list_first = abi.ListHead{ .next = 0, .prev = 0 };
    var list_second = abi.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_second);
    list_first.next = @intFromPtr(&list_second);
    list_first.prev = @intFromPtr(&list_head);
    list_second.next = @intFromPtr(&list_head);
    list_second.prev = @intFromPtr(&list_first);

    try std.testing.expect(abi.listHasConsistentBacklinks(&list_head));
    try std.testing.expectEqual(@as(?abi.ListBackLinkBreak, null), abi.firstBrokenBacklink(&list_head));

    list_second.prev = @intFromPtr(&list_head);
    const list_break = abi.firstBrokenBacklink(&list_head) orelse return error.TestUnexpectedResult;
    try std.testing.expect(!abi.listHasConsistentBacklinks(&list_head));
    try std.testing.expectEqual(@as(usize, 1), list_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_first)), list_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_head)), list_break.actual_prev);

    var hlist_head = abi.HListHead{ .first = 0 };
    var hlist_first = abi.HListNode{ .next = 0, .pprev = 0 };
    var hlist_second = abi.HListNode{ .next = 0, .pprev = 0 };

    try std.testing.expect(abi.hlistFirstPprevMatchesHead(&hlist_head));
    try std.testing.expect(abi.hlistHasConsistentPrevLinks(&hlist_head));

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_second);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_second.next = 0;
    hlist_second.pprev = @intFromPtr(&hlist_first.next);

    try std.testing.expect(abi.hlistFirstPprevMatchesHead(&hlist_head));
    try std.testing.expect(abi.hlistHasConsistentPrevLinks(&hlist_head));
    try std.testing.expectEqual(@as(?abi.HListPrevLinkBreak, null), abi.firstBrokenPrevLink(&hlist_head));

    hlist_first.pprev = @intFromPtr(&hlist_first.next);
    const first_link_break = abi.firstBrokenPrevLink(&hlist_head) orelse return error.TestUnexpectedResult;
    try std.testing.expect(!abi.hlistFirstPprevMatchesHead(&hlist_head));
    try std.testing.expect(!abi.hlistHasConsistentPrevLinks(&hlist_head));
    try std.testing.expectEqual(@as(usize, 0), first_link_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_head.first)), first_link_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_first.next)), first_link_break.actual_pprev);
}
