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

const typed_variant_labels = [_][]const u8{
    "typed-native-ascending",
    "typed-native-descending",
    "typed-c-ascending",
    "typed-c-descending",
};

const raw_variant_labels = [_][]const u8{
    "raw-native-ascending",
    "raw-native-descending",
    "raw-c-ascending",
    "raw-c-descending",
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

fn typedVariants(values: []const u32, descending_values: []const u32) [typed_variant_labels.len]TypedVariant {
    return .{
        .{ .label = typed_variant_labels[0], .values = values, .compare_native = compareNativeCounted },
        .{ .label = typed_variant_labels[1], .values = descending_values, .compare_native = compareNativeDescendingCounted },
        .{ .label = typed_variant_labels[2], .values = values, .compare_c = compareCounted },
        .{ .label = typed_variant_labels[3], .values = descending_values, .compare_c = compareDescendingCounted },
    };
}

fn rawVariants(values: []const u32, descending_values: []const u32) [raw_variant_labels.len]RawVariant {
    return .{
        .{ .label = raw_variant_labels[0], .values = values, .compare_native = compareOpaqueNativeCounted },
        .{ .label = raw_variant_labels[1], .values = descending_values, .compare_native = compareOpaqueNativeDescendingCounted },
        .{ .label = raw_variant_labels[2], .values = values, .compare_c = compareOpaqueCounted },
        .{ .label = raw_variant_labels[3], .values = descending_values, .compare_c = compareOpaqueDescendingCounted },
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
    fixtures.seedPerfQueries(case.len, values, &queries, &expected_hits);

    const typed_variants = typedVariants(values, descending_values);
    const raw_variants = rawVariants(values, descending_values);

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

test "phase 6 bsearch perf harness keeps the widened comparator-shape matrix" {
    const ascending = [_]u32{ 0, 2, 4, 6 };
    const descending = [_]u32{ 6, 4, 2, 0 };
    const typed_variants = typedVariants(ascending[0..], descending[0..]);
    const raw_variants = rawVariants(ascending[0..], descending[0..]);

    try std.testing.expectEqual(@as(usize, 4), typed_variants.len);
    try std.testing.expectEqual(@as(usize, 4), raw_variants.len);
    try std.testing.expectEqual(@as(usize, 16), 2 * (typed_variants.len + raw_variants.len));

    for (typed_variants, typed_variant_labels, 0..) |variant, label, idx| {
        try std.testing.expectEqualStrings(label, variant.label);
        const expects_descending = idx == 1 or idx == 3;
        const expected_values = if (expects_descending) descending[0..] else ascending[0..];
        try std.testing.expectEqual(@intFromPtr(expected_values.ptr), @intFromPtr(variant.values.ptr));
        if (idx < 2) {
            try std.testing.expect(variant.compare_native != null);
            try std.testing.expect(variant.compare_c == null);
        } else {
            try std.testing.expect(variant.compare_native == null);
            try std.testing.expect(variant.compare_c != null);
        }
    }

    for (raw_variants, raw_variant_labels, 0..) |variant, label, idx| {
        try std.testing.expectEqualStrings(label, variant.label);
        const expects_descending = idx == 1 or idx == 3;
        const expected_values = if (expects_descending) descending[0..] else ascending[0..];
        try std.testing.expectEqual(@intFromPtr(expected_values.ptr), @intFromPtr(variant.values.ptr));
        if (idx < 2) {
            try std.testing.expect(variant.compare_native != null);
            try std.testing.expect(variant.compare_c == null);
        } else {
            try std.testing.expect(variant.compare_native == null);
            try std.testing.expect(variant.compare_c != null);
        }
    }
}
