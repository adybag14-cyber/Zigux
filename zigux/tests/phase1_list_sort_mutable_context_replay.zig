const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };

const CompareState = struct {
    mode: SortMode,
    calls: usize = 0,
};

const entry_count = 9;

fn contextCmp(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const state: *CompareState = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    state.calls += 1;
    const delta: i32 = if (lhs.key < rhs.key) -1 else if (lhs.key > rhs.key) 1 else 0;
    return if (state.mode == .ascending) delta else -delta;
}

fn expectForwardOrder(head: *const list_sort.ListHead, expected_keys: []const i32, expected_ordinals: []const usize) !void {
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

test "phase1 list_sort reuses mutable comparator context across mode changes" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 3, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 1, .ordinal = 4 },
        .{ .key = 4, .ordinal = 5 },
        .{ .key = 2, .ordinal = 6 },
        .{ .key = 4, .ordinal = 7 },
        .{ .key = 0, .ordinal = 8 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var state = CompareState{ .mode = .ascending };
    list_sort.listSort(&state, &head, contextCmp);
    try std.testing.expect(state.calls > 0);
    try expectForwardOrder(
        &head,
        &.{ 0, 1, 1, 2, 2, 3, 3, 4, 4 },
        &.{ 8, 1, 4, 3, 6, 0, 2, 5, 7 },
    );
    try std.testing.expect(head.next == &entries[8].node);
    try std.testing.expect(head.prev == &entries[7].node);

    const ascending_calls = state.calls;
    state.mode = .descending;
    list_sort.listSort(&state, &head, contextCmp);
    try std.testing.expect(state.calls > ascending_calls);
    try expectForwardOrder(
        &head,
        &.{ 4, 4, 3, 3, 2, 2, 1, 1, 0 },
        &.{ 5, 7, 0, 2, 3, 6, 1, 4, 8 },
    );
    try std.testing.expect(head.next == &entries[5].node);
    try std.testing.expect(head.prev == &entries[8].node);
}
