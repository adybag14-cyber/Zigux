const std = @import("std");

const bench_checker_path = "scripts/zigux/check-phase1-bench.py";

const success_footer_markers = [_][]const u8{
    "print(\"PHASE1_BENCH_CHECK=pass\")",
    "print(f\"PHASE1_BENCH_EXPECTATIONS={expectations_file}\")",
    "print(f\"PHASE1_BENCH_SOURCE={phase1_bench}\")",
    "print(f\"PHASE1_BENCH_ZIG={zig}\")",
    "return 0",
};

fn countNeedle(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOf(u8, haystack[index..], needle)) |found| {
        count += 1;
        index += found + needle.len;
    }
    return count;
}

fn expectContains(source: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, marker) != null);
}

fn expectContainsOnce(source: []const u8, marker: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countNeedle(source, marker));
}

fn expectBefore(source: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, source, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, source, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn readBenchChecker(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, bench_checker_path, allocator, .limited(256 * 1024));
}

test "bench checker reports pass only after output validation succeeds" {
    const source = try readBenchChecker(std.testing.allocator);
    defer std.testing.allocator.free(source);

    for (success_footer_markers) |marker| {
        try expectContains(source, marker);
    }

    try expectContainsOnce(source, "print(\"PHASE1_BENCH_CHECK=pass\")");
    try expectBefore(source, "kind, payload = validate_output(expectations, result.stdout)", "if kind != \"pass\":");
    try expectBefore(source, "if kind != \"pass\":", "print(\"PHASE1_BENCH_CHECK=pass\")");
    try expectBefore(source, "print(f\"PHASE1_BENCH_CHECK_REASON={kind}\")", "print(\"PHASE1_BENCH_CHECK=pass\")");
}

test "bench checker prints pass footer paths in stable readback order" {
    const source = try readBenchChecker(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectBefore(source, "print(\"PHASE1_BENCH_CHECK=pass\")", "print(f\"PHASE1_BENCH_EXPECTATIONS={expectations_file}\")");
    try expectBefore(source, "print(f\"PHASE1_BENCH_EXPECTATIONS={expectations_file}\")", "print(f\"PHASE1_BENCH_SOURCE={phase1_bench}\")");
    try expectBefore(source, "print(f\"PHASE1_BENCH_SOURCE={phase1_bench}\")", "print(f\"PHASE1_BENCH_ZIG={zig}\")");
    try expectBefore(source, "print(f\"PHASE1_BENCH_ZIG={zig}\")", "return 0");
}

test "bench checker keeps failure and success envelopes separated" {
    const source = try readBenchChecker(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "print(\"PHASE1_BENCH_CHECK=fail\")");
    try expectBefore(source, "print(\"PHASE1_BENCH_CHECK=fail\")", "print(\"PHASE1_BENCH_CHECK=pass\")");
    try expectBefore(source, "return 1\n\n    print(\"PHASE1_BENCH_CHECK=pass\")", "print(f\"PHASE1_BENCH_EXPECTATIONS={expectations_file}\")");
    try expectContainsOnce(source, "print(f\"PHASE1_BENCH_EXPECTATIONS={expectations_file}\")");
    try expectContainsOnce(source, "print(f\"PHASE1_BENCH_SOURCE={phase1_bench}\")");
    try expectContainsOnce(source, "print(f\"PHASE1_BENCH_ZIG={zig}\")");
}
