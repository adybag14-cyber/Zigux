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

fn referencePartial(bytes: []const u8, seed: u32) u32 {
    var sum: u64 = seed;
    var index: usize = 0;

    while (index + 1 < bytes.len) : (index += 2) {
        sum += (@as(u64, bytes[index]) << 8) | bytes[index + 1];
    }

    if (index < bytes.len) {
        sum += @as(u64, bytes[index]) << 8;
    }

    while ((sum >> 16) != 0) {
        sum = (sum & 0xffff) + (sum >> 16);
    }

    return @intCast(sum);
}

test "compute matches the reference checksum across even and odd sizes" {
    const cases = [_][]const u8{
        "",
        "\x00",
        "\x00\x01",
        "\x00\x01\xf2\x03\xf4\xf5\xf6\xf7",
        "\xff\xff",
        "\x12\x34\x56",
    };

    for (cases) |bytes| {
        try std.testing.expectEqual(referencePartial(bytes, 0), partial(bytes, 0));
        try std.testing.expectEqual(~@as(u16, @intCast(referencePartial(bytes, 0))), compute(bytes));
    }
}

test "partial checksums compose across split buffers" {
    const bytes = "split checksum composition still needs parity";
    const prefix = bytes[0..17];
    const suffix = bytes[17..];

    const whole = partial(bytes, 0);
    const left = partial(prefix, 0);
    const right = partial(suffix, 0);
    const combined = blockAdd(left, right, prefix.len);

    try std.testing.expectEqual(whole, normalize(combined));
    try std.testing.expectEqual(fold(whole), compute(bytes));
}

test "tcpUdpNofold matches pseudo header accumulation" {
    const payload = "zigux checksum";
    const payload_partial = partial(payload, 0);
    const saddr: u32 = 0xc0a8_0001;
    const daddr: u32 = 0xc0a8_00c7;
    const proto: u8 = 17;

    var pseudo_header: [12]u8 = undefined;
    pseudo_header[0] = 0xc0;
    pseudo_header[1] = 0xa8;
    pseudo_header[2] = 0x00;
    pseudo_header[3] = 0x01;
    pseudo_header[4] = 0xc0;
    pseudo_header[5] = 0xa8;
    pseudo_header[6] = 0x00;
    pseudo_header[7] = 0xc7;
    pseudo_header[8] = 0;
    pseudo_header[9] = proto;
    pseudo_header[10] = 0;
    pseudo_header[11] = payload.len;

    const expected = blockAdd(partial(&pseudo_header, 0), payload_partial, pseudo_header.len);
    const actual = tcpUdpNofold(payload_partial, saddr, daddr, payload.len, proto);

    try std.testing.expectEqual(normalize(expected), actual);
}

test "add, sub, and offset shifting preserve checksum arithmetic" {
    const lhs: u32 = 0x12_34;
    const rhs: u32 = 0xab_cd;

    try std.testing.expectEqual(lhs, sub(add(lhs, rhs), rhs));
    try std.testing.expectEqual(rhs, shift(rhs, 2));
    try std.testing.expectEqual(@as(u32, 0xcd_00_00_ab), shift(0xab_cd, 1));
    try std.testing.expectEqual(shift(rhs, 1), shift(rhs, 3));
    try std.testing.expectEqual(add(lhs, shift(rhs, 1)), blockAdd(lhs, rhs, 1));
    try std.testing.expectEqual(sub(lhs, shift(rhs, 1)), blockSub(lhs, rhs, 1));
}
