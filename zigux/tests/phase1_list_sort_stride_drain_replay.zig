const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum { ascending, descending, modulo_four };

fn entryFromNode(node: *const ListHead) *const Entry {
    return @fieldParentPtr("node", node);
}

fn cmpByMode(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs = entryFromNode(a);
    const rhs = entryFromNode(b);

    switch (mode.*) {
        .ascending => {
            if (lhs.key < rhs.key) return -1;
            if (lhs.key > rhs.key) return 1;
            return 0;
        },
        .descending => {
            if (lhs.key > rhs.key) return -1;
            if (lhs.key < rhs.key) return 1;
            return 0;
        },
        .modulo_four => {
            const lhs_bucket = @mod(lhs.key, 4);
            const rhs_bucket = @mod(rhs.key, 4);
            if (lhs_bucket < rhs_bucket) return -1;
            if (lhs_bucket > rhs_bucket) return 1;
            return 0;
        },
    }
}

fn collectOrdinals(head: *const ListHead, out: []usize) ![]usize {
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

fn collectKeys(head: *const ListHead, out: []i32) []i32 {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        out[idx] = entryFromNode(current.?).key;
        idx += 1;
    }
    return out[0..idx];
}

test "list_sort supports stride-drain staging rejoin and stable final bucket sort" {
    var entries = [_]Entry{
        .{ .key = 14, .ordinal = 0 },
        .{ .key = 3, .ordinal = 1 },
        .{ .key = 9, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 12, .ordinal = 4 },
        .{ .key = 6, .ordinal = 5 },
        .{ .key = 0, .ordinal = 6 },
        .{ .key = 11, .ordinal = 7 },
        .{ .key = 5, .ordinal = 8 },
        .{ .key = 8, .ordinal = 9 },
        .{ .key = 2, .ordinal = 10 },
        .{ .key = 13, .ordinal = 11 },
        .{ .key = 4, .ordinal = 12 },
        .{ .key = 10, .ordinal = 13 },
        .{ .key = 7, .ordinal = 14 },
    };

    var head: ListHead = .{};
    head.init();
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &head, cmpByMode);

    var staging: ListHead = .{};
    staging.init();
    var sorted_index: usize = 0;
    var current = head.next;
    while (current != &head) {
        const node = current.?;
        current = node.next;
        if (@mod(sorted_index, 3) == 0) {
            list_sort.listDel(node);
            try std.testing.expect(node.next == null);
            try std.testing.expect(node.prev == null);
            list_sort.listAddTail(node, &staging);
        }
        sorted_index += 1;
    }

    var ordinals: [entries.len]usize = undefined;
    var keys: [entries.len]i32 = undefined;
    try std.testing.expectEqualSlices(
        usize,
        &.{ 3, 10, 12, 8, 14, 9, 13, 7, 11, 0 },
        try collectOrdinals(&head, &ordinals),
    );
    try std.testing.expectEqualSlices(
        usize,
        &.{ 6, 1, 5, 2, 4 },
        try collectOrdinals(&staging, &ordinals),
    );

    mode = .descending;
    list_sort.listSort(&mode, &staging, cmpByMode);
    try std.testing.expectEqualSlices(i32, &.{ 12, 9, 6, 3, 0 }, collectKeys(&staging, &keys));
    try std.testing.expect(staging.next == &entries[4].node);
    try std.testing.expect(staging.prev == &entries[6].node);

    while (!list_sort.listEmpty(&staging)) {
        const node = staging.next.?;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        list_sort.listAddTail(node, &head);
    }
    try std.testing.expect(list_sort.listEmpty(&staging));

    try std.testing.expectEqualSlices(
        usize,
        &.{ 3, 10, 12, 8, 14, 9, 13, 7, 11, 0, 4, 2, 5, 1, 6 },
        try collectOrdinals(&head, &ordinals),
    );

    mode = .modulo_four;
    list_sort.listSort(&mode, &head, cmpByMode);

    try std.testing.expectEqualSlices(
        i32,
        &.{ 4, 8, 12, 0, 1, 5, 13, 9, 2, 10, 14, 6, 7, 11, 3 },
        collectKeys(&head, &keys),
    );
    try std.testing.expectEqualSlices(
        usize,
        &.{ 12, 9, 4, 6, 3, 8, 11, 2, 10, 13, 0, 5, 14, 7, 1 },
        try collectOrdinals(&head, &ordinals),
    );
    try std.testing.expect(head.next == &entries[12].node);
    try std.testing.expect(head.prev == &entries[1].node);
}
