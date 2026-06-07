const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;

const Entry = struct {
    list: ListHead = .{ .next = 0, .prev = 0 },
    hlist: HListNode = .{ .next = 0, .pprev = 0 },
};

const entry_count = 36;
const route = [_]usize{ 34, 0, 17, 16, 33, 1, 18, 15, 32, 2, 19, 14, 31, 3, 20, 13, 30, 4, 21, 12, 29, 5, 22, 11, 28, 6, 23, 10, 27, 7, 24, 9, 26, 8, 25 };
const detached_index = 35;

fn resetEntries(entries: *[entry_count]Entry) void {
    for (entries) |*entry| {
        entry.list.next = @intFromPtr(&entry.list);
        entry.list.prev = @intFromPtr(&entry.list);
        entry.hlist.next = 0;
        entry.hlist.pprev = 0;
    }
}

fn poisonDetached(entries: *[entry_count]Entry) void {
    entries[detached_index].list.next = @intFromPtr(&entries[detached_index].list);
    entries[detached_index].list.prev = @intFromPtr(&entries[detached_index].list);
    entries[detached_index].hlist.next = 0;
    entries[detached_index].hlist.pprev = @intFromPtr(&entries[detached_index].hlist.next);
}

fn linkListForward(head: *ListHead, entries: *[entry_count]Entry) void {
    head.next = @intFromPtr(&entries[route[0]].list);
    head.prev = @intFromPtr(&entries[route[route.len - 1]].list);

    for (route, 0..) |entry_index, order_index| {
        entries[entry_index].list.next = if (order_index + 1 == route.len)
            @intFromPtr(head)
        else
            @intFromPtr(&entries[route[order_index + 1]].list);
        entries[entry_index].list.prev = 0;
    }
}

fn linkHListForward(head: *HListHead, entries: *[entry_count]Entry) void {
    head.first = @intFromPtr(&entries[route[0]].hlist);

    for (route, 0..) |entry_index, order_index| {
        entries[entry_index].hlist.next = if (order_index + 1 == route.len)
            0
        else
            @intFromPtr(&entries[route[order_index + 1]].hlist);
        entries[entry_index].hlist.pprev = 0;
    }
}

fn repairListPrefix(head: *ListHead, entries: *[entry_count]Entry, prefix_len: usize) void {
    var previous_raw = @intFromPtr(head);
    for (route, 0..) |entry_index, order_index| {
        if (order_index >= prefix_len) break;
        entries[entry_index].list.prev = previous_raw;
        previous_raw = @intFromPtr(&entries[entry_index].list);
    }
    if (prefix_len == route.len) {
        head.prev = previous_raw;
    }
}

fn repairHListPrefix(head: *HListHead, entries: *[entry_count]Entry, prefix_len: usize) void {
    var previous_link_raw = @intFromPtr(&head.first);
    for (route, 0..) |entry_index, order_index| {
        if (order_index >= prefix_len) break;
        entries[entry_index].hlist.pprev = previous_link_raw;
        previous_link_raw = @intFromPtr(&entries[entry_index].hlist.next);
    }
}

fn expectListRoute(view: list_view.ListView, entries: *[entry_count]Entry) !void {
    try std.testing.expect(!view.isEmpty());
    try std.testing.expect(!view.isSingular());
    try std.testing.expectEqual(@as(usize, route.len), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &entries[route[0]].list), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &entries[route[route.len - 1]].list), view.last());
    try std.testing.expect(!view.contains(&entries[detached_index].list));

    var iterator = view.iterator();
    for (route) |entry_index| {
        try std.testing.expectEqual(@as(?*const ListHead, &entries[entry_index].list), iterator.next());
        try std.testing.expect(view.contains(&entries[entry_index].list));
    }
    try std.testing.expectEqual(@as(?*const ListHead, null), iterator.next());
}

fn expectHListRoute(view: hlist_view.HListView, entries: *[entry_count]Entry) !void {
    try std.testing.expect(!view.isEmpty());
    try std.testing.expect(!view.isSingular());
    try std.testing.expectEqual(@as(usize, route.len), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &entries[route[0]].hlist), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, &entries[route[route.len - 1]].hlist), view.last());
    try std.testing.expect(view.tailNextIsNull());
    try std.testing.expect(!view.contains(&entries[detached_index].hlist));

    var iterator = view.iterator();
    for (route) |entry_index| {
        try std.testing.expectEqual(@as(?*const HListNode, &entries[entry_index].hlist), iterator.next());
        try std.testing.expect(view.contains(&entries[entry_index].hlist));
    }
    try std.testing.expectEqual(@as(?*const HListNode, null), iterator.next());
}

test "pentatriaconta inner spoke keeps forward list and hlist visibility before repair" {
    var entries: [entry_count]Entry = undefined;
    resetEntries(&entries);
    poisonDetached(&entries);

    var list_head = ListHead{ .next = 0, .prev = 0 };
    var hlist_head = HListHead{ .first = 0 };
    linkListForward(&list_head, &entries);
    linkHListForward(&hlist_head, &entries);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try expectListRoute(list, &entries);
    try expectHListRoute(hlist, &entries);
    try std.testing.expect(!list.hasConsistentBacklinks());
    try std.testing.expect(!hlist.firstPprevMatchesHead());
    try std.testing.expect(!hlist.hasConsistentPrevLinks());

    const list_break = list.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), list_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_head)), list_break.expected_prev);
    try std.testing.expectEqual(@as(usize, 0), list_break.actual_prev);

    const hlist_break = hlist.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), hlist_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_head.first)), hlist_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, 0), hlist_break.actual_pprev);
}

test "pentatriaconta inner spoke staged repair reaches the inner hinge" {
    var entries: [entry_count]Entry = undefined;
    resetEntries(&entries);
    poisonDetached(&entries);

    var list_head = ListHead{ .next = 0, .prev = 0 };
    var hlist_head = HListHead{ .first = 0 };
    linkListForward(&list_head, &entries);
    linkHListForward(&hlist_head, &entries);

    repairListPrefix(&list_head, &entries, 31);
    repairHListPrefix(&hlist_head, &entries, 31);

    const list_after_spoke = list_view.ListView.init(&list_head);
    const hlist_after_spoke = hlist_view.HListView.init(&hlist_head);
    try expectListRoute(list_after_spoke, &entries);
    try expectHListRoute(hlist_after_spoke, &entries);

    const list_break = list_after_spoke.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 31), list_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&entries[route[30]].list)), list_break.expected_prev);
    try std.testing.expectEqual(@as(usize, 0), list_break.actual_prev);

    const hlist_break = hlist_after_spoke.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 31), hlist_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&entries[route[30]].hlist.next)), hlist_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, 0), hlist_break.actual_pprev);

    repairListPrefix(&list_head, &entries, route.len);
    repairHListPrefix(&hlist_head, &entries, route.len);

    const repaired_list = list_view.ListView.init(&list_head);
    const repaired_hlist = hlist_view.HListView.init(&hlist_head);
    try expectListRoute(repaired_list, &entries);
    try expectHListRoute(repaired_hlist, &entries);
    try std.testing.expect(repaired_list.hasConsistentBacklinks());
    try std.testing.expect(repaired_hlist.firstPprevMatchesHead());
    try std.testing.expect(repaired_hlist.hasConsistentPrevLinks());
}
