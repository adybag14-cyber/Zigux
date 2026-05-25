const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn cmpSigned(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    const delta = lhs.key - rhs.key;
    return if (mode.* == .ascending) delta else -delta;
}

fn cmpAllTies(_: ?*anyopaque, _: *const list_sort.ListHead, _: *const list_sort.ListHead) i32 {
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

test "phase1 list_sort signed replay keeps stable duplicates with non-unit comparator magnitudes" {
    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = -2, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = -2, .ordinal = 3 },
        .{ .key = 0, .ordinal = 4 },
        .{ .key = -5, .ordinal = 5 },
        .{ .key = 7, .ordinal = 6 },
    };
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &head, cmpSigned);
    try expectCircularLinks(&head);

    var keys: [7]i32 = undefined;
    var ordinals: [7]usize = undefined;
    const key_count = collectKeys(&head, &keys);
    const ordinal_count = collectOrdinals(&head, &ordinals);

    try std.testing.expectEqualSlices(i32, &.{ -5, -2, -2, 0, 4, 7, 7 }, keys[0..key_count]);
    try std.testing.expectEqualSlices(usize, &.{ 5, 1, 3, 4, 0, 2, 6 }, ordinals[0..ordinal_count]);
    try std.testing.expect(head.next == &entries[5].node);
    try std.testing.expect(head.prev == &entries[6].node);
}

test "phase1 list_sort signed replay reuses comparator context across repeated reordering" {
    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = -3, .ordinal = 0 },
        .{ .key = 7, .ordinal = 1 },
        .{ .key = -1, .ordinal = 2 },
        .{ .key = 7, .ordinal = 3 },
        .{ .key = 0, .ordinal = 4 },
        .{ .key = -3, .ordinal = 5 },
        .{ .key = 5, .ordinal = 6 },
    };
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    var mode = SortMode.descending;
    list_sort.listSort(&mode, &head, cmpSigned);
    try expectCircularLinks(&head);

    mode = .ascending;
    list_sort.listSort(&mode, &head, cmpSigned);
    try expectCircularLinks(&head);

    var keys: [7]i32 = undefined;
    var ordinals: [7]usize = undefined;
    const key_count = collectKeys(&head, &keys);
    const ordinal_count = collectOrdinals(&head, &ordinals);

    try std.testing.expectEqualSlices(i32, &.{ -3, -3, -1, 0, 5, 7, 7 }, keys[0..key_count]);
    try std.testing.expectEqualSlices(usize, &.{ 0, 5, 2, 4, 6, 1, 3 }, ordinals[0..ordinal_count]);
    try std.testing.expect(head.next == &entries[0].node);
    try std.testing.expect(head.prev == &entries[3].node);
}

test "phase1 list_sort signed replay preserves current order when a later pass ties everything" {
    var head: list_sort.ListHead = .{};
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
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    var mode = SortMode.descending;
    list_sort.listSort(&mode, &head, cmpSigned);
    try expectCircularLinks(&head);

    list_sort.listSort(null, &head, cmpAllTies);
    try expectCircularLinks(&head);

    var keys: [7]i32 = undefined;
    var ordinals: [7]usize = undefined;
    const key_count = collectKeys(&head, &keys);
    const ordinal_count = collectOrdinals(&head, &ordinals);

    try std.testing.expectEqualSlices(i32, &.{ 7, 4, 4, 1, 1, -2, -2 }, keys[0..key_count]);
    try std.testing.expectEqualSlices(usize, &.{ 5, 0, 2, 1, 4, 3, 6 }, ordinals[0..ordinal_count]);
    try std.testing.expect(head.next == &entries[5].node);
    try std.testing.expect(head.prev == &entries[6].node);
}
