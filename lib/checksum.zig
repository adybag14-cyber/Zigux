// SPDX-License-Identifier: GPL-2.0-or-later
const std = @import("std");

pub fn add(sum: u32, addend: u32) u32 {
    const result = sum +% addend;
    return result + @intFromBool(result < addend);
}

pub fn sub(sum: u32, addend: u32) u32 {
    return add(sum, ~addend);
}

pub fn shift(sum: u32, offset: usize) u32 {
    if ((offset & 1) != 0) {
        return std.math.rotr(u32, sum, 8);
    }
    return sum;
}

pub fn blockAdd(sum: u32, other: u32, offset: usize) u32 {
    return add(sum, shift(other, offset));
}

pub fn blockSub(sum: u32, other: u32, offset: usize) u32 {
    return blockAdd(sum, ~other, offset);
}

pub fn negate(sum: u32) u32 {
    return 0 -% sum;
}

pub fn replace(sum: u32, old: u32, new: u32) u32 {
    return add(sub(sum, old), new);
}

pub fn replaceByDiff(sum: u16, diff: u32) u16 {
    return fold(add(diff, ~unfold(sum)));
}

pub fn replace2(sum: u16, old: u16, new: u16) u16 {
    return ~add16(sub16(~sum, old), new);
}

pub fn replace4(sum: u16, from: u32, to: u32) u16 {
    const adjusted = sub(~unfold(sum), from);
    return fold(add(adjusted, to));
}

pub fn from32to16(sum: u32) u16 {
    return @intCast(normalize(sum));
}

pub fn fold(sum: u32) u16 {
    return ~from32to16(sum);
}

pub fn tcpUdpNofold(sum: u32, saddr: u32, daddr: u32, len: u16, proto: u8) u32 {
    var result = normalize(sum);
    result = add(result, saddr >> 16);
    result = add(result, saddr & 0xffff);
    result = add(result, daddr >> 16);
    result = add(result, daddr & 0xffff);
    result = add(result, proto);
    result = add(result, len);
    return normalize(result);
}

pub fn tcpUdpMagic(sum: u32, saddr: u32, daddr: u32, len: u16, proto: u8) u16 {
    return fold(tcpUdpNofold(sum, saddr, daddr, len, proto));
}

pub fn tcpUdpV6Nofold(sum: u32, saddr: *const [16]u8, daddr: *const [16]u8, len: u32, proto: u8) u32 {
    var result = normalize(sum);

    for (0..4) |index| {
        const offset = index * 4;
        result = add(result, readBigEndianU32(saddr[offset .. offset + 4]));
        result = add(result, readBigEndianU32(daddr[offset .. offset + 4]));
    }

    result = add(result, len >> 16);
    result = add(result, len & 0xffff);
    result = add(result, proto);
    return normalize(result);
}

pub fn tcpUdpV6Magic(sum: u32, saddr: *const [16]u8, daddr: *const [16]u8, len: u32, proto: u8) u16 {
    return fold(tcpUdpV6Nofold(sum, saddr, daddr, len, proto));
}

pub fn partial(bytes: []const u8, seed: u32) u32 {
    var sum: u64 = normalize(seed);
    var index: usize = 0;

    while (index + 1 < bytes.len) : (index += 2) {
        sum += (@as(u64, bytes[index]) << 8) | bytes[index + 1];
    }

    if (index < bytes.len) {
        sum += @as(u64, bytes[index]) << 8;
    }

    return normalizeWide(sum);
}

pub fn compute(bytes: []const u8) u16 {
    return fold(partial(bytes, 0));
}

pub fn ipComputeCsum(bytes: []const u8) u16 {
    return compute(bytes);
}

pub fn ipFastCsum(header: []const u8) u16 {
    std.debug.assert((header.len & 3) == 0);
    var sum: u64 = 0;
    var index: usize = 0;
    while (index < header.len) : (index += 4) {
        sum += readBigEndianU32(header[index .. index + 4]);
    }
    return fold(normalizeWide(sum));
}

fn normalize(sum: u32) u32 {
    var value = sum;
    while ((value >> 16) != 0) {
        value = (value & 0xffff) + (value >> 16);
    }
    return value;
}

fn normalizeWide(sum: u64) u32 {
    var value = sum;
    while ((value >> 16) != 0) {
        value = (value & 0xffff) + (value >> 16);
    }
    return @intCast(value);
}

pub fn unfold(sum: u16) u32 {
    return sum;
}

pub fn add16(sum: u16, addend: u16) u16 {
    const result = sum +% addend;
    return result +% @as(u16, @intFromBool(result < addend));
}

