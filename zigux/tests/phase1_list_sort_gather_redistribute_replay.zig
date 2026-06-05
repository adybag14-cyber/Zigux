const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn cmpByKey(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key == rhs.key) return 0;

    const ascending = lhs.key < rhs.key;
    return if (mode.* == .ascending)
        (if (ascending) -1 else 1)
    else
        (if (ascending) 1 else -1);
}

fn cmpAllTies(_: ?*anyopaque, _: *const list_sort.ListHead, _: *const list_sort.ListHead) i32 {
    return 0;
}

fn collectOrdinals(head: *const list_sort.ListHead, out: []usize) !usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return idx;
}

fn expectOrder(head: *const list_sort.ListHead, expected: []const usize) !void {
    var ordinals: [16]usize = undefined;
    const count = try collectOrdinals(head, &ordinals);
    try std.testing.expectEqualSlices(usize, expected, ordinals[0..count]);
}

fn popFront(head: *list_sort.ListHead) ?*list_sort.ListHead {
    if (list_sort.listEmpty(head)) return null;
    const node = head.next.?;
    list_sort.listDel(node);
    return node;
}

test "list sort preserves gather redistribute staging lifecycle" {
    var main: list_sort.ListHead = .{};
    main.init();

    var stages = [_]list_sort.ListHead{ .{}, .{}, .{} };
    for (&stages) |*stage| stage.init();

    var entries = [_]Entry{
        .{ .key = 42, .ordinal = 0 },
        .{ .key = 5, .ordinal = 1 },
        .{ .key = 33, .ordinal = 2 },
        .{ .key = 17, .ordinal = 3 },
        .{ .key = 28, .ordinal = 4 },
        .{ .key = 9, .ordinal = 5 },
        .{ .key = 40, .ordinal = 6 },
        .{ .key = 12, .ordinal = 7 },
        .{ .key = 24, .ordinal = 8 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &main);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &main, cmpByKey);
    try expectOrder(&main, &.{ 1, 5, 7, 3, 8, 4, 2, 6, 0 });
    try std.testing.expect(main.next == &entries[1].node);
    try std.testing.expect(main.prev == &entries[0].node);

    var gather_index: usize = 0;
    while (popFront(&main)) |node| : (gather_index += 1) {
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        list_sort.listAddTail(node, &stages[gather_index % stages.len]);
    }
    try std.testing.expect(list_sort.listEmpty(&main));

    try expectOrder(&stages[0], &.{ 1, 3, 2 });
    try expectOrder(&stages[1], &.{ 5, 8, 6 });
    try expectOrder(&stages[2], &.{ 7, 4, 0 });

    mode = .descending;
    for (&stages) |*stage| list_sort.listSort(&mode, stage, cmpByKey);
    try expectOrder(&stages[0], &.{ 2, 3, 1 });
    try expectOrder(&stages[1], &.{ 6, 8, 5 });
    try expectOrder(&stages[2], &.{ 0, 4, 7 });

    const rebuild_order = [_]usize{ 2, 0, 1 };
    var moved = true;
    while (moved) {
        moved = false;
        for (rebuild_order) |stage_index| {
            if (popFront(&stages[stage_index])) |node| {
                try std.testing.expect(node.next == null);
                try std.testing.expect(node.prev == null);
                list_sort.listAddTail(node, &main);
                moved = true;
            }
        }
    }
    for (&stages) |*stage| try std.testing.expect(list_sort.listEmpty(stage));

    try expectOrder(&main, &.{ 0, 2, 6, 4, 3, 8, 7, 1, 5 });
    try std.testing.expect(main.next == &entries[0].node);
    try std.testing.expect(main.prev == &entries[5].node);

    list_sort.listSort(null, &main, cmpAllTies);
    try expectOrder(&main, &.{ 0, 2, 6, 4, 3, 8, 7, 1, 5 });
    try std.testing.expect(main.next == &entries[0].node);
    try std.testing.expect(main.prev == &entries[5].node);
}
