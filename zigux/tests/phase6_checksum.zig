const std = @import("std");
const checksum = @import("checksum");
const fixtures = @import("fixtures/phase6_checksum_vectors.zig");

fn referenceNormalizeWide(sum: u64) u32 {
    var value = sum;
    while ((value >> 16) != 0) {
        value = (value & 0xffff) + (value >> 16);
    }
    return @intCast(value);
}

fn referenceFrom32to16(sum: u32) u16 {
    var value = sum;
    while ((value >> 16) != 0) {
        value = (value & 0xffff) + (value >> 16);
    }
    return @intCast(value);
}

fn referenceFold(sum: u32) u16 {
    return ~referenceFrom32to16(sum);
}

fn referencePartial(bytes: []const u8, seed: u32) u32 {
    var acc: u64 = seed;
    var index: usize = 0;
    while (index + 1 < bytes.len) : (index += 2) {
        acc += (@as(u64, bytes[index]) << 8) | bytes[index + 1];
    }
    if (index < bytes.len) {
        acc += @as(u64, bytes[index]) << 8;
    }
    return referenceNormalizeWide(acc);
}

fn referenceCompute(bytes: []const u8) u16 {
    return referenceFold(referencePartial(bytes, 0));
}

fn expectFragmentedPartialMatchesWhole(payload: []const u8, split: usize, seed: u32) !void {
    const head = payload[0..split];
    const tail = payload[split..];
    const head_partial = checksum.partial(head, seed);
    const tail_partial = checksum.partial(tail, 0);
    const recomposed = checksum.blockAdd(head_partial, tail_partial, head.len);
    const recomposed_normalized = @as(u32, checksum.from32to16(recomposed));

    try std.testing.expectEqual(referencePartial(payload, seed), recomposed_normalized);
    try std.testing.expectEqual(checksum.partial(payload, seed), recomposed_normalized);
    if (seed == 0) {
        try std.testing.expectEqual(checksum.compute(payload), checksum.fold(recomposed));
    }
}

fn referencePseudoHeaderV4(sum: u32, saddr: u32, daddr: u32, len: u16, proto: u8) u32 {
    var result: u32 = referenceFrom32to16(sum);
    result = checksum.add(result, saddr >> 16);
    result = checksum.add(result, saddr & 0xffff);
    result = checksum.add(result, daddr >> 16);
    result = checksum.add(result, daddr & 0xffff);
    result = checksum.add(result, proto);
    result = checksum.add(result, len);
    return referenceFrom32to16(result);
}

fn readBigEndianU32(bytes: []const u8) u32 {
    const pair: *const [4]u8 = @ptrCast(bytes[0..4]);
    return std.mem.readInt(u32, pair, .big);
}

fn referencePseudoHeaderV6(sum: u32, saddr: *const [16]u8, daddr: *const [16]u8, len: u32, proto: u8) u32 {
    var result: u32 = referenceFrom32to16(sum);
    for (0..4) |index| {
        const offset = index * 4;
        result = checksum.add(result, readBigEndianU32(saddr[offset .. offset + 4]));
        result = checksum.add(result, readBigEndianU32(daddr[offset .. offset + 4]));
    }
    result = checksum.add(result, len >> 16);
    result = checksum.add(result, len & 0xffff);
    result = checksum.add(result, proto);
    return referenceFrom32to16(result);
}

test "phase 6 checksum compute parity matches local reference vectors" {
    for (fixtures.compute_cases) |case| {
        try std.testing.expectEqual(referenceCompute(case.payload), checksum.compute(case.payload));
    }
}

test "phase 6 checksum split composition stays aligned with seeded partial accumulation" {
    for (fixtures.seeded_cases) |case| {
        const prefix_sum = checksum.partial(case.prefix, case.seed);
        const split_sum = checksum.partial(case.suffix, prefix_sum);

        var joined: [64]u8 = undefined;
        @memcpy(joined[0..case.prefix.len], case.prefix);
        @memcpy(joined[case.prefix.len .. case.prefix.len + case.suffix.len], case.suffix);
        const full = joined[0 .. case.prefix.len + case.suffix.len];

        try std.testing.expectEqual(referencePartial(full, case.seed), split_sum);
        try std.testing.expectEqual(checksum.partial(full, case.seed), split_sum);
    }
}

