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
    expected: []const u8,
    variant_name: []const u8,
    padding: bool,
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

pub const variant_cases = [_]VariantCase{
    .{ .expected = "APv_f4A=", .variant_name = "urlsafe", .padding = true },
    .{ .expected = "APv,f4A=", .variant_name = "imap", .padding = true },
    .{ .expected = "APv_f4A", .variant_name = "urlsafe", .padding = false },
    .{ .expected = "APv,f4A", .variant_name = "imap", .padding = false },
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
    .{ .input = "Zm9v====", .padding = true, .variant_name = "std" },
    .{ .input = "Zm==A", .padding = true, .variant_name = "std" },
    .{ .input = "Zh==", .padding = true, .variant_name = "std" },
    .{ .input = "Zh==", .padding = true, .variant_name = "urlsafe" },
    .{ .input = "Zh==", .padding = true, .variant_name = "imap" },
    .{ .input = "Zm9=", .padding = true, .variant_name = "std" },
    .{ .input = "Zm9=", .padding = true, .variant_name = "urlsafe" },
    .{ .input = "Zm9=", .padding = true, .variant_name = "imap" },
    .{ .input = invalid_with_nul[0..], .padding = true, .variant_name = "std" },
    .{ .input = "Zg=!", .padding = false, .variant_name = "std" },
    .{ .input = "Zm$=", .padding = false, .variant_name = "std" },
    .{ .input = "Z===", .padding = false, .variant_name = "std" },
    .{ .input = "Zg=", .padding = false, .variant_name = "std" },
    .{ .input = "Zm9v====", .padding = false, .variant_name = "std" },
    .{ .input = "Zm==v", .padding = false, .variant_name = "std" },
    .{ .input = "Zh", .padding = false, .variant_name = "std" },
    .{ .input = "Zm9", .padding = false, .variant_name = "std" },
    .{ .input = invalid_with_nul[0..], .padding = false, .variant_name = "std" },
    .{ .input = "Zg==", .padding = false, .variant_name = "urlsafe" },
    .{ .input = "Zg==", .padding = false, .variant_name = "imap" },
};

pub const variant_decode_cases = [_]DecodeCase{
    .{ .input = "APv_f4A=", .expected = &variant_sample, .padding = true, .variant_name = "urlsafe" },
    .{ .input = "APv,f4A=", .expected = &variant_sample, .padding = true, .variant_name = "imap" },
    .{ .input = "APv_f4A", .expected = &variant_sample, .padding = false, .variant_name = "urlsafe" },
    .{ .input = "APv,f4A", .expected = &variant_sample, .padding = false, .variant_name = "imap" },
};

pub const perf_payload =
    "Phase 6 base64 perf gate payload keeps the helper wired to a real throughput check. " ++
    "This packet stays helper-local, avoids widening into neighboring leaf helpers, and " ++
    "exercises repeated encode and decode work over a stable review fixture. " ++
    "Zigux uses the same payload for padded and unpadded standard and urlsafe runs.";

pub const perf_cases = [_]PerfCase{
    .{
        .label = "STD_PAD",
        .payload = perf_payload,
        .padding = true,
        .variant_name = "std",
        .iterations = 12000,
        .max_encode_slowdown_pct = 150,
        .max_decode_slowdown_pct = 325,
    },
    .{
        .label = "STD_NO_PAD",
        .payload = perf_payload,
        .padding = false,
        .variant_name = "std",
        .iterations = 12000,
        .max_encode_slowdown_pct = 150,
        .max_decode_slowdown_pct = 325,
    },
    .{
        .label = "URLSAFE_PAD",
        .payload = perf_payload,
        .padding = true,
        .variant_name = "urlsafe",
        .iterations = 12000,
        .max_encode_slowdown_pct = 150,
        .max_decode_slowdown_pct = 325,
    },
    .{
        .label = "URLSAFE_NO_PAD",
        .payload = perf_payload,
        .padding = false,
        .variant_name = "urlsafe",
        .iterations = 12000,
        .max_encode_slowdown_pct = 150,
        .max_decode_slowdown_pct = 325,
    },
};

