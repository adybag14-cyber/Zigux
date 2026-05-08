const std = @import("std");
const base64 = @import("base64");
const fixtures = @import("fixtures/phase6_base64_vectors.zig");

const Io = std.Io;
const bench_sample_count: usize = 3;

const BenchResult = struct {
    elapsed_ns: u64,
    accumulator: u64,
};

fn fixtureVariant(name: []const u8) base64.Variant {
    if (std.mem.eql(u8, name, "std")) return .std;
    if (std.mem.eql(u8, name, "urlsafe")) return .urlsafe;
    if (std.mem.eql(u8, name, "imap")) return .imap;
    unreachable;
}

fn perfPayloadFingerprint(bytes: []const u8) u64 {
    var acc: u64 = 0xcbf2_9ce4_8422_2325;
    for (bytes, 0..) |byte, idx| {
        acc ^= @as(u64, byte) +% (@as(u64, @intCast(idx)) << 8);
        acc *%= 0x0000_0100_0000_01b3;
    }
    return acc;
}

fn validatePerfMatrix() !void {
    const expected = [_]struct {
        label: []const u8,
        variant_name: []const u8,
        padding: bool,
        iterations: usize,
        max_encode_slowdown_pct: u64,
        max_decode_slowdown_pct: u64,
        fingerprint: u64,
    }{
        .{ .label = "STD_PAD", .variant_name = "std", .padding = true, .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325, .fingerprint = 0xf0fc_dea9_f1c7_6907 },
        .{ .label = "STD_NO_PAD", .variant_name = "std", .padding = false, .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325, .fingerprint = 0xf0fc_dea9_f1c7_6907 },
        .{ .label = "URLSAFE_PAD", .variant_name = "urlsafe", .padding = true, .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325, .fingerprint = 0xf0fc_dea9_f1c7_6907 },
        .{ .label = "URLSAFE_NO_PAD", .variant_name = "urlsafe", .padding = false, .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325, .fingerprint = 0xf0fc_dea9_f1c7_6907 },
    };

    var saw_std_pad = false;
    var saw_std_no_pad = false;
    var saw_urlsafe_pad = false;
    var saw_urlsafe_no_pad = false;

    if (fixtures.perf_cases.len != expected.len) return error.Base64PerfMatrixMismatch;
    if (fixtures.perf_payload.len != fixtures.perf_payload_buf_size) return error.Base64PerfMatrixMismatch;

    for (expected, 0..) |want, idx| {
        const actual = fixtures.perf_cases[idx];
        if (!std.mem.eql(u8, want.label, actual.label)) return error.Base64PerfMatrixMismatch;
        if (!std.mem.eql(u8, want.variant_name, actual.variant_name)) return error.Base64PerfMatrixMismatch;
        if (want.padding != actual.padding) return error.Base64PerfMatrixMismatch;
        if (want.iterations != actual.iterations) return error.Base64PerfMatrixMismatch;
        if (want.max_encode_slowdown_pct != actual.max_encode_slowdown_pct) return error.Base64PerfMatrixMismatch;
        if (want.max_decode_slowdown_pct != actual.max_decode_slowdown_pct) return error.Base64PerfMatrixMismatch;
        if (want.fingerprint != perfPayloadFingerprint(actual.payload)) return error.Base64PerfMatrixMismatch;
    }

    for (fixtures.perf_cases, 0..) |case, idx| {
        if (!std.mem.eql(u8, fixtures.perf_payload, case.payload)) return error.Base64PerfMatrixMismatch;
        if (case.iterations == 0 or case.max_encode_slowdown_pct == 0 or case.max_decode_slowdown_pct == 0) {
            return error.Base64PerfMatrixMismatch;
        }
        if (fixtures.perf_payload_buf_size < case.payload.len) return error.Base64PerfMatrixMismatch;

        const needed_chars = std.base64.standard.Encoder.calcSize(case.payload.len);
        if (fixtures.perf_encoded_buf_size < needed_chars) return error.Base64PerfMatrixMismatch;
        try expectExactFitPerfBuffers(case);

        if (std.mem.eql(u8, case.label, "STD_PAD")) {
            if (!std.mem.eql(u8, case.variant_name, "std") or !case.padding or saw_std_pad) {
                return error.Base64PerfMatrixMismatch;
            }
            saw_std_pad = true;
        } else if (std.mem.eql(u8, case.label, "STD_NO_PAD")) {
            if (!std.mem.eql(u8, case.variant_name, "std") or case.padding or saw_std_no_pad) {
                return error.Base64PerfMatrixMismatch;
            }
            saw_std_no_pad = true;
        } else if (std.mem.eql(u8, case.label, "URLSAFE_PAD")) {
            if (!std.mem.eql(u8, case.variant_name, "urlsafe") or !case.padding or saw_urlsafe_pad) {
                return error.Base64PerfMatrixMismatch;
            }
            saw_urlsafe_pad = true;
        } else if (std.mem.eql(u8, case.label, "URLSAFE_NO_PAD")) {
            if (!std.mem.eql(u8, case.variant_name, "urlsafe") or case.padding or saw_urlsafe_no_pad) {
                return error.Base64PerfMatrixMismatch;
            }
            saw_urlsafe_no_pad = true;
        } else {
            return error.Base64PerfMatrixMismatch;
        }

        for (fixtures.perf_cases[idx + 1 ..]) |other| {
            if (std.mem.eql(u8, case.label, other.label)) return error.Base64PerfMatrixMismatch;
        }
    }

    if (!saw_std_pad or !saw_std_no_pad or !saw_urlsafe_pad or !saw_urlsafe_no_pad) {
        return error.Base64PerfMatrixMismatch;
    }
}

