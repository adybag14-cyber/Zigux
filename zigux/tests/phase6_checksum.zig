const std = @import("std");
const checksum = @import("checksum");
const fixtures = @import("fixtures/phase6_checksum_vectors.zig");

fn foldCarry(sum: u32) u32 {
    var acc = sum;
    while ((acc >> 16) != 0) {
        acc = (acc & 0xffff) + (acc >> 16);
    }
    return acc;
}

fn referenceInternetChecksum(bytes: []const u8) u16 {
    var acc: u32 = 0;
    var index: usize = 0;
    while (index + 1 < bytes.len) : (index += 2) {
        const pair: *const [2]u8 = @ptrCast(bytes[index .. index + 2]);
        acc += std.mem.readInt(u16, pair, .big);
    }
    if (index < bytes.len) {
        acc += @as(u16, bytes[index]) << 8;
    }
    return ~@as(u16, @truncate(foldCarry(acc)));
}

fn referencePartial(bytes: []const u8, seed: u32) u32 {
    var acc: u64 = seed;
    var index: usize = 0;
    while (index + 1 < bytes.len) : (index += 2) {
        const pair: *const [2]u8 = @ptrCast(bytes[index .. index + 2]);
        acc += std.mem.readInt(u16, pair, .big);
    }
    if (index < bytes.len) {
        acc += @as(u16, bytes[index]) << 8;
    }
    while ((acc >> 16) != 0) {
        acc = (acc & 0xffff) + (acc >> 16);
    }
    return @intCast(acc);
}

fn appendBigEndianU16(buffer: []u8, value: u16) void {
    const pair: *[2]u8 = @ptrCast(buffer[0..2]);
    std.mem.writeInt(u16, pair, value, .big);
}

fn appendBigEndianU32(buffer: []u8, value: u32) void {
    const pair: *[4]u8 = @ptrCast(buffer[0..4]);
    std.mem.writeInt(u32, pair, value, .big);
}

test "phase 6 checksum module imports cleanly" {
    _ = checksum;
}

test "fixture-backed compute parity covers the current checksum vectors" {
    for (fixtures.compute_cases) |case| {
        try std.testing.expectEqual(case.expected_partial, checksum.partial(case.bytes, 0));
        try std.testing.expectEqual(case.expected_compute, checksum.compute(case.bytes));
        try std.testing.expectEqual(referenceInternetChecksum(case.bytes), checksum.compute(case.bytes));
    }
}

test "partial sums compose across the fixture split matrix" {
    for (fixtures.composition_cases) |case| {
        const whole = checksum.partial(case.payload, 0);
        const prefix = checksum.partial(case.payload[0..case.split], 0);
        const suffix = checksum.partial(case.payload[case.split..], 0);
        const combined = checksum.blockAdd(prefix, suffix, case.split);

        try std.testing.expectEqual(case.expected_partial, whole);
        try std.testing.expectEqual(case.expected_partial, checksum.partial("", combined));
        try std.testing.expectEqual(case.expected_fold, checksum.fold(whole));
    }
}

test "seeded partial accumulation matches the fixture-backed reference" {
    for (fixtures.seeded_cases) |case| {
        try std.testing.expectEqual(case.expected_partial, checksum.partial(case.bytes, case.seed));
        try std.testing.expectEqual(case.expected_partial, referencePartial(case.bytes, case.seed));
    }
}

test "pseudo header accumulation matches the fixture-backed reference checksum" {
    for (fixtures.pseudo_header_cases) |case| {
        const payload_partial = checksum.partial(case.payload, 0);

        var pseudo_header: [12]u8 = undefined;
        appendBigEndianU32(pseudo_header[0..4], case.saddr);
        appendBigEndianU32(pseudo_header[4..8], case.daddr);
        pseudo_header[8] = 0;
        pseudo_header[9] = case.proto;
        appendBigEndianU16(pseudo_header[10..12], @intCast(case.payload.len));

        const pseudo_partial = checksum.partial(&pseudo_header, 0);
        const combined_partial = checksum.blockAdd(pseudo_partial, payload_partial, pseudo_header.len);
        const helper_partial = checksum.tcpUdpNofold(payload_partial, case.saddr, case.daddr, @intCast(case.payload.len), case.proto);
        const actual = checksum.fold(helper_partial);

        var pseudo_and_payload: [64]u8 = undefined;
        const combined_len = 12 + case.payload.len;
        @memcpy(pseudo_and_payload[0..12], &pseudo_header);
        @memcpy(pseudo_and_payload[12..combined_len], case.payload);

        try std.testing.expectEqual(combined_partial, helper_partial);
        try std.testing.expectEqual(case.expected_compute, actual);
        try std.testing.expectEqual(referenceInternetChecksum(pseudo_and_payload[0..combined_len]), actual);
    }
}
