const std = @import("std");

fn listHeadFromRaw(raw: usize) ?*const ListHead {
    if (raw == 0) return null;
    const node: *const ListHead = @ptrFromInt(raw);
    return node;
}

fn hlistNodeFromRaw(raw: usize) ?*const HListNode {
    if (raw == 0) return null;
    const node: *const HListNode = @ptrFromInt(raw);
    return node;
}

pub const NotifierResult = enum(u32) {
    done = 0,
    ok = 1,
    stop = 2,
};

pub const NotifierBlock = extern struct {
    notifier_call: usize,
    next: usize,
    priority: i32,
};

pub const ListHead = extern struct {
    next: usize,
    prev: usize,
};

pub const HListHead = extern struct {
    first: usize,
};

pub const HListNode = extern struct {
    next: usize,
    pprev: usize,
};

pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {
    var current = head orelse return true;
    var previous_priority = current.priority;

    while (current.next != 0) {
        const next: *const NotifierBlock = @ptrFromInt(current.next);
        if (next.priority > previous_priority) return false;
        previous_priority = next.priority;
        current = next;
    }

    return true;
}

pub fn listHasConsistentBacklinks(head: ?*const ListHead) bool {
    const sentinel = head orelse return false;
    var expected_prev = @intFromPtr(sentinel);
    var cursor = listHeadFromRaw(sentinel.next) orelse return false;

    while (cursor != sentinel) {
        if (cursor.prev != expected_prev) return false;
        expected_prev = @intFromPtr(cursor);
        cursor = listHeadFromRaw(cursor.next) orelse return false;
    }

    return sentinel.prev == expected_prev;
}

pub fn hlistHasConsistentPrevLinks(head: ?*const HListHead) bool {
    const first_head = head orelse return false;
    var expected_pprev = @intFromPtr(&first_head.first);
    var cursor = hlistNodeFromRaw(first_head.first);

    while (cursor) |node| {
        if (node.pprev != expected_pprev) return false;
        expected_pprev = @intFromPtr(&node.next);
        cursor = hlistNodeFromRaw(node.next);
    }

    return true;
}

test "notifier result constants stay aligned with the exported ABI values" {
    try std.testing.expectEqual(@as(u32, 0), @intFromEnum(NotifierResult.done));
    try std.testing.expectEqual(@as(u32, 1), @intFromEnum(NotifierResult.ok));
    try std.testing.expectEqual(@as(u32, 2), @intFromEnum(NotifierResult.stop));
}

test "notifier block layout stays aligned with the exported ABI header" {
    const expected_size = std.mem.alignForward(
        usize,
        (@sizeOf(usize) * 2) + @sizeOf(i32),
        @alignOf(NotifierBlock),
    );

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(NotifierBlock));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(NotifierBlock, "notifier_call"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(NotifierBlock, "next"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(NotifierBlock, "priority"));
    try std.testing.expectEqual(expected_size, @sizeOf(NotifierBlock));
}

test "list and hlist layouts stay aligned with the exported ABI header" {
    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(ListHead));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(ListHead, "next"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(ListHead, "prev"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @sizeOf(ListHead));

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(HListHead));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(HListHead, "first"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @sizeOf(HListHead));

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(HListNode));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(HListNode, "next"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(HListNode, "pprev"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @sizeOf(HListNode));
}

test "notifier priority helper accepts empty chain" {
    try std.testing.expect(chainHasNonincreasingPriority(null));
}

test "notifier priority helper accepts single node chain" {
    const node = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 4,
    };

    try std.testing.expect(chainHasNonincreasingPriority(&node));
}

test "notifier priority helper accepts equal and descending priorities" {
    const third = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 3,
    };
    const second = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&third),
        .priority = 5,
    };
    const first = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&second),
        .priority = 5,
    };

    try std.testing.expect(chainHasNonincreasingPriority(&first));
}

test "notifier priority helper rejects increasing priority" {
    const third = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 6,
    };
    const second = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&third),
        .priority = 2,
    };
    const first = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&second),
        .priority = 4,
    };

    try std.testing.expect(!chainHasNonincreasingPriority(&first));
}

test "list helper accepts a sentinel-only list" {
    var head = ListHead{ .next = 0, .prev = 0 };
    head.next = @intFromPtr(&head);
    head.prev = @intFromPtr(&head);

    try std.testing.expect(listHasConsistentBacklinks(&head));
}

test "list helper rejects a broken backlink" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var second = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&second);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&head);
    second.prev = @intFromPtr(&head);

    try std.testing.expect(!listHasConsistentBacklinks(&head));
}

test "hlist helper accepts an empty head" {
    const head = HListHead{ .first = 0 };
    try std.testing.expect(hlistHasConsistentPrevLinks(&head));
}

test "hlist helper rejects a broken prev-link" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var second = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = 0;
    second.pprev = @intFromPtr(&head.first);

    try std.testing.expect(!hlistHasConsistentPrevLinks(&head));
}
