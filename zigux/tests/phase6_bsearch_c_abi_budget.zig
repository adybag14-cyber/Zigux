const std = @import("std");
const bsearch = @import("bsearch");
const fixtures = @import("fixtures/phase6_bsearch_vectors.zig");

const CountedOpaqueKey = struct {
    target: u32,
    comparisons: *usize,
};

fn compareCountedOpaqueInt(key: *const anyopaque, item: *const anyopaque) callconv(.c) c_int {
    const typed_key: *const CountedOpaqueKey = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    typed_key.comparisons.* += 1;
    return switch (std.math.order(typed_key.target, typed_item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareCountedOpaqueDescendingInt(key: *const anyopaque, item: *const anyopaque) callconv(.c) c_int {
    const typed_key: *const CountedOpaqueKey = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    typed_key.comparisons.* += 1;
    return switch (std.math.order(typed_item.*, typed_key.target)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn maxBinarySearchComparisons(len: usize) usize {
    var budget: usize = 0;
    var remaining = len;
    while (remaining > 0) : (remaining >>= 1) {
        budget += 1;
    }
    return budget;
}

fn expectSearchBudget(items: []const u32, target: u32, expect_hit: bool, compare: bsearch.CRawComparator) !usize {
    var comparisons: usize = 0;
    const key = CountedOpaqueKey{ .target = target, .comparisons = &comparisons };
    const found = bsearch.bsearch(&key, @ptrCast(items.ptr), items.len, @sizeOf(u32), compare);
    if (expect_hit) {
        const opaque_found = found orelse return error.ExpectedMatch;
        const typed_found: *const u32 = @ptrCast(@alignCast(opaque_found));
        try std.testing.expectEqual(target, typed_found.*);
    } else {
        try std.testing.expectEqual(@as(?*const anyopaque, null), found);
    }
    return comparisons;
}

fn expectRangeBudget(items: []const u32, target: u32, expected: bsearch.IndexRange, compare: bsearch.CRawComparator) !usize {
    var comparisons: usize = 0;
    const key = CountedOpaqueKey{ .target = target, .comparisons = &comparisons };
    const range = bsearch.bsearchEqualRangeIndex(&key, @ptrCast(items.ptr), items.len, @sizeOf(u32), compare);
    try std.testing.expectEqual(expected, range);
    return comparisons;
}

fn populateAscending(values: *[32]u32) void {
    for (values, 0..) |*slot, index| {
        slot.* = @as(u32, @intCast((index + 1) * 3));
    }
}

fn populateDescending(descending: *[32]u32, ascending: [32]u32) void {
    for (descending, 0..) |*slot, index| {
        slot.* = ascending[ascending.len - 1 - index];
    }
}

fn assertRepresentativeBudget(items: []const u32, compare: bsearch.CRawComparator) !void {
    const budget = maxBinarySearchComparisons(items.len);
    if (items.len == 0) {
        const empty_budget = try expectSearchBudget(items, 1, false, compare);
        try std.testing.expectEqual(@as(usize, 0), empty_budget);
        return;
    }

    var queries: [8]u32 = undefined;
    var expected_hits: [8]bool = undefined;
    fixtures.seedDeterministicQueries(items.len, items, &queries, &expected_hits);

    for (queries, expected_hits) |query, expect_hit| {
        const comparisons = try expectSearchBudget(items, query, expect_hit, compare);
        try std.testing.expect(comparisons <= budget);
    }
}

test "phase 6 bsearch raw c abi budgets stay logarithmic for deterministic ascending and descending slices" {
    var ascending_storage: [32]u32 = undefined;
    populateAscending(&ascending_storage);

    var descending_storage: [32]u32 = undefined;
    populateDescending(&descending_storage, ascending_storage);

    for (fixtures.dynamic_case_lengths) |len| {
        try assertRepresentativeBudget(ascending_storage[0..len], compareCountedOpaqueInt);
        try assertRepresentativeBudget(descending_storage[(descending_storage.len - len)..], compareCountedOpaqueDescendingInt);
    }
}

test "phase 6 bsearch raw c abi equal-range budgets stay logarithmic for duplicate spans in both sort orders" {
    const ascending_duplicates = fixtures.representative_duplicate_values;
    const descending_duplicates = fixtures.representative_descending_duplicate_values;

    const ascending_budget = try expectRangeBudget(ascending_duplicates[0..], 21, .{ .lower = 4, .upper = 7 }, compareCountedOpaqueInt);
    try std.testing.expect(ascending_budget <= (2 * maxBinarySearchComparisons(ascending_duplicates.len)));

    const ascending_miss_budget = try expectRangeBudget(ascending_duplicates[0..], 20, .{ .lower = 4, .upper = 4 }, compareCountedOpaqueInt);
    try std.testing.expect(ascending_miss_budget <= (2 * maxBinarySearchComparisons(ascending_duplicates.len)));

    const descending_budget = try expectRangeBudget(descending_duplicates[0..], 21, .{ .lower = 3, .upper = 6 }, compareCountedOpaqueDescendingInt);
    try std.testing.expect(descending_budget <= (2 * maxBinarySearchComparisons(descending_duplicates.len)));

    const descending_miss_budget = try expectRangeBudget(descending_duplicates[0..], 20, .{ .lower = 6, .upper = 6 }, compareCountedOpaqueDescendingInt);
    try std.testing.expect(descending_miss_budget <= (2 * maxBinarySearchComparisons(descending_duplicates.len)));
}

test "phase 6 bsearch runtime-selected raw c abi comparator pointers keep the budget contract" {
    const cases = [_]struct {
        items: []const u32,
        target: u32,
        expect_hit: bool,
        compare: bsearch.CRawComparator,
    }{
        .{ .items = fixtures.representative_ascending_values[0..], .target = 24, .expect_hit = true, .compare = compareCountedOpaqueInt },
        .{ .items = fixtures.representative_ascending_values[0..], .target = 26, .expect_hit = false, .compare = compareCountedOpaqueInt },
        .{ .items = fixtures.representative_descending_values[0..], .target = 24, .expect_hit = true, .compare = compareCountedOpaqueDescendingInt },
        .{ .items = fixtures.representative_descending_values[0..], .target = 26, .expect_hit = false, .compare = compareCountedOpaqueDescendingInt },
    };

    for (cases) |case| {
        const comparisons = try expectSearchBudget(case.items, case.target, case.expect_hit, case.compare);
        try std.testing.expect(comparisons <= maxBinarySearchComparisons(case.items.len));
    }
}
