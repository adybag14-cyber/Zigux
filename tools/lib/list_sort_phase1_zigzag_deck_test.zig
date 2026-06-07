const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum {
    key_asc,
    key_desc,
    ordinal_asc,
    ordinal_desc,
    all_ties,
};

const SortContext = struct {
    mode: SortMode,
};

fn entryFromNode(node: *const ListHead) *const Entry {
    return @fieldParentPtr("node", node);
}

fn mutableEntryFromNode(node: *ListHead) *Entry {
    return @fieldParentPtr("node", node);
}

fn compareValues(lhs: usize, rhs: usize) i32 {
    if (lhs < rhs) return -1;
    if (lhs > rhs) return 1;
    return 0;
}

fn compare(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const lhs = entryFromNode(a);
    const rhs = entryFromNode(b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn compareWithContext(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const ctx: *const SortContext = @ptrCast(@alignCast(priv.?));
    const lhs = entryFromNode(a);
    const rhs = entryFromNode(b);

    return switch (ctx.mode) {
        .key_asc => compare(null, a, b),
        .key_desc => -compare(null, a, b),
        .ordinal_asc => compareValues(lhs.ordinal, rhs.ordinal),
        .ordinal_desc => -compareValues(lhs.ordinal, rhs.ordinal),
        .all_ties => 0,
    };
}

fn initHeads(heads: []ListHead) void {
    for (heads) |*head| head.init();
}

fn appendOrdinal(out: []usize, index: *usize, entry: *const Entry) void {
    out[index.*] = entry.ordinal;
    index.* += 1;
}

fn popFront(head: *ListHead) !?*Entry {
    if (list_sort.listEmpty(head)) return null;
    const node = head.next.?;
    list_sort.listDel(node);
    try std.testing.expectEqual(@as(?*ListHead, null), node.next);
    try std.testing.expectEqual(@as(?*ListHead, null), node.prev);
    return mutableEntryFromNode(node);
}

fn popBack(head: *ListHead) !?*Entry {
    if (list_sort.listEmpty(head)) return null;
    const node = head.prev.?;
    list_sort.listDel(node);
    try std.testing.expectEqual(@as(?*ListHead, null), node.next);
    try std.testing.expectEqual(@as(?*ListHead, null), node.prev);
    return mutableEntryFromNode(node);
}

fn collectOrdinals(head: *const ListHead, out: []usize) usize {
    var count: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        out[count] = entryFromNode(current.?).ordinal;
        count += 1;
    }
    return count;
}

fn countNodes(head: *const ListHead) usize {
    var count: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        count += 1;
    }
    return count;
}

fn expectCircular(head: *const ListHead, expected_count: usize) !void {
    var forward_count: usize = 0;
    var current = head.next;
    var previous: *const ListHead = head;
    while (current != head) : (current = current.?.next) {
        try std.testing.expectEqual(previous, current.?.prev.?);
        previous = current.?;
        forward_count += 1;
    }
    try std.testing.expectEqual(expected_count, forward_count);
    try std.testing.expectEqual(previous, head.prev.?);

    var reverse_count: usize = 0;
    current = head.prev;
    var next: *const ListHead = head;
    while (current != head) : (current = current.?.prev) {
        try std.testing.expectEqual(next, current.?.next.?);
        next = current.?;
        reverse_count += 1;
    }
    try std.testing.expectEqual(expected_count, reverse_count);
    try std.testing.expectEqual(next, head.next.?);
}

fn expectSortedStable(head: *const ListHead, expected_count: usize) !void {
    var current = head.next;
    var prior: ?*const Entry = null;
    var count: usize = 0;
    while (current != head) : (current = current.?.next) {
        const entry = entryFromNode(current.?);
        if (prior) |previous| {
            try std.testing.expect(previous.key <= entry.key);
            if (previous.key == entry.key) {
                try std.testing.expect(previous.ordinal < entry.ordinal);
            }
        }
        prior = entry;
        count += 1;
    }
    try std.testing.expectEqual(expected_count, count);
}

