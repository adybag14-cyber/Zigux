const std = @import("std");

const File = struct {
    contents: []u8,
};

fn readFile(path: []const u8, limit: usize) !File {
    return .{
        .contents = try std.Io.Dir.cwd().readFileAlloc(
            std.testing.io,
            path,
            std.testing.allocator,
            .limited(limit),
        ),
    };
}

fn unload(file: File) void {
    std.testing.allocator.free(file.contents);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectExactOccurrence(haystack: []const u8, needle: []const u8) !void {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |idx| {
        count += 1;
        offset = idx + needle.len;
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstNeedle;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondNeedle;
    try std.testing.expect(first_index < second_index);
}

const hweight_source_markers = [_][]const u8{
    "fn hweightBench() struct { checksum: u64 } {",
    "while (idx < iterations_hweight) : (idx += 1) {",
    "checksum +%= hweight.swHweight8(0xf0);",
    "checksum +%= hweight.swHweight16(0xf0f0);",
    "checksum +%= hweight.swHweight32(0xf0f0_f0f0);",
    "checksum +%= hweight.swHweight64(0xf0f0_f0f0_f0f0_f0f0);",
    "checksum +%= @intCast(hweight.hweightLong(0xf0f0));",
    "const hweight_result = hweightBench();",
    "PHASE1_BENCH_HWEIGHT_ITERATIONS={d}",
    "PHASE1_BENCH_HWEIGHT_CHECKSUM={d}",
};

test "phase1 hweight bench source keeps expectation markers explicit" {
    const bench_source = try readFile("zigux/tests/phase1_bench.zig", 192 * 1024);
    defer unload(bench_source);

    inline for (hweight_source_markers) |marker| {
        try expectContains(bench_source.contents, marker);
    }

    try expectBefore(
        bench_source.contents,
        "const iterations_hweight: u64 = 100000;",
        "fn hweightBench() struct { checksum: u64 } {",
    );
    try expectBefore(
        bench_source.contents,
        "const hweight_result = hweightBench();",
        "PHASE1_BENCH_HWEIGHT_CHECKSUM={d}",
    );
}

test "phase1 hweight bench expectations stay exact in the fixture" {
    const expectations = try readFile("zigux/tests/fixtures/phase1_bench_expectations.json", 64 * 1024);
    defer unload(expectations);

    try expectExactOccurrence(expectations.contents, "\"PHASE1_BENCH_HWEIGHT_ITERATIONS\": 100000");
    try expectContains(expectations.contents, "\"PHASE1_BENCH_HWEIGHT_CHECKSUM\"");
    try expectExactOccurrence(expectations.contents, "\"PHASE1_BENCH_HWEIGHT_CHECKSUM\": 6800000");

    try expectBefore(
        expectations.contents,
        "\"PHASE1_BENCH_STRING_CHECKSUM\"",
        "\"PHASE1_BENCH_HWEIGHT_CHECKSUM\"",
    );
    try expectBefore(
        expectations.contents,
        "\"PHASE1_BENCH_HWEIGHT_CHECKSUM\"",
        "\"PHASE1_BENCH_LIST_SORT_CHECKSUM\"",
    );
}

test "phase1 bench checker fail-closes missing hweight exact checksums" {
    const checker = try readFile("scripts/zigux/check-phase1-bench.py", 192 * 1024);
    defer unload(checker);

    const checker_markers = [_][]const u8{
        "HWEIGHT_REQUIRED_EXACT_CHECKSUMS = {\"PHASE1_BENCH_HWEIGHT_CHECKSUM\"}",
        "(\"expectations_checksums_hweight_exact_required\", HWEIGHT_REQUIRED_EXACT_CHECKSUMS)",
        "(\"missing_hweight_exact_checksums\", HWEIGHT_REQUIRED_EXACT_CHECKSUMS)",
        "\"PHASE1_BENCH_HWEIGHT_ITERATIONS\": 100000",
        "\"PHASE1_BENCH_HWEIGHT_CHECKSUM\"",
    };
    inline for (checker_markers) |marker| {
        try expectContains(checker.contents, marker);
    }

    try expectBefore(
        checker.contents,
        "(\"missing_string_exact_checksums\", STRING_REQUIRED_EXACT_CHECKSUMS)",
        "(\"missing_hweight_exact_checksums\", HWEIGHT_REQUIRED_EXACT_CHECKSUMS)",
    );
    try expectBefore(
        checker.contents,
        "(\"missing_hweight_exact_checksums\", HWEIGHT_REQUIRED_EXACT_CHECKSUMS)",
        "(\"missing_list_sort_exact_checksums\", LIST_SORT_REQUIRED_EXACT_CHECKSUMS)",
    );
}
