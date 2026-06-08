const std = @import("std");

const checker_path = "scripts/zigux/check-phase2-cross.py";
const makefile_path = "zigux/Makefile";
const workflow_path = ".github/workflows/zigux-bootstrap.yml";

fn readFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(512 * 1024),
    );
}

fn countTrimmedLines(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), needle)) {
            count += 1;
        }
    }
    return count;
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOfPos(u8, haystack, before_index + before.len, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "direct cross checker pins self-test footer count" {
    const checker = try readFile(checker_path);
    defer std.testing.allocator.free(checker);

    try requireContains(checker, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try requireContains(checker, "assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT");
    try requireContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass");
    try requireContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT={checks_run}");
    try requireContains(checker, "PHASE2_DIRECT_CROSS_ROUTE=pass");
    try requireContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT=");
    try requireContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT=");
    try requireContains(checker, "parser.add_argument(\"--self-test\"");
}

test "phase2-cross make route runs direct self-test before live check" {
    const makefile = try readFile(makefile_path);
    defer std.testing.allocator.free(makefile);

    try requireOrdered(
        makefile,
        "phase2-cross:",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
    );
    try requireOrdered(
        makefile,
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    );
    try requireOrdered(
        makefile,
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test",
    );
    try std.testing.expectEqual(@as(usize, 1), countTrimmedLines(
        makefile,
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
    ));
}

test "bootstrap workflow keeps direct cross self-test before packet check" {
    const workflow = try readFile(workflow_path);
    defer std.testing.allocator.free(workflow);

    try requireOrdered(
        workflow,
        "Self-test current Phase 2 cross checker",
        "Check current Phase 2 direct cross-route packet",
    );
    try requireOrdered(
        workflow,
        "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
        "run: python3 scripts/zigux/check-phase2-cross.py",
    );
    try requireOrdered(
        workflow,
        "Check current Phase 2 direct cross-route packet",
        "Run current Phase 2 cross make route",
    );
    try std.testing.expectEqual(@as(usize, 1), countTrimmedLines(
        workflow,
        "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    ));
}
