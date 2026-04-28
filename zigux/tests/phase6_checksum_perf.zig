const std = @import("std");
const checksum = @import("checksum");
const fixtures = @import("fixtures/phase6_checksum_vectors.zig");

pub fn main(init: std.process.Init) !void {
    const io = init.io;

    for (fixtures.perf_cases) |case| {
        const result = try runPerfCase(case, io);
        std.debug.print(
            "phase6-checksum-perf {s} len={} reps={} helper_ns_per_call={} helper_ns_per_byte={d:.2} reference_ns_per_call={} reference_ns_per_byte={d:.2} slowdown_pct={} folded=0x{x:0>4} sink=0x{x:0>8}\n",
            .{
                case.label,
                case.len,
                case.reps,
                result.helper_ns_per_call,
                result.helper_ns_per_byte,
                result.reference_ns_per_call,
                result.reference_ns_per_byte,
                result.slowdown_pct,
                result.folded,
                result.sink,
            },
        );
    }
}

const PerfResult = struct {
    helper_ns_per_call: u64,
    helper_ns_per_byte: f64,
    reference_ns_per_call: u64,
    reference_ns_per_byte: f64,
    slowdown_pct: u64,
    folded: u16,
    sink: u32,
};

const BenchResult = struct {
    elapsed: i96,
    sink: u32,
};

fn referencePartial(bytes: []const u8, seed: u32) u32 {
    var acc: u64 = seed;
    var index: usize = 0;

    while (index + 1 < bytes.len) : (index += 2) {
        acc += (@as(u64, bytes[index]) << 8) | bytes[index + 1];
    }

    if (index < bytes.len) {
        acc += @as(u64, bytes[index]) << 8;
    }

    while ((acc >> 16) != 0) {
        acc = (acc & 0xffff) + (acc >> 16);
    }

    return @intCast(acc);
}

fn benchTime(io: std.Io) i96 {
    return std.Io.Clock.awake.now(io).nanoseconds;
}

fn benchHelper(payload: []const u8, reps: usize, seed: u32, io: std.Io) BenchResult {
    var sink: u32 = 0;
    const started_at = benchTime(io);
    for (0..reps) |_| {
        sink +%= checksum.partial(payload, seed);
    }
    return .{ .elapsed = benchTime(io) - started_at, .sink = sink };
}

fn benchReference(payload: []const u8, reps: usize, seed: u32, io: std.Io) BenchResult {
    var sink: u32 = 0;
    const started_at = benchTime(io);
    for (0..reps) |_| {
        sink +%= referencePartial(payload, seed);
    }
    return .{ .elapsed = benchTime(io) - started_at, .sink = sink };
}

fn median3(a: u64, b: u64, c: u64) u64 {
    return a + b + c - @min(a, @min(b, c)) - @max(a, @max(b, c));
}

fn runPerfCase(case: fixtures.PerfCase, io: std.Io) !PerfResult {
    const allocator = std.heap.page_allocator;
    const payload = try allocator.alloc(u8, case.len);
    defer allocator.free(payload);
    fixtures.fillPerfPayload(payload);

    const expected_partial = referencePartial(payload, case.seed);
    const expected_folded = ~@as(u16, @truncate(expected_partial));

    try std.testing.expectEqual(expected_partial, checksum.partial(payload, case.seed));
    try std.testing.expectEqual(expected_folded, checksum.fold(expected_partial));

    _ = benchHelper(payload, case.reps, case.seed, io);
    _ = benchReference(payload, case.reps, case.seed, io);

    var helper_elapsed: i96 = std.math.maxInt(i96);
    var reference_elapsed: i96 = std.math.maxInt(i96);
    var sink: u32 = 0;
    var slowdown_samples: [3]u64 = undefined;

    for (0..slowdown_samples.len) |sample_index| {
        const helper_sample = benchHelper(payload, case.reps, case.seed, io);
        const reference_sample = benchReference(payload, case.reps, case.seed, io);

        try std.testing.expect(helper_sample.elapsed > 0);
        try std.testing.expect(reference_sample.elapsed > 0);
        try std.testing.expect(helper_sample.sink != 0 or expected_partial == 0);
        try std.testing.expectEqual(helper_sample.sink, reference_sample.sink);

        if (helper_sample.elapsed < helper_elapsed) {
            helper_elapsed = helper_sample.elapsed;
            sink = helper_sample.sink;
        }
        if (reference_sample.elapsed < reference_elapsed) {
            reference_elapsed = reference_sample.elapsed;
        }

        slowdown_samples[sample_index] = @as(u64, @intCast(@divFloor(
            helper_sample.elapsed * @as(i96, 100),
            reference_sample.elapsed,
        )));
    }

    const slowdown_pct = median3(
        slowdown_samples[0],
        slowdown_samples[1],
        slowdown_samples[2],
    );

    const helper_ns_per_call = @max(@as(u64, @intCast(@divFloor(helper_elapsed, @as(i96, @intCast(case.reps))))), 1);
    const reference_ns_per_call = @max(@as(u64, @intCast(@divFloor(reference_elapsed, @as(i96, @intCast(case.reps))))), 1);
    const total_bytes = case.reps * case.len;
    const helper_ns_per_byte = @as(f64, @floatFromInt(@max(helper_elapsed, 1))) /
        @as(f64, @floatFromInt(@max(total_bytes, 1)));
    const reference_ns_per_byte = @as(f64, @floatFromInt(@max(reference_elapsed, 1))) /
        @as(f64, @floatFromInt(@max(total_bytes, 1)));

    try std.testing.expect(slowdown_pct <= case.max_slowdown_pct);

    return .{
        .helper_ns_per_call = helper_ns_per_call,
        .helper_ns_per_byte = helper_ns_per_byte,
        .reference_ns_per_call = reference_ns_per_call,
        .reference_ns_per_byte = reference_ns_per_byte,
        .slowdown_pct = slowdown_pct,
        .folded = expected_folded,
        .sink = sink,
    };
}
