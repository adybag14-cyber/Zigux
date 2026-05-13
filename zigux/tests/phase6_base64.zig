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
    const decoded_len = try base64.bytes(case.input, case.padding, case.variant);
    try std.testing.expectEqual(case.expected.len, decoded_len);

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

test "phase 6 base64 chars reports exact padded and unpadded lengths" {
    const cases = [_]struct {
        len: usize,
        padding: bool,
        expected: usize,
    }{
        .{ .len = 0, .padding = true, .expected = 0 },
        .{ .len = 1, .padding = true, .expected = 4 },
        .{ .len = 2, .padding = true, .expected = 4 },
        .{ .len = 3, .padding = true, .expected = 4 },
        .{ .len = 4, .padding = true, .expected = 8 },
        .{ .len = 0, .padding = false, .expected = 0 },
        .{ .len = 1, .padding = false, .expected = 2 },
        .{ .len = 2, .padding = false, .expected = 3 },
        .{ .len = 3, .padding = false, .expected = 4 },
        .{ .len = 4, .padding = false, .expected = 6 },
    };

    for (cases) |case| {
        try std.testing.expectEqual(case.expected, base64.chars(case.len, case.padding));
    }
}

test "phase 6 base64 bytes reports exact decoded lengths for kernel-aligned vectors" {
    const cases = [_]struct {
        input: []const u8,
        padding: bool,
        variant: base64.Variant,
        expected: usize,
    }{
        .{ .input = "TQ==", .padding = true, .variant = .std, .expected = 1 },
        .{ .input = "TWE=", .padding = true, .variant = .std, .expected = 2 },
        .{ .input = "TWFu", .padding = false, .variant = .std, .expected = 3 },
        .{ .input = "APv_f4A", .padding = false, .variant = .urlsafe, .expected = 5 },
        .{ .input = "APv,f4A=", .padding = true, .variant = .imap, .expected = 5 },
    };

    for (cases) |case| {
        try std.testing.expectEqual(case.expected, try base64.bytes(case.input, case.padding, case.variant));
    }
}

test "phase 6 base64 standard encode parity matches kernel vectors" {
    for (fixtures.standard_cases) |case| {
        try expectEncode(case.input, case.expected, case.padding, .std);
    }
}

test "phase 6 base64 variant alphabets match the kernel mappings with and without padding" {
    for (fixtures.variant_cases) |case| {
        try expectEncode(&fixtures.variant_sample, case.expected, case.padding, fixtureVariant(case.variant_name));
    }
}

test "phase 6 base64 standard decode parity keeps bytes and decode aligned with kernel vectors" {
    for (fixtures.standard_decode_cases) |case| {
        try expectDecode(.{
            .input = case.input,
            .expected = case.expected,
            .padding = case.padding,
            .variant = fixtureVariant(case.variant_name),
        });
    }
}

test "phase 6 base64 invalid vectors fail bytes and decode together" {
    var buf: [128]u8 = undefined;
    for (fixtures.invalid_decode_cases) |case| {
        const variant = fixtureVariant(case.variant_name);
        try std.testing.expectError(base64.DecodeError.InvalidInput, base64.bytes(case.input, case.padding, variant));
        try std.testing.expectError(base64.DecodeError.InvalidInput, base64.decode(buf[0..], case.input, case.padding, variant));
    }
}

test "phase 6 base64 invalid decode vectors leave destination bytes untouched" {
    for (fixtures.invalid_decode_cases) |case| {
        const variant = fixtureVariant(case.variant_name);
        var buf = [_]u8{0xee} ** 32;

        try std.testing.expectError(base64.DecodeError.InvalidInput, base64.decode(buf[0..], case.input, case.padding, variant));
        try std.testing.expectEqualSlices(u8, &([_]u8{0xee} ** 32), buf[0..]);
    }
}

test "phase 6 base64 bytes rejects malformed kernel-style vectors" {
    const cases = [_]struct {
        input: []const u8,
        padding: bool,
        variant: base64.Variant,
    }{
        .{ .input = "A", .padding = false, .variant = .std },
        .{ .input = "Zh==", .padding = true, .variant = .std },
        .{ .input = "Zm9=", .padding = false, .variant = .std },
        .{ .input = "Zg==", .padding = false, .variant = .urlsafe },
    };

    for (cases) |case| {
        try std.testing.expectError(base64.DecodeError.InvalidInput, base64.bytes(case.input, case.padding, case.variant));
    }
}

test "phase 6 base64 variant decode parity keeps bytes and decode aligned with kernel mappings" {
    for (fixtures.variant_decode_cases) |case| {
        try expectDecode(.{
            .input = case.input,
            .expected = case.expected,
            .padding = case.padding,
            .variant = fixtureVariant(case.variant_name),
        });
    }
}

test "phase 6 base64 reports destination bounds before encoding" {
    var padded_buf = [_]u8{0xaa} ** 3;
    try std.testing.expectError(base64.EncodeError.DestinationTooSmall, base64.encode(padded_buf[0..], "f", true, .std));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0xaa, 0xaa }, padded_buf[0..]);

    var unpadded_buf = [_]u8{0xbb} ** 3;
    try std.testing.expectError(base64.EncodeError.DestinationTooSmall, base64.encode(unpadded_buf[0..], "foo", false, .std));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xbb, 0xbb, 0xbb }, unpadded_buf[0..]);
}

test "phase 6 base64 reports destination bounds before decoding" {
    var padded_buf = [_]u8{0xcc} ** 1;
    try std.testing.expectError(base64.DecodeError.DestinationTooSmall, base64.decode(padded_buf[0..], "Zm8=", true, .std));
    try std.testing.expectEqualSlices(u8, &[_]u8{0xcc}, padded_buf[0..]);

    var unpadded_buf = [_]u8{0xdd} ** 2;
    try std.testing.expectError(base64.DecodeError.DestinationTooSmall, base64.decode(unpadded_buf[0..], "Zm9v", false, .std));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xdd, 0xdd }, unpadded_buf[0..]);
}
