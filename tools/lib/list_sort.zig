const std = @import("std");

pub const ListHead = struct {
    next: ?*ListHead = null,
    prev: ?*ListHead = null,

    pub fn init(head: *ListHead) void {
        head.next = head;
        head.prev = head;
    }
};

pub const CmpFn = *const fn (?*anyopaque, *const ListHead, *const ListHead) i32;

pub fn listEmpty(head: *const ListHead) bool {
    return head.next == head;
}

pub fn listAdd(new: *ListHead, head: *ListHead) void {
    __listAdd(new, head, head.next.?);
}

pub fn listAddTail(new: *ListHead, head: *ListHead) void {
    __listAdd(new, head.prev.?, head);
}

pub fn listDel(entry: *ListHead) void {
    __listDel(entry.prev.?, entry.next.?);
    entry.next = null;
    entry.prev = null;
}

fn __listAdd(new: *ListHead, prev: *ListHead, next: *ListHead) void {
    next.prev = new;
    new.next = next;
    new.prev = prev;
    prev.next = new;
}

fn __listDel(prev: *ListHead, next: *ListHead) void {
    next.prev = prev;
    prev.next = next;
}

fn merge(priv: ?*anyopaque, cmp: CmpFn, a: *ListHead, b: *ListHead) *ListHead {
    var lhs: ?*ListHead = a;
    var rhs: ?*ListHead = b;
    var head: ?*ListHead = null;
    var tail: *?*ListHead = &head;

    while (true) {
        if (cmp(priv, lhs.?, rhs.?) <= 0) {
            tail.* = lhs.?;
            tail = &lhs.?.next;
            lhs = lhs.?.next;
            if (lhs == null) {
                tail.* = rhs;
                break;
            }
        } else {
            tail.* = rhs.?;
            tail = &rhs.?.next;
            rhs = rhs.?.next;
            if (rhs == null) {
                tail.* = lhs;
                break;
            }
        }
    }

    return head.?;
}

fn mergeFinal(priv: ?*anyopaque, cmp: CmpFn, head: *ListHead, a: *ListHead, b: *ListHead) void {
    var lhs: ?*ListHead = a;
    var rhs: ?*ListHead = b;
    var tail: *ListHead = head;

    while (true) {
        if (cmp(priv, lhs.?, rhs.?) <= 0) {
            tail.next = lhs;
            lhs.?.prev = tail;
            tail = lhs.?;
            lhs = lhs.?.next;
            if (lhs == null) {
                break;
            }
        } else {
            tail.next = rhs;
            rhs.?.prev = tail;
            tail = rhs.?;
            rhs = rhs.?.next;
            if (rhs == null) {
                rhs = lhs;
                break;
            }
        }
    }

    tail.next = rhs;
    while (rhs) |node| {
        node.prev = tail;
        tail = node;
        rhs = node.next;
    }

    tail.next = head;
    head.prev = tail;
}

pub fn listSort(priv: ?*anyopaque, head: *ListHead, cmp: CmpFn) void {
    var list = head.next.?;
    var pending: ?*ListHead = null;
    var count: usize = 0;

    if (list == head.prev.?) {
        return;
    }

    head.prev.?.next = null;

    while (true) {
        var bits = count;
        var tail: *?*ListHead = &pending;

        while ((bits & 1) == 1) : (bits >>= 1) {
            tail = &tail.*.?.prev;
        }

        if (bits != 0) {
            const first = tail.*.?;
            const second = first.prev.?;
            const merged = merge(priv, cmp, second, first);
            merged.prev = second.prev;
            tail.* = merged;
        }

        const next = list.next;
        list.prev = pending;
        pending = list;
        pending.?.next = null;
        count += 1;

        if (next == null) {
            break;
        }
        list = next.?;
    }

    list = pending.?;
    pending = pending.?.prev;
    while (true) {
        const next = pending.?.prev;
        if (next == null) {
            break;
        }
        list = merge(priv, cmp, pending.?, list);
        pending = next;
    }

    mergeFinal(priv, cmp, head, pending.?, list);
}