fn expectExactFitPerfBuffers(case: fixtures.PerfCase) !void {
    const variant = fixtureVariant(case.variant_name);
    const codec = stdCodecs(variant, case.padding);
    const helper_needed = base64.chars(case.payload.len, case.padding);
    const reference_needed = codec.Encoder.calcSize(case.payload.len);

    if (helper_needed != reference_needed) return error.Base64PerfMatrixMismatch;

    var helper_encoded: [fixtures.perf_encoded_buf_size]u8 = undefined;
    var reference_encoded: [fixtures.perf_encoded_buf_size]u8 = undefined;
    const helper_exact = helper_encoded[0..helper_needed];
    const helper_written = try base64.encode(helper_exact, case.payload, case.padding, variant);
    if (helper_written != helper_needed) return error.Base64PerfMatrixMismatch;

    const reference_written = codec.Encoder.encode(reference_encoded[0..reference_needed], case.payload);
    if (!std.mem.eql(u8, helper_exact[0..helper_written], reference_written)) {
        return error.Base64PerfMatrixMismatch;
    }

    if (helper_needed > 0) {
        var truncated_encoded: [fixtures.perf_encoded_buf_size]u8 = [_]u8{0xaa} ** fixtures.perf_encoded_buf_size;
        const truncated_exact = truncated_encoded[0 .. helper_needed - 1];
        try std.testing.expectError(
            base64.EncodeError.DestinationTooSmall,
            base64.encode(truncated_exact, case.payload, case.padding, variant),
        );
        for (truncated_exact) |byte| {
            try std.testing.expectEqual(@as(u8, 0xaa), byte);
        }
    }

    var decoded: [fixtures.perf_payload_buf_size]u8 = undefined;
    const decoded_exact = decoded[0..case.payload.len];
    const decoded_written = try base64.decode(decoded_exact, helper_exact[0..helper_written], case.padding, variant);
    if (decoded_written != case.payload.len) return error.Base64PerfMatrixMismatch;
    if (!std.mem.eql(u8, case.payload, decoded_exact[0..decoded_written])) {
        return error.Base64PerfMatrixMismatch;
    }

    if (case.payload.len > 0) {
        var truncated_decoded: [fixtures.perf_payload_buf_size]u8 = [_]u8{0xdd} ** fixtures.perf_payload_buf_size;
        const truncated_exact = truncated_decoded[0 .. case.payload.len - 1];
        try std.testing.expectError(
            base64.DecodeError.DestinationTooSmall,
            base64.decode(truncated_exact, helper_exact[0..helper_written], case.padding, variant),
        );
        for (truncated_exact) |byte| {
            try std.testing.expectEqual(@as(u8, 0xdd), byte);
        }
    }
}

fn stdCodecs(variant: base64.Variant, padding: bool) std.base64.Codecs {
    return switch (variant) {
        .std => if (padding) std.base64.standard else std.base64.standard_no_pad,
        .urlsafe => if (padding) std.base64.url_safe else std.base64.url_safe_no_pad,
        .imap => unreachable,
    };
}

fn monotonicNs() !u64 {
    var timespec: std.posix.timespec = undefined;
    switch (std.posix.errno(std.posix.system.clock_gettime(std.posix.CLOCK.MONOTONIC, &timespec))) {
        .SUCCESS => {},
        else => return error.ClockUnavailable,
    }
    return (@as(u64, @intCast(timespec.sec)) * std.time.ns_per_s) + @as(u64, @intCast(timespec.nsec));
}

fn sampleAccumulator(bytes: []const u8) u64 {
    if (bytes.len == 0) return 0;
    return @as(u64, bytes.len) +
        @as(u64, bytes[0]) +
        @as(u64, bytes[bytes.len - 1]) +
        @as(u64, bytes[bytes.len / 2]);
}

