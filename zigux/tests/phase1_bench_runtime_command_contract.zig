const std = @import("std");

const checker_path = "scripts/zigux/check-phase1-bench.py";
const build_path = "zigux/tests/phase1_bench_build.zig";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const found = std.mem.indexOfPos(u8, haystack, cursor, needle) orelse {
            return error.ExpectedNeedleInOrder;
        };
        cursor = found + needle.len;
    }
}

test "phase1 bench checker invokes standalone bench build in release-safe mode" {
    const allocator = std.testing.allocator;
    const checker = try readFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectOrdered(checker, &.{
        "subprocess.run(",
        "[zig, \"build\", \"bench\", \"--build-file\", \"zigux/tests/phase1_bench_build.zig\", \"-Doptimize=ReleaseSafe\"]",
        "cwd=str(root)",
        "capture_output=True",
        "text=True",
    });
    try expectContains(checker, "zig = find_zig(root, args.zig)");
    try expectContains(checker, "phase1_bench = bench_source_path(root)");
    try expectNotContains(checker, "\"zigux/tests/build.zig\", \"-Doptimize=ReleaseSafe\"");
}

test "phase1 bench checker keeps bench command failure diagnostics fail closed" {
    const allocator = std.testing.allocator;
    const checker = try readFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectOrdered(checker, &.{
        "if result.returncode != 0:",
        "print(\"PHASE1_BENCH_CHECK=fail\")",
        "print(f\"BENCH_COMMAND_EXIT={result.returncode}\")",
        "if result.stdout:",
        "print(result.stdout.rstrip(\"\\n\"))",
        "if result.stderr:",
        "print(result.stderr.rstrip(\"\\n\"))",
        "return 1",
    });
}

test "phase1 bench checker reports resolved success inputs" {
    const allocator = std.testing.allocator;
    const checker = try readFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectOrdered(checker, &.{
        "kind, payload = validate_output(expectations, result.stdout)",
        "print(\"PHASE1_BENCH_CHECK=pass\")",
        "print(f\"PHASE1_BENCH_EXPECTATIONS={expectations_file}\")",
        "print(f\"PHASE1_BENCH_SOURCE={phase1_bench}\")",
        "print(f\"PHASE1_BENCH_ZIG={zig}\")",
        "return 0",
    });
}

test "phase1 bench build exposes focused bench and test routes" {
    const allocator = std.testing.allocator;
    const build = try readFile(allocator, build_path);
    defer allocator.free(build);

    try expectContains(build, ".root_source_file = b.path(\"phase1_bench.zig\")");
    try expectContains(build, ".name = \"phase1-bench\"");
    try expectContains(build, "const run_bench = b.addRunArtifact(exe);");
    try expectContains(build, "b.step(\n        \"bench\",\n        \"Run the focused Phase 1 helper benchmark packet from zigux/tests\"");
    try expectContains(build, "b.step(\n        \"test\",\n        \"Run the focused Phase 1 helper benchmark packet from zigux/tests\"");
    try expectContains(build, "bench_step.dependOn(&run_bench.step);");
    try expectContains(build, "test_step.dependOn(&run_bench.step);");
    try expectContains(build, "b.default_step.dependOn(test_step);");
}
