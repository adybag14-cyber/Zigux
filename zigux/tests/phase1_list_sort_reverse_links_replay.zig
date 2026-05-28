const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn collectForward(head: *list_sort.ListHead, ordinals: []usize) usize {
    var count: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        ordinals[count] = entry.ordinal;
        count += 1;
    }
    return count;
}

fn collectBackward(head: *list_sort.ListHead, ordinals: []usize) usize {
    var count: usize = 0;
    var current = head.prev;
    while (current != head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        ordinals[count] = entry.ordinal;
        count += 1;
    }
    return count;
}

test "phase1 list_sort replay keeps reverse links aligned after reordering" {
    const cmp = struct {
        fn compare(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            if (lhs.key < rhs.key) return -1;
            if (lhs.key > rhs.key) return 1;
            return 0;
        }
    }.compare;

    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
    };
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    list_sort.listSort(null, &head, cmp);

    var forward_ordinals: [4]usize = undefined;
    var backward_ordinals: [4]usize = undefined;

    const forward_count = collectForward(&head, &forward_ordinals);
    const backward_count = collectBackward(&head, &backward_ordinals);

    try std.testing.expectEqual(@as(usize, entries.len), forward_count);
    try std.testing.expectEqual(@as(usize, entries.len), backward_count);
    try std.testing.expectEqualSlices(usize, &.{ 3, 1, 0, 2 }, forward_ordinals[0..forward_count]);
    try std.testing.expectEqualSlices(usize, &.{ 2, 0, 1, 3 }, backward_ordinals[0..backward_count]);
    try std.testing.expect(head.next == &entries[3].node);
    try std.testing.expect(head.prev == &entries[2].node);
    try std.testing.expect(entries[3].node.prev == &head);
    try std.testing.expect(entries[2].node.next == &head);

    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
    }
}
