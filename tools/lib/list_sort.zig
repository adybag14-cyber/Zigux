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

    var ordinals: [5]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        ordinals[idx] = entry.ordinal;
        idx += 1;
    }

    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 0, 2, 4 }, ordinals[0..idx]);
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
