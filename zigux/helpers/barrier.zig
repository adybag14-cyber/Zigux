const std = @import("std");

var fence_word = std.atomic.Value(u8).init(0);

test "phase3 barrier wrappers stay on an atomic backing word" {
    acquire();
    release();
    full();
    try std.testing.expectEqual(@as(u8, 0), fence_word.load(.seq_cst));
}

pub fn acquire() void {
    _ = fence_word.load(.acquire);
}

pub fn release() void {
    fence_word.store(0, .release);
}

pub fn full() void {
    _ = fence_word.swap(0, .seq_cst);
}
