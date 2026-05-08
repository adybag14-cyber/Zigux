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

fn expectShortRoundtrip(length: usize, padding: bool, variant: base64.Variant) !void {
    var encoded: [8]u8 = undefined;
    var decoded: [2]u8 = undefined;

    switch (length) {
        1 => {
            for (0..256) |a| {
                const input = [_]u8{@intCast(a)};
                const encoded_len = try base64.encode(encoded[0..], input[0..], padding, variant);
                try std.testing.expectEqual(base64.chars(input.len, padding), encoded_len);
                try std.testing.expectEqual(@as(usize, input.len), try base64.bytes(encoded[0..encoded_len], padding, variant));

                const decoded_len = try base64.decode(decoded[0..], encoded[0..encoded_len], padding, variant);
                try std.testing.expectEqual(@as(usize, 1), decoded_len);
                try std.testing.expectEqualSlices(u8, input[0..], decoded[0..decoded_len]);
            }
        },
        2 => {
            for (0..256) |a| {
                for (0..256) |b| {
                    const input = [_]u8{ @intCast(a), @intCast(b) };
                    const encoded_len = try base64.encode(encoded[0..], input[0..], padding, variant);
                    try std.testing.expectEqual(base64.chars(input.len, padding), encoded_len);
                    try std.testing.expectEqual(@as(usize, input.len), try base64.bytes(encoded[0..encoded_len], padding, variant));

                    const decoded_len = try base64.decode(decoded[0..], encoded[0..encoded_len], padding, variant);
                    try std.testing.expectEqual(@as(usize, 2), decoded_len);
                    try std.testing.expectEqualSlices(u8, input[0..], decoded[0..decoded_len]);
                }
            }
        },
        else => unreachable,
    }
}

test "phase 6 base64 module imports cleanly" {
    _ = base64;
}

