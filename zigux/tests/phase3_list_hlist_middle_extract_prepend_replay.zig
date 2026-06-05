const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

fn expectListRoute(
    head: *const list_view.ListHead,
    first: *const list_view.ListHead,
    second: *const list_view.ListHead,
    third: *const list_view.ListHead,
) !void {
    const view = list_view.ListView.init(head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expect(!view.isSingular());
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, third), view.last());
    try std.testing.expect(view.contains(first));
    try std.testing.expect(view.contains(second));
    try std.testing.expect(view.contains(third));
}

fn expectCleanListRoute(
    head: *const list_view.ListHead,
    first: *const list_view.ListHead,
    second: *const list_view.ListHead,
    third: *const list_view.ListHead,
) !void {
    try expectListRoute(head, first, second, third);
    try std.testing.expect(list_view.ListView.init(head).hasConsistentBacklinks());
}

fn expectHListRoute(
    head: *const hlist_view.HListHead,
    first: *const hlist_view.HListNode,
    second: *const hlist_view.HListNode,
    third: *const hlist_view.HListNode,
) !void {
    const view = hlist_view.HListView.init(head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expect(!view.isSingular());
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, first), view.first());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, third), view.last());
    try std.testing.expect(view.contains(first));
    try std.testing.expect(view.contains(second));
    try std.testing.expect(view.contains(third));
    try std.testing.expect(view.tailNextIsNull());
}

fn expectCleanHListRoute(
    head: *const hlist_view.HListHead,
    first: *const hlist_view.HListNode,
    second: *const hlist_view.HListNode,
    third: *const hlist_view.HListNode,
) !void {
    try expectHListRoute(head, first, second, third);
    const view = hlist_view.HListView.init(head);
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
}

test "list middle extract can prepend before backlink repair" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&middle);
    first.prev = @intFromPtr(&head);
    middle.next = @intFromPtr(&tail);
    middle.prev = @intFromPtr(&first);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&middle);

    try expectCleanListRoute(&head, &first, &middle, &tail);

    first.next = @intFromPtr(&tail);
    middle.next = @intFromPtr(&first);
    middle.prev = @intFromPtr(&head);
    head.next = @intFromPtr(&middle);

    var view = list_view.ListView.init(&head);
    try expectListRoute(&head, &middle, &first, &tail);
    var breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&middle)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);

    first.prev = @intFromPtr(&middle);
    view = list_view.ListView.init(&head);
    breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&middle)), breakage.actual_prev);

    tail.prev = @intFromPtr(&first);
    try expectCleanListRoute(&head, &middle, &first, &tail);
}

test "hlist middle extract can prepend before prev-link repair" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&middle);
    first.pprev = @intFromPtr(&head.first);
    middle.next = @intFromPtr(&tail);
    middle.pprev = @intFromPtr(&first.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&middle.next);

    try expectCleanHListRoute(&head, &first, &middle, &tail);

    first.next = @intFromPtr(&tail);
    middle.next = @intFromPtr(&first);
    middle.pprev = @intFromPtr(&head.first);
    head.first = @intFromPtr(&middle);

    var view = hlist_view.HListView.init(&head);
    try expectHListRoute(&head, &middle, &first, &tail);
    var breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&middle.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);

    first.pprev = @intFromPtr(&middle.next);
    view = hlist_view.HListView.init(&head);
    breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&middle.next)), breakage.actual_pprev);

    tail.pprev = @intFromPtr(&first.next);
    try expectCleanHListRoute(&head, &middle, &first, &tail);
}
