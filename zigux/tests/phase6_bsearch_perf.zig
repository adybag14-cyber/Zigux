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

const TypedComparator = *const fn (*const u32, *const u32) i32;
const RawComparator = *const fn (*const anyopaque, *const anyopaque) i32;

const ExpectedBounds = struct {
    lower: usize,
    upper: usize,
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

fn compareCountedDescending(key: *const u32, item: *const u32) i32 {
    compare_calls += 1;
    return switch (std.math.order(item.*, key.*)) {
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

fn compareCountedOpaqueDescending(key: *const anyopaque, item: *const anyopaque) i32 {
    compare_calls += 1;
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return switch (std.math.order(typed_item.*, typed_key.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn benchTime(io: std.Io) i96 {
    return std.Io.Clock.awake.now(io).nanoseconds;
}

fn expectedBounds(values: []const u32, query: u32, descending: bool) ExpectedBounds {
    var lower = values.len;
    var upper = values.len;

    if (descending) {
        for (values, 0..) |value, index| {
            if (lower == values.len and value <= query) lower = index;
            if (upper == values.len and value < query) upper = index;
        }
    } else {
        for (values, 0..) |value, index| {
            if (lower == values.len and value >= query) lower = index;
            if (upper == values.len and value > query) upper = index;
        }
    }

    return .{ .lower = lower, .upper = upper };
}

fn runTypedVariants(values: []const u32, query: u32, expected_hit: bool, compare: TypedComparator, stats: *VariantStats) !void {
    compare_calls = 0;
    const found_index = bsearch.searchIndex(u32, u32, &query, values, compare);
    stats.record(compare_calls);

    compare_calls = 0;
    const found_value = bsearch.search(u32, u32, &query, values, compare);
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

fn runTypedBoundVariants(values: []const u32, query: u32, descending: bool, compare: TypedComparator, stats: *VariantStats) !void {
    const expected = expectedBounds(values, query, descending);

    compare_calls = 0;
    const lower_index = bsearch.lowerBoundIndex(u32, u32, &query, values, compare);
    stats.record(compare_calls);
    try std.testing.expectEqual(expected.lower, lower_index);

    compare_calls = 0;
    const lower_value = bsearch.lowerBound(u32, u32, &query, values, compare);
    stats.record(compare_calls);
    if (expected.lower == values.len) {
        try std.testing.expectEqual(@as(?*const u32, null), lower_value);
    } else {
        const typed_lower = lower_value orelse return error.ExpectedMatch;
        try std.testing.expectEqual(values[expected.lower], typed_lower.*);
        try std.testing.expectEqual(@intFromPtr(&values[expected.lower]), @intFromPtr(typed_lower));
    }

    compare_calls = 0;
    const upper_index = bsearch.upperBoundIndex(u32, u32, &query, values, compare);
    stats.record(compare_calls);
    try std.testing.expectEqual(expected.upper, upper_index);

    compare_calls = 0;
    const upper_value = bsearch.upperBound(u32, u32, &query, values, compare);
    stats.record(compare_calls);
    if (expected.upper == values.len) {
        try std.testing.expectEqual(@as(?*const u32, null), upper_value);
    } else {
        const typed_upper = upper_value orelse return error.ExpectedMatch;
        try std.testing.expectEqual(values[expected.upper], typed_upper.*);
        try std.testing.expectEqual(@intFromPtr(&values[expected.upper]), @intFromPtr(typed_upper));
    }
}

fn runRawVariants(values: []const u32, query: u32, expected_hit: bool, compare: RawComparator, stats: *VariantStats) !void {
    const base: [*]const u8 = @ptrCast(values.ptr);

    compare_calls = 0;
    const found_index = bsearch.bsearchIndex(&query, base, values.len, @sizeOf(u32), compare);
    stats.record(compare_calls);

    compare_calls = 0;
    const found_value = bsearch.bsearch(&query, base, values.len, @sizeOf(u32), compare);
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

fn runRawBoundVariants(values: []const u32, query: u32, descending: bool, compare: RawComparator, stats: *VariantStats) !void {
    const expected = expectedBounds(values, query, descending);
    const base: [*]const u8 = @ptrCast(values.ptr);

    compare_calls = 0;
    const lower_index = bsearch.bsearchLowerBoundIndex(&query, base, values.len, @sizeOf(u32), compare);
    stats.record(compare_calls);
    try std.testing.expectEqual(expected.lower, lower_index);

    compare_calls = 0;
    const lower_value = bsearch.bsearchLowerBound(&query, base, values.len, @sizeOf(u32), compare);
    stats.record(compare_calls);
    if (expected.lower == values.len) {
        try std.testing.expectEqual(@as(?*const anyopaque, null), lower_value);
    } else {
        const raw_lower = lower_value orelse return error.ExpectedMatch;
        const typed_lower: *const u32 = @ptrCast(@alignCast(raw_lower));
        try std.testing.expectEqual(values[expected.lower], typed_lower.*);
        try std.testing.expectEqual(@intFromPtr(&values[expected.lower]), @intFromPtr(typed_lower));
    }

    compare_calls = 0;
    const upper_index = bsearch.bsearchUpperBoundIndex(&query, base, values.len, @sizeOf(u32), compare);
    stats.record(compare_calls);
    try std.testing.expectEqual(expected.upper, upper_index);

    compare_calls = 0;
    const upper_value = bsearch.bsearchUpperBound(&query, base, values.len, @sizeOf(u32), compare);
    stats.record(compare_calls);
    if (expected.upper == values.len) {
        try std.testing.expectEqual(@as(?*const anyopaque, null), upper_value);
    } else {
        const raw_upper = upper_value orelse return error.ExpectedMatch;
        const typed_upper: *const u32 = @ptrCast(@alignCast(raw_upper));
        try std.testing.expectEqual(values[expected.upper], typed_upper.*);
        try std.testing.expectEqual(@intFromPtr(&values[expected.upper]), @intFromPtr(typed_upper));
    }
}

fn runWitnessCases(
    values: []const u32,
    queries: []const u32,
    expected_hits: []const bool,
    descending: bool,
    typed_compare: TypedComparator,
    raw_compare: RawComparator,
) !WitnessResult {
    var stats = VariantStats{};

    for (queries, expected_hits) |query, expected_hit| {
        try runTypedVariants(values, query, expected_hit, typed_compare, &stats);
        try runTypedBoundVariants(values, query, descending, typed_compare, &stats);
        try runRawVariants(values, query, expected_hit, raw_compare, &stats);
        try runRawBoundVariants(values, query, descending, raw_compare, &stats);
    }

    return .{
        .max_compare_calls = stats.max_compare_calls,
        .case_count = stats.case_count,
    };
}

fn populateDescending(descending: []u32, ascending: []const u32) void {
    std.debug.assert(descending.len == ascending.len);
    for (descending, 0..) |*slot, index| {
        slot.* = ascending[ascending.len - 1 - index];
    }
}

fn runPerfCase(case: fixtures.PerfCase, io: std.Io) !PerfResult {
    const allocator = std.heap.page_allocator;
    const ascending_values = try allocator.alloc(u32, case.len);
    defer allocator.free(ascending_values);
    const descending_values = try allocator.alloc(u32, case.len);
    defer allocator.free(descending_values);

    for (ascending_values, 0..) |*value, idx| {
        value.* = @as(u32, @intCast(idx * 2));
    }
    populateDescending(descending_values, ascending_values);

    const max_compare_budget = std.math.log2_int_ceil(usize, case.len) + 1;

    var ascending_queries: [fixtures.query_count]u32 = undefined;
    var ascending_expected_hits: [fixtures.query_count]bool = undefined;
    fixtures.seedDeterministicQueries(case.len, ascending_values, &ascending_queries, &ascending_expected_hits);

    var descending_queries: [fixtures.query_count]u32 = undefined;
    var descending_expected_hits: [fixtures.query_count]bool = undefined;
    fixtures.seedDeterministicQueries(case.len, descending_values, &descending_queries, &descending_expected_hits);

    const ascending_witness = try runWitnessCases(
        ascending_values,
        &ascending_queries,
        &ascending_expected_hits,
        false,
        compareCounted,
        compareCountedOpaque,
    );
    try std.testing.expect(ascending_witness.max_compare_calls <= max_compare_budget);

    const descending_witness = try runWitnessCases(
        descending_values,
        &descending_queries,
        &descending_expected_hits,
        true,
        compareCountedDescending,
        compareCountedOpaqueDescending,
    );
    try std.testing.expect(descending_witness.max_compare_calls <= max_compare_budget);

    var perf_stats = VariantStats{};
    const started_at = benchTime(io);

    for (0..case.reps) |_| {
        for (ascending_queries, ascending_expected_hits) |query, expected_hit| {
            try runTypedVariants(ascending_values, query, expected_hit, compareCounted, &perf_stats);
            try runTypedBoundVariants(ascending_values, query, false, compareCounted, &perf_stats);
            try runRawVariants(ascending_values, query, expected_hit, compareCountedOpaque, &perf_stats);
            try runRawBoundVariants(ascending_values, query, false, compareCountedOpaque, &perf_stats);
        }
        for (descending_queries, descending_expected_hits) |query, expected_hit| {
            try runTypedVariants(descending_values, query, expected_hit, compareCountedDescending, &perf_stats);
            try runTypedBoundVariants(descending_values, query, true, compareCountedDescending, &perf_stats);
            try runRawVariants(descending_values, query, expected_hit, compareCountedOpaqueDescending, &perf_stats);
            try runRawBoundVariants(descending_values, query, true, compareCountedOpaqueDescending, &perf_stats);
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
        .witness_max_compare_calls = @max(ascending_witness.max_compare_calls, descending_witness.max_compare_calls),
        .witness_case_count = ascending_witness.case_count + descending_witness.case_count,
    };
}
