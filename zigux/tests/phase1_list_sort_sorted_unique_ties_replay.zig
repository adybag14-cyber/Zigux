const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

test "phase1 list_sort sorted-unique result stays fixed across a later all-ties pass" {
    const Entry = struct {
        key: i32,
        ordinal: usize,
        node: ListHead = .{},
    };

    const sorted_cmp = struct {
        fn less(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            if (lhs.key < rhs.key) return -1;
            if (lhs.key > rhs.key) return 1;
            return 0;
        }
    }.less;

    const ties_cmp = struct {
        fn less(_: ?*anyopaque, _: *const ListHead, _: *const ListHead) i32 {
            return 0;
        }
    }.less;

    var head: ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 1, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 4, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 6, .ordinal = 5 },
    };
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    list_sort.listSort(null, &head, sorted_cmp);
    list_sort.listSort(null, &head, ties_cmp);

    var keys: [6]i32 = undefined;
    var ordinals: [6]usize = undefined;
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

    try std.testing.expectEqualSlices(i32, &.{ 1, 2, 3, 4, 5, 6 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 0, 1, 2, 3, 4, 5 }, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[0].node);
    try std.testing.expect(head.prev == &entries[5].node);
    try std.testing.expect(entries[0].node.prev == &head);
    try std.testing.expect(entries[5].node.next == &head);
}
