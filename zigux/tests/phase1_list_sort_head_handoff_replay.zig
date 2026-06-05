const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    band: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum { key_asc, key_desc, band_asc, parity_bucket };

fn cmp(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    return switch (mode.*) {
        .key_asc => compare(lhs.key, rhs.key),
        .key_desc => compare(rhs.key, lhs.key),
        .band_asc => compare(lhs.band, rhs.band),
        .parity_bucket => compare(@mod(lhs.key, 2), @mod(rhs.key, 2)),
    };
}

fn compare(lhs: i32, rhs: i32) i32 {
    if (lhs < rhs) return -1;
    if (lhs > rhs) return 1;
    return 0;
}

fn expectOrdinals(head: *const ListHead, expected: []const usize) !void {
    var actual: [16]usize = undefined;
    var idx: usize = 0;
    var current = head.next;

    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        actual[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqualSlices(usize, expected, actual[0..idx]);
}

fn expectReverseOrdinals(head: *const ListHead, expected: []const usize) !void {
    var actual: [16]usize = undefined;
    var idx: usize = 0;
    var current = head.prev;

    while (current != head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        actual[idx] = entry.ordinal;
        idx += 1;
    }

    try std.testing.expectEqualSlices(usize, expected, actual[0..idx]);
}

test "list sort preserves stability across head handoff lifecycle" {
    var main_head: ListHead = .{};
    main_head.init();
    var staging_head: ListHead = .{};
    staging_head.init();

    var entries = [_]Entry{
        .{ .key = 5, .band = 1, .ordinal = 0 },
        .{ .key = 1, .band = 0, .ordinal = 1 },
        .{ .key = 4, .band = 1, .ordinal = 2 },
        .{ .key = 2, .band = 0, .ordinal = 3 },
        .{ .key = 3, .band = 1, .ordinal = 4 },
        .{ .key = 1, .band = 2, .ordinal = 5 },
        .{ .key = 4, .band = 0, .ordinal = 6 },
        .{ .key = 2, .band = 2, .ordinal = 7 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &main_head);

    var mode = SortMode.key_asc;
    list_sort.listSort(&mode, &main_head, cmp);
    try expectOrdinals(&main_head, &.{ 1, 5, 3, 7, 4, 2, 6, 0 });

    for (0..3) |_| {
        const node = main_head.next.?;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        list_sort.listAddTail(node, &staging_head);
    }

    try expectOrdinals(&staging_head, &.{ 1, 5, 3 });
    try expectOrdinals(&main_head, &.{ 7, 4, 2, 6, 0 });

    mode = .key_desc;
    list_sort.listSort(&mode, &main_head, cmp);
    try expectOrdinals(&main_head, &.{ 0, 2, 6, 4, 7 });

    mode = .band_asc;
    list_sort.listSort(&mode, &staging_head, cmp);
    try expectOrdinals(&staging_head, &.{ 1, 3, 5 });

    while (!list_sort.listEmpty(&staging_head)) {
        const node = staging_head.prev.?;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        list_sort.listAdd(node, &main_head);
    }

    try std.testing.expect(list_sort.listEmpty(&staging_head));
    try expectOrdinals(&main_head, &.{ 1, 3, 5, 0, 2, 6, 4, 7 });

    mode = .parity_bucket;
    list_sort.listSort(&mode, &main_head, cmp);
    try expectOrdinals(&main_head, &.{ 3, 2, 6, 7, 1, 5, 0, 4 });
    try expectReverseOrdinals(&main_head, &.{ 4, 0, 5, 1, 7, 6, 2, 3 });
    try std.testing.expect(main_head.next == &entries[3].node);
    try std.testing.expect(main_head.prev == &entries[4].node);
}
