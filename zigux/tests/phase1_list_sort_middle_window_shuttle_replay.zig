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

fn moveFrontChecked(src: *list_sort.ListHead, dst: *list_sort.ListHead) !void {
    const node = popFront(src).?;
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    list_sort.listAddTail(node, dst);
}

fn detachAfterChecked(anchor: *list_sort.ListHead, dst: *list_sort.ListHead) !void {
    const node = anchor.next.?;
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    list_sort.listAddTail(node, dst);
}

test "list sort preserves middle window shuttle lifecycle" {
    var main: list_sort.ListHead = .{};
    main.init();
    var shuttle: list_sort.ListHead = .{};
    shuttle.init();
    var rebuilt: list_sort.ListHead = .{};
    rebuilt.init();

    var entries = [_]Entry{
        .{ .key = 19, .ordinal = 0 },
        .{ .key = -4, .ordinal = 1 },
        .{ .key = 11, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 17, .ordinal = 4 },
        .{ .key = 3, .ordinal = 5 },
        .{ .key = -8, .ordinal = 6 },
        .{ .key = 11, .ordinal = 7 },
        .{ .key = 0, .ordinal = 8 },
        .{ .key = 25, .ordinal = 9 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &main);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &main, cmpByKey);
    try expectOrder(&main, &.{ 6, 1, 8, 3, 5, 2, 7, 4, 0, 9 });
    try std.testing.expect(main.next == &entries[6].node);
    try std.testing.expect(main.prev == &entries[9].node);

    const prefix_tail = &entries[1].node;
    var detached: usize = 0;
    while (detached < 6) : (detached += 1) {
        try detachAfterChecked(prefix_tail, &shuttle);
    }
    try expectOrder(&main, &.{ 6, 1, 0, 9 });
    try expectOrder(&shuttle, &.{ 8, 3, 5, 2, 7, 4 });
    try std.testing.expect(main.next == &entries[6].node);
    try std.testing.expect(main.prev == &entries[9].node);

    mode = .descending;
    list_sort.listSort(&mode, &shuttle, cmpByKey);
    try expectOrder(&shuttle, &.{ 4, 2, 7, 3, 5, 8 });
    try std.testing.expect(shuttle.next == &entries[4].node);
    try std.testing.expect(shuttle.prev == &entries[8].node);

    try moveFrontChecked(&main, &rebuilt);
    try moveFrontChecked(&main, &rebuilt);
    while (popFront(&shuttle)) |node| {
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        list_sort.listAddTail(node, &rebuilt);
    }
    while (popFront(&main)) |node| {
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        list_sort.listAddTail(node, &rebuilt);
    }
    try std.testing.expect(list_sort.listEmpty(&main));
    try std.testing.expect(list_sort.listEmpty(&shuttle));

    try expectOrder(&rebuilt, &.{ 6, 1, 4, 2, 7, 3, 5, 8, 0, 9 });
    try std.testing.expect(rebuilt.next == &entries[6].node);
    try std.testing.expect(rebuilt.prev == &entries[9].node);

    list_sort.listSort(null, &rebuilt, cmpAllTies);
    try expectOrder(&rebuilt, &.{ 6, 1, 4, 2, 7, 3, 5, 8, 0, 9 });
    try std.testing.expect(rebuilt.next == &entries[6].node);
    try std.testing.expect(rebuilt.prev == &entries[9].node);
}
