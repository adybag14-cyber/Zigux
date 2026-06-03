const std = @import("std");
const hweight = @import("hweight");

const iterations_hweight: u64 = 100_000;

const HweightBenchReplay = struct {
    w8: u32,
    w16: u32,
    w32: u32,
    w64: u64,
    long: usize,
    per_iteration_checksum: u64,
};

fn runHweightBenchReplay() HweightBenchReplay {
    const w8 = hweight.swHweight8(0xf0);
    const w16 = hweight.swHweight16(0xf0f0);
    const w32 = hweight.swHweight32(0xf0f0_f0f0);
    const w64 = hweight.swHweight64(0xf0f0_f0f0_f0f0_f0f0);
    const long = hweight.hweightLong(0xf0f0);

    return .{
        .w8 = w8,
        .w16 = w16,
        .w32 = w32,
        .w64 = w64,
        .long = long,
        .per_iteration_checksum = @as(u64, w8) +
            @as(u64, w16) +
            @as(u64, w32) +
            w64 +
            @as(u64, @intCast(long)),
    };
}

fn runHweightBenchChecksum() u64 {
    var checksum: u64 = 0;
    var idx: u64 = 0;
    while (idx < iterations_hweight) : (idx += 1) {
        checksum +%= runHweightBenchReplay().per_iteration_checksum;
    }
    return checksum;
}

test "phase1 hweight bench replay pins width contributions" {
    const replay = runHweightBenchReplay();

    try std.testing.expectEqual(@as(u32, 4), replay.w8);
    try std.testing.expectEqual(@as(u32, 8), replay.w16);
    try std.testing.expectEqual(@as(u32, 16), replay.w32);
    try std.testing.expectEqual(@as(u64, 32), replay.w64);
    try std.testing.expectEqual(@as(usize, 8), replay.long);
    try std.testing.expectEqual(@as(u64, 68), replay.per_iteration_checksum);
}

test "phase1 hweight bench replay matches the bench checksum packet" {
    try std.testing.expectEqual(@as(u64, 6_800_000), runHweightBenchChecksum());
}
