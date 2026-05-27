const std = @import("std");
const transfer_contract = @import("bytestream_fifo_transfer_contract");

test "phase 5 bytestream fifo transfer contract keeps the Linux-style transfer packet explicit" {
    const contract = transfer_contract.referencePattern();

    try std.testing.expectEqualStrings("samples/kfifo/bytestream-example.c", contract.anchor);
    try std.testing.expectEqual(@as(usize, 5), contract.initial_string_copy_count);
    try std.testing.expectEqual(@as(usize, 15), contract.len_after_initial_fill);
    try std.testing.expectEqualSlices(u8, "hello", contract.first_drain[0..]);
    try std.testing.expectEqual(@as(usize, 5), contract.first_drain_count);
    try std.testing.expectEqualSlices(u8, &.{ 0, 1 }, contract.second_drain[0..]);
    try std.testing.expectEqual(@as(usize, 2), contract.second_drain_count);
    try std.testing.expectEqual(@as(usize, 2), contract.requeue_count);
    try std.testing.expectEqual(@as(u8, 2), contract.skipped_byte);
    try std.testing.expectEqual(@as(u8, 3), contract.peek_value);
    try std.testing.expectEqual(@as(usize, 8), contract.preview_len);
    try std.testing.expectEqual(@as(usize, 32), contract.preview_total_visible);
    try std.testing.expectEqualSlices(u8, &.{ 3, 4, 5, 6, 7, 8, 9, 0 }, contract.preview_prefix[0..]);
}

test "phase 5 bytestream fifo transfer contract keeps helper and bounded enqueue cues reviewable" {
    const contract = transfer_contract.referencePattern();

    try std.testing.expectEqualSlices(u8, "hel", contract.short_drain_prefix[0..]);
    try std.testing.expectEqualSlices(u8, "lo", contract.short_drain_remainder[0..]);
    try std.testing.expectEqual(@as(usize, 4), contract.partial_enqueue_requested_len);
    try std.testing.expectEqual(@as(usize, 2), contract.partial_enqueue_copied_len);
    try std.testing.expectEqual(@as(usize, 2), contract.partial_enqueue_dropped_len);
    try std.testing.expect(contract.full_queue_rejects_overflow);
    try std.testing.expect(contract.sample_remains_non_runtime);
    try std.testing.expect(contract.sample_provides_selfcheck);
    try std.testing.expect(contract.fixed_buffer_storage);
}
