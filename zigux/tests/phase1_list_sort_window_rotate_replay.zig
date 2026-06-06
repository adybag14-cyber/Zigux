const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum {
    ascending,
    descending,
    all_ties,
};

fn entryFromNode(node: *const ListHead) *const Entry {
    return @fieldParentPtr("node", node);
}

fn cmpByMode(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    if (mode.* == .all_ties) return 0;

    const lhs = entryFromNode(a);
    const rhs = entryFromNode(b);
    if (lhs.key == rhs.key) return 0;

    const lhs_before_rhs = lhs.key < rhs.key;
    return if (mode.* == .ascending)
        (if (lhs_before_rhs) -1 else 1)
    else
        (if (lhs_before_rhs) 1 else -1);
}

fn cmpByModulo(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    if (mode.* == .all_ties) return 0;

    const lhs = entryFromNode(a);
    const rhs = entryFromNode(b);
    const lhs_bucket = @mod(lhs.key, 3);
    const rhs_bucket = @mod(rhs.key, 3);
    if (lhs_bucket == rhs_bucket) return 0;

    const lhs_before_rhs = lhs_bucket < rhs_bucket;
    return if (mode.* == .ascending)
        (if (lhs_before_rhs) -1 else 1)
    else
        (if (lhs_before_rhs) 1 else -1);
}

fn collectOrdinals(head: *const ListHead, out: []usize) usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry = entryFromNode(current.?);
        out[idx] = entry.ordinal;
        idx += 1;
    }
    return idx;
}

fn expectCircularLinks(head: *const ListHead, expected_len: usize) !void {
    var count: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        count += 1;
    }
    try std.testing.expectEqual(expected_len, count);

    count = 0;
    current = head.prev;
    while (current != head) : (current = current.?.prev) {
        count += 1;
    }
    try std.testing.expectEqual(expected_len, count);
}

fn expectOrder(head: *const ListHead, expected: []const usize) !void {
    var ordinals: [12]usize = undefined;
    const len = collectOrdinals(head, &ordinals);
    try std.testing.expectEqualSlices(usize, expected, ordinals[0..len]);
    try expectCircularLinks(head, expected.len);
}

test "list_sort rotates a sorted middle window through staging heads" {
    var head: ListHead = .{};
    head.init();
    var window: ListHead = .{};
    window.init();
    var front: ListHead = .{};
    front.init();
    var back: ListHead = .{};
    back.init();

    var entries = [_]Entry{
        .{ .key = 9, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = 4, .ordinal = 3 },
        .{ .key = 6, .ordinal = 4 },
        .{ .key = 1, .ordinal = 5 },
        .{ .key = 8, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
        .{ .key = 5, .ordinal = 8 },
    };
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &head, cmpByMode);
    try expectOrder(&head, &.{ 5, 1, 7, 3, 8, 4, 2, 6, 0 });

    var index: usize = 0;
    var current = head.next;
    while (current != &head) {
        const next = current.?.next;
        if (index >= 2 and index <= 5) {
            const node = current.?;
            list_sort.listDel(node);
            try std.testing.expect(node.next == null);
            try std.testing.expect(node.prev == null);
            list_sort.listAddTail(node, &window);
        }
        index += 1;
        current = next;
    }
    try expectOrder(&head, &.{ 5, 1, 2, 6, 0 });
    try expectOrder(&window, &.{ 7, 3, 8, 4 });

    mode = .descending;
    list_sort.listSort(&mode, &window, cmpByMode);
    try expectOrder(&window, &.{ 4, 8, 3, 7 });

    mode = .ascending;
    list_sort.listSort(&mode, &head, cmpByModulo);
    try expectOrder(&head, &.{ 0, 5, 2, 1, 6 });

    var take_front = true;
    current = window.next;
    while (current != &window) {
        const next = current.?.next;
        const node = current.?;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        if (take_front) {
            list_sort.listAdd(node, &front);
        } else {
            list_sort.listAddTail(node, &back);
        }
        take_front = !take_front;
        current = next;
    }
    try std.testing.expect(list_sort.listEmpty(&window));
    try expectOrder(&front, &.{ 3, 4 });
    try expectOrder(&back, &.{ 8, 7 });

    current = front.next;
    while (current != &front) {
        const next = current.?.next;
        const node = current.?;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        list_sort.listAdd(node, &head);
        current = next;
    }

    current = back.prev;
    while (current != &back) {
        const prev = current.?.prev;
        const node = current.?;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        list_sort.listAddTail(node, &head);
        current = prev;
    }
    try std.testing.expect(list_sort.listEmpty(&front));
    try std.testing.expect(list_sort.listEmpty(&back));
    try expectOrder(&head, &.{ 4, 3, 0, 5, 2, 1, 6, 7, 8 });

    mode = .all_ties;
    list_sort.listSort(&mode, &head, cmpByMode);
    try expectOrder(&head, &.{ 4, 3, 0, 5, 2, 1, 6, 7, 8 });
    try std.testing.expect(head.next == &entries[4].node);
    try std.testing.expect(head.prev == &entries[8].node);
}
