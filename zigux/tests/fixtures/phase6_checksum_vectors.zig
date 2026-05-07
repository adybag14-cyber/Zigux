const std = @import("std");

pub const ComputeCase = struct {
    name: []const u8,
    bytes: []const u8,
    expected_partial: u32,
    expected_compute: u16,
};

pub const CompositionCase = struct {
    name: []const u8,
    payload: []const u8,
    split: usize,
    expected_partial: u32,
    expected_fold: u16,
};

pub const SeededCase = struct {
    name: []const u8,
    bytes: []const u8,
    seed: u32,
    expected_partial: u32,
};

pub const PseudoHeaderCase = struct {
    name: []const u8,
    payload: []const u8,
    saddr: u32,
    daddr: u32,
    proto: u8,
    expected_compute: u16,
};

pub const CarryDisciplineCase = struct {
    name: []const u8,
    bytes: []const u8,
    seed: u32,
    expected_partial: u32,
    expected_compute: u16,
};

pub const NegateCase = struct {
    name: []const u8,
    sum: u32,
    expected_negate: u32,
    expected_add_with_negate: u32,
};

pub const FoldCase = struct {
    name: []const u8,
    sum: u32,
    expected_folded: u16,
};

pub const Add16Case = struct {
    name: []const u8,
    sum: u16,
    addend: u16,
    expected: u16,
};

pub const Sub16Case = struct {
    name: []const u8,
    sum: u16,
    addend: u16,
    expected: u16,
};

pub const PerfCase = struct {
    label: []const u8,
    bytes: []const u8,
    iterations: usize,
    max_slowdown_pct: u64,
};

const ipv4_header = [_]u8{
    0x45, 0x00, 0x00, 0x3c,
    0x1c, 0x46, 0x40, 0x00,
    0x40, 0x06, 0x00, 0x00,
    0xc0, 0xa8, 0x00, 0x01,
    0xc0, 0xa8, 0x00, 0xc7,
};

const carry_payload = [_]u8{ 0xff, 0xff, 0xff, 0xff, 0x7f };

const all_ones_odd = [_]u8{0xff};
const all_ones_even = [_]u8{ 0xff, 0xff };
const no_carry_single = [_]u8{0x04};
const no_carry_pair = [_]u8{ 0x04, 0x04 };

fn makePatternedPayload(comptime len: usize, comptime seed: u8) [len]u8 {
    @setEvalBranchQuota(len * 4);
    var bytes: [len]u8 = undefined;
    for (0..len) |i| {
        const idx: u32 = @intCast(i);
        const mixed = (idx * 37) + (idx >> 1) + seed;
        bytes[i] = @truncate((mixed ^ 0x5a) & 0xff);
    }
    return bytes;
}

const payload_64 = makePatternedPayload(64, 0x31);
const payload_1501 = makePatternedPayload(1501, 0x6d);

pub const compute_cases = [_]ComputeCase{
    .{
        .name = "empty",
        .bytes = "",
        .expected_partial = 0x0000,
        .expected_compute = 0xffff,
    },
    .{
        .name = "two-byte word",
        .bytes = "\x00\x01",
        .expected_partial = 0x0001,
        .expected_compute = 0xfffe,
    },
    .{
        .name = "ipv4 header",
        .bytes = &ipv4_header,
        .expected_partial = 0x63a2,
        .expected_compute = 0x9c5d,
    },
    .{
        .name = "odd payload",
        .bytes = "abcde",
        .expected_partial = 0x29c7,
        .expected_compute = 0xd638,
    },
    .{
        .name = "carry-heavy payload",
        .bytes = &carry_payload,
        .expected_partial = 0x7f00,
        .expected_compute = 0x80ff,
    },
};

pub const composition_cases = [_]CompositionCase{
    .{
        .name = "even split",
        .payload = "checksum fragments keep their carry",
        .split = 20,
        .expected_partial = 0x0e7b,
        .expected_fold = 0xf184,
    },
    .{
        .name = "odd split",
        .payload = "checksum fragments keep their carry",
        .split = 21,
        .expected_partial = 0x0e7b,
        .expected_fold = 0xf184,
    },
};

pub const seeded_cases = [_]SeededCase{
    .{
        .name = "odd payload with saturated seed",
        .bytes = "abcde",
        .seed = 0xffff,
        .expected_partial = 0x29c7,
    },
    .{
        .name = "carry-heavy payload with unfolded seed",
        .bytes = &carry_payload,
        .seed = 0x1fffe,
        .expected_partial = 0x7f00,
    },
    .{
        .name = "ipv4 fragment with arbitrary seed",
        .bytes = ipv4_header[0..7],
        .seed = 0xabcd,
        .expected_partial = 0x4d50,
    },
};

pub const pseudo_header_cases = [_]PseudoHeaderCase{
    .{
        .name = "udp pseudo header",
        .payload = "zigux checksum",
        .saddr = 0xc0a80001,
        .daddr = 0xc0a800c7,
        .proto = 17,
        .expected_compute = 0x7a1b,
    },
};

