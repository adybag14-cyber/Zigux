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
    // Rotate the partial sum when the offset lands on an odd byte.
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

pub fn unfold(sum: u16) u32 {
    return sum;
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

pub fn ipFastCsum(header: []const u8) u16 {
    std.debug.assert((header.len & 3) == 0);
    return compute(header);
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

fn writeBigEndianU16(bytes: []u8, value: u16) void {
    const pair: *[2]u8 = @ptrCast(bytes[0..2]);
    std.mem.writeInt(u16, pair, value, .big);
}

fn writeBigEndianU32(bytes: []u8, value: u32) void {
    const pair: *[4]u8 = @ptrCast(bytes[0..4]);
    std.mem.writeInt(u32, pair, value, .big);
}

test "negate wraps around unfolded checksum sums" {
    try std.testing.expectEqual(@as(u32, 0), negate(0));
    try std.testing.expectEqual(@as(u32, 0xffff_ffff), negate(1));
    try std.testing.expectEqual(@as(u32, 1), negate(0xffff_ffff));
    try std.testing.expectEqual(@as(u32, 0x2152_4110), negate(0xdead_bef0));
}

test "negate is its own inverse" {
    const cases = [_]u32{
        0,
        1,
        0x0001_0000,
        0xffff_ffff,
        0x1234_5678,
        0xdead_bef0,
    };

    for (cases) |case| {
        try std.testing.expectEqual(case, negate(negate(case)));
    }
}

test "add plus negate keeps one's-complement carry semantics" {
    const cases = [_]struct {
        sum: u32,
        expected: u32,
    }{
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

test "partial fragments recombine through blockAdd across odd and even split points" {
    const payload = [_]u8{ 0x70, 0x68, 0x61, 0x73, 0x65, 0x36, 0xaa };
    const seed: u32 = 0x1357;
    const whole = partial(&payload, seed);
    const split_points = [_]usize{ 1, 2, 3, 5, payload.len };

    for (split_points) |split| {
        const head = partial(payload[0..split], seed);
        const tail = partial(payload[split..], 0);
        const recombined = blockAdd(head, tail, split);

        try std.testing.expectEqual(whole, normalize(recombined));
        try std.testing.expectEqual(head, normalize(blockSub(recombined, tail, split)));
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

test "unfold exposes stored checksum words for replacement helpers" {
    const stored_word_cases = [_]u16{ 0x0000, 0x0001, 0x9c5d, 0xffff };
    const replacement_stable_cases = [_]u16{ 0x0001, 0x9c5d, 0xfffe };

    for (stored_word_cases) |case| {
        try std.testing.expectEqual(@as(u32, case), unfold(case));
    }

    for (replacement_stable_cases) |case| {
        try std.testing.expectEqual(case, replaceByDiff(case, 0));
        try std.testing.expectEqual(case, replace2(case, 0x1234, 0x1234));
        try std.testing.expectEqual(case, replace4(case, 0xc0a8_0001, 0xc0a8_0001));
    }
}

test "pseudo-header helpers match direct pseudo-header plus payload recomputation" {
    const ipv4_payload = [_]u8{ 0xde, 0xad, 0xbe, 0xef, 0xfa };
    const ipv4_saddr: u32 = 0xc0a8_0001;
    const ipv4_daddr: u32 = 0xc0a8_00c7;
    const ipv4_proto: u8 = 17;
    const ipv4_partial = tcpUdpNofold(partial(&ipv4_payload, 0), ipv4_saddr, ipv4_daddr, ipv4_payload.len, ipv4_proto);
    var ipv4_packet: [17]u8 = undefined;
    writeBigEndianU32(ipv4_packet[0..4], ipv4_saddr);
    writeBigEndianU32(ipv4_packet[4..8], ipv4_daddr);
    ipv4_packet[8] = 0;
    ipv4_packet[9] = ipv4_proto;
    writeBigEndianU16(ipv4_packet[10..12], ipv4_payload.len);
    @memcpy(ipv4_packet[12..], &ipv4_payload);
    try std.testing.expectEqual(compute(&ipv4_packet), fold(ipv4_partial));

    const ipv6_payload = [_]u8{ 0x70, 0x68, 0x61, 0x73, 0x65, 0x36, 0xaa };
    const ipv6_saddr = [_]u8{ 0x20, 0x01, 0x0d, 0xb8, 0x00, 0x00, 0x00, 0x01, 0xde, 0xad, 0xbe, 0xef, 0xca, 0xfe, 0xba, 0xbe };
    const ipv6_daddr = [_]u8{ 0x20, 0x01, 0x0d, 0xb8, 0x00, 0x00, 0x00, 0x02, 0xde, 0xad, 0xbe, 0xef, 0xca, 0xfe, 0xba, 0xbf };
    const ipv6_proto: u8 = 58;
    const ipv6_partial = tcpUdpV6Nofold(partial(&ipv6_payload, 0), &ipv6_saddr, &ipv6_daddr, ipv6_payload.len, ipv6_proto);
    var ipv6_packet: [47]u8 = undefined;
    @memcpy(ipv6_packet[0..16], &ipv6_saddr);
    @memcpy(ipv6_packet[16..32], &ipv6_daddr);
    writeBigEndianU32(ipv6_packet[32..36], ipv6_payload.len);
    ipv6_packet[36] = 0;
    ipv6_packet[37] = 0;
    ipv6_packet[38] = 0;
    ipv6_packet[39] = ipv6_proto;
    @memcpy(ipv6_packet[40..], &ipv6_payload);
    try std.testing.expectEqual(compute(&ipv6_packet), fold(ipv6_partial));
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
}
