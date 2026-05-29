const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const entry_count = 9;

const SortMode = enum { ascending, descending };

fn modeCmp(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (lhs.key == rhs.key) return 0;
    const ascending = lhs.key < rhs.key;
    return if ((mode.* == .ascending) == ascending) -1 else 1;
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

test "phase1 list_sort stabilizes mixed insertions after an initial sort" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 3, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 2, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 1, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
        .{ .key = 2, .ordinal = 8 },
    };

    for (entries[0..5]) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &head, modeCmp);
    try expectOrder(
        &head,
        &.{ 1, 1, 2, 3, 3 },
        &.{ 1, 3, 2, 0, 4 },
    );

    list_sort.listAdd(&entries[5].node, &head);
    list_sort.listAddTail(&entries[6].node, &head);
    list_sort.listAdd(&entries[7].node, &head);
    list_sort.listAddTail(&entries[8].node, &head);
    try expectOrder(
        &head,
        &.{ 3, 2, 1, 1, 2, 3, 3, 1, 2 },
        &.{ 7, 5, 1, 3, 2, 0, 4, 6, 8 },
    );

    mode = .ascending;
    list_sort.listSort(&mode, &head, modeCmp);
    try expectOrder(
        &head,
        &.{ 1, 1, 1, 2, 2, 2, 3, 3, 3 },
        &.{ 1, 3, 6, 5, 2, 8, 7, 0, 4 },
    );
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[4].node);

    mode = .descending;
    list_sort.listSort(&mode, &head, modeCmp);
    try expectOrder(
        &head,
        &.{ 3, 3, 3, 2, 2, 2, 1, 1, 1 },
        &.{ 7, 0, 4, 5, 2, 8, 1, 3, 6 },
    );
    try std.testing.expect(head.next == &entries[7].node);
    try std.testing.expect(head.prev == &entries[6].node);
}
