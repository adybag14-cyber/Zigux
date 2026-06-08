const std = @import("std");
const atomic = @import("atomic_helpers");

test "atomic exchange reports old values while replacing storage" {
    var byte_value: u8 = 0x12;

    try std.testing.expectEqual(@as(u8, 0x12), try atomic.exchange(u8, &byte_value, 0x34, .monotonic));
    try std.testing.expectEqual(@as(u8, 0x34), byte_value);

    try std.testing.expectEqual(@as(u8, 0x34), try atomic.exchange(u8, &byte_value, 0x56, .release));
    try std.testing.expectEqual(@as(u8, 0x56), byte_value);

    var word_value: u32 = 0x1020_3040;

    try std.testing.expectEqual(
        @as(u32, 0x1020_3040),
        try atomic.exchange(u32, &word_value, 0xA0B0_C0D0, .acq_rel),
    );
    try std.testing.expectEqual(@as(u32, 0xA0B0_C0D0), word_value);
}

test "atomic exchange accepts the shared RMW ordering set" {
    var value: u16 = 1;

    try std.testing.expectEqual(@as(u16, 1), try atomic.exchange(u16, &value, 2, .monotonic));
    try std.testing.expectEqual(@as(u16, 2), try atomic.exchange(u16, &value, 3, .acquire));
    try std.testing.expectEqual(@as(u16, 3), try atomic.exchange(u16, &value, 4, .release));
    try std.testing.expectEqual(@as(u16, 4), try atomic.exchange(u16, &value, 5, .acq_rel));
    try std.testing.expectEqual(@as(u16, 5), try atomic.exchange(u16, &value, 6, .seq_cst));
    try std.testing.expectEqual(@as(u16, 6), value);
}

test "atomic exchange rejects unordered without mutation" {
    var value: u32 = 0xFEED_FACE;

    try std.testing.expectError(
        error.InvalidRmwOrdering,
        atomic.exchange(u32, &value, 0xDEAD_BEEF, .unordered),
    );
    try std.testing.expectEqual(@as(u32, 0xFEED_FACE), value);
}

test "atomic exchange preserves pointer-sized payload handoff" {
    var first: usize = 0x1111;
    var second: usize = 0x2222;
    var slot: usize = @intFromPtr(&first);

    try std.testing.expectEqual(@intFromPtr(&first), try atomic.exchange(usize, &slot, @intFromPtr(&second), .seq_cst));
    try std.testing.expectEqual(@intFromPtr(&second), slot);
}
