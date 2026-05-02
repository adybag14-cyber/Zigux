const std = @import("std");
const hexdump = @import("hexdump");
const fixtures = @import("phase6_hexdump_vectors");

fn printDumpCase(writer: anytype, case: fixtures.ParityCase) !void {
    var linebuf: [fixtures.test_hexdump_buf_size]u8 = undefined;
    const required = hexdump.hexDumpToBuffer(
        fixtures.data_b[0..case.len],
        case.rowsize,
        case.groupsize,
        linebuf[0..],
        case.ascii,
    );
    try writer.print("dump\t{s}\t{}\t{s}\n", .{
        case.name,
        required,
        std.mem.sliceTo(linebuf[0..], 0),
    });
}

fn printOverflowCase(writer: anytype, case: fixtures.OverflowCase) !void {
    var linebuf: [fixtures.test_hexdump_buf_size]u8 =
        [_]u8{fixtures.fill_char} ** fixtures.test_hexdump_buf_size;
    const required = hexdump.hexDumpToBuffer(
        fixtures.data_b[0..case.len],
        case.rowsize,
        case.groupsize,
        linebuf[0..case.buflen],
        case.ascii,
    );
    const visible = if (case.buflen == 0) "" else std.mem.sliceTo(linebuf[0..], 0);
    try writer.print("overflow\t{s}\t{}\t{s}\n", .{
        case.name,
        required,
        visible,
    });
}

pub fn main() !void {
    var stdout_buffer: [8192]u8 = undefined;
    var stdout = std.fs.File.stdout().writer(&stdout_buffer);
    const writer = &stdout.interface;

    try writer.print("hexToBin\t0\t{}\n", .{hexdump.hexToBin('0')});
    try writer.print("hexToBin\t9\t{}\n", .{hexdump.hexToBin('9')});
    try writer.print("hexToBin\tA\t{}\n", .{hexdump.hexToBin('A')});
    try writer.print("hexToBin\tF\t{}\n", .{hexdump.hexToBin('F')});
    try writer.print("hexToBin\ta\t{}\n", .{hexdump.hexToBin('a')});
    try writer.print("hexToBin\tf\t{}\n", .{hexdump.hexToBin('f')});
    try writer.print("hexToBin\tg\t{}\n", .{hexdump.hexToBin('g')});

    var decoded: [4]u8 = undefined;
    try hexdump.hex2bin(decoded[0..], "Be32dB7b");
    var decoded_text: [8]u8 = undefined;
    _ = try hexdump.bin2hex(decoded_text[0..], decoded[0..]);
    try writer.print("hex2bin\tmixed-case\t{s}\n", .{decoded_text[0..]});

    var lower_text: [8]u8 = undefined;
    const lower = try hexdump.bin2hex(lower_text[0..], fixtures.data_b[0..4]);
    try writer.print("bin2hex\tlower\t{s}\n", .{lower});

    var upper_text: [8]u8 = undefined;
    const upper = try hexdump.bin2hexUpper(upper_text[0..], fixtures.data_b[0..4]);
    try writer.print("bin2hex\tupper\t{s}\n", .{upper});

    var append_text: [12]u8 = [_]u8{'#'} ** 12;
    var rest = try hexdump.bin2hexAppend(append_text[0..], fixtures.data_b[0..2]);
    rest = try hexdump.bin2hexAppendUpper(rest, fixtures.data_b[2..4]);
    _ = rest;
    try writer.print("bin2hex\tappend-mixed\t{s}\n", .{append_text[0..8]});

    try writer.print("length\tascii rowsize-16 group-1\t{}\n", .{
        hexdump.hexDumpLineLength(16, 16, 1, true),
    });
    try writer.print("length\tascii rowsize-16 group-4\t{}\n", .{
        hexdump.hexDumpLineLength(16, 16, 4, true),
    });
    try writer.print("length\tnormalized rowsize and groupsize fallback\t{}\n", .{
        hexdump.hexDumpLineLength(16, 7, 3, true),
    });
    try writer.print("length\tplain rowsize-16 group-8\t{}\n", .{
        hexdump.hexDumpLineLength(16, 16, 8, false),
    });

    for (fixtures.parity_cases) |case| {
        if (std.mem.eql(u8, case.name, "plain rowsize-16 group-1") or
            std.mem.eql(u8, case.name, "ascii rowsize-16 group-1") or
            std.mem.eql(u8, case.name, "plain rowsize-16 group-4") or
            std.mem.eql(u8, case.name, "ascii rowsize-16 group-4") or
            std.mem.eql(u8, case.name, "ascii rowsize-16 group-8") or
            std.mem.eql(u8, case.name, "ascii rowsize-32 group-2") or
            std.mem.eql(u8, case.name, "normalized rowsize and groupsize fallback") or
            std.mem.eql(u8, case.name, "plain rowsize-16 group-8"))
        {
            try printDumpCase(writer, case);
        }
    }

    for (fixtures.overflow_cases) |case| {
        try printOverflowCase(writer, case);
    }

    try stdout.flush();
}
