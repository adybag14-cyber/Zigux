const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn cmpByKey(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (lhs.key == rhs.key) return 0;
    const ascending = lhs.key < rhs.key;
    return if (mode.* == .ascending)
        (if (ascending) -3 else 11)
    else
        (if (ascending) 11 else -3);
}

fn cmpAllTies(_: ?*anyopaque, _: *const ListHead, _: *const ListHead) i32 {
    return 0;
}

fn detachFront(head: *ListHead) !*ListHead {
    const node = head.next.?;
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    return node;
}

fn detachBack(head: *ListHead) !*ListHead {
    const node = head.prev.?;
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    return node;
}

fn expectEmpty(head: *const ListHead) !void {
    try std.testing.expect(list_sort.listEmpty(head));
    try std.testing.expect(head.next == head);
    try std.testing.expect(head.prev == head);
}

fn expectTraversal(head: *const ListHead, expected_ordinals: []const usize, expected_keys: []const i32) !void {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        try std.testing.expect(idx < expected_ordinals.len);
        try std.testing.expectEqual(expected_ordinals[idx], entry.ordinal);
        try std.testing.expectEqual(expected_keys[idx], entry.key);
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    try std.testing.expectEqual(expected_ordinals.len, idx);
}

fn expectOrdinals(head: *const ListHead, expected_ordinals: []const usize) !void {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        try std.testing.expect(idx < expected_ordinals.len);
        try std.testing.expectEqual(expected_ordinals[idx], entry.ordinal);
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    try std.testing.expectEqual(expected_ordinals.len, idx);
}

test "list sort tail splice roundtrip preserves appended run order" {
    var main: ListHead = .{};
    var tail_run: ListHead = .{};
    main.init();
    tail_run.init();

    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 9, .ordinal = 1 },
        .{ .key = 1, .ordinal = 2 },
        .{ .key = 7, .ordinal = 3 },
        .{ .key = 2, .ordinal = 4 },
        .{ .key = 6, .ordinal = 5 },
        .{ .key = 3, .ordinal = 6 },
        .{ .key = 8, .ordinal = 7 },
        .{ .key = 5, .ordinal = 8 },
        .{ .key = 0, .ordinal = 9 },
        .{ .key = 7, .ordinal = 10 },
        .{ .key = 2, .ordinal = 11 },
    };
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &main);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &main, cmpByKey);
    try expectTraversal(
        &main,
        &.{ 9, 2, 4, 11, 6, 0, 8, 5, 3, 10, 7, 1 },
        &.{ 0, 1, 2, 2, 3, 4, 5, 6, 7, 7, 8, 9 },
    );

    var detached: usize = 0;
    while (detached < 5) : (detached += 1) {
        list_sort.listAddTail(try detachBack(&main), &tail_run);
    }
    try expectTraversal(&main, &.{ 9, 2, 4, 11, 6, 0, 8 }, &.{ 0, 1, 2, 2, 3, 4, 5 });
    try expectTraversal(&tail_run, &.{ 1, 7, 10, 3, 5 }, &.{ 9, 8, 7, 7, 6 });

    mode = .descending;
    list_sort.listSort(&mode, &main, cmpByKey);
    mode = .ascending;
    list_sort.listSort(&mode, &tail_run, cmpByKey);
    try expectTraversal(&main, &.{ 8, 0, 6, 4, 11, 2, 9 }, &.{ 5, 4, 3, 2, 2, 1, 0 });
    try expectTraversal(&tail_run, &.{ 5, 10, 3, 7, 1 }, &.{ 6, 7, 7, 8, 9 });

    while (!list_sort.listEmpty(&tail_run)) {
        list_sort.listAddTail(try detachFront(&tail_run), &main);
    }
    try expectEmpty(&tail_run);
    try expectTraversal(
        &main,
        &.{ 8, 0, 6, 4, 11, 2, 9, 5, 10, 3, 7, 1 },
        &.{ 5, 4, 3, 2, 2, 1, 0, 6, 7, 7, 8, 9 },
    );

    detached = 0;
    while (detached < 5) : (detached += 1) {
        list_sort.listAdd(try detachBack(&main), &main);
    }
    try expectTraversal(
        &main,
        &.{ 5, 10, 3, 7, 1, 8, 0, 6, 4, 11, 2, 9 },
        &.{ 6, 7, 7, 8, 9, 5, 4, 3, 2, 2, 1, 0 },
    );
    try std.testing.expect(main.next == &entries[5].node);
    try std.testing.expect(main.prev == &entries[9].node);

    list_sort.listSort(null, &main, cmpAllTies);
    try expectOrdinals(&main, &.{ 5, 10, 3, 7, 1, 8, 0, 6, 4, 11, 2, 9 });
    try std.testing.expect(main.next == &entries[5].node);
    try std.testing.expect(main.prev == &entries[9].node);

    var reverse_ordinals: [entries.len]usize = undefined;
    var reverse_len: usize = 0;
    var current = main.prev;
    while (current != &main) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        reverse_ordinals[reverse_len] = entry.ordinal;
        reverse_len += 1;
    }
    try std.testing.expectEqualSlices(
        usize,
        &.{ 9, 2, 11, 4, 6, 0, 8, 1, 7, 3, 10, 5 },
        reverse_ordinals[0..reverse_len],
    );
}
