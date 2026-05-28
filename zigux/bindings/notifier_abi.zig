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

pub const notifier_block_size = @sizeOf(NotifierBlock);
pub const notifier_block_align = @alignOf(NotifierBlock);
pub const notifier_block_notifier_call_offset = @offsetOf(NotifierBlock, "notifier_call");
pub const notifier_block_next_offset = @offsetOf(NotifierBlock, "next");
pub const notifier_block_priority_offset = @offsetOf(NotifierBlock, "priority");

pub const notifier_chain_priority_increase_size = @sizeOf(NotifierChainPriorityIncrease);
pub const notifier_chain_priority_increase_align = @alignOf(NotifierChainPriorityIncrease);
pub const notifier_chain_priority_increase_previous_index_offset =
    @offsetOf(NotifierChainPriorityIncrease, "previous_index");
pub const notifier_chain_priority_increase_current_index_offset =
    @offsetOf(NotifierChainPriorityIncrease, "current_index");
pub const notifier_chain_priority_increase_previous_priority_offset =
    @offsetOf(NotifierChainPriorityIncrease, "previous_priority");
pub const notifier_chain_priority_increase_current_priority_offset =
    @offsetOf(NotifierChainPriorityIncrease, "current_priority");

pub const list_head_size = @sizeOf(ListHead);
pub const list_head_align = @alignOf(ListHead);
pub const list_head_next_offset = @offsetOf(ListHead, "next");
pub const list_head_prev_offset = @offsetOf(ListHead, "prev");

pub const hlist_head_size = @sizeOf(HListHead);
pub const hlist_head_align = @alignOf(HListHead);
pub const hlist_head_first_offset = @offsetOf(HListHead, "first");

pub const hlist_node_size = @sizeOf(HListNode);
pub const hlist_node_align = @alignOf(HListNode);
pub const hlist_node_next_offset = @offsetOf(HListNode, "next");
pub const hlist_node_pprev_offset = @offsetOf(HListNode, "pprev");

pub const list_back_link_break_size = @sizeOf(ListBackLinkBreak);
pub const list_back_link_break_align = @alignOf(ListBackLinkBreak);
pub const list_back_link_break_current_index_offset = @offsetOf(ListBackLinkBreak, "current_index");
pub const list_back_link_break_expected_prev_offset = @offsetOf(ListBackLinkBreak, "expected_prev");
pub const list_back_link_break_actual_prev_offset = @offsetOf(ListBackLinkBreak, "actual_prev");

pub const hlist_prev_link_break_size = @sizeOf(HListPrevLinkBreak);
pub const hlist_prev_link_break_align = @alignOf(HListPrevLinkBreak);
pub const hlist_prev_link_break_current_index_offset = @offsetOf(HListPrevLinkBreak, "current_index");
pub const hlist_prev_link_break_expected_pprev_offset = @offsetOf(HListPrevLinkBreak, "expected_pprev");
pub const hlist_prev_link_break_actual_pprev_offset = @offsetOf(HListPrevLinkBreak, "actual_pprev");

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

pub fn listIsEmpty(head: ?*const ListHead) bool {
    const sentinel = head orelse return false;
    const sentinel_ptr = @intFromPtr(sentinel);
    return sentinel.next == sentinel_ptr and sentinel.prev == sentinel_ptr;
}

