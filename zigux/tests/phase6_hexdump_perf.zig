const std = @import("std");
const hexdump = @import("hexdump");
const fixtures = @import("phase6_hexdump_vectors");

pub fn main(init: std.process.Init) !void {
    const io = init.io;

    for (fixtures.perf_cases) |case| {
        const result = try runPerfCase(case, io);
        std.debug.print(
            "phase6-hexdump-perf {s} len={} rowsize={} groupsize={} ascii={} reps={} helper_ns_per_call={} helper_ns_per_byte={d:.2} reference_ns_per_call={} reference_ns_per_byte={d:.2} slowdown_pct={} required={} sink=0x{x:0>8}\n",
            .{
                case.label,
                case.len,
                case.rowsize,
                case.groupsize,
                case.ascii,
                case.reps,
                result.helper_ns_per_call,
                result.helper_ns_per_byte,
                result.reference_ns_per_call,
                result.reference_ns_per_byte,
                result.slowdown_pct,
                result.required,
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
    required: usize,
    sink: u32,
};

const BenchResult = struct {
    elapsed: i96,
    sink: u32,
};

fn benchTime(io: std.Io) i96 {
    return std.Io.Clock.awake.now(io).nanoseconds;
}

fn benchHelper(
    payload: []const u8,
    reps: usize,
    rowsize: usize,
    groupsize: usize,
    ascii: bool,
    io: std.Io,
) BenchResult {
    var actual: [fixtures.test_hexdump_buf_size]u8 = undefined;
    var sink: u32 = 0;
    const started_at = benchTime(io);

    for (0..reps) |_| {
        const written = hexdump.hexDumpToBuffer(payload, rowsize, groupsize, actual[0..], ascii);
        sink +%= @as(u32, @intCast(written));
        sink +%= actual[0];
        sink +%= actual[@max(written, 1) - 1];
    }

    return .{ .elapsed = benchTime(io) - started_at, .sink = sink };
}

fn benchReference(
    len: usize,
    reps: usize,
    rowsize: usize,
    groupsize: usize,
    ascii: bool,
    io: std.Io,
) BenchResult {
    var expected_buf: [fixtures.test_hexdump_buf_size]u8 = undefined;
    var sink: u32 = 0;
    const started_at = benchTime(io);

    for (0..reps) |_| {
        const expected = fixtures.prepareExpectedLine(expected_buf[0..], len, rowsize, groupsize, ascii);
        sink +%= @as(u32, @intCast(expected.len));
        if (expected.len != 0) {
            sink +%= expected[0];
            sink +%= expected[expected.len - 1];
        }
    }

    return .{ .elapsed = benchTime(io) - started_at, .sink = sink };
}

fn median3(a: u64, b: u64, c: u64) u64 {
    return a + b + c - @min(a, @min(b, c)) - @max(a, @max(b, c));
}

fn runPerfCase(case: fixtures.PerfCase, io: std.Io) !PerfResult {
    var actual: [fixtures.test_hexdump_buf_size]u8 = undefined;
    var expected_buf: [fixtures.test_hexdump_buf_size]u8 = undefined;

    const payload = fixtures.data_b[0..case.len];
    const expected = fixtures.prepareExpectedLine(expected_buf[0..], case.len, case.rowsize, case.groupsize, case.ascii);
    const required = fixtures.expectedLength(case.len, case.rowsize, case.groupsize, case.ascii);

    try std.testing.expectEqual(required, hexdump.hexDumpLineLength(case.len, case.rowsize, case.groupsize, case.ascii));
    try std.testing.expectEqual(required, hexdump.hexDumpToBuffer(payload, case.rowsize, case.groupsize, actual[0..], case.ascii));
    try std.testing.expectEqualSlices(u8, expected, std.mem.sliceTo(actual[0..], 0));

    _ = benchHelper(payload, case.reps, case.rowsize, case.groupsize, case.ascii, io);
    _ = benchReference(case.len, case.reps, case.rowsize, case.groupsize, case.ascii, io);

    var helper_elapsed: i96 = std.math.maxInt(i96);
    var reference_elapsed: i96 = std.math.maxInt(i96);
    var sink: u32 = 0;
    var slowdown_samples: [3]u64 = undefined;

    for (0..slowdown_samples.len) |sample_index| {
        const helper_sample = benchHelper(payload, case.reps, case.rowsize, case.groupsize, case.ascii, io);
        const reference_sample = benchReference(case.len, case.reps, case.rowsize, case.groupsize, case.ascii, io);

        try std.testing.expect(helper_sample.elapsed > 0);
        try std.testing.expect(reference_sample.elapsed > 0);
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

    const slowdown_pct = median3(slowdown_samples[0], slowdown_samples[1], slowdown_samples[2]);
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
        .required = required,
        .sink = sink,
    };
}
