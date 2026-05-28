const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum {
    abs_then_signed,
    abs_only,
};

fn absKey(key: i32) i32 {
    return if (key < 0) -key else key;
}

fn absBucketCmp(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    const lhs_abs = absKey(lhs.key);
    const rhs_abs = absKey(rhs.key);

    if (lhs_abs < rhs_abs) return -1;
    if (lhs_abs > rhs_abs) return 1;
    if (mode.* == .abs_only or lhs.key == rhs.key) return 0;
    return if (lhs.key < rhs.key) -1 else 1;
}

fn readList(head: *const list_sort.ListHead, comptime field: enum { key, ordinal }, out: anytype) !usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = switch (field) {
            .key => entry.key,
            .ordinal => entry.ordinal,
        };
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return idx;
}

test "phase1 list_sort absolute bucket roundtrip replay" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 3, .ordinal = 0 },
        .{ .key = -1, .ordinal = 1 },
        .{ .key = 2, .ordinal = 2 },
        .{ .key = -3, .ordinal = 3 },
        .{ .key = 1, .ordinal = 4 },
        .{ .key = -2, .ordinal = 5 },
        .{ .key = 0, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
        .{ .key = -1, .ordinal = 8 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.abs_then_signed;
    list_sort.listSort(&mode, &head, absBucketCmp);

    var first_keys: [entries.len]i32 = undefined;
    var first_ordinals: [entries.len]usize = undefined;
    const first_key_len = try readList(&head, .key, &first_keys);
    const first_ordinal_len = try readList(&head, .ordinal, &first_ordinals);

    try std.testing.expectEqual(entries.len, first_key_len);
    try std.testing.expectEqual(entries.len, first_ordinal_len);
    try std.testing.expectEqualSlices(i32, &.{ 0, -1, -1, 1, -2, 2, -3, 3, 3 }, first_keys[0..first_key_len]);
    try std.testing.expectEqualSlices(usize, &.{ 6, 1, 8, 4, 5, 2, 3, 0, 7 }, first_ordinals[0..first_ordinal_len]);
    try std.testing.expect(head.next == &entries[6].node);
    try std.testing.expect(head.prev == &entries[7].node);

    mode = .abs_only;
    list_sort.listSort(&mode, &head, absBucketCmp);

    var second_keys: [entries.len]i32 = undefined;
    var second_ordinals: [entries.len]usize = undefined;
    const second_key_len = try readList(&head, .key, &second_keys);
    const second_ordinal_len = try readList(&head, .ordinal, &second_ordinals);

    try std.testing.expectEqual(entries.len, second_key_len);
    try std.testing.expectEqual(entries.len, second_ordinal_len);
    try std.testing.expectEqualSlices(i32, &.{ 0, -1, -1, 1, -2, 2, -3, 3, 3 }, second_keys[0..second_key_len]);
    try std.testing.expectEqualSlices(usize, &.{ 6, 1, 8, 4, 5, 2, 3, 0, 7 }, second_ordinals[0..second_ordinal_len]);
    try std.testing.expect(head.next == &entries[6].node);
    try std.testing.expect(head.prev == &entries[7].node);
    try std.testing.expect(entries[6].node.prev == &head);
    try std.testing.expect(entries[7].node.next == &head);
}