pub fn listLength(head: ?*const ListHead) usize {
    const sentinel = head orelse return 0;
    var count: usize = 0;
    var cursor = listHeadFromRaw(sentinel.next);

    while (cursor) |node| {
        if (node == sentinel) break;
        count += 1;
        cursor = listHeadFromRaw(node.next);
    }

    return count;
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

pub fn hlistIsEmpty(head: ?*const HListHead) bool {
    const first_head = head orelse return false;
    return first_head.first == 0;
}

pub fn firstPprevMatchesHead(head: ?*const HListHead) bool {
    const first_head = head orelse return false;
    const first_node = hlistNodeFromRaw(first_head.first) orelse return true;
    return first_node.pprev == @intFromPtr(&first_head.first);
}

pub fn hlistLength(head: ?*const HListHead) usize {
    var count: usize = 0;
    var cursor = hlistNodeFromRaw((head orelse return 0).first);

    while (cursor) |node| {
        count += 1;
        cursor = hlistNodeFromRaw(node.next);
    }

    return count;
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

pub fn hlistTailNextIsNull(head: ?*const HListHead) bool {
    const first_head = head orelse return false;
    var cursor = hlistNodeFromRaw(first_head.first);
    var tail: ?*const HListNode = null;

    while (cursor) |node| {
        tail = node;
        cursor = hlistNodeFromRaw(node.next);
    }

    return if (tail) |node| node.next == 0 else true;
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

test "notifier block layout constants stay aligned with the exported ABI header" {
    const expected_size = std.mem.alignForward(
        usize,
        (@sizeOf(usize) * 2) + @sizeOf(i32),
        @alignOf(NotifierBlock),
    );
    try std.testing.expectEqual(@as(usize, @alignOf(usize)), notifier_block_align);
    try std.testing.expectEqual(@as(usize, 0), notifier_block_notifier_call_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), notifier_block_next_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), notifier_block_priority_offset);
    try std.testing.expectEqual(expected_size, notifier_block_size);
    try std.testing.expectEqual(notifier_block_size, @sizeOf(NotifierBlock));
    try std.testing.expectEqual(notifier_block_align, @alignOf(NotifierBlock));
}

test "notifier priority increase layout constants stay aligned with the exported ABI header" {
    const expected_size = std.mem.alignForward(
        usize,
        (@sizeOf(usize) * 2) + (@sizeOf(i32) * 2),
        @alignOf(NotifierChainPriorityIncrease),
    );
    try std.testing.expectEqual(@as(usize, @alignOf(usize)), notifier_chain_priority_increase_align);
    try std.testing.expectEqual(@as(usize, 0), notifier_chain_priority_increase_previous_index_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), notifier_chain_priority_increase_current_index_offset);
    try std.testing.expectEqual(
        @as(usize, @sizeOf(usize) * 2),
        notifier_chain_priority_increase_previous_priority_offset,
    );
    try std.testing.expectEqual(
        @as(usize, (@sizeOf(usize) * 2) + @sizeOf(i32)),
        notifier_chain_priority_increase_current_priority_offset,
    );
    try std.testing.expectEqual(expected_size, notifier_chain_priority_increase_size);
    try std.testing.expectEqual(notifier_chain_priority_increase_size, @sizeOf(NotifierChainPriorityIncrease));
    try std.testing.expectEqual(notifier_chain_priority_increase_align, @alignOf(NotifierChainPriorityIncrease));
}

test "list and hlist layout constants stay aligned with the exported ABI header" {
    try std.testing.expectEqual(@as(usize, @alignOf(usize)), list_head_align);
    try std.testing.expectEqual(@as(usize, 0), list_head_next_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), list_head_prev_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), list_head_size);
    try std.testing.expectEqual(list_head_size, @sizeOf(ListHead));
    try std.testing.expectEqual(list_head_align, @alignOf(ListHead));

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), hlist_head_align);
    try std.testing.expectEqual(@as(usize, 0), hlist_head_first_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), hlist_head_size);
    try std.testing.expectEqual(hlist_head_size, @sizeOf(HListHead));
    try std.testing.expectEqual(hlist_head_align, @alignOf(HListHead));

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), hlist_node_align);
    try std.testing.expectEqual(@as(usize, 0), hlist_node_next_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), hlist_node_pprev_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), hlist_node_size);
    try std.testing.expectEqual(hlist_node_size, @sizeOf(HListNode));
    try std.testing.expectEqual(hlist_node_align, @alignOf(HListNode));
}

