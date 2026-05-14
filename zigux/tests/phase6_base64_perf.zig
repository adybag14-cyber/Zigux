const std = @import("std");
const base64 = @import("base64");
const fixtures = @import("fixtures/phase6_base64_vectors.zig");

const PerfCase = fixtures.PerfCase;

const ExpectedPerfCase = struct {
    label: []const u8,
    variant_name: []const u8,
    reference_kind: []const u8,
    padding: bool,
    iterations: usize,
    max_encode_slowdown_pct: u64,
    max_decode_slowdown_pct: u64,
};

const expected_perf_cases = [_]ExpectedPerfCase{
    .{ .label = "STD_PAD", .variant_name = "std", .reference_kind = "std_padded", .padding = true, .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
    .{ .label = "STD_NO_PAD", .variant_name = "std", .reference_kind = "std_no_pad", .padding = false, .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
    .{ .label = "URLSAFE_PAD", .variant_name = "urlsafe", .reference_kind = "urlsafe_padded", .padding = true, .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
    .{ .label = "URLSAFE_NO_PAD", .variant_name = "urlsafe", .reference_kind = "urlsafe_no_pad", .padding = false, .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
};

const PerfResult = struct {
    helper_encode_ns_per_op: u64,
    helper_decode_ns_per_op: u64,
    reference_encode_ns_per_op: u64,
    reference_decode_ns_per_op: u64,
    encode_slowdown_pct: u64,
    decode_slowdown_pct: u64,
    encoded_len: usize,
    decoded_len: usize,
};

pub fn main() !void {
    for (fixtures.perf_cases) |case| {
        const result = try runPerfCase(case);
        std.debug.print(
            "phase6-base64-perf {s} helper_encode_ns_per_op={} helper_decode_ns_per_op={} reference_encode_ns_per_op={} reference_decode_ns_per_op={} encode_slowdown_pct={} decode_slowdown_pct={} encoded_len={} decoded_len={}\n",
            .{
                case.label,
                result.helper_encode_ns_per_op,
                result.helper_decode_ns_per_op,
                result.reference_encode_ns_per_op,
                result.reference_decode_ns_per_op,
                result.encode_slowdown_pct,
                result.decode_slowdown_pct,
                result.encoded_len,
                result.decoded_len,
            },
        );
    }
}

fn fixtureVariant(name: []const u8) base64.Variant {
    if (std.mem.eql(u8, name, "std")) return .std;
    if (std.mem.eql(u8, name, "urlsafe")) return .urlsafe;
    if (std.mem.eql(u8, name, "imap")) return .imap;
    unreachable;
}

fn monotonicNs() u64 {
    var ts: std.os.linux.timespec = undefined;
    _ = std.os.linux.clock_gettime(.MONOTONIC, &ts);
    return @intCast(@as(i128, ts.sec) * std.time.ns_per_s + ts.nsec);
}

fn stripPaddingLen(padded_len: usize, src_len: usize) usize {
    return padded_len - switch (src_len % 3) {
        0 => @as(usize, 0),
        1 => @as(usize, 2),
        2 => @as(usize, 1),
        else => unreachable,
    };
}

fn normalizeNoPadInput(dst: []u8, src: []const u8) ![]const u8 {
    if (src.len > dst.len) return error.InvalidInput;
    @memcpy(dst[0..src.len], src);
    var len = src.len;
    while ((len % 4) != 0) : (len += 1) {
        if (len >= dst.len) return error.InvalidInput;
        dst[len] = '=';
    }
    return dst[0..len];
}

fn referenceEncode(kind: []const u8, dst: []u8, src: []const u8) ![]const u8 {
    if (std.mem.eql(u8, kind, "std_padded")) {
        return std.base64.standard.Encoder.encode(dst, src);
    }
    if (std.mem.eql(u8, kind, "std_no_pad")) {
        const encoded = std.base64.standard.Encoder.encode(dst, src);
        return encoded[0..stripPaddingLen(encoded.len, src.len)];
    }
    if (std.mem.eql(u8, kind, "urlsafe_padded")) {
        return std.base64.url_safe.Encoder.encode(dst, src);
    }
    if (std.mem.eql(u8, kind, "urlsafe_no_pad")) {
        const encoded = std.base64.url_safe.Encoder.encode(dst, src);
        return encoded[0..stripPaddingLen(encoded.len, src.len)];
    }
    return error.InvalidInput;
}

fn referenceDecode(kind: []const u8, dst: []u8, encoded: []const u8, scratch: []u8) !usize {
    if (std.mem.eql(u8, kind, "std_padded")) {
        try std.base64.standard.Decoder.decode(dst, encoded);
        return dst.len;
    }
    if (std.mem.eql(u8, kind, "std_no_pad")) {
        const normalized = try normalizeNoPadInput(scratch, encoded);
        try std.base64.standard.Decoder.decode(dst, normalized);
        return dst.len;
    }
    if (std.mem.eql(u8, kind, "urlsafe_padded")) {
        try std.base64.url_safe.Decoder.decode(dst, encoded);
        return dst.len;
    }
    if (std.mem.eql(u8, kind, "urlsafe_no_pad")) {
        const normalized = try normalizeNoPadInput(scratch, encoded);
        try std.base64.url_safe.Decoder.decode(dst, normalized);
        return dst.len;
    }
    return error.InvalidInput;
}

fn median3(a: u64, b: u64, c: u64) u64 {
    return a + b + c - @min(a, @min(b, c)) - @max(a, @max(b, c));
}

fn benchHelperEncode(src: []const u8, dst: []u8, reps: usize, padding: bool, variant: base64.Variant) !struct { elapsed: u64, sink: u32 } {
    var sink: u32 = 0;
    const started_at = monotonicNs();
    for (0..reps) |_| {
        const written = try base64.encode(dst, src, padding, variant);
        sink +%= @as(u32, @intCast(written));
        if (written != 0) {
            sink +%= dst[0];
            sink +%= dst[written - 1];
        }
    }
    return .{ .elapsed = monotonicNs() - started_at, .sink = sink };
}

fn benchReferenceEncode(kind: []const u8, src: []const u8, dst: []u8, reps: usize) !struct { elapsed: u64, sink: u32 } {
    var sink: u32 = 0;
    const started_at = monotonicNs();
    for (0..reps) |_| {
        const encoded = try referenceEncode(kind, dst, src);
        sink +%= @as(u32, @intCast(encoded.len));
        if (encoded.len != 0) {
            sink +%= encoded[0];
            sink +%= encoded[encoded.len - 1];
        }
    }
    return .{ .elapsed = monotonicNs() - started_at, .sink = sink };
}

fn benchHelperDecode(encoded: []const u8, dst: []u8, expected_len: usize, reps: usize, padding: bool, variant: base64.Variant) !struct { elapsed: u64, sink: u32 } {
    var sink: u32 = 0;
    const started_at = monotonicNs();
    for (0..reps) |_| {
        const written = try base64.decode(dst, encoded, padding, variant);
        try std.testing.expectEqual(expected_len, written);
        sink +%= @as(u32, @intCast(written));
        if (written != 0) {
            sink +%= dst[0];
            sink +%= dst[written - 1];
        }
    }
    return .{ .elapsed = monotonicNs() - started_at, .sink = sink };
}

fn benchReferenceDecode(kind: []const u8, encoded: []const u8, dst: []u8, expected_len: usize, reps: usize) !struct { elapsed: u64, sink: u32 } {
    var sink: u32 = 0;
    var scratch: [768]u8 = undefined;
    const started_at = monotonicNs();
    for (0..reps) |_| {
        const written = try referenceDecode(kind, dst, encoded, scratch[0..]);
        try std.testing.expectEqual(expected_len, written);
        sink +%= @as(u32, @intCast(written));
        if (written != 0) {
            sink +%= dst[0];
            sink +%= dst[written - 1];
        }
    }
    return .{ .elapsed = monotonicNs() - started_at, .sink = sink };
}

fn slowdownPct(helper_elapsed: u64, reference_elapsed: u64) u64 {
    return @max(@as(u64, 1), @divFloor(helper_elapsed * 100, @max(reference_elapsed, 1)));
}

fn nsPerOp(elapsed_ns: u64, reps: usize) u64 {
    return @max(@as(u64, 1), @divFloor(elapsed_ns, @as(u64, @intCast(reps))));
}

fn runPerfCase(case: PerfCase) !PerfResult {
    const variant = fixtureVariant(case.variant_name);
    var helper_encoded: [fixtures.perf_encoded_buf_size]u8 = undefined;
    var reference_encoded: [fixtures.perf_encoded_buf_size]u8 = undefined;
    var helper_decoded: [fixtures.perf_payload_buf_size]u8 = undefined;
    var reference_decoded: [fixtures.perf_payload_buf_size]u8 = undefined;
    var reference_decode_scratch: [fixtures.perf_encoded_buf_size]u8 = undefined;

    const helper_encoded_len = try base64.encode(helper_encoded[0..], case.payload, case.padding, variant);
    const reference_encoded_slice = try referenceEncode(case.reference_kind, reference_encoded[0..], case.payload);
    try std.testing.expectEqualSlices(u8, reference_encoded_slice, helper_encoded[0..helper_encoded_len]);

    const helper_decoded_len = try base64.decode(helper_decoded[0..], helper_encoded[0..helper_encoded_len], case.padding, variant);
    const reference_decoded_len = try referenceDecode(case.reference_kind, reference_decoded[0..], reference_encoded_slice, reference_decode_scratch[0..]);
    try std.testing.expectEqual(case.payload.len, helper_decoded_len);
    try std.testing.expectEqual(case.payload.len, reference_decoded_len);
    try std.testing.expectEqualSlices(u8, case.payload, helper_decoded[0..helper_decoded_len]);
    try std.testing.expectEqualSlices(u8, case.payload, reference_decoded[0..reference_decoded_len]);

    _ = try benchHelperEncode(case.payload, helper_encoded[0..], case.iterations / 10, case.padding, variant);
    _ = try benchReferenceEncode(case.reference_kind, case.payload, reference_encoded[0..], case.iterations / 10);
    _ = try benchHelperDecode(reference_encoded_slice, helper_decoded[0..], case.payload.len, case.iterations / 10, case.padding, variant);
    _ = try benchReferenceDecode(case.reference_kind, reference_encoded_slice, reference_decoded[0..], case.payload.len, case.iterations / 10);

    var encode_samples: [3]u64 = undefined;
    var decode_samples: [3]u64 = undefined;
    var best_helper_encode: u64 = std.math.maxInt(u64);
    var best_helper_decode: u64 = std.math.maxInt(u64);
    var best_reference_encode: u64 = std.math.maxInt(u64);
    var best_reference_decode: u64 = std.math.maxInt(u64);

    for (0..3) |sample_index| {
        const helper_encode = try benchHelperEncode(case.payload, helper_encoded[0..], case.iterations, case.padding, variant);
        const reference_encode = try benchReferenceEncode(case.reference_kind, case.payload, reference_encoded[0..], case.iterations);
        const helper_decode = try benchHelperDecode(reference_encoded_slice, helper_decoded[0..], case.payload.len, case.iterations, case.padding, variant);
        const reference_decode = try benchReferenceDecode(case.reference_kind, reference_encoded_slice, reference_decoded[0..], case.payload.len, case.iterations);

        best_helper_encode = @min(best_helper_encode, helper_encode.elapsed);
        best_reference_encode = @min(best_reference_encode, reference_encode.elapsed);
        best_helper_decode = @min(best_helper_decode, helper_decode.elapsed);
        best_reference_decode = @min(best_reference_decode, reference_decode.elapsed);

        try std.testing.expectEqual(helper_encode.sink, reference_encode.sink);
        try std.testing.expectEqual(helper_decode.sink, reference_decode.sink);

        encode_samples[sample_index] = slowdownPct(helper_encode.elapsed, reference_encode.elapsed);
        decode_samples[sample_index] = slowdownPct(helper_decode.elapsed, reference_decode.elapsed);
    }

    const encode_slowdown_pct = median3(encode_samples[0], encode_samples[1], encode_samples[2]);
    const decode_slowdown_pct = median3(decode_samples[0], decode_samples[1], decode_samples[2]);
    try std.testing.expect(encode_slowdown_pct <= case.max_encode_slowdown_pct);
    try std.testing.expect(decode_slowdown_pct <= case.max_decode_slowdown_pct);

    return .{
        .helper_encode_ns_per_op = nsPerOp(best_helper_encode, case.iterations),
        .helper_decode_ns_per_op = nsPerOp(best_helper_decode, case.iterations),
        .reference_encode_ns_per_op = nsPerOp(best_reference_encode, case.iterations),
        .reference_decode_ns_per_op = nsPerOp(best_reference_decode, case.iterations),
        .encode_slowdown_pct = encode_slowdown_pct,
        .decode_slowdown_pct = decode_slowdown_pct,
        .encoded_len = helper_encoded_len,
        .decoded_len = helper_decoded_len,
    };
}

test "phase 6 base64 perf matrix keeps all shipped variant-and-padding replays" {
    try std.testing.expectEqual(expected_perf_cases.len, fixtures.perf_cases.len);

    for (expected_perf_cases, fixtures.perf_cases) |expected, actual| {
        try std.testing.expectEqualStrings(expected.label, actual.label);
        try std.testing.expectEqualStrings(expected.variant_name, actual.variant_name);
        try std.testing.expectEqualStrings(expected.reference_kind, actual.reference_kind);
        try std.testing.expectEqual(expected.padding, actual.padding);
        try std.testing.expectEqual(expected.iterations, actual.iterations);
        try std.testing.expectEqual(expected.max_encode_slowdown_pct, actual.max_encode_slowdown_pct);
        try std.testing.expectEqual(expected.max_decode_slowdown_pct, actual.max_decode_slowdown_pct);
        try std.testing.expectEqualStrings(fixtures.perf_payload, actual.payload);
    }
}
