const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };
const entry_count = 9;

fn modeCmp(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (lhs.key == rhs.key) return 0;
    const asc_result: i32 = if (lhs.key < rhs.key) -1 else 1;
    return if (mode.* == .ascending) asc_result else -asc_result;
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

test "phase1 list_sort mode switch roundtrip preserves stable duplicate order" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 2, .ordinal = 0 },
        .{ .key = -1, .ordinal = 1 },
        .{ .key = 2, .ordinal = 2 },
        .{ .key = 5, .ordinal = 3 },
        .{ .key = -1, .ordinal = 4 },
        .{ .key = 0, .ordinal = 5 },
        .{ .key = 5, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = -3, .ordinal = 8 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.descending;
    list_sort.listSort(&mode, &head, modeCmp);
    try expectOrder(
        &head,
        &.{ 5, 5, 2, 2, 2, 0, -1, -1, -3 },
        &.{ 3, 6, 0, 2, 7, 5, 1, 4, 8 },
    );
    try std.testing.expect(head.next == &entries[3].node);
    try std.testing.expect(head.prev == &entries[8].node);

    mode = .ascending;
    list_sort.listSort(&mode, &head, modeCmp);
    try expectOrder(
        &head,
        &.{ -3, -1, -1, 0, 2, 2, 2, 5, 5 },
        &.{ 8, 1, 4, 5, 0, 2, 7, 3, 6 },
    );
    try std.testing.expect(head.next == &entries[8].node);
    try std.testing.expect(head.prev == &entries[6].node);
}
