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

fn unfold(sum: u16) u32 {
    return sum;
}

fn add16(sum: u16, addend: u16) u16 {
    const result = sum +% addend;
    return result +% @as(u16, @intFromBool(result < addend));
}

fn sub16(sum: u16, addend: u16) u16 {
    return add16(sum, ~addend);
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

test "tcpUdpNofold matches direct pseudo-header accumulation" {
    const payload = [_]u8{ 0xde, 0xad, 0xbe, 0xef, 0xfa, 0xce };
    const saddr: u32 = 0xc0a8_0001;
    const daddr: u32 = 0xc0a8_0002;
    const proto: u8 = 17;

    var pseudo_header = [_]u8{
        0xc0, 0xa8, 0x00, 0x01,
        0xc0, 0xa8, 0x00, 0x02,
        0x00, proto, 0x00, payload.len,
    };

    const payload_partial = partial(&payload, 0);
    const pseudo_partial = partial(&pseudo_header, 0);
    const direct_combined = partial("", blockAdd(pseudo_partial, payload_partial, pseudo_header.len));
    const helper_combined = tcpUdpNofold(payload_partial, saddr, daddr, payload.len, proto);

    try std.testing.expectEqual(direct_combined, helper_combined);
    try std.testing.expectEqual(fold(direct_combined), fold(helper_combined));
}
