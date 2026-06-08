const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum {
    key_ascending,
    key_descending,
    ordinal_ascending,
    all_ties,
};

const SortContext = struct {
    mode: SortMode,
};

fn compareEntries(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const context: *const SortContext = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    switch (context.mode) {
        .key_ascending => {
            if (lhs.key < rhs.key) return -17;
            if (lhs.key > rhs.key) return 19;
            return 0;
        },
        .key_descending => {
            if (lhs.key > rhs.key) return -17;
            if (lhs.key < rhs.key) return 19;
            return 0;
        },
        .ordinal_ascending => {
            if (lhs.ordinal < rhs.ordinal) return -17;
            if (lhs.ordinal > rhs.ordinal) return 19;
            return 0;
        },
        .all_ties => return 0,
    }
}

fn expectOrdinals(head: *const ListHead, expected: []const usize) !void {
    var actual: [32]usize = undefined;
    var count: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        actual[count] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        count += 1;
    }
    try std.testing.expectEqualSlices(usize, expected, actual[0..count]);
}

fn popFront(head: *ListHead) !*Entry {
    try std.testing.expect(!list_sort.listEmpty(head));
    const node = head.next.?;
    const entry: *Entry = @fieldParentPtr("node", node);
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    return entry;
}

fn popBack(head: *ListHead) !*Entry {
    try std.testing.expect(!list_sort.listEmpty(head));
    const node = head.prev.?;
    const entry: *Entry = @fieldParentPtr("node", node);
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    return entry;
}

test "list sort zigzag fanfold lifecycle preserves staged stable order" {
    var source: ListHead = .{};
    source.init();
    var rails = [_]ListHead{.{}} ** 4;
    for (&rails) |*rail| rail.init();

    var entries = [_]Entry{
        .{ .key = 7, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 5, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 8, .ordinal = 4 },
        .{ .key = 1, .ordinal = 5 },
        .{ .key = 5, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
        .{ .key = 7, .ordinal = 8 },
        .{ .key = 0, .ordinal = 9 },
        .{ .key = 4, .ordinal = 10 },
        .{ .key = 1, .ordinal = 11 },
        .{ .key = 6, .ordinal = 12 },
        .{ .key = 3, .ordinal = 13 },
        .{ .key = 4, .ordinal = 14 },
        .{ .key = 0, .ordinal = 15 },
    };

    for (&entries, 0..) |*entry, idx| {
        if ((idx & 1) == 0) {
            list_sort.listAddTail(&entry.node, &source);
        } else {
            list_sort.listAdd(&entry.node, &source);
        }
    }
    try expectOrdinals(&source, &.{ 15, 13, 11, 9, 7, 5, 3, 1, 0, 2, 4, 6, 8, 10, 12, 14 });

    var context = SortContext{ .mode = .key_ascending };
    list_sort.listSort(&context, &source, compareEntries);
    try expectOrdinals(&source, &.{ 15, 9, 11, 5, 3, 1, 13, 7, 10, 14, 2, 6, 12, 0, 8, 4 });

    var sorted_index: usize = 0;
    while (!list_sort.listEmpty(&source)) : (sorted_index += 1) {
        const entry = try popFront(&source);
        const wave = sorted_index & 7;
        const rail_index = if (wave < 4) wave else 7 - wave;
        if ((sorted_index & 1) == 0) {
            list_sort.listAddTail(&entry.node, &rails[rail_index]);
        } else {
            list_sort.listAdd(&entry.node, &rails[rail_index]);
        }
    }
    try std.testing.expect(list_sort.listEmpty(&source));
    try expectOrdinals(&rails[0], &.{ 4, 7, 15, 10 });
    try expectOrdinals(&rails[1], &.{ 14, 9, 13, 8 });
    try expectOrdinals(&rails[2], &.{ 0, 1, 11, 2 });
    try expectOrdinals(&rails[3], &.{ 6, 5, 3, 12 });

    context.mode = .key_descending;
    list_sort.listSort(&context, &rails[0], compareEntries);
    context.mode = .ordinal_ascending;
    list_sort.listSort(&context, &rails[1], compareEntries);
    context.mode = .key_ascending;
    list_sort.listSort(&context, &rails[2], compareEntries);
    context.mode = .key_descending;
    list_sort.listSort(&context, &rails[3], compareEntries);

    try expectOrdinals(&rails[0], &.{ 4, 10, 7, 15 });
    try expectOrdinals(&rails[1], &.{ 8, 9, 13, 14 });
    try expectOrdinals(&rails[2], &.{ 11, 1, 2, 0 });
    try expectOrdinals(&rails[3], &.{ 12, 6, 3, 5 });

    const schedule = [_]struct {
        rail: usize,
        back: bool,
    }{
        .{ .rail = 0, .back = true },
        .{ .rail = 1, .back = false },
        .{ .rail = 2, .back = true },
        .{ .rail = 3, .back = false },
        .{ .rail = 3, .back = true },
        .{ .rail = 2, .back = false },
        .{ .rail = 1, .back = true },
        .{ .rail = 0, .back = false },
    };

    for (0..16) |idx| {
        const step = schedule[idx % schedule.len];
        const entry = if (step.back) try popBack(&rails[step.rail]) else try popFront(&rails[step.rail]);
        list_sort.listAddTail(&entry.node, &source);
    }
    for (&rails) |*rail| try std.testing.expect(list_sort.listEmpty(rail));
    try expectOrdinals(&source, &.{ 15, 8, 0, 12, 5, 11, 14, 4, 7, 9, 2, 6, 3, 1, 13, 10 });

    context.mode = .all_ties;
    list_sort.listSort(&context, &source, compareEntries);
    try expectOrdinals(&source, &.{ 15, 8, 0, 12, 5, 11, 14, 4, 7, 9, 2, 6, 3, 1, 13, 10 });
    try std.testing.expect(source.next == &entries[15].node);
    try std.testing.expect(source.prev == &entries[10].node);
}
