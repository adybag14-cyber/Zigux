const std = @import("std");
const fixtures = @import("fixtures/phase6_base64_c_parity_vectors.zig");

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [4096]u8 = undefined;
    var stdout = std.Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout.interface;

    try writer.writeAll("/* Generated from zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig. */\n\n");

    for (fixtures.standard_cases, 0..) |case, idx| {
        try emitBytesDecl(writer, "enc_input", idx, case.input);
    }
    for (fixtures.variant_cases, 0..) |case, idx| {
        try emitBytesDecl(writer, "variant_enc_input", idx, case.input);
    }
    try writer.writeByte('\n');

    for (fixtures.standard_decode_cases, 0..) |case, idx| {
        try emitBytesDecl(writer, "dec_input", idx, case.input);
    }
    for (fixtures.variant_decode_cases, 0..) |case, idx| {
        try emitBytesDecl(writer, "variant_dec_input", idx, case.input);
    }
    try writer.writeByte('\n');

    for (fixtures.invalid_decode_cases, 0..) |case, idx| {
        try emitBytesDecl(writer, "invalid_input", idx, case.input);
    }
    try writer.writeByte('\n');

    try writer.writeAll("static const struct encode_case encode_cases[] = {\n");
    for (fixtures.standard_cases, 0..) |case, idx| {
        try writer.print("    {{ BASE64_STD, {s}, phase6_base64_enc_input_{d}, {} }},\n", .{
            boolLiteral(case.padding),
            idx,
            case.input.len,
        });
    }
    for (fixtures.variant_cases, 0..) |case, idx| {
        try writer.print("    {{ {s}, {s}, phase6_base64_variant_enc_input_{d}, {} }},\n", .{
            variantEnum(case.variant_name),
            boolLiteral(case.padding),
            idx,
            case.input.len,
        });
    }
    try writer.writeAll("};\n\n");

    try writer.writeAll("static const struct decode_case decode_cases[] = {\n");
    for (fixtures.standard_decode_cases, 0..) |case, idx| {
        try writer.print("    {{ BASE64_STD, {s}, phase6_base64_dec_input_{d}, {} }},\n", .{
            boolLiteral(case.padding),
            idx,
            case.input.len,
        });
    }
    for (fixtures.variant_decode_cases, 0..) |case, idx| {
        try writer.print("    {{ {s}, {s}, phase6_base64_variant_dec_input_{d}, {} }},\n", .{
            variantEnum(case.variant_name),
            boolLiteral(case.padding),
            idx,
            case.input.len,
        });
    }
    try writer.writeAll("};\n\n");

    try writer.writeAll("static const struct invalid_case invalid_cases[] = {\n");
    for (fixtures.invalid_decode_cases, 0..) |case, idx| {
        try writer.print("    {{ {s}, {s}, phase6_base64_invalid_input_{d}, {} }},\n", .{
            variantEnum(case.variant_name),
            boolLiteral(case.padding),
            idx,
            case.input.len,
        });
    }
    try writer.writeAll("};\n");

    try stdout.flush();
}

fn emitBytesDecl(writer: anytype, comptime prefix: []const u8, idx: usize, bytes: []const u8) !void {
    try writer.print("static const unsigned char phase6_base64_{s}_{d}[] = {{", .{ prefix, idx });
    if (bytes.len == 0) {
        try writer.writeAll(" 0x00");
    } else {
        for (bytes, 0..) |byte, byte_idx| {
            if (byte_idx == 0) {
                try writer.print(" 0x{x:0>2}", .{byte});
            } else {
                try writer.print(", 0x{x:0>2}", .{byte});
            }
        }
    }
    try writer.writeAll(" };\n");
}

fn variantEnum(name: []const u8) []const u8 {
    if (std.mem.eql(u8, name, "std")) return "BASE64_STD";
    if (std.mem.eql(u8, name, "urlsafe")) return "BASE64_URLSAFE";
    if (std.mem.eql(u8, name, "imap")) return "BASE64_IMAP";
    unreachable;
}

fn boolLiteral(value: bool) []const u8 {
    return if (value) "true" else "false";
}
