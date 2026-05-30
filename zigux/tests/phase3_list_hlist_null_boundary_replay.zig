const std = @import("std");

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list null forward head remains malformed while empty hlist is valid" {
    var list_head = ListHead{ .next = 0, .prev = 0 };
    list_head.prev = @intFromPtr(&list_head);

    const list = ListView.init(&list_head);
    try std.testing.expect(!list.isEmpty());
    try std.testing.expectEqual(@as(usize, 0), list.len());
    try std.testing.expectEqual(@as(?*const ListHead, null), list.first());
    try std.testing.expectEqual(@as(?*const ListHead, null), list.last());
    try std.testing.expect(!list.hasConsistentBacklinks());

    const list_break = list.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), list_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_head)), list_break.expected_prev);
    try std.testing.expectEqual(@as(usize, 0), list_break.actual_prev);

    const hlist_head = HListHead{ .first = 0 };
    const hlist = HListView.init(&hlist_head);
    try std.testing.expect(hlist.isEmpty());
    try std.testing.expectEqual(@as(usize, 0), hlist.len());
    try std.testing.expectEqual(@as(?*const HListNode, null), hlist.first());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.firstBrokenPrevLink() == null);
    try std.testing.expect(hlist.tailNextIsNull());
}

test "hlist visible null pprev is repaired independently of its null tail" {
    var head = HListHead{ .first = 0 };
    var node = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&node);

    var view = HListView.init(&head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 1), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &node), view.first());
    try std.testing.expect(view.tailNextIsNull());
    try std.testing.expect(!view.firstPprevMatchesHead());
    try std.testing.expect(!view.hasConsistentPrevLinks());

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, 0), breakage.actual_pprev);

    node.pprev = @intFromPtr(&head.first);
    view = HListView.init(&head);
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try std.testing.expect(view.tailNextIsNull());
}
