const builtin = @import("builtin");

pub const data_b = [_]u8{
    0xbe, 0x32, 0xdb, 0x7b, 0x0a, 0x18, 0x93, 0xb2,
    0x70, 0xba, 0xc4, 0x24, 0x7d, 0x83, 0x34, 0x9b,
    0xa6, 0x9c, 0x31, 0xad, 0x9c, 0x0f, 0xac, 0xe9,
    0x4c, 0xd1, 0x19, 0x99, 0x43, 0xb1, 0xaf, 0x0c,
};

pub const data_a = ".2.{....p..$}.4...1.....L...C...";
pub const fill_char: u8 = '#';
pub const test_hexdump_buf_size = 32 * 3 + 2 + 32 + 1;

pub const ExpectedText = struct {
    little: []const u8,
    big: []const u8,

    pub fn current(self: @This()) []const u8 {
        return if (builtin.cpu.arch.endian() == .big) self.big else self.little;
    }
};

pub const ParityCase = struct {
    name: []const u8,
    len: usize,
    rowsize: usize,
    groupsize: usize,
    ascii: bool,
    expected_length: usize,
    expected_text: ExpectedText,
};

pub const OverflowCase = struct {
    name: []const u8,
    buflen: usize,
    len: usize,
    rowsize: usize,
    groupsize: usize,
    ascii: bool,
    expected_length: usize,
    visible_text: ExpectedText,
};

fn same(text: []const u8) ExpectedText {
    return .{ .little = text, .big = text };
}

pub const parity_cases = [_]ParityCase{
    .{
        .name = "plain rowsize-16 group-1",
        .len = 16,
        .rowsize = 16,
        .groupsize = 1,
        .ascii = false,
        .expected_length = 47,
        .expected_text = same("be 32 db 7b 0a 18 93 b2 70 ba c4 24 7d 83 34 9b"),
    },
    .{
        .name = "ascii rowsize-16 group-1",
        .len = 16,
        .rowsize = 16,
        .groupsize = 1,
        .ascii = true,
        .expected_length = 65,
        .expected_text = same("be 32 db 7b 0a 18 93 b2 70 ba c4 24 7d 83 34 9b  .2.{....p..$}.4."),
    },
    .{
        .name = "plain rowsize-16 group-2",
        .len = 16,
        .rowsize = 16,
        .groupsize = 2,
        .ascii = false,
        .expected_length = 39,
        .expected_text = .{
            .little = "32be 7bdb 180a b293 ba70 24c4 837d 9b34",
            .big = "be32 db7b 0a18 93b2 70ba c424 7d83 349b",
        },
    },
    .{
        .name = "ascii rowsize-32 group-2",
        .len = 32,
        .rowsize = 32,
        .groupsize = 2,
        .ascii = true,
        .expected_length = 113,
        .expected_text = .{
            .little = "32be 7bdb 180a b293 ba70 24c4 837d 9b34 9ca6 ad31 0f9c e9ac d14c 9919 b143 0caf  .2.{....p..$}.4...1.....L...C...",
            .big = "be32 db7b 0a18 93b2 70ba c424 7d83 349b a69c 31ad 9c0f ace9 4cd1 1999 43b1 af0c  .2.{....p..$}.4...1.....L...C...",
        },
    },
    .{
        .name = "normalized rowsize and groupsize fallback",
        .len = 12,
        .rowsize = 99,
        .groupsize = 3,
        .ascii = true,
        .expected_length = 61,
        .expected_text = same("be 32 db 7b 0a 18 93 b2 70 ba c4 24              .2.{....p..$"),
    },
    .{
        .name = "normalized uneven group fallback",
        .len = 9,
        .rowsize = 32,
        .groupsize = 4,
        .ascii = false,
        .expected_length = 26,
        .expected_text = same("be 32 db 7b 0a 18 93 b2 70"),
    },
    .{
        .name = "plain rowsize-16 group-8",
        .len = 16,
        .rowsize = 16,
        .groupsize = 8,
        .ascii = false,
        .expected_length = 33,
        .expected_text = .{
            .little = "b293180a7bdb32be 9b34837d24c4ba70",
            .big = "be32db7b0a1893b2 70bac4247d83349b",
        },
    },
};

pub const overflow_cases = [_]OverflowCase{
    .{
        .name = "zero-sized caller buffer reports required ascii length",
        .buflen = 0,
        .len = 16,
        .rowsize = 7,
        .groupsize = 3,
        .ascii = true,
        .expected_length = 65,
        .visible_text = same(""),
    },
    .{
        .name = "short ascii buffer truncates but stays NUL terminated",
        .buflen = 8,
        .len = 4,
        .rowsize = 16,
        .groupsize = 1,
        .ascii = true,
        .expected_length = 53,
        .visible_text = same("be 32 d"),
    },
    .{
        .name = "grouped plain buffer truncates deterministically",
        .buflen = 20,
        .len = 16,
        .rowsize = 16,
        .groupsize = 2,
        .ascii = false,
        .expected_length = 39,
        .visible_text = .{
            .little = "32be 7bdb 180a b293",
            .big = "be32 db7b 0a18 93b2",
        },
    },
    .{
        .name = "normalized ascii buffer truncates after fallback formatting",
        .buflen = 12,
        .len = 15,
        .rowsize = 16,
        .groupsize = 8,
        .ascii = true,
        .expected_length = 64,
        .visible_text = same("be 32 db 7b"),
    },
};
