const std = @import("std");

const default_source_path = "scripts/zigux/check-phase1-route-summary-counts.py";

const RequiredMarker = struct {
    needle: []const u8,
    min_count: usize = 1,
};

const required_markers = [_]RequiredMarker{
    .{ .needle = "\"\"\"Guard the current Phase 1 route-summary packet across closure, Makefile, and workflow.\"\"\"" },
    .{ .needle = "REQUIRED_FILES = (" },
    .{ .needle = "EXACT_LINE_MARKERS = {" },
    .{ .needle = "FORBIDDEN_EXACT_LINES = {" },
    .{ .needle = "\"Documentation/zigux/README.md\"," },
    .{ .needle = "\"Documentation/zigux/phase1-closure.md\"," },
    .{ .needle = "\"Documentation/zigux/phase1-host-helper-lane-sequencing.md\"," },
    .{ .needle = "\"scripts/zigux/README.md\"," },
    .{ .needle = "\"zigux/tests/README.md\"," },
    .{ .needle = "\"zigux/Makefile\"," },
    .{ .needle = "\".github/workflows/zigux-bootstrap.yml\"," },
    .{ .needle = "\"phase1-route-summary:\"" },
    .{ .needle = "\"phase1-validate:\"" },
    .{ .needle = "\"phase1-test:\"" },
    .{ .needle = "\"phase1-bench:\"" },
    .{ .needle = "\"phase1:\"" },
    .{ .needle = "def require_exact_line(text: str, label: str, marker: str) -> list[str]:" },
    .{ .needle = "def require_absent_line(text: str, label: str, marker: str) -> list[str]:" },
    .{ .needle = "sum(1 for line in text.splitlines() if line.strip() == marker.strip())", .min_count = 2 },
    .{ .needle = "cases.append((f\"missing_file:{relative_path}\", (\"missing_file\", relative_path)))" },
    .{ .needle = "cases.append((f\"missing_marker:{relative_path}\", (\"remove\", relative_path, marker)))" },
    .{ .needle = "cases.append((f\"duplicate_marker:{relative_path}\", (\"duplicate\", relative_path, marker)))" },
    .{ .needle = "cases.append((f\"forbidden_marker:{relative_path}\", (\"forbidden\", relative_path, marker)))" },
    .{ .needle = "print(\"PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=pass\")" },
    .{ .needle = "print(f\"PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST_CASE_COUNT={len(cases)}\")" },
    .{ .needle = "print(\"PHASE1_ROUTE_SUMMARY_COUNTS=pass\")" },
    .{ .needle = "PHASE1_ROUTE_SUMMARY_COUNTS_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}" },
    .{ .needle = "PHASE1_ROUTE_SUMMARY_COUNTS_REQUIRED_MARKER_COUNT=" },
    .{ .needle = "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test" },
    .{ .needle = "run: python3 scripts/zigux/check-phase1-route-summary-counts.py" },
    .{ .needle = "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig" },
};

fn readSource(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |found| {
        count += 1;
        offset = found + needle.len;
    }
    return count;
}

fn requireMinimumCount(source: []const u8, marker: RequiredMarker) !void {
    const actual = countOccurrences(source, marker.needle);
    try std.testing.expect(actual >= marker.min_count);
}

fn requireOrdered(source: []const u8, first: []const u8, second: []const u8) !void {
    const first_pos = std.mem.indexOf(u8, source, first) orelse return error.MissingFirstMarker;
    const second_pos = std.mem.indexOf(u8, source, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_pos < second_pos);
}

test "route-summary checker keeps required source markers" {
    const path = @import("build_options").source_path;
    const source = try readSource(std.testing.allocator, path);
    defer std.testing.allocator.free(source);

    for (required_markers) |marker| {
        try requireMinimumCount(source, marker);
    }
}

test "route-summary checker keeps marker families ordered" {
    const path = @import("build_options").source_path;
    const source = try readSource(std.testing.allocator, path);
    defer std.testing.allocator.free(source);

    try requireOrdered(source, "REQUIRED_FILES = (", "EXACT_LINE_MARKERS = {");
    try requireOrdered(source, "EXACT_LINE_MARKERS = {", "FORBIDDEN_EXACT_LINES = {");
    try requireOrdered(source, "FORBIDDEN_EXACT_LINES = {", "def repo_root(root: str | None) -> Path:");
    try requireOrdered(source, "def collect_failures(root: Path) -> list[str]:", "def run_self_test() -> int:");
    try requireOrdered(source, "if args.self_test:", "PHASE1_ROUTE_SUMMARY_COUNTS=pass");
}

test "route-summary checker public counts stay tied to live rosters" {
    const path = @import("build_options").source_path;
    const source = try readSource(std.testing.allocator, path);
    defer std.testing.allocator.free(source);

    try std.testing.expect(source.len > 1000);
    try std.testing.expect(countOccurrences(source, "REQUIRED_FILES") >= 2);
    try std.testing.expect(countOccurrences(source, "EXACT_LINE_MARKERS") >= 2);
    try std.testing.expect(countOccurrences(source, "FORBIDDEN_EXACT_LINES") >= 1);
    try std.testing.expect(countOccurrences(source, "PHASE1_ROUTE_SUMMARY_COUNTS") >= 5);
}
