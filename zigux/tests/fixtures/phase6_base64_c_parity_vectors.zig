const std = @import("std");

pub const EncodeCase = struct {
    input: []const u8,
    expected: []const u8,
    padding: bool,
};

pub const VariantCase = struct {
    input: []const u8,
    expected: []const u8,
    padding: bool,
    variant_name: []const u8,
};

pub const DecodeCase = struct {
    input: []const u8,
    expected: []const u8,
    padding: bool,
    variant_name: []const u8,
};

pub const InvalidDecodeCase = struct {
    input: []const u8,
    padding: bool,
    variant_name: []const u8,
};

const empty = [_]u8{};
const one_byte_fb = [_]u8{0xfb};
const three_ff = [_]u8{ 0xfb, 0xff, 0xff };
const invalid_with_nul = [_]u8{ 'Z', 'g', 0, '=' };

pub const standard_cases = [_]EncodeCase{
    .{ .input = empty[0..], .expected = "", .padding = true },
    .{ .input = "f", .expected = "Zg==", .padding = true },
    .{ .input = "fo", .expected = "Zm8=", .padding = true },
    .{ .input = "foo", .expected = "Zm9v", .padding = true },
};

pub const variant_cases = [_]VariantCase{
    .{ .input = &one_byte_fb, .expected = "-w", .padding = false, .variant_name = "urlsafe" },
    .{ .input = &one_byte_fb, .expected = "-w==", .padding = true, .variant_name = "urlsafe" },
    .{ .input = &one_byte_fb, .expected = "+w==", .padding = true, .variant_name = "imap" },
    .{ .input = &three_ff, .expected = "+,,,", .padding = false, .variant_name = "imap" },
};

pub const standard_decode_cases = [_]DecodeCase{
    .{ .input = "", .expected = empty[0..], .padding = true, .variant_name = "std" },
    .{ .input = "Zg==", .expected = "f", .padding = true, .variant_name = "std" },
    .{ .input = "Zm8=", .expected = "fo", .padding = true, .variant_name = "std" },
    .{ .input = "Zm9v", .expected = "foo", .padding = true, .variant_name = "std" },
};

pub const variant_decode_cases = [_]DecodeCase{
    .{ .input = "-w", .expected = &one_byte_fb, .padding = false, .variant_name = "urlsafe" },
    .{ .input = "-w==", .expected = &one_byte_fb, .padding = true, .variant_name = "urlsafe" },
    .{ .input = "+w==", .expected = &one_byte_fb, .padding = true, .variant_name = "imap" },
    .{ .input = "+,,,", .expected = &three_ff, .padding = false, .variant_name = "imap" },
};

pub const invalid_decode_cases = [_]InvalidDecodeCase{
    .{ .input = "A", .padding = false, .variant_name = "std" },
    .{ .input = "AA=A", .padding = true, .variant_name = "std" },
    .{ .input = "AR==", .padding = true, .variant_name = "std" },
    .{ .input = "aGl=", .padding = true, .variant_name = "std" },
    .{ .input = "-___", .padding = false, .variant_name = "std" },
    .{ .input = "+///", .padding = false, .variant_name = "urlsafe" },
    .{ .input = "+///", .padding = false, .variant_name = "imap" },
    .{ .input = invalid_with_nul[0..], .padding = true, .variant_name = "std" },
};

test "phase6 base64 direct parity corpus stays compact and portable" {
    try std.testing.expectEqual(@as(usize, 4), standard_cases.len);
    try std.testing.expectEqual(@as(usize, 4), variant_cases.len);
    try std.testing.expectEqual(@as(usize, 4), standard_decode_cases.len);
    try std.testing.expectEqual(@as(usize, 4), variant_decode_cases.len);
    try std.testing.expectEqual(@as(usize, 8), invalid_decode_cases.len);
}
