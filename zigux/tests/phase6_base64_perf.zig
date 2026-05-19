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

fn validatePerfMatrix() !void {
    try std.testing.expect(fixtures.perf_cases.len > 0);
    try std.testing.expectEqual(fixtures.perf_payload.len, fixtures.perf_payload_buf_size);

    for (fixtures.perf_cases, 0..) |case, idx| {
        try std.testing.expectEqualStrings(fixtures.perf_payload, case.payload);
        try std.testing.expect(case.iterations > 0);
        try std.testing.expect(case.max_encode_slowdown_pct > 0);
        try std.testing.expect(case.max_decode_slowdown_pct > 0);
        try std.testing.expect(
            std.mem.eql(u8, case.variant_name, "std") or
                std.mem.eql(u8, case.variant_name, "urlsafe") or
                std.mem.eql(u8, case.variant_name, "imap"),
        );
        for (fixtures.perf_cases[idx + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, case.label, other.label));
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
    // The committed IMAP perf payload intentionally avoids the '/' glyph, so the standard
    // encoder and decoder remain a byte-for-byte baseline while the helper still exercises
    // its dedicated IMAP alphabet path.
    if (std.mem.eql(u8, case.variant_name, "imap")) {
        return .{
            .helper_variant = .imap,
            .encoder = if (case.padding) &std.base64.standard.Encoder else &std.base64.standard_no_pad.Encoder,
            .decoder = if (case.padding) &std.base64.standard.Decoder else &std.base64.standard_no_pad.Decoder,
        };
    }
    unreachable;
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
    var sink: u8 = 0;
    const start_ns = monotonicNs();
    var iteration: usize = 0;
    while (iteration < case.iterations) : (iteration += 1) {
        const encoded = codec.encoder.encode(std_buf[0..], case.payload);
        sink +%= encoded[encoded.len - 1];
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
    var sink: u8 = 0;
    const start_ns = monotonicNs();
    var iteration: usize = 0;
    while (iteration < case.iterations) : (iteration += 1) {
        codec.decoder.decode(std_buf[0..case.payload.len], encoded) catch unreachable;
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

    const helper_len = try base64.encode(helper_buf[0..], case.payload, case.padding, codec.helper_variant);
    const std_out = codec.encoder.encode(std_buf[0..], case.payload);
    try std.testing.expectEqual(helper_len, std_out.len);
    try std.testing.expectEqualStrings(std_out, helper_buf[0..helper_len]);

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

    const helper_written = try base64.decode(helper_buf[0..], encoded, case.padding, codec.helper_variant);
    try codec.decoder.decode(std_buf[0..case.payload.len], encoded);
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
