const std = @import("std");

pub const Variant = enum {
    std,
    urlsafe,
    imap,
};

pub const EncodeCase = struct {
    variant: Variant,
    padding: bool,
    input: []const u8,
};

pub const DecodeCase = struct {
    variant: Variant,
    padding: bool,
    input: []const u8,
};

pub const InvalidCase = struct {
    variant: Variant,
    padding: bool,
    input: []const u8,
};

pub const empty_input = "";
pub const one_byte = "f";
pub const two_bytes = "fo";
pub const foobar = "foobar";
pub const hello_world = "Hello, world!";
pub const variant_sample = [_]u8{ 0x00, 0xfb, 0xff, 0x7f, 0x80 };
pub const variant_one_byte = [_]u8{0xfb};
pub const variant_two_byte = [_]u8{ 0xff, 0xf0 };
pub const invalid_with_nul = [_]u8{ 'Z', 'g', 0, '=' };

pub const encode_cases = [_]EncodeCase{
    .{ .variant = .std, .padding = true, .input = empty_input },
    .{ .variant = .std, .padding = true, .input = one_byte },
    .{ .variant = .std, .padding = true, .input = two_bytes },
    .{ .variant = .std, .padding = false, .input = foobar },
    .{ .variant = .std, .padding = true, .input = hello_world },
    .{ .variant = .urlsafe, .padding = false, .input = &variant_sample },
    .{ .variant = .urlsafe, .padding = true, .input = &variant_sample },
    .{ .variant = .urlsafe, .padding = false, .input = &variant_one_byte },
    .{ .variant = .urlsafe, .padding = true, .input = &variant_one_byte },
    .{ .variant = .urlsafe, .padding = false, .input = &variant_two_byte },
    .{ .variant = .urlsafe, .padding = true, .input = &variant_two_byte },
    .{ .variant = .imap, .padding = false, .input = &variant_sample },
    .{ .variant = .imap, .padding = true, .input = &variant_sample },
    .{ .variant = .imap, .padding = false, .input = &variant_one_byte },
    .{ .variant = .imap, .padding = true, .input = &variant_one_byte },
    .{ .variant = .imap, .padding = false, .input = &variant_two_byte },
    .{ .variant = .imap, .padding = true, .input = &variant_two_byte },
};

pub const decode_cases = [_]DecodeCase{
    .{ .variant = .std, .padding = true, .input = "" },
    .{ .variant = .std, .padding = true, .input = "Zg==" },
    .{ .variant = .std, .padding = true, .input = "Zm8=" },
    .{ .variant = .std, .padding = false, .input = "Zm9vYmFy" },
    .{ .variant = .std, .padding = true, .input = "SGVsbG8sIHdvcmxkIQ==" },
    .{ .variant = .urlsafe, .padding = false, .input = "APv_f4A" },
    .{ .variant = .urlsafe, .padding = true, .input = "APv_f4A=" },
    .{ .variant = .urlsafe, .padding = false, .input = "-w" },
    .{ .variant = .urlsafe, .padding = true, .input = "-w==" },
    .{ .variant = .urlsafe, .padding = false, .input = "__A" },
    .{ .variant = .urlsafe, .padding = true, .input = "__A=" },
    .{ .variant = .imap, .padding = false, .input = "APv,f4A" },
    .{ .variant = .imap, .padding = true, .input = "APv,f4A=" },
    .{ .variant = .imap, .padding = false, .input = "+w" },
    .{ .variant = .imap, .padding = true, .input = "+w==" },
    .{ .variant = .imap, .padding = false, .input = ",,A" },
    .{ .variant = .imap, .padding = true, .input = ",,A=" },
};

pub const invalid_cases = [_]InvalidCase{
    .{ .variant = .std, .padding = true, .input = "Zg=!" },
    .{ .variant = .std, .padding = true, .input = "Z===" },
    .{ .variant = .std, .padding = false, .input = "Zm9v====" },
    .{ .variant = .std, .padding = true, .input = &invalid_with_nul },
    .{ .variant = .urlsafe, .padding = false, .input = "Zg==" },
    .{ .variant = .imap, .padding = false, .input = "Zg==" },
};

pub fn variantName(variant: Variant) []const u8 {
    return switch (variant) {
        .std => "std",
        .urlsafe => "urlsafe",
        .imap => "imap",
    };
}

test "base64 c parity corpus counts stay pinned" {
    try std.testing.expectEqual(@as(usize, 17), encode_cases.len);
    try std.testing.expectEqual(@as(usize, 17), decode_cases.len);
    try std.testing.expectEqual(@as(usize, 6), invalid_cases.len);
}

test "base64 c parity corpus keeps the three variant names" {
    try std.testing.expectEqualStrings("std", variantName(.std));
    try std.testing.expectEqualStrings("urlsafe", variantName(.urlsafe));
    try std.testing.expectEqualStrings("imap", variantName(.imap));
}
