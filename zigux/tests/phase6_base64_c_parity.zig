const std = @import("std");
const base64 = @import("base64");
const fixtures = @import("fixtures/phase6_base64_vectors.zig");

const EncodeCase = struct {
    variant: base64.Variant,
    padding: bool,
    input: []const u8,
};

const DecodeCase = struct {
    variant: base64.Variant,
    padding: bool,
    input: []const u8,
};

const InvalidCase = struct {
    variant: base64.Variant,
    padding: bool,
    input: []const u8,
};

const encode_cases = [_]EncodeCase{
    .{ .variant = .std, .padding = fixtures.standard_cases[0].padding, .input = fixtures.standard_cases[0].input },
    .{ .variant = .std, .padding = fixtures.standard_cases[1].padding, .input = fixtures.standard_cases[1].input },
    .{ .variant = .std, .padding = fixtures.standard_cases[2].padding, .input = fixtures.standard_cases[2].input },
    .{ .variant = .std, .padding = fixtures.standard_cases[17].padding, .input = fixtures.standard_cases[17].input },
    .{ .variant = .std, .padding = fixtures.standard_cases[7].padding, .input = fixtures.standard_cases[7].input },
    .{ .variant = fixtureVariant(fixtures.variant_cases[2].variant_name), .padding = fixtures.variant_cases[2].padding, .input = fixtures.variant_cases[2].input },
    .{ .variant = fixtureVariant(fixtures.variant_cases[3].variant_name), .padding = fixtures.variant_cases[3].padding, .input = fixtures.variant_cases[3].input },
    .{ .variant = fixtureVariant(fixtures.variant_cases[8].variant_name), .padding = fixtures.variant_cases[8].padding, .input = fixtures.variant_cases[8].input },
    .{ .variant = fixtureVariant(fixtures.variant_cases[9].variant_name), .padding = fixtures.variant_cases[9].padding, .input = fixtures.variant_cases[9].input },
    .{ .variant = fixtureVariant(fixtures.variant_cases[14].variant_name), .padding = fixtures.variant_cases[14].padding, .input = fixtures.variant_cases[14].input },
    .{ .variant = fixtureVariant(fixtures.variant_cases[15].variant_name), .padding = fixtures.variant_cases[15].padding, .input = fixtures.variant_cases[15].input },
    .{ .variant = fixtureVariant(fixtures.variant_cases[4].variant_name), .padding = fixtures.variant_cases[4].padding, .input = fixtures.variant_cases[4].input },
    .{ .variant = fixtureVariant(fixtures.variant_cases[5].variant_name), .padding = fixtures.variant_cases[5].padding, .input = fixtures.variant_cases[5].input },
    .{ .variant = fixtureVariant(fixtures.variant_cases[10].variant_name), .padding = fixtures.variant_cases[10].padding, .input = fixtures.variant_cases[10].input },
    .{ .variant = fixtureVariant(fixtures.variant_cases[11].variant_name), .padding = fixtures.variant_cases[11].padding, .input = fixtures.variant_cases[11].input },
    .{ .variant = fixtureVariant(fixtures.variant_cases[16].variant_name), .padding = fixtures.variant_cases[16].padding, .input = fixtures.variant_cases[16].input },
    .{ .variant = fixtureVariant(fixtures.variant_cases[17].variant_name), .padding = fixtures.variant_cases[17].padding, .input = fixtures.variant_cases[17].input },
};

const decode_cases = [_]DecodeCase{
    .{ .variant = .std, .padding = fixtures.standard_decode_cases[0].padding, .input = fixtures.standard_decode_cases[0].input },
    .{ .variant = .std, .padding = fixtures.standard_decode_cases[1].padding, .input = fixtures.standard_decode_cases[1].input },
    .{ .variant = .std, .padding = fixtures.standard_decode_cases[2].padding, .input = fixtures.standard_decode_cases[2].input },
    .{ .variant = .std, .padding = fixtures.standard_decode_cases[16].padding, .input = fixtures.standard_decode_cases[16].input },
    .{ .variant = .std, .padding = fixtures.standard_decode_cases[7].padding, .input = fixtures.standard_decode_cases[7].input },
    .{ .variant = fixtureVariant(fixtures.variant_decode_cases[2].variant_name), .padding = fixtures.variant_decode_cases[2].padding, .input = fixtures.variant_decode_cases[2].input },
    .{ .variant = fixtureVariant(fixtures.variant_decode_cases[3].variant_name), .padding = fixtures.variant_decode_cases[3].padding, .input = fixtures.variant_decode_cases[3].input },
    .{ .variant = fixtureVariant(fixtures.variant_decode_cases[8].variant_name), .padding = fixtures.variant_decode_cases[8].padding, .input = fixtures.variant_decode_cases[8].input },
    .{ .variant = fixtureVariant(fixtures.variant_decode_cases[9].variant_name), .padding = fixtures.variant_decode_cases[9].padding, .input = fixtures.variant_decode_cases[9].input },
    .{ .variant = fixtureVariant(fixtures.variant_decode_cases[14].variant_name), .padding = fixtures.variant_decode_cases[14].padding, .input = fixtures.variant_decode_cases[14].input },
    .{ .variant = fixtureVariant(fixtures.variant_decode_cases[15].variant_name), .padding = fixtures.variant_decode_cases[15].padding, .input = fixtures.variant_decode_cases[15].input },
    .{ .variant = fixtureVariant(fixtures.variant_decode_cases[4].variant_name), .padding = fixtures.variant_decode_cases[4].padding, .input = fixtures.variant_decode_cases[4].input },
    .{ .variant = fixtureVariant(fixtures.variant_decode_cases[5].variant_name), .padding = fixtures.variant_decode_cases[5].padding, .input = fixtures.variant_decode_cases[5].input },
    .{ .variant = fixtureVariant(fixtures.variant_decode_cases[10].variant_name), .padding = fixtures.variant_decode_cases[10].padding, .input = fixtures.variant_decode_cases[10].input },
    .{ .variant = fixtureVariant(fixtures.variant_decode_cases[11].variant_name), .padding = fixtures.variant_decode_cases[11].padding, .input = fixtures.variant_decode_cases[11].input },
    .{ .variant = fixtureVariant(fixtures.variant_decode_cases[16].variant_name), .padding = fixtures.variant_decode_cases[16].padding, .input = fixtures.variant_decode_cases[16].input },
    .{ .variant = fixtureVariant(fixtures.variant_decode_cases[17].variant_name), .padding = fixtures.variant_decode_cases[17].padding, .input = fixtures.variant_decode_cases[17].input },
};

