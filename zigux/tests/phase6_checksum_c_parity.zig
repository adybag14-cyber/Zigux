const std = @import("std");
const checksum = @import("checksum");

const ComputeCase = struct {
    name: []const u8,
    bytes: []const u8,
};

const SeededCase = struct {
    name: []const u8,
    bytes: []const u8,
    seed: u32,
};

const CompositionCase = struct {
    name: []const u8,
    payload: []const u8,
    split: usize,
};

const PseudoHeaderCase = struct {
    name: []const u8,
    payload: []const u8,
    saddr: u32,
    daddr: u32,
    proto: u8,
};

const compute_cases = [_]ComputeCase{
    .{ .name = "empty", .bytes = "" },
    .{ .name = "two-byte word", .bytes = &[_]u8{ 0x00, 0x01 } },
    .{ .name = "ipv4 header", .bytes = &[_]u8{
        0x45, 0x00, 0x00, 0x3c,
        0x1c, 0x46, 0x40, 0x00,
        0x40, 0x06, 0x00, 0x00,
        0xc0, 0xa8, 0x00, 0x01,
        0xc0, 0xa8, 0x00, 0xc7,
    } },
    .{ .name = "odd payload", .bytes = "abcde" },
    .{ .name = "carry-heavy payload", .bytes = &[_]u8{ 0xff, 0xff, 0xff, 0xff, 0x7f } },
};

const seeded_cases = [_]SeededCase{
    .{ .name = "odd payload with saturated seed", .bytes = "abcde", .seed = 0xffff },
    .{ .name = "carry-heavy payload with unfolded seed", .bytes = &[_]u8{ 0xff, 0xff, 0xff, 0xff, 0x7f }, .seed = 0x1fffe },
    .{ .name = "ipv4 fragment with arbitrary seed", .bytes = &[_]u8{ 0x45, 0x00, 0x00, 0x3c, 0x1c, 0x46, 0x40 }, .seed = 0xabcd },
};

const composition_cases = [_]CompositionCase{
    .{ .name = "even split", .payload = "checksum fragments keep their carry", .split = 20 },
    .{ .name = "odd split", .payload = "checksum fragments keep their carry", .split = 21 },
};

const pseudo_header_cases = [_]PseudoHeaderCase{
    .{ .name = "udp pseudo header", .payload = "zigux checksum", .saddr = 0xc0a8_0001, .daddr = 0xc0a8_00c7, .proto = 17 },
};

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [2048]u8 = undefined;
    var stdout = std.Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout.interface;

    for (compute_cases) |case| {
        try writer.print("compute\t{s}\t0x{x:0>4}\n", .{ case.name, checksum.compute(case.bytes) });
    }

    for (seeded_cases) |case| {
        try writer.print("partial\t{s}\t0x{x:0>8}\n", .{ case.name, checksum.partial(case.bytes, case.seed) });
    }

    for (composition_cases) |case| {
        const prefix = checksum.partial(case.payload[0..case.split], 0);
        const suffix = checksum.partial(case.payload[case.split..], 0);
        const combined = checksum.blockAdd(prefix, suffix, case.split);
        try writer.print("compose\t{s}\t0x{x:0>8}\n", .{ case.name, checksum.partial("", combined) });
    }

    for (pseudo_header_cases) |case| {
        const payload_partial = checksum.partial(case.payload, 0);
        try writer.print(
            "tcpudp-nofold\t{s}\t0x{x:0>8}\n",
            .{ case.name, checksum.tcpUdpNofold(payload_partial, case.saddr, case.daddr, @intCast(case.payload.len), case.proto) },
        );
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
