const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn bucketCmp(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    const lhs_bucket = @mod(lhs.key, 3);
    const rhs_bucket = @mod(rhs.key, 3);
    if (lhs_bucket == rhs_bucket) return 0;
    return if (lhs_bucket < rhs_bucket) -1 else 1;
}

fn signedContextCmp(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    const delta = lhs.key - rhs.key;
    return if (mode.* == .ascending) delta else -delta;
}

fn allTiesCmp(_: ?*anyopaque, _: *const list_sort.ListHead, _: *const list_sort.ListHead) i32 {
    return 0;
}

fn expectCircularLinks(head: *list_sort.ListHead) !void {
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
    }
}

fn collectKeys(head: *list_sort.ListHead, out: []i32) usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.key;
        idx += 1;
    }
    return idx;
}

fn collectOrdinals(head: *list_sort.ListHead, out: []usize) usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.ordinal;
        idx += 1;
    }
    return idx;
}

test "phase1 list_sort replay keeps stable bucket order after detached tail reinsertion" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 8, .ordinal = 0 },
        .{ .key = 3, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 6, .ordinal = 3 },
        .{ .key = 1, .ordinal = 4 },
        .{ .key = 7, .ordinal = 5 },
        .{ .key = 0, .ordinal = 6 },
    };
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    list_sort.listSort(null, &head, bucketCmp);
    try expectCircularLinks(&head);

    list_sort.listDel(&entries[4].node);
    try std.testing.expect(entries[4].node.next == null);
    try std.testing.expect(entries[4].node.prev == null);

    entries[4].key = 10;
    list_sort.listAddTail(&entries[4].node, &head);
    list_sort.listSort(null, &head, bucketCmp);
    try expectCircularLinks(&head);

    var keys: [7]i32 = undefined;
    var ordinals: [7]usize = undefined;
    const key_count = collectKeys(&head, &keys);
    const ordinal_count = collectOrdinals(&head, &ordinals);

    try std.testing.expectEqual(key_count, ordinal_count);
    try std.testing.expectEqualSlices(i32, &.{ 3, 6, 0, 4, 7, 10, 8 }, keys[0..key_count]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 6, 2, 5, 4, 0 }, ordinals[0..ordinal_count]);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[0].node);
}

test "phase1 list_sort replay preserves current order when a later pass ties everything" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 2, .ordinal = 0 },
        .{ .key = 5, .ordinal = 1 },
        .{ .key = 1, .ordinal = 2 },
        .{ .key = 5, .ordinal = 3 },
        .{ .key = 4, .ordinal = 4 },
        .{ .key = 1, .ordinal = 5 },
    };
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    var mode = SortMode.descending;
    list_sort.listSort(&mode, &head, signedContextCmp);
    try expectCircularLinks(&head);

    list_sort.listDel(&entries[4].node);
    try std.testing.expect(entries[4].node.next == null);
    try std.testing.expect(entries[4].node.prev == null);
    list_sort.listAddTail(&entries[4].node, &head);

    list_sort.listSort(null, &head, allTiesCmp);
    try expectCircularLinks(&head);

    var keys: [6]i32 = undefined;
    var ordinals: [6]usize = undefined;
    const key_count = collectKeys(&head, &keys);
    const ordinal_count = collectOrdinals(&head, &ordinals);

    try std.testing.expectEqual(key_count, ordinal_count);
    try std.testing.expectEqualSlices(i32, &.{ 5, 5, 2, 1, 1, 4 }, keys[0..key_count]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 0, 2, 5, 4 }, ordinals[0..ordinal_count]);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[4].node);
}
