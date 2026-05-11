pub const ArgvSplitCase = struct {
    name: []const u8,
    input: []const u8,
    expected: []const []const u8,
};

const whitespace_expected = [_][]const u8{
    "init=/init",
    "console=ttyS0",
    "panic=-1",
};

const blank_expected = [_][]const u8{};

const leading_nul_expected = [_][]const u8{};

const nul_expected = [_][]const u8{
    "root=/dev/vda",
    "rw",
};

const quote_expected = [_][]const u8{
    "root=\"/dev/sda",
    "1\"",
    "single",
};

pub const argv_split_cases = [_]ArgvSplitCase{
    .{
        .name = "repeated whitespace collapses into separators",
        .input = " init=/init   console=ttyS0\tpanic=-1 ",
        .expected = &whitespace_expected,
    },
    .{
        .name = "blank input stays empty",
        .input = " \t\n",
        .expected = &blank_expected,
    },
    .{
        .name = "whitespace before first NUL stays blank",
        .input = " \t\n\x00ignored debug",
        .expected = &blank_expected,
    },
    .{
        .name = "leading NUL truncates to zero argv entries",
        .input = "\x00ignored debug",
        .expected = &leading_nul_expected,
    },
    .{
        .name = "first NUL stops counting and splitting",
        .input = "root=/dev/vda rw\x00ignored debug",
        .expected = &nul_expected,
    },
    .{
        .name = "quote characters stay inside returned tokens",
        .input = "root=\"/dev/sda 1\" single",
        .expected = &quote_expected,
    },
};
