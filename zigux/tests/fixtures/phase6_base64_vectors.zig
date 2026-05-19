const std = @import("std");

pub const EncodeCase = struct {
    input: []const u8,
    expected: []const u8,
    padding: bool,
};

pub const DecodeCase = struct {
    input: []const u8,
    expected: []const u8,
    padding: bool,
    variant_name: []const u8,
};

pub const VariantCase = struct {
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

pub const PerfCase = struct {
    label: []const u8,
    payload: []const u8,
    padding: bool,
    variant_name: []const u8,
    iterations: usize,
    max_encode_slowdown_pct: u64,
    max_decode_slowdown_pct: u64,
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
    .{ .input = "ABCDEFGHIJKLMNOPQRSTUVWXYZ", .expected = "QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVo=", .padding = true },
    .{ .input = "abcdefghijklmnopqrstuvwxyz", .expected = "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo=", .padding = true },
    .{ .input = "0123456789+/", .expected = "MDEyMzQ1Njc4OSsv", .padding = true },
    .{ .input = "", .expected = "", .padding = false },
    .{ .input = "f", .expected = "Zg", .padding = false },
    .{ .input = "fo", .expected = "Zm8", .padding = false },
    .{ .input = "foo", .expected = "Zm9v", .padding = false },
    .{ .input = "foob", .expected = "Zm9vYg", .padding = false },
    .{ .input = "fooba", .expected = "Zm9vYmE", .padding = false },
    .{ .input = "foobar", .expected = "Zm9vYmFy", .padding = false },
    .{ .input = "Hello, world!", .expected = "SGVsbG8sIHdvcmxkIQ", .padding = false },
    .{ .input = "ABCDEFGHIJKLMNOPQRSTUVWXYZ", .expected = "QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVo", .padding = false },
    .{ .input = "abcdefghijklmnopqrstuvwxyz", .expected = "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo", .padding = false },
    .{ .input = "0123456789+/", .expected = "MDEyMzQ1Njc4OSsv", .padding = false },
};

pub const variant_sample = [_]u8{ 0x00, 0xfb, 0xff, 0x7f, 0x80 };
pub const variant_one_byte_sample = [_]u8{0xfb};
pub const variant_two_byte_sample = [_]u8{ 0xff, 0xf0 };

pub const variant_cases = [_]VariantCase{
    .{ .input = &variant_sample, .expected = "APv/f4A", .padding = false, .variant_name = "std" },
    .{ .input = &variant_sample, .expected = "APv/f4A=", .padding = true, .variant_name = "std" },
    .{ .input = &variant_sample, .expected = "APv_f4A", .padding = false, .variant_name = "urlsafe" },
    .{ .input = &variant_sample, .expected = "APv_f4A=", .padding = true, .variant_name = "urlsafe" },
    .{ .input = &variant_sample, .expected = "APv,f4A", .padding = false, .variant_name = "imap" },
    .{ .input = &variant_sample, .expected = "APv,f4A=", .padding = true, .variant_name = "imap" },
    .{ .input = &variant_one_byte_sample, .expected = "+w", .padding = false, .variant_name = "std" },
    .{ .input = &variant_one_byte_sample, .expected = "+w==", .padding = true, .variant_name = "std" },
    .{ .input = &variant_one_byte_sample, .expected = "-w", .padding = false, .variant_name = "urlsafe" },
    .{ .input = &variant_one_byte_sample, .expected = "-w==", .padding = true, .variant_name = "urlsafe" },
    .{ .input = &variant_one_byte_sample, .expected = "+w", .padding = false, .variant_name = "imap" },
    .{ .input = &variant_one_byte_sample, .expected = "+w==", .padding = true, .variant_name = "imap" },
    .{ .input = &variant_two_byte_sample, .expected = "//A", .padding = false, .variant_name = "std" },
    .{ .input = &variant_two_byte_sample, .expected = "//A=", .padding = true, .variant_name = "std" },
    .{ .input = &variant_two_byte_sample, .expected = "__A", .padding = false, .variant_name = "urlsafe" },
    .{ .input = &variant_two_byte_sample, .expected = "__A=", .padding = true, .variant_name = "urlsafe" },
    .{ .input = &variant_two_byte_sample, .expected = ",,A", .padding = false, .variant_name = "imap" },
    .{ .input = &variant_two_byte_sample, .expected = ",,A=", .padding = true, .variant_name = "imap" },
};

pub const standard_decode_cases = [_]DecodeCase{
    .{ .input = "", .expected = "", .padding = true, .variant_name = "std" },
    .{ .input = "Zg==", .expected = "f", .padding = true, .variant_name = "std" },
    .{ .input = "Zm8=", .expected = "fo", .padding = true, .variant_name = "std" },
    .{ .input = "Zm9v", .expected = "foo", .padding = true, .variant_name = "std" },
    .{ .input = "Zm9vYg==", .expected = "foob", .padding = true, .variant_name = "std" },
    .{ .input = "Zm9vYmE=", .expected = "fooba", .padding = true, .variant_name = "std" },
    .{ .input = "Zm9vYmFy", .expected = "foobar", .padding = true, .variant_name = "std" },
    .{ .input = "SGVsbG8sIHdvcmxkIQ==", .expected = "Hello, world!", .padding = true, .variant_name = "std" },
    .{ .input = "QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVo=", .expected = "ABCDEFGHIJKLMNOPQRSTUVWXYZ", .padding = true, .variant_name = "std" },
    .{ .input = "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo=", .expected = "abcdefghijklmnopqrstuvwxyz", .padding = true, .variant_name = "std" },
    .{ .input = "", .expected = "", .padding = false, .variant_name = "std" },
    .{ .input = "Zg", .expected = "f", .padding = false, .variant_name = "std" },
    .{ .input = "Zm8", .expected = "fo", .padding = false, .variant_name = "std" },
    .{ .input = "Zm9v", .expected = "foo", .padding = false, .variant_name = "std" },
    .{ .input = "Zm9vYg", .expected = "foob", .padding = false, .variant_name = "std" },
    .{ .input = "Zm9vYmE", .expected = "fooba", .padding = false, .variant_name = "std" },
    .{ .input = "Zm9vYmFy", .expected = "foobar", .padding = false, .variant_name = "std" },
    .{ .input = "TWFu", .expected = "Man", .padding = false, .variant_name = "std" },
    .{ .input = "SGVsbG8sIHdvcmxkIQ", .expected = "Hello, world!", .padding = false, .variant_name = "std" },
    .{ .input = "QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVo", .expected = "ABCDEFGHIJKLMNOPQRSTUVWXYZ", .padding = false, .variant_name = "std" },
    .{ .input = "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo", .expected = "abcdefghijklmnopqrstuvwxyz", .padding = false, .variant_name = "std" },
    .{ .input = "MDEyMzQ1Njc4OSsv", .expected = "0123456789+/", .padding = false, .variant_name = "std" },
};

const invalid_with_nul = [_]u8{ 'Z', 'g', 0, '=' };

pub const invalid_decode_cases = [_]InvalidDecodeCase{
    .{ .input = "Zg=!", .padding = true, .variant_name = "std" },
    .{ .input = "Zm$=", .padding = true, .variant_name = "std" },
    .{ .input = "Z===", .padding = true, .variant_name = "std" },
    .{ .input = "Zg", .padding = true, .variant_name = "std" },
    .{ .input = "Zm9v====", .padding = true, .variant_name = "std" },
    .{ .input = "Zm==A", .padding = true, .variant_name = "std" },
    .{ .input = invalid_with_nul[0..], .padding = true, .variant_name = "std" },
    .{ .input = "Zg=!", .padding = false, .variant_name = "std" },
    .{ .input = "Zm$=", .padding = false, .variant_name = "std" },
    .{ .input = "Z===", .padding = false, .variant_name = "std" },
    .{ .input = "Zg=", .padding = false, .variant_name = "std" },
    .{ .input = "Zm9v====", .padding = false, .variant_name = "std" },
    .{ .input = "Zm==v", .padding = false, .variant_name = "std" },
    .{ .input = invalid_with_nul[0..], .padding = false, .variant_name = "std" },
    .{ .input = "Zg==", .padding = false, .variant_name = "urlsafe" },
    .{ .input = "Zg==", .padding = false, .variant_name = "imap" },
};

pub const variant_decode_cases = [_]DecodeCase{
    .{ .input = "APv_f4A", .expected = &variant_sample, .padding = false, .variant_name = "urlsafe" },
    .{ .input = "APv_f4A=", .expected = &variant_sample, .padding = true, .variant_name = "urlsafe" },
    .{ .input = "APv,f4A", .expected = &variant_sample, .padding = false, .variant_name = "imap" },
    .{ .input = "APv,f4A=", .expected = &variant_sample, .padding = true, .variant_name = "imap" },
    .{ .input = "-w", .expected = &variant_one_byte_sample, .padding = false, .variant_name = "urlsafe" },
    .{ .input = "-w==", .expected = &variant_one_byte_sample, .padding = true, .variant_name = "urlsafe" },
    .{ .input = "+w", .expected = &variant_one_byte_sample, .padding = false, .variant_name = "imap" },
    .{ .input = "+w==", .expected = &variant_one_byte_sample, .padding = true, .variant_name = "imap" },
    .{ .input = "__A", .expected = &variant_two_byte_sample, .padding = false, .variant_name = "urlsafe" },
    .{ .input = "__A=", .expected = &variant_two_byte_sample, .padding = true, .variant_name = "urlsafe" },
    .{ .input = ",,A", .expected = &variant_two_byte_sample, .padding = false, .variant_name = "imap" },
    .{ .input = ",,A=", .expected = &variant_two_byte_sample, .padding = true, .variant_name = "imap" },
};

pub const perf_payload =
    "Phase 6 base64 perf gate payload keeps the helper wired to a real throughput check. " ++
    "This packet stays helper-local, avoids widening into neighboring leaf helpers, and " ++
    "exercises repeated encode and decode work over a stable review fixture. " ++
    "Zigux uses the same payload for padded and unpadded standard, urlsafe, and imap runs.";

pub const perf_cases = [_]PerfCase{
    .{ .label = "STD_PAD", .payload = perf_payload, .padding = true, .variant_name = "std", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
    .{ .label = "STD_NO_PAD", .payload = perf_payload, .padding = false, .variant_name = "std", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
    .{ .label = "URLSAFE_PAD", .payload = perf_payload, .padding = true, .variant_name = "urlsafe", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
    .{ .label = "URLSAFE_NO_PAD", .payload = perf_payload, .padding = false, .variant_name = "urlsafe", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
    .{ .label = "IMAP_PAD", .payload = perf_payload, .padding = true, .variant_name = "imap", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
    .{ .label = "IMAP_NO_PAD", .payload = perf_payload, .padding = false, .variant_name = "imap", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
};

pub const perf_payload_buf_size = perf_payload.len;
pub const perf_encoded_buf_size = 512;

fn encodedChars(nbytes: usize, padding: bool) usize {
    const full_groups = (nbytes / 3) * 4;
    if (padding) {
        return full_groups + (if (nbytes % 3 == 0) @as(usize, 0) else @as(usize, 4));
    }

    return full_groups + switch (nbytes % 3) {
        0 => @as(usize, 0),
        1 => @as(usize, 2),
        2 => @as(usize, 3),
        else => unreachable,
    };
}

test "phase 6 base64 perf fixture packet stays bounded to the documented matrix" {
    const expected_case_count = 6;
    const expected_iterations = 12_000;
    const expected_max_encode_slowdown_pct = 150;
    const expected_max_decode_slowdown_pct = 325;

    var saw_std_pad = false;
    var saw_std_no_pad = false;
    var saw_urlsafe_pad = false;
    var saw_urlsafe_no_pad = false;
    var saw_imap_pad = false;
    var saw_imap_no_pad = false;

    try std.testing.expectEqual(expected_case_count, perf_cases.len);
    try std.testing.expectEqual(perf_payload.len, perf_payload_buf_size);

    for (perf_cases, 0..) |case, idx| {
        try std.testing.expectEqualStrings(perf_payload, case.payload);
        try std.testing.expectEqual(expected_iterations, case.iterations);
        try std.testing.expectEqual(expected_max_encode_slowdown_pct, case.max_encode_slowdown_pct);
        try std.testing.expectEqual(expected_max_decode_slowdown_pct, case.max_decode_slowdown_pct);
        try std.testing.expect(perf_payload_buf_size >= case.payload.len);
        try std.testing.expect(perf_encoded_buf_size >= encodedChars(case.payload.len, case.padding));

        if (std.mem.eql(u8, case.variant_name, "std")) {
            if (case.padding) {
                try std.testing.expectEqualStrings("STD_PAD", case.label);
                try std.testing.expect(!saw_std_pad);
                saw_std_pad = true;
            } else {
                try std.testing.expectEqualStrings("STD_NO_PAD", case.label);
                try std.testing.expect(!saw_std_no_pad);
                saw_std_no_pad = true;
            }
        } else if (std.mem.eql(u8, case.variant_name, "urlsafe")) {
            if (case.padding) {
                try std.testing.expectEqualStrings("URLSAFE_PAD", case.label);
                try std.testing.expect(!saw_urlsafe_pad);
                saw_urlsafe_pad = true;
            } else {
                try std.testing.expectEqualStrings("URLSAFE_NO_PAD", case.label);
                try std.testing.expect(!saw_urlsafe_no_pad);
                saw_urlsafe_no_pad = true;
            }
        } else if (std.mem.eql(u8, case.variant_name, "imap")) {
            if (case.padding) {
                try std.testing.expectEqualStrings("IMAP_PAD", case.label);
                try std.testing.expect(!saw_imap_pad);
                saw_imap_pad = true;
            } else {
                try std.testing.expectEqualStrings("IMAP_NO_PAD", case.label);
                try std.testing.expect(!saw_imap_no_pad);
                saw_imap_no_pad = true;
            }
        } else {
            try std.testing.expect(false);
        }

        for (perf_cases[idx + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, case.label, other.label));
        }
    }

    try std.testing.expect(saw_std_pad);
    try std.testing.expect(saw_std_no_pad);
    try std.testing.expect(saw_urlsafe_pad);
    try std.testing.expect(saw_urlsafe_no_pad);
    try std.testing.expect(saw_imap_pad);
    try std.testing.expect(saw_imap_no_pad);
}
