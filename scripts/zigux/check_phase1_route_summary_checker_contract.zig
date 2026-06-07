const std = @import("std");
const config = @import("config");

fn readSource(allocator: std.mem.Allocator) ![]const u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        config.source_path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn expectContainsOnce(haystack: []const u8, needle: []const u8) !void {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingMarker;
    const rest = haystack[first + needle.len ..];
    try std.testing.expect(std.mem.indexOf(u8, rest, needle) == null);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "route summary checker keeps source contract and exact-line machinery" {
    const source = try readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContainsOnce(source, "\"\"\"Guard the current Phase 1 route-summary packet across closure, Makefile, and workflow.\"\"\"");
    try expectContainsOnce(source, "REQUIRED_FILES = (");
    try expectContainsOnce(source, "EXACT_LINE_MARKERS = {");
    try expectContainsOnce(source, "FORBIDDEN_EXACT_LINES = {");
    try expectContainsOnce(source, "def require_exact_line(text: str, label: str, marker: str) -> list[str]:");
    try expectContainsOnce(source, "def require_absent_line(text: str, label: str, marker: str) -> list[str]:");
    try expectContainsOnce(source, "def collect_failures(root: Path) -> list[str]:");
    try expectContainsOnce(source, "def build_sample_repo(root: Path) -> None:");

    try expectContains(source, "\"Documentation/zigux/README.md\"");
    try expectContains(source, "\"Documentation/zigux/phase1-closure.md\"");
    try expectContains(source, "\"Documentation/zigux/phase1-host-helper-lane-sequencing.md\"");
    try expectContains(source, "\"scripts/zigux/README.md\"");
    try expectContains(source, "\"zigux/tests/README.md\"");
    try expectContains(source, "\"zigux/Makefile\"");
    try expectContains(source, "\".github/workflows/zigux-bootstrap.yml\"");
}

test "route summary checker pins Phase 1 gate handoff markers" {
    const source = try readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContainsOnce(source, "- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`");
    try expectContainsOnce(source, "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`");
    try expectContainsOnce(source, "- `scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `.github/workflows/zigux-bootstrap.yml` keep the adjacent Phase 1 route-summary guard explicit beside the narrower reminder packet, so scripts-root follow-through can verify the returned non-Phase-1 Makefile route inventory without promoting the older Phase 1 wrappers back into shipped proof");
    try expectContainsOnce(source, "\"phase1-route-summary:\"");
    try expectContainsOnce(source, "\"run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test\"");
    try expectContainsOnce(source, "\"run: python3 scripts/zigux/check-phase1-route-summary-counts.py\"");
    try expectContainsOnce(source, "\"run: python3 scripts/zigux/check-phase1-bench.py --self-test\"");
    try expectContainsOnce(source, "\"run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\"");

    try expectOrder(
        source,
        "\"run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test\"",
        "\"run: python3 scripts/zigux/check-phase1-route-summary-counts.py\"",
    );
    try expectOrder(
        source,
        "\"run: python3 scripts/zigux/check-phase1-route-summary-counts.py\"",
        "\"run: python3 scripts/zigux/check-phase1-bench.py --self-test\"",
    );
    try expectOrder(
        source,
        "\"run: python3 scripts/zigux/check-phase1-bench.py --self-test\"",
        "\"run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\"",
    );
}

test "route summary checker preserves forbidden old Phase 1 wrapper guard" {
    const source = try readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContainsOnce(source, "\"phase1-validate:\"");
    try expectContainsOnce(source, "\"phase1-test:\"");
    try expectContainsOnce(source, "\"phase1-bench:\"");
    try expectContainsOnce(source, "\"phase1:\"");
    try expectContains(source, "It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`");
    try expectContains(source, "older Phase 1 wrapper names remain historical packet members rather than active closure proof");
}

test "route summary checker keeps self-test and public result envelope" {
    const source = try readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContainsOnce(source, "def run_self_test() -> int:");
    try expectContainsOnce(source, "cases = [(\"success\", None)]");
    try expectContainsOnce(source, "cases.append((f\"missing_file:{relative_path}\", (\"missing_file\", relative_path)))");
    try expectContainsOnce(source, "cases.append((f\"missing_marker:{relative_path}\", (\"remove\", relative_path, marker)))");
    try expectContainsOnce(source, "cases.append((f\"duplicate_marker:{relative_path}\", (\"duplicate\", relative_path, marker)))");
    try expectContainsOnce(source, "cases.append((f\"forbidden_marker:{relative_path}\", (\"forbidden\", relative_path, marker)))");
    try expectContainsOnce(source, "print(\"PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=pass\")");
    try expectContainsOnce(source, "print(f\"PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST_CASE_COUNT={len(cases)}\")");
    try expectContainsOnce(source, "print(\"PHASE1_ROUTE_SUMMARY_COUNTS=fail\")");
    try expectContainsOnce(source, "print(\"PHASE1_ROUTE_SUMMARY_COUNTS=pass\")");
    try expectContainsOnce(source, "PHASE1_ROUTE_SUMMARY_COUNTS_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}");
    try expectContainsOnce(source, "PHASE1_ROUTE_SUMMARY_COUNTS_REQUIRED_MARKER_COUNT=");
}
