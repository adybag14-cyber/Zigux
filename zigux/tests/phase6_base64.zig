const std = @import("std");
const base64 = @import("base64");
const fixtures = @import("fixtures/phase6_base64_vectors.zig");

const DecodeCase = struct {
    input: []const u8,
    expected: []const u8,
    padding: bool,
    variant: base64.Variant,
};

fn expectEncode(input: []const u8, expected: []const u8, padding: bool, variant: base64.Variant) !void {
    var buf: [128]u8 = undefined;
    const written = try base64.encode(buf[0..], input, padding, variant);

    try std.testing.expectEqual(expected.len, written);
    try std.testing.expectEqual(expected.len, base64.chars(input.len, padding));
    try std.testing.expectEqualStrings(expected, buf[0..written]);
}

fn expectDecode(case: DecodeCase) !void {
    var buf: [128]u8 = undefined;
    const written = try base64.decode(buf[0..], case.input, case.padding, case.variant);

    try std.testing.expectEqual(case.expected.len, written);
    try std.testing.expectEqualSlices(u8, case.expected, buf[0..written]);
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

test "phase 6 base64 module imports cleanly" {
    _ = base64;
}

test "phase 6 base64 standard encode parity matches kernel vectors" {
    for (fixtures.standard_cases) |case| {
        try expectEncode(case.input, case.expected, case.padding, .std);
    }
}

test "phase 6 base64 variant alphabets match the kernel mappings" {
    for (fixtures.variant_cases) |case| {
        try expectEncode(&fixtures.variant_sample, case.expected, false, fixtureVariant(case.variant_name));
    }
}

test "phase 6 base64 standard decode parity matches kernel vectors" {
    const cases = [_]DecodeCase{
        .{ .input = "", .expected = "", .padding = true, .variant = .std },
        .{ .input = "Zg==", .expected = "f", .padding = true, .variant = .std },
        .{ .input = "Zm8=", .expected = "fo", .padding = true, .variant = .std },
        .{ .input = "Zm9v", .expected = "foo", .padding = true, .variant = .std },
        .{ .input = "Zm9vYg==", .expected = "foob", .padding = true, .variant = .std },
        .{ .input = "Zm9vYmE=", .expected = "fooba", .padding = true, .variant = .std },
        .{ .input = "Zm9vYmFy", .expected = "foobar", .padding = true, .variant = .std },
        .{ .input = "SGVsbG8sIHdvcmxkIQ==", .expected = "Hello, world!", .padding = true, .variant = .std },
        .{ .input = "QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVo=", .expected = "ABCDEFGHIJKLMNOPQRSTUVWXYZ", .padding = true, .variant = .std },
        .{ .input = "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo=", .expected = "abcdefghijklmnopqrstuvwxyz", .padding = true, .variant = .std },
        .{ .input = "", .expected = "", .padding = false, .variant = .std },
        .{ .input = "Zg", .expected = "f", .padding = false, .variant = .std },
        .{ .input = "Zm8", .expected = "fo", .padding = false, .variant = .std },
        .{ .input = "Zm9v", .expected = "foo", .padding = false, .variant = .std },
        .{ .input = "Zm9vYg", .expected = "foob", .padding = false, .variant = .std },
        .{ .input = "Zm9vYmE", .expected = "fooba", .padding = false, .variant = .std },
        .{ .input = "Zm9vYmFy", .expected = "foobar", .padding = false, .variant = .std },
        .{ .input = "SGVsbG8sIHdvcmxkIQ", .expected = "Hello, world!", .padding = false, .variant = .std },
        .{ .input = "QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVo", .expected = "ABCDEFGHIJKLMNOPQRSTUVWXYZ", .padding = false, .variant = .std },
        .{ .input = "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo", .expected = "abcdefghijklmnopqrstuvwxyz", .padding = false, .variant = .std },
        .{ .input = "MDEyMzQ1Njc4OSsv", .expected = "0123456789+/", .padding = false, .variant = .std },
    };

    for (cases) |case| {
        try expectDecode(case);
    }
}

test "phase 6 base64 decode rejects invalid kernel-style vectors" {
    var buf: [128]u8 = undefined;
    const with_nul = [_]u8{ 'Z', 'g', 0, '=' };
    const invalid_cases = [_]struct {
        input: []const u8,
        padding: bool,
        variant: base64.Variant,
    }{
        .{ .input = "Zg=!", .padding = true, .variant = .std },
        .{ .input = "Zm$=", .padding = true, .variant = .std },
        .{ .input = "Z===", .padding = true, .variant = .std },
        .{ .input = "Zg", .padding = true, .variant = .std },
        .{ .input = "Zm9v====", .padding = true, .variant = .std },
        .{ .input = "Zm==A", .padding = true, .variant = .std },
        .{ .input = &with_nul, .padding = true, .variant = .std },
        .{ .input = "Zg=!", .padding = false, .variant = .std },
        .{ .input = "Zm$=", .padding = false, .variant = .std },
        .{ .input = "Z===", .padding = false, .variant = .std },
        .{ .input = "Zg=", .padding = false, .variant = .std },
        .{ .input = "Zm9v====", .padding = false, .variant = .std },
        .{ .input = "Zm==v", .padding = false, .variant = .std },
        .{ .input = &with_nul, .padding = false, .variant = .std },
        .{ .input = "Zg==", .padding = false, .variant = .urlsafe },
        .{ .input = "Zg==", .padding = false, .variant = .imap },
    };

    for (invalid_cases) |case| {
        try std.testing.expectError(base64.DecodeError.InvalidInput, base64.decode(buf[0..], case.input, case.padding, case.variant));
    }
}

test "phase 6 base64 variant decode parity matches the kernel mappings" {
    const cases = [_]DecodeCase{
        .{ .input = "APv_f4A", .expected = &fixtures.variant_sample, .padding = false, .variant = .urlsafe },
        .{ .input = "APv,f4A", .expected = &fixtures.variant_sample, .padding = false, .variant = .imap },
    };

    for (cases) |case| {
        try expectDecode(case);
    }
}

test "phase 6 base64 reports destination bounds before encoding" {
    var buf: [3]u8 = undefined;
    try std.testing.expectError(base64.EncodeError.DestinationTooSmall, base64.encode(buf[0..], "f", true, .std));
    try std.testing.expectError(base64.EncodeError.DestinationTooSmall, base64.encode(buf[0..], "foo", false, .std));
}

test "phase 6 base64 reports destination bounds before decoding" {
    var buf: [2]u8 = undefined;
    try std.testing.expectError(base64.DecodeError.DestinationTooSmall, base64.decode(buf[0..], "Zm9v", false, .std));
}