pub const perf_payload_buf_size = perf_payload.len;
pub const perf_encoded_buf_size = 512;

pub fn perfReferenceSupportedVariant(variant_name: []const u8) bool {
    return std.mem.eql(u8, variant_name, "std") or std.mem.eql(u8, variant_name, "urlsafe");
}

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

test "phase 6 base64 standard fixture packet stays bounded to the documented matrix" {
    const expected = [_]EncodeCase{
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

    var padded_count: usize = 0;
    var unpadded_count: usize = 0;

    try std.testing.expectEqual(expected.len, standard_cases.len);
    try std.testing.expectEqual(expected.len, standard_decode_cases.len);

    for (expected, 0..) |want, idx| {
        const actual_encode = standard_cases[idx];
        const actual_decode = standard_decode_cases[idx];

        try std.testing.expectEqualStrings(want.input, actual_encode.input);
        try std.testing.expectEqualStrings(want.expected, actual_encode.expected);
        try std.testing.expectEqual(want.padding, actual_encode.padding);

        try std.testing.expectEqualStrings(want.expected, actual_decode.input);
        try std.testing.expectEqualStrings(want.input, actual_decode.expected);
        try std.testing.expectEqual(want.padding, actual_decode.padding);
        try std.testing.expectEqualStrings("std", actual_decode.variant_name);

        if (want.padding) {
            padded_count += 1;
        } else {
            unpadded_count += 1;
        }
    }

    try std.testing.expectEqual(@as(usize, 11), padded_count);
    try std.testing.expectEqual(@as(usize, 11), unpadded_count);
}

test "phase 6 base64 variant fixture packet stays bounded to the documented matrix" {
    const expected = [_]struct {
        encoded: []const u8,
        variant_name: []const u8,
        padding: bool,
    }{
        .{ .encoded = "APv_f4A=", .variant_name = "urlsafe", .padding = true },
        .{ .encoded = "APv,f4A=", .variant_name = "imap", .padding = true },
        .{ .encoded = "APv_f4A", .variant_name = "urlsafe", .padding = false },
        .{ .encoded = "APv,f4A", .variant_name = "imap", .padding = false },
    };

    var saw_urlsafe_pad = false;
    var saw_urlsafe_no_pad = false;
    var saw_imap_pad = false;
    var saw_imap_no_pad = false;

    try std.testing.expectEqual(expected.len, variant_cases.len);
    try std.testing.expectEqual(expected.len, variant_decode_cases.len);

    for (expected, 0..) |want, idx| {
        const actual_encode = variant_cases[idx];
        const actual_decode = variant_decode_cases[idx];

        try std.testing.expectEqualStrings(want.encoded, actual_encode.expected);
        try std.testing.expectEqualStrings(want.variant_name, actual_encode.variant_name);
        try std.testing.expectEqual(want.padding, actual_encode.padding);

        try std.testing.expectEqualStrings(want.encoded, actual_decode.input);
        try std.testing.expectEqualSlices(u8, &variant_sample, actual_decode.expected);
        try std.testing.expectEqualStrings(want.variant_name, actual_decode.variant_name);
        try std.testing.expectEqual(want.padding, actual_decode.padding);

        if (std.mem.eql(u8, want.variant_name, "urlsafe")) {
            if (want.padding) {
                try std.testing.expect(!saw_urlsafe_pad);
                saw_urlsafe_pad = true;
            } else {
                try std.testing.expect(!saw_urlsafe_no_pad);
                saw_urlsafe_no_pad = true;
            }
        } else {
            if (want.padding) {
                try std.testing.expect(!saw_imap_pad);
                saw_imap_pad = true;
            } else {
                try std.testing.expect(!saw_imap_no_pad);
                saw_imap_no_pad = true;
            }
        }
    }

    try std.testing.expect(saw_urlsafe_pad);
    try std.testing.expect(saw_urlsafe_no_pad);
    try std.testing.expect(saw_imap_pad);
    try std.testing.expect(saw_imap_no_pad);
}

test "phase 6 base64 invalid decode fixture packet stays bounded to the documented matrix" {
    const expected = [_]InvalidDecodeCase{
        .{ .input = "Zg=!", .padding = true, .variant_name = "std" },
        .{ .input = "Zm$=", .padding = true, .variant_name = "std" },
        .{ .input = "Z===", .padding = true, .variant_name = "std" },
        .{ .input = "Zg", .padding = true, .variant_name = "std" },
        .{ .input = "Zm9v====", .padding = true, .variant_name = "std" },
        .{ .input = "Zm==A", .padding = true, .variant_name = "std" },
        .{ .input = "Zh==", .padding = true, .variant_name = "std" },
        .{ .input = "Zh==", .padding = true, .variant_name = "urlsafe" },
        .{ .input = "Zh==", .padding = true, .variant_name = "imap" },
        .{ .input = "Zm9=", .padding = true, .variant_name = "std" },
        .{ .input = "Zm9=", .padding = true, .variant_name = "urlsafe" },
        .{ .input = "Zm9=", .padding = true, .variant_name = "imap" },
        .{ .input = invalid_with_nul[0..], .padding = true, .variant_name = "std" },
        .{ .input = "Zg=!", .padding = false, .variant_name = "std" },
        .{ .input = "Zm$=", .padding = false, .variant_name = "std" },
        .{ .input = "Z===", .padding = false, .variant_name = "std" },
        .{ .input = "Zg=", .padding = false, .variant_name = "std" },
        .{ .input = "Zm9v====", .padding = false, .variant_name = "std" },
        .{ .input = "Zm==v", .padding = false, .variant_name = "std" },
        .{ .input = "Zh", .padding = false, .variant_name = "std" },
        .{ .input = "Zm9", .padding = false, .variant_name = "std" },
        .{ .input = invalid_with_nul[0..], .padding = false, .variant_name = "std" },
        .{ .input = "Zg==", .padding = false, .variant_name = "urlsafe" },
        .{ .input = "Zg==", .padding = false, .variant_name = "imap" },
    };

    var std_padded: usize = 0;
    var std_unpadded: usize = 0;
    var urlsafe_padded: usize = 0;
    var urlsafe_unpadded: usize = 0;
    var imap_padded: usize = 0;
    var imap_unpadded: usize = 0;

    try std.testing.expectEqual(expected.len, invalid_decode_cases.len);

    for (expected, 0..) |want, idx| {
        const actual = invalid_decode_cases[idx];

        try std.testing.expectEqualSlices(u8, want.input, actual.input);
        try std.testing.expectEqual(want.padding, actual.padding);
        try std.testing.expectEqualStrings(want.variant_name, actual.variant_name);

        if (std.mem.eql(u8, actual.variant_name, "std")) {
            if (actual.padding) {
                std_padded += 1;
            } else {
                std_unpadded += 1;
            }
        } else if (std.mem.eql(u8, actual.variant_name, "urlsafe")) {
            if (actual.padding) {
                urlsafe_padded += 1;
            } else {
                urlsafe_unpadded += 1;
            }
        } else {
            if (actual.padding) {
                imap_padded += 1;
            } else {
                imap_unpadded += 1;
            }
        }

        for (invalid_decode_cases[idx + 1 ..]) |other| {
            if (actual.padding == other.padding and std.mem.eql(u8, actual.variant_name, other.variant_name)) {
                try std.testing.expect(!std.mem.eql(u8, actual.input, other.input));
            }
        }
    }

    try std.testing.expectEqual(@as(usize, 9), std_padded);
    try std.testing.expectEqual(@as(usize, 9), std_unpadded);
    try std.testing.expectEqual(@as(usize, 2), urlsafe_padded);
    try std.testing.expectEqual(@as(usize, 1), urlsafe_unpadded);
    try std.testing.expectEqual(@as(usize, 2), imap_padded);
    try std.testing.expectEqual(@as(usize, 1), imap_unpadded);
}

test "phase 6 base64 perf fixture packet stays bounded to the documented matrix" {
    const expected = [_]struct {
        label: []const u8,
        variant_name: []const u8,
        padding: bool,
        iterations: usize,
        max_encode_slowdown_pct: u64,
        max_decode_slowdown_pct: u64,
    }{
        .{ .label = "STD_PAD", .variant_name = "std", .padding = true, .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
        .{ .label = "STD_NO_PAD", .variant_name = "std", .padding = false, .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
        .{ .label = "URLSAFE_PAD", .variant_name = "urlsafe", .padding = true, .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
        .{ .label = "URLSAFE_NO_PAD", .variant_name = "urlsafe", .padding = false, .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
    };

    var saw_std_pad = false;
    var saw_std_no_pad = false;
    var saw_urlsafe_pad = false;
    var saw_urlsafe_no_pad = false;

    try std.testing.expectEqual(expected.len, perf_cases.len);
    try std.testing.expectEqual(perf_payload.len, perf_payload_buf_size);

    for (expected, 0..) |want, idx| {
        const actual = perf_cases[idx];
        try std.testing.expectEqualStrings(want.label, actual.label);
        try std.testing.expectEqualStrings(want.variant_name, actual.variant_name);
        try std.testing.expectEqual(want.padding, actual.padding);
        try std.testing.expectEqual(want.iterations, actual.iterations);
        try std.testing.expectEqual(want.max_encode_slowdown_pct, actual.max_encode_slowdown_pct);
        try std.testing.expectEqual(want.max_decode_slowdown_pct, actual.max_decode_slowdown_pct);
    }

    for (perf_cases, 0..) |case, idx| {
        try std.testing.expectEqualStrings(perf_payload, case.payload);
        try std.testing.expect(case.iterations > 0);
        try std.testing.expect(case.max_encode_slowdown_pct > 0);
        try std.testing.expect(case.max_decode_slowdown_pct > 0);
        try std.testing.expect(perf_payload_buf_size >= case.payload.len);
        try std.testing.expect(perf_encoded_buf_size >= encodedChars(case.payload.len, case.padding));
        try std.testing.expect(perfReferenceSupportedVariant(case.variant_name));

        if (std.mem.eql(u8, case.variant_name, "std")) {
            if (case.padding) {
                try std.testing.expect(!saw_std_pad);
                saw_std_pad = true;
            } else {
                try std.testing.expect(!saw_std_no_pad);
                saw_std_no_pad = true;
            }
        } else {
            if (case.padding) {
                try std.testing.expect(!saw_urlsafe_pad);
                saw_urlsafe_pad = true;
            } else {
                try std.testing.expect(!saw_urlsafe_no_pad);
                saw_urlsafe_no_pad = true;
            }
        }

        for (perf_cases[idx + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, case.label, other.label));
        }
    }

    try std.testing.expect(saw_std_pad);
    try std.testing.expect(saw_std_no_pad);
    try std.testing.expect(saw_urlsafe_pad);
    try std.testing.expect(saw_urlsafe_no_pad);
}

test "phase 6 base64 perf fixture packet keeps IMAP outside the slowdown corpus until a direct baseline lands" {
    var saw_std = false;
    var saw_urlsafe = false;

    for (perf_cases) |case| {
        try std.testing.expect(perfReferenceSupportedVariant(case.variant_name));
        if (std.mem.eql(u8, case.variant_name, "std")) saw_std = true;
        if (std.mem.eql(u8, case.variant_name, "urlsafe")) saw_urlsafe = true;
    }

    try std.testing.expect(saw_std);
    try std.testing.expect(saw_urlsafe);
    try std.testing.expect(!perfReferenceSupportedVariant("imap"));
}
