const std = @import("std");
const sample = @import("bytestream_fifo.zig");

pub const linux_anchor = "samples/kfifo/bytestream-example.c";

pub const TransferContract = struct {
    anchor: []const u8,
    initial_string_copy_count: usize,
    len_after_initial_fill: usize,
    first_drain: [5]u8,
    first_drain_count: usize,
    second_drain: [2]u8,
    second_drain_count: usize,
    requeue_count: usize,
    skipped_byte: u8,
    peek_value: u8,
    preview_prefix: [8]u8,
    preview_len: usize,
    preview_total_visible: usize,
    short_drain_prefix: [3]u8,
    short_drain_remainder: [2]u8,
    partial_enqueue_requested_len: usize,
    partial_enqueue_copied_len: usize,
    partial_enqueue_dropped_len: usize,
    full_queue_rejects_overflow: bool,
    sample_remains_non_runtime: bool,
    sample_provides_selfcheck: bool,
    fixed_buffer_storage: bool,
};

pub fn referencePattern() TransferContract {
    return .{
        .anchor = linux_anchor,
        .initial_string_copy_count = 5,
        .len_after_initial_fill = 15,
        .first_drain = "hello".*,
        .first_drain_count = 5,
        .second_drain = .{ 0, 1 },
        .second_drain_count = 2,
        .requeue_count = 2,
        .skipped_byte = 2,
        .peek_value = 3,
        .preview_prefix = .{ 3, 4, 5, 6, 7, 8, 9, 0 },
        .preview_len = 8,
        .preview_total_visible = 32,
        .short_drain_prefix = "hel".*,
        .short_drain_remainder = "lo".*,
        .partial_enqueue_requested_len = 4,
        .partial_enqueue_copied_len = 2,
        .partial_enqueue_dropped_len = 2,
        .full_queue_rejects_overflow = true,
        .sample_remains_non_runtime = true,
        .sample_provides_selfcheck = true,
        .fixed_buffer_storage = true,
    };
}

test "bytestream fifo transfer companion keeps anchor replay counts explicit" {
    const contract = referencePattern();

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

test "bytestream fifo transfer companion keeps helper and partial-enqueue boundaries explicit" {
    const contract = referencePattern();

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

test "bytestream fifo transfer companion stays aligned with the shipped sample root replay" {
    const contract = referencePattern();
    var module = sample.BytestreamFifoSample{};

    try module.init();
    const replay = try module.runAnchorReplay();

    try std.testing.expectEqualStrings(contract.anchor, sample.BytestreamFifoSample.descriptor().anchor);
    try std.testing.expectEqualStrings(contract.anchor, replay.anchor);
    try std.testing.expectEqual(contract.initial_string_copy_count, replay.initial_string_copy_count);
    try std.testing.expectEqual(contract.len_after_initial_fill, replay.len_after_initial_fill);
    try std.testing.expectEqualSlices(u8, contract.first_drain[0..], replay.first_out[0..]);
    try std.testing.expectEqual(contract.first_drain_count, replay.first_drain_count);
    try std.testing.expectEqualSlices(u8, contract.second_drain[0..], replay.second_out[0..]);
    try std.testing.expectEqual(contract.second_drain_count, replay.second_drain_count);
    try std.testing.expectEqual(contract.requeue_count, replay.requeue_count);
    try std.testing.expectEqual(contract.skipped_byte, replay.skipped_byte);
    try std.testing.expectEqual(contract.peek_value, replay.peek_value);
    try std.testing.expectEqual(contract.preview_len, replay.preview_len);
    try std.testing.expectEqual(contract.preview_total_visible, replay.preview_total_visible);
    try std.testing.expectEqualSlices(u8, contract.preview_prefix[0..], replay.preview_prefix[0..]);
    try std.testing.expect(contract.sample_remains_non_runtime);
    try std.testing.expect(contract.sample_provides_selfcheck);
    try std.testing.expect(contract.fixed_buffer_storage);
    try std.testing.expectEqual(sample.StorageBacking.embedded_fixed_buffer, sample.BytestreamFifoSample.descriptor().storage_backing);

    module.reset();
    try std.testing.expectEqual(@as(usize, 5), module.enqueueSlice("hello"));
    var prefix: [3]u8 = undefined;
    try std.testing.expectEqual(@as(usize, prefix.len), module.drain(prefix[0..]));
    try std.testing.expectEqualSlices(u8, contract.short_drain_prefix[0..], prefix[0..]);
    var remainder: [2]u8 = undefined;
    try std.testing.expectEqual(@as(usize, remainder.len), module.dequeueSlice(remainder[0..]));
    try std.testing.expectEqualSlices(u8, contract.short_drain_remainder[0..], remainder[0..]);

    const partial = try module.runPartialEnqueueBoundaryReplay();
    try std.testing.expectEqual(contract.partial_enqueue_requested_len, partial.requested_extra_len);
    try std.testing.expectEqual(contract.partial_enqueue_copied_len, partial.copied_extra_len);
    try std.testing.expectEqual(contract.partial_enqueue_dropped_len, partial.dropped_extra_len);
    try std.testing.expectEqual(contract.full_queue_rejects_overflow, partial.occupancy_after_extra.full);
}
