const string_helpers = @import("string_helpers");

pub const UnescapeCase = struct {
    name: []const u8,
    input: []const u8,
    flags: u32,
    expected_len: usize,
    expected: []const u8,
};

pub const EscapeCase = struct {
    name: []const u8,
    input: []const u8,
    flags: u32,
    only: ?[]const u8,
    expected_len: usize,
    expected: []const u8,
};

pub const unescape_cases = [_]UnescapeCase{
    .{
        .name = "space escapes",
        .input = "\\f\\ \\n\\r\\t\\v",
        .flags = string_helpers.UNESCAPE_SPACE,
        .expected_len = 7,
        .expected = "\x0c\\ \n\r\t\x0b",
    },
    .{
        .name = "octal escapes",
        .input = "\\40\\1\\387\\0064\\05\\040\\8a\\110\\777",
        .flags = string_helpers.UNESCAPE_OCTAL,
        .expected_len = 15,
        .expected = " \x01\x0387\x064\x05 \\8aH?7",
    },
    .{
        .name = "hex escapes",
        .input = "\\xv\\xa\\x2c\\xD\\x6f2",
        .flags = string_helpers.UNESCAPE_HEX,
        .expected_len = 8,
        .expected = "\\xv\n,\ro2",
    },
    .{
        .name = "special escapes",
        .input = "\\h\\\\\\\"\\a\\e\\",
        .flags = string_helpers.UNESCAPE_SPECIAL,
        .expected_len = 7,
        .expected = "\\h\\\"\x07\x1b\\",
    },
    .{
        .name = "combined escape classes",
        .input = "\\n\\x41\\040\\e",
        .flags = string_helpers.UNESCAPE_ANY,
        .expected_len = 4,
        .expected = "\nA \x1b",
    },
};

pub const escape_cases = [_]EscapeCase{
    .{
        .name = "escape any subset",
        .input = "\n\\\x00",
        .flags = string_helpers.ESCAPE_ANY,
        .only = null,
        .expected_len = 6,
        .expected = "\\n\\\\\\0",
    },
    .{
        .name = "special-character escaping",
        .input = "\"\x07\x1b\\",
        .flags = string_helpers.ESCAPE_SPECIAL,
        .only = null,
        .expected_len = 8,
        .expected = "\\\"\\a\\e\\\\",
    },
    .{
        .name = "dictionary-limited space escaping",
        .input = "A\n\tZ",
        .flags = string_helpers.ESCAPE_SPACE,
        .only = "\n",
        .expected_len = 5,
        .expected = "A\\n\tZ",
    },
    .{
        .name = "append dictionary entries with hex escaping",
        .input = "A\nZ",
        .flags = string_helpers.ESCAPE_NAP | string_helpers.ESCAPE_HEX | string_helpers.ESCAPE_APPEND,
        .only = "\n",
        .expected_len = 6,
        .expected = "A\\x0aZ",
    },
    .{
        .name = "hex escapes with printable passthrough",
        .input = "A\x01z",
        .flags = string_helpers.ESCAPE_NP | string_helpers.ESCAPE_HEX,
        .only = null,
        .expected_len = 6,
        .expected = "A\\x01z",
    },
    .{
        .name = "hex escapes with ascii passthrough",
        .input = "A\x80z",
        .flags = string_helpers.ESCAPE_NA | string_helpers.ESCAPE_HEX,
        .only = null,
        .expected_len = 6,
        .expected = "A\\x80z",
    },
    .{
        .name = "hex escapes with ascii and printable passthrough",
        .input = "A\x01\x80z",
        .flags = string_helpers.ESCAPE_NAP | string_helpers.ESCAPE_HEX,
        .only = null,
        .expected_len = 10,
        .expected = "A\\x01\\x80z",
    },
};
