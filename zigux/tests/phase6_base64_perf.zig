const std = @import("std");
const base64 = @import("base64");
const fixtures = @import("fixtures/phase6_base64_vectors.zig");

const bench_sample_count: usize = 3;

const Codec = struct {
    helper_variant: base64.Variant,
    encoder: *const std.base64.Base64Encoder,
    decoder: *const std.base64.Base64Decoder,
};

const BenchResult = struct {
    elapsed_ns: u64,
    sink: u8,
};

fn perfPayloadFingerprint(bytes: []const u8) u64 {
    var acc: u64 = 0xcbf2_9ce4_8422_2325;
    for (bytes, 0..) |byte, idx| {
        acc ^= @as(u64, byte) +% (@as(u64, @intCast(idx)) << 8);
        acc *%= 0x0000_0100_0000_01b3;
    }
    return acc;
}

fn validatePerfMatrix() !void {
    const expected_payload_fingerprint: u64 = 0xf49a_c027_ffb2_a2e4;
    const expected = [_]struct {
        label: []const u8,
        padding: bool,
        variant_name: []const u8,
        iterations: usize,
        max_encode_slowdown_pct: u64,
        max_decode_slowdown_pct: u64,
    }{
        .{ .label = "STD_PAD", .padding = true, .variant_name = "std", .iterations = 12_000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
        .{ .label = "STD_NO_PAD", .padding = false, .variant_name = "std", .iterations = 12_000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
        .{ .label = "URLSAFE_PAD", .padding = true, .variant_name = "urlsafe", .iterations = 12_000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
        .{ .label = "URLSAFE_NO_PAD", .padding = false, .variant_name = "urlsafe", .iterations = 12_000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
        .{ .label = "IMAP_PAD", .padding = true, .variant_name = "imap", .iterations = 12_000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
        .{ .label = "IMAP_NO_PAD", .padding = false, .variant_name = "imap", .iterations = 12_000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
    };

    if (fixtures.perf_cases.len != expected.len) {
        return error.Base64PerfMatrixMismatch;
    }
    if (fixtures.perf_payload.len != fixtures.perf_payload_buf_size) {
        return error.Base64PerfMatrixMismatch;
    }
    if (perfPayloadFingerprint(fixtures.perf_payload) != expected_payload_fingerprint) {
        return error.Base64PerfMatrixMismatch;
    }

    for (expected, 0..) |want, idx| {
        const actual = fixtures.perf_cases[idx];
        if (!std.mem.eql(u8, want.label, actual.label)) {
            return error.Base64PerfMatrixMismatch;
        }
        if (want.padding != actual.padding) {
            return error.Base64PerfMatrixMismatch;
        }
        if (!std.mem.eql(u8, want.variant_name, actual.variant_name)) {
            return error.Base64PerfMatrixMismatch;
        }
        if (want.iterations != actual.iterations) {
            return error.Base64PerfMatrixMismatch;
        }
        if (want.max_encode_slowdown_pct != actual.max_encode_slowdown_pct) {
            return error.Base64PerfMatrixMismatch;
        }
        if (want.max_decode_slowdown_pct != actual.max_decode_slowdown_pct) {
            return error.Base64PerfMatrixMismatch;
        }
        if (!std.mem.eql(u8, fixtures.perf_payload, actual.payload)) {
            return error.Base64PerfMatrixMismatch;
        }
        if (fixtures.perf_encoded_buf_size < base64.chars(actual.payload.len, actual.padding)) {
            return error.Base64PerfMatrixMismatch;
        }
    }

    for (fixtures.perf_cases, 0..) |case, idx| {
        if (case.payload.len == 0 or case.iterations == 0) {
            return error.Base64PerfMatrixMismatch;
        }
        if (case.max_encode_slowdown_pct == 0 or case.max_decode_slowdown_pct == 0) {
            return error.Base64PerfMatrixMismatch;
        }

        for (fixtures.perf_cases[idx + 1 ..]) |other| {
            if (std.mem.eql(u8, case.label, other.label)) {
                return error.Base64PerfMatrixMismatch;
            }
        }
    }
}

fn resolveCodec(case: fixtures.PerfCase) Codec {
    if (std.mem.eql(u8, case.variant_name, "std")) {
        return .{
            .helper_variant = .std,
            .encoder = if (case.padding) &std.base64.standard.Encoder else &std.base64.standard_no_pad.Encoder,
            .decoder = if (case.padding) &std.base64.standard.Decoder else &std.base64.standard_no_pad.Decoder,
        };
    }
    if (std.mem.eql(u8, case.variant_name, "urlsafe")) {
        return .{
            .helper_variant = .urlsafe,
            .encoder = if (case.padding) &std.base64.url_safe.Encoder else &std.base64.url_safe_no_pad.Encoder,
            .decoder = if (case.padding) &std.base64.url_safe.Decoder else &std.base64.url_safe_no_pad.Decoder,
        };
    }
    if (std.mem.eql(u8, case.variant_name, "imap")) {
        return .{
            .helper_variant = .imap,
            .encoder = if (case.padding) &std.base64.standard.Encoder else &std.base64.standard_no_pad.Encoder,
            .decoder = if (case.padding) &std.base64.standard.Decoder else &std.base64.standard_no_pad.Decoder,
        };
    }
    unreachable;
}

fn isImapCase(case: fixtures.PerfCase) bool {
    return std.mem.eql(u8, case.variant_name, "imap");
}

fn mapStdEncodedToImap(dst: []u8, src: []const u8) []const u8 {
    std.debug.assert(dst.len >= src.len);
    for (src, 0..) |byte, idx| {
        dst[idx] = if (byte == '/') ',' else byte;
    }
    return dst[0..src.len];
}

fn mapImapEncodedToStd(dst: []u8, src: []const u8) []const u8 {
    std.debug.assert(dst.len >= src.len);
    for (src, 0..) |byte, idx| {
        dst[idx] = if (byte == ',') '/' else byte;
    }
    return dst[0..src.len];
}

fn monotonicNs() u64 {
    var ts: std.posix.timespec = undefined;
    switch (std.posix.errno(std.posix.system.clock_gettime(std.posix.CLOCK.MONOTONIC, &ts))) {
        .SUCCESS => {},
        else => unreachable,
    }
    return @as(u64, @intCast(ts.sec)) * std.time.ns_per_s + @as(u64, @intCast(ts.nsec));
}

fn runHelperEncodeBench(case: fixtures.PerfCase, codec: Codec) BenchResult {
    var helper_buf: [fixtures.perf_encoded_buf_size]u8 = undefined;
    var sink: u8 = 0;
    const start_ns = monotonicNs();
    var iteration: usize = 0;
    while (iteration < case.iterations) : (iteration += 1) {
        const written = base64.encode(helper_buf[0..], case.payload, case.padding, codec.helper_variant) catch unreachable;
        sink +%= helper_buf[written - 1];
    }
    return .{ .elapsed_ns = monotonicNs() - start_ns, .sink = sink };
}

fn runReferenceEncodeBench(case: fixtures.PerfCase, codec: Codec) BenchResult {
    var std_buf: [fixtures.perf_encoded_buf_size]u8 = undefined;
    var imap_buf: [fixtures.perf_encoded_buf_size]u8 = undefined;
    var sink: u8 = 0;
    const start_ns = monotonicNs();
    var iteration: usize = 0;
    while (iteration < case.iterations) : (iteration += 1) {
        const encoded = codec.encoder.encode(std_buf[0..], case.payload);
        const reference_encoded = if (isImapCase(case)) mapStdEncodedToImap(imap_buf[0..], encoded) else encoded;
        sink +%= reference_encoded[reference_encoded.len - 1];
    }
    return .{ .elapsed_ns = monotonicNs() - start_ns, .sink = sink };
}

fn runHelperDecodeBench(case: fixtures.PerfCase, codec: Codec, encoded: []const u8) BenchResult {
    var helper_buf: [fixtures.perf_payload_buf_size]u8 = undefined;
    var sink: u8 = 0;
    const start_ns = monotonicNs();
    var iteration: usize = 0;
    while (iteration < case.iterations) : (iteration += 1) {
        const written = base64.decode(helper_buf[0..], encoded, case.padding, codec.helper_variant) catch unreachable;
        sink +%= helper_buf[written - 1];
    }
    return .{ .elapsed_ns = monotonicNs() - start_ns, .sink = sink };
}

fn runReferenceDecodeBench(case: fixtures.PerfCase, codec: Codec, encoded: []const u8) BenchResult {
    var std_buf: [fixtures.perf_payload_buf_size]u8 = undefined;
    var normalized_encoded_buf: [fixtures.perf_encoded_buf_size]u8 = undefined;
    var sink: u8 = 0;
    const start_ns = monotonicNs();
    var iteration: usize = 0;
    while (iteration < case.iterations) : (iteration += 1) {
        const reference_encoded = if (isImapCase(case)) mapImapEncodedToStd(normalized_encoded_buf[0..], encoded) else encoded;
        codec.decoder.decode(std_buf[0..case.payload.len], reference_encoded) catch unreachable;
        sink +%= std_buf[case.payload.len - 1];
    }
    return .{ .elapsed_ns = monotonicNs() - start_ns, .sink = sink };
}

fn slowdownPct(helper_ns: u64, baseline_ns: u64) u64 {
    if (helper_ns <= baseline_ns) {
        return 0;
    }
    const delta = @as(u128, helper_ns - baseline_ns) * 100;
    const denom = @max(@as(u128, baseline_ns), 1);
    return @intCast(delta / denom);
}

fn medianNs(samples: []u64) u64 {
    std.debug.assert(samples.len == bench_sample_count);
    std.mem.sort(u64, samples, {}, std.sort.asc(u64));
    return samples[samples.len / 2];
}

fn encodeSlowdownPct(case: fixtures.PerfCase, codec: Codec) !u64 {
    var helper_buf: [fixtures.perf_encoded_buf_size]u8 = undefined;
    var std_buf: [fixtures.perf_encoded_buf_size]u8 = undefined;
    var imap_reference_buf: [fixtures.perf_encoded_buf_size]u8 = undefined;

    const helper_len = try base64.encode(helper_buf[0..], case.payload, case.padding, codec.helper_variant);
    const std_out = codec.encoder.encode(std_buf[0..], case.payload);
    const reference_out = if (isImapCase(case)) mapStdEncodedToImap(imap_reference_buf[0..], std_out) else std_out;
    try std.testing.expectEqual(helper_len, reference_out.len);
    try std.testing.expectEqualStrings(reference_out, helper_buf[0..helper_len]);

    var helper_samples: [bench_sample_count]u64 = undefined;
    var baseline_samples: [bench_sample_count]u64 = undefined;
    var helper_sink: u8 = 0;
    var baseline_sink: u8 = 0;

    for (0..bench_sample_count) |sample_index| {
        const helper_result = runHelperEncodeBench(case, codec);
        const baseline_result = runReferenceEncodeBench(case, codec);
        helper_samples[sample_index] = helper_result.elapsed_ns;
        baseline_samples[sample_index] = baseline_result.elapsed_ns;
        helper_sink +%= helper_result.sink;
        baseline_sink +%= baseline_result.sink;
    }

    std.mem.doNotOptimizeAway(helper_sink);
    std.mem.doNotOptimizeAway(baseline_sink);
    return slowdownPct(medianNs(helper_samples[0..]), medianNs(baseline_samples[0..]));
}

fn decodeSlowdownPct(case: fixtures.PerfCase, codec: Codec) !u64 {
    var encoded_buf: [fixtures.perf_encoded_buf_size]u8 = undefined;
    const encoded_len = try base64.encode(encoded_buf[0..], case.payload, case.padding, codec.helper_variant);
    const encoded = encoded_buf[0..encoded_len];

    var helper_buf: [fixtures.perf_payload_buf_size]u8 = undefined;
    var std_buf: [fixtures.perf_payload_buf_size]u8 = undefined;
    var normalized_encoded_buf: [fixtures.perf_encoded_buf_size]u8 = undefined;

    const helper_written = try base64.decode(helper_buf[0..], encoded, case.padding, codec.helper_variant);
    const reference_encoded = if (isImapCase(case)) mapImapEncodedToStd(normalized_encoded_buf[0..], encoded) else encoded;
    try codec.decoder.decode(std_buf[0..case.payload.len], reference_encoded);
    try std.testing.expectEqual(case.payload.len, helper_written);
    try std.testing.expectEqualStrings(case.payload, helper_buf[0..helper_written]);
    try std.testing.expectEqualStrings(case.payload, std_buf[0..case.payload.len]);

    var helper_samples: [bench_sample_count]u64 = undefined;
    var baseline_samples: [bench_sample_count]u64 = undefined;
    var helper_sink: u8 = 0;
    var baseline_sink: u8 = 0;

    for (0..bench_sample_count) |sample_index| {
        const helper_result = runHelperDecodeBench(case, codec, encoded);
        const baseline_result = runReferenceDecodeBench(case, codec, encoded);
        helper_samples[sample_index] = helper_result.elapsed_ns;
        baseline_samples[sample_index] = baseline_result.elapsed_ns;
        helper_sink +%= helper_result.sink;
        baseline_sink +%= baseline_result.sink;
    }

    std.mem.doNotOptimizeAway(helper_sink);
    std.mem.doNotOptimizeAway(baseline_sink);
    return slowdownPct(medianNs(helper_samples[0..]), medianNs(baseline_samples[0..]));
}

pub fn main() !void {
    try validatePerfMatrix();

    for (fixtures.perf_cases) |case| {
        const codec = resolveCodec(case);
        const encode_slowdown = try encodeSlowdownPct(case, codec);
        if (encode_slowdown > case.max_encode_slowdown_pct) {
            std.debug.print(
                "PHASE6_BASE64_PERF=fail label={s} encode_slowdown_pct={} max={}\n",
                .{ case.label, encode_slowdown, case.max_encode_slowdown_pct },
            );
            return error.TestExpectedEqual;
        }

        const decode_slowdown = try decodeSlowdownPct(case, codec);
        if (decode_slowdown > case.max_decode_slowdown_pct) {
            std.debug.print(
                "PHASE6_BASE64_PERF=fail label={s} decode_slowdown_pct={} max={}\n",
                .{ case.label, decode_slowdown, case.max_decode_slowdown_pct },
            );
            return error.TestExpectedEqual;
        }

        std.debug.print(
            "PHASE6_BASE64_PERF_CASE=pass label={s} encode_slowdown_pct={} decode_slowdown_pct={}\n",
            .{ case.label, encode_slowdown, decode_slowdown },
        );
    }

    std.debug.print("PHASE6_BASE64_PERF=pass\n", .{});
}
