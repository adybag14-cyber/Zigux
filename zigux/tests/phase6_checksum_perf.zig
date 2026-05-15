const std = @import("std");
const checksum = @import("checksum");
const fixtures = @import("phase6_checksum_vectors");

const PerfResult = struct {
    helper_ns_per_call: u64,
    reference_ns_per_call: u64,
    slowdown_pct: u64,
    helper_compute: u16,
    helper_partial: u32,
};

pub fn main() !void {
    for (fixtures.perf_cases) |case| {
        const result = try runPerfCase(case);
        std.debug.print(
            "phase6-checksum-perf {s} len={} iterations={} helper_ns_per_call={} reference_ns_per_call={} slowdown_pct={} compute=0x{x:0>4} partial=0x{x:0>8}\n",
            .{
                case.label,
                case.payload.len,
                case.iterations,
                result.helper_ns_per_call,
                result.reference_ns_per_call,
                result.slowdown_pct,
                result.helper_compute,
                result.helper_partial,
            },
        );
    }
}

fn monotonicNs() u64 {
    var ts: std.os.linux.timespec = undefined;
    _ = std.os.linux.clock_gettime(.MONOTONIC, &ts);
    return @intCast(@as(i128, ts.sec) * std.time.ns_per_s + ts.nsec);
}

fn referencePartial(bytes: []const u8, seed: u32) u32 {
    var acc: u64 = seed;
    var index: usize = 0;

    while (index + 1 < bytes.len) : (index += 2) {
        acc += (@as(u64, bytes[index]) << 8) | @as(u64, bytes[index + 1]);
    }

    if (index < bytes.len) {
        acc += @as(u64, bytes[index]) << 8;
    }

    while ((acc >> 16) != 0) {
        acc = (acc & 0xffff) + (acc >> 16);
    }

    return @intCast(acc);
}

fn referenceCompute(bytes: []const u8) u16 {
    return ~@as(u16, @truncate(referencePartial(bytes, 0)));
}

const BenchResult = struct {
    elapsed: u64,
    sink: u64,
};

fn benchHelper(payload: []const u8, seed: u32, reps: usize) BenchResult {
    var sink: u64 = 0;
    const started_at = monotonicNs();
    for (0..reps) |_| {
        const partial = checksum.partial(payload, seed);
        const folded = checksum.compute(payload);
        sink +%= partial;
        sink +%= folded;
    }
    return .{ .elapsed = monotonicNs() - started_at, .sink = sink };
}

fn benchReference(payload: []const u8, seed: u32, reps: usize) BenchResult {
    var sink: u64 = 0;
    const started_at = monotonicNs();
    for (0..reps) |_| {
        const partial = referencePartial(payload, seed);
        const folded = referenceCompute(payload);
        sink +%= partial;
        sink +%= folded;
    }
    return .{ .elapsed = monotonicNs() - started_at, .sink = sink };
}

fn median3(a: u64, b: u64, c: u64) u64 {
    return a + b + c - @min(a, @min(b, c)) - @max(a, @max(b, c));
}

fn nsPerCall(elapsed_ns: u64, reps: usize) u64 {
    return @max(@as(u64, 1), @divFloor(elapsed_ns, @as(u64, @intCast(reps))));
}

fn slowdownPct(helper_elapsed: u64, reference_elapsed: u64) u64 {
    return @max(@as(u64, 1), @divFloor(helper_elapsed * 100, @max(reference_elapsed, 1)));
}

fn runPerfCase(case: fixtures.PerfCase) !PerfResult {
    const seed: u32 = 0x13579bdf;
    const helper_partial = checksum.partial(case.payload, seed);
    const reference_partial = referencePartial(case.payload, seed);
    const helper_compute = checksum.compute(case.payload);
    const reference_compute = referenceCompute(case.payload);
    try std.testing.expectEqual(reference_partial, helper_partial);
    try std.testing.expectEqual(reference_compute, helper_compute);

    _ = benchHelper(case.payload, seed, @max(case.iterations / 10, 1));
    _ = benchReference(case.payload, seed, @max(case.iterations / 10, 1));

    var helper_best: u64 = std.math.maxInt(u64);
    var reference_best: u64 = std.math.maxInt(u64);
    var slowdown_samples: [3]u64 = undefined;

    for (0..slowdown_samples.len) |sample_index| {
        const helper_sample = benchHelper(case.payload, seed, case.iterations);
        const reference_sample = benchReference(case.payload, seed, case.iterations);
        try std.testing.expectEqual(helper_sample.sink, reference_sample.sink);
        helper_best = @min(helper_best, helper_sample.elapsed);
        reference_best = @min(reference_best, reference_sample.elapsed);
        slowdown_samples[sample_index] = slowdownPct(helper_sample.elapsed, reference_sample.elapsed);
    }

    const slowdown_pct = median3(slowdown_samples[0], slowdown_samples[1], slowdown_samples[2]);
    try std.testing.expect(slowdown_pct <= case.max_slowdown_pct);

    return .{
        .helper_ns_per_call = nsPerCall(helper_best, case.iterations),
        .reference_ns_per_call = nsPerCall(reference_best, case.iterations),
        .slowdown_pct = slowdown_pct,
        .helper_compute = helper_compute,
        .helper_partial = helper_partial,
    };
}

test "phase6 checksum perf cases keep the documented labels and thresholds" {
    try std.testing.expectEqual(@as(usize, 2), fixtures.perf_cases.len);
    try std.testing.expectEqualStrings("64B", fixtures.perf_cases[0].label);
    try std.testing.expectEqual(@as(usize, 200000), fixtures.perf_cases[0].iterations);
    try std.testing.expectEqual(@as(u64, 150), fixtures.perf_cases[0].max_slowdown_pct);
    try std.testing.expectEqualStrings("1501B", fixtures.perf_cases[1].label);
    try std.testing.expectEqual(@as(usize, 12000), fixtures.perf_cases[1].iterations);
    try std.testing.expectEqual(@as(u64, 150), fixtures.perf_cases[1].max_slowdown_pct);
}

test "phase6 checksum perf cases keep helper and reference outputs aligned before timing" {
    for (fixtures.perf_cases) |case| {
        const seed: u32 = 0x13579bdf;
        try std.testing.expectEqual(referencePartial(case.payload, seed), checksum.partial(case.payload, seed));
        try std.testing.expectEqual(referenceCompute(case.payload), checksum.compute(case.payload));
    }
}
