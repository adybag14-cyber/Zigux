const std = @import("std");
const base64 = @import("base64");

const Io = std.Io;

const BenchResult = struct {
    elapsed_ns: u64,
    accumulator: u64,
};

const PerfCase = struct {
    label: []const u8,
    variant: base64.Variant,
    padding: bool,
    payload: []const u8,
    iterations: usize,
    max_encode_slowdown_pct: u64,
    max_decode_slowdown_pct: u64,
};

const payload_text =
    "Phase 6 base64 perf gate payload 0123456789 abcdefghijklmnopqrstuvwxyz " ++ "ABCDEFGHIJKLMNOPQRSTUVWXYZ /+ keep variant transforms reviewable.";

const perf_cases = [_]PerfCase{
    .{ .label = "STD_PADDED", .variant = .std, .padding = true, .payload = payload_text, .iterations = 40_000, .max_encode_slowdown_pct = 250, .max_decode_slowdown_pct = 250 },
    .{ .label = "STD_UNPADDED", .variant = .std, .padding = false, .payload = payload_text, .iterations = 40_000, .max_encode_slowdown_pct = 250, .max_decode_slowdown_pct = 250 },
    .{ .label = "URLSAFE_PADDED", .variant = .urlsafe, .padding = true, .payload = payload_text, .iterations = 40_000, .max_encode_slowdown_pct = 250, .max_decode_slowdown_pct = 250 },
    .{ .label = "URLSAFE_UNPADDED", .variant = .urlsafe, .padding = false, .payload = payload_text, .iterations = 40_000, .max_encode_slowdown_pct = 250, .max_decode_slowdown_pct = 250 },
    .{ .label = "IMAP_PADDED", .variant = .imap, .padding = true, .payload = payload_text, .iterations = 40_000, .max_encode_slowdown_pct = 250, .max_decode_slowdown_pct = 250 },
    .{ .label = "IMAP_UNPADDED", .variant = .imap, .padding = false, .payload = payload_text, .iterations = 40_000, .max_encode_slowdown_pct = 250, .max_decode_slowdown_pct = 250 },
};

fn monotonicNs() !u64 {
    var timespec: std.posix.timespec = undefined;
    switch (std.posix.errno(std.posix.system.clock_gettime(std.posix.CLOCK.MONOTONIC, &timespec))) {
        .SUCCESS => {},
        else => return error.ClockUnavailable,
    }
    return (@as(u64, @intCast(timespec.sec)) * std.time.ns_per_s) + @as(u64, @intCast(timespec.nsec));
}

fn translateImapToStandard(dst: []u8, src: []const u8) []const u8 {
    @memcpy(dst[0..src.len], src);
    for (dst[0..src.len]) |*ch| {
        if (ch.* == ',') ch.* = '/';
    }
    return dst[0..src.len];
}

fn helperAccumulator(bytes: []const u8) u64 {
    if (bytes.len == 0) return 0;
    return @as(u64, bytes.len) +
        @as(u64, bytes[0]) +
        @as(u64, bytes[bytes.len - 1]) +
        @as(u64, bytes[@min(bytes.len / 2, bytes.len - 1)]);
}

fn encodeReference(dst: []u8, src: []const u8, padding: bool, variant: base64.Variant) []const u8 {
    return switch (variant) {
        .std => if (padding)
            std.base64.standard.Encoder.encode(dst, src)
        else
            std.base64.standard_no_pad.Encoder.encode(dst, src),
        .urlsafe => if (padding)
            std.base64.url_safe.Encoder.encode(dst, src)
        else
            std.base64.url_safe_no_pad.Encoder.encode(dst, src),
        .imap => blk: {
            const encoded = if (padding)
                std.base64.standard.Encoder.encode(dst, src)
            else
                std.base64.standard_no_pad.Encoder.encode(dst, src);
            for (dst[0..encoded.len]) |*ch| {
                if (ch.* == '/') ch.* = ',';
            }
            break :blk encoded;
        },
    };
}

