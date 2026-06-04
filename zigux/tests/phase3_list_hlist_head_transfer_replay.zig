const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

fn initListPair(head: *ListHead, first: *ListHead, second: *ListHead) void {
    head.next = @intFromPtr(first);
    head.prev = @intFromPtr(second);
    first.next = @intFromPtr(second);
    first.prev = @intFromPtr(head);
    second.next = @intFromPtr(head);
    second.prev = @intFromPtr(first);
}

fn initListSingle(head: *ListHead, only: *ListHead) void {
    head.next = @intFromPtr(only);
    head.prev = @intFromPtr(only);
    only.next = @intFromPtr(head);
    only.prev = @intFromPtr(head);
}

fn initHListPair(head: *HListHead, first: *HListNode, second: *HListNode) void {
    head.first = @intFromPtr(first);
    first.next = @intFromPtr(second);
    first.pprev = @intFromPtr(&head.first);
    second.next = 0;
    second.pprev = @intFromPtr(&first.next);
}

fn initHListSingle(head: *HListHead, only: *HListNode) void {
    head.first = @intFromPtr(only);
    only.next = 0;
    only.pprev = @intFromPtr(&head.first);
}

test "list view reports adopted head transfer before and after backlink repair" {
    var source_head = ListHead{ .next = 0, .prev = 0 };
    var dest_head = ListHead{ .next = 0, .prev = 0 };
    var moved = ListHead{ .next = 0, .prev = 0 };
    var source_tail = ListHead{ .next = 0, .prev = 0 };
    var dest_tail = ListHead{ .next = 0, .prev = 0 };

    initListPair(&source_head, &moved, &source_tail);
    initListSingle(&dest_head, &dest_tail);

    source_head.next = @intFromPtr(&source_tail);
    source_head.prev = @intFromPtr(&source_tail);
    source_tail.prev = @intFromPtr(&source_head);

    dest_head.next = @intFromPtr(&moved);
    dest_head.prev = @intFromPtr(&dest_tail);
    moved.next = @intFromPtr(&dest_tail);
    dest_tail.next = @intFromPtr(&dest_head);

    const source_after_detach = ListView.init(&source_head);
    try std.testing.expectEqual(@as(?*const ListHead, &source_tail), source_after_detach.first());
    try std.testing.expectEqual(@as(usize, 1), source_after_detach.len());
    try std.testing.expect(!source_after_detach.contains(&moved));
    try std.testing.expect(source_after_detach.hasConsistentBacklinks());

    const stale_dest = ListView.init(&dest_head);
    try std.testing.expectEqual(@as(?*const ListHead, &moved), stale_dest.first());
    try std.testing.expectEqual(@as(?*const ListHead, &dest_tail), stale_dest.last());
    try std.testing.expectEqual(@as(usize, 2), stale_dest.len());
    try std.testing.expect(stale_dest.contains(&moved));
    try std.testing.expect(stale_dest.contains(&dest_tail));

    const stale_break = stale_dest.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), stale_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&dest_head)), stale_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&source_head)), stale_break.actual_prev);

    moved.prev = @intFromPtr(&dest_head);
    dest_tail.prev = @intFromPtr(&moved);

    const repaired_dest = ListView.init(&dest_head);
    try std.testing.expect(repaired_dest.hasConsistentBacklinks());
    try std.testing.expect(!repaired_dest.isSingular());
    try std.testing.expectEqual(@as(?*const ListHead, &moved), repaired_dest.first());
    try std.testing.expectEqual(@as(?*const ListHead, &dest_tail), repaired_dest.last());
}

test "hlist view reports adopted head transfer before and after prev-link repair" {
    var source_head = HListHead{ .first = 0 };
    var dest_head = HListHead{ .first = 0 };
    var moved = HListNode{ .next = 0, .pprev = 0 };
    var source_tail = HListNode{ .next = 0, .pprev = 0 };
    var dest_tail = HListNode{ .next = 0, .pprev = 0 };

    initHListPair(&source_head, &moved, &source_tail);
    initHListSingle(&dest_head, &dest_tail);

    source_head.first = @intFromPtr(&source_tail);
    source_tail.pprev = @intFromPtr(&source_head.first);

    dest_head.first = @intFromPtr(&moved);
    moved.next = @intFromPtr(&dest_tail);
    dest_tail.next = 0;

    const source_after_detach = HListView.init(&source_head);
    try std.testing.expectEqual(@as(?*const HListNode, &source_tail), source_after_detach.first());
    try std.testing.expectEqual(@as(usize, 1), source_after_detach.len());
    try std.testing.expect(!source_after_detach.contains(&moved));
    try std.testing.expect(source_after_detach.hasConsistentPrevLinks());
    try std.testing.expect(source_after_detach.tailNextIsNull());

    const stale_dest = HListView.init(&dest_head);
    try std.testing.expectEqual(@as(?*const HListNode, &moved), stale_dest.first());
    try std.testing.expectEqual(@as(?*const HListNode, &dest_tail), stale_dest.last());
    try std.testing.expectEqual(@as(usize, 2), stale_dest.len());
    try std.testing.expect(stale_dest.contains(&moved));
    try std.testing.expect(stale_dest.contains(&dest_tail));
    try std.testing.expect(!stale_dest.firstPprevMatchesHead());

    const stale_break = stale_dest.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), stale_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&dest_head.first)), stale_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&source_head.first)), stale_break.actual_pprev);

    moved.pprev = @intFromPtr(&dest_head.first);
    dest_tail.pprev = @intFromPtr(&moved.next);

    const repaired_dest = HListView.init(&dest_head);
    try std.testing.expect(repaired_dest.firstPprevMatchesHead());
    try std.testing.expect(repaired_dest.hasConsistentPrevLinks());
    try std.testing.expect(repaired_dest.tailNextIsNull());
    try std.testing.expect(!repaired_dest.isSingular());
    try std.testing.expectEqual(@as(?*const HListNode, &moved), repaired_dest.first());
    try std.testing.expectEqual(@as(?*const HListNode, &dest_tail), repaired_dest.last());
}
