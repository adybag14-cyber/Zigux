const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn cmpKey(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
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

fn cmpModBucket(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    const lhs_bucket = @mod(lhs.key, 4);
    const rhs_bucket = @mod(rhs.key, 4);
    if (lhs_bucket == rhs_bucket) return 0;
    return if (lhs_bucket < rhs_bucket) -1 else 1;
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

fn collectKeys(head: *const list_sort.ListHead, out: []i32) !usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.key;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return idx;
}

fn popFront(head: *list_sort.ListHead) ?*list_sort.ListHead {
    if (list_sort.listEmpty(head)) return null;
    const node = head.next.?;
    list_sort.listDel(node);
    std.testing.expect(node.next == null) catch unreachable;
    std.testing.expect(node.prev == null) catch unreachable;
    return node;
}

test "list sort survives zigzag split sort weave and stable bucket replay" {
    var entries = [_]Entry{
        .{ .key = 12, .ordinal = 0 },
        .{ .key = 3, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = 12, .ordinal = 3 },
        .{ .key = 0, .ordinal = 4 },
        .{ .key = 5, .ordinal = 5 },
        .{ .key = 9, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = 10, .ordinal = 8 },
        .{ .key = 5, .ordinal = 9 },
        .{ .key = 14, .ordinal = 10 },
        .{ .key = 1, .ordinal = 11 },
        .{ .key = 6, .ordinal = 12 },
        .{ .key = 13, .ordinal = 13 },
    };

    var head: list_sort.ListHead = .{};
    var left: list_sort.ListHead = .{};
    var right: list_sort.ListHead = .{};
    head.init();
    left.init();
    right.init();

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &head, cmpKey);

    var sorted_ordinals: [entries.len]usize = undefined;
    const sorted_count = try collectOrdinals(&head, &sorted_ordinals);
    try std.testing.expectEqual(entries.len, sorted_count);
    try std.testing.expectEqualSlices(usize, &.{ 4, 11, 7, 1, 5, 9, 12, 2, 6, 8, 0, 3, 13, 10 }, sorted_ordinals[0..sorted_count]);

    var split_index: usize = 0;
    while (!list_sort.listEmpty(&head)) : (split_index += 1) {
        const node = popFront(&head).?;
        if ((split_index & 1) == 0) {
            list_sort.listAddTail(node, &left);
        } else {
            list_sort.listAddTail(node, &right);
        }
    }
    try std.testing.expect(list_sort.listEmpty(&head));

    mode = .ascending;
    list_sort.listSort(&mode, &left, cmpKey);
    mode = .descending;
    list_sort.listSort(&mode, &right, cmpKey);

    var left_ordinals: [entries.len]usize = undefined;
    var right_ordinals: [entries.len]usize = undefined;
    const left_count = try collectOrdinals(&left, &left_ordinals);
    const right_count = try collectOrdinals(&right, &right_ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 4, 7, 5, 12, 6, 0, 13 }, left_ordinals[0..left_count]);
    try std.testing.expectEqualSlices(usize, &.{ 10, 3, 8, 2, 9, 1, 11 }, right_ordinals[0..right_count]);

    while (true) {
        const from_right = popFront(&right);
        if (from_right) |node| list_sort.listAddTail(node, &head);

        const from_left = popFront(&left);
        if (from_left) |node| list_sort.listAddTail(node, &head);

        if (from_right == null and from_left == null) break;
    }
    try std.testing.expect(list_sort.listEmpty(&left));
    try std.testing.expect(list_sort.listEmpty(&right));

    var woven_ordinals: [entries.len]usize = undefined;
    var woven_keys: [entries.len]i32 = undefined;
    const woven_count = try collectOrdinals(&head, &woven_ordinals);
    _ = try collectKeys(&head, &woven_keys);
    try std.testing.expectEqualSlices(usize, &.{ 10, 4, 3, 7, 8, 5, 2, 12, 9, 6, 1, 0, 11, 13 }, woven_ordinals[0..woven_count]);

    list_sort.listSort(null, &head, cmpModBucket);

    var expected_bucket_ordinals: [entries.len]usize = undefined;
    var expected_count: usize = 0;
    for (0..4) |bucket| {
        for (woven_ordinals[0..woven_count]) |ordinal| {
            if (@mod(entries[ordinal].key, 4) == @as(i32, @intCast(bucket))) {
                expected_bucket_ordinals[expected_count] = ordinal;
                expected_count += 1;
            }
        }
    }

    var final_ordinals: [entries.len]usize = undefined;
    var final_keys: [entries.len]i32 = undefined;
    const final_count = try collectOrdinals(&head, &final_ordinals);
    _ = try collectKeys(&head, &final_keys);
    try std.testing.expectEqual(expected_count, final_count);
    try std.testing.expectEqualSlices(usize, expected_bucket_ordinals[0..expected_count], final_ordinals[0..final_count]);
    try std.testing.expectEqualSlices(i32, &.{ 0, 12, 12, 5, 5, 9, 1, 13, 14, 2, 10, 6, 7, 3 }, final_keys[0..final_count]);
    try std.testing.expect(head.next == &entries[4].node);
    try std.testing.expect(head.prev == &entries[1].node);
}
