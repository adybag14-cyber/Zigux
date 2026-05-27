const std = @import("std");

pub const ComputeCase = struct {
    label: []const u8,
    payload: []const u8,
};

pub const SeededCase = struct {
    label: []const u8,
    prefix: []const u8,
    suffix: []const u8,
    seed: u32,
};

pub const PerfCase = struct {
    label: []const u8,
    bytes: []const u8,
    iterations: usize,
    max_slowdown_pct: u64,
};

pub const FastPathCase = struct {
    label: []const u8,
    header: []const u8,
    iterations: usize,
    max_slowdown_pct: u64,
};

pub const Carry16Case = struct {
    label: []const u8,
    sum: u16,
    addend: u16,
    expected_add: u16,
    expected_sub: u16,
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

pub const compute_cases = [_]ComputeCase{
    .{ .label = "empty", .payload = "" },
    .{ .label = "single-byte", .payload = "f" },
    .{ .label = "two-byte", .payload = "fo" },
    .{ .label = "three-byte", .payload = "foo" },
    .{ .label = "phase6", .payload = "phase6" },
};

pub const seeded_cases = [_]SeededCase{
    .{ .label = "seed-zero", .prefix = "ph", .suffix = "ase6", .seed = 0x0000_0000 },
    .{ .label = "seed-carry", .prefix = "netw", .suffix = "orkstack", .seed = 0x0001_ffff },
    .{ .label = "seed-wrap", .prefix = "carryf", .suffix = "old", .seed = 0xffff_ff10 },
};

pub const carry16_cases = [_]Carry16Case{
    .{ .label = "zero-plus-zero", .sum = 0x0000, .addend = 0x0000, .expected_add = 0x0000, .expected_sub = 0xffff },
    .{ .label = "saturated-plus-one", .sum = 0xffff, .addend = 0x0001, .expected_add = 0x0001, .expected_sub = 0xfffe },
    .{ .label = "halfword-wrap", .sum = 0x7fff, .addend = 0x8000, .expected_add = 0xffff, .expected_sub = 0xfffe },
    .{ .label = "near-wrap-plus-three", .sum = 0xfffe, .addend = 0x0003, .expected_add = 0x0002, .expected_sub = 0xfffb },
};

pub const ip_fast_csum_ipv4_20b = [_]u8{
    0x45, 0x00, 0x00, 0x3c,
    0x1c, 0x46, 0x40, 0x00,
    0x40, 0x06, 0x00, 0x00,
    0xc0, 0xa8, 0x00, 0x01,
    0xc0, 0xa8, 0x00, 0xc7,
};

pub const ip_fast_csum_ipv4_20b_updated = [_]u8{
    0x45, 0x00, 0x00, 0x40,
    0x1c, 0x46, 0x40, 0x00,
    0x3f, 0x11, 0x00, 0x00,
    0xc0, 0xa8, 0x00, 0x02,
    0xc0, 0xa8, 0x00, 0xc7,
};

pub const ip_fast_csum_ipv4_24b = [_]u8{
    0x46, 0x00, 0x00, 0x30,
    0x12, 0x34, 0x20, 0x00,
    0x40, 0x11, 0x00, 0x00,
    0xc0, 0xa8, 0x01, 0x01,
    0xc0, 0xa8, 0x01, 0x02,
    0x01, 0x01, 0x00, 0x00,
};

pub const ip_fast_csum_ipv4_60b = [_]u8{
    0x4f, 0x00, 0x00, 0x3c,
    0xbe, 0xef, 0x40, 0x00,
    0x40, 0x11, 0x00, 0x00,
    0xc0, 0x00, 0x02, 0x01,
    0xc6, 0x33, 0x64, 0x07,
    0x01, 0x01, 0x94, 0x04,
    0xde, 0xad, 0xbe, 0xef,
    0xca, 0xfe, 0xba, 0xbe,
    0x11, 0x22, 0x33, 0x44,
    0x55, 0x66, 0x77, 0x88,
    0x99, 0xaa, 0xbb, 0xcc,
    0xdd, 0xee, 0xf0, 0x0d,
    0x10, 0x20, 0x30, 0x40,
    0x50, 0x60, 0x70, 0x80,
    0x90, 0xa0, 0xb0, 0xc0,
};

pub const fast_path_cases = [_]FastPathCase{
    .{ .label = "IPV4_20B", .header = &ip_fast_csum_ipv4_20b, .iterations = 600_000, .max_slowdown_pct = 100 },
    .{ .label = "IPV4_20B_UPDATED", .header = &ip_fast_csum_ipv4_20b_updated, .iterations = 600_000, .max_slowdown_pct = 100 },
    .{ .label = "IPV4_24B", .header = &ip_fast_csum_ipv4_24b, .iterations = 500_000, .max_slowdown_pct = 100 },
    .{ .label = "IPV4_60B", .header = &ip_fast_csum_ipv4_60b, .iterations = 250_000, .max_slowdown_pct = 100 },
};

fn perfPayloadFingerprint(bytes: []const u8) u64 {
    var acc: u64 = 0xcbf2_9ce4_8422_2325;
    for (bytes, 0..) |byte, idx| {
        acc ^= @as(u64, byte) +% (@as(u64, @intCast(idx)) << 8);
        acc *%= 0x0000_0100_0000_01b3;
    }
    return acc;
}

fn validateFastPathHeader(header: []const u8) !void {
    try std.testing.expect(header.len >= 20);
    try std.testing.expectEqual(@as(usize, 0), header.len & 3);
    try std.testing.expectEqual(@as(u8, 4), header[0] >> 4);
    try std.testing.expectEqual(header.len, @as(usize, (header[0] & 0x0f) * 4));
}

test "phase 6 checksum fixture packet stays bounded to the documented matrices" {
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
    const compute_expected = [_]ComputeCase{
        .{ .label = "empty", .payload = "" },
        .{ .label = "single-byte", .payload = "f" },
        .{ .label = "two-byte", .payload = "fo" },
        .{ .label = "three-byte", .payload = "foo" },
        .{ .label = "phase6", .payload = "phase6" },
    };
    const seeded_expected = [_]SeededCase{
        .{ .label = "seed-zero", .prefix = "ph", .suffix = "ase6", .seed = 0x0000_0000 },
        .{ .label = "seed-carry", .prefix = "netw", .suffix = "orkstack", .seed = 0x0001_ffff },
        .{ .label = "seed-wrap", .prefix = "carryf", .suffix = "old", .seed = 0xffff_ff10 },
    };
    const carry16_expected = [_]struct {
        label: []const u8,
        sum: u16,
        addend: u16,
        expected_add: u16,
        expected_sub: u16,
    }{
        .{ .label = "zero-plus-zero", .sum = 0x0000, .addend = 0x0000, .expected_add = 0x0000, .expected_sub = 0xffff },
        .{ .label = "saturated-plus-one", .sum = 0xffff, .addend = 0x0001, .expected_add = 0x0001, .expected_sub = 0xfffe },
        .{ .label = "halfword-wrap", .sum = 0x7fff, .addend = 0x8000, .expected_add = 0xffff, .expected_sub = 0xfffe },
        .{ .label = "near-wrap-plus-three", .sum = 0xfffe, .addend = 0x0003, .expected_add = 0x0002, .expected_sub = 0xfffb },
    };
    const fast_path_expected = [_]struct {
        label: []const u8,
        len: usize,
        iterations: usize,
        max_slowdown_pct: u64,
        fingerprint: u64,
    }{
        .{ .label = "IPV4_20B", .len = 20, .iterations = 600_000, .max_slowdown_pct = 100, .fingerprint = 0x0682_5249_d059_7d1a },
        .{ .label = "IPV4_20B_UPDATED", .len = 20, .iterations = 600_000, .max_slowdown_pct = 100, .fingerprint = 0x5f42_250b_82c8_2bed },
        .{ .label = "IPV4_24B", .len = 24, .iterations = 500_000, .max_slowdown_pct = 100, .fingerprint = 0x5eb5_c436_a23c_5f85 },
        .{ .label = "IPV4_60B", .len = 60, .iterations = 250_000, .max_slowdown_pct = 100, .fingerprint = 0xdf35_6721_260f_0ddd },
    };

    try std.testing.expectEqual(expected.len, perf_cases.len);
    try std.testing.expectEqual(compute_expected.len, compute_cases.len);
    try std.testing.expectEqual(seeded_expected.len, seeded_cases.len);
    try std.testing.expectEqual(carry16_expected.len, carry16_cases.len);
    try std.testing.expectEqual(fast_path_expected.len, fast_path_cases.len);

    for (expected, 0..) |want, idx| {
        const actual = perf_cases[idx];
        try std.testing.expectEqualStrings(want.label, actual.label);
        try std.testing.expectEqual(want.len, actual.bytes.len);
        try std.testing.expectEqual(want.iterations, actual.iterations);
        try std.testing.expectEqual(want.max_slowdown_pct, actual.max_slowdown_pct);
        try std.testing.expectEqual(want.fingerprint, perfPayloadFingerprint(actual.bytes));
    }

    for (compute_expected, 0..) |want, idx| {
        const actual = compute_cases[idx];
        try std.testing.expectEqualStrings(want.label, actual.label);
        try std.testing.expectEqualSlices(u8, want.payload, actual.payload);
    }

    for (seeded_expected, 0..) |want, idx| {
        const actual = seeded_cases[idx];
        try std.testing.expectEqualStrings(want.label, actual.label);
        try std.testing.expectEqualSlices(u8, want.prefix, actual.prefix);
        try std.testing.expectEqualSlices(u8, want.suffix, actual.suffix);
        try std.testing.expectEqual(want.seed, actual.seed);
    }

    for (carry16_expected, 0..) |want, idx| {
        const actual = carry16_cases[idx];
        try std.testing.expectEqualStrings(want.label, actual.label);
        try std.testing.expectEqual(want.sum, actual.sum);
        try std.testing.expectEqual(want.addend, actual.addend);
        try std.testing.expectEqual(want.expected_add, actual.expected_add);
        try std.testing.expectEqual(want.expected_sub, actual.expected_sub);
    }

    for (fast_path_expected, 0..) |want, idx| {
        const actual = fast_path_cases[idx];
        try std.testing.expectEqualStrings(want.label, actual.label);
        try std.testing.expectEqual(want.len, actual.header.len);
        try std.testing.expectEqual(want.iterations, actual.iterations);
        try std.testing.expectEqual(want.max_slowdown_pct, actual.max_slowdown_pct);
        try std.testing.expectEqual(want.fingerprint, perfPayloadFingerprint(actual.header));
        try validateFastPathHeader(actual.header);
    }
}