pub fn sub16(sum: u16, addend: u16) u16 {
    return add16(sum, ~addend);
}

fn readBigEndianU32(bytes: []const u8) u32 {
    const pair: *const [4]u8 = @ptrCast(bytes[0..4]);
    return std.mem.readInt(u32, pair, .big);
}

test "negate wraps around unfolded checksum sums" {
    try std.testing.expectEqual(@as(u32, 0), negate(0));
    try std.testing.expectEqual(@as(u32, 0xffff_ffff), negate(1));
    try std.testing.expectEqual(@as(u32, 1), negate(0xffff_ffff));
    try std.testing.expectEqual(@as(u32, 0x2152_4110), negate(0xdead_bef0));
}

test "negate is its own inverse" {
    const cases = [_]u32{ 0, 1, 0x0001_0000, 0xffff_ffff, 0x1234_5678, 0xdead_bef0 };
    for (cases) |case| {
        try std.testing.expectEqual(case, negate(negate(case)));
    }
}

test "add plus negate keeps one's-complement carry semantics" {
    const cases = [_]struct { sum: u32, expected: u32 }{
        .{ .sum = 0x0000_0000, .expected = 0x0000_0000 },
        .{ .sum = 0x0000_0001, .expected = 0x0000_0001 },
        .{ .sum = 0x0001_0000, .expected = 0x0000_0001 },
        .{ .sum = 0x1234_5678, .expected = 0x0000_0001 },
        .{ .sum = 0xffff_ffff, .expected = 0x0000_0001 },
    };

    for (cases) |case| {
        try std.testing.expectEqual(case.expected, add(case.sum, negate(case.sum)));
    }
}

test "shift and block helpers preserve odd-byte carry discipline" {
    const seed = 0x1357_9bdf;
    const fragment = 0x2468_ace0;

    try std.testing.expectEqual(fragment, shift(fragment, 0));
    try std.testing.expectEqual(std.math.rotr(u32, fragment, 8), shift(fragment, 1));
    try std.testing.expectEqual(fragment, shift(fragment, 2));
    try std.testing.expectEqual(std.math.rotr(u32, fragment, 8), shift(fragment, 3));

    const even_added = blockAdd(seed, fragment, 0);
    const odd_added = blockAdd(seed, fragment, 1);

    try std.testing.expectEqual(add(seed, fragment), even_added);
    try std.testing.expectEqual(add(seed, std.math.rotr(u32, fragment, 8)), odd_added);
    try std.testing.expectEqual(seed, blockSub(even_added, fragment, 0));
    try std.testing.expectEqual(seed, blockSub(odd_added, fragment, 1));
}

test "incremental helper exports keep large odd offsets and 16-bit carries aligned" {
    const seed = 0x1357_9bdf;
    const fragment = 0x2468_ace0;

    try std.testing.expectEqual(fragment, shift(fragment, 256));
    try std.testing.expectEqual(std.math.rotr(u32, fragment, 8), shift(fragment, 255));
    try std.testing.expectEqual(add(seed, fragment), blockAdd(seed, fragment, 256));
    try std.testing.expectEqual(add(seed, std.math.rotr(u32, fragment, 8)), blockAdd(seed, fragment, 255));
    try std.testing.expectEqual(seed, blockSub(blockAdd(seed, fragment, 255), fragment, 255));

    const fold_cases = [_]u32{ 0, 1, 0x0001_0000, 0x1234_5678, 0xffff_ffff };
    for (fold_cases) |sum| {
        try std.testing.expectEqual(from32to16(sum), unfold(~fold(sum)));
    }

    const add16_cases = [_]struct {
        sum: u16,
        addend: u16,
        expected_add: u16,
        expected_sub: u16,
    }{
        .{ .sum = 0x0000, .addend = 0x0000, .expected_add = 0x0000, .expected_sub = 0xffff },
        .{ .sum = 0xffff, .addend = 0x0001, .expected_add = 0x0001, .expected_sub = 0xfffe },
        .{ .sum = 0x7fff, .addend = 0x8000, .expected_add = 0xffff, .expected_sub = 0xfffe },
        .{ .sum = 0xfffe, .addend = 0x0003, .expected_add = 0x0002, .expected_sub = 0xfffb },
    };

    for (add16_cases) |case| {
        try std.testing.expectEqual(case.expected_add, add16(case.sum, case.addend));
        try std.testing.expectEqual(case.expected_sub, sub16(case.sum, case.addend));
    }
}

