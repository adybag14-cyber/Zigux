const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum {
    key_asc,
    key_desc,
    all_ties,
};

fn compare(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (mode.* == .all_ties or lhs.key == rhs.key) return 0;
    const ascending = lhs.key < rhs.key;
    return switch (mode.*) {
        .key_asc => if (ascending) -1 else 1,
        .key_desc => if (ascending) 1 else -1,
        .all_ties => unreachable,
    };
}

fn popFront(head: *ListHead) ?*ListHead {
    if (list_sort.listEmpty(head)) return null;
    const node = head.next.?;
    list_sort.listDel(node);
    return node;
}

fn popBack(head: *ListHead) ?*ListHead {
    if (list_sort.listEmpty(head)) return null;
    const node = head.prev.?;
    list_sort.listDel(node);
    return node;
}

fn expectDetached(node: *const ListHead) !void {
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
}

fn expectOrdinals(head: *ListHead, expected: []const usize) !void {
    var observed: [16]usize = undefined;
    var count: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        observed[count] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        count += 1;
    }

    try std.testing.expectEqualSlices(usize, expected, observed[0..count]);
}

test "list sort survives alternating run detach and splice replay" {
    var head: ListHead = .{};
    var low_run: ListHead = .{};
    var high_run: ListHead = .{};
    var scratch: ListHead = .{};
    head.init();
    low_run.init();
    high_run.init();
    scratch.init();

    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 9, .ordinal = 1 },
        .{ .key = 1, .ordinal = 2 },
        .{ .key = 8, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
        .{ .key = 7, .ordinal = 5 },
        .{ .key = 2, .ordinal = 6 },
        .{ .key = 6, .ordinal = 7 },
        .{ .key = 5, .ordinal = 8 },
        .{ .key = 0, .ordinal = 9 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.key_asc;
    list_sort.listSort(&mode, &head, compare);
    try expectOrdinals(&head, &.{ 9, 2, 6, 4, 0, 8, 7, 5, 3, 1 });

    var rank: usize = 0;
    var current = head.next;
    while (current != &head) {
        const node = current.?;
        current = node.next;
        list_sort.listDel(node);
        try expectDetached(node);
        if ((rank & 1) == 0) {
            list_sort.listAddTail(node, &low_run);
        } else {
            list_sort.listAddTail(node, &high_run);
        }
        rank += 1;
    }
    try std.testing.expect(list_sort.listEmpty(&head));
    try expectOrdinals(&low_run, &.{ 9, 6, 0, 7, 3 });
    try expectOrdinals(&high_run, &.{ 2, 4, 8, 5, 1 });

    mode = .key_desc;
    list_sort.listSort(&mode, &low_run, compare);
    mode = .key_asc;
    list_sort.listSort(&mode, &high_run, compare);
    try expectOrdinals(&low_run, &.{ 3, 7, 0, 6, 9 });
    try expectOrdinals(&high_run, &.{ 2, 4, 8, 5, 1 });

    while (!list_sort.listEmpty(&low_run) or !list_sort.listEmpty(&high_run)) {
        if (popBack(&low_run)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &scratch);
        }
        if (popFront(&high_run)) |node| {
            try expectDetached(node);
            list_sort.listAdd(node, &scratch);
        }
    }
    try std.testing.expect(list_sort.listEmpty(&low_run));
    try std.testing.expect(list_sort.listEmpty(&high_run));
    try expectOrdinals(&scratch, &.{ 1, 5, 8, 4, 2, 9, 6, 0, 7, 3 });

    while (popFront(&scratch)) |node| {
        try expectDetached(node);
        list_sort.listAddTail(node, &head);
    }
    try std.testing.expect(list_sort.listEmpty(&scratch));
    try expectOrdinals(&head, &.{ 1, 5, 8, 4, 2, 9, 6, 0, 7, 3 });

    mode = .all_ties;
    list_sort.listSort(&mode, &head, compare);
    try expectOrdinals(&head, &.{ 1, 5, 8, 4, 2, 9, 6, 0, 7, 3 });
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[3].node);
}
