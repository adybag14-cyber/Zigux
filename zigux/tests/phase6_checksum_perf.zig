const std = @import("std");
const checksum = @import("checksum");
const fixtures = @import("fixtures/phase6_checksum_vectors.zig");

const Io = std.Io;

const BenchResult = struct {
    elapsed_ns: u64,
    checksum_accumulator: u64,
};

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

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [4096]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    var failed = false;

    try stdout_writer.interface.print("PHASE6_CHECKSUM_PERF_CASE_COUNT={d}\n", .{fixtures.perf_cases.len});

    for (fixtures.perf_cases) |case| {
        const helper_expected = checksum.compute(case.bytes);
        const reference_expected = referenceInternetChecksum(case.bytes);
        if (helper_expected != reference_expected) {
            return error.ChecksumPerfBaselineMismatch;
        }

        const helper_result = try runHelperBench(case.bytes, case.iterations);
        const reference_result = try runReferenceBench(case.bytes, case.iterations);
        const slowdown_pct = slowdownPct(helper_result.elapsed_ns, reference_result.elapsed_ns);

        try stdout_writer.interface.print("PHASE6_CHECKSUM_PERF_{s}_ITERATIONS={d}\n", .{ case.label, case.iterations });
        try stdout_writer.interface.print("PHASE6_CHECKSUM_PERF_{s}_HELPER_NS={d}\n", .{ case.label, helper_result.elapsed_ns });
        try stdout_writer.interface.print("PHASE6_CHECKSUM_PERF_{s}_REFERENCE_NS={d}\n", .{ case.label, reference_result.elapsed_ns });
        try stdout_writer.interface.print("PHASE6_CHECKSUM_PERF_{s}_SLOWDOWN_PCT={d}\n", .{ case.label, slowdown_pct });
        try stdout_writer.interface.print("PHASE6_CHECKSUM_PERF_{s}_THRESHOLD_PCT={d}\n", .{ case.label, case.max_slowdown_pct });
        try stdout_writer.interface.print("PHASE6_CHECKSUM_PERF_{s}_CHECKSUM={d}\n", .{ case.label, helper_result.checksum_accumulator });

        if (helper_result.checksum_accumulator != reference_result.checksum_accumulator) {
            return error.ChecksumPerfChecksumMismatch;
        }
        if (slowdown_pct > case.max_slowdown_pct) {
            failed = true;
            try stdout_writer.interface.print("PHASE6_CHECKSUM_PERF_{s}=fail\n", .{case.label});
        } else {
            try stdout_writer.interface.print("PHASE6_CHECKSUM_PERF_{s}=pass\n", .{case.label});
        }
    }

    try stdout_writer.interface.print("PHASE6_CHECKSUM_PERF={s}\n", .{if (failed) "fail" else "pass"});
    try stdout_writer.interface.flush();

    if (failed) return error.ChecksumPerfRegression;
}