pub const carry_discipline_cases = [_]CarryDisciplineCase{
    .{
        .name = "all-ones odd payload with saturated seed",
        .bytes = &all_ones_odd,
        .seed = 0xffff_ffff,
        .expected_partial = 0xff00,
        .expected_compute = 0x00ff,
    },
    .{
        .name = "all-ones even payload with zero seed",
        .bytes = &all_ones_even,
        .seed = 0,
        .expected_partial = 0xffff,
        .expected_compute = 0x0000,
    },
    .{
        .name = "single-byte no-carry seed stays one step below overflow",
        .bytes = &no_carry_single,
        .seed = 0xffff_fbfb,
        .expected_partial = 0xfffb,
        .expected_compute = 0x0004,
    },
    .{
        .name = "two-byte no-carry seed stays one step below overflow",
        .bytes = &no_carry_pair,
        .seed = 0xffff_f7f7,
        .expected_partial = 0xfbfb,
        .expected_compute = 0x0404,
    },
};

pub const negate_cases = [_]NegateCase{
    .{
        .name = "zero stays zero",
        .sum = 0x0000_0000,
        .expected_negate = 0x0000_0000,
        .expected_add_with_negate = 0x0000_0000,
    },
    .{
        .name = "one negates to all ones",
        .sum = 0x0000_0001,
        .expected_negate = 0xffff_ffff,
        .expected_add_with_negate = 0x0000_0001,
    },
    .{
        .name = "all ones negates to one",
        .sum = 0xffff_ffff,
        .expected_negate = 0x0000_0001,
        .expected_add_with_negate = 0x0000_0001,
    },
    .{
        .name = "mixed payload preserves ones complement carry",
        .sum = 0xdead_bef0,
        .expected_negate = 0x2152_4110,
        .expected_add_with_negate = 0x0000_0001,
    },
};

pub const fold_cases = [_]FoldCase{
    .{ .name = "zero", .sum = 0x0000_0000, .expected_folded = 0x0000 },
    .{ .name = "single carry into the low word", .sum = 0x0001_0000, .expected_folded = 0x0001 },
    .{ .name = "double carry collapse", .sum = 0xffff_0001, .expected_folded = 0x0001 },
    .{ .name = "all ones saturates to sixteen bits", .sum = 0xffff_ffff, .expected_folded = 0xffff },
    .{ .name = "mixed words preserve the remaining payload", .sum = 0x1234_5678, .expected_folded = 0x68ac },
};

pub const add16_cases = [_]Add16Case{
    .{ .name = "saturated plus one wraps with carry", .sum = 0xffff, .addend = 0x0001, .expected = 0x0001 },
    .{ .name = "saturated plus zero stays saturated", .sum = 0xffff, .addend = 0x0000, .expected = 0xffff },
    .{ .name = "saturated plus saturated preserves ones complement", .sum = 0xffff, .addend = 0xffff, .expected = 0xffff },
};

pub const sub16_cases = [_]Sub16Case{
    .{ .name = "zero minus one borrows across ones complement", .sum = 0x0000, .addend = 0x0001, .expected = 0xfffe },
    .{ .name = "subtracting a prior addend recovers the original word", .sum = 0xbe01, .addend = 0xabcd, .expected = 0x1234 },
};

pub const perf_cases = [_]PerfCase{
    .{
        .label = "64B",
        .bytes = &payload_64,
        .iterations = 200_000,
        .max_slowdown_pct = 150,
    },
    .{
        .label = "1501B",
        .bytes = &payload_1501,
        .iterations = 12_000,
        .max_slowdown_pct = 150,
    },
};

test "phase 6 checksum perf fixture packet stays bounded to the documented matrix" {
    const expected = [_]struct {
        label: []const u8,
        len: usize,
        iterations: usize,
        max_slowdown_pct: u64,
    }{
        .{ .label = "64B", .len = 64, .iterations = 200_000, .max_slowdown_pct = 150 },
        .{ .label = "1501B", .len = 1501, .iterations = 12_000, .max_slowdown_pct = 150 },
    };

    try std.testing.expectEqual(expected.len, perf_cases.len);

    for (expected, 0..) |want, idx| {
        const actual = perf_cases[idx];
        try std.testing.expectEqualStrings(want.label, actual.label);
        try std.testing.expectEqual(want.len, actual.bytes.len);
        try std.testing.expectEqual(want.iterations, actual.iterations);
        try std.testing.expectEqual(want.max_slowdown_pct, actual.max_slowdown_pct);
    }

    for (perf_cases, 0..) |case, idx| {
        try std.testing.expect(case.bytes.len > 0);
        try std.testing.expect(case.iterations > 0);
        try std.testing.expect(case.max_slowdown_pct > 0);

        for (perf_cases[idx + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, case.label, other.label));
        }
    }
}
