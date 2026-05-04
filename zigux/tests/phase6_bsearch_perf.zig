const std = @import("std");
const bsearch = @import("bsearch");
const fixtures = @import("fixtures/phase6_bsearch_vectors.zig");

const TypedVariant = struct {
    label: []const u8,
    values: []const u32,
    compare_native: ?bsearch.Comparator(u32, u32) = null,
    compare_c: ?bsearch.CComparator(u32, u32) = null,
};

const RawVariant = struct {
    label: []const u8,
    values: []const u32,
    compare_native: ?bsearch.RawComparator = null,
    compare_c: ?bsearch.CRawComparator = null,
};

var compare_calls: usize = 0;

pub fn main(init: std.process.Init) !void {
    const io = init.io;

    for (fixtures.perf_cases) |case| {
        const result = try runPerfCase(case, io);
        std.debug.print(
            "phase6-bsearch-perf {s} len={} reps={} ns_per_lookup={} avg_compare_calls={d:.2} max_compare_calls={} max_compare_budget={}\n",
            .{
                case.label,
                case.len,
                case.reps,
                result.ns_per_lookup,
                result.avg_compare_calls,
                result.max_compare_calls,
                result.max_compare_budget,
            },
        );
    }
}

const PerfResult = struct {
    ns_per_lookup: u64,
    avg_compare_calls: f64,
    max_compare_calls: usize,
    max_compare_budget: usize,
};

