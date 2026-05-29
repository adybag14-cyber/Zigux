const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const sorted_count = 10;
const parked_count = 4;

fn ascendingCmp(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn expectForwardOrder(head: *const list_sort.ListHead, expected_keys: []const i32, expected_ordinals: []const usize) !void {
    var keys: [sorted_count]i32 = undefined;
    var ordinals: [sorted_count]usize = undefined;
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

fn expectParkedOrder(head: *const list_sort.ListHead, expected_ordinals: []const usize) !void {
    var ordinals: [parked_count]usize = undefined;
    var index: usize = 0;
    var current = head.next;

    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        ordinals[index] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        index += 1;
    }

    try std.testing.expectEqual(expected_ordinals.len, index);
    try std.testing.expectEqualSlices(usize, expected_ordinals, ordinals[0..index]);
}

test "phase1 list_sort only rewires the selected circular list head" {
    var sorted_head: list_sort.ListHead = .{};
    sorted_head.init();
    var parked_head: list_sort.ListHead = .{};
    parked_head.init();

    var sorted_entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 2, .ordinal = 4 },
        .{ .key = 4, .ordinal = 5 },
        .{ .key = 0, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = 3, .ordinal = 8 },
        .{ .key = 0, .ordinal = 9 },
    };
    var parked_entries = [_]Entry{
        .{ .key = 99, .ordinal = 10 },
        .{ .key = -7, .ordinal = 11 },
        .{ .key = 99, .ordinal = 12 },
        .{ .key = 5, .ordinal = 13 },
    };

    for (&sorted_entries) |*entry| list_sort.listAddTail(&entry.node, &sorted_head);
    for (&parked_entries) |*entry| list_sort.listAddTail(&entry.node, &parked_head);

    list_sort.listSort(null, &sorted_head, ascendingCmp);

    try expectForwardOrder(
        &sorted_head,
        &.{ 0, 0, 1, 1, 2, 2, 3, 3, 4, 4 },
        &.{ 6, 9, 1, 3, 4, 7, 2, 8, 0, 5 },
    );
    try std.testing.expect(sorted_head.next == &sorted_entries[6].node);
    try std.testing.expect(sorted_head.prev == &sorted_entries[5].node);
    try std.testing.expect(sorted_entries[6].node.prev == &sorted_head);
    try std.testing.expect(sorted_entries[5].node.next == &sorted_head);

    try expectParkedOrder(&parked_head, &.{ 10, 11, 12, 13 });
    try std.testing.expect(parked_head.next == &parked_entries[0].node);
    try std.testing.expect(parked_head.prev == &parked_entries[3].node);
    try std.testing.expect(parked_entries[0].node.prev == &parked_head);
    try std.testing.expect(parked_entries[3].node.next == &parked_head);
}
