const std = @import("std");
const checksum = @import("checksum");
const fixtures = @import("fixtures/phase6_checksum_vectors.zig");

const bench_sample_count: usize = 3;

const BenchResult = struct {
    elapsed_ns: u64,
    checksum_accumulator: u64,
};

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
        len: usize,
        iterations: usize,
        max_slowdown_pct: u64,
        fingerprint: u64,
    }{
        .{ .label = "64B", .len = 64, .iterations = 200_000, .max_slowdown_pct = 150, .fingerprint = 0x3193_4305_ba03_9b45 },
        .{ .label = "1501B", .len = 1501, .iterations = 12_000, .max_slowdown_pct = 150, .fingerprint = 0x457f_efb1_ea64_3164 },
    };

    var saw_64b = false;
    var saw_1501b = false;

    if (fixtures.perf_cases.len != expected.len) return error.ChecksumPerfMatrixMismatch;

    for (expected, 0..) |want, idx| {
        const actual = fixtures.perf_cases[idx];
        if (!std.mem.eql(u8, want.label, actual.label)) return error.ChecksumPerfMatrixMismatch;
        if (want.len != actual.bytes.len) return error.ChecksumPerfMatrixMismatch;
        if (want.iterations != actual.iterations) return error.ChecksumPerfMatrixMismatch;
        if (want.max_slowdown_pct != actual.max_slowdown_pct) return error.ChecksumPerfMatrixMismatch;
        if (want.fingerprint != perfPayloadFingerprint(actual.bytes)) return error.ChecksumPerfMatrixMismatch;
    }

    for (fixtures.perf_cases, 0..) |case, idx| {
        if (case.bytes.len == 0 or case.iterations == 0 or case.max_slowdown_pct == 0) {
            return error.ChecksumPerfMatrixMismatch;
        }

        if (std.mem.eql(u8, case.label, "64B")) {
            if (case.bytes.len != 64 or case.iterations != 200_000 or case.max_slowdown_pct != 150 or saw_64b) {
                return error.ChecksumPerfMatrixMismatch;
            }
            saw_64b = true;
        } else if (std.mem.eql(u8, case.label, "1501B")) {
            if (case.bytes.len != 1501 or case.iterations != 12_000 or case.max_slowdown_pct != 150 or saw_1501b) {
                return error.ChecksumPerfMatrixMismatch;
            }
            saw_1501b = true;
        } else {
            return error.ChecksumPerfMatrixMismatch;
        }

        for (fixtures.perf_cases[idx + 1 ..]) |other| {
            if (std.mem.eql(u8, case.label, other.label)) return error.ChecksumPerfMatrixMismatch;
        }
    }

    if (!saw_64b or !saw_1501b) return error.ChecksumPerfMatrixMismatch;
}

test "phase 6 checksum perf matrix preflight stays aligned with the documented packet" {
    try validatePerfMatrix();
}

fn referenceInternetChecksum(bytes: []const u8) u16 {
    var acc: u64 = 0;
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
    return ~@as(u16, @truncate(acc));
}

fn monotonicNs() !u64 {
    var timespec: std.posix.timespec = undefined;
    switch (std.posix.errno(std.posix.system.clock_gettime(std.posix.CLOCK.MONOTONIC, &timespec))) {
        .SUCCESS => {},
        else => return error.ClockUnavailable,
    }
    return (@as(u64, @intCast(timespec.sec)) * std.time.ns_per_s) + @as(u64, @intCast(timespec.nsec));
}

fn runHelperBench(bytes: []const u8, iterations: usize) !BenchResult {
    var checksum_accumulator: u64 = 0;
    const start_ns = try monotonicNs();
    var idx: usize = 0;
    while (idx < iterations) : (idx += 1) {
        checksum_accumulator +%= checksum.compute(bytes);
    }
    return .{
        .elapsed_ns = (try monotonicNs()) - start_ns,
        .checksum_accumulator = checksum_accumulator,
    };
}

fn runReferenceBench(bytes: []const u8, iterations: usize) !BenchResult {
    var checksum_accumulator: u64 = 0;
    const start_ns = try monotonicNs();
    var idx: usize = 0;
    while (idx < iterations) : (idx += 1) {
        checksum_accumulator +%= referenceInternetChecksum(bytes);
    }
    return .{
        .elapsed_ns = (try monotonicNs()) - start_ns,
        .checksum_accumulator = checksum_accumulator,
    };
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

pub fn main() !void {
    try validatePerfMatrix();
    var failed = false;

    std.debug.print("PHASE6_CHECKSUM_PERF_CASE_COUNT={d}\n", .{fixtures.perf_cases.len});

    for (fixtures.perf_cases) |case| {
        const helper_expected = checksum.compute(case.bytes);
        const reference_expected = referenceInternetChecksum(case.bytes);
        if (helper_expected != reference_expected) {
            return error.ChecksumPerfBaselineMismatch;
        }

        var helper_elapsed_samples: [bench_sample_count]u64 = undefined;
        var reference_elapsed_samples: [bench_sample_count]u64 = undefined;
        var helper_checksum_accumulator: u64 = 0;

        for (0..bench_sample_count) |sample_index| {
            const helper_result = try runHelperBench(case.bytes, case.iterations);
            const reference_result = try runReferenceBench(case.bytes, case.iterations);

            helper_elapsed_samples[sample_index] = helper_result.elapsed_ns;
            reference_elapsed_samples[sample_index] = reference_result.elapsed_ns;

            if (helper_result.checksum_accumulator != reference_result.checksum_accumulator) {
                return error.ChecksumPerfChecksumMismatch;
            }

            helper_checksum_accumulator = helper_result.checksum_accumulator;
        }

        const helper_median_ns = medianNs(helper_elapsed_samples[0..]);
        const reference_median_ns = medianNs(reference_elapsed_samples[0..]);
        const slowdown_pct = slowdownPct(helper_median_ns, reference_median_ns);

        std.debug.print("PHASE6_CHECKSUM_PERF_{s}_ITERATIONS={d}\n", .{ case.label, case.iterations });
        std.debug.print("PHASE6_CHECKSUM_PERF_{s}_HELPER_NS={d}\n", .{ case.label, helper_median_ns });
        std.debug.print("PHASE6_CHECKSUM_PERF_{s}_REFERENCE_NS={d}\n", .{ case.label, reference_median_ns });
        std.debug.print("PHASE6_CHECKSUM_PERF_{s}_SLOWDOWN_PCT={d}\n", .{ case.label, slowdown_pct });
        std.debug.print("PHASE6_CHECKSUM_PERF_{s}_THRESHOLD_PCT={d}\n", .{ case.label, case.max_slowdown_pct });
        std.debug.print("PHASE6_CHECKSUM_PERF_{s}_CHECKSUM={d}\n", .{ case.label, helper_checksum_accumulator });

        if (slowdown_pct > case.max_slowdown_pct) {
            failed = true;
            std.debug.print("PHASE6_CHECKSUM_PERF_{s}=fail\n", .{case.label});
        } else {
            std.debug.print("PHASE6_CHECKSUM_PERF_{s}=pass\n", .{case.label});
        }
    }

    std.debug.print("PHASE6_CHECKSUM_PERF={s}\n", .{if (failed) "fail" else "pass"});

    if (failed) return error.ChecksumPerfRegression;
}