test "list sort keeps stable ordering for tri-state comparator" {
    const Entry = struct {
        key: i32,
        ordinal: usize,
        node: ListHead = .{},
    };

    const cmp = struct {
        fn less(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            if (lhs.key < rhs.key) return -1;
            if (lhs.key > rhs.key) return 1;
            return 0;
        }
    }.less;

    var head: ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 2, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
    };

    for (&entries) |*entry| listAddTail(&entry.node, &head);
    listSort(null, &head, cmp);

    var keys: [5]i32 = undefined;
    var ordinals: [5]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        idx += 1;
    }

    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 3, 3 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 0, 2, 4 }, ordinals[0..idx]);
}

test "list sort accepts boolean-style comparator" {
    const Entry = struct {
        key: i32,
        ordinal: usize,
        node: ListHead = .{},
    };

    const cmp = struct {
        fn less(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            return @intFromBool(lhs.key > rhs.key);
        }
    }.less;

    var head: ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 2, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
    };

    for (&entries) |*entry| listAddTail(&entry.node, &head);
    listSort(null, &head, cmp);

    var keys: [5]i32 = undefined;
    var ordinals: [5]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        idx += 1;
    }

    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 3, 3 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 0, 2, 4 }, ordinals[0..idx]);
}

test "list sort honors comparator context" {
    const Entry = struct {
        key: i32,
        ordinal: usize,
        node: ListHead = .{},
    };

    const SortMode = enum { ascending, descending };

    const cmp = struct {
        fn less(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
            const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);

            if (lhs.key == rhs.key) return 0;
            const ascending = lhs.key < rhs.key;
            return if (mode.* == .ascending)
                (if (ascending) -1 else 1)
            else
                (if (ascending) 1 else -1);
        }
    }.less;

    var head: ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 2, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
    };
    for (&entries) |*entry| listAddTail(&entry.node, &head);

    var mode = SortMode.descending;
    listSort(&mode, &head, cmp);

    var keys: [5]i32 = undefined;
    var ordinals: [5]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        idx += 1;
    }

    try std.testing.expectEqualSlices(i32, &.{ 3, 3, 2, 1, 1 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 2, 4, 0, 1, 3 }, ordinals[0..idx]);
}

test "list sort can reorder the same circular list twice" {
    const Entry = struct {
        key: i32,
        ordinal: usize,
        node: ListHead = .{},
    };

    const SortMode = enum { ascending, descending };

    const cmp = struct {
        fn less(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
            const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);

            if (lhs.key == rhs.key) return 0;
            const ascending = lhs.key < rhs.key;
            return if (mode.* == .ascending)
                (if (ascending) -1 else 1)
            else
                (if (ascending) 1 else -1);
        }
    }.less;

    var head: ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 2, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
    };
    for (&entries) |*entry| listAddTail(&entry.node, &head);

    var mode = SortMode.descending;
    listSort(&mode, &head, cmp);

    mode = .ascending;
    listSort(&mode, &head, cmp);

    var keys: [5]i32 = undefined;
    var ordinals: [5]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 3, 3 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 0, 2, 4 }, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[4].node);
}

test "list sort keeps reverse links aligned after reordering" {
    const Entry = struct {
        key: i32,
        ordinal: usize,
        node: ListHead = .{},
    };

    const cmp = struct {
        fn less(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            if (lhs.key < rhs.key) return -1;
            if (lhs.key > rhs.key) return 1;
            return 0;
        }
    }.less;

    var head: ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
    };

    for (&entries) |*entry| listAddTail(&entry.node, &head);
    listSort(null, &head, cmp);

    var forward_ordinals: [4]usize = undefined;
    var backward_ordinals: [4]usize = undefined;

    var forward_idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        forward_ordinals[forward_idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        forward_idx += 1;
    }

    var backward_idx: usize = 0;
    current = head.prev;
    while (current != &head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        backward_ordinals[backward_idx] = entry.ordinal;
        backward_idx += 1;
    }

    try std.testing.expectEqualSlices(usize, &.{ 3, 1, 0, 2 }, forward_ordinals[0..forward_idx]);
    try std.testing.expectEqualSlices(usize, &.{ 2, 0, 1, 3 }, backward_ordinals[0..backward_idx]);
    try std.testing.expect(head.next == &entries[3].node);
    try std.testing.expect(head.prev == &entries[2].node);
}

