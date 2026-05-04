pub const NextArgCase = struct {
    name: []const u8,
    input: []const u8,
    expected_param: []const u8,
    expected_value: ?[]const u8,
    expected_rest: []const u8,
};

pub const next_arg_cases = [_]NextArgCase{
    .{
        .name = "quoted value with trailing token",
        .input = "root=\"/dev/sda 1\" ro",
        .expected_param = "root",
        .expected_value = "/dev/sda 1",
        .expected_rest = "ro",
    },
    .{
        .name = "quoted bare token with trailing token",
        .input = "\"noparam value\" next",
        .expected_param = "noparam value",
        .expected_value = null,
        .expected_rest = "next",
    },
    .{
        .name = "unquoted value keeps punctuation until whitespace",
        .input = "console=ttyS0,115200n8 panic=-1",
        .expected_param = "console",
        .expected_value = "ttyS0,115200n8",
        .expected_rest = "panic=-1",
    },
    .{
        .name = "empty quoted value becomes empty string",
        .input = "rdinit=\"\" quiet",
        .expected_param = "rdinit",
        .expected_value = "",
        .expected_rest = "quiet",
    },
    .{
        .name = "first equals wins inside the value",
        .input = "key=alpha=beta tail",
        .expected_param = "key",
        .expected_value = "alpha=beta",
        .expected_rest = "tail",
    },
    .{
        .name = "quoted value without trailing token leaves empty rest",
        .input = "mode=\"fast boot\"",
        .expected_param = "mode",
        .expected_value = "fast boot",
        .expected_rest = "",
    },
    .{
        .name = "unterminated quoted value consumes the token tail",
        .input = "mode=\"fast boot",
        .expected_param = "mode",
        .expected_value = "fast boot",
        .expected_rest = "",
    },
    .{
        .name = "leading equals sign stays in the parameter token",
        .input = "=bad next",
        .expected_param = "=bad",
        .expected_value = null,
        .expected_rest = "next",
    },
    .{
        .name = "trailing spaces after key=value trim to empty rest",
        .input = "mode=fast   ",
        .expected_param = "mode",
        .expected_value = "fast",
        .expected_rest = "",
    },
};
