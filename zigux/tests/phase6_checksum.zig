const std = @import("std");
const checksum = @import("checksum");
const fixtures = @import("phase6_checksum_vectors");

const Add16Case = struct {
    sum: u16,
    addend: u16,
    expected: u16,
};

const Sub16Case = struct {
    sum: u16,
    addend: u16,
    expected: u16,
};

const add16_cases = [_]Add16Case{
    .{ .sum = 0xffff, .addend = 0x0001, .expected = 0x0001 },
    .{ .sum = 0xffff, .addend = 0x0000, .expected = 0xffff },
    .{ .sum = 0xffff, .addend = 0xffff, .expected = 0xffff },
};

const sub16_cases = [_]Sub16Case{
    .{ .sum = 0x0000, .addend = 0x0001, .expected = 0xfffe },
    .{ .sum = 0x2345, .addend = 0x1111, .expected = 0x1234 },
};

test "phase6 checksum compute cases match the shared fixture corpus" {
    for (fixtures.compute_cases) |case| {
        try std.testing.expectEqual(case.expected_sum, checksum.compute(case.bytes));
    }
}

test "phase6 checksum seeded partial cases match the shared fixture corpus" {
    for (fixtures.seeded_cases) |case| {
        try std.testing.expectEqual(case.expected_sum, checksum.partial(case.bytes, case.seed));
    }
}

test "phase6 checksum composition cases preserve split parity through blockAdd" {
    for (fixtures.composition_cases) |case| {
        const prefix = checksum.partial(case.payload[0..case.split], 0);
        const suffix = checksum.partial(case.payload[case.split..], 0);
        const combined = checksum.blockAdd(prefix, suffix, case.split);
        try std.testing.expectEqual(case.expected_sum, checksum.partial("", combined));
    }
}

test "phase6 checksum pseudo header helpers match the shared fixture corpus" {
    for (fixtures.pseudo_header_cases) |case| {
        const payload_partial = checksum.partial(case.payload, 0);
        try std.testing.expectEqual(
            case.expected_sum,
            checksum.tcpUdpNofold(payload_partial, case.saddr, case.daddr, @intCast(case.payload.len), case.proto),
        );
    }

    for (fixtures.ipv6_pseudo_header_cases) |case| {
        const payload_partial = checksum.partial(case.payload, 0);
        try std.testing.expectEqual(
            case.expected_sum,
            checksum.tcpUdpV6Nofold(payload_partial, case.saddr, case.daddr, case.declared_len, case.proto),
        );
    }
}

test "phase6 checksum carry discipline cases match the shared fixture corpus" {
    for (fixtures.carry_discipline_cases) |case| {
        try std.testing.expectEqual(case.expected_fold, checksum.fold(checksum.partial(case.bytes, case.seed)));
    }
}

test "phase6 checksum direct carry helpers preserve ones-complement semantics" {
    for (add16_cases) |case| {
        try std.testing.expectEqual(case.expected, checksum.add16(case.sum, case.addend));
    }
    for (sub16_cases) |case| {
        try std.testing.expectEqual(case.expected, checksum.sub16(case.sum, case.addend));
    }
}

test "phase6 checksum replacement helpers match the documented IPv4 and payload updates" {
    var payload = [_]u8{ 0x70, 0x68, 0x61, 0x73, 0x65, 0x36 };
    const old_partial = checksum.partial(&payload, 0);
    const old_word = (@as(u32, payload[0]) << 8) | payload[1];
    payload[0] = 0x12;
    payload[1] = 0x34;
    const new_word = (@as(u32, payload[0]) << 8) | payload[1];
    try std.testing.expectEqual(@as(u32, 0xffffd8dd), checksum.replace(old_partial, old_word, new_word));

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
    try std.testing.expectEqual(@as(u16, 0x9c59), checksum.replaceByDiff(old_checksum, diff));
    try std.testing.expectEqual(@as(u16, 0x9c59), checksum.replace2(old_checksum, old_total_length, new_total_length));

    ipv4_header[10] = 0;
    ipv4_header[11] = 0;
    const checksum_before_addr_change = checksum.compute(&ipv4_header);
    try std.testing.expectEqual(@as(u16, 0x9c58), checksum.replace4(checksum_before_addr_change, 0xc0a80001, 0xc0a80002));
}

test "phase6 checksum low-level transforms keep the documented carry and offset behavior" {
    try std.testing.expectEqual(@as(u32, 0x44112233), checksum.shift(0x11223344, 1));
    try std.testing.expectEqual(@as(u32, 0x11223344), checksum.shift(0x11223344, 2));
    try std.testing.expectEqual(@as(u16, 0x0001), checksum.from32To16(0x00010000));
    try std.testing.expectEqual(@as(u32, 0xbeef), checksum.unfold(0xbeef));
}
