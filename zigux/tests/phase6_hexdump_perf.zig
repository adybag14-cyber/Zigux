const std = @import("std");
const hexdump = @import("hexdump");
const fixtures = @import("phase6_hexdump_vectors");

const PerfCase = struct {
    label: []const u8,
    len: usize,
    rowsize: usize,
    groupsize: usize,
    ascii: bool,
    reps: usize,
};

const perf_cases = [_]PerfCase{
    .{ .label = "16B-plain", .len = 16, .rowsize = 16, .groupsize = 1, .ascii = false, .reps = 40_000 },
    .{ .label = "32B-ascii-g2", .len = 32, .rowsize = 32, .groupsize = 2, .ascii = true, .reps = 10_000 },
};

pub fn main(init: std.process.Init) !void {
    const io = init.io;

    for (perf_cases) |case| {
        const result = try runPerfCase(case, io);
        std.debug.print(
            "phase6-hexdump-perf {s} len={} rowsize={} groupsize={} ascii={} reps={} ns_per_call={} ns_per_byte={d:.2} required={} sink=0x{x:0>8}\n",
            .{
                case.label,
                case.len,
                case.rowsize,
                case.groupsize,
                case.ascii,
                case.reps,
                result.ns_per_call,
                result.ns_per_byte,
                result.required,
                result.sink,
            },
        );
    }
}

const PerfResult = struct {
    ns_per_call: u64,
    ns_per_byte: f64,
    required: usize,
    sink: u32,
};

fn benchTime(io: std.Io) i96 {
    return std.Io.Clock.awake.now(io).nanoseconds;
}

fn runPerfCase(case: PerfCase, io: std.Io) !PerfResult {
    var actual: [fixtures.test_hexdump_buf_size]u8 = undefined;
    var expected_buf: [fixtures.test_hexdump_buf_size]u8 = undefined;

    const payload = fixtures.data_b[0..case.len];
    const expected = fixtures.prepareExpectedLine(expected_buf[0..], case.len, case.rowsize, case.groupsize, case.ascii);
    const required = fixtures.expectedLength(case.len, case.rowsize, case.groupsize, case.ascii);

    try std.testing.expectEqual(required, hexdump.hexDumpLineLength(case.len, case.rowsize, case.groupsize, case.ascii));
    try std.testing.expectEqual(required, hexdump.hexDumpToBuffer(payload, case.rowsize, case.groupsize, actual[0..], case.ascii));
    try std.testing.expectEqualSlices(u8, expected, std.mem.sliceTo(actual[0..], 0));

    var sink: u32 = 0;
    const started_at = benchTime(io);

    for (0..case.reps) |_| {
        const written = hexdump.hexDumpToBuffer(payload, case.rowsize, case.groupsize, actual[0..], case.ascii);
        sink +%= @as(u32, @intCast(written));
        sink +%= actual[0];
        sink +%= actual[@max(written, 1) - 1];
    }

    const elapsed = benchTime(io) - started_at;
    try std.testing.expect(elapsed > 0);
    try std.testing.expectEqualSlices(u8, expected, std.mem.sliceTo(actual[0..], 0));

    const ns_per_call = @max(@as(u64, @intCast(@divFloor(elapsed, @as(i96, @intCast(case.reps))))), 1);
    const total_bytes = case.reps * case.len;
    const ns_per_byte = @as(f64, @floatFromInt(@max(@as(i96, elapsed), 1))) /
        @as(f64, @floatFromInt(@max(total_bytes, 1)));

    return .{
        .ns_per_call = ns_per_call,
        .ns_per_byte = ns_per_byte,
        .required = required,
        .sink = sink,
    };
}
