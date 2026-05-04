const std = @import("std");
const base64 = @import("base64");

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

pub const PerfPayloadCase = struct {
    label: []const u8,
    size: usize,
    reps: usize,
};

pub const ReferenceKind = enum {
    standard,
    url_safe_padded,
    url_safe_no_pad,
    imap_padded,
    imap_no_pad,
};

pub const PerfCase = struct {
    label: []const u8,
    size: usize,
    reps: usize,
    max_encode_slowdown_pct: u16,
    max_decode_slowdown_pct: u16,
    padding: bool,
    variant: base64.Variant,
    reference_kind: ReferenceKind,
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
pub const multi_quartet_variant_sample = [_]u8{ 0xfb, 0xff, 0xef, 0xff, 0xf0 };
pub const long_multi_quartet_variant_sample = [_]u8{ 0xfb, 0xff, 0xef, 0xff, 0xf0, 0xfb, 0xff };

pub const variant_cases = [_]VariantCase{
    .{ .input = &variant_sample, .expected = "APv/f4A", .padding = false, .variant_name = "std" },
    .{ .input = &variant_sample, .expected = "APv/f4A=", .padding = true, .variant_name = "std" },
    .{ .input = &variant_sample, .expected = "APv_f4A", .padding = false, .variant_name = "urlsafe" },
    .{ .input = &variant_sample, .expected = "APv_f4A=", .padding = true, .variant_name = "urlsafe" },
    .{ .input = &variant_sample, .expected = "APv,f4A", .padding = false, .variant_name = "imap" },
    .{ .input = &variant_sample, .expected = "APv,f4A=", .padding = true, .variant_name = "imap" },
    .{ .input = &multi_quartet_variant_sample, .expected = "+//v//A", .padding = false, .variant_name = "std" },
    .{ .input = &multi_quartet_variant_sample, .expected = "+//v//A=", .padding = true, .variant_name = "std" },
    .{ .input = &multi_quartet_variant_sample, .expected = "-__v__A", .padding = false, .variant_name = "urlsafe" },
    .{ .input = &multi_quartet_variant_sample, .expected = "-__v__A=", .padding = true, .variant_name = "urlsafe" },
    .{ .input = &multi_quartet_variant_sample, .expected = "+,,v,,A", .padding = false, .variant_name = "imap" },
    .{ .input = &multi_quartet_variant_sample, .expected = "+,,v,,A=", .padding = true, .variant_name = "imap" },
    .{ .input = &long_multi_quartet_variant_sample, .expected = "+//v//D7/w", .padding = false, .variant_name = "std" },
    .{ .input = &long_multi_quartet_variant_sample, .expected = "+//v//D7/w==", .padding = true, .variant_name = "std" },
    .{ .input = &long_multi_quartet_variant_sample, .expected = "-__v__D7_w", .padding = false, .variant_name = "urlsafe" },
    .{ .input = &long_multi_quartet_variant_sample, .expected = "-__v__D7_w==", .padding = true, .variant_name = "urlsafe" },
    .{ .input = &long_multi_quartet_variant_sample, .expected = "+,,v,,D7,w", .padding = false, .variant_name = "imap" },
    .{ .input = &long_multi_quartet_variant_sample, .expected = "+,,v,,D7,w==", .padding = true, .variant_name = "imap" },
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
    .{ .input = "MDEyMzQ1Njc4OSsv", .expected = "0123456789+/", .padding = true, .variant_name = "std" },
    .{ .input = "", .expected = "", .padding = false, .variant_name = "std" },
    .{ .input = "Zg", .expected = "f", .padding = false, .variant_name = "std" },
    .{ .input = "Zm8", .expected = "fo", .padding = false, .variant_name = "std" },
    .{ .input = "Zm9v", .expected = "foo", .padding = false, .variant_name = "std" },
    .{ .input = "Zm9vYg", .expected = "foob", .padding = false, .variant_name = "std" },
    .{ .input = "Zm9vYmE", .expected = "fooba", .padding = false, .variant_name = "std" },
    .{ .input = "Zm9vYmFy", .expected = "foobar", .padding = false, .variant_name = "std" },
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
    .{ .input = "Zh==", .padding = true, .variant_name = "std" },
    .{ .input = "Zm9v====", .padding = true, .variant_name = "std" },
    .{ .input = "Zm==A", .padding = true, .variant_name = "std" },
    .{ .input = "//B=", .padding = true, .variant_name = "std" },
    .{ .input = invalid_with_nul[0..], .padding = true, .variant_name = "std" },
    .{ .input = "Zg=!", .padding = false, .variant_name = "std" },
    .{ .input = "Zm$=", .padding = false, .variant_name = "std" },
    .{ .input = "Z===", .padding = false, .variant_name = "std" },
    .{ .input = "Zg=", .padding = false, .variant_name = "std" },
    .{ .input = "Zm9v====", .padding = false, .variant_name = "std" },
    .{ .input = "Zm==v", .padding = false, .variant_name = "std" },
    .{ .input = "Zh", .padding = false, .variant_name = "std" },
    .{ .input = "//B", .padding = false, .variant_name = "std" },
    .{ .input = invalid_with_nul[0..], .padding = false, .variant_name = "std" },
    .{ .input = "Zg==", .padding = false, .variant_name = "urlsafe" },
    .{ .input = "-x==", .padding = true, .variant_name = "urlsafe" },
    .{ .input = "-x", .padding = false, .variant_name = "urlsafe" },
    .{ .input = "__B=", .padding = true, .variant_name = "urlsafe" },
    .{ .input = "__B", .padding = false, .variant_name = "urlsafe" },
    .{ .input = "Zg==", .padding = false, .variant_name = "imap" },
    .{ .input = "+x==", .padding = true, .variant_name = "imap" },
    .{ .input = "+x", .padding = false, .variant_name = "imap" },
    .{ .input = ",,B=", .padding = true, .variant_name = "imap" },
    .{ .input = ",,B", .padding = false, .variant_name = "imap" },
};

pub const variant_decode_cases = [_]DecodeCase{
    .{ .input = "APv_f4A", .expected = &variant_sample, .padding = false, .variant_name = "urlsafe" },
    .{ .input = "APv_f4A=", .expected = &variant_sample, .padding = true, .variant_name = "urlsafe" },
    .{ .input = "APv,f4A", .expected = &variant_sample, .padding = false, .variant_name = "imap" },
    .{ .input = "APv,f4A=", .expected = &variant_sample, .padding = true, .variant_name = "imap" },
    .{ .input = "-__v__A", .expected = &multi_quartet_variant_sample, .padding = false, .variant_name = "urlsafe" },
    .{ .input = "-__v__A=", .expected = &multi_quartet_variant_sample, .padding = true, .variant_name = "urlsafe" },
    .{ .input = "+,,v,,A", .expected = &multi_quartet_variant_sample, .padding = false, .variant_name = "imap" },
    .{ .input = "+,,v,,A=", .expected = &multi_quartet_variant_sample, .padding = true, .variant_name = "imap" },
    .{ .input = "-__v__D7_w", .expected = &long_multi_quartet_variant_sample, .padding = false, .variant_name = "urlsafe" },
    .{ .input = "-__v__D7_w==", .expected = &long_multi_quartet_variant_sample, .padding = true, .variant_name = "urlsafe" },
    .{ .input = "+,,v,,D7,w", .expected = &long_multi_quartet_variant_sample, .padding = false, .variant_name = "imap" },
    .{ .input = "+,,v,,D7,w==", .expected = &long_multi_quartet_variant_sample, .padding = true, .variant_name = "imap" },
    .{ .input = "-w", .expected = &variant_one_byte_sample, .padding = false, .variant_name = "urlsafe" },
    .{ .input = "-w==", .expected = &variant_one_byte_sample, .padding = true, .variant_name = "urlsafe" },
    .{ .input = "+w", .expected = &variant_one_byte_sample, .padding = false, .variant_name = "imap" },
    .{ .input = "+w==", .expected = &variant_one_byte_sample, .padding = true, .variant_name = "imap" },
    .{ .input = "__A", .expected = &variant_two_byte_sample, .padding = false, .variant_name = "urlsafe" },
    .{ .input = "__A=", .expected = &variant_two_byte_sample, .padding = true, .variant_name = "urlsafe" },
    .{ .input = ",,A", .expected = &variant_two_byte_sample, .padding = false, .variant_name = "imap" },
    .{ .input = ",,A=", .expected = &variant_two_byte_sample, .padding = true, .variant_name = "imap" },
};

pub const perf_payload_cases = [_]PerfPayloadCase{
    .{ .label = "64B", .size = 64, .reps = 20_000 },
    .{ .label = "1KB", .size = 1024, .reps = 4_000 },
};

pub const perf_cases = [_]PerfCase{
    .{ .label = "std-64B", .size = perf_payload_cases[0].size, .reps = perf_payload_cases[0].reps, .max_encode_slowdown_pct = 190, .max_decode_slowdown_pct = 320, .padding = true, .variant = .std, .reference_kind = .standard },
    .{ .label = "std-1KB", .size = perf_payload_cases[1].size, .reps = perf_payload_cases[1].reps, .max_encode_slowdown_pct = 190, .max_decode_slowdown_pct = 320, .padding = true, .variant = .std, .reference_kind = .standard },
    .{ .label = "urlsafe-padded-64B", .size = perf_payload_cases[0].size, .reps = perf_payload_cases[0].reps, .max_encode_slowdown_pct = 190, .max_decode_slowdown_pct = 320, .padding = true, .variant = .urlsafe, .reference_kind = .url_safe_padded },
    .{ .label = "urlsafe-padded-1KB", .size = perf_payload_cases[1].size, .reps = perf_payload_cases[1].reps, .max_encode_slowdown_pct = 190, .max_decode_slowdown_pct = 320, .padding = true, .variant = .urlsafe, .reference_kind = .url_safe_padded },
    .{ .label = "urlsafe-64B", .size = perf_payload_cases[0].size, .reps = perf_payload_cases[0].reps, .max_encode_slowdown_pct = 190, .max_decode_slowdown_pct = 320, .padding = false, .variant = .urlsafe, .reference_kind = .url_safe_no_pad },
    .{ .label = "urlsafe-1KB", .size = perf_payload_cases[1].size, .reps = perf_payload_cases[1].reps, .max_encode_slowdown_pct = 190, .max_decode_slowdown_pct = 320, .padding = false, .variant = .urlsafe, .reference_kind = .url_safe_no_pad },
    .{ .label = "imap-padded-64B", .size = perf_payload_cases[0].size, .reps = perf_payload_cases[0].reps, .max_encode_slowdown_pct = 190, .max_decode_slowdown_pct = 320, .padding = true, .variant = .imap, .reference_kind = .imap_padded },
    .{ .label = "imap-padded-1KB", .size = perf_payload_cases[1].size, .reps = perf_payload_cases[1].reps, .max_encode_slowdown_pct = 190, .max_decode_slowdown_pct = 320, .padding = true, .variant = .imap, .reference_kind = .imap_padded },
    .{ .label = "imap-64B", .size = perf_payload_cases[0].size, .reps = perf_payload_cases[0].reps, .max_encode_slowdown_pct = 190, .max_decode_slowdown_pct = 320, .padding = false, .variant = .imap, .reference_kind = .imap_no_pad },
    .{ .label = "imap-1KB", .size = perf_payload_cases[1].size, .reps = perf_payload_cases[1].reps, .max_encode_slowdown_pct = 190, .max_decode_slowdown_pct = 320, .padding = false, .variant = .imap, .reference_kind = .imap_no_pad },
};

pub fn expectPerfCases() !void {
    try std.testing.expectEqual(@as(usize, 10), perf_cases.len);

    const expected = [_]PerfCase{
        .{ .label = "std-64B", .size = 64, .reps = 20_000, .max_encode_slowdown_pct = 190, .max_decode_slowdown_pct = 320, .padding = true, .variant = .std, .reference_kind = .standard },
        .{ .label = "std-1KB", .size = 1024, .reps = 4_000, .max_encode_slowdown_pct = 190, .max_decode_slowdown_pct = 320, .padding = true, .variant = .std, .reference_kind = .standard },
        .{ .label = "urlsafe-padded-64B", .size = 64, .reps = 20_000, .max_encode_slowdown_pct = 190, .max_decode_slowdown_pct = 320, .padding = true, .variant = .urlsafe, .reference_kind = .url_safe_padded },
        .{ .label = "urlsafe-padded-1KB", .size = 1024, .reps = 4_000, .max_encode_slowdown_pct = 190, .max_decode_slowdown_pct = 320, .padding = true, .variant = .urlsafe, .reference_kind = .url_safe_padded },
        .{ .label = "urlsafe-64B", .size = 64, .reps = 20_000, .max_encode_slowdown_pct = 190, .max_decode_slowdown_pct = 320, .padding = false, .variant = .urlsafe, .reference_kind = .url_safe_no_pad },
        .{ .label = "urlsafe-1KB", .size = 1024, .reps = 4_000, .max_encode_slowdown_pct = 190, .max_decode_slowdown_pct = 320, .padding = false, .variant = .urlsafe, .reference_kind = .url_safe_no_pad },
        .{ .label = "imap-padded-64B", .size = 64, .reps = 20_000, .max_encode_slowdown_pct = 190, .max_decode_slowdown_pct = 320, .padding = true, .variant = .imap, .reference_kind = .imap_padded },
        .{ .label = "imap-padded-1KB", .size = 1024, .reps = 4_000, .max_encode_slowdown_pct = 190, .max_decode_slowdown_pct = 320, .padding = true, .variant = .imap, .reference_kind = .imap_padded },
        .{ .label = "imap-64B", .size = 64, .reps = 20_000, .max_encode_slowdown_pct = 190, .max_decode_slowdown_pct = 320, .padding = false, .variant = .imap, .reference_kind = .imap_no_pad },
        .{ .label = "imap-1KB", .size = 1024, .reps = 4_000, .max_encode_slowdown_pct = 190, .max_decode_slowdown_pct = 320, .padding = false, .variant = .imap, .reference_kind = .imap_no_pad },
    };

    for (expected, perf_cases) |expected_case, actual_case| {
        try std.testing.expectEqualStrings(expected_case.label, actual_case.label);
        try std.testing.expectEqual(expected_case.size, actual_case.size);
        try std.testing.expectEqual(expected_case.reps, actual_case.reps);
        try std.testing.expectEqual(expected_case.max_encode_slowdown_pct, actual_case.max_encode_slowdown_pct);
        try std.testing.expectEqual(expected_case.max_decode_slowdown_pct, actual_case.max_decode_slowdown_pct);
        try std.testing.expectEqual(expected_case.padding, actual_case.padding);
        try std.testing.expect(expected_case.variant == actual_case.variant);
        try std.testing.expect(expected_case.reference_kind == actual_case.reference_kind);
    }
}

pub fn fillPerfPayload(buffer: []u8) void {
    var prng = std.Random.DefaultPrng.init(0x5a17_2026_0640_0001);
    prng.random().bytes(buffer);
}
