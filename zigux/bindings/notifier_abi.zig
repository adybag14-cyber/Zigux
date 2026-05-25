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

pub const ListBackLinkBreak = extern struct {
    current_index: usize,
    expected_prev: usize,
    actual_prev: usize,
};

pub const HListPrevLinkBreak = extern struct {
    current_index: usize,
    expected_pprev: usize,
    actual_pprev: usize,
};

pub fn resultFromInt(result: u32) ?NotifierResult {
    return switch (result) {
        @intFromEnum(NotifierResult.done) => .done,
        @intFromEnum(NotifierResult.ok) => .ok,
        @intFromEnum(NotifierResult.stop) => .stop,
        else => null,
    };
}

pub fn resultIsKnown(result: u32) bool {
    return resultFromInt(result) != null;
}

pub fn resultStopsChainValue(result: u32) bool {
    return result == @intFromEnum(NotifierResult.stop);
}

pub fn resultStopsChain(result: NotifierResult) bool {
    return resultStopsChainValue(@intFromEnum(result));
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

pub fn firstBrokenBacklink(head: ?*const ListHead) ?ListBackLinkBreak {
    const sentinel = head orelse return null;
    var expected_prev = @intFromPtr(sentinel);
    var current_index: usize = 0;
    var cursor = listHeadFromRaw(sentinel.next) orelse {
        return .{
            .current_index = 0,
            .expected_prev = expected_prev,
            .actual_prev = 0,
        };
    };

    while (cursor != sentinel) {
        if (cursor.prev != expected_prev) {
            return .{
                .current_index = current_index,
                .expected_prev = expected_prev,
                .actual_prev = cursor.prev,
            };
        }
        expected_prev = @intFromPtr(cursor);
        current_index += 1;
        cursor = listHeadFromRaw(cursor.next) orelse {
            return .{
                .current_index = current_index,
                .expected_prev = expected_prev,
                .actual_prev = 0,
            };
        };
    }

    if (sentinel.prev != expected_prev) {
        return .{
            .current_index = current_index,
            .expected_prev = expected_prev,
            .actual_prev = sentinel.prev,
        };
    }

    return null;
}

pub fn listHasConsistentBacklinks(head: ?*const ListHead) bool {
    if (head == null) return false;
    return firstBrokenBacklink(head) == null;
}

pub fn firstPprevMatchesHead(head: ?*const HListHead) bool {
    const first_head = head orelse return false;
    const first_node = hlistNodeFromRaw(first_head.first) orelse return true;
    return first_node.pprev == @intFromPtr(&first_head.first);
}

pub fn firstBrokenPrevLink(head: ?*const HListHead) ?HListPrevLinkBreak {
    const first_head = head orelse return null;
    var expected_pprev = @intFromPtr(&first_head.first);
    var current_index: usize = 0;
    var cursor = hlistNodeFromRaw(first_head.first);

    while (cursor) |node| {
        if (node.pprev != expected_pprev) {
            return .{
                .current_index = current_index,
                .expected_pprev = expected_pprev,
                .actual_pprev = node.pprev,
            };
        }
        expected_pprev = @intFromPtr(&node.next);
        current_index += 1;
        cursor = hlistNodeFromRaw(node.next);
    }

    return null;
}

pub fn hlistHasConsistentPrevLinks(head: ?*const HListHead) bool {
    if (head == null) return false;
    return firstBrokenPrevLink(head) == null;
}

test "notifier result constants stay aligned with the exported ABI values" {
    try std.testing.expectEqual(@as(u32, 0), @intFromEnum(NotifierResult.done));
    try std.testing.expectEqual(@as(u32, 1), @intFromEnum(NotifierResult.ok));
    try std.testing.expectEqual(@as(u32, 2), @intFromEnum(NotifierResult.stop));
}

test "notifier result helper surface stays explicit" {
    try std.testing.expectEqual(@as(?NotifierResult, .done), resultFromInt(@intFromEnum(NotifierResult.done)));
    try std.testing.expectEqual(@as(?NotifierResult, .ok), resultFromInt(@intFromEnum(NotifierResult.ok)));
    try std.testing.expectEqual(@as(?NotifierResult, .stop), resultFromInt(@intFromEnum(NotifierResult.stop)));
    try std.testing.expectEqual(@as(?NotifierResult, null), resultFromInt(7));
    try std.testing.expect(resultIsKnown(@intFromEnum(NotifierResult.done)));
    try std.testing.expect(resultIsKnown(@intFromEnum(NotifierResult.ok)));
    try std.testing.expect(resultIsKnown(@intFromEnum(NotifierResult.stop)));
    try std.testing.expect(!resultIsKnown(7));
    try std.testing.expect(!resultStopsChainValue(@intFromEnum(NotifierResult.done)));
    try std.testing.expect(!resultStopsChainValue(@intFromEnum(NotifierResult.ok)));
    try std.testing.expect(resultStopsChainValue(@intFromEnum(NotifierResult.stop)));
    try std.testing.expect(!resultStopsChainValue(7));
    try std.testing.expect(!resultStopsChain(.done));
    try std.testing.expect(!resultStopsChain(.ok));
    try std.testing.expect(resultStopsChain(.stop));
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

    const increase_expected_size = std.mem.alignForward(
        usize,
        (@sizeOf(usize) * 2) + (@sizeOf(i32) * 2),
        @alignOf(NotifierChainPriorityIncrease),
    );
    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(NotifierChainPriorityIncrease));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(NotifierChainPriorityIncrease, "previous_index"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(NotifierChainPriorityIncrease, "current_index"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(NotifierChainPriorityIncrease, "previous_priority"));
    try std.testing.expectEqual(
        @as(usize, (@sizeOf(usize) * 2) + @sizeOf(i32)),
        @offsetOf(NotifierChainPriorityIncrease, "current_priority"),
    );
    try std.testing.expectEqual(increase_expected_size, @sizeOf(NotifierChainPriorityIncrease));
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

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(ListBackLinkBreak));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(ListBackLinkBreak, "current_index"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(ListBackLinkBreak, "expected_prev"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(ListBackLinkBreak, "actual_prev"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 3), @sizeOf(ListBackLinkBreak));

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(HListPrevLinkBreak));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(HListPrevLinkBreak, "current_index"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(HListPrevLinkBreak, "expected_pprev"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(HListPrevLinkBreak, "actual_pprev"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 3), @sizeOf(HListPrevLinkBreak));
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

test "notifier priority increase helper returns null for empty and single-node chains" {
    try std.testing.expect(firstChainPriorityIncrease(null) == null);

    const node = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 9,
    };

    try std.testing.expect(firstChainPriorityIncrease(&node) == null);
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

    try std.testing.expect(firstChainPriorityIncrease(&first) == null);
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
    try std.testing.expectEqual(@as(usize, 2), increase.previous_index);
    try std.testing.expectEqual(@as(usize, 3), increase.current_index);
    try std.testing.expectEqual(@as(i32, 2), increase.previous_priority);
    try std.testing.expectEqual(@as(i32, 7), increase.current_priority);
}

test "list helper accepts a sentinel-only list" {
    var head = ListHead{ .next = 0, .prev = 0 };
    head.next = @intFromPtr(&head);
    head.prev = @intFromPtr(&head);

    try std.testing.expect(firstBrokenBacklink(&head) == null);
    try std.testing.expect(listHasConsistentBacklinks(&head));
}

test "list helper treats a null head as absent rather than consistent" {
    try std.testing.expect(firstBrokenBacklink(null) == null);
    try std.testing.expect(!listHasConsistentBacklinks(null));
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

    const breakage = firstBrokenBacklink(&head) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);
    try std.testing.expect(!listHasConsistentBacklinks(&head));
}

