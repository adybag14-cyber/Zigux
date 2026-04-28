const std = @import("std");
const checksum = @import("checksum");
const fixtures = @import("fixtures/phase6_checksum_vectors.zig");

pub fn main(init: std.process.Init) !void {
    const io = init.io;

    for (fixtures.perf_cases) |case| {
        const result = try runPerfCase(case, io);
        std.debug.print(
            "phase6-checksum-perf {s} len={} reps={} ns_per_call={} ns_per_byte={d:.2} folded=0x{x:0>4} sink=0x{x:0>8}\n",
            .{
                case.label,
                case.len,
                case.reps,
                result.ns_per_call,
                result.ns_per_byte,
                result.folded,
                result.sink,
            },
        );
    }
}

const PerfResult = struct {
    ns_per_call: u64,
    ns_per_byte: f64,
    folded: u16,
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

fn runPerfCase(case: fixtures.PerfCase, io: std.Io) !PerfResult {
    const allocator = std.heap.page_allocator;
    const payload = try allocator.alloc(u8, case.len);
    defer allocator.free(payload);
    fixtures.fillPerfPayload(payload);

    const expected_partial = referencePartial(payload, case.seed);
    const expected_folded = ~@as(u16, @truncate(expected_partial));

    try std.testing.expectEqual(expected_partial, checksum.partial(payload, case.seed));
    try std.testing.expectEqual(expected_folded, checksum.fold(expected_partial));

    var sink: u32 = 0;
    const started_at = benchTime(io);

    for (0..case.reps) |_| {
        const partial = checksum.partial(payload, case.seed);
        sink +%= partial;
    }

    const elapsed = benchTime(io) - started_at;
    try std.testing.expect(elapsed > 0);
    try std.testing.expect(sink != 0 or expected_partial == 0);

    const ns_per_call = @max(@as(u64, @intCast(@divFloor(elapsed, @as(i96, @intCast(case.reps))))), 1);
    const total_bytes = case.reps * case.len;
    const ns_per_byte = @as(f64, @floatFromInt(@max(@as(i96, elapsed), 1))) /
        @as(f64, @floatFromInt(@max(total_bytes, 1)));

    return .{
        .ns_per_call = ns_per_call,
        .ns_per_byte = ns_per_byte,
        .folded = expected_folded,
        .sink = sink,
    };
}
