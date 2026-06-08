const std = @import("std");

const bench_checker_path = "scripts/zigux/check-phase1-bench.py";

const cli_markers = [_][]const u8{
    "parser.add_argument(\"--repo-root\", \"--root\", dest=\"repo_root\", help=\"Override the repository root used for validation.\")",
    "parser.add_argument(\"--zig\", help=\"Path to Zig executable\")",
    "parser.add_argument(\"--self-test\", action=\"store_true\", help=\"Run checker self-test cases without invoking Zig.\")",
    "if args.self_test:",
    "root = repo_root(args.repo_root)",
    "zig = find_zig(root, args.zig)",
};

const failclosed_output_markers = [_][]const u8{
    "print(\"PHASE1_BENCH_CHECK=fail\")",
    "print(f\"PHASE1_BENCH_CHECK_REASON={kind}\")",
    "print(f\"EXPECTATIONS_PATH={payload}\")",
    "print(f\"EXPECTATIONS_JSON_ERROR={exc.msg}\")",
    "print(f\"EXPECTATIONS_JSON_LINE={exc.lineno}\")",
    "print(f\"EXPECTATIONS_JSON_COLUMN={exc.colno}\")",
    "print(f\"BENCH_COMMAND_EXIT={result.returncode}\")",
};

const success_output_markers = [_][]const u8{
    "print(\"PHASE1_BENCH_CHECK=pass\")",
    "print(f\"PHASE1_BENCH_EXPECTATIONS={expectations_file}\")",
    "print(f\"PHASE1_BENCH_SOURCE={phase1_bench}\")",
    "print(f\"PHASE1_BENCH_ZIG={zig}\")",
};

const reason_markers = [_][]const u8{
    "\"missing_expectations_file\"",
    "\"expectations_json_error\"",
    "\"missing_bench_source_file\"",
    "\"bench_source_missing_markers\"",
    "\"bench_source_duplicate_rbtree_markers\"",
    "\"duplicate\"",
    "\"unexpected\"",
    "\"status\"",
    "\"missing_rbtree_iterations\"",
    "\"missing_rbtree_exact_checksums\"",
    "\"exact_checksum_mismatch\"",
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

fn expectContainsOnce(source: []const u8, marker: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countNeedle(source, marker));
}

fn expectContains(source: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, marker) != null);
}

fn readBenchChecker(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, bench_checker_path, allocator, .limited(256 * 1024));
}

test "bench checker keeps root zig and self-test cli contract" {
    const source = try readBenchChecker(std.testing.allocator);
    defer std.testing.allocator.free(source);

    for (cli_markers) |marker| {
        try expectContainsOnce(source, marker);
    }
    try std.testing.expect(std.mem.indexOf(u8, source, "--repo-root\", \"--root\"").? < std.mem.indexOf(u8, source, "root = repo_root(args.repo_root)").?);
    try std.testing.expect(std.mem.indexOf(u8, source, "parser.add_argument(\"--self-test\"").? < std.mem.indexOf(u8, source, "if args.self_test:").?);
}

test "bench checker fail-closed outputs stay explicit" {
    const source = try readBenchChecker(std.testing.allocator);
    defer std.testing.allocator.free(source);

    for (failclosed_output_markers) |marker| {
        try expectContains(source, marker);
    }
    try std.testing.expect(countNeedle(source, "print(\"PHASE1_BENCH_CHECK=fail\")") >= 4);
    try std.testing.expect(std.mem.indexOf(u8, source, "print(f\"EXPECTATIONS_JSON_ERROR={exc.msg}\")").? < std.mem.indexOf(u8, source, "return 1\n    if kind != \"pass\":").?);
    try std.testing.expect(std.mem.indexOf(u8, source, "print(f\"BENCH_COMMAND_EXIT={result.returncode}\")").? < std.mem.indexOf(u8, source, "return 1\n\n    kind, payload = validate_output").?);
}

test "bench checker pass outputs identify resolved inputs" {
    const source = try readBenchChecker(std.testing.allocator);
    defer std.testing.allocator.free(source);

    for (success_output_markers) |marker| {
        try expectContainsOnce(source, marker);
    }
    try std.testing.expect(std.mem.indexOf(u8, source, "print(\"PHASE1_BENCH_CHECK=pass\")").? < std.mem.indexOf(u8, source, "print(f\"PHASE1_BENCH_EXPECTATIONS={expectations_file}\")").?);
    try std.testing.expect(std.mem.indexOf(u8, source, "print(f\"PHASE1_BENCH_SOURCE={phase1_bench}\")").? < std.mem.indexOf(u8, source, "print(f\"PHASE1_BENCH_ZIG={zig}\")").?);
}

test "bench checker reason vocabulary covers fail-closed lanes" {
    const source = try readBenchChecker(std.testing.allocator);
    defer std.testing.allocator.free(source);

    for (reason_markers) |marker| {
        try expectContains(source, marker);
    }
    try expectContainsOnce(source, "if kind == \"missing_expectations_file\":");
    try expectContainsOnce(source, "if kind == \"expectations_json_error\":");
    try std.testing.expect(countNeedle(source, "if kind != \"pass\":\n        print(\"PHASE1_BENCH_CHECK=fail\")") >= 3);
}
