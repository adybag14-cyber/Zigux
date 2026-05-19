const std = @import("std");
const bsearch = @import("bsearch");
const fixtures = @import("fixtures/phase6_bsearch_vectors.zig");

const WitnessResult = struct {
    max_compare_calls: usize,
    case_count: usize,
};

const PerfResult = struct {
    ns_per_lookup: u64,
    avg_compare_calls: f64,
    max_compare_calls: usize,
    max_compare_budget: usize,
    witness_max_compare_calls: usize,
    witness_case_count: usize,
};

var compare_calls: usize = 0;

pub fn main(init: std.process.Init) !void {
    const io = init.io;

    for (fixtures.perf_cases) |case| {
        const result = try runPerfCase(case, io);
        std.debug.print(
            "phase6-bsearch-perf {s} len={} reps={} ns_per_lookup={} avg_compare_calls={d:.2} max_compare_calls={} max_compare_budget={} witness_max_compare_calls={} witness_case_count={}\n",
            .{
                case.label,
                case.len,
                case.reps,
                result.ns_per_lookup,
                result.avg_compare_calls,
                result.max_compare_calls,
                result.max_compare_budget,
                result.witness_max_compare_calls,
                result.witness_case_count,
            },
        );
    }
}

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

fn runWitnessCases(values: []const u32, queries: []const u32, expected_hits: []const bool) !WitnessResult {
    var witness_max_compare_calls: usize = 0;

    for (queries, expected_hits) |query, expected_hit| {
        compare_calls = 0;
        const found = bsearch.searchIndex(u32, u32, &query, values, compareCounted);
        witness_max_compare_calls = @max(witness_max_compare_calls, compare_calls);

        if (expected_hit) {
            const index = found orelse return error.ExpectedMatch;
            try std.testing.expectEqual(query, values[index]);
        } else {
            try std.testing.expect(found == null);
        }
    }

    return .{
        .max_compare_calls = witness_max_compare_calls,
        .case_count = queries.len,
    };
}

fn runPerfCase(case: fixtures.PerfCase, io: std.Io) !PerfResult {
    const allocator = std.heap.page_allocator;
    const values = try allocator.alloc(u32, case.len);
    defer allocator.free(values);

    for (values, 0..) |*value, idx| {
        value.* = @as(u32, @intCast(idx * 2));
    }

    const max_compare_budget = std.math.log2_int_ceil(usize, case.len) + 1;

    var queries: [fixtures.query_count]u32 = undefined;
    var expected_hits: [fixtures.query_count]bool = undefined;
    fixtures.seedDeterministicQueries(case.len, values, &queries, &expected_hits);

    const witness_result = try runWitnessCases(&values[0..case.len], &queries, &expected_hits);
    try std.testing.expect(witness_result.max_compare_calls <= max_compare_budget);

    var total_compare_calls: usize = 0;
    var worst_compare_calls: usize = 0;
    const total_lookups = case.reps * queries.len;
    const started_at = benchTime(io);

    for (0..case.reps) |_| {
        for (queries, expected_hits) |query, expected_hit| {
            compare_calls = 0;
            const found = bsearch.searchIndex(u32, u32, &query, values, compareCounted);
            total_compare_calls += compare_calls;
            worst_compare_calls = @max(worst_compare_calls, compare_calls);

            if (expected_hit) {
                try std.testing.expect(found != null);
            } else {
                try std.testing.expect(found == null);
            }
        }
    }

    const elapsed = benchTime(io) - started_at;
    const avg_compare_calls = @as(f64, @floatFromInt(total_compare_calls)) /
        @as(f64, @floatFromInt(total_lookups));

    try std.testing.expect(avg_compare_calls <= @as(f64, @floatFromInt(max_compare_budget)));
    try std.testing.expect(worst_compare_calls <= max_compare_budget);

    return .{
        .ns_per_lookup = @max(@as(u64, @intCast(@divFloor(elapsed, @as(i96, @intCast(total_lookups))))), 1),
        .avg_compare_calls = avg_compare_calls,
        .max_compare_calls = worst_compare_calls,
        .max_compare_budget = max_compare_budget,
        .witness_max_compare_calls = witness_result.max_compare_calls,
        .witness_case_count = witness_result.case_count,
    };
}
