const std = @import("std");
const testing = std.testing;

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "list tail shadow stays off-route until the visible tail adopts it" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };
    var third = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&third);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&third);
    second.prev = @intFromPtr(&first);
    third.next = @intFromPtr(&head);
    third.prev = @intFromPtr(&second);

    shadow.next = @intFromPtr(&head);
    shadow.prev = @intFromPtr(&second);

    const stable = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 3), stable.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &third), stable.last());
    try testing.expect(stable.hasConsistentBacklinks());

    third.prev = @intFromPtr(&shadow);
    const broken = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 3), broken.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &third), broken.last());

    const breakage = broken.firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 2), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&second)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&shadow)), breakage.actual_prev);
    try testing.expect(!broken.hasConsistentBacklinks());
}

test "hlist tail shadow stays off-route until the visible tail adopts it" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var third = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&third);
    second.pprev = @intFromPtr(&first.next);
    third.next = 0;
    third.pprev = @intFromPtr(&second.next);

    shadow.next = 0;
    shadow.pprev = @intFromPtr(&second.next);

    const stable = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 3), stable.len());
    try testing.expect(stable.hasConsistentPrevLinks());
    try testing.expect(stable.tailNextIsNull());

    third.pprev = @intFromPtr(&shadow.next);
    const broken = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 3), broken.len());
    try testing.expect(broken.tailNextIsNull());

    const breakage = broken.firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 2), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&second.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&shadow.next)), breakage.actual_pprev);
    try testing.expect(!broken.hasConsistentPrevLinks());
}
