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

const Carry16Case = struct {
    name: []const u8,
    sum: u16,
    addend: u16,
};

const FastPathCase = struct {
    name: []const u8,
    header: []const u8,
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

const carry16_cases = [_]Carry16Case{
    .{ .name = "zero-plus-zero", .sum = 0x0000, .addend = 0x0000 },
    .{ .name = "saturated-plus-one", .sum = 0xffff, .addend = 0x0001 },
    .{ .name = "halfword-wrap", .sum = 0x7fff, .addend = 0x8000 },
    .{ .name = "near-wrap-plus-three", .sum = 0xfffe, .addend = 0x0003 },
};

const fast_path_cases = [_]FastPathCase{
    .{ .name = "IPV4_20B", .header = &[_]u8{
        0x45, 0x00, 0x00, 0x3c,
        0x1c, 0x46, 0x40, 0x00,
        0x40, 0x06, 0x00, 0x00,
        0xc0, 0xa8, 0x00, 0x01,
        0xc0, 0xa8, 0x00, 0xc7,
    } },
    .{ .name = "IPV4_20B_UPDATED", .header = &[_]u8{
        0x45, 0x00, 0x00, 0x40,
        0x1c, 0x46, 0x40, 0x00,
        0x3f, 0x11, 0x00, 0x00,
        0xc0, 0xa8, 0x00, 0x02,
        0xc0, 0xa8, 0x00, 0xc7,
    } },
    .{ .name = "IPV4_24B", .header = &[_]u8{
        0x46, 0x00, 0x00, 0x30,
        0x12, 0x34, 0x20, 0x00,
        0x40, 0x11, 0x00, 0x00,
        0xc0, 0xa8, 0x01, 0x01,
        0xc0, 0xa8, 0x01, 0x02,
        0x01, 0x01, 0x00, 0x00,
    } },
    .{ .name = "IPV4_60B", .header = &[_]u8{
        0x4f, 0x00, 0x00, 0x3c,
        0xbe, 0xef, 0x40, 0x00,
        0x40, 0x11, 0x00, 0x00,
        0xc0, 0x00, 0x02, 0x01,
        0xc6, 0x33, 0x64, 0x07,
        0x01, 0x01, 0x94, 0x04,
        0xde, 0xad, 0xbe, 0xef,
        0xca, 0xfe, 0xba, 0xbe,
        0x11, 0x22, 0x33, 0x44,
        0x55, 0x66, 0x77, 0x88,
        0x99, 0xaa, 0xbb, 0xcc,
        0xdd, 0xee, 0xf0, 0x0d,
        0x10, 0x20, 0x30, 0x40,
        0x50, 0x60, 0x70, 0x80,
        0x90, 0xa0, 0xb0, 0xc0,
    } },
};

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [4096]u8 = undefined;
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

    for (carry16_cases) |case| {
        try writer.print("add16\t{s}\t0x{x:0>4}\n", .{ case.name, checksum.add16(case.sum, case.addend) });
        try writer.print("sub16\t{s}\t0x{x:0>4}\n", .{ case.name, checksum.sub16(case.sum, case.addend) });
    }

    for (fast_path_cases) |case| {
        const ihl_words: usize = case.header[0] & 0x0f;
        try writer.print("ip-fast-csum\t{s}\t0x{x:0>4}\n", .{ case.name, checksum.ipFastCsum(case.header) });
        try writer.print("ip-fast-csum-ihl\t{s}\t0x{x:0>4}\n", .{ case.name, checksum.ipFastCsumIhl(case.header, ihl_words) });
    }

    const negate_cases = [_]struct {
        name: []const u8,
        value: u32,
    }{
        .{ .name = "zero", .value = 0x0000_0000 },
        .{ .name = "unit", .value = 0x0000_0001 },
        .{ .name = "saturated", .value = 0xffff_ffff },
        .{ .name = "carry-heavy", .value = 0xdead_bef0 },
    };
    for (negate_cases) |case| {
        try writer.print("negate\t{s}\t0x{x:0>8}\n", .{ case.name, checksum.negate(case.value) });
    }

    const from64_cases = [_]struct {
        name: []const u8,
        value: u64,
    }{
        .{ .name = "zero", .value = 0x0000_0000_0000_0000 },
        .{ .name = "single carry", .value = 0x0000_0001_0000_0000 },
        .{ .name = "saturated plus one", .value = 0xffff_ffff_0000_0001 },
        .{ .name = "mixed words", .value = 0x1234_5678_9abc_def0 },
    };
    for (from64_cases) |case| {
        try writer.print("from64to32\t{s}\t0x{x:0>8}\n", .{ case.name, checksum.from64to32(case.value) });
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
