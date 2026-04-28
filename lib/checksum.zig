// SPDX-License-Identifier: GPL-2.0-or-later
const std = @import("std");
const fixtures = @import("phase6_checksum_vectors");

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

test "compute matches the shared checksum edge-case matrix" {
    for (fixtures.compute_cases) |case| {
        try std.testing.expectEqual(case.expected_partial, referencePartial(case.bytes, 0));
        try std.testing.expectEqual(case.expected_partial, partial(case.bytes, 0));
        try std.testing.expectEqual(case.expected_compute, compute(case.bytes));
    }
}

test "partial checksums compose across the shared even and odd split matrix" {
    for (fixtures.composition_cases) |case| {
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

test "partial honors shared non-zero seeded cases across carry-heavy inputs" {
    for (fixtures.seeded_cases) |case| {
        try std.testing.expectEqual(case.expected_partial, referencePartial(case.bytes, case.seed));
        try std.testing.expectEqual(case.expected_partial, partial(case.bytes, case.seed));
    }
}

test "carry discipline matches the shared helper-local edge matrix" {
    for (fixtures.carry_discipline_cases) |case| {
        const actual_partial = partial(case.bytes, case.seed);
        try std.testing.expectEqual(case.expected_partial, referencePartial(case.bytes, case.seed));
        try std.testing.expectEqual(case.expected_partial, actual_partial);
        try std.testing.expectEqual(case.expected_compute, fold(actual_partial));
    }
}

test "tcpUdpNofold matches the shared pseudo-header fixture parity" {
    for (fixtures.pseudo_header_cases) |case| {
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
