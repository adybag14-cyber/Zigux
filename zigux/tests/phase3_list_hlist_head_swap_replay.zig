const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

fn ptrOf(value: anytype) usize {
    return @intFromPtr(value);
}

test "list view reports stale head-swap backlinks before repair" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var replacement_first = ListHead{ .next = 0, .prev = 0 };
    var replacement_second = ListHead{ .next = 0, .prev = 0 };
    var old_first = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };

    head.next = ptrOf(&replacement_first);
    head.prev = ptrOf(&tail);
    replacement_first.next = ptrOf(&replacement_second);
    replacement_first.prev = 0;
    replacement_second.next = ptrOf(&old_first);
    replacement_second.prev = 0;
    old_first.next = ptrOf(&tail);
    old_first.prev = ptrOf(&head);
    tail.next = ptrOf(&head);
    tail.prev = ptrOf(&old_first);

    const view = ListView.init(&head);
    try std.testing.expectEqual(@as(?*const ListHead, &replacement_first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), view.last());
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expect(!view.hasConsistentBacklinks());

    const first_break = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), first_break.current_index);
    try std.testing.expectEqual(ptrOf(&head), first_break.expected_prev);
    try std.testing.expectEqual(@as(usize, 0), first_break.actual_prev);
}

test "list view accepts repaired head-swap chain shape" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var replacement_first = ListHead{ .next = 0, .prev = 0 };
    var replacement_second = ListHead{ .next = 0, .prev = 0 };
    var old_first = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };

    head.next = ptrOf(&replacement_first);
    head.prev = ptrOf(&tail);
    replacement_first.next = ptrOf(&replacement_second);
    replacement_first.prev = ptrOf(&head);
    replacement_second.next = ptrOf(&old_first);
    replacement_second.prev = ptrOf(&replacement_first);
    old_first.next = ptrOf(&tail);
    old_first.prev = ptrOf(&replacement_second);
    tail.next = ptrOf(&head);
    tail.prev = ptrOf(&old_first);

    const view = ListView.init(&head);
    try std.testing.expectEqual(@as(?*const ListHead, &replacement_first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), view.last());
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "hlist view reports stale head-swap prev links before repair" {
    var head = HListHead{ .first = 0 };
    var replacement_first = HListNode{ .next = 0, .pprev = 0 };
    var replacement_second = HListNode{ .next = 0, .pprev = 0 };
    var old_first = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };

    head.first = ptrOf(&replacement_first);
    replacement_first.next = ptrOf(&replacement_second);
    replacement_first.pprev = 0;
    replacement_second.next = ptrOf(&old_first);
    replacement_second.pprev = 0;
    old_first.next = ptrOf(&tail);
    old_first.pprev = ptrOf(&head.first);
    tail.next = 0;
    tail.pprev = ptrOf(&old_first.next);

    const view = HListView.init(&head);
    try std.testing.expectEqual(@as(?*const HListNode, &replacement_first), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, &tail), view.last());
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expect(!view.firstPprevMatchesHead());
    try std.testing.expect(!view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());

    const first_break = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), first_break.current_index);
    try std.testing.expectEqual(ptrOf(&head.first), first_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, 0), first_break.actual_pprev);
}

test "hlist view accepts repaired head-swap chain shape" {
    var head = HListHead{ .first = 0 };
    var replacement_first = HListNode{ .next = 0, .pprev = 0 };
    var replacement_second = HListNode{ .next = 0, .pprev = 0 };
    var old_first = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };

    head.first = ptrOf(&replacement_first);
    replacement_first.next = ptrOf(&replacement_second);
    replacement_first.pprev = ptrOf(&head.first);
    replacement_second.next = ptrOf(&old_first);
    replacement_second.pprev = ptrOf(&replacement_first.next);
    old_first.next = ptrOf(&tail);
    old_first.pprev = ptrOf(&replacement_second.next);
    tail.next = 0;
    tail.pprev = ptrOf(&old_first.next);

    const view = HListView.init(&head);
    try std.testing.expectEqual(@as(?*const HListNode, &replacement_first), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, &tail), view.last());
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try std.testing.expect(view.tailNextIsNull());
}
