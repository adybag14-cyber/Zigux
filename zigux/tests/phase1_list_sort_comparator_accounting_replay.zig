const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const ComparatorState = struct {
    modulus: i32,
    descending: bool = false,
    calls: usize = 0,
    equal_bucket_calls: usize = 0,
    unequal_bucket_calls: usize = 0,
    checksum: u64 = 0,
};

fn bucketComparator(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const state: *ComparatorState = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    const lhs_bucket = @mod(lhs.key, state.modulus);
    const rhs_bucket = @mod(rhs.key, state.modulus);

    state.calls += 1;
    state.checksum = (state.checksum *% 131) +% @as(u64, @intCast(lhs.ordinal + 1));
    state.checksum = (state.checksum *% 131) +% @as(u64, @intCast(rhs.ordinal + 1));

    if (lhs_bucket == rhs_bucket) {
        state.equal_bucket_calls += 1;
        return 0;
    }

    state.unequal_bucket_calls += 1;
    const lhs_before_rhs = lhs_bucket < rhs_bucket;
    if (state.descending) {
        return if (lhs_before_rhs) 1 else -1;
    }
    return if (lhs_before_rhs) -1 else 1;
}

fn addEntries(head: *list_sort.ListHead, entries: []Entry) void {
    for (entries) |*entry| {
        list_sort.listAddTail(&entry.node, head);
    }
}

fn expectOrder(head: *list_sort.ListHead, expected_keys: []const i32, expected_ordinals: []const usize) !void {
    var keys: [10]i32 = undefined;
    var ordinals: [10]usize = undefined;
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

    try std.testing.expectEqual(expected_keys.len, idx);
    try std.testing.expectEqualSlices(i32, expected_keys, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, expected_ordinals, ordinals[0..idx]);
}

test "list sort preserves comparator accounting across repeated stable passes" {
    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 9, .ordinal = 0 },
        .{ .key = 4, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 8, .ordinal = 5 },
        .{ .key = 1, .ordinal = 6 },
        .{ .key = 6, .ordinal = 7 },
        .{ .key = 3, .ordinal = 8 },
        .{ .key = 0, .ordinal = 9 },
    };
    addEntries(&head, &entries);

    var state = ComparatorState{ .modulus = 3, .descending = true };
    list_sort.listSort(&state, &head, bucketComparator);

    try expectOrder(
        &head,
        &.{ 2, 5, 8, 4, 7, 1, 9, 6, 3, 0 },
        &.{ 3, 4, 5, 1, 2, 6, 0, 7, 8, 9 },
    );
    try std.testing.expect(state.calls > 0);
    try std.testing.expect(state.equal_bucket_calls > 0);
    try std.testing.expect(state.unequal_bucket_calls > 0);
    try std.testing.expect(state.checksum != 0);
    try std.testing.expect(head.next == &entries[3].node);
    try std.testing.expect(head.prev == &entries[9].node);

    const first_pass_calls = state.calls;
    const first_pass_checksum = state.checksum;
    state.modulus = 1;
    state.descending = false;
    list_sort.listSort(&state, &head, bucketComparator);

    try expectOrder(
        &head,
        &.{ 2, 5, 8, 4, 7, 1, 9, 6, 3, 0 },
        &.{ 3, 4, 5, 1, 2, 6, 0, 7, 8, 9 },
    );
    try std.testing.expect(state.calls > first_pass_calls);
    try std.testing.expect(state.checksum != first_pass_checksum);
    try std.testing.expect(state.equal_bucket_calls > state.unequal_bucket_calls);
    try std.testing.expect(head.next == &entries[3].node);
    try std.testing.expect(head.prev == &entries[9].node);
}