test "list sort preserves sorted unique input" {
    const Entry = struct {
        key: i32,
        ordinal: usize,
        node: ListHead = .{},
    };

    const cmp = struct {
        fn less(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            if (lhs.key < rhs.key) return -1;
            if (lhs.key > rhs.key) return 1;
            return 0;
        }
    }.less;

    var head: ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 1, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 4, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
    };
    for (&entries) |*entry| listAddTail(&entry.node, &head);

    listSort(null, &head, cmp);

    var ordinals: [5]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqualSlices(usize, &.{ 0, 1, 2, 3, 4 }, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[0].node);
    try std.testing.expect(head.prev == &entries[4].node);
    try std.testing.expect(entries[0].node.prev == &head);
    try std.testing.expect(entries[4].node.next == &head);
}

test "list sort preserves stable bucket order across parity groups" {
    const Entry = struct {
        key: i32,
        ordinal: usize,
        node: ListHead = .{},
    };

    const cmp = struct {
        fn less(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            const lhs_is_odd = @mod(lhs.key, 2) != 0;
            const rhs_is_odd = @mod(rhs.key, 2) != 0;
            if (lhs_is_odd == rhs_is_odd) return 0;
            return if (lhs_is_odd) -1 else 1;
        }
    }.less;

    var head: ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 6, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 2, .ordinal = 4 },
        .{ .key = 5, .ordinal = 5 },
        .{ .key = 8, .ordinal = 6 },
        .{ .key = 7, .ordinal = 7 },
    };
    for (&entries) |*entry| listAddTail(&entry.node, &head);

    listSort(null, &head, cmp);

    var keys: [8]i32 = undefined;
    var ordinals: [8]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqualSlices(i32, &.{ 1, 3, 5, 7, 4, 6, 2, 8 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 5, 7, 0, 2, 4, 6 }, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[6].node);
}

test "list sort preserves stable modulo bucket order across a longer merge path" {
    const Entry = struct {
        key: i32,
        ordinal: usize,
        node: ListHead = .{},
    };

    const cmp = struct {
        fn less(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            const lhs_bucket = @mod(lhs.key, 3);
            const rhs_bucket = @mod(rhs.key, 3);
            if (lhs_bucket == rhs_bucket) return 0;
            return if (lhs_bucket < rhs_bucket) -1 else 1;
        }
    }.less;

    var head: ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 8, .ordinal = 0 },
        .{ .key = 3, .ordinal = 1 },
        .{ .key = 10, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 7, .ordinal = 4 },
        .{ .key = 4, .ordinal = 5 },
        .{ .key = 6, .ordinal = 6 },
        .{ .key = 11, .ordinal = 7 },
        .{ .key = 0, .ordinal = 8 },
        .{ .key = 5, .ordinal = 9 },
        .{ .key = 9, .ordinal = 10 },
        .{ .key = 2, .ordinal = 11 },
    };
    for (&entries) |*entry| listAddTail(&entry.node, &head);

    listSort(null, &head, cmp);

    var keys: [12]i32 = undefined;
    var ordinals: [12]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqualSlices(i32, &.{ 3, 6, 0, 9, 10, 1, 7, 4, 8, 11, 5, 2 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 6, 8, 10, 2, 3, 4, 5, 0, 7, 9, 11 }, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[11].node);
}

test "list sort accepts non-unit comparator magnitudes" {
    const Entry = struct {
        key: i32,
        ordinal: usize,
        node: ListHead = .{},
    };

    const cmp = struct {
        fn less(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            if (lhs.key < rhs.key) return -7;
            if (lhs.key > rhs.key) return 9;
            return 0;
        }
    }.less;

    var head: ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 3, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 2, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 4, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
    };
    for (&entries) |*entry| listAddTail(&entry.node, &head);

    listSort(null, &head, cmp);

    var keys: [6]i32 = undefined;
    var ordinals: [6]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 2, 3, 4 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 2, 5, 0, 4 }, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[4].node);
}

