const std = @import("std");
const checksum = @import("checksum");
const fixtures = @import("phase6_checksum_vectors");

const Add16Case = struct {
    name: []const u8,
    sum: u16,
    addend: u16,
    expected_sum: u16,
};

const Sub16Case = struct {
    name: []const u8,
    sum: u16,
    addend: u16,
    expected_sum: u16,
};

const add16_cases = [_]Add16Case{
    .{ .name = "saturated plus one wraps with carry", .sum = 0xffff, .addend = 0x0001, .expected_sum = 0x0001 },
    .{ .name = "saturated plus zero stays saturated", .sum = 0xffff, .addend = 0x0000, .expected_sum = 0xffff },
    .{ .name = "saturated plus saturated preserves ones complement", .sum = 0xffff, .addend = 0xffff, .expected_sum = 0xffff },
};

const sub16_cases = [_]Sub16Case{
    .{ .name = "zero minus one borrows across ones complement", .sum = 0x0000, .addend = 0x0001, .expected_sum = 0xfffe },
    .{ .name = "subtracting a prior addend recovers the original word", .sum = 0x2345, .addend = 0x1111, .expected_sum = 0x1234 },
};

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [4096]u8 = undefined;
    var stdout = std.Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout.interface;

    for (fixtures.compute_cases) |case| {
        try writer.print("compute\t{s}\t0x{x:0>4}\n", .{ case.name, checksum.compute(case.bytes) });
    }

    for (fixtures.seeded_cases) |case| {
        try writer.print("partial\t{s}\t0x{x:0>8}\n", .{ case.name, checksum.partial(case.bytes, case.seed) });
    }

    for (fixtures.composition_cases) |case| {
        const prefix = checksum.partial(case.payload[0..case.split], 0);
        const suffix = checksum.partial(case.payload[case.split..], 0);
        const combined = checksum.blockAdd(prefix, suffix, case.split);
        try writer.print("compose\t{s}\t0x{x:0>8}\n", .{ case.name, checksum.partial("", combined) });
    }

    for (fixtures.pseudo_header_cases) |case| {
        const payload_partial = checksum.partial(case.payload, 0);
        try writer.print(
            "tcpudp-nofold\t{s}\t0x{x:0>8}\n",
            .{ case.name, checksum.tcpUdpNofold(payload_partial, case.saddr, case.daddr, @intCast(case.payload.len), case.proto) },
        );
    }

    for (fixtures.ipv6_pseudo_header_cases) |case| {
        const payload_partial = checksum.partial(case.payload, 0);
        try writer.print(
            "tcpudpv6-nofold\t{s}\t0x{x:0>8}\n",
            .{ case.name, checksum.tcpUdpV6Nofold(payload_partial, case.saddr, case.daddr, case.declared_len, case.proto) },
        );
    }

    for (fixtures.carry_discipline_cases) |case| {
        const partial = checksum.partial(case.bytes, case.seed);
        try writer.print("carry-discipline\t{s}\t0x{x:0>4}\n", .{ case.name, checksum.fold(partial) });
    }

    for (add16_cases) |case| {
        try writer.print("add16\t{s}\t0x{x:0>4}\n", .{ case.name, checksum.add16(case.sum, case.addend) });
    }

    for (sub16_cases) |case| {
        try writer.print("sub16\t{s}\t0x{x:0>4}\n", .{ case.name, checksum.sub16(case.sum, case.addend) });
    }

    var payload = [_]u8{ 0x70, 0x68, 0x61, 0x73, 0x65, 0x36 };
    const old_partial = checksum.partial(&payload, 0);
    const old_word = (@as(u32, payload[0]) << 8) | payload[1];
    payload[0] = 0x12;
    payload[1] = 0x34;
    const new_word = (@as(u32, payload[0]) << 8) | payload[1];
    try writer.print("replace\tpayload-word\t0x{x:0>8}\n", .{checksum.replace(old_partial, old_word, new_word)});

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
    try writer.print("replace-by-diff\tipv4-total-length\t0x{x:0>4}\n", .{checksum.replaceByDiff(old_checksum, diff)});
    try writer.print("replace2\tipv4-total-length\t0x{x:0>4}\n", .{checksum.replace2(old_checksum, old_total_length, new_total_length)});

    ipv4_header[10] = 0;
    ipv4_header[11] = 0;
    const checksum_before_addr_change = checksum.compute(&ipv4_header);
    const old_saddr: u32 = 0xc0a80001;
    const new_saddr: u32 = 0xc0a80002;
    try writer.print("replace4\tipv4-saddr\t0x{x:0>4}\n", .{checksum.replace4(checksum_before_addr_change, old_saddr, new_saddr)});

    try stdout.flush();
}
