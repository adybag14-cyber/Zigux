const std = @import("std");

const bench_source_path = "zigux/tests/phase1_bench.zig";
const expectations_path = "zigux/tests/fixtures/phase1_bench_expectations.json";
const checker_path = "scripts/zigux/check-phase1-bench.py";

const string_source_markers = [_][]const u8{
    "const iterations_string: u64 = 40000;",
    "fn stringBench() !struct { checksum: u64 } {",
    "const enabled = try string.strtobool(if (even) \"on\" else \"0\");",
    "var trim_buf = [_]u8{ ' ', '\\t', 'h', 'i', ' ', '\\n' };",
    "const trimmed = string.trimSpaces(&trim_buf);",
    "const parsed = string.memparse(if (even) \"64K rest\" else \"-17 tail\");",
    "string.memchrInv(\"aaaaXaaa\", 'a')",
    "string.memchrInv(\"bbbb\", 'b');",
    "const string_result = try stringBench();",
    "try stdout_writer.interface.print(\"PHASE1_BENCH_STRING_ITERATIONS={d}\\n\", .{iterations_string});",
    "try stdout_writer.interface.print(\"PHASE1_BENCH_STRING_CHECKSUM={d}\\n\", .{string_result.checksum});",
};

const expectation_markers = [_][]const u8{
    "\"PHASE1_BENCH_STRING_ITERATIONS\": 40000",
    "\"PHASE1_BENCH_STRING_CHECKSUM\"",
    "\"PHASE1_BENCH_STRING_CHECKSUM\": 320000",
};

const checker_markers = [_][]const u8{
    "\"PHASE1_BENCH_STRING_ITERATIONS\": 40000",
    "\"PHASE1_BENCH_STRING_CHECKSUM\"",
    "STRING_REQUIRED_EXACT_CHECKSUMS = {\"PHASE1_BENCH_STRING_CHECKSUM\"}",
    "(\"expectations_checksums_string_exact_required\", STRING_REQUIRED_EXACT_CHECKSUMS)",
    "(\"missing_string_exact_checksums\", STRING_REQUIRED_EXACT_CHECKSUMS)",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireContainsOnce(haystack: []const u8, needle: []const u8) !void {
    const first = std.mem.indexOf(u8, haystack, needle);
    try std.testing.expect(first != null);
    const after_first = haystack[first.? + needle.len ..];
    try std.testing.expect(std.mem.indexOf(u8, after_first, needle) == null);
}

test "phase1 string bench source keeps expected operations and output keys" {
    const allocator = std.testing.allocator;
    const source = try readRepoFile(allocator, bench_source_path);
    defer allocator.free(source);

    for (string_source_markers) |marker| {
        try requireContains(source, marker);
    }
    try requireContainsOnce(source, "fn stringBench() !struct { checksum: u64 } {");
    try requireContainsOnce(source, "const string_result = try stringBench();");
    try requireContainsOnce(source, "PHASE1_BENCH_STRING_ITERATIONS={d}\\n");
    try requireContainsOnce(source, "PHASE1_BENCH_STRING_CHECKSUM={d}\\n");
}

test "phase1 bench expectations pin string iteration and exact checksum" {
    const allocator = std.testing.allocator;
    const expectations = try readRepoFile(allocator, expectations_path);
    defer allocator.free(expectations);

    for (expectation_markers) |marker| {
        try requireContains(expectations, marker);
    }
    try requireContainsOnce(expectations, "\"PHASE1_BENCH_STRING_ITERATIONS\": 40000");
    try requireContainsOnce(expectations, "\"PHASE1_BENCH_STRING_CHECKSUM\": 320000");
}

test "phase1 bench checker keeps string exact checksum fail closed" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    for (checker_markers) |marker| {
        try requireContains(checker, marker);
    }
    try requireContainsOnce(checker, "STRING_REQUIRED_EXACT_CHECKSUMS = {\"PHASE1_BENCH_STRING_CHECKSUM\"}");
    try requireContainsOnce(checker, "(\"missing_string_exact_checksums\", STRING_REQUIRED_EXACT_CHECKSUMS)");
}