test "list sort honors comparator context with non-unit magnitudes" {
    const Entry = struct {
        key: i32,
        ordinal: usize,
        node: ListHead = .{},
    };

    const SortMode = enum { ascending, descending };

    const cmp = struct {
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
    for (&entries) |*entry| listAddTail(&entry.node, &head);

    var mode = SortMode.descending;
    listSort(&mode, &head, cmp);

    var keys: [6]i32 = undefined;
    var ordinals: [6]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqualSlices(i32, &.{ 5, 5, 4, 2, 1, 1 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 4, 0, 2, 5 }, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[5].node);
}

test "list sort reuses non-unit comparator context across repeated reordering" {
    const Entry = struct {
        key: i32,
        ordinal: usize,
        node: ListHead = .{},
    };

    const SortMode = enum { ascending, descending };

    const cmp = struct {
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
    for (&entries) |*entry| listAddTail(&entry.node, &head);

    var mode = SortMode.descending;
    listSort(&mode, &head, cmp);

    mode = .ascending;
    listSort(&mode, &head, cmp);

    var keys: [6]i32 = undefined;
    var ordinals: [6]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 4, 5, 5 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 2, 5, 0, 4, 1, 3 }, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[2].node);
    try std.testing.expect(head.prev == &entries[3].node);
}

test "list sort accepts signed subtractive comparator" {
    const Entry = struct {
        key: i32,
        ordinal: usize,
        node: ListHead = .{},
    };

    const cmp = struct {
        fn less(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            return lhs.key - rhs.key;
        }
    }.less;

    var head: ListHead = .{};
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
    for (&entries) |*entry| listAddTail(&entry.node, &head);

    listSort(null, &head, cmp);

    var keys: [7]i32 = undefined;
    var ordinals: [7]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqualSlices(i32, &.{ -5, -2, -2, 0, 4, 7, 7 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 5, 1, 3, 4, 0, 2, 6 }, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[5].node);
    try std.testing.expect(head.prev == &entries[6].node);
}

test "list sort preserves input order when every comparison ties" {
    const Entry = struct {
        key: i32,
        ordinal: usize,
        node: ListHead = .{},
    };

    const cmp = struct {
        fn less(_: ?*anyopaque, _: *const ListHead, _: *const ListHead) i32 {
            return 0;
        }
    }.less;

    var head: ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 7, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 9, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 3, .ordinal = 5 },
        .{ .key = 8, .ordinal = 6 },
        .{ .key = 4, .ordinal = 7 },
    };

    for (&entries) |*entry| listAddTail(&entry.node, &head);
    listSort(null, &head, cmp);

    var ordinals: [8]usize = undefined;
    var keys: [8]i32 = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        ordinals[idx] = entry.ordinal;
        keys[idx] = entry.key;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqualSlices(usize, &.{ 0, 1, 2, 3, 4, 5, 6, 7 }, ordinals[0..idx]);
    try std.testing.expectEqualSlices(i32, &.{ 7, 2, 9, 1, 5, 3, 8, 4 }, keys[0..idx]);
    try std.testing.expect(head.next == &entries[0].node);
    try std.testing.expect(head.prev == &entries[7].node);
}

test "list sort handles empty and singleton lists" {
    const Entry = struct {
        key: i32,
        node: ListHead = .{},
    };

    const cmp = struct {
        fn less(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            return @intCast(@intFromBool(lhs.key > rhs.key));
        }
    }.less;

    var empty_head: ListHead = .{};
    empty_head.init();
    listSort(null, &empty_head, cmp);
    try std.testing.expect(listEmpty(&empty_head));

    var single_head: ListHead = .{};
    single_head.init();
    var entry = Entry{ .key = 7 };
    listAddTail(&entry.node, &single_head);
    listSort(null, &single_head, cmp);
    try std.testing.expect(single_head.next == &entry.node);
    try std.testing.expect(single_head.prev == &entry.node);
    try std.testing.expect(entry.node.next == &single_head);
    try std.testing.expect(entry.node.prev == &single_head);
}
