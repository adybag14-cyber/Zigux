const std = @import("std");
const base64 = @import("base64");

const PerfCase = struct {
    label: []const u8,
    size: usize,
    reps: usize,
    max_encode_slowdown_pct: u16,
    max_decode_slowdown_pct: u16,
};

const perf_cases = [_]PerfCase{
    .{ .label = "64B", .size = 64, .reps = 20_000, .max_encode_slowdown_pct = 125, .max_decode_slowdown_pct = 225 },
    .{ .label = "1KB", .size = 1024, .reps = 4_000, .max_encode_slowdown_pct = 125, .max_decode_slowdown_pct = 225 },
};

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

fn benchTime(io: std.Io) i96 {
    return std.Io.Clock.awake.now(io).nanoseconds;
}

fn benchHelperEncode(src: []const u8, dst: []u8, reps: usize, io: std.Io) !struct { elapsed: i96, sink: u32 } {
    var sink: u32 = 0;
    const started_at = benchTime(io);
    for (0..reps) |_| {
        const len = try base64.encode(dst, src, true, .std);
        sink +%= @as(u32, @intCast(len));
        sink +%= dst[0];
        sink +%= dst[@max(len, 1) - 1];
    }
    return .{ .elapsed = benchTime(io) - started_at, .sink = sink };
}

fn benchReferenceEncode(src: []const u8, dst: []u8, reps: usize, io: std.Io) struct { elapsed: i96, sink: u32 } {
    var sink: u32 = 0;
    const started_at = benchTime(io);
    for (0..reps) |_| {
        const encoded = std.base64.standard.Encoder.encode(dst, src);
        sink +%= @as(u32, @intCast(encoded.len));
        sink +%= encoded[0];
        sink +%= encoded[@max(encoded.len, 1) - 1];
    }
    return .{ .elapsed = benchTime(io) - started_at, .sink = sink };
}

fn benchHelperDecode(encoded: []const u8, dst: []u8, expected_len: usize, reps: usize, io: std.Io) !struct { elapsed: i96, sink: u32 } {
    var sink: u32 = 0;
    const started_at = benchTime(io);
    for (0..reps) |_| {
        const len = try base64.decode(dst, encoded, true, .std);
        std.debug.assert(len == expected_len);
        sink +%= @as(u32, @intCast(len));
        sink +%= dst[0];
        sink +%= dst[@max(len, 1) - 1];
    }
    return .{ .elapsed = benchTime(io) - started_at, .sink = sink };
}

fn benchReferenceDecode(encoded: []const u8, dst: []u8, expected_len: usize, reps: usize, io: std.Io) !struct { elapsed: i96, sink: u32 } {
    var sink: u32 = 0;
    const started_at = benchTime(io);
    for (0..reps) |_| {
        try std.base64.standard.Decoder.decode(dst[0..expected_len], encoded);
        sink +%= @as(u32, @intCast(expected_len));
        sink +%= dst[0];
        sink +%= dst[@max(expected_len, 1) - 1];
    }
    return .{ .elapsed = benchTime(io) - started_at, .sink = sink };
}

fn runPerfCase(case: PerfCase, io: std.Io) !PerfResult {
    var input: [1024]u8 = undefined;
    var helper_encoded: [1368]u8 = undefined;
    var reference_encoded: [1368]u8 = undefined;
    var helper_decoded: [1024]u8 = undefined;
    var reference_decoded: [1024]u8 = undefined;

    std.debug.assert(case.size <= input.len);

    var prng = std.Random.DefaultPrng.init(0x5a17_2026_0640_0001);
    prng.random().bytes(input[0..case.size]);

    const encoded_len = try base64.encode(helper_encoded[0..], input[0..case.size], true, .std);
    const reference_encoded_slice = std.base64.standard.Encoder.encode(reference_encoded[0..], input[0..case.size]);
    const decoded_len = try base64.decode(helper_decoded[0..], helper_encoded[0..encoded_len], true, .std);
    const reference_decoded_len = try std.base64.standard.Decoder.calcSizeForSlice(reference_encoded_slice);
    try std.base64.standard.Decoder.decode(reference_decoded[0..reference_decoded_len], reference_encoded_slice);

    try std.testing.expectEqual(encoded_len, reference_encoded_slice.len);
    try std.testing.expectEqual(case.size, decoded_len);
    try std.testing.expectEqual(case.size, reference_decoded_len);
    try std.testing.expectEqualSlices(u8, helper_encoded[0..encoded_len], reference_encoded_slice);
    try std.testing.expectEqualSlices(u8, input[0..case.size], helper_decoded[0..decoded_len]);
    try std.testing.expectEqualSlices(u8, input[0..case.size], reference_decoded[0..reference_decoded_len]);

    const helper_encode_warmup = try benchHelperEncode(input[0..case.size], helper_encoded[0..], case.reps, io);
    const reference_encode_warmup = benchReferenceEncode(input[0..case.size], reference_encoded[0..], case.reps, io);
    const helper_decode_warmup = try benchHelperDecode(reference_encoded_slice, helper_decoded[0..], decoded_len, case.reps, io);
    const reference_decode_warmup = try benchReferenceDecode(reference_encoded_slice, reference_decoded[0..], reference_decoded_len, case.reps, io);

    var helper_encode_elapsed = helper_encode_warmup.elapsed;
    var reference_encode_elapsed = reference_encode_warmup.elapsed;
    var helper_decode_elapsed = helper_decode_warmup.elapsed;
    var reference_decode_elapsed = reference_decode_warmup.elapsed;
    var helper_encode_sink = helper_encode_warmup.sink;
    var reference_encode_sink = reference_encode_warmup.sink;
    var helper_decode_sink = helper_decode_warmup.sink;
    var reference_decode_sink = reference_decode_warmup.sink;

    for (0..2) |_| {
        const helper_encode_sample = try benchHelperEncode(input[0..case.size], helper_encoded[0..], case.reps, io);
        if (helper_encode_sample.elapsed < helper_encode_elapsed) {
            helper_encode_elapsed = helper_encode_sample.elapsed;
            helper_encode_sink = helper_encode_sample.sink;
        }
        const reference_encode_sample = benchReferenceEncode(input[0..case.size], reference_encoded[0..], case.reps, io);
        if (reference_encode_sample.elapsed < reference_encode_elapsed) {
            reference_encode_elapsed = reference_encode_sample.elapsed;
            reference_encode_sink = reference_encode_sample.sink;
        }
        const helper_decode_sample = try benchHelperDecode(reference_encoded_slice, helper_decoded[0..], decoded_len, case.reps, io);
        if (helper_decode_sample.elapsed < helper_decode_elapsed) {
            helper_decode_elapsed = helper_decode_sample.elapsed;
            helper_decode_sink = helper_decode_sample.sink;
        }
        const reference_decode_sample = try benchReferenceDecode(reference_encoded_slice, reference_decoded[0..], reference_decoded_len, case.reps, io);
        if (reference_decode_sample.elapsed < reference_decode_elapsed) {
            reference_decode_elapsed = reference_decode_sample.elapsed;
            reference_decode_sink = reference_decode_sample.sink;
        }
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
    const encode_slowdown_pct = @divFloor(helper_encode_ns_per_op * 100, reference_encode_ns_per_op);
    const decode_slowdown_pct = @divFloor(helper_decode_ns_per_op * 100, reference_decode_ns_per_op);

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
