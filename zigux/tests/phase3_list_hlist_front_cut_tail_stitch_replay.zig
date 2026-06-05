const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

fn expectListRoute(
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
}

fn expectCleanListRoute(
    head: *const list_view.ListHead,
    first: *const list_view.ListHead,
    second: *const list_view.ListHead,
) !void {
    try expectListRoute(head, first, second);
    try std.testing.expect(list_view.ListView.init(head).hasConsistentBacklinks());
}

fn expectHListRoute(
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
    try std.testing.expect(view.tailNextIsNull());
}

fn expectCleanHListRoute(
    head: *const hlist_view.HListHead,
    first: *const hlist_view.HListNode,
    second: *const hlist_view.HListNode,
) !void {
    try expectHListRoute(head, first, second);
    const view = hlist_view.HListView.init(head);
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
}

test "list front cut can stitch a replacement tail before backlink repair" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var old_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var old_second = list_view.ListHead{ .next = 0, .prev = 0 };
    var kept_tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var stitched_tail = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&old_first);
    head.prev = @intFromPtr(&kept_tail);
    old_first.next = @intFromPtr(&old_second);
    old_first.prev = @intFromPtr(&head);
    old_second.next = @intFromPtr(&kept_tail);
    old_second.prev = @intFromPtr(&old_first);
    kept_tail.next = @intFromPtr(&head);
    kept_tail.prev = @intFromPtr(&old_second);
    stitched_tail.next = @intFromPtr(&stitched_tail);
    stitched_tail.prev = @intFromPtr(&stitched_tail);

    var view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expect(view.contains(&old_first));
    try std.testing.expect(view.contains(&old_second));
    try std.testing.expect(view.contains(&kept_tail));
    try std.testing.expect(view.hasConsistentBacklinks());

    head.next = @intFromPtr(&kept_tail);
    head.prev = @intFromPtr(&stitched_tail);
    kept_tail.next = @intFromPtr(&stitched_tail);
    stitched_tail.next = @intFromPtr(&head);
    stitched_tail.prev = @intFromPtr(&head);

    view = list_view.ListView.init(&head);
    try expectListRoute(&head, &kept_tail, &stitched_tail);
    try std.testing.expect(!view.contains(&old_first));
    try std.testing.expect(!view.contains(&old_second));

    const stale_kept_tail = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), stale_kept_tail.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), stale_kept_tail.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_second)), stale_kept_tail.actual_prev);

    kept_tail.prev = @intFromPtr(&head);

    view = list_view.ListView.init(&head);
    const stale_stitched_tail = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), stale_stitched_tail.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&kept_tail)), stale_stitched_tail.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), stale_stitched_tail.actual_prev);

    stitched_tail.prev = @intFromPtr(&kept_tail);

    try expectCleanListRoute(&head, &kept_tail, &stitched_tail);
}

test "hlist front cut can stitch a replacement tail before prev-link repair" {
    var head = hlist_view.HListHead{ .first = 0 };
    var old_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var old_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var kept_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var stitched_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&old_first);
    old_first.next = @intFromPtr(&old_second);
    old_first.pprev = @intFromPtr(&head.first);
    old_second.next = @intFromPtr(&kept_tail);
    old_second.pprev = @intFromPtr(&old_first.next);
    kept_tail.next = 0;
    kept_tail.pprev = @intFromPtr(&old_second.next);
    stitched_tail.next = 0;
    stitched_tail.pprev = 0;

    var view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expect(view.contains(&old_first));
    try std.testing.expect(view.contains(&old_second));
    try std.testing.expect(view.contains(&kept_tail));
    try std.testing.expect(view.hasConsistentPrevLinks());

    head.first = @intFromPtr(&kept_tail);
    kept_tail.next = @intFromPtr(&stitched_tail);
    stitched_tail.next = 0;
    stitched_tail.pprev = @intFromPtr(&head.first);

    view = hlist_view.HListView.init(&head);
    try expectHListRoute(&head, &kept_tail, &stitched_tail);
    try std.testing.expect(!view.contains(&old_first));
    try std.testing.expect(!view.contains(&old_second));
    try std.testing.expect(!view.firstPprevMatchesHead());

    const stale_kept_tail = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), stale_kept_tail.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), stale_kept_tail.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_second.next)), stale_kept_tail.actual_pprev);

    kept_tail.pprev = @intFromPtr(&head.first);

    view = hlist_view.HListView.init(&head);
    const stale_stitched_tail = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), stale_stitched_tail.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&kept_tail.next)), stale_stitched_tail.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), stale_stitched_tail.actual_pprev);

    stitched_tail.pprev = @intFromPtr(&kept_tail.next);

    try expectCleanHListRoute(&head, &kept_tail, &stitched_tail);
}
