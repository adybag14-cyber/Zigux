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

test "blockSub reverses blockAdd across odd and even fragment boundaries" {
    const Case = struct {
        bytes: []const u8,
        split: usize,
    };

    const carry_heavy = [_]u8{ 0xff, 0xfe, 0x01, 0x00, 0xaa, 0x55 };
    const odd_tail = [_]u8{ 0x10, 0x20, 0x30, 0x40, 0x50 };
    const cases = [_]Case{
        .{ .bytes = "abc", .split = 1 },
        .{ .bytes = "phase6", .split = 2 },
        .{ .bytes = &carry_heavy, .split = 3 },
        .{ .bytes = &odd_tail, .split = 4 },
    };

    for (cases) |case| {
        const prefix = checksum.partial(case.bytes[0..case.split], 0);
        const suffix = checksum.partial(case.bytes[case.split..], 0);
        const whole = checksum.partial(case.bytes, 0);
        const combined = checksum.blockAdd(prefix, suffix, case.split);
        const restored = checksum.partial("", checksum.blockSub(combined, suffix, case.split));

        try std.testing.expectEqual(whole, checksum.partial("", combined));
        try std.testing.expectEqual(prefix, restored);
        try std.testing.expectEqual(whole, checksum.partial("", checksum.blockAdd(restored, suffix, case.split)));
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

test "fixture-backed negate cases keep the public checksum helper reviewable" {
    try std.testing.expectEqual(@as(usize, 4), fixtures.negate_cases.len);
    try std.testing.expectEqualStrings("zero stays zero", fixtures.negate_cases[0].name);
    try std.testing.expectEqualStrings("mixed payload preserves ones complement carry", fixtures.negate_cases[3].name);

    for (fixtures.negate_cases) |case| {
        const negated = checksum.negate(case.sum);
        try std.testing.expectEqual(case.expected_negate, negated);
        try std.testing.expectEqual(case.expected_add_with_negate, checksum.add(case.sum, negated));
    }
}

test "fixture-backed fold cases keep the public checksum helper reviewable" {
    try std.testing.expectEqual(@as(usize, 5), fixtures.fold_cases.len);
    try std.testing.expectEqualStrings("zero", fixtures.fold_cases[0].name);
    try std.testing.expectEqual(@as(u16, 0x68ac), fixtures.fold_cases[4].expected_folded);

    for (fixtures.fold_cases) |case| {
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

test "incremental checksum replacement helpers match direct recomputation" {
    var payload = [_]u8{ 0x70, 0x68, 0x61, 0x73, 0x65, 0x36 };
    const old_partial = checksum.partial(&payload, 0);
    const old_word = (@as(u32, payload[0]) << 8) | payload[1];
    payload[0] = 0x12;
    payload[1] = 0x34;
    const new_word = (@as(u32, payload[0]) << 8) | payload[1];
    const replaced_partial = checksum.replace(old_partial, old_word, new_word);
    try std.testing.expectEqual(checksum.partial(&payload, 0), checksum.partial("", replaced_partial));

    var ipv4_header = [_]u8{
        0x45, 0x00, 0x00, 0x3c,
        0x1c, 0x46, 0x40, 0x00,
        0x40, 0x06, 0x00, 0x00,
        0xc0, 0xa8, 0x00, 0x01,
        0xc0, 0xa8, 0x00, 0xc7,
    };
    const old_checksum = checksum.compute(&ipv4_header);
    const old_total_length = (@as(u16, ipv4_header[2]) << 8) | ipv4_header[3];
    ipv4_header[2] = 0x00;
    ipv4_header[3] = 0x40;
    const new_total_length = (@as(u16, ipv4_header[2]) << 8) | ipv4_header[3];
    const diff = checksum.sub(new_total_length, old_total_length);
    const recomputed_length_checksum = checksum.compute(&ipv4_header);
    try std.testing.expectEqual(recomputed_length_checksum, checksum.replaceByDiff(old_checksum, diff));
    try std.testing.expectEqual(recomputed_length_checksum, checksum.replace2(old_checksum, old_total_length, new_total_length));

    ipv4_header[10] = 0;
    ipv4_header[11] = 0;
    const checksum_before_addr_change = checksum.compute(&ipv4_header);
    ipv4_header[12] = 0xc0;
    ipv4_header[13] = 0xa8;
    ipv4_header[14] = 0x00;
    ipv4_header[15] = 0x02;
    try std.testing.expectEqual(checksum.compute(&ipv4_header), checksum.replace4(checksum_before_addr_change, 0xc0a8_0001, 0xc0a8_0002));
}
