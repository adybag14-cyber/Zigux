const std = @import("std");

const bench_source_path = "zigux/tests/phase1_bench.zig";
const expectations_path = "zigux/tests/fixtures/phase1_bench_expectations.json";
const checker_path = "scripts/zigux/check-phase1-bench.py";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(2 * 1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "bitmap bench source still emits the two bitmap expectation keys" {
    const allocator = std.testing.allocator;
    const source = try readFile(allocator, bench_source_path);
    defer allocator.free(source);

    try expectContains(source, "fn bitmapWeightBench() struct { checksum: u64 } {");
    try expectContains(source, "fn bitmapWindowBench() struct { checksum: u64 } {");
    try expectContains(source, "const bitmap_weight_result = bitmapWeightBench();");
    try expectContains(source, "const bitmap_window_result = bitmapWindowBench();");
    try expectContains(source, "try stdout_writer.interface.print(\"PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS={d}\\n\", .{iterations_bitmap_weight});");
    try expectContains(source, "try stdout_writer.interface.print(\"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM={d}\\n\", .{bitmap_weight_result.checksum});");
    try expectContains(source, "try stdout_writer.interface.print(\"PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS={d}\\n\", .{iterations_bitmap_window});");
    try expectContains(source, "try stdout_writer.interface.print(\"PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM={d}\\n\", .{bitmap_window_result.checksum});");
}

test "bitmap expectations fixture pins current exact iteration and checksum values" {
    const allocator = std.testing.allocator;
    const expectations = try readFile(allocator, expectations_path);
    defer allocator.free(expectations);

    try expectContains(expectations, "\"PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS\": 20000");
    try expectContains(expectations, "\"PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS\": 20000");
    try expectContains(expectations, "\"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM\"");
    try expectContains(expectations, "\"PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM\"");
    try expectContains(expectations, "\"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM\": 100000");
    try expectContains(expectations, "\"PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM\": 120000");
}

test "bench checker keeps bitmap exact-checksum fail-closed labels" {
    const allocator = std.testing.allocator;
    const checker = try readFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "BITMAP_REQUIRED_EXACT_CHECKSUMS = {");
    try expectContains(checker, "\"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM\"");
    try expectContains(checker, "\"PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM\"");
    try expectContains(checker, "expectations_missing_bitmap_exact_checksums");
    try expectContains(checker, "expectations_bitmap_exact_checksum_value");
}
