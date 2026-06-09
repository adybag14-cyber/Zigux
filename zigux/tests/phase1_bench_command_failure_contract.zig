const std = @import("std");

const bench_checker_path = "scripts/zigux/check-phase1-bench.py";

const command_invocation_markers = [_][]const u8{
    "result = subprocess.run(",
    "[zig, \"build\", \"bench\", \"--build-file\", \"zigux/tests/phase1_bench_build.zig\", \"-Doptimize=ReleaseSafe\"]",
    "cwd=str(root)",
    "capture_output=True",
    "text=True",
};

const command_failure_markers = [_][]const u8{
    "if result.returncode != 0:",
    "print(\"PHASE1_BENCH_CHECK=fail\")",
    "print(f\"BENCH_COMMAND_EXIT={result.returncode}\")",
    "if result.stdout:",
    "print(result.stdout.rstrip(\"\\n\"))",
    "if result.stderr:",
    "print(result.stderr.rstrip(\"\\n\"))",
    "return 1",
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

test "bench checker invokes the Phase 1 bench command with captured diagnostics" {
    const source = try readBenchChecker(std.testing.allocator);
    defer std.testing.allocator.free(source);

    for (command_invocation_markers) |marker| {
        try expectContains(source, marker);
    }
    try expectContainsOnce(source, "result = subprocess.run(");
    try expectBefore(source, "result = subprocess.run(", "if result.returncode != 0:");
    try expectBefore(source, "capture_output=True", "if result.returncode != 0:");
    try expectBefore(source, "text=True", "if result.returncode != 0:");
}

test "bench checker fails closed and reports the command exit code" {
    const source = try readBenchChecker(std.testing.allocator);
    defer std.testing.allocator.free(source);

    for (command_failure_markers) |marker| {
        try expectContains(source, marker);
    }
    try expectBefore(source, "if result.returncode != 0:", "print(\"PHASE1_BENCH_CHECK=fail\")");
    try expectBefore(source, "print(\"PHASE1_BENCH_CHECK=fail\")", "print(f\"BENCH_COMMAND_EXIT={result.returncode}\")");
    try expectBefore(source, "print(f\"BENCH_COMMAND_EXIT={result.returncode}\")", "return 1\n\n    kind, payload = validate_output");
}

test "bench checker preserves captured bench stdout before stderr on command failure" {
    const source = try readBenchChecker(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectBefore(source, "if result.stdout:", "print(result.stdout.rstrip(\"\\n\"))");
    try expectBefore(source, "print(result.stdout.rstrip(\"\\n\"))", "if result.stderr:");
    try expectBefore(source, "if result.stderr:", "print(result.stderr.rstrip(\"\\n\"))");
    try expectBefore(source, "print(f\"BENCH_COMMAND_EXIT={result.returncode}\")", "if result.stdout:");
}