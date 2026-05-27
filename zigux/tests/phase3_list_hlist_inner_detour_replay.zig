const std = @import("std");
const testing = std.testing;

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

fn collectListPointers(view: list_view.ListView, buffer: []usize) []const usize {
    var count: usize = 0;
    var it = view.iterator();
    while (it.next()) |node| {
        buffer[count] = @intFromPtr(node);
        count += 1;
    }
    return buffer[0..count];
}

fn collectHListPointers(view: hlist_view.HListView, buffer: []usize) []const usize {
    var count: usize = 0;
    var it = view.iterator();
    while (it.next()) |node| {
        buffer[count] = @intFromPtr(node);
        count += 1;
    }
    return buffer[0..count];
}

test "list inner detour replay keeps the visible route until the detour is adopted" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };
    var third = list_view.ListHead{ .next = 0, .prev = 0 };
    var detour = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&third);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&third);
    second.prev = @intFromPtr(&first);
    third.next = @intFromPtr(&head);
    third.prev = @intFromPtr(&second);

    detour.next = @intFromPtr(&third);
    detour.prev = @intFromPtr(&first);

    const view = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 3), view.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &third), view.last());
    try testing.expect(view.hasConsistentBacklinks());

    var actual: [3]usize = undefined;
    try testing.expectEqualSlices(
        usize,
        &[_]usize{ @intFromPtr(&first), @intFromPtr(&second), @intFromPtr(&third) },
        collectListPointers(view, &actual),
    );
}

test "list inner detour replay reports the tail witness once the detour is adopted too early" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };
    var third = list_view.ListHead{ .next = 0, .prev = 0 };
    var detour = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&third);
    first.next = @intFromPtr(&detour);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&third);
    second.prev = @intFromPtr(&first);
    third.next = @intFromPtr(&head);
    third.prev = @intFromPtr(&second);

    detour.next = @intFromPtr(&third);
    detour.prev = @intFromPtr(&first);

    const view = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 3), view.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &third), view.last());
    try testing.expect(!view.hasConsistentBacklinks());

    var actual: [3]usize = undefined;
    try testing.expectEqualSlices(
        usize,
        &[_]usize{ @intFromPtr(&first), @intFromPtr(&detour), @intFromPtr(&third) },
        collectListPointers(view, &actual),
    );

    const breakage = view.firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 2), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&detour)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&second)), breakage.actual_prev);
}

test "hlist inner detour replay keeps the visible route until the detour is adopted" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var third = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var detour = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&third);
    second.pprev = @intFromPtr(&first.next);
    third.next = 0;
    third.pprev = @intFromPtr(&second.next);

    detour.next = @intFromPtr(&third);
    detour.pprev = @intFromPtr(&first.next);

    const view = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 3), view.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try testing.expect(view.firstPprevMatchesHead());
    try testing.expect(view.hasConsistentPrevLinks());
    try testing.expect(view.tailNextIsNull());

    var actual: [3]usize = undefined;
    try testing.expectEqualSlices(
        usize,
        &[_]usize{ @intFromPtr(&first), @intFromPtr(&second), @intFromPtr(&third) },
        collectHListPointers(view, &actual),
    );
}

test "hlist inner detour replay reports the tail witness once the detour is adopted too early" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var third = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var detour = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&detour);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&third);
    second.pprev = @intFromPtr(&first.next);
    third.next = 0;
    third.pprev = @intFromPtr(&second.next);

    detour.next = @intFromPtr(&third);
    detour.pprev = @intFromPtr(&first.next);

    const view = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 3), view.len());
    try testing.expect(view.firstPprevMatchesHead());
    try testing.expect(!view.hasConsistentPrevLinks());
    try testing.expect(view.tailNextIsNull());

    var actual: [3]usize = undefined;
    try testing.expectEqualSlices(
        usize,
        &[_]usize{ @intFromPtr(&first), @intFromPtr(&detour), @intFromPtr(&third) },
        collectHListPointers(view, &actual),
    );

    const breakage = view.firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 2), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&detour.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&second.next)), breakage.actual_pprev);
}
