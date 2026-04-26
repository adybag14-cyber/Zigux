const std = @import("std");
const base64 = @import("base64");

const EncodeCase = struct {
    input: []const u8,
    expected: []const u8,
    padding: bool,
    variant: base64.Variant,
};

fn expectEncode(case: EncodeCase) !void {
    var buf: [128]u8 = undefined;
    const written = try base64.encode(buf[0..], case.input, case.padding, case.variant);

    try std.testing.expectEqual(case.expected.len, written);
    try std.testing.expectEqual(case.expected.len, base64.chars(case.input.len, case.padding));
    try std.testing.expectEqualStrings(case.expected, buf[0..written]);
}

test "phase 6 base64 module imports cleanly" {
    _ = base64;
}

test "phase 6 base64 standard encode parity matches kernel vectors" {
    const cases = [_]EncodeCase{
        .{ .input = "", .expected = "", .padding = true, .variant = .std },
        .{ .input = "f", .expected = "Zg==", .padding = true, .variant = .std },
        .{ .input = "fo", .expected = "Zm8=", .padding = true, .variant = .std },
        .{ .input = "foo", .expected = "Zm9v", .padding = true, .variant = .std },
        .{ .input = "foob", .expected = "Zm9vYg==", .padding = true, .variant = .std },
        .{ .input = "fooba", .expected = "Zm9vYmE=", .padding = true, .variant = .std },
        .{ .input = "foobar", .expected = "Zm9vYmFy", .padding = true, .variant = .std },
        .{ .input = "Hello, world!", .expected = "SGVsbG8sIHdvcmxkIQ==", .padding = true, .variant = .std },
        .{ .input = "", .expected = "", .padding = false, .variant = .std },
        .{ .input = "f", .expected = "Zg", .padding = false, .variant = .std },
        .{ .input = "fo", .expected = "Zm8", .padding = false, .variant = .std },
        .{ .input = "foo", .expected = "Zm9v", .padding = false, .variant = .std },
        .{ .input = "foob", .expected = "Zm9vYg", .padding = false, .variant = .std },
        .{ .input = "fooba", .expected = "Zm9vYmE", .padding = false, .variant = .std },
        .{ .input = "foobar", .expected = "Zm9vYmFy", .padding = false, .variant = .std },
        .{ .input = "Hello, world!", .expected = "SGVsbG8sIHdvcmxkIQ", .padding = false, .variant = .std },
    };

    for (cases) |case| {
        try expectEncode(case);
    }
}

test "phase 6 base64 variant alphabets match the kernel mappings" {
    const sample = [_]u8{ 0x00, 0xfb, 0xff, 0x7f, 0x80 };
    const cases = [_]EncodeCase{
        .{ .input = &sample, .expected = "APv/f4A", .padding = false, .variant = .std },
        .{ .input = &sample, .expected = "APv_f4A", .padding = false, .variant = .urlsafe },
        .{ .input = &sample, .expected = "APv,f4A", .padding = false, .variant = .imap },
    };

    for (cases) |case| {
        try expectEncode(case);
    }
}

test "phase 6 base64 reports destination bounds before encoding" {
    var buf: [3]u8 = undefined;
    try std.testing.expectError(base64.EncodeError.DestinationTooSmall, base64.encode(buf[0..], "f", true, .std));
    try std.testing.expectError(base64.EncodeError.DestinationTooSmall, base64.encode(buf[0..], "foo", false, .std));
}
