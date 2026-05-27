const std = @import("std");
const hexdump = @import("hexdump");

const data = [_]u8{
    0xbe, 0x32, 0xdb, 0x7b, 0x0a, 0x18, 0x93, 0xb2,
    0x70, 0xba, 0xc4, 0x24, 0x7d, 0x83, 0x34, 0x9b,
    0xa6, 0x9c, 0x31, 0xad, 0x9c, 0x0f, 0xac, 0xe9,
    0x4c, 0xd1, 0x19, 0x99, 0x43, 0xb1, 0xaf, 0x0c,
};

fn writeHex2binCase(writer: *std.Io.Writer, label: []const u8, src: []const u8) !void {
    var decoded: [4]u8 = undefined;
    hexdump.hex2bin(decoded[0..], src) catch |err| {
        try writer.print("hex2bin\t{s}\t{s}\n", .{ label, @errorName(err) });
        return;
    };

    var encoded: [8]u8 = undefined;
    const text = try hexdump.bin2hex(encoded[0..], decoded[0..]);
    try writer.print("hex2bin\t{s}\t{s}\n", .{ label, text });
}

fn writeDumpCase(
    writer: *std.Io.Writer,
    label: []const u8,
    len: usize,
    rowsize: usize,
    groupsize: usize,
    ascii: bool,
) !void {
    var line: [131]u8 = undefined;
    const required = hexdump.hexDumpToBuffer(data[0..len], rowsize, groupsize, line[0..], ascii);
    const visible = std.mem.sliceTo(line[0..], 0);
    try writer.print("dump\t{s}\t{d}\t{s}\n", .{ label, required, visible });
}

fn writeTruncatedDumpCase(
    writer: *std.Io.Writer,
    label: []const u8,
    len: usize,
    rowsize: usize,
    groupsize: usize,
    ascii: bool,
    buflen: usize,
) !void {
    var line: [131]u8 = [_]u8{0xaa} ** 131;
    const required = hexdump.hexDumpToBuffer(data[0..len], rowsize, groupsize, line[0..buflen], ascii);
    const visible = if (buflen == 0) "" else std.mem.sliceTo(line[0..buflen], 0);
    try writer.print("dump-trunc\t{s}\t{d}\t{s}\n", .{ label, required, visible });
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [8192]u8 = undefined;
    var stdout = std.Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout.interface;

    try writer.print("hex-to-bin\tzero\t{d}\n", .{hexdump.hexToBin('0')});
    try writer.print("hex-to-bin\tlower-f\t{d}\n", .{hexdump.hexToBin('f')});
    try writer.print("hex-to-bin\tupper-B\t{d}\n", .{hexdump.hexToBin('B')});
    try writer.print("hex-to-bin\tinvalid-x\t{d}\n", .{hexdump.hexToBin('x')});

    try writeHex2binCase(writer, "lower", "be32db7b");
    try writeHex2binCase(writer, "mixed", "bE32Db7B");
    try writeHex2binCase(writer, "invalid-length", "be32db");
    try writeHex2binCase(writer, "invalid-digit", "be32dz7b");

    var lower: [8]u8 = undefined;
    const lower_text = try hexdump.bin2hex(lower[0..], data[0..4]);
    try writer.print("bin2hex\tlower\t{s}\n", .{lower_text});

    var upper: [8]u8 = undefined;
    const upper_text = try hexdump.bin2hexUpper(upper[0..], data[0..4]);
    try writer.print("bin2hex-upper\tupper\t{s}\n", .{upper_text});

    try writeDumpCase(writer, "plain-16-g1", 16, 16, 1, false);
    try writeDumpCase(writer, "ascii-16-g4", 16, 16, 4, true);
    try writeDumpCase(writer, "ascii-32-g2", 32, 32, 2, true);
    try writeDumpCase(writer, "normalized-fallback", 12, 99, 3, true);
    try writeDumpCase(writer, "uneven-group-fallback", 9, 32, 4, false);

    try writeTruncatedDumpCase(writer, "ascii-32-g2-buf8", 32, 32, 2, true, 8);
    try writeTruncatedDumpCase(writer, "ascii-32-g2-buf113", 32, 32, 2, true, 113);
    try writeTruncatedDumpCase(writer, "ascii-16-g4-buf0", 16, 16, 4, true, 0);

    try writer.print(
        "required\tascii-32-g2\t{d}\n",
        .{hexdump.hexDumpToBuffer(data[0..32], 32, 2, &[_]u8{}, true)},
    );
    try writer.print(
        "required\tnormalized-fallback\t{d}\n",
        .{hexdump.hexDumpToBuffer(data[0..12], 99, 3, &[_]u8{}, true)},
    );
    try stdout.flush();
}
