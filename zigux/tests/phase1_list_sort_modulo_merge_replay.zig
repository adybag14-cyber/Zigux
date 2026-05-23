const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn moduloBucketCmp(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    const lhs_bucket = @mod(lhs.key, 3);
    const rhs_bucket = @mod(rhs.key, 3);
    if (lhs_bucket == rhs_bucket) return 0;
    return if (lhs_bucket < rhs_bucket) -1 else 1;
}

fn descendingKeyCmp(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key > rhs.key) return -1;
    if (lhs.key < rhs.key) return 1;
    return 0;
}

fn expectModuloReplayOrder(
    head: *list_sort.ListHead,
    entries: []const Entry,
    expected_keys: []const i32,
    expected_ordinals: []const usize,
    expected_reverse_ordinals: []const usize,
    expected_first: *const list_sort.ListHead,
    expected_last: *const list_sort.ListHead,
) !void {
    var keys: [12]i32 = undefined;
    var ordinals: [12]usize = undefined;
    var reverse_ordinals: [12]usize = undefined;

    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    var reverse_idx: usize = 0;
    current = head.prev;
    while (current != head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        reverse_ordinals[reverse_idx] = entry.ordinal;
        reverse_idx += 1;
    }

    try std.testing.expectEqual(@as(usize, entries.len), idx);
    try std.testing.expectEqual(@as(usize, entries.len), reverse_idx);
    try std.testing.expectEqualSlices(i32, expected_keys, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, expected_ordinals, ordinals[0..idx]);
    try std.testing.expectEqualSlices(usize, expected_reverse_ordinals, reverse_ordinals[0..reverse_idx]);
    try std.testing.expect(head.next == expected_first);
    try std.testing.expect(head.prev == expected_last);
    try std.testing.expect(expected_first.prev == head);
    try std.testing.expect(expected_last.next == head);
}

fn expectModuloReplay(head: *list_sort.ListHead, entries: []const Entry) !void {
    try expectModuloReplayOrder(
        head,
        entries,
        &.{ 3, 6, 0, 9, 10, 1, 7, 4, 8, 11, 5, 2 },
        &.{ 1, 6, 8, 10, 2, 3, 4, 5, 0, 7, 9, 11 },
        &.{ 11, 9, 7, 0, 5, 4, 3, 2, 10, 8, 6, 1 },
        &entries[1].node,
        &entries[11].node,
    );
}

test "phase1 list_sort replay preserves stable modulo bucket order across a longer merge path" {
    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 8, .ordinal = 0 },
        .{ .key = 3, .ordinal = 1 },
        .{ .key = 10, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 7, .ordinal = 4 },
        .{ .key = 4, .ordinal = 5 },
        .{ .key = 6, .ordinal = 6 },
        .{ .key = 11, .ordinal = 7 },
        .{ .key = 0, .ordinal = 8 },
        .{ .key = 5, .ordinal = 9 },
        .{ .key = 9, .ordinal = 10 },
        .{ .key = 2, .ordinal = 11 },
    };
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    list_sort.listSort(null, &head, moduloBucketCmp);

    try expectModuloReplay(&head, &entries);
}

test "phase1 list_sort replay can resort the same modulo-merged ring without changing stable order" {
    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 8, .ordinal = 0 },
        .{ .key = 3, .ordinal = 1 },
        .{ .key = 10, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 7, .ordinal = 4 },
        .{ .key = 4, .ordinal = 5 },
        .{ .key = 6, .ordinal = 6 },
        .{ .key = 11, .ordinal = 7 },
        .{ .key = 0, .ordinal = 8 },
        .{ .key = 5, .ordinal = 9 },
        .{ .key = 9, .ordinal = 10 },
        .{ .key = 2, .ordinal = 11 },
    };
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    list_sort.listSort(null, &head, moduloBucketCmp);
    list_sort.listSort(null, &head, moduloBucketCmp);

    try expectModuloReplay(&head, &entries);
}

test "phase1 list_sort replay preserves modulo bucket stability after a prior descending reorder" {
    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 8, .ordinal = 0 },
        .{ .key = 3, .ordinal = 1 },
        .{ .key = 10, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 7, .ordinal = 4 },
        .{ .key = 4, .ordinal = 5 },
        .{ .key = 6, .ordinal = 6 },
        .{ .key = 11, .ordinal = 7 },
        .{ .key = 0, .ordinal = 8 },
        .{ .key = 5, .ordinal = 9 },
        .{ .key = 9, .ordinal = 10 },
        .{ .key = 2, .ordinal = 11 },
    };
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    list_sort.listSort(null, &head, descendingKeyCmp);
    list_sort.listSort(null, &head, moduloBucketCmp);

    try expectModuloReplayOrder(
        &head,
        &entries,
        &.{ 9, 6, 3, 0, 10, 7, 4, 1, 11, 8, 5, 2 },
        &.{ 10, 6, 1, 8, 2, 4, 5, 3, 7, 0, 9, 11 },
        &.{ 11, 9, 0, 7, 3, 5, 4, 2, 8, 1, 6, 10 },
        &entries[10].node,
        &entries[11].node,
    );
}
