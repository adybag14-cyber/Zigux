const std = @import("std");
const bsearch = @import("bsearch");
const fixtures = @import("fixtures/phase6_bsearch_vectors.zig");

const CountedOpaqueKey = struct {
    target: u32,
    comparisons: *usize,
};

const CountedTypedKey = struct {
    target: u32,
    comparisons: *usize,
};

const max_perf_case_len: usize = comptime blk: {
    var max_len: usize = 0;
    for (fixtures.perf_cases) |case| {
        max_len = @max(max_len, case.len);
    }
    break :blk max_len;
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

fn compareCountedTypedInt(key: *const CountedTypedKey, item: *const u32) callconv(.c) c_int {
    key.comparisons.* += 1;
    return switch (std.math.order(key.target, item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareCountedTypedDescendingInt(key: *const CountedTypedKey, item: *const u32) callconv(.c) c_int {
    key.comparisons.* += 1;
    return switch (std.math.order(item.*, key.target)) {
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

fn expectRawLowerBoundBudget(items: []const u32, target: u32, expected: usize, compare: bsearch.CRawComparator) !usize {
    var comparisons: usize = 0;
    const key = CountedOpaqueKey{ .target = target, .comparisons = &comparisons };
    const index = bsearch.bsearchLowerBoundIndex(&key, @ptrCast(items.ptr), items.len, @sizeOf(u32), compare);
    try std.testing.expectEqual(expected, index);
    return comparisons;
}

fn expectRawUpperBoundBudget(items: []const u32, target: u32, expected: usize, compare: bsearch.CRawComparator) !usize {
    var comparisons: usize = 0;
    const key = CountedOpaqueKey{ .target = target, .comparisons = &comparisons };
    const index = bsearch.bsearchUpperBoundIndex(&key, @ptrCast(items.ptr), items.len, @sizeOf(u32), compare);
    try std.testing.expectEqual(expected, index);
    return comparisons;
}

fn expectTypedSearchBudget(
    items: []const u32,
    target: u32,
    expect_hit: bool,
    compare: bsearch.CComparator(CountedTypedKey, u32),
) !usize {
    var comparisons: usize = 0;
    const key = CountedTypedKey{ .target = target, .comparisons = &comparisons };
    const found = bsearch.search(CountedTypedKey, u32, &key, items, compare);
    if (expect_hit) {
        const typed_found = found orelse return error.ExpectedMatch;
        try std.testing.expectEqual(target, typed_found.*);
    } else {
        try std.testing.expectEqual(@as(?*const u32, null), found);
    }
    return comparisons;
}

fn expectTypedRangeBudget(
    items: []const u32,
    target: u32,
    expected: bsearch.IndexRange,
    compare: bsearch.CComparator(CountedTypedKey, u32),
) !usize {
    var comparisons: usize = 0;
    const key = CountedTypedKey{ .target = target, .comparisons = &comparisons };
    const range = bsearch.equalRangeIndex(CountedTypedKey, u32, &key, items, compare);
    try std.testing.expectEqual(expected, range);
    return comparisons;
}

fn expectTypedLowerBoundBudget(
    items: []const u32,
    target: u32,
    expected: usize,
    compare: bsearch.CComparator(CountedTypedKey, u32),
) !usize {
    var comparisons: usize = 0;
    const key = CountedTypedKey{ .target = target, .comparisons = &comparisons };
    const index = bsearch.lowerBoundIndex(CountedTypedKey, u32, &key, items, compare);
    try std.testing.expectEqual(expected, index);
    return comparisons;
}

fn expectTypedUpperBoundBudget(
    items: []const u32,
    target: u32,
    expected: usize,
    compare: bsearch.CComparator(CountedTypedKey, u32),
) !usize {
    var comparisons: usize = 0;
    const key = CountedTypedKey{ .target = target, .comparisons = &comparisons };
    const index = bsearch.upperBoundIndex(CountedTypedKey, u32, &key, items, compare);
    try std.testing.expectEqual(expected, index);
    return comparisons;
}

fn populateAscending(values: []u32) void {
    for (values, 0..) |*slot, index| {
        slot.* = @as(u32, @intCast((index + 1) * 3));
    }
}

fn populateDescending(descending: []u32, ascending: []const u32) void {
    std.debug.assert(descending.len == ascending.len);
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

fn assertRepresentativeTypedBudget(items: []const u32, compare: bsearch.CComparator(CountedTypedKey, u32)) !void {
    const budget = maxBinarySearchComparisons(items.len);
    if (items.len == 0) {
        const empty_budget = try expectTypedSearchBudget(items, 1, false, compare);
        try std.testing.expectEqual(@as(usize, 0), empty_budget);
        return;
    }

    var queries: [8]u32 = undefined;
    var expected_hits: [8]bool = undefined;
    fixtures.seedDeterministicQueries(items.len, items, &queries, &expected_hits);

    for (queries, expected_hits) |query, expect_hit| {
        const comparisons = try expectTypedSearchBudget(items, query, expect_hit, compare);
        try std.testing.expect(comparisons <= budget);
    }
}

test "phase 6 bsearch raw c abi budgets stay logarithmic for deterministic ascending and descending slices" {
    var ascending_storage: [max_perf_case_len]u32 = undefined;
    populateAscending(ascending_storage[0..]);

    var descending_storage: [max_perf_case_len]u32 = undefined;
    populateDescending(descending_storage[0..], ascending_storage[0..]);

    for (fixtures.dynamic_case_lengths) |len| {
        try assertRepresentativeBudget(ascending_storage[0..len], compareCountedOpaqueInt);
        try assertRepresentativeBudget(descending_storage[(descending_storage.len - len)..], compareCountedOpaqueDescendingInt);
    }

    for (fixtures.perf_cases) |case| {
        try assertRepresentativeBudget(ascending_storage[0..case.len], compareCountedOpaqueInt);
        try assertRepresentativeBudget(descending_storage[(descending_storage.len - case.len)..], compareCountedOpaqueDescendingInt);
    }
}

test "phase 6 bsearch typed c abi budgets stay logarithmic for deterministic ascending and descending slices" {
    var ascending_storage: [max_perf_case_len]u32 = undefined;
    populateAscending(ascending_storage[0..]);

    var descending_storage: [max_perf_case_len]u32 = undefined;
    populateDescending(descending_storage[0..], ascending_storage[0..]);

    for (fixtures.dynamic_case_lengths) |len| {
        try assertRepresentativeTypedBudget(ascending_storage[0..len], compareCountedTypedInt);
        try assertRepresentativeTypedBudget(descending_storage[(descending_storage.len - len)..], compareCountedTypedDescendingInt);
    }

    for (fixtures.perf_cases) |case| {
        try assertRepresentativeTypedBudget(ascending_storage[0..case.len], compareCountedTypedInt);
        try assertRepresentativeTypedBudget(descending_storage[(descending_storage.len - case.len)..], compareCountedTypedDescendingInt);
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

test "phase 6 bsearch typed c abi equal-range budgets stay logarithmic for duplicate spans in both sort orders" {
    const ascending_duplicates = fixtures.representative_duplicate_values;
    const descending_duplicates = fixtures.representative_descending_duplicate_values;

    const ascending_budget = try expectTypedRangeBudget(ascending_duplicates[0..], 21, .{ .lower = 4, .upper = 7 }, compareCountedTypedInt);
    try std.testing.expect(ascending_budget <= (2 * maxBinarySearchComparisons(ascending_duplicates.len)));

    const ascending_miss_budget = try expectTypedRangeBudget(ascending_duplicates[0..], 20, .{ .lower = 4, .upper = 4 }, compareCountedTypedInt);
    try std.testing.expect(ascending_miss_budget <= (2 * maxBinarySearchComparisons(ascending_duplicates.len)));

    const descending_budget = try expectTypedRangeBudget(descending_duplicates[0..], 21, .{ .lower = 3, .upper = 6 }, compareCountedTypedDescendingInt);
    try std.testing.expect(descending_budget <= (2 * maxBinarySearchComparisons(descending_duplicates.len)));

    const descending_miss_budget = try expectTypedRangeBudget(descending_duplicates[0..], 20, .{ .lower = 6, .upper = 6 }, compareCountedTypedDescendingInt);
    try std.testing.expect(descending_miss_budget <= (2 * maxBinarySearchComparisons(descending_duplicates.len)));
}

test "phase 6 bsearch raw c abi bound budgets stay logarithmic for duplicate spans and insertion points" {
    const ascending_duplicates = fixtures.representative_duplicate_values;
    const descending_duplicates = fixtures.representative_descending_duplicate_values;

    const ascending_budget = maxBinarySearchComparisons(ascending_duplicates.len);
    try std.testing.expect((try expectRawLowerBoundBudget(ascending_duplicates[0..], 21, 4, compareCountedOpaqueInt)) <= ascending_budget);
    try std.testing.expect((try expectRawUpperBoundBudget(ascending_duplicates[0..], 21, 7, compareCountedOpaqueInt)) <= ascending_budget);
    try std.testing.expect((try expectRawLowerBoundBudget(ascending_duplicates[0..], 20, 4, compareCountedOpaqueInt)) <= ascending_budget);
    try std.testing.expect((try expectRawUpperBoundBudget(ascending_duplicates[0..], 20, 4, compareCountedOpaqueInt)) <= ascending_budget);

    const descending_budget = maxBinarySearchComparisons(descending_duplicates.len);
    try std.testing.expect((try expectRawLowerBoundBudget(descending_duplicates[0..], 21, 3, compareCountedOpaqueDescendingInt)) <= descending_budget);
    try std.testing.expect((try expectRawUpperBoundBudget(descending_duplicates[0..], 21, 6, compareCountedOpaqueDescendingInt)) <= descending_budget);
    try std.testing.expect((try expectRawLowerBoundBudget(descending_duplicates[0..], 20, 6, compareCountedOpaqueDescendingInt)) <= descending_budget);
    try std.testing.expect((try expectRawUpperBoundBudget(descending_duplicates[0..], 20, 6, compareCountedOpaqueDescendingInt)) <= descending_budget);
}

test "phase 6 bsearch typed c abi bound budgets stay logarithmic for duplicate spans and insertion points" {
    const ascending_duplicates = fixtures.representative_duplicate_values;
    const descending_duplicates = fixtures.representative_descending_duplicate_values;

    const ascending_budget = maxBinarySearchComparisons(ascending_duplicates.len);
    try std.testing.expect((try expectTypedLowerBoundBudget(ascending_duplicates[0..], 21, 4, compareCountedTypedInt)) <= ascending_budget);
    try std.testing.expect((try expectTypedUpperBoundBudget(ascending_duplicates[0..], 21, 7, compareCountedTypedInt)) <= ascending_budget);
    try std.testing.expect((try expectTypedLowerBoundBudget(ascending_duplicates[0..], 20, 4, compareCountedTypedInt)) <= ascending_budget);
    try std.testing.expect((try expectTypedUpperBoundBudget(ascending_duplicates[0..], 20, 4, compareCountedTypedInt)) <= ascending_budget);

    const descending_budget = maxBinarySearchComparisons(descending_duplicates.len);
    try std.testing.expect((try expectTypedLowerBoundBudget(descending_duplicates[0..], 21, 3, compareCountedTypedDescendingInt)) <= descending_budget);
    try std.testing.expect((try expectTypedUpperBoundBudget(descending_duplicates[0..], 21, 6, compareCountedTypedDescendingInt)) <= descending_budget);
    try std.testing.expect((try expectTypedLowerBoundBudget(descending_duplicates[0..], 20, 6, compareCountedTypedDescendingInt)) <= descending_budget);
    try std.testing.expect((try expectTypedUpperBoundBudget(descending_duplicates[0..], 20, 6, compareCountedTypedDescendingInt)) <= descending_budget);
}

test "phase 6 bsearch typed c abi runtime-selected comparator pointers keep the budget contract" {
    const cases = [_]struct {
        items: []const u32,
        target: u32,
        expect_hit: bool,
        compare: bsearch.CComparator(CountedTypedKey, u32),
    }{
        .{ .items = fixtures.representative_ascending_values[0..], .target = 24, .expect_hit = true, .compare = compareCountedTypedInt },
        .{ .items = fixtures.representative_ascending_values[0..], .target = 26, .expect_hit = false, .compare = compareCountedTypedInt },
        .{ .items = fixtures.representative_descending_values[0..], .target = 24, .expect_hit = true, .compare = compareCountedTypedDescendingInt },
        .{ .items = fixtures.representative_descending_values[0..], .target = 26, .expect_hit = false, .compare = compareCountedTypedDescendingInt },
    };

    for (cases) |case| {
        const comparisons = try expectTypedSearchBudget(case.items, case.target, case.expect_hit, case.compare);
        try std.testing.expect(comparisons <= maxBinarySearchComparisons(case.items.len));
    }
}

test "phase 6 bsearch typed c abi runtime-selected bound and equal-range comparator pointers keep the budget contract" {
    const cases = [_]struct {
        items: []const u32,
        target: u32,
        expected: bsearch.IndexRange,
        compare: bsearch.CComparator(CountedTypedKey, u32),
    }{
        .{ .items = fixtures.representative_duplicate_values[0..], .target = 21, .expected = .{ .lower = 4, .upper = 7 }, .compare = compareCountedTypedInt },
        .{ .items = fixtures.representative_duplicate_values[0..], .target = 20, .expected = .{ .lower = 4, .upper = 4 }, .compare = compareCountedTypedInt },
        .{ .items = fixtures.representative_descending_duplicate_values[0..], .target = 21, .expected = .{ .lower = 3, .upper = 6 }, .compare = compareCountedTypedDescendingInt },
        .{ .items = fixtures.representative_descending_duplicate_values[0..], .target = 20, .expected = .{ .lower = 6, .upper = 6 }, .compare = compareCountedTypedDescendingInt },
    };

    for (cases) |case| {
        const budget = maxBinarySearchComparisons(case.items.len);
        try std.testing.expect((try expectTypedLowerBoundBudget(case.items, case.target, case.expected.lower, case.compare)) <= budget);
        try std.testing.expect((try expectTypedUpperBoundBudget(case.items, case.target, case.expected.upper, case.compare)) <= budget);
        try std.testing.expect((try expectTypedRangeBudget(case.items, case.target, case.expected, case.compare)) <= (2 * budget));
    }
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

test "phase 6 bsearch runtime-selected raw c abi bound and equal-range comparator pointers keep the budget contract" {
    const cases = [_]struct {
        items: []const u32,
        target: u32,
        expected: bsearch.IndexRange,
        compare: bsearch.CRawComparator,
    }{
        .{ .items = fixtures.representative_duplicate_values[0..], .target = 21, .expected = .{ .lower = 4, .upper = 7 }, .compare = compareCountedOpaqueInt },
        .{ .items = fixtures.representative_duplicate_values[0..], .target = 20, .expected = .{ .lower = 4, .upper = 4 }, .compare = compareCountedOpaqueInt },
        .{ .items = fixtures.representative_descending_duplicate_values[0..], .target = 21, .expected = .{ .lower = 3, .upper = 6 }, .compare = compareCountedOpaqueDescendingInt },
        .{ .items = fixtures.representative_descending_duplicate_values[0..], .target = 20, .expected = .{ .lower = 6, .upper = 6 }, .compare = compareCountedOpaqueDescendingInt },
    };

    for (cases) |case| {
        const budget = maxBinarySearchComparisons(case.items.len);
        try std.testing.expect((try expectRawLowerBoundBudget(case.items, case.target, case.expected.lower, case.compare)) <= budget);
        try std.testing.expect((try expectRawUpperBoundBudget(case.items, case.target, case.expected.upper, case.compare)) <= budget);
        try std.testing.expect((try expectRangeBudget(case.items, case.target, case.expected, case.compare)) <= (2 * budget));
    }
}
