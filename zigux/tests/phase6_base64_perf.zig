const std = @import("std");
const base64 = @import("base64");

const PerfCase = struct {
    label: []const u8,
    size: usize,
    reps: usize,
};

const perf_cases = [_]PerfCase{
    .{ .label = "64B", .size = 64, .reps = 20_000 },
    .{ .label = "1KB", .size = 1024, .reps = 4_000 },
};

pub fn main(init: std.process.Init) !void {
    const io = init.io;

    for (perf_cases) |case| {
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

fn runPerfCase(case: PerfCase, io: std.Io) !PerfResult {
    var input: [1024]u8 = undefined;
    var encoded: [1368]u8 = undefined;
    var decoded: [1024]u8 = undefined;

    std.debug.assert(case.size <= input.len);

    var prng = std.Random.DefaultPrng.init(0x5a17_2026_0640_0001);
    prng.random().bytes(input[0..case.size]);

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
