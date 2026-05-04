const std = @import("std");
const base64 = @import("base64");
const fixtures = @import("fixtures/phase6_base64_vectors.zig");

const perf_cases = fixtures.perf_cases;
const ReferenceKind = fixtures.ReferenceKind;

pub fn main(init: std.process.Init) !void {
    const io = init.io;

    for (perf_cases) |case| {
        const result = try runPerfCase(case, io);
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

const ExpectedPerfCase = struct {
    label: []const u8,
    size: usize,
    reps: usize,
    max_encode_slowdown_pct: u16,
    max_decode_slowdown_pct: u16,
    padding: bool,
    variant: base64.Variant,
    reference_kind: ReferenceKind,
};

const expected_perf_cases = [_]ExpectedPerfCase{
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

fn median3(a: u64, b: u64, c: u64) u64 {
    return a + b + c - @min(a, @min(b, c)) - @max(a, @max(b, c));
}

fn benchTime(io: std.Io) i96 {
    return std.Io.Clock.awake.now(io).nanoseconds;
}

fn benchHelperEncode(src: []const u8, dst: []u8, reps: usize, padding: bool, variant: base64.Variant, io: std.Io) !struct { elapsed: i96, sink: u32 } {
    var sink: u32 = 0;
    const started_at = benchTime(io);
    for (0..reps) |_| {
        const len = try base64.encode(dst, src, padding, variant);
        sink +%= @as(u32, @intCast(len));
        sink +%= dst[0];
        sink +%= dst[@max(len, 1) - 1];
    }
    return .{ .elapsed = benchTime(io) - started_at, .sink = sink };
}

fn referenceEncode(kind: ReferenceKind, dst: []u8, src: []const u8) []const u8 {
    return switch (kind) {
        .standard => std.base64.standard.Encoder.encode(dst, src),
        .url_safe_padded => std.base64.url_safe.Encoder.encode(dst, src),
        .url_safe_no_pad => std.base64.url_safe_no_pad.Encoder.encode(dst, src),
        .imap_padded => encodeImapReference(dst, src, true),
        .imap_no_pad => encodeImapReference(dst, src, false),
    };
}

fn encodeImapReference(dst: []u8, src: []const u8, padding: bool) []const u8 {
    const standard_encoded = std.base64.standard.Encoder.encode(dst, src);
    var len = standard_encoded.len;
    if (!padding) {
        while (len > 0 and dst[len - 1] == '=') {
            len -= 1;
        }
    }

    for (dst[0..len]) |*byte| {
        if (byte.* == '/') {
            byte.* = ',';
        }
    }
    return dst[0..len];
}

fn benchReferenceEncode(kind: ReferenceKind, src: []const u8, dst: []u8, reps: usize, io: std.Io) struct { elapsed: i96, sink: u32 } {
    var sink: u32 = 0;
    const started_at = benchTime(io);
    for (0..reps) |_| {
        const encoded = referenceEncode(kind, dst, src);
        sink +%= @as(u32, @intCast(encoded.len));
        sink +%= encoded[0];
        sink +%= encoded[@max(encoded.len, 1) - 1];
    }
    return .{ .elapsed = benchTime(io) - started_at, .sink = sink };
}

fn benchHelperDecode(encoded: []const u8, dst: []u8, expected_len: usize, reps: usize, padding: bool, variant: base64.Variant, io: std.Io) !struct { elapsed: i96, sink: u32 } {
    var sink: u32 = 0;
    const started_at = benchTime(io);
    for (0..reps) |_| {
        const len = try base64.decode(dst, encoded, padding, variant);
        std.debug.assert(len == expected_len);
        sink +%= @as(u32, @intCast(len));
        sink +%= dst[0];
        sink +%= dst[@max(len, 1) - 1];
    }
    return .{ .elapsed = benchTime(io) - started_at, .sink = sink };
}

fn referenceDecodedLen(kind: ReferenceKind, encoded: []const u8, scratch: []u8) !usize {
    return switch (kind) {
        .standard => std.base64.standard.Decoder.calcSizeForSlice(encoded),
        .url_safe_padded => std.base64.url_safe.Decoder.calcSizeForSlice(encoded),
        .url_safe_no_pad => std.base64.url_safe_no_pad.Decoder.calcSizeForSlice(encoded),
        .imap_padded => std.base64.standard.Decoder.calcSizeForSlice(try normalizeImapDecodeInput(scratch, encoded)),
        .imap_no_pad => std.base64.standard.Decoder.calcSizeForSlice(try normalizeImapDecodeInput(scratch, encoded)),
    };
}

fn referenceDecode(kind: ReferenceKind, dst: []u8, encoded: []const u8, scratch: []u8) !void {
    switch (kind) {
        .standard => try std.base64.standard.Decoder.decode(dst, encoded),
        .url_safe_padded => try std.base64.url_safe.Decoder.decode(dst, encoded),
        .url_safe_no_pad => try std.base64.url_safe_no_pad.Decoder.decode(dst, encoded),
        .imap_padded => try std.base64.standard.Decoder.decode(dst, try normalizeImapDecodeInput(scratch, encoded)),
        .imap_no_pad => try std.base64.standard.Decoder.decode(dst, try normalizeImapDecodeInput(scratch, encoded)),
    }
}

fn normalizeImapDecodeInput(scratch: []u8, encoded: []const u8) ![]const u8 {
    if (encoded.len > scratch.len) {
        return error.InvalidInput;
    }

    @memcpy(scratch[0..encoded.len], encoded);
    for (scratch[0..encoded.len]) |*byte| {
        if (byte.* == ',') {
            byte.* = '/';
        }
    }

    var normalized_len = encoded.len;
    while ((normalized_len % 4) != 0) : (normalized_len += 1) {
        if (normalized_len >= scratch.len) {
            return error.InvalidInput;
        }
        scratch[normalized_len] = '=';
    }

    return scratch[0..normalized_len];
}

fn benchReferenceDecode(kind: ReferenceKind, encoded: []const u8, dst: []u8, expected_len: usize, reps: usize, io: std.Io) !struct { elapsed: i96, sink: u32 } {
    var sink: u32 = 0;
    var scratch: [1368]u8 = undefined;
    const started_at = benchTime(io);
    for (0..reps) |_| {
        try referenceDecode(kind, dst[0..expected_len], encoded, scratch[0..]);
        sink +%= @as(u32, @intCast(expected_len));
        sink +%= dst[0];
        sink +%= dst[@max(expected_len, 1) - 1];
    }
    return .{ .elapsed = benchTime(io) - started_at, .sink = sink };
}

fn runPerfCase(case: fixtures.PerfCase, io: std.Io) !PerfResult {
    var input: [1024]u8 = undefined;
    var helper_encoded: [1368]u8 = undefined;
    var reference_encoded: [1368]u8 = undefined;
    var reference_decode_input: [1368]u8 = undefined;
    var helper_decoded: [1024]u8 = undefined;
    var reference_decoded: [1024]u8 = undefined;

    std.debug.assert(case.size <= input.len);

    fixtures.fillPerfPayload(input[0..case.size]);

    const encoded_len = try base64.encode(helper_encoded[0..], input[0..case.size], case.padding, case.variant);
    const reference_encoded_slice = referenceEncode(case.reference_kind, reference_encoded[0..], input[0..case.size]);
    const decoded_len = try base64.decode(helper_decoded[0..], helper_encoded[0..encoded_len], case.padding, case.variant);
    const reference_decoded_len = try referenceDecodedLen(case.reference_kind, reference_encoded_slice, reference_decode_input[0..]);
    try referenceDecode(case.reference_kind, reference_decoded[0..reference_decoded_len], reference_encoded_slice, reference_decode_input[0..]);

    try std.testing.expectEqual(encoded_len, reference_encoded_slice.len);
    try std.testing.expectEqual(case.size, decoded_len);
    try std.testing.expectEqual(case.size, reference_decoded_len);
    try std.testing.expectEqualSlices(u8, helper_encoded[0..encoded_len], reference_encoded_slice);
    try std.testing.expectEqualSlices(u8, input[0..case.size], helper_decoded[0..decoded_len]);
    try std.testing.expectEqualSlices(u8, input[0..case.size], reference_decoded[0..reference_decoded_len]);

    const helper_encode_warmup = try benchHelperEncode(input[0..case.size], helper_encoded[0..], case.reps, case.padding, case.variant, io);
    const reference_encode_warmup = benchReferenceEncode(case.reference_kind, input[0..case.size], reference_encoded[0..], case.reps, io);
    const helper_decode_warmup = try benchHelperDecode(reference_encoded_slice, helper_decoded[0..], decoded_len, case.reps, case.padding, case.variant, io);
    const reference_decode_warmup = try benchReferenceDecode(case.reference_kind, reference_encoded_slice, reference_decoded[0..], reference_decoded_len, case.reps, io);

    var helper_encode_elapsed = helper_encode_warmup.elapsed;
    var reference_encode_elapsed = reference_encode_warmup.elapsed;
    var helper_decode_elapsed = helper_decode_warmup.elapsed;
    var reference_decode_elapsed = reference_decode_warmup.elapsed;
    var helper_encode_sink = helper_encode_warmup.sink;
    var reference_encode_sink = reference_encode_warmup.sink;
    var helper_decode_sink = helper_decode_warmup.sink;
    var reference_decode_sink = reference_decode_warmup.sink;
    var encode_slowdown_samples: [3]u64 = undefined;
    var decode_slowdown_samples: [3]u64 = undefined;

    for (0..encode_slowdown_samples.len) |sample_index| {
        const helper_encode_sample = try benchHelperEncode(input[0..case.size], helper_encoded[0..], case.reps, case.padding, case.variant, io);
        if (helper_encode_sample.elapsed < helper_encode_elapsed) {
            helper_encode_elapsed = helper_encode_sample.elapsed;
            helper_encode_sink = helper_encode_sample.sink;
        }
        const reference_encode_sample = benchReferenceEncode(case.reference_kind, input[0..case.size], reference_encoded[0..], case.reps, io);
        if (reference_encode_sample.elapsed < reference_encode_elapsed) {
            reference_encode_elapsed = reference_encode_sample.elapsed;
            reference_encode_sink = reference_encode_sample.sink;
        }
        const helper_decode_sample = try benchHelperDecode(reference_encoded_slice, helper_decoded[0..], decoded_len, case.reps, case.padding, case.variant, io);
        if (helper_decode_sample.elapsed < helper_decode_elapsed) {
            helper_decode_elapsed = helper_decode_sample.elapsed;
            helper_decode_sink = helper_decode_sample.sink;
        }
        const reference_decode_sample = try benchReferenceDecode(case.reference_kind, reference_encoded_slice, reference_decoded[0..], reference_decoded_len, case.reps, io);
        if (reference_decode_sample.elapsed < reference_decode_elapsed) {
            reference_decode_elapsed = reference_decode_sample.elapsed;
            reference_decode_sink = reference_decode_sample.sink;
        }

        try std.testing.expect(helper_encode_sample.elapsed > 0);
        try std.testing.expect(reference_encode_sample.elapsed > 0);
        try std.testing.expect(helper_decode_sample.elapsed > 0);
        try std.testing.expect(reference_decode_sample.elapsed > 0);

        encode_slowdown_samples[sample_index] = @as(u64, @intCast(@divFloor(
            helper_encode_sample.elapsed * @as(i96, 100),
            reference_encode_sample.elapsed,
        )));
        decode_slowdown_samples[sample_index] = @as(u64, @intCast(@divFloor(
            helper_decode_sample.elapsed * @as(i96, 100),
            reference_decode_sample.elapsed,
        )));
    }
    try std.testing.expect(helper_encode_elapsed > 0);
    try std.testing.expect(reference_encode_elapsed > 0);
    try std.testing.expect(helper_decode_elapsed > 0);
    try std.testing.expect(reference_decode_elapsed > 0);
    try std.testing.expectEqual(helper_encode_sink, reference_encode_sink);
    try std.testing.expectEqual(helper_decode_sink, reference_decode_sink);
    try std.testing.expectEqualSlices(u8, helper_encoded[0..encoded_len], reference_encoded_slice);
    try std.testing.expectEqualSlices(u8, input[0..case.size], helper_decoded[0..decoded_len]);
    try std.testing.expectEqualSlices(u8, input[0..case.size], reference_decoded[0..reference_decoded_len]);

    const helper_encode_ns_per_op = @max(@as(u64, @intCast(@divFloor(helper_encode_elapsed, @as(i96, @intCast(case.reps))))), 1);
    const helper_decode_ns_per_op = @max(@as(u64, @intCast(@divFloor(helper_decode_elapsed, @as(i96, @intCast(case.reps))))), 1);
    const reference_encode_ns_per_op = @max(@as(u64, @intCast(@divFloor(reference_encode_elapsed, @as(i96, @intCast(case.reps))))), 1);
    const reference_decode_ns_per_op = @max(@as(u64, @intCast(@divFloor(reference_decode_elapsed, @as(i96, @intCast(case.reps))))), 1);
    const encode_slowdown_pct = median3(
        encode_slowdown_samples[0],
        encode_slowdown_samples[1],
        encode_slowdown_samples[2],
    );
    const decode_slowdown_pct = median3(
        decode_slowdown_samples[0],
        decode_slowdown_samples[1],
        decode_slowdown_samples[2],
    );

    try std.testing.expect(encode_slowdown_pct <= case.max_encode_slowdown_pct);
    try std.testing.expect(decode_slowdown_pct <= case.max_decode_slowdown_pct);

    return .{
        .helper_encode_ns_per_op = helper_encode_ns_per_op,
        .helper_decode_ns_per_op = helper_decode_ns_per_op,
        .reference_encode_ns_per_op = reference_encode_ns_per_op,
        .reference_decode_ns_per_op = reference_decode_ns_per_op,
        .encode_slowdown_pct = encode_slowdown_pct,
        .decode_slowdown_pct = decode_slowdown_pct,
        .encoded_len = encoded_len,
        .decoded_len = decoded_len,
    };
}

test "phase 6 base64 perf matrix keeps all shipped variant-and-padding replays" {
    try std.testing.expectEqual(expected_perf_cases.len, perf_cases.len);

    for (expected_perf_cases, perf_cases) |expected, actual| {
        try std.testing.expectEqualStrings(expected.label, actual.label);
        try std.testing.expectEqual(expected.size, actual.size);
        try std.testing.expectEqual(expected.reps, actual.reps);
        try std.testing.expectEqual(expected.max_encode_slowdown_pct, actual.max_encode_slowdown_pct);
        try std.testing.expectEqual(expected.max_decode_slowdown_pct, actual.max_decode_slowdown_pct);
        try std.testing.expectEqual(expected.padding, actual.padding);
        try std.testing.expect(actual.variant == expected.variant);
        try std.testing.expect(actual.reference_kind == expected.reference_kind);
    }
}
