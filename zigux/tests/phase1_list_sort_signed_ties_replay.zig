const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

fn expectRing(current: *const ListHead) !void {
    try std.testing.expect(current.next.?.prev == current);
    try std.testing.expect(current.prev.?.next == current);
}

test "list sort keeps descending signed order when a later pass ties everything" {
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

    const ties_cmp = struct {
        fn less(_: ?*anyopaque, _: *const ListHead, _: *const ListHead) i32 {
            return 0;
        }
    }.less;

    var head: ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = -2, .ordinal = 3 },
        .{ .key = 1, .ordinal = 4 },
        .{ .key = 7, .ordinal = 5 },
        .{ .key = -2, .ordinal = 6 },
    };
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.descending;
    list_sort.listSort(&mode, &head, signed_cmp);
    list_sort.listSort(null, &head, ties_cmp);

    var keys: [7]i32 = undefined;
    var ordinals: [7]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        try expectRing(current.?);
        idx += 1;
    }

    try std.testing.expectEqualSlices(i32, &.{ 7, 4, 4, 1, 1, -2, -2 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 5, 0, 2, 1, 4, 3, 6 }, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[5].node);
    try std.testing.expect(head.prev == &entries[6].node);
}

test "list sort keeps ascending non-unit signed order when a later pass ties everything" {
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

            if (lhs.key == rhs.key) return 0;
            const ascending = lhs.key < rhs.key;
            return if (mode.* == .ascending)
                (if (ascending) -11 else 13)
            else
                (if (ascending) 13 else -11);
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
        .{ .key = 2, .ordinal = 0 },
        .{ .key = 5, .ordinal = 1 },
        .{ .key = 1, .ordinal = 2 },
        .{ .key = 5, .ordinal = 3 },
        .{ .key = 4, .ordinal = 4 },
        .{ .key = 1, .ordinal = 5 },
    };
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.descending;
    list_sort.listSort(&mode, &head, signed_cmp);
    mode = .ascending;
    list_sort.listSort(&mode, &head, signed_cmp);
    list_sort.listSort(null, &head, ties_cmp);

    var keys: [6]i32 = undefined;
    var ordinals: [6]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        try expectRing(current.?);
        idx += 1;
    }

    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 4, 5, 5 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 2, 5, 0, 4, 1, 3 }, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[2].node);
    try std.testing.expect(head.prev == &entries[3].node);
}
