const std = @import("std");
const list_sort = @import("list_sort");

const Fixture = struct {
    list_sort: struct {
        tri_sorted_keys: []const i32,
        tri_sorted_ordinals: []const usize,
        bool_sorted_keys: []const i32,
        bool_sorted_ordinals: []const usize,
    },
};

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn loadFixture(allocator: std.mem.Allocator) !std.json.Parsed(Fixture) {
    return std.json.parseFromSlice(Fixture, allocator, @embedFile("fixtures/phase1_helpers.json"), .{
        .ignore_unknown_fields = true,
    });
}

fn collectSorted(
    head: *list_sort.ListHead,
    keys: []i32,
    ordinals: []usize,
) !usize {
    var count: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[count] = entry.key;
        ordinals[count] = entry.ordinal;
        count += 1;
    }
    return count;
}

test "phase1 list_sort replay imports the live helper" {
    try std.testing.expect(@hasDecl(list_sort, "listSort"));
    try std.testing.expect(@hasDecl(list_sort, "listAddTail"));
}

test "phase1 list_sort replay matches committed parity fixture" {
    var parsed = try loadFixture(std.testing.allocator);
    defer parsed.deinit();
    const fixture = parsed.value;

    const tri_cmp = struct {
        fn compare(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            if (lhs.key < rhs.key) return -1;
            if (lhs.key > rhs.key) return 1;
            return 0;
        }
    }.compare;

    const bool_cmp = struct {
        fn compare(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            return @intFromBool(lhs.key > rhs.key);
        }
    }.compare;

    var tri_head: list_sort.ListHead = .{};
    tri_head.init();
    var tri_entries = [_]Entry{
        .{ .key = 2, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
    };
    for (&tri_entries) |*entry| {
        list_sort.listAddTail(&entry.node, &tri_head);
    }
    list_sort.listSort(null, &tri_head, tri_cmp);

    var tri_keys: [5]i32 = undefined;
    var tri_ordinals: [5]usize = undefined;
    const tri_count = try collectSorted(&tri_head, &tri_keys, &tri_ordinals);
    try std.testing.expectEqual(fixture.list_sort.tri_sorted_keys.len, tri_count);
    try std.testing.expectEqualSlices(i32, fixture.list_sort.tri_sorted_keys, tri_keys[0..tri_count]);
    try std.testing.expectEqualSlices(usize, fixture.list_sort.tri_sorted_ordinals, tri_ordinals[0..tri_count]);

    var bool_head: list_sort.ListHead = .{};
    bool_head.init();
    var bool_entries = [_]Entry{
        .{ .key = 2, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
    };
    for (&bool_entries) |*entry| {
        list_sort.listAddTail(&entry.node, &bool_head);
    }
    list_sort.listSort(null, &bool_head, bool_cmp);

    var bool_keys: [5]i32 = undefined;
    var bool_ordinals: [5]usize = undefined;
    const bool_count = try collectSorted(&bool_head, &bool_keys, &bool_ordinals);
    try std.testing.expectEqual(fixture.list_sort.bool_sorted_keys.len, bool_count);
    try std.testing.expectEqualSlices(i32, fixture.list_sort.bool_sorted_keys, bool_keys[0..bool_count]);
    try std.testing.expectEqualSlices(usize, fixture.list_sort.bool_sorted_ordinals, bool_ordinals[0..bool_count]);
}

test "phase1 list_sort replay covers signed subtractive ordering with intact links" {
    const signed_cmp = struct {
        fn compare(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            return lhs.key - rhs.key;
        }
    }.compare;

    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = -2, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = -2, .ordinal = 3 },
        .{ .key = 0, .ordinal = 4 },
        .{ .key = -5, .ordinal = 5 },
        .{ .key = 7, .ordinal = 6 },
    };
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }
    list_sort.listSort(null, &head, signed_cmp);

    var keys: [7]i32 = undefined;
    var ordinals: [7]usize = undefined;
    var count: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[count] = entry.key;
        ordinals[count] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, entries.len), count);
    try std.testing.expectEqualSlices(i32, &.{ -5, -2, -2, 0, 4, 7, 7 }, keys[0..count]);
    try std.testing.expectEqualSlices(usize, &.{ 5, 1, 3, 4, 0, 2, 6 }, ordinals[0..count]);
    try std.testing.expect(head.next == &entries[5].node);
    try std.testing.expect(head.prev == &entries[6].node);
    try std.testing.expect(entries[5].node.prev == &head);
    try std.testing.expect(entries[6].node.next == &head);
}