test "list sort survives zigzag deck split and rebuilt tie pass" {
    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 4, .ordinal = 4 },
        .{ .key = 0, .ordinal = 5 },
        .{ .key = 3, .ordinal = 6 },
        .{ .key = 1, .ordinal = 7 },
        .{ .key = 2, .ordinal = 8 },
        .{ .key = 5, .ordinal = 9 },
        .{ .key = 0, .ordinal = 10 },
        .{ .key = 5, .ordinal = 11 },
        .{ .key = 2, .ordinal = 12 },
        .{ .key = 4, .ordinal = 13 },
        .{ .key = 1, .ordinal = 14 },
        .{ .key = 3, .ordinal = 15 },
    };

    var main: ListHead = .{};
    main.init();
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &main);

    list_sort.listSort(null, &main, compare);
    try expectSortedStable(&main, entries.len);
    try expectCircular(&main, entries.len);

    var decks: [4]ListHead = undefined;
    initHeads(&decks);
    const deck_pattern = [_]usize{ 0, 1, 2, 3, 3, 2, 1, 0 };
    var sorted_rank: usize = 0;
    while (try popFront(&main)) |entry| : (sorted_rank += 1) {
        const deck_index = deck_pattern[sorted_rank % deck_pattern.len];
        if ((sorted_rank & 1) == 0) {
            list_sort.listAddTail(&entry.node, &decks[deck_index]);
        } else {
            list_sort.listAdd(&entry.node, &decks[deck_index]);
        }
    }
    try std.testing.expect(list_sort.listEmpty(&main));
    try std.testing.expectEqual(entries.len, sorted_rank);

    var contexts = [_]SortContext{
        .{ .mode = .key_desc },
        .{ .mode = .ordinal_asc },
        .{ .mode = .ordinal_desc },
        .{ .mode = .key_asc },
    };
    for (&decks, &contexts) |*deck, *ctx| {
        if (!list_sort.listEmpty(deck)) {
            list_sort.listSort(ctx, deck, compareWithContext);
            try expectCircular(deck, countNodes(deck));
        }
    }

    var rebuilt_ordinals: [entries.len]usize = undefined;
    var rebuilt_count: usize = 0;
    const rebuild_decks = [_]usize{ 3, 0, 2, 1 };
    var round: usize = 0;
    while (rebuilt_count < entries.len) : (round += 1) {
        var moved_this_round = false;
        for (rebuild_decks, 0..) |deck_index, slot| {
            const entry = if (((round + slot) & 1) == 0)
                try popFront(&decks[deck_index])
            else
                try popBack(&decks[deck_index]);
            if (entry) |item| {
                list_sort.listAddTail(&item.node, &main);
                appendOrdinal(&rebuilt_ordinals, &rebuilt_count, item);
                moved_this_round = true;
            }
        }
        try std.testing.expect(moved_this_round);
    }

    for (&decks) |*deck| try std.testing.expect(list_sort.listEmpty(deck));
    try expectCircular(&main, entries.len);

    var before_tie_sort: [entries.len]usize = undefined;
    const before_count = collectOrdinals(&main, &before_tie_sort);
    try std.testing.expectEqual(entries.len, before_count);
    try std.testing.expectEqualSlices(usize, rebuilt_ordinals[0..], before_tie_sort[0..]);

    var tie_context = SortContext{ .mode = .all_ties };
    list_sort.listSort(&tie_context, &main, compareWithContext);
    try expectCircular(&main, entries.len);

    var after_tie_sort: [entries.len]usize = undefined;
    const after_count = collectOrdinals(&main, &after_tie_sort);
    try std.testing.expectEqual(entries.len, after_count);
    try std.testing.expectEqualSlices(usize, before_tie_sort[0..], after_tie_sort[0..]);
}
