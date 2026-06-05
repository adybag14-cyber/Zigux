const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list view exposes dual-pop append before and after backlink repair" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var popped = ListHead{ .next = 0, .prev = 0 };
    var kept = ListHead{ .next = 0, .prev = 0 };
    var appended = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&popped);
    head.prev = @intFromPtr(&kept);
    popped.next = @intFromPtr(&kept);
    popped.prev = @intFromPtr(&head);
    kept.next = @intFromPtr(&head);
    kept.prev = @intFromPtr(&popped);
    appended.next = @intFromPtr(&appended);
    appended.prev = @intFromPtr(&appended);

    head.next = @intFromPtr(&kept);
    kept.prev = @intFromPtr(&head);
    popped.next = @intFromPtr(&popped);
    popped.prev = @intFromPtr(&popped);

    kept.next = @intFromPtr(&appended);
    appended.next = @intFromPtr(&head);
    head.prev = @intFromPtr(&appended);
    appended.prev = @intFromPtr(&head);

    var stale = ListView.init(&head);
    try std.testing.expect(!stale.isEmpty());
    try std.testing.expect(!stale.isSingular());
    try std.testing.expectEqual(@as(usize, 2), stale.len());
    try std.testing.expectEqual(@as(?*const ListHead, &kept), stale.first());
    try std.testing.expectEqual(@as(?*const ListHead, &appended), stale.last());
    try std.testing.expect(stale.contains(&kept));
    try std.testing.expect(stale.contains(&appended));
    try std.testing.expect(!stale.contains(&popped));

    const breakage = stale.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&kept)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);
    try std.testing.expect(!stale.hasConsistentBacklinks());

    appended.prev = @intFromPtr(&kept);

    const repaired = ListView.init(&head);
    try std.testing.expect(repaired.hasConsistentBacklinks());
    try std.testing.expect(repaired.firstBrokenBacklink() == null);

    var it = repaired.iterator();
    try std.testing.expectEqual(@as(?*const ListHead, &kept), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &appended), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());
}

test "hlist view exposes dual-pop append before and after prev-link repair" {
    var head = HListHead{ .first = 0 };
    var popped = HListNode{ .next = 0, .pprev = 0 };
    var kept = HListNode{ .next = 0, .pprev = 0 };
    var appended = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&popped);
    popped.next = @intFromPtr(&kept);
    popped.pprev = @intFromPtr(&head.first);
    kept.next = 0;
    kept.pprev = @intFromPtr(&popped.next);
    appended.next = 0;
    appended.pprev = 0;

    head.first = @intFromPtr(&kept);
    kept.pprev = @intFromPtr(&head.first);
    popped.next = 0;
    popped.pprev = 0;

    kept.next = @intFromPtr(&appended);
    appended.next = 0;
    appended.pprev = @intFromPtr(&head.first);

    var stale = HListView.init(&head);
    try std.testing.expect(!stale.isEmpty());
    try std.testing.expect(!stale.isSingular());
    try std.testing.expectEqual(@as(usize, 2), stale.len());
    try std.testing.expectEqual(@as(?*const HListNode, &kept), stale.first());
    try std.testing.expectEqual(@as(?*const HListNode, &appended), stale.last());
    try std.testing.expect(stale.firstPprevMatchesHead());
    try std.testing.expect(stale.tailNextIsNull());
    try std.testing.expect(stale.contains(&kept));
    try std.testing.expect(stale.contains(&appended));
    try std.testing.expect(!stale.contains(&popped));

    const breakage = stale.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&kept.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);
    try std.testing.expect(!stale.hasConsistentPrevLinks());

    appended.pprev = @intFromPtr(&kept.next);

    const repaired = HListView.init(&head);
    try std.testing.expect(repaired.hasConsistentPrevLinks());
    try std.testing.expect(repaired.firstBrokenPrevLink() == null);

    var it = repaired.iterator();
    try std.testing.expectEqual(@as(?*const HListNode, &kept), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &appended), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, null), it.next());
}
