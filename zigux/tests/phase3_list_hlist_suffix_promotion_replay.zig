const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

fn expectListRoute(
    head: *const list_view.ListHead,
    first: *const list_view.ListHead,
    second: *const list_view.ListHead,
    third: *const list_view.ListHead,
    fourth: *const list_view.ListHead,
) !void {
    const view = list_view.ListView.init(head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expect(!view.isSingular());
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, fourth), view.last());
    try std.testing.expect(view.contains(first));
    try std.testing.expect(view.contains(second));
    try std.testing.expect(view.contains(third));
    try std.testing.expect(view.contains(fourth));
}

fn expectCleanListRoute(
    head: *const list_view.ListHead,
    first: *const list_view.ListHead,
    second: *const list_view.ListHead,
    third: *const list_view.ListHead,
    fourth: *const list_view.ListHead,
) !void {
    try expectListRoute(head, first, second, third, fourth);
    try std.testing.expect(list_view.ListView.init(head).hasConsistentBacklinks());
}

fn expectHListRoute(
    head: *const hlist_view.HListHead,
    first: *const hlist_view.HListNode,
    second: *const hlist_view.HListNode,
    third: *const hlist_view.HListNode,
    fourth: *const hlist_view.HListNode,
) !void {
    const view = hlist_view.HListView.init(head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expect(!view.isSingular());
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, first), view.first());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, fourth), view.last());
    try std.testing.expect(view.contains(first));
    try std.testing.expect(view.contains(second));
    try std.testing.expect(view.contains(third));
    try std.testing.expect(view.contains(fourth));
    try std.testing.expect(view.tailNextIsNull());
}

fn expectCleanHListRoute(
    head: *const hlist_view.HListHead,
    first: *const hlist_view.HListNode,
    second: *const hlist_view.HListNode,
    third: *const hlist_view.HListNode,
    fourth: *const hlist_view.HListNode,
) !void {
    try expectHListRoute(head, first, second, third, fourth);
    const view = hlist_view.HListView.init(head);
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
}

test "list two-node suffix promotion exposes stale backlink stages" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };
    var third = list_view.ListHead{ .next = 0, .prev = 0 };
    var fourth = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&fourth);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&third);
    second.prev = @intFromPtr(&first);
    third.next = @intFromPtr(&fourth);
    third.prev = @intFromPtr(&second);
    fourth.next = @intFromPtr(&head);
    fourth.prev = @intFromPtr(&third);

    try expectCleanListRoute(&head, &first, &second, &third, &fourth);

    second.next = @intFromPtr(&head);
    third.next = @intFromPtr(&fourth);
    fourth.next = @intFromPtr(&first);
    head.next = @intFromPtr(&third);
    head.prev = @intFromPtr(&second);

    var view = list_view.ListView.init(&head);
    try expectListRoute(&head, &third, &fourth, &first, &second);
    var breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&second)), breakage.actual_prev);

    third.prev = @intFromPtr(&head);
    view = list_view.ListView.init(&head);
    breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&fourth)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);

    first.prev = @intFromPtr(&fourth);
    try expectCleanListRoute(&head, &third, &fourth, &first, &second);
}

test "hlist two-node suffix promotion exposes stale prev-link stages" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var third = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var fourth = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&third);
    second.pprev = @intFromPtr(&first.next);
    third.next = @intFromPtr(&fourth);
    third.pprev = @intFromPtr(&second.next);
    fourth.next = 0;
    fourth.pprev = @intFromPtr(&third.next);

    try expectCleanHListRoute(&head, &first, &second, &third, &fourth);

    second.next = 0;
    third.next = @intFromPtr(&fourth);
    fourth.next = @intFromPtr(&first);
    head.first = @intFromPtr(&third);

    var view = hlist_view.HListView.init(&head);
    try expectHListRoute(&head, &third, &fourth, &first, &second);
    var breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&second.next)), breakage.actual_pprev);

    third.pprev = @intFromPtr(&head.first);
    view = hlist_view.HListView.init(&head);
    breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&fourth.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);

    first.pprev = @intFromPtr(&fourth.next);
    try expectCleanHListRoute(&head, &third, &fourth, &first, &second);
}
