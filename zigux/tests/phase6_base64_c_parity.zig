const std = @import("std");
const base64 = @import("base64");

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

const variant_sample = [_]u8{ 0x00, 0xfb, 0xff, 0x7f, 0x80 };
const invalid_with_nul = [_]u8{ 'Z', 'g', 0, '=' };

const encode_cases = [_]EncodeCase{
    .{ .variant = .std, .padding = true, .input = "" },
    .{ .variant = .std, .padding = true, .input = "f" },
    .{ .variant = .std, .padding = true, .input = "fo" },
    .{ .variant = .std, .padding = false, .input = "foobar" },
    .{ .variant = .std, .padding = true, .input = "Hello, world!" },
    .{ .variant = .urlsafe, .padding = false, .input = &variant_sample },
    .{ .variant = .urlsafe, .padding = true, .input = &variant_sample },
    .{ .variant = .imap, .padding = false, .input = &variant_sample },
    .{ .variant = .imap, .padding = true, .input = &variant_sample },
};

const decode_cases = [_]DecodeCase{
    .{ .variant = .std, .padding = true, .input = "" },
    .{ .variant = .std, .padding = true, .input = "Zg==" },
    .{ .variant = .std, .padding = true, .input = "Zm8=" },
    .{ .variant = .std, .padding = false, .input = "Zm9vYmFy" },
    .{ .variant = .std, .padding = true, .input = "SGVsbG8sIHdvcmxkIQ==" },
    .{ .variant = .urlsafe, .padding = false, .input = "APv_f4A" },
    .{ .variant = .urlsafe, .padding = true, .input = "APv_f4A=" },
    .{ .variant = .imap, .padding = false, .input = "APv,f4A" },
    .{ .variant = .imap, .padding = true, .input = "APv,f4A=" },
};

const invalid_cases = [_]InvalidCase{
    .{ .variant = .std, .padding = true, .input = "Zg=!" },
    .{ .variant = .std, .padding = true, .input = "Z===" },
    .{ .variant = .std, .padding = false, .input = "Zm9v====" },
    .{ .variant = .std, .padding = true, .input = invalid_with_nul[0..] },
    .{ .variant = .urlsafe, .padding = false, .input = "Zg==" },
    .{ .variant = .imap, .padding = false, .input = "Zg==" },
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
