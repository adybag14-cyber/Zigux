// SPDX-License-Identifier: GPL-2.0-or-later
const std = @import("std");
pub fn add(sum: u32, addend: u32) u32 {
    const result = sum +% addend;
    return result + @intFromBool(result < addend);
}

pub fn sub(sum: u32, addend: u32) u32 {
    return add(sum, ~addend);
}

pub fn negate(sum: u32) u32 {
    return 0 -% sum;
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

pub fn from32to16(sum: u32) u16 {
    return @intCast(normalize(sum));
}

pub fn fold(sum: u32) u16 {
    return ~from32to16(sum);
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

pub fn replaceByDiff(sum: u16, diff: u32) u16 {
    return fold(add(diff, ~unfold(sum)));
}

pub fn replace4(sum: u16, from: u32, to: u32) u16 {
    const tmp = sub(~unfold(sum), from);
    return fold(add(tmp, to));
}

pub fn replace2(sum: u16, old: u16, new: u16) u16 {
    return ~add16(sub16(~sum, old), new);
}

pub fn replace(sum: u32, old: u32, new: u32) u32 {
    return add(sub(sum, old), new);
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

pub fn tcpUdpV6Nofold(sum: u32, saddr: [16]u8, daddr: [16]u8, len: u32, proto: u8) u32 {
    var result = normalize(sum);
    var trailer = [_]u8{0} ** 8;

    appendBigEndianU32(trailer[0..4], len);
    trailer[7] = proto;

    result = blockAdd(result, partial(&saddr, 0), 0);
    result = blockAdd(result, partial(&daddr, 0), 0);
    result = blockAdd(result, partial(&trailer, 0), 0);
    return normalize(result);
}

pub fn partial(bytes: []const u8, seed: u32) u32 {
    var sum = normalize(seed);
    var index: usize = 0;

    while (index + 1 < bytes.len) : (index += 2) {
        const word = (@as(u32, bytes[index]) << 8) | bytes[index + 1];
        sum = add(sum, word);
    }

    if (index < bytes.len) {
        sum = add(sum, @as(u32, bytes[index]) << 8);
    }

    return normalize(sum);
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

fn appendBigEndianU32(buffer: []u8, value: u32) void {
    const pair: *[4]u8 = @ptrCast(buffer[0..4]);
    std.mem.writeInt(u32, pair, value, .big);
}

test "add, sub, negate, and offset shifting preserve checksum arithmetic" {
    const lhs: u32 = 0x12_34;
    const rhs: u32 = 0xab_cd;
    const value: u32 = 0x1234_5678;

    try std.testing.expectEqual(lhs, sub(add(lhs, rhs), rhs));
    try std.testing.expectEqual(rhs, shift(rhs, 2));
    try std.testing.expectEqual(@as(u32, 0xcd_00_00_ab), shift(0xab_cd, 1));
    try std.testing.expectEqual(shift(rhs, 1), shift(rhs, 3));
    try std.testing.expectEqual(add(lhs, shift(rhs, 1)), blockAdd(lhs, rhs, 1));
    try std.testing.expectEqual(sub(lhs, shift(rhs, 1)), blockSub(lhs, rhs, 1));
    try std.testing.expectEqual(@as(u32, 0), negate(0));
    try std.testing.expectEqual(@as(u32, 0xffff_ffff), negate(1));
    try std.testing.expectEqual(@as(u32, 0xedcb_a988), negate(value));
    try std.testing.expectEqual(value, negate(negate(value)));
    try std.testing.expectEqual(@as(u32, 1), add(value, negate(value)));
}

test "from32to16, fold, unfold, and 16-bit carry helpers preserve checksum identities" {
    const cases = [_]struct {
        sum: u32,
        expected_from32to16: u16,
    }{
        .{ .sum = 0x0000_0000, .expected_from32to16 = 0x0000 },
        .{ .sum = 0x0000_ffff, .expected_from32to16 = 0xffff },
        .{ .sum = 0x0001_0000, .expected_from32to16 = 0x0001 },
        .{ .sum = 0xffff_0001, .expected_from32to16 = 0x0001 },
        .{ .sum = 0xffff_ffff, .expected_from32to16 = 0xffff },
        .{ .sum = 0x1234_fedc, .expected_from32to16 = 0x1111 },
    };

    for (cases) |case| {
        try std.testing.expectEqual(case.expected_from32to16, from32to16(case.sum));
        try std.testing.expectEqual(case.expected_from32to16, @as(u16, @intCast(normalize(case.sum))));
        try std.testing.expectEqual(~case.expected_from32to16, fold(case.sum));
        try std.testing.expectEqual(@as(u32, case.expected_from32to16), unfold(case.expected_from32to16));
    }

    try std.testing.expectEqual(@as(u16, 0x0001), add16(0xffff, 0x0001));
    try std.testing.expectEqual(@as(u16, 0xffff), add16(0xffff, 0x0000));
    try std.testing.expectEqual(@as(u16, 0xffff), add16(0xffff, 0xffff));
    try std.testing.expectEqual(@as(u16, 0xfffe), sub16(0x0000, 0x0001));
    try std.testing.expectEqual(@as(u16, 0x1234), sub16(add16(0x1234, 0xabcd), 0xabcd));
}

test "incremental replacement helpers match recomputed payload and header checksums" {
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
    ipv4_header[10] = 0;
    ipv4_header[11] = 0;
    const diff = sub(new_total_length, old_total_length);
    const replaced_by_diff = replaceByDiff(old_checksum, diff);
    const replaced2 = replace2(old_checksum, old_total_length, new_total_length);

    try std.testing.expectEqual(compute(&ipv4_header), replaced_by_diff);
    try std.testing.expectEqual(compute(&ipv4_header), replaced2);

    ipv4_header[10] = 0;
    ipv4_header[11] = 0;
    const checksum_before_addr_change = compute(&ipv4_header);
    const old_saddr: u32 = 0xc0a80001;
    const new_saddr: u32 = 0xc0a80002;
    ipv4_header[12] = 0xc0;
    ipv4_header[13] = 0xa8;
    ipv4_header[14] = 0x00;
    ipv4_header[15] = 0x02;

    try std.testing.expectEqual(compute(&ipv4_header), replace4(checksum_before_addr_change, old_saddr, new_saddr));
}
