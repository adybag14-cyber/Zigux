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
    findStandardEncodeCase("", true),
    findStandardEncodeCase("f", true),
    findStandardEncodeCase("fo", true),
    findStandardEncodeCase("foobar", false),
    findStandardEncodeCase("Hello, world!", true),
    findVariantEncodeCase("urlsafe", "APv_f4A", false),
    findVariantEncodeCase("urlsafe", "APv_f4A=", true),
    findVariantEncodeCase("urlsafe", "-w", false),
    findVariantEncodeCase("urlsafe", "-w==", true),
    findVariantEncodeCase("urlsafe", "__A", false),
    findVariantEncodeCase("urlsafe", "__A=", true),
    findVariantEncodeCase("imap", "APv,f4A", false),
    findVariantEncodeCase("imap", "APv,f4A=", true),
    findVariantEncodeCase("imap", "+w", false),
    findVariantEncodeCase("imap", "+w==", true),
    findVariantEncodeCase("imap", ",,A", false),
    findVariantEncodeCase("imap", ",,A=", true),
};

const decode_cases = [_]DecodeCase{
    findStandardDecodeCase("", true),
    findStandardDecodeCase("Zg==", true),
    findStandardDecodeCase("Zm8=", true),
    findStandardDecodeCase("Zm9vYmFy", false),
    findStandardDecodeCase("SGVsbG8sIHdvcmxkIQ==", true),
    findVariantDecodeCase("urlsafe", "APv_f4A", false),
    findVariantDecodeCase("urlsafe", "APv_f4A=", true),
    findVariantDecodeCase("urlsafe", "-w", false),
    findVariantDecodeCase("urlsafe", "-w==", true),
    findVariantDecodeCase("urlsafe", "__A", false),
    findVariantDecodeCase("urlsafe", "__A=", true),
    findVariantDecodeCase("imap", "APv,f4A", false),
    findVariantDecodeCase("imap", "APv,f4A=", true),
    findVariantDecodeCase("imap", "+w", false),
    findVariantDecodeCase("imap", "+w==", true),
    findVariantDecodeCase("imap", ",,A", false),
    findVariantDecodeCase("imap", ",,A=", true),
};

const invalid_cases = [_]InvalidCase{
    findInvalidCase("std", "Zg=!", true),
    findInvalidCase("std", "Z===", true),
    findInvalidCase("std", "Zm9v====", false),
    findInvalidCase("std", &[_]u8{ 'Z', 'g', 0, '=' }, true),
    findInvalidCase("urlsafe", "Zg==", false),
    findInvalidCase("imap", "Zg==", false),
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

fn findStandardEncodeCase(comptime input: []const u8, comptime padding: bool) EncodeCase {
    inline for (fixtures.standard_cases) |case| {
        if (case.padding == padding and std.mem.eql(u8, case.input, input)) {
            return .{ .variant = .std, .padding = case.padding, .input = case.input };
        }
    }
    @compileError("missing standard Phase 6 base64 C parity encode case");
}

fn findVariantEncodeCase(comptime variant_name: []const u8, comptime expected: []const u8, comptime padding: bool) EncodeCase {
    inline for (fixtures.variant_cases) |case| {
        if (case.padding == padding and
            std.mem.eql(u8, case.variant_name, variant_name) and
            std.mem.eql(u8, case.expected, expected))
        {
            return .{
                .variant = fixtureVariant(case.variant_name),
                .padding = case.padding,
                .input = case.input,
            };
        }
    }
    @compileError("missing variant Phase 6 base64 C parity encode case");
}

fn findStandardDecodeCase(comptime input: []const u8, comptime padding: bool) DecodeCase {
    inline for (fixtures.standard_decode_cases) |case| {
        if (case.padding == padding and std.mem.eql(u8, case.input, input)) {
            return .{ .variant = .std, .padding = case.padding, .input = case.input };
        }
    }
    @compileError("missing standard Phase 6 base64 C parity decode case");
}

fn findVariantDecodeCase(comptime variant_name: []const u8, comptime input: []const u8, comptime padding: bool) DecodeCase {
    inline for (fixtures.variant_decode_cases) |case| {
        if (case.padding == padding and
            std.mem.eql(u8, case.variant_name, variant_name) and
            std.mem.eql(u8, case.input, input))
        {
            return .{
                .variant = fixtureVariant(case.variant_name),
                .padding = case.padding,
                .input = case.input,
            };
        }
    }
    @compileError("missing variant Phase 6 base64 C parity decode case");
}

fn findInvalidCase(comptime variant_name: []const u8, comptime input: []const u8, comptime padding: bool) InvalidCase {
    inline for (fixtures.invalid_decode_cases) |case| {
        if (case.padding == padding and
            std.mem.eql(u8, case.variant_name, variant_name) and
            std.mem.eql(u8, case.input, input))
        {
            return .{
                .variant = fixtureVariant(case.variant_name),
                .padding = case.padding,
                .input = case.input,
            };
        }
    }
    @compileError("missing invalid Phase 6 base64 C parity case");
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
