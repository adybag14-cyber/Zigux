const std = @import("std");
const sample = @import("bytestream_fifo_sample");

test "phase 5 bytestream fifo sample stays in the reference-sample lane" {
    const descriptor = sample.BytestreamFifoSample.descriptor();

    try std.testing.expectEqualStrings("bytestream_fifo", descriptor.name);
    try std.testing.expectEqualStrings("samples/kfifo/bytestream-example.c", descriptor.anchor);
    try std.testing.expect(!descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selfcheck);
}

test "phase 5 bytestream fifo sample replays exact queue behavior from the Linux anchor" {
    var module = sample.BytestreamFifoSample{};
    const replay = try module.runAnchorReplay();

    try std.testing.expectEqual(@as(usize, 15), replay.len_after_initial_fill);
    try std.testing.expectEqualStrings("hello", replay.first_out[0..]);
    try std.testing.expectEqualSlices(u8, &.{ 0, 1 }, replay.second_out[0..]);
    try std.testing.expectEqual(@as(u8, 2), replay.skipped_byte);
    try std.testing.expectEqual(@as(u8, 3), replay.peek_value);
    try std.testing.expectEqual(@as(u8, 20), replay.fill_start);
    try std.testing.expectEqual(@as(u8, 42), replay.fill_end);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), replay.final_len);
    try std.testing.expectEqual(@as(usize, 4), replay.checked_focus.len);
    try std.testing.expectEqualSlices(u8, sample.expected_anchor_result[0..], replay.final_sequence[0..]);
    try std.testing.expectEqual(@as(usize, 0), module.count());

    const second = try module.runAnchorReplay();
    try std.testing.expectEqualSlices(u8, replay.final_sequence[0..], second.final_sequence[0..]);
}

test "phase 5 bytestream fifo sample keeps bounded helper behavior explicit" {
    var module = sample.BytestreamFifoSample{};

    try std.testing.expectEqual(@as(?u8, null), module.peekByte());
    try std.testing.expectEqual(@as(?u8, null), module.skipByte());
    try std.testing.expectEqual(@as(usize, 0), module.enqueueSlice(&.{}));

    var count: u8 = 0;
    while (count < sample.BytestreamFifoSample.capacity) : (count += 1) {
        try std.testing.expect(module.pushByte(count));
    }
    try std.testing.expect(!module.pushByte(255));
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), module.count());
    try std.testing.expectEqual(@as(?u8, 0), module.peekByte());
    try std.testing.expectEqual(@as(?u8, 0), module.skipByte());
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity - 1), module.count());

    module.reset();
    try std.testing.expectEqual(@as(usize, 0), module.count());
    try std.testing.expectEqual(@as(?u8, null), module.popByte());
}
