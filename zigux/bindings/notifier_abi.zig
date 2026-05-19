const std = @import("std");
const testing = std.testing;

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

pub const NOTIFIER_DONE: u32 = 0;
pub const NOTIFIER_OK: u32 = 1;
pub const NOTIFIER_STOP: u32 = 2;

pub const NotifierResult = enum(u32) {
    done = NOTIFIER_DONE,
    ok = NOTIFIER_OK,
    stop = NOTIFIER_STOP,
};

pub const NotifierBlock = extern struct {
    notifier_call: usize,
    next: usize,
    priority: i32,
};

pub const notifier_block_align: usize = @alignOf(NotifierBlock);
pub const notifier_block_size: usize = @sizeOf(NotifierBlock);
pub const notifier_call_offset: usize = @offsetOf(NotifierBlock, "notifier_call");
pub const next_offset: usize = @offsetOf(NotifierBlock, "next");
pub const priority_offset: usize = @offsetOf(NotifierBlock, "priority");

pub const NotifierChainPriorityIncrease = extern struct {
    previous_index: usize,
    current_index: usize,
    previous_priority: i32,
    current_priority: i32,
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

pub fn resultFromInt(value: u32) ?NotifierResult {
    return switch (value) {
        NOTIFIER_DONE => .done,
        NOTIFIER_OK => .ok,
        NOTIFIER_STOP => .stop,
        else => null,
    };
}

pub fn recognizesResult(value: u32) bool {
    return resultFromInt(value) != null;
}

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

pub fn firstChainPriorityIncrease(head: ?*const NotifierBlock) ?NotifierChainPriorityIncrease {
    var current = head orelse return null;
    var previous_index: usize = 0;
    var previous_priority = current.priority;

    while (current.next != 0) {
        const next: *const NotifierBlock = @ptrFromInt(current.next);
        const current_index = previous_index + 1;
        if (next.priority > previous_priority) {
            return .{
                .previous_index = previous_index,
                .current_index = current_index,
                .previous_priority = previous_priority,
                .current_priority = next.priority,
            };
        }
        previous_index = current_index;
        previous_priority = next.priority;
        current = next;
    }

    return null;
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

comptime {
    const raw_size = (@sizeOf(usize) * 2) + @sizeOf(i32);
    const expected_size = std.mem.alignForward(usize, raw_size, @alignOf(usize));

    std.debug.assert(@intFromEnum(NotifierResult.done) == NOTIFIER_DONE);
    std.debug.assert(@intFromEnum(NotifierResult.ok) == NOTIFIER_OK);
    std.debug.assert(@intFromEnum(NotifierResult.stop) == NOTIFIER_STOP);
    std.debug.assert(notifier_block_align == @alignOf(usize));
    std.debug.assert(notifier_block_size == expected_size);
    std.debug.assert(notifier_call_offset == 0);
    std.debug.assert(next_offset == @sizeOf(usize));
    std.debug.assert(priority_offset == (@sizeOf(usize) * 2));
}

test "notifier result constants stay aligned with the exported ABI values" {
    try testing.expectEqual(@as(u32, NOTIFIER_DONE), @intFromEnum(NotifierResult.done));
    try testing.expectEqual(@as(u32, NOTIFIER_OK), @intFromEnum(NotifierResult.ok));
    try testing.expectEqual(@as(u32, NOTIFIER_STOP), @intFromEnum(NotifierResult.stop));
}

test "notifier result helpers keep the raw ABI values explicit" {
    try testing.expectEqual(@as(?NotifierResult, .done), resultFromInt(NOTIFIER_DONE));
    try testing.expectEqual(@as(?NotifierResult, .ok), resultFromInt(NOTIFIER_OK));
    try testing.expectEqual(@as(?NotifierResult, .stop), resultFromInt(NOTIFIER_STOP));
    try testing.expectEqual(@as(?NotifierResult, null), resultFromInt(9));

    try testing.expect(recognizesResult(NOTIFIER_DONE));
    try testing.expect(recognizesResult(NOTIFIER_OK));
    try testing.expect(recognizesResult(NOTIFIER_STOP));
    try testing.expect(!recognizesResult(9));
}

test "notifier block layout stays aligned with the exported ABI header" {
    const expected_size = std.mem.alignForward(
        usize,
        (@sizeOf(usize) * 2) + @sizeOf(i32),
        @alignOf(NotifierBlock),
    );

    try testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(NotifierBlock));
    try testing.expectEqual(@as(usize, 0), @offsetOf(NotifierBlock, "notifier_call"));
    try testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(NotifierBlock, "next"));
    try testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(NotifierBlock, "priority"));
    try testing.expectEqual(expected_size, @sizeOf(NotifierBlock));

    const increase_expected_size = std.mem.alignForward(
        usize,
        (@sizeOf(usize) * 2) + (@sizeOf(i32) * 2),
        @alignOf(NotifierChainPriorityIncrease),
    );
    try testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(NotifierChainPriorityIncrease));
    try testing.expectEqual(@as(usize, 0), @offsetOf(NotifierChainPriorityIncrease, "previous_index"));
    try testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(NotifierChainPriorityIncrease, "current_index"));
    try testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(NotifierChainPriorityIncrease, "previous_priority"));
    try testing.expectEqual(@as(usize, (@sizeOf(usize) * 2) + @sizeOf(i32)), @offsetOf(NotifierChainPriorityIncrease, "current_priority"));
    try testing.expectEqual(increase_expected_size, @sizeOf(NotifierChainPriorityIncrease));
}