test "hlist helper accepts an empty head" {
    const head = HListHead{ .first = 0 };

    try std.testing.expect(firstPprevMatchesHead(&head));
    try std.testing.expect(firstBrokenPrevLink(&head) == null);
    try std.testing.expect(hlistHasConsistentPrevLinks(&head));
}

test "hlist helper treats a null head as absent rather than consistent" {
    try std.testing.expect(!firstPprevMatchesHead(null));
    try std.testing.expect(firstBrokenPrevLink(null) == null);
    try std.testing.expect(!hlistHasConsistentPrevLinks(null));
}

test "hlist helper accepts a bounded chain whose first pprev targets the head" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var second = HListNode{ .next = 0, .pprev = 0 };
    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = 0;
    second.pprev = @intFromPtr(&first.next);

    try std.testing.expect(firstPprevMatchesHead(&head));
    try std.testing.expect(firstBrokenPrevLink(&head) == null);
    try std.testing.expect(hlistHasConsistentPrevLinks(&head));
}

test "hlist helper rejects a mismatched first-node pprev witness" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    head.first = @intFromPtr(&first);
    first.next = 0;
    first.pprev = 0;

    try std.testing.expect(!firstPprevMatchesHead(&head));

    const breakage = firstBrokenPrevLink(&head) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, 0), breakage.actual_pprev);
    try std.testing.expect(!hlistHasConsistentPrevLinks(&head));
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

    const breakage = firstBrokenPrevLink(&head) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);
    try std.testing.expect(!hlistHasConsistentPrevLinks(&head));
}
