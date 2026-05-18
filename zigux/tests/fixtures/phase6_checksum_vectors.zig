const std = @import("std");

pub const PerfCase = struct {
    label: []const u8,
    bytes: []const u8,
    iterations: usize,
    max_slowdown_pct: u64,
};

fn makePerfPayload(comptime len: usize, comptime seed: u8) [len]u8 {
    @setEvalBranchQuota(len * 4);
    var bytes: [len]u8 = undefined;
    for (&bytes, 0..) |*slot, index| {
        const idx: u8 = @truncate(index);
        slot.* = (seed +% (idx *% 37)) ^ (0x5a +% (idx *% 13));
    }
    return bytes;
}

pub const perf_payload_64b = makePerfPayload(64, 0x36);
pub const perf_payload_1501b = makePerfPayload(1501, 0x6c);

pub const perf_cases = [_]PerfCase{
    .{ .label = "64B", .bytes = &perf_payload_64b, .iterations = 200_000, .max_slowdown_pct = 150 },
    .{ .label = "1501B", .bytes = &perf_payload_1501b, .iterations = 12_000, .max_slowdown_pct = 150 },
};

fn perfPayloadFingerprint(bytes: []const u8) u64 {
    var acc: u64 = 0xcbf2_9ce4_8422_2325;
    for (bytes, 0..) |byte, idx| {
        acc ^= @as(u64, byte) +% (@as(u64, @intCast(idx)) << 8);
        acc *%= 0x0000_0100_0000_01b3;
    }
    return acc;
}

test "phase 6 checksum perf fixture packet stays bounded to the documented matrix" {
    const expected = [_]struct {
        label: []const u8,
        len: usize,
        iterations: usize,
        max_slowdown_pct: u64,
        fingerprint: u64,
    }{
        .{ .label = "64B", .len = 64, .iterations = 200_000, .max_slowdown_pct = 150, .fingerprint = 0xb498_d304_d0ee_aea5 },
        .{ .label = "1501B", .len = 1501, .iterations = 12_000, .max_slowdown_pct = 150, .fingerprint = 0xc457_3e1a_cc20_3461 },
    };

    try std.testing.expectEqual(expected.len, perf_cases.len);

    for (expected, 0..) |want, idx| {
        const actual = perf_cases[idx];
        try std.testing.expectEqualStrings(want.label, actual.label);
        try std.testing.expectEqual(want.len, actual.bytes.len);
        try std.testing.expectEqual(want.iterations, actual.iterations);
        try std.testing.expectEqual(want.max_slowdown_pct, actual.max_slowdown_pct);
        try std.testing.expectEqual(want.fingerprint, perfPayloadFingerprint(actual.bytes));
    }
}
