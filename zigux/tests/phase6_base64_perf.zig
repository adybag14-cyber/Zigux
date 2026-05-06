const std = @import("std");
const base64 = @import("base64");
const fixtures = @import("fixtures/phase6_base64_vectors.zig");

const Io = std.Io;

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

        const helper_encode_result = try runHelperEncodeBench(case, variant);
        const std_encode_result = try runStdEncodeBench(case, codec);
        const helper_decode_result = try runHelperDecodeBench(helper_encoded[0..helper_encoded_len], case.payload.len, case.padding, variant, case.iterations);
        const std_decode_result = try runStdDecodeBench(std_encoded_slice, case.payload.len, codec, case.iterations);

        const encode_slowdown_pct = slowdownPct(helper_encode_result.elapsed_ns, std_encode_result.elapsed_ns);
        const decode_slowdown_pct = slowdownPct(helper_decode_result.elapsed_ns, std_decode_result.elapsed_ns);

        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_ITERATIONS={d}\n", .{ case.label, case.iterations });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_ENCODE_HELPER_NS={d}\n", .{ case.label, helper_encode_result.elapsed_ns });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_ENCODE_REFERENCE_NS={d}\n", .{ case.label, std_encode_result.elapsed_ns });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_ENCODE_SLOWDOWN_PCT={d}\n", .{ case.label, encode_slowdown_pct });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_ENCODE_THRESHOLD_PCT={d}\n", .{ case.label, case.max_encode_slowdown_pct });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_DECODE_HELPER_NS={d}\n", .{ case.label, helper_decode_result.elapsed_ns });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_DECODE_REFERENCE_NS={d}\n", .{ case.label, std_decode_result.elapsed_ns });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_DECODE_SLOWDOWN_PCT={d}\n", .{ case.label, decode_slowdown_pct });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_DECODE_THRESHOLD_PCT={d}\n", .{ case.label, case.max_decode_slowdown_pct });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_ACCUMULATOR={d}\n", .{ case.label, helper_encode_result.accumulator +% helper_decode_result.accumulator });

        if (helper_encode_result.accumulator != std_encode_result.accumulator or helper_decode_result.accumulator != std_decode_result.accumulator) {
            return error.Base64PerfAccumulatorMismatch;
        }

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
