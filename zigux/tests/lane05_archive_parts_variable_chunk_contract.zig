const std = @import("std");

const Packet = struct {
    size: usize,
    chunk_bytes: usize,
    part_count: usize,
};

fn expectedPartCount(size: usize, chunk_bytes: usize) usize {
    return (size + chunk_bytes - 1) / chunk_bytes;
}

fn finalShardSize(size: usize, chunk_bytes: usize) usize {
    const remainder = size % chunk_bytes;
    return if (remainder == 0) chunk_bytes else remainder;
}

fn requireValidPacket(packet: Packet) !void {
    try std.testing.expect(packet.size > 0);
    try std.testing.expect(packet.chunk_bytes > 0);
    try std.testing.expectEqual(expectedPartCount(packet.size, packet.chunk_bytes), packet.part_count);
    try std.testing.expect(finalShardSize(packet.size, packet.chunk_bytes) > 0);
    try std.testing.expect(finalShardSize(packet.size, packet.chunk_bytes) <= packet.chunk_bytes);
}

test "Lane 05 archive parts packet supports the shipped default chunk size" {
    const packet = Packet{
        .size = 58_159_088,
        .chunk_bytes = 786_432,
        .part_count = 74,
    };

    try requireValidPacket(packet);
    try std.testing.expectEqual(@as(usize, 749_552), finalShardSize(packet.size, packet.chunk_bytes));
}

test "Lane 05 archive parts packet can use fewer larger chunks" {
    const packet = Packet{
        .size = 58_159_088,
        .chunk_bytes = 2_097_152,
        .part_count = 28,
    };

    try requireValidPacket(packet);
    try std.testing.expect(packet.part_count < 74);
    try std.testing.expectEqual(@as(usize, 1_535_984), finalShardSize(packet.size, packet.chunk_bytes));
}

test "Lane 05 archive parts packet must reject stale part counts" {
    const chunk_bytes = 2_097_152;
    const size = 58_159_088;

    try std.testing.expectEqual(@as(usize, 28), expectedPartCount(size, chunk_bytes));
    try std.testing.expect(expectedPartCount(size, chunk_bytes) != 74);
}
