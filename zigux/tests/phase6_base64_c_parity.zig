const std = @import("std");
const base64 = @import("base64");
const fixtures = @import("phase6_base64_vectors");
const Io = std.Io;

fn variantFromName(name: []const u8) base64.Variant {
    if (std.mem.eql(u8, name, "std")) return .std;
    if (std.mem.eql(u8, name, "urlsafe")) return .urlsafe;
    if (std.mem.eql(u8, name, "imap")) return .imap;
    unreachable;
}

fn findEncodeCase(input: []const u8, padding: bool) fixtures.EncodeCase {
    for (fixtures.standard_cases) |case| {
        if (case.padding == padding and std.mem.eql(u8, case.input, input)) return case;
    }
    unreachable;
}

fn findDecodeCase(input: []const u8, padding: bool, variant_name: []const u8) fixtures.DecodeCase {
    for (fixtures.standard_decode_cases) |case| {
        if (case.padding == padding and std.mem.eql(u8, case.input, input) and std.mem.eql(u8, case.variant_name, variant_name)) return case;
    }
    for (fixtures.variant_decode_cases) |case| {
        if (case.padding == padding and std.mem.eql(u8, case.input, input) and std.mem.eql(u8, case.variant_name, variant_name)) return case;
    }
    unreachable;
}

fn findVariantCase(variant_name: []const u8, padding: bool) fixtures.VariantCase {
    for (fixtures.variant_cases) |case| {
        if (case.padding == padding and std.mem.eql(u8, case.variant_name, variant_name)) return case;
    }
    unreachable;
}

fn findInvalidCase(input: []const u8, padding: bool, variant_name: []const u8) fixtures.InvalidDecodeCase {
    for (fixtures.invalid_decode_cases) |case| {
        if (case.padding == padding and std.mem.eql(u8, case.input, input) and std.mem.eql(u8, case.variant_name, variant_name)) return case;
    }
    unreachable;
}

fn printDecodeHex(writer: anytype, label: []const u8, input: []const u8, padding: bool, variant: base64.Variant) !void {
    var buf: [64]u8 = undefined;
    const written = try base64.decode(buf[0..], input, padding, variant);
    try writer.print("decode\t{s}\t", .{label});
    for (buf[0..written]) |byte| try writer.print("{x:0>2}", .{byte});
    try writer.writeByte('\n');
}

fn printEncode(writer: anytype, label: []const u8, input: []const u8, padding: bool, variant: base64.Variant) !void {
    var buf: [128]u8 = undefined;
    const written = try base64.encode(buf[0..], input, padding, variant);
    try writer.print("encode\t{s}\t{s}\n", .{ label, buf[0..written] });
}

fn printInvalid(writer: anytype, label: []const u8, input: []const u8, padding: bool, variant: base64.Variant) !void {
    var buf: [16]u8 = undefined;
    try std.testing.expectError(base64.DecodeError.InvalidInput, base64.bytes(input, padding, variant));
    try std.testing.expectError(base64.DecodeError.InvalidInput, base64.decode(buf[0..], input, padding, variant));
    try writer.print("invalid\t{s}\treject\n", .{label});
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [4096]u8 = undefined;
    var stdout = Io.File.stdout().writer(io, &stdout_buffer);

    const enc_f = findEncodeCase("f", true);
    const enc_fo = findEncodeCase("fo", false);
    const enc_hello = findEncodeCase("Hello, world!", true);
    const var_url = findVariantCase("urlsafe", true);
    const var_imap = findVariantCase("imap", false);

    try printEncode(&stdout.interface, "std-pad-f", enc_f.input, enc_f.padding, .std);
    try printEncode(&stdout.interface, "std-no-pad-fo", enc_fo.input, enc_fo.padding, .std);
    try printEncode(&stdout.interface, "std-pad-hello", enc_hello.input, enc_hello.padding, .std);
    try printEncode(&stdout.interface, "urlsafe-pad-variant", &fixtures.variant_sample, var_url.padding, variantFromName(var_url.variant_name));
    try printEncode(&stdout.interface, "imap-no-pad-variant", &fixtures.variant_sample, var_imap.padding, variantFromName(var_imap.variant_name));

    const dec_foobar = findDecodeCase("Zm9vYmFy", true, "std");
    const dec_hello = findDecodeCase("SGVsbG8sIHdvcmxkIQ", false, "std");
    const dec_url = findDecodeCase("APv_f4A=", true, "urlsafe");
    const dec_imap = findDecodeCase("APv,f4A", false, "imap");

    try printDecodeHex(&stdout.interface, "std-pad-foobar", dec_foobar.input, dec_foobar.padding, .std);
    try printDecodeHex(&stdout.interface, "std-no-pad-hello", dec_hello.input, dec_hello.padding, .std);
    try printDecodeHex(&stdout.interface, "urlsafe-pad-variant", dec_url.input, dec_url.padding, .urlsafe);
    try printDecodeHex(&stdout.interface, "imap-no-pad-variant", dec_imap.input, dec_imap.padding, .imap);

    const inv_a = findInvalidCase("Zh==", true, "std");
    const inv_b = findInvalidCase("Zh==", true, "urlsafe");
    const inv_c = findInvalidCase("Zm9=", true, "imap");
    const inv_d = findInvalidCase("Zh", false, "std");
    const inv_e = findInvalidCase("Zm9", false, "std");
    const inv_f = findInvalidCase("Zg==", false, "imap");

    try printInvalid(&stdout.interface, "std-pad-noncanonical-pair", inv_a.input, inv_a.padding, .std);
    try printInvalid(&stdout.interface, "urlsafe-pad-noncanonical-pair", inv_b.input, inv_b.padding, .urlsafe);
    try printInvalid(&stdout.interface, "imap-pad-noncanonical-triple", inv_c.input, inv_c.padding, .imap);
    try printInvalid(&stdout.interface, "std-no-pad-noncanonical-pair", inv_d.input, inv_d.padding, .std);
    try printInvalid(&stdout.interface, "std-no-pad-noncanonical-triple", inv_e.input, inv_e.padding, .std);
    try printInvalid(&stdout.interface, "imap-no-pad-padding-reject", inv_f.input, inv_f.padding, .imap);

    try stdout.interface.flush();
}
