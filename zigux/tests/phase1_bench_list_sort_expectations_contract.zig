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

test "list_sort bench source exposes stable duplicate-order benchmark route" {
    const allocator = testing.allocator;
    const source = try readFile(allocator, bench_source_path);
    defer allocator.free(source);

    try expectContains(source, "const iterations_list_sort: u64 = 1000;");
    try expectContains(source, "const ListEntry = struct {");
    try expectContains(source, "fn listSortBench() struct { checksum: u64 } {");
    try expectContains(source, "fn less(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {");
    try expectContains(source, "var head: list_sort.ListHead = .{};");
    try expectContains(source, "head.init();");
    try expectContains(source, ".{ .key = 2, .ordinal = 0 },");
    try expectContains(source, ".{ .key = 1, .ordinal = 1 },");
    try expectContains(source, ".{ .key = 3, .ordinal = 2 },");
    try expectContains(source, ".{ .key = 1, .ordinal = 3 },");
    try expectContains(source, ".{ .key = 3, .ordinal = 4 },");
    try expectContains(source, "list_sort.listAddTail(&entry.node, &head);");
    try expectContains(source, "list_sort.listSort(null, &head, cmp);");
    try expectContains(source, "checksum +%= @intCast(entry.ordinal);");
    try expectContains(source, "const list_sort_result = listSortBench();");
    try expectOrdered(
        source,
        "try stdout_writer.interface.print(\"PHASE1_BENCH_LIST_SORT_ITERATIONS={d}\\n\", .{iterations_list_sort});",
        "try stdout_writer.interface.print(\"PHASE1_BENCH_LIST_SORT_CHECKSUM={d}\\n\", .{list_sort_result.checksum});",
    );
}

test "list_sort expectations fixture pins exact iteration and checksum values" {
    const allocator = testing.allocator;
    const expectations = try readFile(allocator, expectations_path);
    defer allocator.free(expectations);

    try expectContains(expectations, "\"PHASE1_BENCH_LIST_SORT_ITERATIONS\": 1000");
    try expectContains(expectations, "\"PHASE1_BENCH_LIST_SORT_CHECKSUM\"");
    try expectContains(expectations, "\"PHASE1_BENCH_LIST_SORT_CHECKSUM\": 10000");
    try expectOrdered(
        expectations,
        "\"PHASE1_BENCH_HWEIGHT_ITERATIONS\": 100000",
        "\"PHASE1_BENCH_LIST_SORT_ITERATIONS\": 1000",
    );
    try expectOrdered(
        expectations,
        "\"PHASE1_BENCH_LIST_SORT_CHECKSUM\"",
        "\"PHASE1_BENCH_RBTREE_CHECKSUM\"",
    );
    try expectCount(expectations, "\"PHASE1_BENCH_LIST_SORT_CHECKSUM\"", 2);
}

test "bench checker fail-closes around list_sort exact checksum" {
    const allocator = testing.allocator;
    const checker = try readFile(allocator, bench_checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "\"PHASE1_BENCH_LIST_SORT_ITERATIONS\": 1000");
    try expectContains(checker, "\"PHASE1_BENCH_LIST_SORT_CHECKSUM\"");
    try expectContains(checker, "LIST_SORT_REQUIRED_EXACT_CHECKSUMS = {\"PHASE1_BENCH_LIST_SORT_CHECKSUM\"}");
    try expectContains(checker, "(\"expectations_checksums_list_sort_exact_required\", LIST_SORT_REQUIRED_EXACT_CHECKSUMS)");
    try expectContains(checker, "(\"missing_list_sort_exact_checksums\", LIST_SORT_REQUIRED_EXACT_CHECKSUMS)");
    try expectContains(checker, "\"PHASE1_BENCH_LIST_SORT_ITERATIONS=1000\"");
    try expectContains(checker, "\"PHASE1_BENCH_LIST_SORT_CHECKSUM=7\"");
    try expectContains(checker, "PHASE1_BENCH_CHECK_SELF_TEST=pass");
    try expectContains(checker, "PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT=");
}