fn referencePartial(bytes: []const u8, seed: u32) u32 {
    var sum: u64 = seed;
    var index: usize = 0;

    while (index < bytes.len) : (index += 2) {
        const hi = @as(u64, bytes[index]) << 8;
        const lo = if (index + 1 < bytes.len) @as(u64, bytes[index + 1]) else 0;
        sum += hi | lo;
    }

    while ((sum >> 16) != 0) {
        sum = (sum & 0xffff) + (sum >> 16);
    }
    return @intCast(sum);
}

test "partial and compute match reference accumulation across seeded odd payloads" {
    const odd_payload = [_]u8{ 0xde, 0xad, 0xbe, 0xef, 0x42 };
    const even_payload = [_]u8{ 0x70, 0x68, 0x61, 0x73, 0x65, 0x36 };
    const single_payload = [_]u8{0xa5};
    const empty_payload = [_]u8{};
    const partial_cases = [_]struct {
        bytes: []const u8,
        seed: u32,
    }{
        .{ .bytes = empty_payload[0..], .seed = 0 },
        .{ .bytes = odd_payload[0..], .seed = 0 },
        .{ .bytes = odd_payload[0..], .seed = 0x1357_9bdf },
        .{ .bytes = even_payload[0..], .seed = 0x2468_ace0 },
        .{ .bytes = single_payload[0..], .seed = 0xffff_ffff },
    };

    for (partial_cases) |case| {
        try std.testing.expectEqual(referencePartial(case.bytes, case.seed), partial(case.bytes, case.seed));
    }

    const compute_cases = [_][]const u8{
        empty_payload[0..],
        odd_payload[0..],
        even_payload[0..],
        single_payload[0..],
    };
    for (compute_cases) |case| {
        try std.testing.expectEqual(fold(referencePartial(case, 0)), compute(case));
        try std.testing.expectEqual(compute(case), ipComputeCsum(case));
    }
}

fn expectFragmentedPartialMatchesWhole(payload: []const u8, split: usize, seed: u32) !void {
    const head = payload[0..split];
    const tail = payload[split..];
    const head_partial = partial(head, seed);
    const tail_partial = partial(tail, 0);
    const recomposed = blockAdd(head_partial, tail_partial, head.len);

    try std.testing.expectEqual(partial(payload, seed), normalize(recomposed));
    if (seed == 0) {
        try std.testing.expectEqual(compute(payload), fold(recomposed));
    }
}

test "block helpers recompute whole payload partials across fragment boundaries" {
    const odd_payload = [_]u8{ 0xde, 0xad, 0xbe, 0xef, 0x42 };
    const even_payload = [_]u8{ 0x70, 0x68, 0x61, 0x73, 0x65, 0x36 };
    const singleton_payload = [_]u8{0xa5};
    const empty_payload = [_]u8{};
    const payloads = [_][]const u8{
        empty_payload[0..],
        singleton_payload[0..],
        odd_payload[0..],
        even_payload[0..],
        "phase6-fragment-checksum",
    };
    const seeds = [_]u32{ 0, 0x1357_9bdf, 0xffff_ffff };

    for (payloads) |payload| {
        for (seeds) |seed| {
            for (0..payload.len + 1) |split| {
                try expectFragmentedPartialMatchesWhole(payload, split, seed);
            }
        }
    }
}

test "replacement helpers match direct recomputation for payload and header edits" {
    var payload = [_]u8{ 0x70, 0x68, 0x61, 0x73, 0x65, 0x36 };
    const old_partial = partial(&payload, 0);
    const old_word = (@as(u32, payload[0]) << 8) | payload[1];
    payload[0] = 0x12;
    payload[1] = 0x34;
    const new_word = (@as(u32, payload[0]) << 8) | payload[1];
    const replaced_partial = replace(old_partial, old_word, new_word);
    try std.testing.expectEqual(partial(&payload, 0), partial("", replaced_partial));

    var ipv4_header = [_]u8{
        0x45, 0x00, 0x00, 0x3c,
        0x1c, 0x46, 0x40, 0x00,
        0x40, 0x06, 0x00, 0x00,
        0xc0, 0xa8, 0x00, 0x01,
        0xc0, 0xa8, 0x00, 0xc7,
    };
    const old_checksum = compute(&ipv4_header);
    const old_total_length = (@as(u16, ipv4_header[2]) << 8) | ipv4_header[3];
    ipv4_header[2] = 0x00;
    ipv4_header[3] = 0x40;
    const new_total_length = (@as(u16, ipv4_header[2]) << 8) | ipv4_header[3];
    const diff = sub(new_total_length, old_total_length);
    const recomputed_length_checksum = compute(&ipv4_header);
    try std.testing.expectEqual(recomputed_length_checksum, replaceByDiff(old_checksum, diff));
    try std.testing.expectEqual(recomputed_length_checksum, replace2(old_checksum, old_total_length, new_total_length));

    ipv4_header[10] = 0;
    ipv4_header[11] = 0;
    const checksum_before_addr_change = compute(&ipv4_header);
    ipv4_header[12] = 0xc0;
    ipv4_header[13] = 0xa8;
    ipv4_header[14] = 0x00;
    ipv4_header[15] = 0x02;
    try std.testing.expectEqual(compute(&ipv4_header), replace4(checksum_before_addr_change, 0xc0a8_0001, 0xc0a8_0002));
}

