const std = @import("std");

pub const ComputeCase = struct {
    name: []const u8,
    bytes: []const u8,
    expected_sum: u16,
};

pub const SeededCase = struct {
    name: []const u8,
    bytes: []const u8,
    seed: u32,
    expected_sum: u32,
};

pub const CompositionCase = struct {
    name: []const u8,
    payload: []const u8,
    split: usize,
    expected_sum: u32,
};

pub const PseudoHeaderCase = struct {
    name: []const u8,
    payload: []const u8,
    saddr: u32,
    daddr: u32,
    proto: u8,
    expected_sum: u32,
};

pub const Ipv6PseudoHeaderCase = struct {
    name: []const u8,
    payload: []const u8,
    saddr: [16]u8,
    daddr: [16]u8,
    declared_len: u32,
    proto: u8,
    expected_sum: u32,
};

pub const CarryDisciplineCase = struct {
    name: []const u8,
    bytes: []const u8,
    seed: u32,
    expected_fold: u16,
};

pub const PerfCase = struct {
    label: []const u8,
    payload: []const u8,
    iterations: usize,
    max_slowdown_pct: u64,
};

const two_byte_word = [_]u8{ 0x00, 0x01 };
const ipv4_header = [_]u8{
    0x45, 0x00, 0x00, 0x3c,
    0x1c, 0x46, 0x40, 0x00,
    0x40, 0x06, 0x00, 0x00,
    0xc0, 0xa8, 0x00, 0x01,
    0xc0, 0xa8, 0x00, 0xc7,
};
const odd_payload = [_]u8{ 'a', 'b', 'c', 'd', 'e' };
const carry_payload = [_]u8{ 0xff, 0xff, 0xff, 0xff, 0x7f };
const carry_phrase = "checksum fragments keep their carry";
const udp_payload = "zigux checksum";
const udp_v6_payload = "zigux v6 checksum";
const tcp_v6_payload = [_]u8{ 0xff, 0xff, 0x00, 0x01, 0xab, 0xcd, 0x12, 0x34 };
const all_ones_odd = [_]u8{0xff};
const all_ones_even = [_]u8{ 0xff, 0xff };
const no_carry_single = [_]u8{0x04};
const no_carry_pair = [_]u8{ 0x04, 0x04 };
const udp_v6_saddr = [_]u8{
    0x20, 0x01, 0x0d, 0xb8, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
};
const udp_v6_daddr = [_]u8{
    0x20, 0x01, 0x0d, 0xb8, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02,
};
const tcp_v6_saddr = [_]u8{
    0xfd, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10,
};
const tcp_v6_daddr = [_]u8{
    0xfd, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x20,
};
const icmp_v6_saddr = [_]u8{
    0xfd, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x12, 0x34, 0x56, 0x78, 0x00, 0x00, 0x00, 0x01,
};
const icmp_v6_daddr = [_]u8{
    0xfd, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x87, 0x65, 0x43, 0x21, 0x00, 0x00, 0x00, 0x02,
};
const v6_len_payload = "v6len";

pub const compute_cases = [_]ComputeCase{
    .{ .name = "empty", .bytes = "", .expected_sum = 0xffff },
    .{ .name = "two-byte word", .bytes = two_byte_word[0..], .expected_sum = 0xfffe },
    .{ .name = "ipv4 header", .bytes = ipv4_header[0..], .expected_sum = 0x9c5d },
    .{ .name = "odd payload", .bytes = odd_payload[0..], .expected_sum = 0xd638 },
    .{ .name = "carry-heavy payload", .bytes = carry_payload[0..], .expected_sum = 0x80ff },
};

pub const seeded_cases = [_]SeededCase{
    .{ .name = "odd payload with saturated seed", .bytes = odd_payload[0..], .seed = 0xffff, .expected_sum = 0x000029c7 },
    .{ .name = "carry-heavy payload with unfolded seed", .bytes = carry_payload[0..], .seed = 0x1fffe, .expected_sum = 0x00007f00 },
    .{ .name = "ipv4 fragment with arbitrary seed", .bytes = ipv4_header[0..7], .seed = 0xabcd, .expected_sum = 0x00004d50 },
};

