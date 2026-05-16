const std = @import("std");
const checksum = @import("checksum");
const fixtures = @import("fixtures/phase6_checksum_vectors.zig");

const PerfResult = struct {
    helper_partial_ns_per_op: u64,
    helper_compute_ns_per_op: u64,
    reference_partial_ns_per_op: u64,
    reference_compute_ns_per_op: u64,
    partial_slowdown_pct: u64,
    compute_slowdown_pct: u64,
    partial_sum: u32,
    compute_sum: u16,
};

const IpFastPerfResult = struct {
    helper_ipfast_ns_per_op: u64,
    helper_compute_ns_per_op: u64,
    compute_slowdown_pct: u64,
    checksum_sum: u16,
};

const BenchResult = struct {
    elapsed: u64,
    sink: u32,
};

fn monotonicNs() u64 {
    var ts: std.os.linux.timespec = undefined;
    _ = std.os.linux.clock_gettime(.MONOTONIC, &ts);
    return @intCast(@as(i128, ts.sec) * std.time.ns_per_s + ts.nsec);
}

fn referencePartial(bytes: []const u8, seed: u32) u32 {
    var acc: u64 = seed;
    var index: usize = 0;

    while (index + 1 < bytes.len) : (index += 2) {
        const pair: *const [2]u8 = @ptrCast(bytes[index .. index + 2]);
        acc += std.mem.readInt(u16, pair, .big);
    }

    if (index < bytes.len) {
        acc += @as(u16, bytes[index]) << 8;
    }

    while ((acc >> 16) != 0) {
        acc = (acc & 0xffff) + (acc >> 16);
    }

    return @intCast(acc);
}

fn referenceCompute(bytes: []const u8) u16 {
    return ~@as(u16, @truncate(referencePartial(bytes, 0)));
}

fn median3(a: u64, b: u64, c: u64) u64 {
    return a + b + c - @min(a, @min(b, c)) - @max(a, @max(b, c));
}

fn nsPerOp(elapsed_ns: u64, reps: usize) u64 {
    return @max(@as(u64, 1), @divFloor(elapsed_ns, @as(u64, @intCast(reps))));
}

fn slowdownPct(helper_elapsed: u64, reference_elapsed: u64) u64 {
    return @max(@as(u64, 1), @divFloor(helper_elapsed * 100, @max(reference_elapsed, 1)));
}

fn benchHelperPartial(payload: []const u8, seed: u32, reps: usize) BenchResult {
    var sink: u32 = 0;
    const started_at = monotonicNs();
    for (0..reps) |_| {
        const sum = checksum.partial(payload, seed);
        sink +%= sum;
        sink +%= checksum.from32to16(sum);
    }
    return .{ .elapsed = monotonicNs() - started_at, .sink = sink };
}

fn benchReferencePartial(payload: []const u8, seed: u32, reps: usize) BenchResult {
    var sink: u32 = 0;
    const started_at = monotonicNs();
    for (0..reps) |_| {
        const sum = referencePartial(payload, seed);
        sink +%= sum;
        sink +%= @as(u32, @truncate(sum));
    }
    return .{ .elapsed = monotonicNs() - started_at, .sink = sink };
}

fn benchHelperCompute(payload: []const u8, reps: usize) BenchResult {
    var sink: u32 = 0;
    const started_at = monotonicNs();
    for (0..reps) |_| {
        const sum = checksum.compute(payload);
        sink +%= sum;
    }
    return .{ .elapsed = monotonicNs() - started_at, .sink = sink };
}

fn benchHelperIpFast(header: []const u8, reps: usize) BenchResult {
    var sink: u32 = 0;
    const started_at = monotonicNs();
    for (0..reps) |_| {
        const sum = checksum.ipFastCsum(header);
        sink +%= sum;
    }
    return .{ .elapsed = monotonicNs() - started_at, .sink = sink };
}