test "pseudo-header helpers match manual accumulation for IPv4 and IPv6" {
    const payload_seed = partial("phase6", 0);

    const v4_result = tcpUdpNofold(payload_seed, 0xc0a8_0001, 0xc0a8_00c7, 6, 17);
    var manual_v4 = normalize(payload_seed);
    manual_v4 = add(manual_v4, 0xc0a8);
    manual_v4 = add(manual_v4, 0x0001);
    manual_v4 = add(manual_v4, 0xc0a8);
    manual_v4 = add(manual_v4, 0x00c7);
    manual_v4 = add(manual_v4, 17);
    manual_v4 = add(manual_v4, 6);
    try std.testing.expectEqual(normalize(manual_v4), v4_result);
    try std.testing.expectEqual(fold(v4_result), tcpUdpMagic(payload_seed, 0xc0a8_0001, 0xc0a8_00c7, 6, 17));

    const v6_saddr = [_]u8{ 0x20, 0x01, 0x0d, 0xb8, 0x00, 0x00, 0x00, 0x01, 0xde, 0xad, 0xbe, 0xef, 0xca, 0xfe, 0xba, 0xbe };
    const v6_daddr = [_]u8{ 0x20, 0x01, 0x0d, 0xb8, 0x00, 0x00, 0x00, 0x02, 0xde, 0xad, 0xbe, 0xef, 0xca, 0xfe, 0xba, 0xbf };
    const v6_len: u32 = 0x0001_2345;
    const v6_proto: u8 = 58;
    const v6_result = tcpUdpV6Nofold(payload_seed, &v6_saddr, &v6_daddr, v6_len, v6_proto);
    var manual_v6 = normalize(payload_seed);

    for (0..4) |index| {
        const offset = index * 4;
        manual_v6 = add(manual_v6, readBigEndianU32(v6_saddr[offset .. offset + 4]));
        manual_v6 = add(manual_v6, readBigEndianU32(v6_daddr[offset .. offset + 4]));
    }

    manual_v6 = add(manual_v6, v6_len >> 16);
    manual_v6 = add(manual_v6, v6_len & 0xffff);
    manual_v6 = add(manual_v6, v6_proto);
    try std.testing.expectEqual(normalize(manual_v6), v6_result);
    try std.testing.expectEqual(fold(v6_result), tcpUdpV6Magic(payload_seed, &v6_saddr, &v6_daddr, v6_len, v6_proto));
}

test "ipFastCsum stays aligned with compute across aligned IPv4 headers" {
    const HeaderCase = struct {
        name: []const u8,
        header: []const u8,
    };

    const minimal_ipv4 = [_]u8{
        0x45, 0x00, 0x00, 0x3c,
        0x1c, 0x46, 0x40, 0x00,
        0x40, 0x06, 0x00, 0x00,
        0xc0, 0xa8, 0x00, 0x01,
        0xc0, 0xa8, 0x00, 0xc7,
    };
    const ttl_and_length_update = [_]u8{
        0x45, 0x00, 0x00, 0x40,
        0x1c, 0x46, 0x40, 0x00,
        0x3f, 0x11, 0x00, 0x00,
        0xc0, 0xa8, 0x00, 0x02,
        0xc0, 0xa8, 0x00, 0xc7,
    };
    const ipv4_with_options = [_]u8{
        0x46, 0x00, 0x00, 0x30,
        0x12, 0x34, 0x20, 0x00,
        0x40, 0x11, 0x00, 0x00,
        0xc0, 0xa8, 0x01, 0x01,
        0xc0, 0xa8, 0x01, 0x02,
        0x01, 0x01, 0x00, 0x00,
    };
    const headers = [_]HeaderCase{
        .{ .name = "minimal ipv4 header", .header = &minimal_ipv4 },
        .{ .name = "ttl and length update keeps aligned header fast path", .header = &ttl_and_length_update },
        .{ .name = "header with 4-byte options stays on the aligned fast path", .header = &ipv4_with_options },
    };
    for (headers) |case| try std.testing.expectEqual(compute(case.header), ipFastCsum(case.header));
}
