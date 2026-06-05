const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    band: i32,
    phase: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const Direction = enum { ascending, descending };

fn entryFromNode(node: *const ListHead) *const Entry {
    return @fieldParentPtr("node", node);
}

fn cmpBand(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const lhs = entryFromNode(a);
    const rhs = entryFromNode(b);
    if (lhs.band < rhs.band) return -1;
    if (lhs.band > rhs.band) return 1;
    return 0;
}

fn cmpPhase(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const direction: *const Direction = @ptrCast(@alignCast(priv.?));
    const lhs = entryFromNode(a);
    const rhs = entryFromNode(b);
    if (lhs.phase == rhs.phase) return 0;
    const ascending = lhs.phase < rhs.phase;
    return if (direction.* == .ascending)
        (if (ascending) -1 else 1)
    else
        (if (ascending) 1 else -1);
}

fn collectOrdinals(head: *ListHead, out: []usize) ![]usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry = entryFromNode(current.?);
        out[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return out[0..idx];
}

fn drainBand(source: *ListHead, dest: *ListHead, band: i32) void {
    var current = source.next;
    while (current != source) {
        const node = current.?;
        current = node.next;
        if (entryFromNode(node).band == band) {
            list_sort.listDel(node);
            std.debug.assert(node.next == null);
            std.debug.assert(node.prev == null);
            list_sort.listAddTail(node, dest);
        }
    }
}

fn appendAll(dest: *ListHead, source: *ListHead) void {
    while (!list_sort.listEmpty(source)) {
        const node = source.next.?;
        list_sort.listDel(node);
        list_sort.listAddTail(node, dest);
    }
}

test "list sort survives cascade splicing through independently sorted staging heads" {
    var main: ListHead = .{};
    var low: ListHead = .{};
    var mid: ListHead = .{};
    var high: ListHead = .{};
    main.init();
    low.init();
    mid.init();
    high.init();

    var entries = [_]Entry{
        .{ .band = 2, .phase = 1, .ordinal = 0 },
        .{ .band = 0, .phase = 3, .ordinal = 1 },
        .{ .band = 1, .phase = 2, .ordinal = 2 },
        .{ .band = 2, .phase = 0, .ordinal = 3 },
        .{ .band = 0, .phase = 1, .ordinal = 4 },
        .{ .band = 1, .phase = 3, .ordinal = 5 },
        .{ .band = 0, .phase = 0, .ordinal = 6 },
        .{ .band = 2, .phase = 2, .ordinal = 7 },
        .{ .band = 1, .phase = 1, .ordinal = 8 },
        .{ .band = 0, .phase = 2, .ordinal = 9 },
        .{ .band = 2, .phase = 3, .ordinal = 10 },
        .{ .band = 1, .phase = 0, .ordinal = 11 },
        .{ .band = 0, .phase = 1, .ordinal = 12 },
        .{ .band = 2, .phase = 0, .ordinal = 13 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &main);

    list_sort.listSort(null, &main, cmpBand);
    drainBand(&main, &low, 0);
    drainBand(&main, &mid, 1);
    drainBand(&main, &high, 2);
    try std.testing.expect(list_sort.listEmpty(&main));

    var ascending = Direction.ascending;
    var descending = Direction.descending;
    list_sort.listSort(&ascending, &low, cmpPhase);
    list_sort.listSort(&descending, &mid, cmpPhase);
    list_sort.listSort(&ascending, &high, cmpPhase);

    appendAll(&main, &high);
    appendAll(&main, &low);
    appendAll(&main, &mid);
    try std.testing.expect(list_sort.listEmpty(&low));
    try std.testing.expect(list_sort.listEmpty(&mid));
    try std.testing.expect(list_sort.listEmpty(&high));

    var ordinals: [entries.len]usize = undefined;
    try std.testing.expectEqualSlices(
        usize,
        &.{ 3, 13, 0, 7, 10, 6, 4, 12, 9, 1, 5, 2, 8, 11 },
        try collectOrdinals(&main, &ordinals),
    );

    list_sort.listSort(&ascending, &main, cmpPhase);
    try std.testing.expectEqualSlices(
        usize,
        &.{ 3, 13, 6, 11, 0, 4, 12, 8, 7, 9, 2, 10, 1, 5 },
        try collectOrdinals(&main, &ordinals),
    );
    try std.testing.expect(main.next == &entries[3].node);
    try std.testing.expect(main.prev == &entries[5].node);
}
