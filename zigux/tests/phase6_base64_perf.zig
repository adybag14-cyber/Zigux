const std = @import("std");
const base64 = @import("base64");
const fixtures = @import("fixtures/phase6_base64_vectors.zig");

pub fn main(init: std.process.Init) !void {
    const io = init.io;

    for (fixtures.perf_cases) |case| {
        const result = try runPerfCase(case, io);
        std.debug.print(
            "phase6-base64-perf {s} encode_ns_per_op={} decode_ns_per_op={} encoded_len={} decoded_len={}\n",
            .{ case.label, result.encode_ns_per_op, result.decode_ns_per_op, result.encoded_len, result.decoded_len },
        );
    }
}

const PerfResult = struct {
    encode_ns_per_op: u64,
    decode_ns_per_op: u64,
    encoded_len: usize,
    decoded_len: usize,
};

fn benchTime(io: std.Io) i96 {
    return std.Io.Clock.awake.now(io).nanoseconds;
}

fn runPerfCase(case: fixtures.PerfCase, io: std.Io) !PerfResult {
    var input: [1024]u8 = undefined;
    var encoded: [1368]u8 = undefined;
    var decoded: [1024]u8 = undefined;

    std.debug.assert(case.size <= input.len);

    fixtures.fillPerfPayload(input[0..case.size]);

    const encoded_len = try base64.encode(encoded[0..], input[0..case.size], true, .std);
    const decoded_len = try base64.decode(decoded[0..], encoded[0..encoded_len], true, .std);

    try std.testing.expectEqual(case.size, decoded_len);
    try std.testing.expectEqualSlices(u8, input[0..case.size], decoded[0..decoded_len]);

    const encode_start = benchTime(io);
    for (0..case.reps) |_| {
        const len = try base64.encode(encoded[0..], input[0..case.size], true, .std);
        std.debug.assert(len == encoded_len);
    }
    const encode_elapsed = benchTime(io) - encode_start;

    const decode_start = benchTime(io);
    for (0..case.reps) |_| {
        const len = try base64.decode(decoded[0..], encoded[0..encoded_len], true, .std);
        std.debug.assert(len == decoded_len);
    }
    const decode_elapsed = benchTime(io) - decode_start;

    try std.testing.expectEqualSlices(u8, input[0..case.size], decoded[0..decoded_len]);

    return .{
        .encode_ns_per_op = @max(@as(u64, @intCast(@divFloor(encode_elapsed, @as(i96, @intCast(case.reps))))), 1),
        .decode_ns_per_op = @max(@as(u64, @intCast(@divFloor(decode_elapsed, @as(i96, @intCast(case.reps))))), 1),
        .encoded_len = encoded_len,
        .decoded_len = decoded_len,
    };
}
