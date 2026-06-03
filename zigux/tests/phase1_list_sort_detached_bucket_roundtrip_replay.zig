const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

fn cmpKey(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn cmpOrdinalDescending(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.ordinal > rhs.ordinal) return -1;
    if (lhs.ordinal < rhs.ordinal) return 1;
    return 0;
}

fn expectOrdinals(head: *const ListHead, expected: []const usize) !void {
    var ordinals: [16]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqualSlices(usize, expected, ordinals[0..idx]);
}

test "list sort preserves detached bucket order after independent bucket sort" {
    var main: ListHead = .{};
    main.init();
    var bucket: ListHead = .{};
    bucket.init();

    var entries = [_]Entry{
        .{ .key = 2, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 2, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 1, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 3, .ordinal = 6 },
    };
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &main);

    list_sort.listSort(null, &main, cmpKey);
    try expectOrdinals(&main, &.{ 1, 4, 0, 2, 5, 3, 6 });

    var current = main.next;
    while (current != &main) {
        const next = current.?.next;
        const entry: *Entry = @fieldParentPtr("node", current.?);
        if (entry.key == 2) {
            list_sort.listDel(&entry.node);
            try std.testing.expect(entry.node.next == null);
            try std.testing.expect(entry.node.prev == null);
            list_sort.listAddTail(&entry.node, &bucket);
        }
        current = next;
    }

    try expectOrdinals(&main, &.{ 1, 4, 3, 6 });
    try expectOrdinals(&bucket, &.{ 0, 2, 5 });

    list_sort.listSort(null, &bucket, cmpOrdinalDescending);
    try expectOrdinals(&bucket, &.{ 5, 2, 0 });

    while (!list_sort.listEmpty(&bucket)) {
        const node = bucket.next.?;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        list_sort.listAddTail(node, &main);
    }

    try std.testing.expect(list_sort.listEmpty(&bucket));
    try expectOrdinals(&main, &.{ 1, 4, 3, 6, 5, 2, 0 });

    list_sort.listSort(null, &main, cmpKey);
    try expectOrdinals(&main, &.{ 1, 4, 5, 2, 0, 3, 6 });
    try std.testing.expect(main.next == &entries[1].node);
    try std.testing.expect(main.prev == &entries[6].node);
}