fn benchReferenceCompute(payload: []const u8, reps: usize) BenchResult {
    var sink: u32 = 0;
    const started_at = monotonicNs();
    for (0..reps) |_| {
        const sum = referenceCompute(payload);
        sink +%= sum;
    }
    return .{ .elapsed = monotonicNs() - started_at, .sink = sink };
}

fn runPerfCase(case: fixtures.PerfCase) !PerfResult {
    var payload: [1501]u8 = undefined;
    fixtures.fillPerfPayload(payload[0..case.len]);
    const bytes = payload[0..case.len];

    const expected_partial = referencePartial(bytes, case.seed);
    const actual_partial = checksum.partial(bytes, case.seed);
    try std.testing.expectEqual(expected_partial, actual_partial);

    const expected_compute = referenceCompute(bytes);
    const actual_compute = checksum.compute(bytes);
    try std.testing.expectEqual(expected_compute, actual_compute);

    const warmup_reps = @max(case.reps / 10, 1);
    _ = benchHelperPartial(bytes, case.seed, warmup_reps);
    _ = benchReferencePartial(bytes, case.seed, warmup_reps);
    _ = benchHelperCompute(bytes, warmup_reps);
    _ = benchReferenceCompute(bytes, warmup_reps);

    var partial_samples: [3]u64 = undefined;
    var compute_samples: [3]u64 = undefined;
    var best_helper_partial: u64 = std.math.maxInt(u64);
    var best_reference_partial: u64 = std.math.maxInt(u64);
    var best_helper_compute: u64 = std.math.maxInt(u64);
    var best_reference_compute: u64 = std.math.maxInt(u64);

    for (0..3) |sample_index| {
        const helper_partial = benchHelperPartial(bytes, case.seed, case.reps);
        const reference_partial = benchReferencePartial(bytes, case.seed, case.reps);
        const helper_compute = benchHelperCompute(bytes, case.reps);
        const reference_compute = benchReferenceCompute(bytes, case.reps);

        try std.testing.expectEqual(reference_partial.sink, helper_partial.sink);
        try std.testing.expectEqual(reference_compute.sink, helper_compute.sink);

        best_helper_partial = @min(best_helper_partial, helper_partial.elapsed);
        best_reference_partial = @min(best_reference_partial, reference_partial.elapsed);
        best_helper_compute = @min(best_helper_compute, helper_compute.elapsed);
        best_reference_compute = @min(best_reference_compute, reference_compute.elapsed);

        partial_samples[sample_index] = slowdownPct(helper_partial.elapsed, reference_partial.elapsed);
        compute_samples[sample_index] = slowdownPct(helper_compute.elapsed, reference_compute.elapsed);
    }

    const partial_slowdown_pct = median3(partial_samples[0], partial_samples[1], partial_samples[2]);
    const compute_slowdown_pct = median3(compute_samples[0], compute_samples[1], compute_samples[2]);

    try std.testing.expect(partial_slowdown_pct <= case.max_slowdown_pct);
    try std.testing.expect(compute_slowdown_pct <= case.max_slowdown_pct);

    return .{
        .helper_partial_ns_per_op = nsPerOp(best_helper_partial, case.reps),
        .helper_compute_ns_per_op = nsPerOp(best_helper_compute, case.reps),
        .reference_partial_ns_per_op = nsPerOp(best_reference_partial, case.reps),
        .reference_compute_ns_per_op = nsPerOp(best_reference_compute, case.reps),
        .partial_slowdown_pct = partial_slowdown_pct,
        .compute_slowdown_pct = compute_slowdown_pct,
        .partial_sum = actual_partial,
        .compute_sum = actual_compute,
    };
}

