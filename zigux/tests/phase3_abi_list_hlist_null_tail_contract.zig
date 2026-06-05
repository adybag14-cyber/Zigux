const std = @import("std");

const abi = @import("abi_bindings");
const notifier_abi = @import("notifier_abi");

test "abi list and hlist relays keep null-head absence semantics explicit" {
    try std.testing.expectEqual(@as(?abi.ListBackLinkBreak, null), abi.firstBrokenBacklink(null));
    try std.testing.expect(!abi.listHasConsistentBacklinks(null));

    try std.testing.expect(!abi.hlistFirstPprevMatchesHead(null));
    try std.testing.expectEqual(@as(?abi.HListPrevLinkBreak, null), abi.firstBrokenPrevLink(null));
    try std.testing.expect(!abi.hlistHasConsistentPrevLinks(null));

    try std.testing.expectEqual(@as(?notifier_abi.ListBackLinkBreak, null), notifier_abi.firstBrokenBacklink(null));
    try std.testing.expect(!notifier_abi.listIsEmpty(null));
    try std.testing.expectEqual(@as(usize, 0), notifier_abi.listLength(null));
    try std.testing.expect(!notifier_abi.listHasConsistentBacklinks(null));

    try std.testing.expect(!notifier_abi.hlistIsEmpty(null));
    try std.testing.expect(!notifier_abi.firstPprevMatchesHead(null));
    try std.testing.expectEqual(@as(?notifier_abi.HListPrevLinkBreak, null), notifier_abi.firstBrokenPrevLink(null));
    try std.testing.expectEqual(@as(usize, 0), notifier_abi.hlistLength(null));
    try std.testing.expect(!notifier_abi.hlistHasConsistentPrevLinks(null));
    try std.testing.expect(!notifier_abi.hlistTailNextIsNull(null));
}

test "abi list backlink relay reports a null next pointer at the sentinel boundary" {
    var head = abi.ListHead{
        .next = 0,
        .prev = 0,
    };
    head.prev = @intFromPtr(&head);

    const abi_break = abi.firstBrokenBacklink(&head) orelse return error.TestUnexpectedResult;
    try std.testing.expect(!abi.listHasConsistentBacklinks(&head));
    try std.testing.expectEqual(@as(usize, 0), abi_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), abi_break.expected_prev);
    try std.testing.expectEqual(@as(usize, 0), abi_break.actual_prev);

    const notifier_break = notifier_abi.firstBrokenBacklink(&head) orelse return error.TestUnexpectedResult;
    try std.testing.expect(!notifier_abi.listHasConsistentBacklinks(&head));
    try std.testing.expectEqual(abi_break.current_index, notifier_break.current_index);
    try std.testing.expectEqual(abi_break.expected_prev, notifier_break.expected_prev);
    try std.testing.expectEqual(abi_break.actual_prev, notifier_break.actual_prev);
}

test "abi list relay accepts sentinel-only lists without reporting break details" {
    var head = abi.ListHead{
        .next = 0,
        .prev = 0,
    };
    head.next = @intFromPtr(&head);
    head.prev = @intFromPtr(&head);

    try std.testing.expectEqual(@as(?abi.ListBackLinkBreak, null), abi.firstBrokenBacklink(&head));
    try std.testing.expect(abi.listHasConsistentBacklinks(&head));
    try std.testing.expect(notifier_abi.listIsEmpty(&head));
    try std.testing.expectEqual(@as(usize, 0), notifier_abi.listLength(&head));
}

test "abi hlist relays keep empty, valid, and mismatched prev-link tails explicit" {
    const empty = abi.HListHead{ .first = 0 };
    try std.testing.expect(abi.hlistFirstPprevMatchesHead(&empty));
    try std.testing.expectEqual(@as(?abi.HListPrevLinkBreak, null), abi.firstBrokenPrevLink(&empty));
    try std.testing.expect(abi.hlistHasConsistentPrevLinks(&empty));
    try std.testing.expect(notifier_abi.hlistIsEmpty(&empty));
    try std.testing.expectEqual(@as(usize, 0), notifier_abi.hlistLength(&empty));
    try std.testing.expect(notifier_abi.hlistTailNextIsNull(&empty));

    var head = abi.HListHead{ .first = 0 };
    var first = abi.HListNode{ .next = 0, .pprev = 0 };
    var second = abi.HListNode{ .next = 0, .pprev = 0 };
    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = 0;
    second.pprev = @intFromPtr(&first.next);

    try std.testing.expect(abi.hlistFirstPprevMatchesHead(&head));
    try std.testing.expectEqual(@as(?abi.HListPrevLinkBreak, null), abi.firstBrokenPrevLink(&head));
    try std.testing.expect(abi.hlistHasConsistentPrevLinks(&head));
    try std.testing.expectEqual(@as(usize, 2), notifier_abi.hlistLength(&head));
    try std.testing.expect(notifier_abi.hlistTailNextIsNull(&head));

    second.pprev = @intFromPtr(&head.first);
    const breakage = abi.firstBrokenPrevLink(&head) orelse return error.TestUnexpectedResult;
    try std.testing.expect(!abi.hlistHasConsistentPrevLinks(&head));
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);
    try std.testing.expect(notifier_abi.hlistTailNextIsNull(&head));
}