const invalid_cases = [_]InvalidCase{
    .{ .variant = fixtureVariant(fixtures.invalid_decode_cases[0].variant_name), .padding = fixtures.invalid_decode_cases[0].padding, .input = fixtures.invalid_decode_cases[0].input },
    .{ .variant = fixtureVariant(fixtures.invalid_decode_cases[2].variant_name), .padding = fixtures.invalid_decode_cases[2].padding, .input = fixtures.invalid_decode_cases[2].input },
    .{ .variant = fixtureVariant(fixtures.invalid_decode_cases[11].variant_name), .padding = fixtures.invalid_decode_cases[11].padding, .input = fixtures.invalid_decode_cases[11].input },
    .{ .variant = fixtureVariant(fixtures.invalid_decode_cases[6].variant_name), .padding = fixtures.invalid_decode_cases[6].padding, .input = fixtures.invalid_decode_cases[6].input },
    .{ .variant = fixtureVariant(fixtures.invalid_decode_cases[14].variant_name), .padding = fixtures.invalid_decode_cases[14].padding, .input = fixtures.invalid_decode_cases[14].input },
    .{ .variant = fixtureVariant(fixtures.invalid_decode_cases[15].variant_name), .padding = fixtures.invalid_decode_cases[15].padding, .input = fixtures.invalid_decode_cases[15].input },
};

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [4096]u8 = undefined;
    var stdout = std.Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout.interface;
    var encode_buf: [128]u8 = undefined;
    var decode_buf: [128]u8 = undefined;

    for (encode_cases) |case| {
        const written = try base64.encode(encode_buf[0..], case.input, case.padding, case.variant);
        try writer.print("enc\t{s}\t{}\t", .{ variantName(case.variant), @intFromBool(case.padding) });
        try writeHex(writer, case.input);
        try writer.writeAll("\t");
        try writeHex(writer, encode_buf[0..written]);
        try writer.writeAll("\n");
    }

    for (decode_cases) |case| {
        const written = try base64.decode(decode_buf[0..], case.input, case.padding, case.variant);
        try writer.print("dec\t{s}\t{}\t", .{ variantName(case.variant), @intFromBool(case.padding) });
        try writeHex(writer, case.input);
        try writer.writeAll("\t");
        try writeHex(writer, decode_buf[0..written]);
        try writer.writeAll("\n");
    }

    for (invalid_cases) |case| {
        const bytes_result = base64.bytes(case.input, case.padding, case.variant);
        const decode_result = base64.decode(decode_buf[0..], case.input, case.padding, case.variant);
        try writer.print("inv\t{s}\t{}\t", .{ variantName(case.variant), @intFromBool(case.padding) });
        try writeHex(writer, case.input);
        try writer.print("\t{s}\t{s}\n", .{ errorName(bytes_result), errorName(decode_result) });
    }

    try stdout.flush();
}

fn fixtureVariant(name: []const u8) base64.Variant {
    if (std.mem.eql(u8, name, "std")) {
        return .std;
    }
    if (std.mem.eql(u8, name, "urlsafe")) {
        return .urlsafe;
    }
    if (std.mem.eql(u8, name, "imap")) {
        return .imap;
    }
    unreachable;
}

fn variantName(variant: base64.Variant) []const u8 {
    return switch (variant) {
        .std => "std",
        .urlsafe => "urlsafe",
        .imap => "imap",
    };
}

fn errorName(result: anytype) []const u8 {
    return if (result) |_| "ok" else |err| @errorName(err);
}

fn writeHex(writer: *std.Io.Writer, bytes: []const u8) !void {
    const hex = "0123456789abcdef";
    for (bytes) |byte| {
        const pair = [_]u8{
            hex[byte >> 4],
            hex[byte & 0x0f],
        };
        try writer.writeAll(&pair);
    }
}