test "phase 6 base64 paddedChars keeps the kernel-style padded sizing explicit" {
    const cases = [_]struct {
        len: usize,
        expected: usize,
    }{
        .{ .len = 0, .expected = 0 },
        .{ .len = 1, .expected = 4 },
        .{ .len = 2, .expected = 4 },
        .{ .len = 3, .expected = 4 },
        .{ .len = 4, .expected = 8 },
        .{ .len = 5, .expected = 8 },
        .{ .len = 6, .expected = 8 },
        .{ .len = 7, .expected = 12 },
    };

    for (cases) |case| {
        try std.testing.expectEqual(case.expected, base64.paddedChars(case.len));
        try std.testing.expectEqual(case.expected, base64.chars(case.len, true));
    }
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

test "phase 6 base64 maxDecodedBytes keeps the public decode bound reviewable" {
    const cases = [_]struct {
        nchars: usize,
        expected: usize,
    }{
        .{ .nchars = 0, .expected = 0 },
        .{ .nchars = 1, .expected = 0 },
        .{ .nchars = 2, .expected = 1 },
        .{ .nchars = 3, .expected = 2 },
        .{ .nchars = 4, .expected = 3 },
        .{ .nchars = 5, .expected = 3 },
        .{ .nchars = 6, .expected = 4 },
        .{ .nchars = 7, .expected = 5 },
        .{ .nchars = 8, .expected = 6 },
    };

    for (cases) |case| {
        try std.testing.expectEqual(case.expected, base64.maxDecodedBytes(case.nchars));
    }

    for (fixtures.standard_decode_cases) |case| {
        try std.testing.expect(base64.maxDecodedBytes(case.input.len) >= case.expected.len);
    }
    for (fixtures.variant_decode_cases) |case| {
        try std.testing.expect(base64.maxDecodedBytes(case.input.len) >= case.expected.len);
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

test "phase 6 base64 foreign alphabet rejection leaves destination bytes untouched" {
    const cases = [_]struct {
        input: []const u8,
        padding: bool,
        variant: base64.Variant,
    }{
        .{ .input = "APv_f4A", .padding = false, .variant = .std },
        .{ .input = "APv/f4A", .padding = false, .variant = .urlsafe },
        .{ .input = "APv/f4A=", .padding = true, .variant = .imap },
        .{ .input = "APv,f4A=", .padding = true, .variant = .std },
    };

    for (cases) |case| {
        var decoded = [_]u8{0xdd} ** 8;
        try std.testing.expectError(base64.DecodeError.InvalidInput, base64.bytes(case.input, case.padding, case.variant));
        try std.testing.expectError(base64.DecodeError.InvalidInput, base64.decode(decoded[0..], case.input, case.padding, case.variant));
        try std.testing.expectEqualSlices(u8, &([_]u8{0xdd} ** 8), decoded[0..]);
    }
}

test "phase 6 base64 successful decode leaves caller bytes past the returned payload untouched" {
    const cases = [_]DecodeCase{
        .{ .input = "Zg==", .expected = "f", .padding = true, .variant = .std },
        .{ .input = "Zg", .expected = "f", .padding = false, .variant = .std },
        .{ .input = "Zm8=", .expected = "fo", .padding = true, .variant = .std },
        .{ .input = "Zm8", .expected = "fo", .padding = false, .variant = .std },
        .{ .input = "APv_f4A", .expected = &fixtures.variant_sample, .padding = false, .variant = .urlsafe },
        .{ .input = "APv,f4A=", .expected = &fixtures.variant_sample, .padding = true, .variant = .imap },
    };

    for (cases) |case| {
        var decoded = [_]u8{0xaa} ** 8;
        const written = try base64.decode(decoded[0..], case.input, case.padding, case.variant);

        try std.testing.expectEqual(case.expected.len, written);
        try std.testing.expectEqualSlices(u8, case.expected, decoded[0..written]);
        for (decoded[written..]) |byte| {
            try std.testing.expectEqual(@as(u8, 0xaa), byte);
        }
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

test "phase 6 base64 exact-fit encode and decode buffers stay accepted across std, urlsafe, and imap variants" {
    const encode_cases = [_]struct {
        input: []const u8,
        expected: []const u8,
        padding: bool,
        variant: base64.Variant,
    }{
        .{ .input = "fooba", .expected = "Zm9vYmE=", .padding = true, .variant = .std },
        .{ .input = "fooba", .expected = "Zm9vYmE", .padding = false, .variant = .std },
        .{ .input = &fixtures.variant_sample, .expected = "APv_f4A=", .padding = true, .variant = .urlsafe },
        .{ .input = &fixtures.variant_sample, .expected = "APv_f4A", .padding = false, .variant = .urlsafe },
        .{ .input = &fixtures.variant_sample, .expected = "APv,f4A=", .padding = true, .variant = .imap },
        .{ .input = &fixtures.variant_sample, .expected = "APv,f4A", .padding = false, .variant = .imap },
    };

    for (encode_cases) |case| {
        var encoded = [_]u8{0xaa} ** 8;
        const exact = encoded[0..base64.chars(case.input.len, case.padding)];
        const written = try base64.encode(exact, case.input, case.padding, case.variant);

        try std.testing.expectEqual(exact.len, written);
        try std.testing.expectEqualStrings(case.expected, exact[0..written]);
    }

    const decode_cases = [_]DecodeCase{
        .{ .input = "Zm9vYmE=", .expected = "fooba", .padding = true, .variant = .std },
        .{ .input = "Zm9vYmE", .expected = "fooba", .padding = false, .variant = .std },
        .{ .input = "APv_f4A=", .expected = &fixtures.variant_sample, .padding = true, .variant = .urlsafe },
        .{ .input = "APv_f4A", .expected = &fixtures.variant_sample, .padding = false, .variant = .urlsafe },
        .{ .input = "APv,f4A=", .expected = &fixtures.variant_sample, .padding = true, .variant = .imap },
        .{ .input = "APv,f4A", .expected = &fixtures.variant_sample, .padding = false, .variant = .imap },
    };

    for (decode_cases) |case| {
        var decoded = [_]u8{0xdd} ** 5;
        const exact_len = try base64.bytes(case.input, case.padding, case.variant);
        const exact = decoded[0..exact_len];
        const written = try base64.decode(exact, case.input, case.padding, case.variant);

        try std.testing.expectEqual(exact.len, written);
        try std.testing.expectEqualSlices(u8, case.expected, exact[0..written]);
    }
}

test "phase 6 base64 exhaustive one-byte and two-byte roundtrip coverage stays aligned across std, urlsafe, and imap variants" {
    const variants = [_]base64.Variant{ .std, .urlsafe, .imap };
    const padding_modes = [_]bool{ true, false };

    for (variants) |variant| {
        for (padding_modes) |padding| {
            try expectShortRoundtrip(1, padding, variant);
            try expectShortRoundtrip(2, padding, variant);
        }
    }
}

test "phase 6 base64 empty encode and decode inputs stay zero-length no-ops across variants" {
    const variants = [_]base64.Variant{ .std, .urlsafe, .imap };

    for (variants) |variant| {
        var encoded = [_]u8{0xa1} ** 4;
        const encoded_exact = encoded[0..0];

        try std.testing.expectEqual(@as(usize, 0), base64.chars(0, true));
        try std.testing.expectEqual(@as(usize, 0), base64.chars(0, false));
        try std.testing.expectEqual(@as(usize, 0), try base64.encode(encoded_exact, "", true, variant));
        try std.testing.expectEqual(@as(usize, 0), try base64.encode(encoded_exact, "", false, variant));
        for (encoded) |byte| {
            try std.testing.expectEqual(@as(u8, 0xa1), byte);
        }

        var decoded_padded = [_]u8{0xb2} ** 4;
        const decoded_padded_exact = decoded_padded[0..0];
        try std.testing.expectEqual(@as(usize, 0), try base64.bytes("", true, variant));
        try std.testing.expectEqual(@as(usize, 0), try base64.decode(decoded_padded_exact, "", true, variant));
        for (decoded_padded) |byte| {
            try std.testing.expectEqual(@as(u8, 0xb2), byte);
        }

        var decoded_unpadded = [_]u8{0xc3} ** 4;
        const decoded_unpadded_exact = decoded_unpadded[0..0];
        try std.testing.expectEqual(@as(usize, 0), try base64.bytes("", false, variant));
        try std.testing.expectEqual(@as(usize, 0), try base64.decode(decoded_unpadded_exact, "", false, variant));
        for (decoded_unpadded) |byte| {
            try std.testing.expectEqual(@as(u8, 0xc3), byte);
        }
    }
}