fn slowdownPct(helper_ns: u64, reference_ns: u64) u64 {
    if (helper_ns <= reference_ns or reference_ns == 0) return 0;
    return @intCast((@as(u128, helper_ns - reference_ns) * 100) / @as(u128, reference_ns));
}

fn medianNs(samples: []u64) u64 {
    std.debug.assert(samples.len == bench_sample_count);
    std.mem.sort(u64, samples, {}, std.sort.asc(u64));
    return samples[samples.len / 2];
}

fn runHelperEncodeBench(case: fixtures.PerfCase, variant: base64.Variant) !BenchResult {
    var encoded: [fixtures.perf_encoded_buf_size]u8 = undefined;
    var accumulator: u64 = 0;
    const start_ns = try monotonicNs();
    var iter: usize = 0;
    while (iter < case.iterations) : (iter += 1) {
        const written = try base64.encode(encoded[0..], case.payload, case.padding, variant);
        accumulator +%= sampleAccumulator(encoded[0..written]);
    }
    return .{ .elapsed_ns = (try monotonicNs()) - start_ns, .accumulator = accumulator };
}

fn runStdEncodeBench(case: fixtures.PerfCase, codec: std.base64.Codecs) !BenchResult {
    var encoded: [fixtures.perf_encoded_buf_size]u8 = undefined;
    var accumulator: u64 = 0;
    const needed = codec.Encoder.calcSize(case.payload.len);
    const start_ns = try monotonicNs();
    var iter: usize = 0;
    while (iter < case.iterations) : (iter += 1) {
        const written = codec.Encoder.encode(encoded[0..needed], case.payload);
        accumulator +%= sampleAccumulator(written);
    }
    return .{ .elapsed_ns = (try monotonicNs()) - start_ns, .accumulator = accumulator };
}

fn runHelperDecodeBench(encoded: []const u8, expected_len: usize, padding: bool, variant: base64.Variant, iterations: usize) !BenchResult {
    var decoded: [fixtures.perf_payload_buf_size]u8 = undefined;
    var accumulator: u64 = 0;
    const start_ns = try monotonicNs();
    var iter: usize = 0;
    while (iter < iterations) : (iter += 1) {
        const written = try base64.decode(decoded[0..expected_len], encoded, padding, variant);
        accumulator +%= sampleAccumulator(decoded[0..written]);
    }
    return .{ .elapsed_ns = (try monotonicNs()) - start_ns, .accumulator = accumulator };
}

fn runStdDecodeBench(encoded: []const u8, expected_len: usize, codec: std.base64.Codecs, iterations: usize) !BenchResult {
    var decoded: [fixtures.perf_payload_buf_size]u8 = undefined;
    var accumulator: u64 = 0;
    const start_ns = try monotonicNs();
    var iter: usize = 0;
    while (iter < iterations) : (iter += 1) {
        try codec.Decoder.decode(decoded[0..expected_len], encoded);
        accumulator +%= sampleAccumulator(decoded[0..expected_len]);
    }
    return .{ .elapsed_ns = (try monotonicNs()) - start_ns, .accumulator = accumulator };
}

