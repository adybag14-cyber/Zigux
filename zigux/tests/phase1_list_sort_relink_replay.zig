const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn cmpAscending(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn expectCircularLinks(head: *list_sort.ListHead) !void {
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
    }
}

fn collectKeys(head: *list_sort.ListHead, out: []i32) usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.key;
        idx += 1;
    }
    return idx;
}

fn collectOrdinals(head: *list_sort.ListHead, out: []usize) usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.ordinal;
        idx += 1;
    }
    return idx;
}

test "phase1 list_sort replay reuses detached nodes through head insertion and resort" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
    };

    list_sort.listAddTail(&entries[0].node, &head);
    list_sort.listAdd(&entries[1].node, &head);
    list_sort.listAddTail(&entries[2].node, &head);
    list_sort.listAdd(&entries[3].node, &head);

    list_sort.listSort(null, &head, cmpAscending);
    try expectCircularLinks(&head);

    var first_pass_keys: [4]i32 = undefined;
    const first_count = collectKeys(&head, &first_pass_keys);
    try std.testing.expectEqualSlices(i32, &.{ 1, 2, 3, 4 }, first_pass_keys[0..first_count]);

    list_sort.listDel(&entries[2].node);
    try std.testing.expect(entries[2].node.next == null);
    try std.testing.expect(entries[2].node.prev == null);

    entries[2].key = 0;
    list_sort.listAdd(&entries[2].node, &head);
    list_sort.listSort(null, &head, cmpAscending);
    try expectCircularLinks(&head);

    var second_pass_keys: [4]i32 = undefined;
    const second_count = collectKeys(&head, &second_pass_keys);
    try std.testing.expectEqualSlices(i32, &.{ 0, 1, 2, 4 }, second_pass_keys[0..second_count]);
    try std.testing.expect(head.next == &entries[2].node);
    try std.testing.expect(head.prev == &entries[0].node);
}

test "phase1 list_sort replay keeps stable equal-key order after head reinsertion" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 2, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 2, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 2, .ordinal = 4 },
    };

    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    list_sort.listSort(null, &head, cmpAscending);
    try expectCircularLinks(&head);

    list_sort.listDel(&entries[4].node);
    try std.testing.expect(entries[4].node.next == null);
    try std.testing.expect(entries[4].node.prev == null);

    entries[4].key = 2;
    list_sort.listAdd(&entries[4].node, &head);
    list_sort.listSort(null, &head, cmpAscending);
    try expectCircularLinks(&head);

    var ordinals: [5]usize = undefined;
    const count = collectOrdinals(&head, &ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 1, 4, 0, 2, 3 }, ordinals[0..count]);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[3].node);
}
