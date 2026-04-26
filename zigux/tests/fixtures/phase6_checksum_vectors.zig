pub const ComputeCase = struct {
    name: []const u8,
    bytes: []const u8,
    expected_partial: u32,
    expected_compute: u16,
};

pub const CompositionCase = struct {
    name: []const u8,
    payload: []const u8,
    split: usize,
    expected_partial: u32,
    expected_fold: u16,
};

pub const PseudoHeaderCase = struct {
    name: []const u8,
    payload: []const u8,
    saddr: u32,
    daddr: u32,
    proto: u8,
    expected_compute: u16,
};

const ipv4_header = [_]u8{
    0x45, 0x00, 0x00, 0x3c,
    0x1c, 0x46, 0x40, 0x00,
    0x40, 0x06, 0x00, 0x00,
    0xc0, 0xa8, 0x00, 0x01,
    0xc0, 0xa8, 0x00, 0xc7,
};

const carry_payload = [_]u8{ 0xff, 0xff, 0xff, 0xff, 0x7f };

pub const compute_cases = [_]ComputeCase{
    .{
        .name = "empty",
        .bytes = "",
        .expected_partial = 0x0000,
        .expected_compute = 0xffff,
    },
    .{
        .name = "two-byte word",
        .bytes = "\x00\x01",
        .expected_partial = 0x0001,
        .expected_compute = 0xfffe,
    },
    .{
        .name = "ipv4 header",
        .bytes = &ipv4_header,
        .expected_partial = 0x63a2,
        .expected_compute = 0x9c5d,
    },
    .{
        .name = "odd payload",
        .bytes = "abcde",
        .expected_partial = 0x29c7,
        .expected_compute = 0xd638,
    },
    .{
        .name = "carry-heavy payload",
        .bytes = &carry_payload,
        .expected_partial = 0x7f00,
        .expected_compute = 0x80ff,
    },
};

pub const composition_cases = [_]CompositionCase{
    .{
        .name = "even split",
        .payload = "checksum fragments keep their carry",
        .split = 20,
        .expected_partial = 0x0e7b,
        .expected_fold = 0xf184,
    },
    .{
        .name = "odd split",
        .payload = "checksum fragments keep their carry",
        .split = 21,
        .expected_partial = 0x0e7b,
        .expected_fold = 0xf184,
    },
};

pub const pseudo_header_cases = [_]PseudoHeaderCase{
    .{
        .name = "udp pseudo header",
        .payload = "zigux checksum",
        .saddr = 0xc0a80001,
        .daddr = 0xc0a800c7,
        .proto = 17,
        .expected_compute = 0x7a1b,
    },
};
