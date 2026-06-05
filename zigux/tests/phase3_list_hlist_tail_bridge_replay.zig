const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list tail bridge replacement reports staged backlink repair" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var retained = ListHead{ .next = 0, .prev = 0 };
    var old_left = ListHead{ .next = 0, .prev = 0 };
    var old_right = ListHead{ .next = 0, .prev = 0 };
    var bridge_left = ListHead{ .next = 0, .prev = 0 };
    var bridge_right = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&retained);
    head.prev = @intFromPtr(&old_right);
    retained.next = @intFromPtr(&old_left);
    retained.prev = @intFromPtr(&head);
    old_left.next = @intFromPtr(&old_right);
    old_left.prev = @intFromPtr(&retained);
    old_right.next = @intFromPtr(&head);
    old_right.prev = @intFromPtr(&old_left);

    bridge_left.next = @intFromPtr(&bridge_right);
    bridge_left.prev = @intFromPtr(&bridge_left);
    bridge_right.next = @intFromPtr(&head);
    bridge_right.prev = @intFromPtr(&bridge_left);

    retained.next = @intFromPtr(&bridge_left);
    bridge_right.next = @intFromPtr(&head);

    const staged_view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), staged_view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &retained), staged_view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &old_right), staged_view.last());
    try std.testing.expect(!staged_view.isSingular());
    try std.testing.expect(staged_view.contains(&retained));
    try std.testing.expect(staged_view.contains(&bridge_left));
    try std.testing.expect(staged_view.contains(&bridge_right));
    try std.testing.expect(!staged_view.contains(&old_left));
    try std.testing.expect(!staged_view.contains(&old_right));

    const bridge_break = staged_view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), bridge_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&retained)), bridge_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&bridge_left)), bridge_break.actual_prev);

    bridge_left.prev = @intFromPtr(&retained);
    const sentinel_break = staged_view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 3), sentinel_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&bridge_right)), sentinel_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_right)), sentinel_break.actual_prev);

    head.prev = @intFromPtr(&bridge_right);

    try std.testing.expectEqual(@as(?*const ListHead, &bridge_right), staged_view.last());
    try std.testing.expect(staged_view.hasConsistentBacklinks());
}

test "hlist tail bridge replacement reports staged prev-link repair" {
    var head = HListHead{ .first = 0 };
    var retained = HListNode{ .next = 0, .pprev = 0 };
    var old_left = HListNode{ .next = 0, .pprev = 0 };
    var old_right = HListNode{ .next = 0, .pprev = 0 };
    var bridge_left = HListNode{ .next = 0, .pprev = 0 };
    var bridge_right = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&retained);
    retained.next = @intFromPtr(&old_left);
    retained.pprev = @intFromPtr(&head.first);
    old_left.next = @intFromPtr(&old_right);
    old_left.pprev = @intFromPtr(&retained.next);
    old_right.next = 0;
    old_right.pprev = @intFromPtr(&old_left.next);

    bridge_left.next = @intFromPtr(&bridge_right);
    bridge_left.pprev = @intFromPtr(&bridge_left.next);
    bridge_right.next = 0;
    bridge_right.pprev = @intFromPtr(&old_right.next);

    retained.next = @intFromPtr(&bridge_left);

    const staged_view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), staged_view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &retained), staged_view.first());
    try std.testing.expectEqual(@as(?*const HListNode, &bridge_right), staged_view.last());
    try std.testing.expect(!staged_view.isSingular());
    try std.testing.expect(staged_view.firstPprevMatchesHead());
    try std.testing.expect(staged_view.tailNextIsNull());
    try std.testing.expect(staged_view.contains(&retained));
    try std.testing.expect(staged_view.contains(&bridge_left));
    try std.testing.expect(staged_view.contains(&bridge_right));
    try std.testing.expect(!staged_view.contains(&old_left));
    try std.testing.expect(!staged_view.contains(&old_right));

    const bridge_break = staged_view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), bridge_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&retained.next)), bridge_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&bridge_left.next)), bridge_break.actual_pprev);

    bridge_left.pprev = @intFromPtr(&retained.next);
    const tail_break = staged_view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), tail_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&bridge_left.next)), tail_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_right.next)), tail_break.actual_pprev);

    bridge_right.pprev = @intFromPtr(&bridge_left.next);

    try std.testing.expect(staged_view.hasConsistentPrevLinks());
}
