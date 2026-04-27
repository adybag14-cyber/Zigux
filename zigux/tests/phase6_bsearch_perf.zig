const std = @import("std");
const bsearch = @import("bsearch");

const PerfCase = struct {
    label: []const u8,
    len: usize,
    reps: usize,
};

const perf_cases = [_]PerfCase{
    .{ .label = "256", .len = 256, .reps = 2_000 },
    .{ .label = "4096", .len = 4096, .reps = 500 },
};

var compare_calls: usize = 0;

pub fn main(init: std.process.Init) !void {
    const io = init.io;

    for (perf_cases) |case| {
        const result = try runPerfCase(case, io);
        std.debug.print(
            "phase6-bsearch-perf {s} len={} reps={} ns_per_lookup={} avg_compare_calls={d:.2}\n",
            .{ case.label, case.len, case.reps, result.ns_per_lookup, result.avg_compare_calls },
        );
    }
}

const PerfResult = struct {
    ns_per_lookup: u64,
    avg_compare_calls: f64,
};

fn compareCounted(key: *const u32, item: *const u32) i32 {
    compare_calls += 1;
    return switch (std.math.order(key.*, item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn benchTime(io: std.Io) i96 {
    return std.Io.Clock.awake.now(io).nanoseconds;
}

fn runPerfCase(case: PerfCase, io: std.Io) !PerfResult {
    const allocator = std.heap.page_allocator;
    const values = try allocator.alloc(u32, case.len);
    defer allocator.free(values);

    for (values, 0..) |*value, idx| {
        value.* = @as(u32, @intCast(idx * 2));
    }

    const query_count = 32;
    var queries: [query_count]u32 = undefined;
    var expected_hits: [query_count]bool = undefined;
    var prng = std.Random.DefaultPrng.init(0x5a17_2026_0700_0007);
    const random = prng.random();

    for (&queries, &expected_hits, 0..) |*query, *hit, idx| {
        const value_index = random.uintLessThan(usize, case.len);
        const base_value = values[value_index];
        if ((idx & 1) == 0) {
            query.* = base_value;
            hit.* = true;
        } else {
            query.* = base_value + 1;
            hit.* = false;
        }
    }

    var total_compare_calls: usize = 0;
    const total_lookups = case.reps * query_count;
    const started_at = benchTime(io);

    for (0..case.reps) |_| {
        for (queries, expected_hits) |query, expected_hit| {
            compare_calls = 0;
            const found = bsearch.searchIndex(u32, u32, &query, values, compareCounted);
            total_compare_calls += compare_calls;

            if (expected_hit) {
                try std.testing.expect(found != null);
            } else {
                try std.testing.expect(found == null);
            }
        }
    }

    const elapsed = benchTime(io) - started_at;
    const max_compare_budget = std.math.log2_int_ceil(usize, case.len) + 1;
    const avg_compare_calls = @as(f64, @floatFromInt(total_compare_calls)) /
        @as(f64, @floatFromInt(total_lookups));

    try std.testing.expect(avg_compare_calls <= @as(f64, @floatFromInt(max_compare_budget)));

    return .{
        .ns_per_lookup = @max(@as(u64, @intCast(@divFloor(elapsed, @as(i96, @intCast(total_lookups))))), 1),
        .avg_compare_calls = avg_compare_calls,
    };
}