fn runIpFastPerfCase(case: fixtures.IpFastCsumCase) !IpFastPerfResult {
    const expected = referenceCompute(case.header);
    const actual_compute = checksum.compute(case.header);
    const actual_ipfast = checksum.ipFastCsum(case.header);
    try std.testing.expectEqual(expected, actual_compute);
    try std.testing.expectEqual(expected, actual_ipfast);

    const warmup_reps = @max(case.reps / 10, 1);
    _ = benchHelperCompute(case.header, warmup_reps);
    _ = benchHelperIpFast(case.header, warmup_reps);

    var samples: [3]u64 = undefined;
    var best_helper_compute: u64 = std.math.maxInt(u64);
    var best_helper_ipfast: u64 = std.math.maxInt(u64);

    for (0..3) |sample_index| {
        const helper_compute = benchHelperCompute(case.header, case.reps);
        const helper_ipfast = benchHelperIpFast(case.header, case.reps);

        try std.testing.expectEqual(helper_compute.sink, helper_ipfast.sink);

        best_helper_compute = @min(best_helper_compute, helper_compute.elapsed);
        best_helper_ipfast = @min(best_helper_ipfast, helper_ipfast.elapsed);
        samples[sample_index] = slowdownPct(helper_ipfast.elapsed, helper_compute.elapsed);
    }

    const compute_slowdown_pct = median3(samples[0], samples[1], samples[2]);
    try std.testing.expect(compute_slowdown_pct <= case.max_compute_slowdown_pct);

    return .{
        .helper_ipfast_ns_per_op = nsPerOp(best_helper_ipfast, case.reps),
        .helper_compute_ns_per_op = nsPerOp(best_helper_compute, case.reps),
        .compute_slowdown_pct = compute_slowdown_pct,
        .checksum_sum = actual_ipfast,
    };
}

pub fn main() !void {
    for (fixtures.perf_cases) |case| {
        const result = try runPerfCase(case);
        std.debug.print(
            "phase6-checksum-perf {s} len={} reps={} helper_partial_ns_per_op={} helper_compute_ns_per_op={} reference_partial_ns_per_op={} reference_compute_ns_per_op={} partial_slowdown_pct={} compute_slowdown_pct={} partial_sum=0x{x:0>8} compute_sum=0x{x:0>4}\n",
            .{
                case.label,
                case.len,
                case.reps,
                result.helper_partial_ns_per_op,
                result.helper_compute_ns_per_op,
                result.reference_partial_ns_per_op,
                result.reference_compute_ns_per_op,
                result.partial_slowdown_pct,
                result.compute_slowdown_pct,
                result.partial_sum,
                result.compute_sum,
            },
        );
    }

    for (fixtures.ip_fast_csum_cases) |case| {
        const result = try runIpFastPerfCase(case);
        std.debug.print(
            "phase6-checksum-ipfast-perf {s} len={} reps={} helper_ipfast_ns_per_op={} helper_compute_ns_per_op={} compute_slowdown_pct={} checksum_sum=0x{x:0>4}\n",
            .{
                case.name,
                case.header.len,
                case.reps,
                result.helper_ipfast_ns_per_op,
                result.helper_compute_ns_per_op,
                result.compute_slowdown_pct,
                result.checksum_sum,
            },
        );
    }
}

test "phase 6 checksum perf matrix keeps the shipped slowdown gates aligned" {
    try std.testing.expectEqual(@as(usize, 2), fixtures.perf_cases.len);
}

test "phase 6 checksum perf cases keep helper and reference math aligned before timing" {
    for (fixtures.perf_cases) |case| {
        const result = try runPerfCase(case);
        try std.testing.expect(result.partial_sum != 0);
        try std.testing.expect(result.compute_sum != 0);
    }
}

test "phase 6 checksum ipFastCsum perf gate stays ahead of compute on aligned ipv4 headers" {
    try std.testing.expectEqual(@as(usize, 3), fixtures.ip_fast_csum_cases.len);

    for (fixtures.ip_fast_csum_cases) |case| {
        const result = try runIpFastPerfCase(case);
        try std.testing.expect(result.checksum_sum != 0);
    }
}