pub fn main(init: std.process.Init) !void {
    try validatePerfMatrix();

    const io = init.io;
    var stdout_buffer: [4096]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    var failed = false;

    try stdout_writer.interface.print("PHASE6_BASE64_PERF_CASE_COUNT={d}\n", .{fixtures.perf_cases.len});

    for (fixtures.perf_cases) |case| {
        const variant = fixtureVariant(case.variant_name);
        const codec = stdCodecs(variant, case.padding);
        var helper_encoded: [fixtures.perf_encoded_buf_size]u8 = undefined;
        var std_encoded: [fixtures.perf_encoded_buf_size]u8 = undefined;
        var helper_decoded: [fixtures.perf_payload_buf_size]u8 = undefined;
        var std_decoded: [fixtures.perf_payload_buf_size]u8 = undefined;

        const helper_encoded_len = try base64.encode(helper_encoded[0..], case.payload, case.padding, variant);
        const std_encoded_slice = codec.Encoder.encode(std_encoded[0..codec.Encoder.calcSize(case.payload.len)], case.payload);
        if (!std.mem.eql(u8, helper_encoded[0..helper_encoded_len], std_encoded_slice)) {
            return error.Base64PerfEncodeMismatch;
        }

        const helper_decoded_len = try base64.decode(helper_decoded[0..case.payload.len], helper_encoded[0..helper_encoded_len], case.padding, variant);
        if (helper_decoded_len != case.payload.len or !std.mem.eql(u8, helper_decoded[0..helper_decoded_len], case.payload)) {
            return error.Base64PerfHelperDecodeMismatch;
        }

        const std_decoded_len = try codec.Decoder.calcSizeForSlice(std_encoded_slice);
        if (std_decoded_len != case.payload.len) {
            return error.Base64PerfStdSizeMismatch;
        }
        try codec.Decoder.decode(std_decoded[0..std_decoded_len], std_encoded_slice);
        if (!std.mem.eql(u8, std_decoded[0..std_decoded_len], case.payload)) {
            return error.Base64PerfStdDecodeMismatch;
        }

        var helper_encode_elapsed_samples: [bench_sample_count]u64 = undefined;
        var std_encode_elapsed_samples: [bench_sample_count]u64 = undefined;
        var helper_decode_elapsed_samples: [bench_sample_count]u64 = undefined;
        var std_decode_elapsed_samples: [bench_sample_count]u64 = undefined;
        var helper_encode_accumulator: u64 = 0;
        var helper_decode_accumulator: u64 = 0;

        for (0..bench_sample_count) |sample_index| {
            const helper_encode_result = try runHelperEncodeBench(case, variant);
            const std_encode_result = try runStdEncodeBench(case, codec);
            const helper_decode_result = try runHelperDecodeBench(helper_encoded[0..helper_encoded_len], case.payload.len, case.padding, variant, case.iterations);
            const std_decode_result = try runStdDecodeBench(std_encoded_slice, case.payload.len, codec, case.iterations);

            helper_encode_elapsed_samples[sample_index] = helper_encode_result.elapsed_ns;
            std_encode_elapsed_samples[sample_index] = std_encode_result.elapsed_ns;
            helper_decode_elapsed_samples[sample_index] = helper_decode_result.elapsed_ns;
            std_decode_elapsed_samples[sample_index] = std_decode_result.elapsed_ns;

            if (helper_encode_result.accumulator != std_encode_result.accumulator or helper_decode_result.accumulator != std_decode_result.accumulator) {
                return error.Base64PerfAccumulatorMismatch;
            }

            helper_encode_accumulator = helper_encode_result.accumulator;
            helper_decode_accumulator = helper_decode_result.accumulator;
        }

        const helper_encode_ns = medianNs(helper_encode_elapsed_samples[0..]);
        const std_encode_ns = medianNs(std_encode_elapsed_samples[0..]);
        const helper_decode_ns = medianNs(helper_decode_elapsed_samples[0..]);
        const std_decode_ns = medianNs(std_decode_elapsed_samples[0..]);
        const encode_slowdown_pct = slowdownPct(helper_encode_ns, std_encode_ns);
        const decode_slowdown_pct = slowdownPct(helper_decode_ns, std_decode_ns);

        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_ITERATIONS={d}\n", .{ case.label, case.iterations });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_ENCODE_HELPER_NS={d}\n", .{ case.label, helper_encode_ns });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_ENCODE_REFERENCE_NS={d}\n", .{ case.label, std_encode_ns });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_ENCODE_SLOWDOWN_PCT={d}\n", .{ case.label, encode_slowdown_pct });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_ENCODE_THRESHOLD_PCT={d}\n", .{ case.label, case.max_encode_slowdown_pct });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_DECODE_HELPER_NS={d}\n", .{ case.label, helper_decode_ns });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_DECODE_REFERENCE_NS={d}\n", .{ case.label, std_decode_ns });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_DECODE_SLOWDOWN_PCT={d}\n", .{ case.label, decode_slowdown_pct });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_DECODE_THRESHOLD_PCT={d}\n", .{ case.label, case.max_decode_slowdown_pct });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_ACCUMULATOR={d}\n", .{ case.label, helper_encode_accumulator +% helper_decode_accumulator });

        if (encode_slowdown_pct > case.max_encode_slowdown_pct or decode_slowdown_pct > case.max_decode_slowdown_pct) {
            failed = true;
            try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}=fail\n", .{case.label});
        } else {
            try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}=pass\n", .{case.label});
        }
    }

    try stdout_writer.interface.print("PHASE6_BASE64_PERF={s}\n", .{if (failed) "fail" else "pass"});
    try stdout_writer.interface.flush();

    if (failed) return error.Base64PerfRegression;
}

test "phase 6 base64 perf matrix preflight stays aligned with the documented packet" {
    try validatePerfMatrix();
}

test "phase 6 base64 perf preflight exact-fit and truncated buffers stay aligned with the documented packet" {
    for (fixtures.perf_cases) |case| {
        try expectExactFitPerfBuffers(case);
    }
}

test "medianNs selects the middle sample after sorting" {
    var samples = [_]u64{ 91, 12, 47 };
    try std.testing.expectEqual(@as(u64, 47), medianNs(samples[0..]));
}