pub const composition_cases = [_]CompositionCase{
    .{ .name = "even split", .payload = carry_phrase, .split = 20, .expected_sum = 0x00000e7b },
    .{ .name = "odd split", .payload = carry_phrase, .split = 21, .expected_sum = 0x00000e7b },
};

pub const pseudo_header_cases = [_]PseudoHeaderCase{
    .{
        .name = "udp pseudo header",
        .payload = udp_payload,
        .saddr = 0xc0a80001,
        .daddr = 0xc0a800c7,
        .proto = 17,
        .expected_sum = 0x000085e4,
    },
};

pub const ipv6_pseudo_header_cases = [_]Ipv6PseudoHeaderCase{
    .{
        .name = "udp doc payload odd",
        .payload = udp_v6_payload,
        .saddr = udp_v6_saddr,
        .daddr = udp_v6_daddr,
        .declared_len = udp_v6_payload.len,
        .proto = 17,
        .expected_sum = 0x0000f876,
    },
    .{
        .name = "tcp carry payload even",
        .payload = tcp_v6_payload[0..],
        .saddr = tcp_v6_saddr,
        .daddr = tcp_v6_daddr,
        .declared_len = tcp_v6_payload.len,
        .proto = 6,
        .expected_sum = 0x0000b842,
    },
    .{
        .name = "icmpv6 preserves upper declared length bits",
        .payload = v6_len_payload,
        .saddr = icmp_v6_saddr,
        .daddr = icmp_v6_daddr,
        .declared_len = 0x00010001,
        .proto = 58,
        .expected_sum = 0x00007e10,
    },
};

pub const carry_discipline_cases = [_]CarryDisciplineCase{
    .{ .name = "all-ones odd payload with saturated seed", .bytes = all_ones_odd[0..], .seed = 0xffffffff, .expected_fold = 0x00ff },
    .{ .name = "all-ones even payload with zero seed", .bytes = all_ones_even[0..], .seed = 0, .expected_fold = 0x0000 },
    .{ .name = "single-byte no-carry seed stays one step below overflow", .bytes = no_carry_single[0..], .seed = 0xfffffbfb, .expected_fold = 0x0004 },
    .{ .name = "two-byte no-carry seed stays one step below overflow", .bytes = no_carry_pair[0..], .seed = 0xfffff7f7, .expected_fold = 0x0404 },
};

pub const perf_payload_64 = buildPayload(64, 17, 3);
pub const perf_payload_1501 = buildPayload(1501, 73, 19);

pub const perf_cases = [_]PerfCase{
    .{ .label = "64B", .payload = perf_payload_64[0..], .iterations = 200000, .max_slowdown_pct = 150 },
    .{ .label = "1501B", .payload = perf_payload_1501[0..], .iterations = 12000, .max_slowdown_pct = 150 },
};

fn buildPayload(comptime len: usize, comptime mul: usize, comptime add: usize) [len]u8 {
    @setEvalBranchQuota(len * 4);
    var payload: [len]u8 = undefined;
    for (&payload, 0..) |*byte, idx| {
        byte.* = @intCast((idx * mul + add) % 256);
    }
    return payload;
}

test "phase6 checksum fixtures keep the documented corpus shape" {
    try std.testing.expectEqual(@as(usize, 5), compute_cases.len);
    try std.testing.expectEqual(@as(usize, 3), seeded_cases.len);
    try std.testing.expectEqual(@as(usize, 2), composition_cases.len);
    try std.testing.expectEqual(@as(usize, 1), pseudo_header_cases.len);
    try std.testing.expectEqual(@as(usize, 3), ipv6_pseudo_header_cases.len);
    try std.testing.expectEqual(@as(usize, 4), carry_discipline_cases.len);
    try std.testing.expectEqual(@as(usize, 2), perf_cases.len);
}