fn decodeReference(dst: []u8, src: []const u8, padding: bool, variant: base64.Variant) ![]const u8 {
    var normalized_storage: [256]u8 = undefined;
    const normalized = switch (variant) {
        .std => src,
        .urlsafe => src,
        .imap => translateImapToStandard(normalized_storage[0..src.len], src),
    };

    const decoded_len = switch (variant) {
        .std => if (padding)
            try std.base64.standard.Decoder.calcSizeForSlice(normalized)
        else
            try std.base64.standard_no_pad.Decoder.calcSizeForSlice(normalized),
        .urlsafe => if (padding)
            try std.base64.url_safe.Decoder.calcSizeForSlice(normalized)
        else
            try std.base64.url_safe_no_pad.Decoder.calcSizeForSlice(normalized),
        .imap => if (padding)
            try std.base64.standard.Decoder.calcSizeForSlice(normalized)
        else
            try std.base64.standard_no_pad.Decoder.calcSizeForSlice(normalized),
    };

    switch (variant) {
        .std => if (padding)
            try std.base64.standard.Decoder.decode(dst[0..decoded_len], normalized)
        else
            try std.base64.standard_no_pad.Decoder.decode(dst[0..decoded_len], normalized),
        .urlsafe => if (padding)
            try std.base64.url_safe.Decoder.decode(dst[0..decoded_len], normalized)
        else
            try std.base64.url_safe_no_pad.Decoder.decode(dst[0..decoded_len], normalized),
        .imap => if (padding)
            try std.base64.standard.Decoder.decode(dst[0..decoded_len], normalized)
        else
            try std.base64.standard_no_pad.Decoder.decode(dst[0..decoded_len], normalized),
    }

    return dst[0..decoded_len];
}

fn runHelperEncodeBench(case: PerfCase, output_len: usize) !BenchResult {
    var encoded: [256]u8 = undefined;
    var accumulator: u64 = 0;
    const start_ns = try monotonicNs();
    var iter: usize = 0;
    while (iter < case.iterations) : (iter += 1) {
        const written = try base64.encode(encoded[0..output_len], case.payload, case.padding, case.variant);
        accumulator +%= helperAccumulator(encoded[0..written]);
    }
    return .{ .elapsed_ns = (try monotonicNs()) - start_ns, .accumulator = accumulator };
}

fn runReferenceEncodeBench(case: PerfCase, output_len: usize) !BenchResult {
    var encoded: [256]u8 = undefined;
    var accumulator: u64 = 0;
    const start_ns = try monotonicNs();
    var iter: usize = 0;
    while (iter < case.iterations) : (iter += 1) {
        const slice = encodeReference(encoded[0..output_len], case.payload, case.padding, case.variant);
        accumulator +%= helperAccumulator(slice);
    }
    return .{ .elapsed_ns = (try monotonicNs()) - start_ns, .accumulator = accumulator };
}

fn runHelperDecodeBench(case: PerfCase, encoded: []const u8, decoded_len: usize) !BenchResult {
    var decoded: [256]u8 = undefined;
    var accumulator: u64 = 0;
    const start_ns = try monotonicNs();
    var iter: usize = 0;
    while (iter < case.iterations) : (iter += 1) {
        const written = try base64.decode(decoded[0..decoded_len], encoded, case.padding, case.variant);
        accumulator +%= helperAccumulator(decoded[0..written]);
    }
    return .{ .elapsed_ns = (try monotonicNs()) - start_ns, .accumulator = accumulator };
}

fn runReferenceDecodeBench(case: PerfCase, encoded: []const u8, decoded_len: usize) !BenchResult {
    var decoded: [256]u8 = undefined;
    var accumulator: u64 = 0;
    const start_ns = try monotonicNs();
    var iter: usize = 0;
    while (iter < case.iterations) : (iter += 1) {
        const slice = try decodeReference(decoded[0..decoded_len], encoded, case.padding, case.variant);
        accumulator +%= helperAccumulator(slice);
    }
    return .{ .elapsed_ns = (try monotonicNs()) - start_ns, .accumulator = accumulator };
}

