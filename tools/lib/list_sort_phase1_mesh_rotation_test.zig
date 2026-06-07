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

fn compareOrder(lhs: usize, rhs: usize) i32 {
    if (lhs < rhs) return -1;
    if (lhs > rhs) return 1;
    return 0;
}

fn compareKeys(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
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
        .key_asc => compareKeys(null, a, b),
        .key_desc => -compareKeys(null, a, b),
        .ordinal_asc => compareOrder(lhs.ordinal, rhs.ordinal),
        .ordinal_desc => -compareOrder(lhs.ordinal, rhs.ordinal),
        .all_ties => 0,
    };
}

fn initHeads(heads: []ListHead) void {
    for (heads) |*head| head.init();
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

fn appendOrdinal(out: []usize, index: *usize, entry: *const Entry) void {
    out[index.*] = entry.ordinal;
    index.* += 1;
}

fn collectOrdinals(head: *const ListHead, out: []usize) ![]usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry = entryFromNode(current.?);
        appendOrdinal(out, &idx, entry);
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
    }
    return out[0..idx];
}

fn appendToMain(head: *ListHead, maybe_entry: ?*Entry) void {
    const entry = maybe_entry.?;
    list_sort.listAddTail(&entry.node, head);
}

test "list sort survives mesh rotation staging and all-ties preservation" {
    var head: ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 10, .ordinal = 0 },
        .{ .key = 7, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 12, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 8, .ordinal = 5 },
        .{ .key = 2, .ordinal = 6 },
        .{ .key = 11, .ordinal = 7 },
        .{ .key = 6, .ordinal = 8 },
        .{ .key = 1, .ordinal = 9 },
        .{ .key = 9, .ordinal = 10 },
        .{ .key = 4, .ordinal = 11 },
    };
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    list_sort.listSort(null, &head, compareKeys);

    var sorted_ordinals: [entries.len]usize = undefined;
    try std.testing.expectEqualSlices(usize, &.{ 9, 6, 2, 11, 4, 8, 1, 5, 10, 0, 7, 3 }, try collectOrdinals(&head, &sorted_ordinals));

    var mesh_heads: [4]ListHead = undefined;
    initHeads(&mesh_heads);

    var rank: usize = 0;
    while (try popFront(&head)) |entry| : (rank += 1) {
        const mesh_index = rank % mesh_heads.len;
        if (mesh_index == 1 or mesh_index == 3) {
            list_sort.listAdd(&entry.node, &mesh_heads[mesh_index]);
        } else {
            list_sort.listAddTail(&entry.node, &mesh_heads[mesh_index]);
        }
    }
    try std.testing.expect(list_sort.listEmpty(&head));

    var ctx = SortContext{ .mode = .key_desc };
    list_sort.listSort(&ctx, &mesh_heads[0], compareWithContext);
    ctx.mode = .ordinal_asc;
    list_sort.listSort(&ctx, &mesh_heads[1], compareWithContext);
    ctx.mode = .ordinal_desc;
    list_sort.listSort(&ctx, &mesh_heads[2], compareWithContext);
    ctx.mode = .key_asc;
    list_sort.listSort(&ctx, &mesh_heads[3], compareWithContext);

    appendToMain(&head, try popFront(&mesh_heads[2]));
    appendToMain(&head, try popBack(&mesh_heads[0]));
    appendToMain(&head, try popFront(&mesh_heads[3]));
    appendToMain(&head, try popBack(&mesh_heads[1]));
    appendToMain(&head, try popFront(&mesh_heads[0]));
    appendToMain(&head, try popBack(&mesh_heads[2]));
    appendToMain(&head, try popFront(&mesh_heads[1]));
    appendToMain(&head, try popBack(&mesh_heads[3]));
    appendToMain(&head, try popFront(&mesh_heads[2]));
    appendToMain(&head, try popBack(&mesh_heads[0]));
    appendToMain(&head, try popFront(&mesh_heads[3]));
    appendToMain(&head, try popBack(&mesh_heads[1]));

    for (&mesh_heads) |*mesh_head| try std.testing.expect(list_sort.listEmpty(mesh_head));

    var rotated_ordinals: [entries.len]usize = undefined;
    try std.testing.expectEqualSlices(usize, &.{ 7, 9, 11, 8, 10, 1, 0, 3, 2, 4, 5, 6 }, try collectOrdinals(&head, &rotated_ordinals));

    ctx.mode = .all_ties;
    list_sort.listSort(&ctx, &head, compareWithContext);

    var tied_ordinals: [entries.len]usize = undefined;
    try std.testing.expectEqualSlices(usize, &.{ 7, 9, 11, 8, 10, 1, 0, 3, 2, 4, 5, 6 }, try collectOrdinals(&head, &tied_ordinals));
    try std.testing.expect(head.next == &entries[7].node);
    try std.testing.expect(head.prev == &entries[6].node);
}
