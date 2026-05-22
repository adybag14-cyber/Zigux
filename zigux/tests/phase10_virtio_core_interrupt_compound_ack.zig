const std = @import("std");
const virtio_core = @import("virtio_core");

test "phase10 virtio core interrupt compound ack replay keeps queue-used and config-change bits isolated" {
    var core = try virtio_core.VirtioCoreLab.init(0x1044, 2);
    core.stageInterrupt(0b0101);

    var ack = core.ackInterrupt(0b0001);
    try std.testing.expectEqual(@as(u8, 0b0101), ack.pending_before);
    try std.testing.expectEqual(@as(u8, 0b0001), ack.cleared_bits);
    try std.testing.expectEqual(@as(u8, 0b0100), ack.pending_after);
    try std.testing.expect(!ack.all_acknowledged);

    ack = core.ackInterrupt(0b0100);
    try std.testing.expectEqual(@as(u8, 0b0100), ack.pending_before);
    try std.testing.expectEqual(@as(u8, 0b0100), ack.cleared_bits);
    try std.testing.expectEqual(@as(u8, 0), ack.pending_after);
    try std.testing.expect(ack.all_acknowledged);
}

test "phase10 virtio core interrupt compound ack replay ignores bits that were never pending" {
    var core = try virtio_core.VirtioCoreLab.init(0x1045, 1);
    core.stageInterrupt(0b0011);

    const ack = core.ackInterrupt(0b0111);
    try std.testing.expectEqual(@as(u8, 0b0011), ack.pending_before);
    try std.testing.expectEqual(@as(u8, 0b0011), ack.cleared_bits);
    try std.testing.expectEqual(@as(u8, 0), ack.pending_after);
    try std.testing.expect(ack.all_acknowledged);
}
