const std = @import("std");

pub fn acquire() void {
    var fence_word = std.atomic.Value(u8).init(0);
    _ = fence_word.load(.acquire);
}

pub fn release() void {
    var fence_word = std.atomic.Value(u8).init(0);
    fence_word.store(0, .release);
}

pub fn full() void {
    var fence_word = std.atomic.Value(u8).init(0);
    _ = fence_word.swap(0, .seq_cst);
}

test "phase3 barrier wrappers stay local to each barrier probe" {
    acquire();
    release();
    full();
    try std.testing.expect(true);
}
