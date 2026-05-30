const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const entry_count = 12;

const BucketPlan = struct {
    offset: i32,
    modulus: i32,
};

fn allTies(_: ?*anyopaque, _: *const list_sort.ListHead, _: *const list_sort.ListHead) i32 {
    return 0;
}

fn bucket(plan: *const BucketPlan, key: i32) i32 {
    return @mod(key + plan.offset, plan.modulus);
}

fn bucketCmp(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const plan: *const BucketPlan = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    const lhs_bucket = bucket(plan, lhs.key);
    const rhs_bucket = bucket(plan, rhs.key);

    if (lhs_bucket == rhs_bucket) return 0;
    return if (lhs_bucket < rhs_bucket) -17 else 17;
}

fn expectOrder(head: *const list_sort.ListHead, expected_keys: []const i32, expected_ordinals: []const usize) !void {
    var keys: [entry_count]i32 = undefined;
    var ordinals: [entry_count]usize = undefined;
    var index: usize = 0;
    var current = head.next;

    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[index] = entry.key;
        ordinals[index] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        index += 1;
    }

    try std.testing.expectEqual(expected_keys.len, index);
    try std.testing.expectEqualSlices(i32, expected_keys, keys[0..index]);
    try std.testing.expectEqualSlices(usize, expected_ordinals, ordinals[0..index]);
}

test "phase1 list_sort refines a tie-preserved list with bucket ordering" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 11, .ordinal = 0 },
        .{ .key = -2, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 9, .ordinal = 3 },
        .{ .key = 0, .ordinal = 4 },
        .{ .key = 7, .ordinal = 5 },
        .{ .key = -5, .ordinal = 6 },
        .{ .key = 14, .ordinal = 7 },
        .{ .key = 2, .ordinal = 8 },
        .{ .key = -8, .ordinal = 9 },
        .{ .key = 5, .ordinal = 10 },
        .{ .key = 12, .ordinal = 11 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    list_sort.listSort(null, &head, allTies);
    try expectOrder(
        &head,
        &.{ 11, -2, 4, 9, 0, 7, -5, 14, 2, -8, 5, 12 },
        &.{ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 },
    );
    try std.testing.expect(head.next == &entries[0].node);
    try std.testing.expect(head.prev == &entries[11].node);

    const plan = BucketPlan{ .offset = 2, .modulus = 5 };
    list_sort.listSort(@constCast(&plan), &head, bucketCmp);
    try expectOrder(
        &head,
        &.{ -2, 4, 9, 14, 0, -5, 5, 11, 7, 2, -8, 12 },
        &.{ 1, 2, 3, 7, 4, 6, 10, 0, 5, 8, 9, 11 },
    );
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[11].node);
}