fn slowdownPct(helper_ns: u64, reference_ns: u64) u64 {
    if (helper_ns <= reference_ns or reference_ns == 0) return 0;
    return @intCast((@as(u128, helper_ns - reference_ns) * 100) / @as(u128, reference_ns));
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [4096]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    var failed = false;

    try stdout_writer.interface.print("PHASE6_BASE64_PERF_CASE_COUNT={d}\n", .{perf_cases.len});

    for (perf_cases) |case| {
        const encoded_len = base64.chars(case.payload.len, case.padding);
        var helper_encoded: [256]u8 = undefined;
        var reference_encoded: [256]u8 = undefined;
        const helper_written = try base64.encode(helper_encoded[0..encoded_len], case.payload, case.padding, case.variant);
        const reference_slice = encodeReference(reference_encoded[0..encoded_len], case.payload, case.padding, case.variant);
        try std.testing.expectEqual(encoded_len, helper_written);
        try std.testing.expectEqual(encoded_len, reference_slice.len);
        try std.testing.expectEqualSlices(u8, reference_slice, helper_encoded[0..helper_written]);

        const helper_decoded_len = try base64.bytes(helper_encoded[0..helper_written], case.padding, case.variant);
        try std.testing.expectEqual(case.payload.len, helper_decoded_len);
        var helper_decoded: [256]u8 = undefined;
        const helper_decoded_written = try base64.decode(helper_decoded[0..helper_decoded_len], helper_encoded[0..helper_written], case.padding, case.variant);
        try std.testing.expectEqual(case.payload.len, helper_decoded_written);
        try std.testing.expectEqualSlices(u8, case.payload, helper_decoded[0..helper_decoded_written]);

        var reference_decoded: [256]u8 = undefined;
        const reference_decoded_slice = try decodeReference(reference_decoded[0..case.payload.len], helper_encoded[0..helper_written], case.padding, case.variant);
        try std.testing.expectEqualSlices(u8, case.payload, reference_decoded_slice);

        const helper_encode = try runHelperEncodeBench(case, encoded_len);
        const reference_encode = try runReferenceEncodeBench(case, encoded_len);
        const helper_decode = try runHelperDecodeBench(case, helper_encoded[0..helper_written], helper_decoded_len);
        const reference_decode = try runReferenceDecodeBench(case, helper_encoded[0..helper_written], helper_decoded_len);

        const encode_slowdown_pct = slowdownPct(helper_encode.elapsed_ns, reference_encode.elapsed_ns);
        const decode_slowdown_pct = slowdownPct(helper_decode.elapsed_ns, reference_decode.elapsed_ns);

        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_ITERATIONS={d}\n", .{ case.label, case.iterations });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_ENCODE_HELPER_NS={d}\n", .{ case.label, helper_encode.elapsed_ns });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_ENCODE_REFERENCE_NS={d}\n", .{ case.label, reference_encode.elapsed_ns });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_ENCODE_SLOWDOWN_PCT={d}\n", .{ case.label, encode_slowdown_pct });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_ENCODE_THRESHOLD_PCT={d}\n", .{ case.label, case.max_encode_slowdown_pct });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_DECODE_HELPER_NS={d}\n", .{ case.label, helper_decode.elapsed_ns });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_DECODE_REFERENCE_NS={d}\n", .{ case.label, reference_decode.elapsed_ns });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_DECODE_SLOWDOWN_PCT={d}\n", .{ case.label, decode_slowdown_pct });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_DECODE_THRESHOLD_PCT={d}\n", .{ case.label, case.max_decode_slowdown_pct });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_ENCODE_ACCUMULATOR={d}\n", .{ case.label, helper_encode.accumulator });
        try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_DECODE_ACCUMULATOR={d}\n", .{ case.label, helper_decode.accumulator });

        if (helper_encode.accumulator != reference_encode.accumulator) return error.Base64PerfEncodeAccumulatorMismatch;
        if (helper_decode.accumulator != reference_decode.accumulator) return error.Base64PerfDecodeAccumulatorMismatch;

        const case_failed = encode_slowdown_pct > case.max_encode_slowdown_pct or decode_slowdown_pct > case.max_decode_slowdown_pct;
        if (case_failed) {
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