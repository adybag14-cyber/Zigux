const std = @import("std");

const atomic_helpers = @import("atomic_helpers");

test "phase3 atomic compare-exchange strong succeeds and returns null old value" {
    var word: u32 = 0x10;

    try std.testing.expectEqual(
        @as(?u32, null),
        try atomic_helpers.compareExchangeStrong(u32, &word, 0x10, 0x20, .seq_cst, .seq_cst),
    );
    try std.testing.expectEqual(@as(u32, 0x20), word);

    try std.testing.expectEqual(
        @as(?u32, null),
        try atomic_helpers.compareExchangeStrong(u32, &word, 0x20, 0x30, .release, .monotonic),
    );
    try std.testing.expectEqual(@as(u32, 0x30), word);
}

test "phase3 atomic compare-exchange strong mismatch returns observed value" {
    var word: u32 = 0x44;

    try std.testing.expectEqual(
        @as(?u32, 0x44),
        try atomic_helpers.compareExchangeStrong(u32, &word, 0x40, 0x55, .acq_rel, .acquire),
    );
    try std.testing.expectEqual(@as(u32, 0x44), word);

    try std.testing.expectEqual(
        @as(?u32, 0x44),
        try atomic_helpers.compareExchangeStrong(u32, &word, 0x45, 0x66, .acquire, .monotonic),
    );
    try std.testing.expectEqual(@as(u32, 0x44), word);
}

test "phase3 atomic compare-exchange weak retries success and preserves mismatch" {
    var word: u32 = 7;
    var attempts: usize = 0;

    while (true) {
        attempts += 1;
        const result = try atomic_helpers.compareExchangeWeak(u32, &word, 7, 11, .release, .monotonic);
        if (result == null) break;
        try std.testing.expectEqual(@as(?u32, 7), result);
        try std.testing.expectEqual(@as(u32, 7), word);
        try std.testing.expect(attempts < 32);
    }
    try std.testing.expectEqual(@as(u32, 11), word);

    try std.testing.expectEqual(
        @as(?u32, 11),
        try atomic_helpers.compareExchangeWeak(u32, &word, 7, 13, .release, .monotonic),
    );
    try std.testing.expectEqual(@as(u32, 11), word);
}

test "phase3 atomic compare-exchange wrappers fail closed before touching storage" {
    var word: u32 = 0xAA;

    try std.testing.expectError(
        error.InvalidFailureOrdering,
        atomic_helpers.compareExchangeStrong(u32, &word, 0xAA, 0xBB, .release, .acquire),
    );
    try std.testing.expectEqual(@as(u32, 0xAA), word);

    try std.testing.expectError(
        error.InvalidFailureOrdering,
        atomic_helpers.compareExchangeWeak(u32, &word, 0xAA, 0xCC, .acq_rel, .seq_cst),
    );
    try std.testing.expectEqual(@as(u32, 0xAA), word);

    try std.testing.expectError(
        error.InvalidFailureOrdering,
        atomic_helpers.compareExchangeStrong(u32, &word, 0xAA, 0xDD, .unordered, .monotonic),
    );
    try std.testing.expectEqual(@as(u32, 0xAA), word);
}
