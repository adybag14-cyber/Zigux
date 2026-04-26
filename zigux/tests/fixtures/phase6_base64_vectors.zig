pub const EncodeCase = struct {
    input: []const u8,
    expected: []const u8,
    padding: bool,
};

pub const VariantCase = struct {
    expected: []const u8,
    variant_name: []const u8,
};

pub const standard_cases = [_]EncodeCase{
    .{ .input = "", .expected = "", .padding = true },
    .{ .input = "f", .expected = "Zg==", .padding = true },
    .{ .input = "fo", .expected = "Zm8=", .padding = true },
    .{ .input = "foo", .expected = "Zm9v", .padding = true },
    .{ .input = "foob", .expected = "Zm9vYg==", .padding = true },
    .{ .input = "fooba", .expected = "Zm9vYmE=", .padding = true },
    .{ .input = "foobar", .expected = "Zm9vYmFy", .padding = true },
    .{ .input = "Hello, world!", .expected = "SGVsbG8sIHdvcmxkIQ==", .padding = true },
    .{ .input = "", .expected = "", .padding = false },
    .{ .input = "f", .expected = "Zg", .padding = false },
    .{ .input = "fo", .expected = "Zm8", .padding = false },
    .{ .input = "foo", .expected = "Zm9v", .padding = false },
    .{ .input = "foob", .expected = "Zm9vYg", .padding = false },
    .{ .input = "fooba", .expected = "Zm9vYmE", .padding = false },
    .{ .input = "foobar", .expected = "Zm9vYmFy", .padding = false },
    .{ .input = "Hello, world!", .expected = "SGVsbG8sIHdvcmxkIQ", .padding = false },
};

pub const variant_sample = [_]u8{ 0x00, 0xfb, 0xff, 0x7f, 0x80 };

pub const variant_cases = [_]VariantCase{
    .{ .expected = "APv/f4A", .variant_name = "std" },
    .{ .expected = "APv_f4A", .variant_name = "urlsafe" },
    .{ .expected = "APv,f4A", .variant_name = "imap" },
};
