const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list view reports closed-cycle endpoint drift before tail repair" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var second = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&second);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&head);
    second.prev = @intFromPtr(&first);

    var view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &second), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());

    second.next = @intFromPtr(&first);
    first.prev = @intFromPtr(&second);

    view = ListView.init(&head);
    try std.testing.expectEqual(@as(?*const ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &second), view.last());
    try std.testing.expect(!view.hasConsistentBacklinks());

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&second)), breakage.actual_prev);

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const ListHead, &first), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &second), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &first), it.next());

    second.next = @intFromPtr(&head);
    first.prev = @intFromPtr(&head);

    view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &second), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "hlist view reports closed-cycle tail drift before null repair" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var second = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = 0;
    second.pprev = @intFromPtr(&first.next);

    var view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &first), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, &second), view.last());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());

    second.next = @intFromPtr(&first);
    first.pprev = @intFromPtr(&second.next);

    view = HListView.init(&head);
    try std.testing.expectEqual(@as(?*const HListNode, &first), view.first());
    try std.testing.expect(!view.firstPprevMatchesHead());
    try std.testing.expect(!view.hasConsistentPrevLinks());

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&second.next)), breakage.actual_pprev);

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const HListNode, &first), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &second), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &first), it.next());

    second.next = 0;
    first.pprev = @intFromPtr(&head.first);

    view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &second), view.last());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
}
