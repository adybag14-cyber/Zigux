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
