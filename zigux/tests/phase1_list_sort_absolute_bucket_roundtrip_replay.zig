const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum {
    abs_ascending,
    abs_descending,
};

fn absoluteMagnitude(value: i32) i32 {
    return if (value < 0) -value else value;
}

fn absoluteBucketCmp(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    const lhs_abs = absoluteMagnitude(lhs.key);
    const rhs_abs = absoluteMagnitude(rhs.key);

    if (lhs_abs == rhs_abs) return 0;

    const ascending = lhs_abs < rhs_abs;
    return switch (mode.*) {
        .abs_ascending => if (ascending) -7 else 11,
        .abs_descending => if (ascending) 11 else -7,
    };
}

fn expectCircularLinks(head: *list_sort.ListHead) !void {
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
    }
}

test "phase1 list_sort absolute-bucket replay preserves stable ascending groups" {
    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = -5, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = -2, .ordinal = 2 },
        .{ .key = 4, .ordinal = 3 },
        .{ .key = -4, .ordinal = 4 },
        .{ .key = 1, .ordinal = 5 },
        .{ .key = -1, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.abs_ascending;
    list_sort.listSort(&mode, &head, absoluteBucketCmp);

    var keys: [8]i32 = undefined;
    var ordinals: [8]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        idx += 1;
    }

    try std.testing.expectEqualSlices(i32, &.{ 1, -1, 2, -2, 3, 4, -4, -5 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 5, 6, 1, 2, 7, 3, 4, 0 }, ordinals[0..idx]);
    try expectCircularLinks(&head);
    try std.testing.expect(head.next == &entries[5].node);
    try std.testing.expect(head.prev == &entries[0].node);
}

test "phase1 list_sort absolute-bucket roundtrip replay reuses comparator context" {
    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = -6, .ordinal = 0 },
        .{ .key = 3, .ordinal = 1 },
        .{ .key = -3, .ordinal = 2 },
        .{ .key = 5, .ordinal = 3 },
        .{ .key = -5, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = -2, .ordinal = 6 },
        .{ .key = 1, .ordinal = 7 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.abs_descending;
    list_sort.listSort(&mode, &head, absoluteBucketCmp);

    mode = .abs_ascending;
    list_sort.listSort(&mode, &head, absoluteBucketCmp);

    var keys: [8]i32 = undefined;
    var ordinals: [8]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        idx += 1;
    }

    try std.testing.expectEqualSlices(i32, &.{ 1, 2, -2, 3, -3, 5, -5, -6 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 7, 5, 6, 1, 2, 3, 4, 0 }, ordinals[0..idx]);
    try expectCircularLinks(&head);
    try std.testing.expect(head.next == &entries[7].node);
    try std.testing.expect(head.prev == &entries[0].node);
}
