const std = @import("std");
const checksum = @import("checksum");
const fixtures = @import("phase6_checksum_vectors");

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

test "kunit random-prefix parity stays stable on the helper surface" {
    for (fixtures.kunit_random_prefix_cases) |case| {
        const partial = checksum.partial(case.bytes, case.seed);

        try std.testing.expectEqual(case.expected_partial, partial);
        try std.testing.expectEqual(case.expected_compute, checksum.fold(partial));
        try std.testing.expectEqual(case.expected_compute, referenceFoldedChecksum(case.bytes, case.seed));
    }
}

test "from32to16, fold, and unfold stay aligned with the normalized checksum contract" {
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
        try std.testing.expectEqual(case.expected_from32to16, checksum.from32to16(case.sum));
        try std.testing.expectEqual(case.expected_from32to16, @as(u16, @truncate(foldCarry(case.sum))));
        try std.testing.expectEqual(~case.expected_from32to16, checksum.fold(case.sum));
        try std.testing.expectEqual(@as(u32, case.expected_from32to16), checksum.unfold(case.expected_from32to16));
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

        try std.testing.expectEqual(checksum.partial("", combined_partial), helper_partial);
        try std.testing.expectEqual(case.expected_compute, actual);
        try std.testing.expectEqual(referenceInternetChecksum(pseudo_and_payload[0..combined_len]), actual);
    }
}

test "IPv6 pseudo header accumulation matches the fixture-backed reference checksum" {
    for (fixtures.ipv6_pseudo_header_cases) |case| {
        const payload_partial = checksum.partial(case.payload, 0);

        var pseudo_header = [_]u8{0} ** 40;
        @memcpy(pseudo_header[0..16], &case.saddr);
        @memcpy(pseudo_header[16..32], &case.daddr);
        appendBigEndianU32(pseudo_header[32..36], case.declared_len);
        pseudo_header[39] = case.proto;

        const pseudo_partial = checksum.partial(&pseudo_header, 0);
        const combined_partial = checksum.blockAdd(pseudo_partial, payload_partial, pseudo_header.len);
        const helper_partial = checksum.tcpUdpV6Nofold(payload_partial, case.saddr, case.daddr, case.declared_len, case.proto);
        const actual = checksum.fold(helper_partial);

        var pseudo_and_payload: [96]u8 = undefined;
        const combined_len = pseudo_header.len + case.payload.len;
        @memcpy(pseudo_and_payload[0..pseudo_header.len], &pseudo_header);
        @memcpy(pseudo_and_payload[pseudo_header.len..combined_len], case.payload);

        try std.testing.expectEqual(checksum.partial("", combined_partial), helper_partial);
        try std.testing.expectEqual(case.expected_compute, actual);
        try std.testing.expectEqual(referenceInternetChecksum(pseudo_and_payload[0..combined_len]), actual);

        if (case.declared_len > 0xffff) {
            const truncated_partial = checksum.tcpUdpV6Nofold(payload_partial, case.saddr, case.daddr, case.declared_len & 0xffff, case.proto);
            try std.testing.expect(helper_partial != truncated_partial);
        }
    }
}

test "incremental checksum replacements match full recomputation" {
    var payload = [_]u8{ 0x70, 0x68, 0x61, 0x73, 0x65, 0x36 };
    const old_partial = checksum.partial(&payload, 0);
    const old_word = (@as(u32, payload[0]) << 8) | payload[1];
    payload[0] = 0x12;
    payload[1] = 0x34;
    const new_word = (@as(u32, payload[0]) << 8) | payload[1];

    try std.testing.expectEqual(checksum.partial(&payload, 0), checksum.partial("", checksum.replace(old_partial, old_word, new_word)));

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
    ipv4_header[10] = 0;
    ipv4_header[11] = 0;
    const diff = checksum.sub(new_total_length, old_total_length);

    try std.testing.expectEqual(checksum.compute(&ipv4_header), checksum.replaceByDiff(old_checksum, diff));
    try std.testing.expectEqual(checksum.compute(&ipv4_header), checksum.replace2(old_checksum, old_total_length, new_total_length));

    const checksum_before_addr_change = checksum.compute(&ipv4_header);
    const old_saddr: u32 = 0xc0a80001;
    const new_saddr: u32 = 0xc0a80002;
    ipv4_header[12] = 0xc0;
    ipv4_header[13] = 0xa8;
    ipv4_header[14] = 0x00;
    ipv4_header[15] = 0x02;
    ipv4_header[10] = 0;
    ipv4_header[11] = 0;

    try std.testing.expectEqual(checksum.compute(&ipv4_header), checksum.replace4(checksum_before_addr_change, old_saddr, new_saddr));
}

test "fixture-backed 16-bit carry helpers stay reviewable on the exported checksum surface" {
    for (fixtures.add16_cases) |case| {
        try std.testing.expectEqual(case.expected, checksum.add16(case.sum, case.addend));
    }

    for (fixtures.sub16_cases) |case| {
        try std.testing.expectEqual(case.expected, checksum.sub16(case.sum, case.addend));
    }
}

