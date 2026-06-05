const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list middle bridge replacement reports staged backlink repair" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var old_left = ListHead{ .next = 0, .prev = 0 };
    var old_right = ListHead{ .next = 0, .prev = 0 };
    var bridge_left = ListHead{ .next = 0, .prev = 0 };
    var bridge_right = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&old_left);
    first.prev = @intFromPtr(&head);
    old_left.next = @intFromPtr(&old_right);
    old_left.prev = @intFromPtr(&first);
    old_right.next = @intFromPtr(&tail);
    old_right.prev = @intFromPtr(&old_left);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&old_right);

    bridge_left.next = @intFromPtr(&bridge_right);
    bridge_left.prev = @intFromPtr(&bridge_left);
    bridge_right.next = @intFromPtr(&bridge_right);
    bridge_right.prev = @intFromPtr(&bridge_left);

    first.next = @intFromPtr(&bridge_left);
    bridge_left.next = @intFromPtr(&bridge_right);
    bridge_right.next = @intFromPtr(&tail);

    const staged_view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), staged_view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &first), staged_view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), staged_view.last());
    try std.testing.expect(staged_view.contains(&bridge_left));
    try std.testing.expect(staged_view.contains(&bridge_right));
    try std.testing.expect(!staged_view.contains(&old_left));
    try std.testing.expect(!staged_view.contains(&old_right));

    const first_break = staged_view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), first_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), first_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&bridge_left)), first_break.actual_prev);

    bridge_left.prev = @intFromPtr(&first);
    const second_break = staged_view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 3), second_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&bridge_right)), second_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_right)), second_break.actual_prev);

    bridge_right.prev = @intFromPtr(&bridge_left);
    tail.prev = @intFromPtr(&bridge_right);

    try std.testing.expect(staged_view.hasConsistentBacklinks());
}

test "hlist middle bridge replacement reports staged prev-link repair" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var old_left = HListNode{ .next = 0, .pprev = 0 };
    var old_right = HListNode{ .next = 0, .pprev = 0 };
    var bridge_left = HListNode{ .next = 0, .pprev = 0 };
    var bridge_right = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&old_left);
    first.pprev = @intFromPtr(&head.first);
    old_left.next = @intFromPtr(&old_right);
    old_left.pprev = @intFromPtr(&first.next);
    old_right.next = @intFromPtr(&tail);
    old_right.pprev = @intFromPtr(&old_left.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&old_right.next);

    bridge_left.next = @intFromPtr(&bridge_right);
    bridge_left.pprev = @intFromPtr(&bridge_left.next);
    bridge_right.next = 0;
    bridge_right.pprev = @intFromPtr(&bridge_left.next);

    first.next = @intFromPtr(&bridge_left);
    bridge_left.next = @intFromPtr(&bridge_right);
    bridge_right.next = @intFromPtr(&tail);

    const staged_view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), staged_view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &first), staged_view.first());
    try std.testing.expectEqual(@as(?*const HListNode, &tail), staged_view.last());
    try std.testing.expect(staged_view.firstPprevMatchesHead());
    try std.testing.expect(staged_view.tailNextIsNull());
    try std.testing.expect(staged_view.contains(&bridge_left));
    try std.testing.expect(staged_view.contains(&bridge_right));
    try std.testing.expect(!staged_view.contains(&old_left));
    try std.testing.expect(!staged_view.contains(&old_right));

    const first_break = staged_view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), first_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), first_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&bridge_left.next)), first_break.actual_pprev);

    bridge_left.pprev = @intFromPtr(&first.next);
    const second_break = staged_view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 3), second_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&bridge_right.next)), second_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_right.next)), second_break.actual_pprev);

    bridge_right.pprev = @intFromPtr(&bridge_left.next);
    tail.pprev = @intFromPtr(&bridge_right.next);

    try std.testing.expect(staged_view.hasConsistentPrevLinks());
}
