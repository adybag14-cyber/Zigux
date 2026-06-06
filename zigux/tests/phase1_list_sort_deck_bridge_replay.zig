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
        (if (ascending) -5 else 7)
    else
        (if (ascending) 7 else -5);
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

test "list sort deck bridge replay preserves rebuilt traversal" {
    var main: ListHead = .{};
    var front_deck: ListHead = .{};
    var back_deck: ListHead = .{};
    main.init();
    front_deck.init();
    back_deck.init();

    var entries = [_]Entry{
        .{ .key = 5, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 8, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 6, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 7, .ordinal = 6 },
        .{ .key = 4, .ordinal = 7 },
        .{ .key = 0, .ordinal = 8 },
        .{ .key = 9, .ordinal = 9 },
        .{ .key = 3, .ordinal = 10 },
        .{ .key = 6, .ordinal = 11 },
    };
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &main);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &main, cmpByKey);
    try expectTraversal(
        &main,
        &.{ 8, 1, 5, 3, 10, 7, 0, 4, 11, 6, 2, 9 },
        &.{ 0, 1, 2, 3, 3, 4, 5, 6, 6, 7, 8, 9 },
    );

    var cut_index: usize = 0;
    while (!list_sort.listEmpty(&main)) : (cut_index += 1) {
        const node = try detachFront(&main);
        if ((cut_index % 3) == 0) {
            list_sort.listAdd(node, &front_deck);
        } else {
            list_sort.listAddTail(node, &back_deck);
        }
    }
    try expectEmpty(&main);
    try expectTraversal(&front_deck, &.{ 6, 0, 3, 8 }, &.{ 7, 5, 3, 0 });
    try expectTraversal(&back_deck, &.{ 1, 5, 10, 7, 4, 11, 2, 9 }, &.{ 1, 2, 3, 4, 6, 6, 8, 9 });

    mode = .ascending;
    list_sort.listSort(&mode, &front_deck, cmpByKey);
    mode = .descending;
    list_sort.listSort(&mode, &back_deck, cmpByKey);
    try expectTraversal(&front_deck, &.{ 8, 3, 0, 6 }, &.{ 0, 3, 5, 7 });
    try expectTraversal(&back_deck, &.{ 9, 2, 4, 11, 7, 10, 5, 1 }, &.{ 9, 8, 6, 6, 4, 3, 2, 1 });

    while (!list_sort.listEmpty(&front_deck) or !list_sort.listEmpty(&back_deck)) {
        if (!list_sort.listEmpty(&front_deck)) {
            list_sort.listAddTail(try detachFront(&front_deck), &main);
        }
        if (!list_sort.listEmpty(&back_deck)) {
            list_sort.listAddTail(try detachFront(&back_deck), &main);
        }
        if (!list_sort.listEmpty(&back_deck)) {
            list_sort.listAddTail(try detachFront(&back_deck), &main);
        }
    }
    try expectEmpty(&front_deck);
    try expectEmpty(&back_deck);

    try expectTraversal(
        &main,
        &.{ 8, 9, 2, 3, 4, 11, 0, 7, 10, 6, 5, 1 },
        &.{ 0, 9, 8, 3, 6, 6, 5, 4, 3, 7, 2, 1 },
    );
    try std.testing.expect(main.next == &entries[8].node);
    try std.testing.expect(main.prev == &entries[1].node);

    list_sort.listSort(null, &main, cmpAllTies);
    try expectOrdinals(&main, &.{ 8, 9, 2, 3, 4, 11, 0, 7, 10, 6, 5, 1 });
    try std.testing.expect(main.next == &entries[8].node);
    try std.testing.expect(main.prev == &entries[1].node);

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
        &.{ 1, 5, 6, 10, 7, 0, 11, 4, 3, 2, 9, 8 },
        reverse_ordinals[0..reverse_len],
    );
}
