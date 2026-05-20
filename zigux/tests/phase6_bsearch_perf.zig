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

const VariantStats = struct {
    total_compare_calls: usize = 0,
    max_compare_calls: usize = 0,
    case_count: usize = 0,

    fn record(self: *VariantStats, calls: usize) void {
        self.total_compare_calls += calls;
        self.max_compare_calls = @max(self.max_compare_calls, calls);
        self.case_count += 1;
    }
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

fn compareCountedOpaque(key: *const anyopaque, item: *const anyopaque) i32 {
    compare_calls += 1;
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return switch (std.math.order(typed_key.*, typed_item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn benchTime(io: std.Io) i96 {
    return std.Io.Clock.awake.now(io).nanoseconds;
}

fn runTypedVariants(values: []const u32, query: u32, expected_hit: bool, stats: *VariantStats) !void {
    compare_calls = 0;
    const found_index = bsearch.searchIndex(u32, u32, &query, values, compareCounted);
    stats.record(compare_calls);

    compare_calls = 0;
    const found_value = bsearch.search(u32, u32, &query, values, compareCounted);
    stats.record(compare_calls);

    if (expected_hit) {
        const index = found_index orelse return error.ExpectedMatch;
        const typed_found = found_value orelse return error.ExpectedMatch;
        try std.testing.expectEqual(query, values[index]);
        try std.testing.expectEqual(query, typed_found.*);
        try std.testing.expectEqual(@intFromPtr(&values[index]), @intFromPtr(typed_found));
    } else {
        try std.testing.expectEqual(@as(?usize, null), found_index);
        try std.testing.expectEqual(@as(?*const u32, null), found_value);
    }
}

fn runRawVariants(values: []const u32, query: u32, expected_hit: bool, stats: *VariantStats) !void {
    const base: [*]const u8 = @ptrCast(values.ptr);

    compare_calls = 0;
    const found_index = bsearch.bsearchIndex(&query, base, values.len, @sizeOf(u32), compareCountedOpaque);
    stats.record(compare_calls);

    compare_calls = 0;
    const found_value = bsearch.bsearch(&query, base, values.len, @sizeOf(u32), compareCountedOpaque);
    stats.record(compare_calls);

    if (expected_hit) {
        const index = found_index orelse return error.ExpectedMatch;
        const raw_found = found_value orelse return error.ExpectedMatch;
        const typed_found: *const u32 = @ptrCast(@alignCast(raw_found));
        try std.testing.expectEqual(query, values[index]);
        try std.testing.expectEqual(query, typed_found.*);
        try std.testing.expectEqual(@intFromPtr(&values[index]), @intFromPtr(typed_found));
    } else {
        try std.testing.expectEqual(@as(?usize, null), found_index);
        try std.testing.expectEqual(@as(?*const anyopaque, null), found_value);
    }
}

fn runWitnessCases(values: []const u32, queries: []const u32, expected_hits: []const bool) !WitnessResult {
    var stats = VariantStats{};

    for (queries, expected_hits) |query, expected_hit| {
        try runTypedVariants(values, query, expected_hit, &stats);
        try runRawVariants(values, query, expected_hit, &stats);
    }

    return .{
        .max_compare_calls = stats.max_compare_calls,
        .case_count = stats.case_count,
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

    const witness_result = try runWitnessCases(values, &queries, &expected_hits);
    try std.testing.expect(witness_result.max_compare_calls <= max_compare_budget);

    var perf_stats = VariantStats{};
    const started_at = benchTime(io);

    for (0..case.reps) |_| {
        for (queries, expected_hits) |query, expected_hit| {
            try runTypedVariants(values, query, expected_hit, &perf_stats);
            try runRawVariants(values, query, expected_hit, &perf_stats);
        }
    }

    const elapsed = benchTime(io) - started_at;
    const avg_compare_calls = @as(f64, @floatFromInt(perf_stats.total_compare_calls)) /
        @as(f64, @floatFromInt(perf_stats.case_count));

    try std.testing.expect(avg_compare_calls <= @as(f64, @floatFromInt(max_compare_budget)));
    try std.testing.expect(perf_stats.max_compare_calls <= max_compare_budget);

    return .{
        .ns_per_lookup = @max(@as(u64, @intCast(@divFloor(elapsed, @as(i96, @intCast(perf_stats.case_count))))), 1),
        .avg_compare_calls = avg_compare_calls,
        .max_compare_calls = perf_stats.max_compare_calls,
        .max_compare_budget = max_compare_budget,
        .witness_max_compare_calls = witness_result.max_compare_calls,
        .witness_case_count = witness_result.case_count,
    };
}
