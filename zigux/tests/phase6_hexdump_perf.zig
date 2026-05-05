const std = @import("std");
const hexdump = @import("hexdump");
const fixtures = @import("phase6_hexdump_vectors");

const Io = std.Io;

const BenchResult = struct {
    elapsed_ns: u64,
    accumulator: u64,
};

fn monotonicNs() !u64 {
    var timespec: std.posix.timespec = undefined;
    switch (std.posix.errno(std.posix.system.clock_gettime(std.posix.CLOCK.MONOTONIC, &timespec))) {
        .SUCCESS => {},
        else => return error.ClockUnavailable,
    }
    return (@as(u64, @intCast(timespec.sec)) * std.time.ns_per_s) + @as(u64, @intCast(timespec.nsec));
}

fn helperAccumulator(required: usize, line: []const u8) u64 {
    if (required == 0) return 0;
    return @as(u64, required) +
        @as(u64, line[0]) +
        @as(u64, line[required - 1]) +
        @as(u64, line[@min(required / 2, required - 1)]);
}

fn runHelperBench(case: fixtures.PerfCase) !BenchResult {
    var line: [fixtures.test_hexdump_buf_size]u8 = undefined;
    var accumulator: u64 = 0;
    const start_ns = try monotonicNs();
    var iter: usize = 0;
    while (iter < case.reps) : (iter += 1) {
        const required = hexdump.hexDumpToBuffer(
            fixtures.data_b[0..case.len],
            case.rowsize,
            case.groupsize,
            line[0..],
            case.ascii,
        );
        accumulator +%= helperAccumulator(required, std.mem.sliceTo(line[0..], 0));
    }
    return .{
        .elapsed_ns = (try monotonicNs()) - start_ns,
        .accumulator = accumulator,
    };
}

fn runReferenceBench(case: fixtures.PerfCase) !BenchResult {
    var line: [fixtures.test_hexdump_buf_size]u8 = undefined;
    var accumulator: u64 = 0;
    const start_ns = try monotonicNs();
    var iter: usize = 0;
    while (iter < case.reps) : (iter += 1) {
        const expected = fixtures.prepareExpectedLine(
            line[0..],
            case.len,
            case.rowsize,
            case.groupsize,
            case.ascii,
        );
        accumulator +%= helperAccumulator(expected.len, expected);
    }
    return .{
        .elapsed_ns = (try monotonicNs()) - start_ns,
        .accumulator = accumulator,
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

    try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_CASE_COUNT={d}\n", .{fixtures.perf_cases.len});

    for (fixtures.perf_cases) |case| {
        var helper_line: [fixtures.test_hexdump_buf_size]u8 = undefined;
        var expected_line: [fixtures.test_hexdump_buf_size]u8 = undefined;

        const required = hexdump.hexDumpToBuffer(
            fixtures.data_b[0..case.len],
            case.rowsize,
            case.groupsize,
            helper_line[0..],
            case.ascii,
        );
        const expected = fixtures.prepareExpectedLine(
            expected_line[0..],
            case.len,
            case.rowsize,
            case.groupsize,
            case.ascii,
        );

        try std.testing.expectEqual(fixtures.expectedLength(case.len, case.rowsize, case.groupsize, case.ascii), required);
        try std.testing.expectEqualSlices(u8, expected, std.mem.sliceTo(helper_line[0..], 0));

        const helper_result = try runHelperBench(case);
        const reference_result = try runReferenceBench(case);
        const slowdown_pct = slowdownPct(helper_result.elapsed_ns, reference_result.elapsed_ns);

        try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}_ITERATIONS={d}\n", .{ case.label, case.reps });
        try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}_HELPER_NS={d}\n", .{ case.label, helper_result.elapsed_ns });
        try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}_REFERENCE_NS={d}\n", .{ case.label, reference_result.elapsed_ns });
        try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}_SLOWDOWN_PCT={d}\n", .{ case.label, slowdown_pct });
        try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}_THRESHOLD_PCT={d}\n", .{ case.label, case.max_slowdown_pct });
        try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}_ACCUMULATOR={d}\n", .{ case.label, helper_result.accumulator });

        if (helper_result.accumulator != reference_result.accumulator) {
            return error.HexdumpPerfAccumulatorMismatch;
        }
        if (slowdown_pct > case.max_slowdown_pct) {
            failed = true;
            try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}=fail\n", .{case.label});
        } else {
            try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}=pass\n", .{case.label});
        }
    }

    try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF={s}\n", .{if (failed) "fail" else "pass"});
    try stdout_writer.interface.flush();

    if (failed) return error.HexdumpPerfRegression;
}
