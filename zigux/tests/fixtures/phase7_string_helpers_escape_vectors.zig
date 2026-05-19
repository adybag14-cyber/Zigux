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
        .flags = 1 << 0,
        .expected_len = 7,
        .expected = "\x0c\\ \n\r\t\x0b",
    },
    .{
        .name = "octal escapes",
        .input = "\\40\\1\\387\\0064\\05\\040\\8a\\110\\777",
        .flags = 1 << 1,
        .expected_len = 15,
        .expected = " \x01\x0387\x064\x05 \\8aH?7",
    },
    .{
        .name = "hex escapes",
        .input = "\\xv\\xa\\x2c\\xD\\x6f2",
        .flags = 1 << 2,
        .expected_len = 8,
        .expected = "\\xv\n,\ro2",
    },
    .{
        .name = "special escapes",
        .input = "\\h\\\\\\\"\\a\\e\\",
        .flags = 1 << 3,
        .expected_len = 7,
        .expected = "\\h\\\"\x07\x1b\\",
    },
    .{
        .name = "combined escape classes",
        .input = "\\n\\x41\\040\\e",
        .flags = (1 << 0) | (1 << 1) | (1 << 2) | (1 << 3),
        .expected_len = 4,
        .expected = "\nA \x1b",
    },
    .{
        .name = "sample replay newline suffix",
        .input = "line\\n",
        .flags = 1 << 0,
        .expected_len = 5,
        .expected = "line\n",
    },
    .{
        .name = "sample replay exact-fit newline",
        .input = "\\n",
        .flags = 1 << 0,
        .expected_len = 1,
        .expected = "\n",
    },
};

pub const escape_cases = [_]EscapeCase{
    .{
        .name = "escape any subset",
        .input = "\n\\\x00",
        .flags = (1 << 0) | (1 << 1) | (1 << 2) | (1 << 3),
        .only = null,
        .expected_len = 6,
        .expected = "\\n\\\\\\0",
    },
    .{
        .name = "dictionary-limited space escaping",
        .input = "A\n\tZ",
        .flags = 1 << 0,
        .only = "\n",
        .expected_len = 5,
        .expected = "A\\n\tZ",
    },
    .{
        .name = "append dictionary entries with hex escaping",
        .input = "A\nZ",
        .flags = (1 << 7) | (1 << 5) | (1 << 8),
        .only = "\n",
        .expected_len = 6,
        .expected = "A\\x0aZ",
    },
    .{
        .name = "sample replay newline hex escape",
        .input = "\n",
        .flags = 1 << 5,
        .only = null,
        .expected_len = 4,
        .expected = "\\x0a",
    },
    .{
        .name = "hex escapes with printable passthrough",
        .input = "A\x01z",
        .flags = (1 << 4) | (1 << 5),
        .only = null,
        .expected_len = 6,
        .expected = "A\\x01z",
    },
    .{
        .name = "hex escapes with ascii passthrough",
        .input = "A\x80z",
        .flags = (1 << 6) | (1 << 5),
        .only = null,
        .expected_len = 6,
        .expected = "A\\x80z",
    },
    .{
        .name = "hex escapes with ascii and printable passthrough",
        .input = "A\x01\x80z",
        .flags = (1 << 7) | (1 << 5),
        .only = null,
        .expected_len = 10,
        .expected = "A\\x01\\x80z",
    },
};