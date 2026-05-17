const std = @import("std");

pub const SearchCase = struct {
    name: []const u8,
    haystack: []const i32,
    needle: i32,
    expect_found_index: ?usize,
    expect_lower_bound: usize,
    expect_upper_bound: usize,
};

const EMPTY = [_]i32{};
const ASCENDING_SMALL = [_]i32{ 1, 3, 5, 7 };
const DUPLICATES = [_]i32{ 2, 2, 4, 4, 4, 9 };
const NEGATIVE_TO_POSITIVE = [_]i32{ -9, -4, -1, 0, 6, 11 };
const SPARSE = [_]i32{ 8, 16, 32, 64, 128, 256 };

pub const cases = [_]SearchCase{
    .{
        .name = "empty-haystack",
        .haystack = EMPTY[0..],
        .needle = 4,
        .expect_found_index = null,
        .expect_lower_bound = 0,
        .expect_upper_bound = 0,
    },
    .{
        .name = "exact-hit-middle",
        .haystack = ASCENDING_SMALL[0..],
        .needle = 5,
        .expect_found_index = 2,
        .expect_lower_bound = 2,
        .expect_upper_bound = 3,
    },
    .{
        .name = "before-first",
        .haystack = ASCENDING_SMALL[0..],
        .needle = 0,
        .expect_found_index = null,
        .expect_lower_bound = 0,
        .expect_upper_bound = 0,
    },
    .{
        .name = "after-last",
        .haystack = ASCENDING_SMALL[0..],
        .needle = 8,
        .expect_found_index = null,
        .expect_lower_bound = ASCENDING_SMALL.len,
        .expect_upper_bound = ASCENDING_SMALL.len,
    },
    .{
        .name = "between-entries",
        .haystack = NEGATIVE_TO_POSITIVE[0..],
        .needle = 5,
        .expect_found_index = null,
        .expect_lower_bound = 4,
        .expect_upper_bound = 4,
    },
    .{
        .name = "duplicate-run-first",
        .haystack = DUPLICATES[0..],
        .needle = 2,
        .expect_found_index = 0,
        .expect_lower_bound = 0,
        .expect_upper_bound = 2,
    },
    .{
        .name = "duplicate-run-middle",
        .haystack = DUPLICATES[0..],
        .needle = 4,
        .expect_found_index = 2,
        .expect_lower_bound = 2,
        .expect_upper_bound = 5,
    },
    .{
        .name = "sparse-upper-gap",
        .haystack = SPARSE[0..],
        .needle = 200,
        .expect_found_index = null,
        .expect_lower_bound = 5,
        .expect_upper_bound = 5,
    },
};

test "phase6 bsearch vectors stay internally sorted" {
    for (cases) |case| {
        for (case.haystack, 0..) |value, idx| {
            if (idx == 0) continue;
            try std.testing.expect(case.haystack[idx - 1] <= value);
        }
        try std.testing.expect(case.expect_lower_bound <= case.expect_upper_bound);
        try std.testing.expect(case.expect_upper_bound <= case.haystack.len);
        if (case.expect_found_index) |found_index| {
            try std.testing.expect(found_index < case.haystack.len);
            try std.testing.expect(case.haystack[found_index] == case.needle);
            try std.testing.expect(case.expect_lower_bound <= found_index);
            try std.testing.expect(found_index < case.expect_upper_bound);
        }
    }
}