test "phase 6 checksum fragment recomposition stays aligned across split boundaries" {
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

test "phase 6 checksum carry helpers preserve one's-complement replacement behavior" {
    const sum32: u32 = 0xffff_fffe;

    try std.testing.expectEqual(@as(u32, 1), checksum.add(sum32, 2));
    try std.testing.expectEqual(sum32, checksum.sub(checksum.add(sum32, 0xabcd), 0xabcd));

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

test "phase 6 checksum pseudo-header helpers match direct reference accumulation" {
    const payload = [_]u8{ 'p', 'h', 'a', 's', 'e', '6', '!' };
    const payload_partial = checksum.partial(&payload, 0);

    const v4_saddr: u32 = 0xc0a8_0001;
    const v4_daddr: u32 = 0xc0a8_00c7;
    const v4_proto: u8 = 17;
    try std.testing.expectEqual(
        referencePseudoHeaderV4(payload_partial, v4_saddr, v4_daddr, payload.len, v4_proto),
        checksum.tcpUdpNofold(payload_partial, v4_saddr, v4_daddr, payload.len, v4_proto),
    );
    try std.testing.expectEqual(
        referenceFold(referencePseudoHeaderV4(payload_partial, v4_saddr, v4_daddr, payload.len, v4_proto)),
        checksum.tcpUdpMagic(payload_partial, v4_saddr, v4_daddr, payload.len, v4_proto),
    );

    const v6_saddr = [_]u8{ 0x20, 0x01, 0x0d, 0xb8, 0x00, 0x00, 0x00, 0x01, 0xde, 0xad, 0xbe, 0xef, 0xca, 0xfe, 0xba, 0xbe };
    const v6_daddr = [_]u8{ 0x20, 0x01, 0x0d, 0xb8, 0x00, 0x00, 0x00, 0x02, 0xde, 0xad, 0xbe, 0xef, 0xca, 0xfe, 0xba, 0xbf };
    const v6_len: u32 = payload.len;
    const v6_proto: u8 = 58;
    try std.testing.expectEqual(
        referencePseudoHeaderV6(payload_partial, &v6_saddr, &v6_daddr, v6_len, v6_proto),
        checksum.tcpUdpV6Nofold(payload_partial, &v6_saddr, &v6_daddr, v6_len, v6_proto),
    );
    try std.testing.expectEqual(
        referenceFold(referencePseudoHeaderV6(payload_partial, &v6_saddr, &v6_daddr, v6_len, v6_proto)),
        checksum.tcpUdpV6Magic(payload_partial, &v6_saddr, &v6_daddr, v6_len, v6_proto),
    );
}

test "phase 6 checksum pseudo-header helpers keep high-length IPv6 carries visible" {
    const payload_seed = checksum.partial("phase6", 0);

    const v4_result = checksum.tcpUdpNofold(payload_seed, 0xc0a8_0001, 0xc0a8_00c7, 6, 17);
    try std.testing.expectEqual(referencePseudoHeaderV4(payload_seed, 0xc0a8_0001, 0xc0a8_00c7, 6, 17), v4_result);
    try std.testing.expectEqual(referenceFold(v4_result), checksum.tcpUdpMagic(payload_seed, 0xc0a8_0001, 0xc0a8_00c7, 6, 17));

    const v6_saddr = [_]u8{ 0x20, 0x01, 0x0d, 0xb8, 0x00, 0x00, 0x00, 0x01, 0xde, 0xad, 0xbe, 0xef, 0xca, 0xfe, 0xba, 0xbe };
    const v6_daddr = [_]u8{ 0x20, 0x01, 0x0d, 0xb8, 0x00, 0x00, 0x00, 0x02, 0xde, 0xad, 0xbe, 0xef, 0xca, 0xfe, 0xba, 0xbf };
    const v6_len: u32 = 0x0001_2345;
    const v6_proto: u8 = 58;
    const v6_result = checksum.tcpUdpV6Nofold(payload_seed, &v6_saddr, &v6_daddr, v6_len, v6_proto);
    try std.testing.expectEqual(referencePseudoHeaderV6(payload_seed, &v6_saddr, &v6_daddr, v6_len, v6_proto), v6_result);
    try std.testing.expectEqual(referenceFold(v6_result), checksum.tcpUdpV6Magic(payload_seed, &v6_saddr, &v6_daddr, v6_len, v6_proto));
}

test "phase 6 checksum fast-path fixtures stay aligned with focused correctness replay" {
    for (fixtures.fast_path_cases) |case| {
        const ihl_words: usize = case.header[0] & 0x0f;
        try std.testing.expectEqual(@as(u8, 4), case.header[0] >> 4);
        try std.testing.expectEqual(case.header.len, @as(usize, ihl_words * 4));
        try std.testing.expectEqual(@as(usize, 0), case.header.len & 3);
        try std.testing.expectEqual(referenceCompute(case.header), checksum.compute(case.header));
        try std.testing.expectEqual(checksum.compute(case.header), checksum.ipFastCsum(case.header));
        try std.testing.expectEqual(checksum.compute(case.header), checksum.ipFastCsumIhl(case.header, ihl_words));
        try std.testing.expectEqual(checksum.ipFastCsum(case.header), checksum.ipFastCsumIhl(case.header, ihl_words));
    }
}

test "phase 6 checksum negate stays involutive across representative carry edges" {
    const cases = [_]struct {
        sum: u32,
        expected: u32,
    }{
        .{ .sum = 0x0000_0000, .expected = 0x0000_0000 },
        .{ .sum = 0x0000_0001, .expected = 0xffff_ffff },
        .{ .sum = 0x0001_0000, .expected = 0xffff_0000 },
        .{ .sum = 0x1234_5678, .expected = 0xedcb_a988 },
        .{ .sum = 0xffff_ffff, .expected = 0x0000_0001 },
        .{ .sum = 0xdead_bef0, .expected = 0x2152_4110 },
    };

    for (cases) |case| {
        try std.testing.expectEqual(case.expected, checksum.negate(case.sum));
        try std.testing.expectEqual(case.sum, checksum.negate(checksum.negate(case.sum)));
    }
}

test "phase 6 checksum incremental helpers preserve odd-offset carry discipline" {
    const seed = 0x1357_9bdf;
    const fragment = 0x2468_ace0;

    try std.testing.expectEqual(fragment, checksum.shift(fragment, 0));
    try std.testing.expectEqual(std.math.rotr(u32, fragment, 8), checksum.shift(fragment, 1));
    try std.testing.expectEqual(fragment, checksum.shift(fragment, 2));
    try std.testing.expectEqual(std.math.rotr(u32, fragment, 8), checksum.shift(fragment, 3));

    const even_added = checksum.blockAdd(seed, fragment, 0);
    const odd_added = checksum.blockAdd(seed, fragment, 1);

    try std.testing.expectEqual(checksum.add(seed, fragment), even_added);
    try std.testing.expectEqual(checksum.add(seed, std.math.rotr(u32, fragment, 8)), odd_added);
    try std.testing.expectEqual(seed, checksum.blockSub(even_added, fragment, 0));
    try std.testing.expectEqual(seed, checksum.blockSub(odd_added, fragment, 1));

    try std.testing.expectEqual(fragment, checksum.shift(fragment, 256));
    try std.testing.expectEqual(std.math.rotr(u32, fragment, 8), checksum.shift(fragment, 255));
    try std.testing.expectEqual(checksum.add(seed, fragment), checksum.blockAdd(seed, fragment, 256));
    try std.testing.expectEqual(
        checksum.add(seed, std.math.rotr(u32, fragment, 8)),
        checksum.blockAdd(seed, fragment, 255),
    );
    try std.testing.expectEqual(seed, checksum.blockSub(checksum.blockAdd(seed, fragment, 255), fragment, 255));

    const negate_cases = [_]struct {
        sum: u32,
        expected: u32,
    }{
        .{ .sum = 0x0000_0000, .expected = 0x0000_0000 },
        .{ .sum = 0x0000_0001, .expected = 0x0000_0001 },
        .{ .sum = 0x0001_0000, .expected = 0x0000_0001 },
        .{ .sum = 0x1234_5678, .expected = 0x0000_0001 },
        .{ .sum = 0xffff_ffff, .expected = 0x0000_0001 },
    };

    for (negate_cases) |case| {
        try std.testing.expectEqual(case.expected, checksum.add(case.sum, checksum.negate(case.sum)));
    }

    const sums = [_]u32{
        0,
        1,
        0x0001_0000,
        0x1234_5678,
        0xffff_ffff,
    };
    for (sums) |sum| {
        try std.testing.expectEqual(checksum.from32to16(sum), checksum.unfold(~checksum.fold(sum)));
    }

    for (fixtures.carry16_cases) |case| {
        try std.testing.expectEqual(case.expected_add, checksum.add16(case.sum, case.addend));
        try std.testing.expectEqual(case.expected_sub, checksum.sub16(case.sum, case.addend));
    }
}
