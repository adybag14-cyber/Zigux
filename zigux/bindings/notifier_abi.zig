const std = @import("std");
const testing = std.testing;

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
