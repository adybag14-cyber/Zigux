const std = @import("std");

const default_archive_size: usize = 58_159_088;
const default_chunk_bytes: usize = 786_432;
const larger_chunk_bytes: usize = 2_097_152;

fn partCount(size: usize, chunk_bytes: usize) usize {
    std.debug.assert(size > 0);
    std.debug.assert(chunk_bytes > 0);
    return (size + chunk_bytes - 1) / chunk_bytes;
}

fn shardName(buf: []u8, index: usize) ![]const u8 {
    return std.fmt.bufPrint(buf, "part-{d:0>3}.b64", .{index});
}

fn expectShardName(index: usize, expected: []const u8) !void {
    var buf: [32]u8 = undefined;
    try std.testing.expectEqualStrings(expected, try shardName(&buf, index));
}

test "default archive packet keeps the shipped 74 shard name boundary" {
    const count = partCount(default_archive_size, default_chunk_bytes);
    try std.testing.expectEqual(@as(usize, 74), count);
    try expectShardName(0, "part-000.b64");
    try expectShardName(1, "part-001.b64");
    try expectShardName(count - 2, "part-072.b64");
    try expectShardName(count - 1, "part-073.b64");
}

test "larger chunk packet keeps sequential names through the final shard" {
    const count = partCount(default_archive_size, larger_chunk_bytes);
    try std.testing.expectEqual(@as(usize, 28), count);
    try expectShardName(0, "part-000.b64");
    try expectShardName(9, "part-009.b64");
    try expectShardName(10, "part-010.b64");
    try expectShardName(count - 1, "part-027.b64");
}

test "three digit padding protects lexical order for current packet sizes" {
    var previous_buf: [32]u8 = undefined;
    var current_buf: [32]u8 = undefined;
    var previous = try shardName(&previous_buf, 0);

    for (1..partCount(default_archive_size, default_chunk_bytes)) |index| {
        const current = try shardName(&current_buf, index);
        try std.testing.expect(std.mem.lessThan(u8, previous, current));
        @memcpy(previous_buf[0..current.len], current);
        previous = previous_buf[0..current.len];
    }
}

test "unpadded and wrongly suffixed shard names remain outside the contract" {
    var buf: [32]u8 = undefined;
    const first = try shardName(&buf, 0);
    try std.testing.expect(!std.mem.eql(u8, first, "part-0.b64"));
    try std.testing.expect(!std.mem.eql(u8, first, "part-000.txt"));

    const tenth = try shardName(&buf, 10);
    try std.testing.expect(!std.mem.eql(u8, tenth, "part-10.b64"));
    try std.testing.expect(std.mem.startsWith(u8, tenth, "part-"));
    try std.testing.expect(std.mem.endsWith(u8, tenth, ".b64"));
}
