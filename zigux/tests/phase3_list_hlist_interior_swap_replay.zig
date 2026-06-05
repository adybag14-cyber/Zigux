const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list interior swap reports staged backlink repair" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var left = ListHead{ .next = 0, .prev = 0 };
    var right = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&left);
    first.prev = @intFromPtr(&head);
    left.next = @intFromPtr(&right);
    left.prev = @intFromPtr(&first);
    right.next = @intFromPtr(&tail);
    right.prev = @intFromPtr(&left);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&right);

    first.next = @intFromPtr(&right);
    right.next = @intFromPtr(&left);
    left.next = @intFromPtr(&tail);

    const staged_view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), staged_view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &first), staged_view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), staged_view.last());
    try std.testing.expect(!staged_view.isSingular());
    try std.testing.expect(staged_view.contains(&first));
    try std.testing.expect(staged_view.contains(&right));
    try std.testing.expect(staged_view.contains(&left));
    try std.testing.expect(staged_view.contains(&tail));

    var it = staged_view.iterator();
    try std.testing.expectEqual(@as(?*const ListHead, &first), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &right), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &left), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());

    const right_break = staged_view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), right_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), right_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&left)), right_break.actual_prev);

    right.prev = @intFromPtr(&first);
    const left_break = staged_view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), left_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&right)), left_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), left_break.actual_prev);

    left.prev = @intFromPtr(&right);
    const tail_break = staged_view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 3), tail_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&left)), tail_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&right)), tail_break.actual_prev);

    tail.prev = @intFromPtr(&left);

    try std.testing.expect(staged_view.hasConsistentBacklinks());
}

test "hlist interior swap reports staged prev-link repair" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var left = HListNode{ .next = 0, .pprev = 0 };
    var right = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&left);
    first.pprev = @intFromPtr(&head.first);
    left.next = @intFromPtr(&right);
    left.pprev = @intFromPtr(&first.next);
    right.next = @intFromPtr(&tail);
    right.pprev = @intFromPtr(&left.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&right.next);

    first.next = @intFromPtr(&right);
    right.next = @intFromPtr(&left);
    left.next = @intFromPtr(&tail);

    const staged_view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), staged_view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &first), staged_view.first());
    try std.testing.expectEqual(@as(?*const HListNode, &tail), staged_view.last());
    try std.testing.expect(!staged_view.isSingular());
    try std.testing.expect(staged_view.firstPprevMatchesHead());
    try std.testing.expect(staged_view.tailNextIsNull());
    try std.testing.expect(staged_view.contains(&first));
    try std.testing.expect(staged_view.contains(&right));
    try std.testing.expect(staged_view.contains(&left));
    try std.testing.expect(staged_view.contains(&tail));

    var it = staged_view.iterator();
    try std.testing.expectEqual(@as(?*const HListNode, &first), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &right), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &left), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &tail), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, null), it.next());

    const right_break = staged_view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), right_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), right_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&left.next)), right_break.actual_pprev);

    right.pprev = @intFromPtr(&first.next);
    const left_break = staged_view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), left_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&right.next)), left_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), left_break.actual_pprev);

    left.pprev = @intFromPtr(&right.next);
    const tail_break = staged_view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 3), tail_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&left.next)), tail_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&right.next)), tail_break.actual_pprev);

    tail.pprev = @intFromPtr(&left.next);

    try std.testing.expect(staged_view.hasConsistentPrevLinks());
}
