const std = @import("std");
const hweight = @import("hweight");

const iterations_hweight = 100_000;

const HweightReplay = struct {
    checksum: u64,
    first_counts: [4]u32,
    last_count: u32,
};

fn runHweightReplay() HweightReplay {
    var checksum: u64 = 0;
    var first_counts: [4]u32 = undefined;
    var last_count: u32 = 0;
    var idx: usize = 0;
    while (idx < iterations_hweight) : (idx += 1) {
        const value: u32 = @truncate(0xf0f0_a5a5 ^ @as(u32, @intCast(idx)));
        const count = hweight.swHweight32(value);
        checksum +%= count;
        if (idx < first_counts.len) {
            first_counts[idx] = count;
        }
        if (idx + 1 == iterations_hweight) {
            last_count = count;
        }
    }
    return .{
        .checksum = checksum,
        .first_counts = first_counts,
        .last_count = last_count,
    };
}

test "phase1 hweight bench replay keeps the rolling popcount witness explicit" {
    const replay = runHweightReplay();
    try std.testing.expectEqual([4]u32{ 16, 15, 17, 16 }, replay.first_counts);
    try std.testing.expectEqual(@as(u32, 16), replay.last_count);
    try std.testing.expectEqual(@as(u64, 1_648_432), replay.checksum);
}

test "phase1 hweight bench replay matches the parked bench checksum packet" {
    var checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_hweight) : (idx += 1) {
        const value: u32 = @truncate(0xf0f0_a5a5 ^ @as(u32, @intCast(idx)));
        checksum +%= hweight.swHweight32(value);
    }
    try std.testing.expectEqual(@as(u64, 1_648_432), checksum);
}
