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

fn appendBigEndianU16(buffer: []u8, value: u16) void {
    const pair: *[2]u8 = @ptrCast(buffer[0..2]);
    std.mem.writeInt(u16, pair, value, .big);
}

fn appendBigEndianU32(buffer: []u8, value: u32) void {
    const pair: *[4]u8 = @ptrCast(buffer[0..4]);
    std.mem.writeInt(u32, pair, value, .big);
}

const ComputeCase = struct {
    bytes: []const u8,
    expected_partial: u32,
    expected_compute: u16,
};

const CompositionCase = struct {
    payload: []const u8,
    split: usize,
    expected_partial: u32,
    expected_fold: u16,
};

const PseudoHeaderCase = struct {
    payload: []const u8,
    saddr: u32,
    daddr: u32,
    proto: u8,
    expected_compute: u16,
};

test "compute matches the current checksum edge-case matrix" {
    const carry_payload = [_]u8{ 0xff, 0xff, 0xff, 0xff, 0x7f };
    const cases = [_]ComputeCase{
        .{ .bytes = "", .expected_partial = 0x0000, .expected_compute = 0xffff },
        .{ .bytes = "\x00\x01", .expected_partial = 0x0001, .expected_compute = 0xfffe },
        .{
            .bytes = &[_]u8{
                0x45, 0x00, 0x00, 0x3c,
                0x1c, 0x46, 0x40, 0x00,
                0x40, 0x06, 0x00, 0x00,
                0xc0, 0xa8, 0x00, 0x01,
                0xc0, 0xa8, 0x00, 0xc7,
            },
            .expected_partial = 0x63a2,
            .expected_compute = 0x9c5d,
        },
        .{ .bytes = "abcde", .expected_partial = 0x29c7, .expected_compute = 0xd638 },
        .{ .bytes = &carry_payload, .expected_partial = 0x7f00, .expected_compute = 0x80ff },
    };

    for (cases) |case| {
        try std.testing.expectEqual(case.expected_partial, referencePartial(case.bytes, 0));
        try std.testing.expectEqual(case.expected_partial, partial(case.bytes, 0));
        try std.testing.expectEqual(case.expected_compute, compute(case.bytes));
    }
}

test "partial checksums compose across the even and odd split matrix" {
    const cases = [_]CompositionCase{
        .{ .payload = "checksum fragments keep their carry", .split = 20, .expected_partial = 0x0e7b, .expected_fold = 0xf184 },
        .{ .payload = "checksum fragments keep their carry", .split = 21, .expected_partial = 0x0e7b, .expected_fold = 0xf184 },
    };

    for (cases) |case| {
        const whole = partial(case.payload, 0);
        const left = partial(case.payload[0..case.split], 0);
        const right = partial(case.payload[case.split..], 0);
        const combined = blockAdd(left, right, case.split);

        try std.testing.expectEqual(case.expected_partial, whole);
        try std.testing.expectEqual(case.expected_partial, normalize(combined));
        try std.testing.expectEqual(case.expected_fold, fold(whole));
        try std.testing.expectEqual(case.expected_fold, compute(case.payload));
    }
}

test "tcpUdpNofold matches the pseudo-header fixture parity" {
    const cases = [_]PseudoHeaderCase{
        .{
            .payload = "zigux checksum",
            .saddr = 0xc0a8_0001,
            .daddr = 0xc0a8_00c7,
            .proto = 17,
            .expected_compute = 0x7a1b,
        },
    };

    for (cases) |case| {
        const payload_partial = partial(case.payload, 0);

        var pseudo_header: [12]u8 = undefined;
        appendBigEndianU32(pseudo_header[0..4], case.saddr);
        appendBigEndianU32(pseudo_header[4..8], case.daddr);
        pseudo_header[8] = 0;
        pseudo_header[9] = case.proto;
        appendBigEndianU16(pseudo_header[10..12], @intCast(case.payload.len));

        const expected = blockAdd(partial(&pseudo_header, 0), payload_partial, pseudo_header.len);
        const actual = tcpUdpNofold(payload_partial, case.saddr, case.daddr, @intCast(case.payload.len), case.proto);

        try std.testing.expectEqual(normalize(expected), actual);
        try std.testing.expectEqual(case.expected_compute, fold(actual));
    }
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
