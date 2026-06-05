const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    primary: i32,
    phase: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortPhase = enum {
    primary,
    phase_bucket,
    all_ties,
};

const ComparatorContext = struct {
    phase: SortPhase,
    calls: [3]usize = .{ 0, 0, 0 },

    fn record(self: *ComparatorContext) void {
        self.calls[@intFromEnum(self.phase)] += 1;
    }
};

fn compare(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const context: *ComparatorContext = @ptrCast(@alignCast(priv.?));
    context.record();

    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    switch (context.phase) {
        .primary => {
            if (lhs.primary < rhs.primary) return -9;
            if (lhs.primary > rhs.primary) return 11;
            return 0;
        },
        .phase_bucket => {
            if (lhs.phase < rhs.phase) return -5;
            if (lhs.phase > rhs.phase) return 7;
            return 0;
        },
        .all_ties => return 0,
    }
}

fn expectOrdinals(head: *const list_sort.ListHead, expected: []const usize) !void {
    var actual: [16]usize = undefined;
    var idx: usize = 0;
    var current = head.next;

    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        actual[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqualSlices(usize, expected, actual[0..idx]);
}

test "phase1 list_sort replay keeps stateful comparator context through staged passes" {
    var entries = [_]Entry{
        .{ .primary = 4, .phase = 2, .ordinal = 0 },
        .{ .primary = 1, .phase = 1, .ordinal = 1 },
        .{ .primary = 3, .phase = 0, .ordinal = 2 },
        .{ .primary = 1, .phase = 2, .ordinal = 3 },
        .{ .primary = 2, .phase = 1, .ordinal = 4 },
        .{ .primary = 4, .phase = 0, .ordinal = 5 },
        .{ .primary = 3, .phase = 2, .ordinal = 6 },
        .{ .primary = 2, .phase = 0, .ordinal = 7 },
    };

    var head: list_sort.ListHead = .{};
    head.init();
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var context = ComparatorContext{ .phase = .primary };
    list_sort.listSort(&context, &head, compare);
    try expectOrdinals(&head, &.{ 1, 3, 4, 7, 2, 6, 0, 5 });
    try std.testing.expect(context.calls[@intFromEnum(SortPhase.primary)] > 0);

    var staged: list_sort.ListHead = .{};
    staged.init();

    var sorted_index: usize = 0;
    var current = head.next;
    while (current != &head) {
        const node = current.?;
        current = node.next;

        if ((sorted_index & 1) == 1) {
            list_sort.listDel(node);
            try std.testing.expect(node.next == null);
            try std.testing.expect(node.prev == null);
            list_sort.listAddTail(node, &staged);
        }
        sorted_index += 1;
    }

    try expectOrdinals(&head, &.{ 1, 4, 2, 0 });
    try expectOrdinals(&staged, &.{ 3, 7, 6, 5 });

    context.phase = .phase_bucket;
    list_sort.listSort(&context, &head, compare);
    list_sort.listSort(&context, &staged, compare);
    try expectOrdinals(&head, &.{ 2, 1, 4, 0 });
    try expectOrdinals(&staged, &.{ 7, 5, 3, 6 });
    try std.testing.expect(context.calls[@intFromEnum(SortPhase.phase_bucket)] > 0);

    while (!list_sort.listEmpty(&staged)) {
        const node = staged.next.?;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        list_sort.listAddTail(node, &head);
    }

    try expectOrdinals(&head, &.{ 2, 1, 4, 0, 7, 5, 3, 6 });
    try std.testing.expect(list_sort.listEmpty(&staged));

    context.phase = .all_ties;
    list_sort.listSort(&context, &head, compare);
    try expectOrdinals(&head, &.{ 2, 1, 4, 0, 7, 5, 3, 6 });
    try std.testing.expect(context.calls[@intFromEnum(SortPhase.all_ties)] > 0);

    try std.testing.expect(head.next == &entries[2].node);
    try std.testing.expect(head.prev == &entries[6].node);
}