test "notifier block layout helpers preserve the published shape" {
    const raw_size = (@sizeOf(usize) * 2) + @sizeOf(i32);
    const expected_size = std.mem.alignForward(usize, raw_size, @alignOf(usize));

    try testing.expectEqual(@as(usize, @alignOf(usize)), notifier_block_align);
    try testing.expectEqual(expected_size, notifier_block_size);
    try testing.expectEqual(@as(usize, 0), notifier_call_offset);
    try testing.expectEqual(@as(usize, @sizeOf(usize)), next_offset);
    try testing.expectEqual(@as(usize, @sizeOf(usize) * 2), priority_offset);
}

test "list and hlist layouts stay aligned with the exported ABI header" {
    try testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(ListHead));
    try testing.expectEqual(@as(usize, 0), @offsetOf(ListHead, "next"));
    try testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(ListHead, "prev"));
    try testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @sizeOf(ListHead));

    try testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(HListHead));
    try testing.expectEqual(@as(usize, 0), @offsetOf(HListHead, "first"));
    try testing.expectEqual(@as(usize, @sizeOf(usize)), @sizeOf(HListHead));

    try testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(HListNode));
    try testing.expectEqual(@as(usize, 0), @offsetOf(HListNode, "next"));
    try testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(HListNode, "pprev"));
    try testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @sizeOf(HListNode));
}

test "notifier priority helper accepts empty chain" {
    try testing.expect(chainHasNonincreasingPriority(null));
}

test "notifier priority helper accepts single node chain" {
    const node = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 4,
    };

    try testing.expect(chainHasNonincreasingPriority(&node));
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

    try testing.expect(chainHasNonincreasingPriority(&first));
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

    try testing.expect(!chainHasNonincreasingPriority(&first));
}

test "notifier priority increase helper returns null for empty and single-node chains" {
    try testing.expect(firstChainPriorityIncrease(null) == null);

    const node = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 9,
    };

    try testing.expect(firstChainPriorityIncrease(&node) == null);
}

test "notifier priority increase helper returns null for equal and descending priorities" {
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

    try testing.expect(firstChainPriorityIncrease(&first) == null);
}

test "notifier priority increase helper reports the first increase" {
    const fourth = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 7,
    };
    const third = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&fourth),
        .priority = 2,
    };
    const second = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&third),
        .priority = 4,
    };
    const first = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&second),
        .priority = 6,
    };

    const increase = firstChainPriorityIncrease(&first) orelse return error.TestUnexpectedResult;
    try testing.expectEqual(@as(usize, 2), increase.previous_index);
    try testing.expectEqual(@as(usize, 3), increase.current_index);
    try testing.expectEqual(@as(i32, 2), increase.previous_priority);
    try testing.expectEqual(@as(i32, 7), increase.current_priority);
}

test "list helper accepts a sentinel-only list" {
    var head = ListHead{ .next = 0, .prev = 0 };
    head.next = @intFromPtr(&head);
    head.prev = @intFromPtr(&head);

    try testing.expect(listHasConsistentBacklinks(&head));
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

    try testing.expect(!listHasConsistentBacklinks(&head));
}

test "hlist helper accepts an empty head" {
    const head = HListHead{ .first = 0 };
    try testing.expect(hlistHasConsistentPrevLinks(&head));
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

    try testing.expect(!hlistHasConsistentPrevLinks(&head));
}
