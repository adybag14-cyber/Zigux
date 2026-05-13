const std = @import("std");
const base64 = @import("base64");
const fixtures = @import("fixtures/phase6_base64_c_parity_vectors.zig");

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [4096]u8 = undefined;
    var stdout = std.Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout.interface;
    var encode_buf: [128]u8 = undefined;
    var decode_buf: [128]u8 = undefined;
    var hex_buf: [256]u8 = undefined;

    for (fixtures.standard_cases) |case| {
        const written = try base64.encode(encode_buf[0..], case.input, case.padding, .std);
        try writer.print("enc\tstd\t{}\t", .{@intFromBool(case.padding)});
        try writeHex(writer, case.input);
        try writer.writeAll("\t");
        try writeHex(writer, encode_buf[0..written]);
        try writer.writeAll("\n");
    }

    for (fixtures.variant_cases) |case| {
        const variant = fixtureVariant(case.variant_name);
        const written = try base64.encode(encode_buf[0..], case.input, case.padding, variant);
        try writer.print("enc\t{s}\t{}\t", .{ case.variant_name, @intFromBool(case.padding) });
        try writeHex(writer, case.input);
        try writer.writeAll("\t");
        try writeHex(writer, encode_buf[0..written]);
        try writer.writeAll("\n");
    }

    for (fixtures.standard_decode_cases) |case| {
        const exact_len = try base64.bytes(case.input, case.padding, .std);
        const written = try base64.decode(decode_buf[0..], case.input, case.padding, .std);
        try writer.print("dec\tstd\t{}\t{}\t", .{ @intFromBool(case.padding), exact_len });
        try writeHex(writer, case.input);
        try writer.writeAll("\t");
        try writeHex(writer, decode_buf[0..written]);
        try writer.writeAll("\n");
    }

    for (fixtures.variant_decode_cases) |case| {
        const variant = fixtureVariant(case.variant_name);
        const exact_len = try base64.bytes(case.input, case.padding, variant);
        const written = try base64.decode(decode_buf[0..], case.input, case.padding, variant);
        try writer.print("dec\t{s}\t{}\t{}\t", .{ case.variant_name, @intFromBool(case.padding), exact_len });
        try writeHex(writer, case.input);
        try writer.writeAll("\t");
        try writeHex(writer, decode_buf[0..written]);
        try writer.writeAll("\n");
    }

    for (fixtures.invalid_decode_cases) |case| {
        const variant = fixtureVariant(case.variant_name);
        const bytes_result = base64.bytes(case.input, case.padding, variant);
        const decode_result = base64.decode(decode_buf[0..], case.input, case.padding, variant);
        try writer.print("inv\t{s}\t{}\t", .{ case.variant_name, @intFromBool(case.padding) });
        try writeHex(writer, case.input);
        try writer.print("\t{s}\t{s}\n", .{ errorName(bytes_result), errorName(decode_result) });
    }

    _ = &hex_buf;
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
