const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const entry_count = 10;

const BucketPlan = struct {
    offset: i32,
    modulus: i32,
    descending: bool,
    scale: i32,
};

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
    const lhs_before_rhs = lhs_bucket < rhs_bucket;
    return if (lhs_before_rhs != plan.descending) -plan.scale else plan.scale;
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

test "phase1 list_sort reuses context buckets across stable passes" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 7, .ordinal = 0 },
        .{ .key = 0, .ordinal = 1 },
        .{ .key = 5, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 9, .ordinal = 4 },
        .{ .key = 4, .ordinal = 5 },
        .{ .key = 1, .ordinal = 6 },
        .{ .key = 6, .ordinal = 7 },
        .{ .key = 3, .ordinal = 8 },
        .{ .key = 8, .ordinal = 9 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var plan = BucketPlan{
        .offset = 0,
        .modulus = 4,
        .descending = false,
        .scale = 11,
    };
    list_sort.listSort(&plan, &head, bucketCmp);
    try expectOrder(
        &head,
        &.{ 0, 4, 8, 5, 9, 1, 2, 6, 7, 3 },
        &.{ 1, 5, 9, 2, 4, 6, 3, 7, 0, 8 },
    );
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[8].node);

    plan = .{
        .offset = 1,
        .modulus = 4,
        .descending = true,
        .scale = 13,
    };
    list_sort.listSort(&plan, &head, bucketCmp);
    try expectOrder(
        &head,
        &.{ 2, 6, 5, 9, 1, 0, 4, 8, 7, 3 },
        &.{ 3, 7, 2, 4, 6, 1, 5, 9, 0, 8 },
    );
    try std.testing.expect(head.next == &entries[3].node);
    try std.testing.expect(head.prev == &entries[8].node);
}