test "fixture inventory and representative checksum cases stay reviewable" {
    try std.testing.expectEqual(@as(usize, 5), fixtures.compute_cases.len);
    try std.testing.expectEqual(@as(usize, 2), fixtures.composition_cases.len);
    try std.testing.expectEqual(@as(usize, 3), fixtures.seeded_cases.len);
    try std.testing.expectEqual(@as(usize, 2), fixtures.add16_cases.len);
    try std.testing.expectEqual(@as(usize, 2), fixtures.sub16_cases.len);
    try std.testing.expectEqual(@as(usize, 1), fixtures.pseudo_header_cases.len);
    try std.testing.expectEqual(@as(usize, 3), fixtures.ipv6_pseudo_header_cases.len);
    try std.testing.expectEqual(@as(usize, 4), fixtures.carry_discipline_cases.len);
    try std.testing.expectEqual(@as(usize, 6), fixtures.kunit_random_prefix_cases.len);
    try std.testing.expectEqual(@as(usize, 2), fixtures.perf_cases.len);

    try std.testing.expectEqualStrings("ipv4 header", fixtures.compute_cases[2].name);
    try std.testing.expectEqual(@as(u16, 0x9c5d), fixtures.compute_cases[2].expected_compute);

    try std.testing.expectEqualStrings("saturated plus one wraps with carry", fixtures.add16_cases[0].name);
    try std.testing.expectEqual(@as(u16, 0x0001), fixtures.add16_cases[0].expected);

    try std.testing.expectEqualStrings("subtracting a prior addend recovers the original word", fixtures.sub16_cases[1].name);
    try std.testing.expectEqual(@as(u16, 0x1234), fixtures.sub16_cases[1].expected);

    try std.testing.expectEqualStrings("icmpv6 preserves upper declared length bits", fixtures.ipv6_pseudo_header_cases[2].name);
    try std.testing.expectEqual(@as(u32, 0x0001_0001), fixtures.ipv6_pseudo_header_cases[2].declared_len);
    try std.testing.expectEqual(@as(u16, 0x81ef), fixtures.ipv6_pseudo_header_cases[2].expected_compute);

    try std.testing.expectEqualStrings("two-byte no-carry seed stays one step below overflow", fixtures.carry_discipline_cases[3].name);
    try std.testing.expectEqual(@as(u32, 0xfbfb), fixtures.carry_discipline_cases[3].expected_partial);

    try std.testing.expectEqualStrings("64", fixtures.perf_cases[0].label);
    try std.testing.expectEqual(@as(usize, 20_000), fixtures.perf_cases[0].reps);
    try std.testing.expectEqual(@as(u16, 150), fixtures.perf_cases[0].max_slowdown_pct);

    try std.testing.expectEqualStrings("1501", fixtures.perf_cases[1].label);
    try std.testing.expectEqual(@as(u32, 0x1234_5678), fixtures.perf_cases[1].seed);
}

test "perf fixtures stay bounded and deterministic for checksum-only replay" {
    const expected = [_]struct {
        label: []const u8,
        len: usize,
        reps: usize,
        seed: u32,
        max_slowdown_pct: u16,
        expected_partial: u32,
        expected_folded: u16,
    }{
        .{
            .label = "64",
            .len = 64,
            .reps = 20_000,
            .seed = 0,
            .max_slowdown_pct = 150,
            .expected_partial = 0xa3b1,
            .expected_folded = 0x5c4e,
        },
        .{
            .label = "1501",
            .len = 1501,
            .reps = 4_000,
            .seed = 0x1234_5678,
            .max_slowdown_pct = 150,
            .expected_partial = 0x3ac5,
            .expected_folded = 0xc53a,
        },
    };

    try std.testing.expectEqual(expected.len, fixtures.perf_cases.len);

    for (expected, fixtures.perf_cases) |want, actual| {
        try std.testing.expectEqualStrings(want.label, actual.label);
        try std.testing.expectEqual(want.len, actual.len);
        try std.testing.expectEqual(want.reps, actual.reps);
        try std.testing.expectEqual(want.seed, actual.seed);
        try std.testing.expectEqual(want.max_slowdown_pct, actual.max_slowdown_pct);

        const payload = try std.testing.allocator.alloc(u8, actual.len);
        defer std.testing.allocator.free(payload);
        fixtures.fillPerfPayload(payload);

        const actual_partial = checksum.partial(payload, actual.seed);
        try std.testing.expectEqual(want.expected_partial, actual_partial);
        try std.testing.expectEqual(want.expected_partial, referencePartial(payload, actual.seed));
        try std.testing.expectEqual(want.expected_folded, checksum.fold(actual_partial));
        try std.testing.expectEqual(want.expected_folded, referenceFoldedChecksum(payload, actual.seed));
    }
}
