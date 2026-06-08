const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

const visible_count = 51;
const detached_index = visible_count;
const route = [_]usize{
    50, 0,  26, 25, 49, 1, 27, 24, 48, 2,  28, 23, 47, 3,  29, 22,
    46, 4,  30, 21, 45, 5, 31, 20, 44, 6,  32, 19, 43, 7,  33, 18,
    42, 8,  34, 17, 41, 9, 35, 16, 40, 10, 36, 15, 39, 11, 37, 14,
    38, 12, 13,
};

const Entry = struct {
    list: ListHead = .{ .next = 0, .prev = 0 },
    hlist: HListNode = .{ .next = 0, .pprev = 0 },
};

fn reset(entries: *[visible_count + 1]Entry, head: *ListHead, hhead: *HListHead) void {
    head.next = @intFromPtr(&entries[route[0]].list);
    head.prev = @intFromPtr(&entries[route[visible_count - 1]].list);
    hhead.first = @intFromPtr(&entries[route[0]].hlist);

    for (route, 0..) |entry_index, position| {
        const prev_raw = if (position == 0)
            @intFromPtr(head)
        else
            @intFromPtr(&entries[route[position - 1]].list);
        const next_raw = if (position + 1 == visible_count)
            @intFromPtr(head)
        else
            @intFromPtr(&entries[route[position + 1]].list);

        entries[entry_index].list.prev = prev_raw;
        entries[entry_index].list.next = next_raw;

        entries[entry_index].hlist.pprev = if (position == 0)
            @intFromPtr(&hhead.first)
        else
            @intFromPtr(&entries[route[position - 1]].hlist.next);
        entries[entry_index].hlist.next = if (position + 1 == visible_count)
            0
        else
            @intFromPtr(&entries[route[position + 1]].hlist);
    }

    entries[detached_index].list.next = @intFromPtr(&entries[detached_index].list);
    entries[detached_index].list.prev = @intFromPtr(&entries[detached_index].list);
    entries[detached_index].hlist.next = 0;
    entries[detached_index].hlist.pprev = 0;
}

fn expectForwardRoute(entries: *[visible_count + 1]Entry, head: *const ListHead, hhead: *const HListHead) !void {
    const lview = ListView.init(head);
    const hview = HListView.init(hhead);

    try std.testing.expect(!lview.isEmpty());
    try std.testing.expect(!hview.isEmpty());
    try std.testing.expectEqual(@as(usize, visible_count), lview.len());
    try std.testing.expectEqual(@as(usize, visible_count), hview.len());
    try std.testing.expectEqual(@as(?*const ListHead, &entries[route[0]].list), lview.first());
    try std.testing.expectEqual(@as(?*const ListHead, &entries[route[visible_count - 1]].list), lview.last());
    try std.testing.expectEqual(@as(?*const HListNode, &entries[route[0]].hlist), hview.first());
    try std.testing.expectEqual(@as(?*const HListNode, &entries[route[visible_count - 1]].hlist), hview.last());
    try std.testing.expect(hview.firstPprevMatchesHead());
    try std.testing.expect(hview.tailNextIsNull());

    var list_it = lview.iterator();
    var hlist_it = hview.iterator();
    for (route) |entry_index| {
        try std.testing.expectEqual(@as(?*const ListHead, &entries[entry_index].list), list_it.next());
        try std.testing.expectEqual(@as(?*const HListNode, &entries[entry_index].hlist), hlist_it.next());
        try std.testing.expect(lview.contains(&entries[entry_index].list));
        try std.testing.expect(hview.contains(&entries[entry_index].hlist));
    }
    try std.testing.expectEqual(@as(?*const ListHead, null), list_it.next());
    try std.testing.expectEqual(@as(?*const HListNode, null), hlist_it.next());
    try std.testing.expect(!lview.contains(&entries[detached_index].list));
    try std.testing.expect(!hview.contains(&entries[detached_index].hlist));
}

test "henpentaconta weave-clasp exposes the same visible route through list and hlist" {
    var entries = [_]Entry{.{}} ** (visible_count + 1);
    var head = ListHead{ .next = 0, .prev = 0 };
    var hhead = HListHead{ .first = 0 };

    reset(&entries, &head, &hhead);

    try expectForwardRoute(&entries, &head, &hhead);
    try std.testing.expect(ListView.init(&head).hasConsistentBacklinks());
    try std.testing.expect(HListView.init(&hhead).hasConsistentPrevLinks());
}

test "henpentaconta weave-clasp repairs staged reverse links across the lower clasp" {
    var entries = [_]Entry{.{}} ** (visible_count + 1);
    var head = ListHead{ .next = 0, .prev = 0 };
    var hhead = HListHead{ .first = 0 };

    reset(&entries, &head, &hhead);
    const gate_position = 47;
    const gate_index = route[gate_position];

    entries[gate_index].list.prev = @intFromPtr(&head);
    entries[gate_index].hlist.pprev = @intFromPtr(&hhead.first);

    const list_break = ListView.init(&head).firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, gate_position), list_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&entries[route[gate_position - 1]].list)), list_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), list_break.actual_prev);

    const hlist_break = HListView.init(&hhead).firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, gate_position), hlist_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&entries[route[gate_position - 1]].hlist.next)), hlist_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hhead.first)), hlist_break.actual_pprev);

    entries[gate_index].list.prev = @intFromPtr(&entries[route[gate_position - 1]].list);
    entries[gate_index].hlist.pprev = @intFromPtr(&entries[route[gate_position - 1]].hlist.next);

    try expectForwardRoute(&entries, &head, &hhead);
    try std.testing.expect(ListView.init(&head).hasConsistentBacklinks());
    try std.testing.expect(HListView.init(&hhead).hasConsistentPrevLinks());
}