fn compareNativeCounted(key: *const u32, item: *const u32) i32 {
    compare_calls += 1;
    return switch (std.math.order(key.*, item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareNativeDescendingCounted(key: *const u32, item: *const u32) i32 {
    compare_calls += 1;
    return switch (std.math.order(item.*, key.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareCounted(key: *const u32, item: *const u32) callconv(.c) i32 {
    compare_calls += 1;
    return switch (std.math.order(key.*, item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareDescendingCounted(key: *const u32, item: *const u32) callconv(.c) i32 {
    compare_calls += 1;
    return switch (std.math.order(item.*, key.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareOpaqueNativeCounted(key: *const anyopaque, item: *const anyopaque) i32 {
    compare_calls += 1;
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return switch (std.math.order(typed_key.*, typed_item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareOpaqueNativeDescendingCounted(key: *const anyopaque, item: *const anyopaque) i32 {
    compare_calls += 1;
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return switch (std.math.order(typed_item.*, typed_key.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareOpaqueCounted(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
    compare_calls += 1;
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return switch (std.math.order(typed_key.*, typed_item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareOpaqueDescendingCounted(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
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

fn runPerfCase(case: fixtures.PerfCase, io: std.Io) !PerfResult {
    const allocator = std.heap.page_allocator;
    const values = try allocator.alloc(u32, case.len);
    defer allocator.free(values);
    const descending_values = try allocator.alloc(u32, case.len);
    defer allocator.free(descending_values);

    for (values, 0..) |*value, idx| {
        value.* = @as(u32, @intCast(idx * 2));
    }
    for (descending_values, 0..) |*value, idx| {
        value.* = values[values.len - 1 - idx];
    }

    var queries: [fixtures.query_count]u32 = undefined;
    var expected_hits: [fixtures.query_count]bool = undefined;
    fixtures.seedDeterministicQueries(case.len, values, &queries, &expected_hits);

    var prng = std.Random.DefaultPrng.init(0x5a17_2026_0700_0007);
    const random = prng.random();

    for (queries[8..], expected_hits[8..], 8..) |*query, *hit, idx| {
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

    const typed_variants = [_]TypedVariant{
        .{ .label = "typed-native-ascending", .values = values, .compare_native = compareNativeCounted },
        .{ .label = "typed-native-descending", .values = descending_values, .compare_native = compareNativeDescendingCounted },
        .{ .label = "typed-c-ascending", .values = values, .compare_c = compareCounted },
        .{ .label = "typed-c-descending", .values = descending_values, .compare_c = compareDescendingCounted },
    };
    const raw_variants = [_]RawVariant{
        .{ .label = "raw-native-ascending", .values = values, .compare_native = compareOpaqueNativeCounted },
        .{ .label = "raw-native-descending", .values = descending_values, .compare_native = compareOpaqueNativeDescendingCounted },
        .{ .label = "raw-c-ascending", .values = values, .compare_c = compareOpaqueCounted },
        .{ .label = "raw-c-descending", .values = descending_values, .compare_c = compareOpaqueDescendingCounted },
    };

    var total_compare_calls: usize = 0;
    var max_compare_calls: usize = 0;
    const lookups_per_query = 2 * (typed_variants.len + raw_variants.len);
    const total_lookups = case.reps * fixtures.query_count * lookups_per_query;
    const started_at = benchTime(io);
    const max_compare_budget = std.math.log2_int_ceil(usize, case.len) + 1;

    for (0..case.reps) |_| {
        for (queries, expected_hits) |query, expected_hit| {
            for (typed_variants) |variant| {
                compare_calls = 0;
                const found_index = if (variant.compare_native) |compare|
                    bsearch.searchIndex(u32, u32, &query, variant.values, compare)
                else
                    bsearch.searchIndex(u32, u32, &query, variant.values, variant.compare_c.?);
                total_compare_calls += compare_calls;
                max_compare_calls = @max(max_compare_calls, compare_calls);

                try std.testing.expect(compare_calls <= max_compare_budget);

                compare_calls = 0;
                const found_ptr = if (variant.compare_native) |compare|
                    bsearch.search(u32, u32, &query, variant.values, compare)
                else
                    bsearch.search(u32, u32, &query, variant.values, variant.compare_c.?);
                total_compare_calls += compare_calls;
                max_compare_calls = @max(max_compare_calls, compare_calls);

                try std.testing.expect(compare_calls <= max_compare_budget);
                try expectTypedIndexAndPointerParity(expected_hit, found_index, found_ptr, variant.values, query);
            }

            for (raw_variants) |variant| {
                compare_calls = 0;
                const found_index = if (variant.compare_native) |compare|
                    bsearch.bsearchIndex(&query, @ptrCast(variant.values.ptr), variant.values.len, @sizeOf(u32), compare)
                else
                    bsearch.bsearchIndex(&query, @ptrCast(variant.values.ptr), variant.values.len, @sizeOf(u32), variant.compare_c.?);
                total_compare_calls += compare_calls;
                max_compare_calls = @max(max_compare_calls, compare_calls);

                try std.testing.expect(compare_calls <= max_compare_budget);

                compare_calls = 0;
                const found_ptr = if (variant.compare_native) |compare|
                    bsearch.bsearch(&query, @ptrCast(variant.values.ptr), variant.values.len, @sizeOf(u32), compare)
                else
                    bsearch.bsearch(&query, @ptrCast(variant.values.ptr), variant.values.len, @sizeOf(u32), variant.compare_c.?);
                total_compare_calls += compare_calls;
                max_compare_calls = @max(max_compare_calls, compare_calls);

                try std.testing.expect(compare_calls <= max_compare_budget);
                try expectRawIndexAndPointerParity(expected_hit, found_index, found_ptr, variant.values, query);
            }
        }
    }

    const elapsed = benchTime(io) - started_at;
    const avg_compare_calls = @as(f64, @floatFromInt(total_compare_calls)) /
        @as(f64, @floatFromInt(total_lookups));

    try std.testing.expect(avg_compare_calls <= @as(f64, @floatFromInt(max_compare_budget)));

    return .{
        .ns_per_lookup = @max(@as(u64, @intCast(@divFloor(elapsed, @as(i96, @intCast(total_lookups))))), 1),
        .avg_compare_calls = avg_compare_calls,
        .max_compare_calls = max_compare_calls,
        .max_compare_budget = max_compare_budget,
    };
}

fn expectTypedIndexAndPointerParity(
    expected_hit: bool,
    found_index: ?usize,
    found_ptr: ?*const u32,
    values: []const u32,
    query: u32,
) !void {
    if (expected_hit) {
        const index = found_index orelse return error.TestUnexpectedResult;
        const pointer = found_ptr orelse return error.TestUnexpectedResult;
        try std.testing.expect(index < values.len);
        try std.testing.expectEqual(query, values[index]);
        try std.testing.expectEqual(@intFromPtr(&values[index]), @intFromPtr(pointer));
        try std.testing.expectEqual(query, pointer.*);
    } else {
        try std.testing.expect(found_index == null);
        try std.testing.expect(found_ptr == null);
    }
}

fn expectRawIndexAndPointerParity(
    expected_hit: bool,
    found_index: ?usize,
    found_ptr: ?*const anyopaque,
    values: []const u32,
    query: u32,
) !void {
    if (expected_hit) {
        const index = found_index orelse return error.TestUnexpectedResult;
        const pointer = found_ptr orelse return error.TestUnexpectedResult;
        const typed_pointer: *const u32 = @ptrCast(@alignCast(pointer));
        try std.testing.expect(index < values.len);
        try std.testing.expectEqual(query, values[index]);
        try std.testing.expectEqual(@intFromPtr(&values[index]), @intFromPtr(typed_pointer));
        try std.testing.expectEqual(query, typed_pointer.*);
    } else {
        try std.testing.expect(found_index == null);
        try std.testing.expect(found_ptr == null);
    }
}
