const std = @import("std");

const atomic = @import("atomic_helpers");

test "phase3 atomic load contract keeps allowed orderings explicit" {
    var word: u32 = 0x1234_5678;
    const const_ptr: *const u32 = &word;

    try std.testing.expect(atomic.loadOrderAllowed(.monotonic));
    try std.testing.expect(atomic.loadOrderAllowed(.acquire));
    try std.testing.expect(atomic.loadOrderAllowed(.seq_cst));

    try std.testing.expectEqual(@as(u32, 0x1234_5678), try atomic.load(u32, const_ptr, .monotonic));
    word = 0xCAFE_BABE;
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), try atomic.load(u32, const_ptr, .acquire));
    word = 0x0BAD_C0DE;
    try std.testing.expectEqual(@as(u32, 0x0BAD_C0DE), try atomic.load(u32, const_ptr, .seq_cst));
}

test "phase3 atomic load contract rejects store-only orderings without touching storage" {
    var word: u32 = 0x55AA_33CC;
    const const_ptr: *const u32 = &word;

    try std.testing.expect(!atomic.loadOrderAllowed(.unordered));
    try std.testing.expect(!atomic.loadOrderAllowed(.release));
    try std.testing.expect(!atomic.loadOrderAllowed(.acq_rel));

    try std.testing.expectError(error.InvalidLoadOrdering, atomic.load(u32, const_ptr, .unordered));
    try std.testing.expectError(error.InvalidLoadOrdering, atomic.load(u32, const_ptr, .release));
    try std.testing.expectError(error.InvalidLoadOrdering, atomic.load(u32, const_ptr, .acq_rel));
    try std.testing.expectEqual(@as(u32, 0x55AA_33CC), word);
}

test "phase3 atomic store contract keeps allowed orderings explicit" {
    var word: u32 = 1;

    try std.testing.expect(atomic.storeOrderAllowed(.monotonic));
    try std.testing.expect(atomic.storeOrderAllowed(.release));
    try std.testing.expect(atomic.storeOrderAllowed(.seq_cst));

    try atomic.store(u32, &word, 7, .monotonic);
    try std.testing.expectEqual(@as(u32, 7), word);
    try atomic.store(u32, &word, 19, .release);
    try std.testing.expectEqual(@as(u32, 19), word);
    try atomic.store(u32, &word, 23, .seq_cst);
    try std.testing.expectEqual(@as(u32, 23), word);
}

test "phase3 atomic store contract rejects load-only orderings without touching storage" {
    var byte: u8 = 0xA5;

    try std.testing.expect(!atomic.storeOrderAllowed(.unordered));
    try std.testing.expect(!atomic.storeOrderAllowed(.acquire));
    try std.testing.expect(!atomic.storeOrderAllowed(.acq_rel));

    try std.testing.expectError(error.InvalidStoreOrdering, atomic.store(u8, &byte, 0x11, .unordered));
    try std.testing.expectError(error.InvalidStoreOrdering, atomic.store(u8, &byte, 0x22, .acquire));
    try std.testing.expectError(error.InvalidStoreOrdering, atomic.store(u8, &byte, 0x33, .acq_rel));
    try std.testing.expectEqual(@as(u8, 0xA5), byte);
}
