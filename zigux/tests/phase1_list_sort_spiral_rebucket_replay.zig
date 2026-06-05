const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn keyedCmp(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
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

fn tiesCmp(_: ?*anyopaque, _: *const ListHead, _: *const ListHead) i32 {
    return 0;
}

fn expectList(head: *ListHead, expected_ordinals: []const usize, expected_keys: []const i32) !void {
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

fn expectOrdinals(head: *ListHead, expected_ordinals: []const usize) !void {
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

fn detachFirst(head: *ListHead) !*ListHead {
    const node = head.next.?;
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    return node;
}

test "list sort survives spiral staging and rebucket replay" {
    var main: ListHead = .{};
    var left_stage: ListHead = .{};
    var right_stage: ListHead = .{};
    main.init();
    left_stage.init();
    right_stage.init();

    var entries = [_]Entry{
        .{ .key = 6, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 9, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 7, .ordinal = 4 },
        .{ .key = 4, .ordinal = 5 },
        .{ .key = 1, .ordinal = 6 },
        .{ .key = 8, .ordinal = 7 },
        .{ .key = 4, .ordinal = 8 },
        .{ .key = 5, .ordinal = 9 },
    };
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &main);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &main, keyedCmp);
    try expectList(
        &main,
        &.{ 6, 1, 3, 5, 8, 9, 0, 4, 7, 2 },
        &.{ 1, 2, 2, 4, 4, 5, 6, 7, 8, 9 },
    );

    var drain_index: usize = 0;
    while (!list_sort.listEmpty(&main)) : (drain_index += 1) {
        const node = try detachFirst(&main);
        if ((drain_index & 1) == 0) {
            list_sort.listAddTail(node, &left_stage);
        } else {
            list_sort.listAdd(node, &right_stage);
        }
    }

    try std.testing.expect(list_sort.listEmpty(&main));
    try expectList(&left_stage, &.{ 6, 3, 8, 0, 7 }, &.{ 1, 2, 4, 6, 8 });
    try expectList(&right_stage, &.{ 2, 4, 9, 5, 1 }, &.{ 9, 7, 5, 4, 2 });

    mode = .descending;
    list_sort.listSort(&mode, &left_stage, keyedCmp);
    mode = .ascending;
    list_sort.listSort(&mode, &right_stage, keyedCmp);
    try expectList(&left_stage, &.{ 7, 0, 8, 3, 6 }, &.{ 8, 6, 4, 2, 1 });
    try expectList(&right_stage, &.{ 1, 5, 9, 4, 2 }, &.{ 2, 4, 5, 7, 9 });

    while (!list_sort.listEmpty(&left_stage) or !list_sort.listEmpty(&right_stage)) {
        if (!list_sort.listEmpty(&right_stage)) {
            list_sort.listAddTail(try detachFirst(&right_stage), &main);
        }
        if (!list_sort.listEmpty(&left_stage)) {
            list_sort.listAddTail(try detachFirst(&left_stage), &main);
        }
    }

    try std.testing.expect(list_sort.listEmpty(&left_stage));
    try std.testing.expect(list_sort.listEmpty(&right_stage));
    try expectList(
        &main,
        &.{ 1, 7, 5, 0, 9, 8, 4, 3, 2, 6 },
        &.{ 2, 8, 4, 6, 5, 4, 7, 2, 9, 1 },
    );
    try std.testing.expect(main.next == &entries[1].node);
    try std.testing.expect(main.prev == &entries[6].node);

    list_sort.listSort(null, &main, tiesCmp);
    try expectOrdinals(&main, &.{ 1, 7, 5, 0, 9, 8, 4, 3, 2, 6 });
    try std.testing.expect(main.next == &entries[1].node);
    try std.testing.expect(main.prev == &entries[6].node);
}
