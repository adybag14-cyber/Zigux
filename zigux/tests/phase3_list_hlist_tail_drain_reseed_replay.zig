const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

fn expectListEmpty(head: *const list_view.ListHead) !void {
    const view = list_view.ListView.init(head);
    try std.testing.expect(view.isEmpty());
    try std.testing.expect(!view.isSingular());
    try std.testing.expectEqual(@as(usize, 0), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
}

fn expectListPair(
    head: *const list_view.ListHead,
    first: *const list_view.ListHead,
    second: *const list_view.ListHead,
) !void {
    const view = list_view.ListView.init(head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expect(!view.isSingular());
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, second), view.last());
    try std.testing.expect(view.contains(first));
    try std.testing.expect(view.contains(second));
    try std.testing.expect(view.hasConsistentBacklinks());
}

fn expectHListEmpty(head: *const hlist_view.HListHead) !void {
    const view = hlist_view.HListView.init(head);
    try std.testing.expect(view.isEmpty());
    try std.testing.expect(!view.isSingular());
    try std.testing.expectEqual(@as(usize, 0), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), view.first());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), view.last());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

fn expectHListPair(
    head: *const hlist_view.HListHead,
    first: *const hlist_view.HListNode,
    second: *const hlist_view.HListNode,
) !void {
    const view = hlist_view.HListView.init(head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expect(!view.isSingular());
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, first), view.first());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, second), view.last());
    try std.testing.expect(view.contains(first));
    try std.testing.expect(view.contains(second));
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "list tail drain can reseed another head without stale source state" {
    var source = list_view.ListHead{ .next = 0, .prev = 0 };
    var dest = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };

    source.next = @intFromPtr(&first);
    source.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&tail);
    first.prev = @intFromPtr(&source);
    tail.next = @intFromPtr(&source);
    tail.prev = @intFromPtr(&first);
    dest.next = @intFromPtr(&dest);
    dest.prev = @intFromPtr(&dest);

    try expectListPair(&source, &first, &tail);
    try expectListEmpty(&dest);

    source.next = @intFromPtr(&source);
    source.prev = @intFromPtr(&source);
    dest.next = @intFromPtr(&first);
    dest.prev = @intFromPtr(&tail);
    tail.next = @intFromPtr(&dest);

    var source_view = list_view.ListView.init(&source);
    var dest_view = list_view.ListView.init(&dest);
    try std.testing.expect(source_view.isEmpty());
    try std.testing.expect(!source_view.contains(&first));
    try std.testing.expect(!source_view.contains(&tail));
    try std.testing.expectEqual(@as(usize, 2), dest_view.len());

    const stale_first = dest_view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), stale_first.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&dest)), stale_first.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&source)), stale_first.actual_prev);

    first.prev = @intFromPtr(&dest);

    source_view = list_view.ListView.init(&source);
    dest_view = list_view.ListView.init(&dest);
    try std.testing.expect(source_view.isEmpty());
    try expectListPair(&dest, &first, &tail);
}

test "hlist tail drain can reseed another head without stale source state" {
    var source = hlist_view.HListHead{ .first = 0 };
    var dest = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    source.first = @intFromPtr(&first);
    first.next = @intFromPtr(&tail);
    first.pprev = @intFromPtr(&source.first);
    tail.next = 0;
    tail.pprev = @intFromPtr(&first.next);

    try expectHListPair(&source, &first, &tail);
    try expectHListEmpty(&dest);

    source.first = 0;
    dest.first = @intFromPtr(&first);

    var source_view = hlist_view.HListView.init(&source);
    var dest_view = hlist_view.HListView.init(&dest);
    try std.testing.expect(source_view.isEmpty());
    try std.testing.expect(!source_view.contains(&first));
    try std.testing.expect(!source_view.contains(&tail));
    try std.testing.expectEqual(@as(usize, 2), dest_view.len());
    try std.testing.expect(!dest_view.firstPprevMatchesHead());
    try std.testing.expect(dest_view.tailNextIsNull());

    const stale_first = dest_view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), stale_first.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&dest.first)), stale_first.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&source.first)), stale_first.actual_pprev);

    first.pprev = @intFromPtr(&dest.first);

    source_view = hlist_view.HListView.init(&source);
    dest_view = hlist_view.HListView.init(&dest);
    try std.testing.expect(source_view.isEmpty());
    try expectHListPair(&dest, &first, &tail);
}