test "list and hlist break layout constants stay aligned with the exported ABI header" {
    try std.testing.expectEqual(@as(usize, @alignOf(usize)), list_back_link_break_align);
    try std.testing.expectEqual(@as(usize, 0), list_back_link_break_current_index_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), list_back_link_break_expected_prev_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), list_back_link_break_actual_prev_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 3), list_back_link_break_size);
    try std.testing.expectEqual(list_back_link_break_size, @sizeOf(ListBackLinkBreak));
    try std.testing.expectEqual(list_back_link_break_align, @alignOf(ListBackLinkBreak));

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), hlist_prev_link_break_align);
    try std.testing.expectEqual(@as(usize, 0), hlist_prev_link_break_current_index_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), hlist_prev_link_break_expected_pprev_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), hlist_prev_link_break_actual_pprev_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 3), hlist_prev_link_break_size);
    try std.testing.expectEqual(hlist_prev_link_break_size, @sizeOf(HListPrevLinkBreak));
    try std.testing.expectEqual(hlist_prev_link_break_align, @alignOf(HListPrevLinkBreak));
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

test "list emptiness helper accepts a sentinel-only list" {
    var head = ListHead{ .next = 0, .prev = 0 };
    head.next = @intFromPtr(&head);
    head.prev = @intFromPtr(&head);

    try std.testing.expect(listIsEmpty(&head));
    try std.testing.expectEqual(@as(usize, 0), listLength(&head));
}

test "list emptiness helper treats a null head as absent rather than empty" {
    try std.testing.expect(!listIsEmpty(null));
    try std.testing.expectEqual(@as(usize, 0), listLength(null));
}

test "list emptiness helper rejects a list with nodes or a broken sentinel" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&first);
    first.next = @intFromPtr(&head);
    first.prev = @intFromPtr(&head);
    try std.testing.expect(!listIsEmpty(&head));
    try std.testing.expectEqual(@as(usize, 1), listLength(&head));

    head.next = @intFromPtr(&head);
    head.prev = 0;
    try std.testing.expect(!listIsEmpty(&head));
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
    try std.testing.expectEqual(@as(usize, 2), listLength(&head));
}

test "hlist helper accepts an empty head" {
    const head = HListHead{ .first = 0 };

    try std.testing.expect(hlistIsEmpty(&head));
    try std.testing.expect(firstPprevMatchesHead(&head));
    try std.testing.expect(firstBrokenPrevLink(&head) == null);
    try std.testing.expect(hlistHasConsistentPrevLinks(&head));
    try std.testing.expectEqual(@as(usize, 0), hlistLength(&head));
    try std.testing.expect(hlistTailNextIsNull(&head));
}

test "hlist helper treats a null head as absent rather than consistent" {
    try std.testing.expect(!hlistIsEmpty(null));
    try std.testing.expect(!firstPprevMatchesHead(null));
    try std.testing.expect(firstBrokenPrevLink(null) == null);
    try std.testing.expect(!hlistHasConsistentPrevLinks(null));
    try std.testing.expectEqual(@as(usize, 0), hlistLength(null));
    try std.testing.expect(!hlistTailNextIsNull(null));
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

    try std.testing.expect(!hlistIsEmpty(&head));
    try std.testing.expect(firstPprevMatchesHead(&head));
    try std.testing.expect(firstBrokenPrevLink(&head) == null);
    try std.testing.expect(hlistHasConsistentPrevLinks(&head));
    try std.testing.expectEqual(@as(usize, 2), hlistLength(&head));
    try std.testing.expect(hlistTailNextIsNull(&head));
}

test "hlist helper rejects a mismatched first-node pprev witness" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    head.first = @intFromPtr(&first);
    first.next = 0;
    first.pprev = 0;

    try std.testing.expect(!hlistIsEmpty(&head));
    try std.testing.expect(!firstPprevMatchesHead(&head));

    const breakage = firstBrokenPrevLink(&head) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, 0), breakage.actual_pprev);
    try std.testing.expect(!hlistHasConsistentPrevLinks(&head));
    try std.testing.expectEqual(@as(usize, 1), hlistLength(&head));
    try std.testing.expect(hlistTailNextIsNull(&head));
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
    try std.testing.expect(!hlistIsEmpty(&head));
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);
    try std.testing.expect(!hlistHasConsistentPrevLinks(&head));
    try std.testing.expectEqual(@as(usize, 2), hlistLength(&head));
    try std.testing.expect(hlistTailNextIsNull(&head));
}
