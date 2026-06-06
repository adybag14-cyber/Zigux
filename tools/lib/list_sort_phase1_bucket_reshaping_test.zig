const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const BucketMode = enum {
    mod4_ascending,
    parity_then_descending_key,
};

fn compareBuckets(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const BucketMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    switch (mode.*) {
        .mod4_ascending => {
            const lhs_bucket = @mod(lhs.key, 4);
            const rhs_bucket = @mod(rhs.key, 4);
            if (lhs_bucket == rhs_bucket) return 0;
            return if (lhs_bucket < rhs_bucket) -3 else 5;
        },
        .parity_then_descending_key => {
            const lhs_parity = @mod(lhs.key, 2);
            const rhs_parity = @mod(rhs.key, 2);
            if (lhs_parity != rhs_parity) {
                return if (lhs_parity < rhs_parity) -7 else 9;
            }
            if (lhs.key == rhs.key) return 0;
            return if (lhs.key > rhs.key) -11 else 13;
        },
    }
}

fn compareAllTies(_: ?*anyopaque, _: *const ListHead, _: *const ListHead) i32 {
    return 0;
}

fn assertTraversal(
    head: *const ListHead,
    entries: []Entry,
    expected_keys: []const i32,
    expected_ordinals: []const usize,
) !void {
    var keys: [16]i32 = undefined;
    var ordinals: [16]usize = undefined;

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

    try std.testing.expectEqualSlices(i32, expected_keys, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, expected_ordinals, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[expected_ordinals[0]].node);
    try std.testing.expect(head.prev == &entries[expected_ordinals[expected_ordinals.len - 1]].node);
}

test "list sort reshapes stable bucket order across repeated context passes" {
    var head: ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 10, .ordinal = 0 },
        .{ .key = 3, .ordinal = 1 },
        .{ .key = 8, .ordinal = 2 },
        .{ .key = 5, .ordinal = 3 },
        .{ .key = 6, .ordinal = 4 },
        .{ .key = 1, .ordinal = 5 },
        .{ .key = 12, .ordinal = 6 },
        .{ .key = 7, .ordinal = 7 },
        .{ .key = 2, .ordinal = 8 },
        .{ .key = 9, .ordinal = 9 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = BucketMode.mod4_ascending;
    list_sort.listSort(&mode, &head, compareBuckets);
    try assertTraversal(
        &head,
        entries[0..],
        &.{ 8, 12, 5, 1, 9, 10, 6, 2, 3, 7 },
        &.{ 2, 6, 3, 5, 9, 0, 4, 8, 1, 7 },
    );

    mode = .parity_then_descending_key;
    list_sort.listSort(&mode, &head, compareBuckets);
    try assertTraversal(
        &head,
        entries[0..],
        &.{ 12, 10, 8, 6, 2, 9, 7, 5, 3, 1 },
        &.{ 6, 0, 2, 4, 8, 9, 7, 3, 1, 5 },
    );

    list_sort.listSort(null, &head, compareAllTies);
    try assertTraversal(
        &head,
        entries[0..],
        &.{ 12, 10, 8, 6, 2, 9, 7, 5, 3, 1 },
        &.{ 6, 0, 2, 4, 8, 9, 7, 3, 1, 5 },
    );
}
