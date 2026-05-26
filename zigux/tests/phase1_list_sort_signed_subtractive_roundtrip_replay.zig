const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;
const listAddTail = list_sort.listAddTail;
const listSort = list_sort.listSort;

test "phase1 list_sort signed subtractive roundtrip replay" {
    const Entry = struct {
        key: i32,
        ordinal: usize,
        node: ListHead = .{},
    };

    const SortMode = enum { ascending, descending };

    const signed_cmp = struct {
        fn less(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
            const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            const delta = lhs.key - rhs.key;
            return if (mode.* == .ascending) delta else -delta;
        }
    }.less;

    var head: ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = -4, .ordinal = 0 },
        .{ .key = 6, .ordinal = 1 },
        .{ .key = 2, .ordinal = 2 },
        .{ .key = 6, .ordinal = 3 },
        .{ .key = -1, .ordinal = 4 },
        .{ .key = -4, .ordinal = 5 },
        .{ .key = 3, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
    };
    for (&entries) |*entry| listAddTail(&entry.node, &head);

    var mode = SortMode.descending;
    listSort(&mode, &head, signed_cmp);

    mode = .ascending;
    listSort(&mode, &head, signed_cmp);

    var keys: [entries.len]i32 = undefined;
    var ordinals: [entries.len]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqual(entries.len, idx);
    try std.testing.expectEqualSlices(i32, &.{ -4, -4, -1, 2, 2, 3, 6, 6 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 0, 5, 4, 2, 7, 6, 1, 3 }, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[0].node);
    try std.testing.expect(head.prev == &entries[3].node);
}
