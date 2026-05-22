const std = @import("std");
const testing = std.testing;

const notifier_abi = @import("notifier_abi");
const list_view = @import("list_view");

fn asListViewHead(head: *const notifier_abi.ListHead) *const list_view.ListHead {
    return @ptrCast(head);
}

test "notifier/list starter packet keeps notifier priority witnesses explicit" {
    const tail = notifier_abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 8,
    };
    const head = notifier_abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&tail),
        .priority = 2,
    };

    const increase = notifier_abi.firstChainPriorityIncrease(&head) orelse return error.TestUnexpectedResult;
    try testing.expect(!notifier_abi.chainHasNonincreasingPriority(&head));
    try testing.expectEqual(@as(usize, 0), increase.previous_index);
    try testing.expectEqual(@as(usize, 1), increase.current_index);
    try testing.expectEqual(@as(i32, 2), increase.previous_priority);
    try testing.expectEqual(@as(i32, 8), increase.current_priority);
}

test "notifier/list starter packet keeps notifier list_head layout aligned with list view" {
    try testing.expectEqual(@sizeOf(notifier_abi.ListHead), @sizeOf(list_view.ListHead));
    try testing.expectEqual(@alignOf(notifier_abi.ListHead), @alignOf(list_view.ListHead));
    try testing.expectEqual(@offsetOf(notifier_abi.ListHead, "next"), @offsetOf(list_view.ListHead, "next"));
    try testing.expectEqual(@offsetOf(notifier_abi.ListHead, "prev"), @offsetOf(list_view.ListHead, "prev"));

    try testing.expectEqual(@sizeOf(notifier_abi.ListBackLinkBreak), @sizeOf(list_view.BackLinkBreak));
    try testing.expectEqual(@alignOf(notifier_abi.ListBackLinkBreak), @alignOf(list_view.BackLinkBreak));
    try testing.expectEqual(
        @offsetOf(notifier_abi.ListBackLinkBreak, "current_index"),
        @offsetOf(list_view.BackLinkBreak, "current_index"),
    );
    try testing.expectEqual(
        @offsetOf(notifier_abi.ListBackLinkBreak, "expected_prev"),
        @offsetOf(list_view.BackLinkBreak, "expected_prev"),
    );
    try testing.expectEqual(
        @offsetOf(notifier_abi.ListBackLinkBreak, "actual_prev"),
        @offsetOf(list_view.BackLinkBreak, "actual_prev"),
    );
}

test "notifier/list starter packet keeps sentinel emptiness and backlink parity aligned" {
    var head = notifier_abi.ListHead{ .next = 0, .prev = 0 };
    head.next = @intFromPtr(&head);
    head.prev = @intFromPtr(&head);

    const notifier_break = notifier_abi.firstBrokenBacklink(&head);
    const view = list_view.ListView.init(asListViewHead(&head));

    try testing.expectEqual(@as(?notifier_abi.ListBackLinkBreak, null), notifier_break);
    try testing.expect(notifier_abi.listHasConsistentBacklinks(&head));
    try testing.expect(view.isEmpty());
    try testing.expect(view.hasConsistentBacklinks());
    try testing.expectEqual(@as(?list_view.BackLinkBreak, null), view.firstBrokenBacklink());
}

test "notifier/list starter packet reports the same first broken backlink witness" {
    var head = notifier_abi.ListHead{ .next = 0, .prev = 0 };
    var first = notifier_abi.ListHead{ .next = 0, .prev = 0 };
    var second = notifier_abi.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&second);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&head);
    second.prev = @intFromPtr(&head);

    const notifier_break = notifier_abi.firstBrokenBacklink(&head) orelse return error.TestUnexpectedResult;
    const view_break = list_view.ListView.init(asListViewHead(&head)).firstBrokenBacklink() orelse
        return error.TestUnexpectedResult;

    try testing.expect(!notifier_abi.listHasConsistentBacklinks(&head));
    try testing.expect(!list_view.ListView.init(asListViewHead(&head)).hasConsistentBacklinks());
    try testing.expectEqual(notifier_break.current_index, view_break.current_index);
    try testing.expectEqual(notifier_break.expected_prev, view_break.expected_prev);
    try testing.expectEqual(notifier_break.actual_prev, view_break.actual_prev);
}
