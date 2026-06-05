const std = @import("std");

const testing = std.testing;

const bench_source_path = "zigux/tests/phase1_bench.zig";
const expectations_path = "zigux/tests/fixtures/phase1_bench_expectations.json";
const bench_checker_path = "scripts/zigux/check-phase1-bench.py";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

fn expectCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var remaining = haystack;
    while (std.mem.indexOf(u8, remaining, needle)) |index| {
        count += 1;
        remaining = remaining[index + needle.len ..];
    }
    try testing.expectEqual(expected, count);
}

test "find-bit bench source exposes base and edge hardening routes" {
    const allocator = testing.allocator;
    const source = try readFile(allocator, bench_source_path);
    defer allocator.free(source);

    try expectContains(source, "const iterations_find_bit: u64 = 20000;");
    try expectContains(source, "const iterations_find_bit_edge: u64 = 20000;");
    try expectContains(source, "fn findBitBench() struct { checksum: u64 } {");
    try expectContains(source, "fn findBitEdgeBench() struct { checksum: u64 } {");
    try expectContains(source, "const boundary = find_bit.bits_per_long - 1;");
    try expectContains(source, "const tail_nbits = find_bit.bits_per_long + 5;");
    try expectContains(source, "checksum +%= @intCast(find_bit.findNextBit(&boundary_set, head_nbits, boundary));");
    try expectContains(source, "checksum +%= @intCast(find_bit.findNextAndBit(&boundary_set, &boundary_set, head_nbits, boundary));");
    try expectContains(source, "checksum +%= @intCast(find_bit.findNextZeroBit(&boundary_zero, head_nbits, boundary));");
    try expectContains(source, "checksum +%= @intCast(find_bit.findFirstBit(&tail_set, tail_nbits));");
    try expectContains(source, "checksum +%= @intCast(find_bit.findFirstAndBit(&tail_set, &tail_set, tail_nbits));");
    try expectContains(source, "checksum +%= @intCast(find_bit.findLastBit(&tail_set, tail_nbits));");
    try expectContains(source, "const find_bit_result = findBitBench();");
    try expectContains(source, "const find_bit_edge_result = findBitEdgeBench();");
    try expectOrdered(
        source,
        "try stdout_writer.interface.print(\"PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS={d}\\n\", .{iterations_find_bit});",
        "try stdout_writer.interface.print(\"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM={d}\\n\", .{find_bit_result.checksum});",
    );
    try expectOrdered(
        source,
        "try stdout_writer.interface.print(\"PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS={d}\\n\", .{iterations_find_bit_edge});",
        "try stdout_writer.interface.print(\"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM={d}\\n\", .{find_bit_edge_result.checksum});",
    );
}

test "find-bit expectations fixture pins exact iteration and checksum values" {
    const allocator = testing.allocator;
    const expectations = try readFile(allocator, expectations_path);
    defer allocator.free(expectations);

    try expectContains(expectations, "\"PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS\": 20000");
    try expectContains(expectations, "\"PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS\": 20000");
    try expectContains(expectations, "\"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM\"");
    try expectContains(expectations, "\"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM\"");
    try expectContains(expectations, "\"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM\": 3780000");
    try expectContains(expectations, "\"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM\": 4020000");
    try expectOrdered(
        expectations,
        "\"PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS\": 20000",
        "\"PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS\": 20000",
    );
    try expectOrdered(
        expectations,
        "\"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM\"",
        "\"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM\"",
    );
    try expectCount(expectations, "\"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM\"", 2);
    try expectCount(expectations, "\"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM\"", 2);
}

test "bench checker fail-closes around find-bit exact checksums" {
    const allocator = testing.allocator;
    const checker = try readFile(allocator, bench_checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "\"PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS\": 20000");
    try expectContains(checker, "\"PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS\": 20000");
    try expectContains(checker, "FIND_BIT_REQUIRED_EXACT_CHECKSUMS = {");
    try expectContains(checker, "\"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM\",");
    try expectContains(checker, "\"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM\",");
    try expectContains(checker, "(\"expectations_checksums_find_bit_exact_required\", FIND_BIT_REQUIRED_EXACT_CHECKSUMS)");
    try expectContains(checker, "(\"missing_find_bit_exact_checksums\", FIND_BIT_REQUIRED_EXACT_CHECKSUMS)");
    try expectContains(checker, "assert_case(kind == \"bench_source_missing_markers\", \"missing find_bit marker\", (kind, payload))");
    try expectContains(checker, "assert_case(payload == [\"find_edge_checksum_print\"], \"missing find_bit marker payload\", payload)");
    try expectContains(checker, "PHASE1_BENCH_CHECK_SELF_TEST=pass");
    try expectContains(checker, "PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT=");
}
