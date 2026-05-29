const std = @import("std");

const PacketShape = struct {
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

fn decodedSizeBeforeFinalShard(packet: PacketShape) usize {
    return (packet.part_count - 1) * packet.chunk_bytes;
}

fn requireValidFinalShard(packet: PacketShape, expected_final_size: usize) !void {
    try std.testing.expect(packet.size > 0);
    try std.testing.expect(packet.chunk_bytes > 0);
    try std.testing.expectEqual(expectedPartCount(packet.size, packet.chunk_bytes), packet.part_count);
    try std.testing.expect(packet.part_count > 0);
    try std.testing.expectEqual(expected_final_size, finalShardSize(packet.size, packet.chunk_bytes));
    try std.testing.expect(finalShardSize(packet.size, packet.chunk_bytes) > 0);
    try std.testing.expect(finalShardSize(packet.size, packet.chunk_bytes) <= packet.chunk_bytes);
    try std.testing.expectEqual(packet.size, decodedSizeBeforeFinalShard(packet) + finalShardSize(packet.size, packet.chunk_bytes));
}

test "Lane 05 archive parts default packet keeps a non-empty final shard" {
    const packet = PacketShape{
        .size = 58_159_088,
        .chunk_bytes = 786_432,
        .part_count = 74,
    };

    try requireValidFinalShard(packet, 749_552);
    try std.testing.expect(packet.chunk_bytes - finalShardSize(packet.size, packet.chunk_bytes) < packet.chunk_bytes);
}

test "Lane 05 archive parts larger packet keeps exact decoded-size accounting" {
    const packet = PacketShape{
        .size = 58_159_088,
        .chunk_bytes = 1_048_576,
        .part_count = 56,
    };

    try requireValidFinalShard(packet, 487_408);
    try std.testing.expect(decodedSizeBeforeFinalShard(packet) < packet.size);
}

test "Lane 05 archive parts final shard is full only on exact chunk boundaries" {
    const exact = PacketShape{
        .size = 4_194_304,
        .chunk_bytes = 1_048_576,
        .part_count = 4,
    };

    try requireValidFinalShard(exact, exact.chunk_bytes);
    try std.testing.expectEqual(@as(usize, 0), exact.size % exact.chunk_bytes);
}

test "Lane 05 archive parts stale final-shard math would change the decoded total" {
    const packet = PacketShape{
        .size = 58_159_088,
        .chunk_bytes = 1_048_576,
        .part_count = 56,
    };
    const stale_final_size = packet.chunk_bytes;

    try std.testing.expect(stale_final_size != finalShardSize(packet.size, packet.chunk_bytes));
    try std.testing.expect(decodedSizeBeforeFinalShard(packet) + stale_final_size != packet.size);
}
