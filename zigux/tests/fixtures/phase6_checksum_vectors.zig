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

pub const KunitRandomPrefixCase = struct {
    name: []const u8,
    bytes: []const u8,
    seed: u32,
    expected_partial: u32,
    expected_compute: u16,
};

pub const PerfCase = struct {
    label: []const u8,
    len: usize,
    reps: usize,
    seed: u32,
    max_slowdown_pct: u16,
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
const kunit_random_prefix_source = [_]u8{
    0xac, 0xd7, 0x76, 0x69, 0x6e, 0xf2, 0x93, 0x2c,
    0x1f, 0xe0, 0xde, 0x86, 0x8f, 0x54, 0x33, 0x90,
    0x95, 0xbf, 0xff, 0xb9, 0xea, 0x62, 0x6e, 0xb5,
    0xd3, 0x4f, 0xf5, 0x60, 0x50, 0x5c, 0xc7, 0xfa,
    0x6d, 0x1a, 0xc7, 0xf0, 0xd2, 0x2c, 0x12, 0x3d,
    0x88, 0xe3, 0x14, 0x21, 0xb1, 0x5e, 0x45, 0x31,
    0xa2, 0x85, 0x36, 0x76, 0xba, 0xd8, 0xad, 0xbb,
    0x9e, 0x49, 0x8f, 0xf7, 0xce, 0xea, 0xef, 0xca,
};

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

pub const kunit_random_prefix_cases = [_]KunitRandomPrefixCase{
    .{
        .name = "kunit random prefix len 0",
        .bytes = kunit_random_prefix_source[0..0],
        .seed = 0x8402ab7a,
        .expected_partial = 0x2f7d,
        .expected_compute = 0xd082,
    },
    .{
        .name = "kunit random prefix len 1",
        .bytes = kunit_random_prefix_source[0..1],
        .seed = 0x8402ab7a,
        .expected_partial = 0xdb7d,
        .expected_compute = 0x2482,
    },
    .{
        .name = "kunit random prefix len 2",
        .bytes = kunit_random_prefix_source[0..2],
        .seed = 0x8402ab7a,
        .expected_partial = 0xdc54,
        .expected_compute = 0x23ab,
    },
    .{
        .name = "kunit random prefix len 5",
        .bytes = kunit_random_prefix_source[0..5],
        .seed = 0x8402ab7a,
        .expected_partial = 0xc0be,
        .expected_compute = 0x3f41,
    },
    .{
        .name = "kunit random prefix len 31",
        .bytes = kunit_random_prefix_source[0..31],
        .seed = 0x8402ab7a,
        .expected_partial = 0xe4c8,
        .expected_compute = 0x1b37,
    },
    .{
        .name = "kunit random prefix len 64",
        .bytes = kunit_random_prefix_source[0..64],
        .seed = 0x8402ab7a,
        .expected_partial = 0xc153,
        .expected_compute = 0x3eac,
    },
};

pub const perf_cases = [_]PerfCase{
    .{ .label = "64", .len = 64, .reps = 20_000, .seed = 0, .max_slowdown_pct = 150 },
    .{ .label = "1501", .len = 1501, .reps = 4_000, .seed = 0x1234_5678, .max_slowdown_pct = 150 },
};

pub fn fillPerfPayload(buffer: []u8) void {
    var state: u32 = 0x51_67_2026;

    for (buffer, 0..) |*byte, idx| {
        state = state *% 1664525 +% 1013904223 +% @as(u32, @intCast(idx));
        byte.* = @truncate((state >> 16) ^ state);
    }
}
