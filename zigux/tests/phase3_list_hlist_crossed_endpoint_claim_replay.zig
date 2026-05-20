const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list view ignores detached nodes that cross-claim opposite endpoints" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var middle = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };
    var detached_tail_claim = ListHead{ .next = 0, .prev = 0 };
    var detached_head_claim = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&middle);
    first.prev = @intFromPtr(&head);
    middle.next = @intFromPtr(&tail);
    middle.prev = @intFromPtr(&first);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&middle);

    // This detached pair cross-claims the exposed endpoint slots in the reverse
    // order from the live route without joining the head-rooted chain.
    detached_tail_claim.next = @intFromPtr(&head);
    detached_tail_claim.prev = @intFromPtr(&detached_head_claim);
    detached_head_claim.next = @intFromPtr(&detached_tail_claim);
    detached_head_claim.prev = @intFromPtr(&head);

    const view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const ListHead, &first), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &middle), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());
}

test "hlist view ignores detached nodes that cross-claim opposite endpoints" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var middle = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };
    var detached_tail_claim = HListNode{ .next = 0, .pprev = 0 };
    var detached_head_claim = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&middle);
    first.pprev = @intFromPtr(&head.first);
    middle.next = @intFromPtr(&tail);
    middle.pprev = @intFromPtr(&first.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&middle.next);

    detached_tail_claim.next = 0;
    detached_tail_claim.pprev = @intFromPtr(&detached_head_claim.next);
    detached_head_claim.next = @intFromPtr(&detached_tail_claim);
    detached_head_claim.pprev = @intFromPtr(&head.first);

    const view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &first), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try std.testing.expect(view.tailNextIsNull());

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const HListNode, &first), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &middle), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &tail), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, null), it.next());
}

test "crossed endpoint claims stay detached while the live route remains authoritative" {
    var list_head = ListHead{ .next = 0, .prev = 0 };
    var list_first = ListHead{ .next = 0, .prev = 0 };
    var list_middle = ListHead{ .next = 0, .prev = 0 };
    var list_tail = ListHead{ .next = 0, .prev = 0 };
    var list_detached_tail_claim = ListHead{ .next = 0, .prev = 0 };
    var list_detached_head_claim = ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_tail);
    list_first.next = @intFromPtr(&list_middle);
    list_first.prev = @intFromPtr(&list_head);
    list_middle.next = @intFromPtr(&list_tail);
    list_middle.prev = @intFromPtr(&list_first);
    list_tail.next = @intFromPtr(&list_head);
    list_tail.prev = @intFromPtr(&list_middle);
    list_detached_tail_claim.next = @intFromPtr(&list_head);
    list_detached_tail_claim.prev = @intFromPtr(&list_detached_head_claim);
    list_detached_head_claim.next = @intFromPtr(&list_detached_tail_claim);
    list_detached_head_claim.prev = @intFromPtr(&list_head);

    const list_result = ListView.init(&list_head);
    try std.testing.expectEqual(@as(usize, 3), list_result.len());
    try std.testing.expectEqual(@as(?*const ListHead, &list_tail), list_result.last());
    try std.testing.expect(list_result.hasConsistentBacklinks());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_head)), list_detached_tail_claim.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_head)), list_detached_head_claim.prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_middle)), list_tail.prev);

    var hlist_head = HListHead{ .first = 0 };
    var hlist_first = HListNode{ .next = 0, .pprev = 0 };
    var hlist_middle = HListNode{ .next = 0, .pprev = 0 };
    var hlist_tail = HListNode{ .next = 0, .pprev = 0 };
    var hlist_detached_tail_claim = HListNode{ .next = 0, .pprev = 0 };
    var hlist_detached_head_claim = HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_middle);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_middle.next = @intFromPtr(&hlist_tail);
    hlist_middle.pprev = @intFromPtr(&hlist_first.next);
    hlist_tail.next = 0;
    hlist_tail.pprev = @intFromPtr(&hlist_middle.next);
    hlist_detached_tail_claim.next = 0;
    hlist_detached_tail_claim.pprev = @intFromPtr(&hlist_detached_head_claim.next);
    hlist_detached_head_claim.next = @intFromPtr(&hlist_detached_tail_claim);
    hlist_detached_head_claim.pprev = @intFromPtr(&hlist_head.first);

    const hlist_result = HListView.init(&hlist_head);
    try std.testing.expectEqual(@as(usize, 3), hlist_result.len());
    try std.testing.expect(hlist_result.firstPprevMatchesHead());
    try std.testing.expect(hlist_result.hasConsistentPrevLinks());
    try std.testing.expect(hlist_result.tailNextIsNull());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_head.first)), hlist_detached_head_claim.pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_detached_head_claim.next)), hlist_detached_tail_claim.pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_middle.next)), hlist_tail.pprev);
}
