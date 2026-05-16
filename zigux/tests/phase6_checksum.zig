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

fn referenceFoldedChecksum(bytes: []const u8, seed: u32) u16 {
    return ~@as(u16, @truncate(referencePartial(bytes, seed)));
}

fn appendBigEndianU16(buffer: []u8, value: u16) void {
    const pair: *[2]u8 = @ptrCast(buffer[0..2]);
    std.mem.writeInt(u16, pair, value, .big);
}

fn appendBigEndianU32(buffer: []u8, value: u32) void {
    const pair: *[4]u8 = @ptrCast(buffer[0..4]);
    std.mem.writeInt(u32, pair, value, .big);
}

fn appendIpv6PseudoHeader(buffer: *[40]u8, case: fixtures.Ipv6PseudoHeaderCase) void {
    @memcpy(buffer[0..16], case.saddr[0..]);
    @memcpy(buffer[16..32], case.daddr[0..]);
    appendBigEndianU32(buffer[32..36], case.declared_len);
    buffer[36] = 0;
    buffer[37] = 0;
    buffer[38] = 0;
    buffer[39] = case.proto;
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

test "kunit-inspired carry discipline stays stable on the helper surface" {
    for (fixtures.carry_discipline_cases) |case| {
        const partial = checksum.partial(case.bytes, case.seed);

        try std.testing.expectEqual(case.expected_partial, partial);
        try std.testing.expectEqual(case.expected_compute, checksum.fold(partial));
        try std.testing.expectEqual(case.expected_compute, referenceFoldedChecksum(case.bytes, case.seed));
    }
}

test "fixture-backed 16-bit carry helpers keep one's-complement wrap and borrow stable" {
    for (fixtures.add16_cases) |case| {
        try std.testing.expectEqual(case.expected_sum, checksum.add16(case.sum, case.addend));
    }
    for (fixtures.sub16_cases) |case| {
        try std.testing.expectEqual(case.expected_sum, checksum.sub16(case.sum, case.addend));
        try std.testing.expectEqual(case.expected_sum, checksum.add16(case.sum, ~case.addend));
    }

    const original: u16 = 0x1234;
    const addend: u16 = 0xabcd;
    const updated = checksum.add16(original, addend);
    try std.testing.expectEqual(@as(u16, 0xbe01), updated);
    try std.testing.expectEqual(original, checksum.sub16(updated, addend));
}

test "kunit random prefix matrix keeps partial and folded checksum parity stable" {
    for (fixtures.kunit_random_prefix_cases) |case| {
        const partial = checksum.partial(case.bytes, case.seed);

        try std.testing.expectEqual(case.expected_partial, partial);
        try std.testing.expectEqual(case.expected_partial, referencePartial(case.bytes, case.seed));
        try std.testing.expectEqual(case.expected_compute, checksum.fold(partial));
        try std.testing.expectEqual(case.expected_compute, referenceFoldedChecksum(case.bytes, case.seed));
    }
}

test "from32to16 folds unfolded sums before the final complement" {
    const Case = struct {
        name: []const u8,
        sum: u32,
        expected_folded: u16,
    };
    const cases = [_]Case{
        .{ .name = "zero", .sum = 0x0000_0000, .expected_folded = 0x0000 },
        .{ .name = "single carry into the low word", .sum = 0x0001_0000, .expected_folded = 0x0001 },
        .{ .name = "double carry collapse", .sum = 0xffff_0001, .expected_folded = 0x0001 },
        .{ .name = "all ones saturates to sixteen bits", .sum = 0xffff_ffff, .expected_folded = 0xffff },
        .{ .name = "mixed words preserve the remaining payload", .sum = 0x1234_5678, .expected_folded = 0x68ac },
    };

    for (cases) |case| {
        try std.testing.expectEqual(case.expected_folded, checksum.from32to16(case.sum));
        try std.testing.expectEqual(case.expected_folded, @as(u16, @intCast(foldCarry(case.sum))));
        try std.testing.expectEqual(@as(u16, ~case.expected_folded), checksum.fold(case.sum));
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

test "ipv6 pseudo header accumulation matches the fixture-backed unfolded checksum" {
    for (fixtures.ipv6_pseudo_header_cases) |case| {
        const payload_partial = checksum.partial(case.payload, 0);
        const helper_partial = checksum.tcpUdpV6Nofold(payload_partial, case.saddr, case.daddr, case.declared_len, case.proto);

        var pseudo_header: [40]u8 = undefined;
        appendIpv6PseudoHeader(&pseudo_header, case);

        const pseudo_partial = checksum.partial(&pseudo_header, 0);
        const combined_partial = checksum.blockAdd(pseudo_partial, payload_partial, pseudo_header.len);
        const normalized_combined_partial = checksum.partial("", combined_partial);

        var pseudo_and_payload: [96]u8 = undefined;
        const combined_len = pseudo_header.len + case.payload.len;
        @memcpy(pseudo_and_payload[0..pseudo_header.len], pseudo_header[0..]);
        @memcpy(pseudo_and_payload[pseudo_header.len..combined_len], case.payload);

        try std.testing.expectEqual(case.expected_nofold, helper_partial);
        try std.testing.expectEqual(case.expected_nofold, normalized_combined_partial);
        try std.testing.expectEqual(case.expected_nofold, referencePartial(pseudo_and_payload[0..combined_len], 0));
        try std.testing.expectEqual(referenceFoldedChecksum(pseudo_and_payload[0..combined_len], 0), checksum.fold(helper_partial));
    }
}

test "aligned ipv4 fast path stays matched to compute and reference folding" {
    for (fixtures.ip_fast_csum_cases) |case| {
        const expected = referenceInternetChecksum(case.header);
        try std.testing.expectEqual(expected, checksum.compute(case.header));
        try std.testing.expectEqual(expected, checksum.ipFastCsum(case.header));
    }
}
