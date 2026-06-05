const std = @import("std");
const contract_options = @import("contract_options");

const ContractPaths = struct {
    workflow: []const u8,
    route_summary_checker: []const u8,
    tests_readme: []const u8,
};

const configured_paths = ContractPaths{
    .workflow = contract_options.workflow_path,
    .route_summary_checker = contract_options.route_summary_checker_path,
    .tests_readme = contract_options.tests_readme_path,
};

const ordered_workflow_steps = [_][]const u8{
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    "run: python3 scripts/zigux/check-phase1-bench.py",
    "run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test",
    "run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py",
    "run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
    "run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
    "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
};

const checker_markers = [_][]const u8{
    "\"run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test\"",
    "\"run: python3 scripts/zigux/check-phase1-route-summary-counts.py\"",
    "\"run: python3 scripts/zigux/check-phase1-bench.py --self-test\"",
    "\"run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\"",
    "\"phase1-route-summary:\"",
    "\"phase1-validate:\"",
    "\"phase1-test:\"",
    "\"phase1-bench:\"",
    "\"phase1:\"",
    "PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=pass",
    "PHASE1_ROUTE_SUMMARY_COUNTS=pass",
};

const tests_readme_markers = [_][]const u8{
    "current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "older Phase 1 wrapper names remain historical packet members rather than active tests-root proof",
    "the thirteen helper ports remain closed through the committed manifest",
    "only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
};

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    return count;
}

fn expectOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(haystack, needle));
}

fn countExactLines(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), needle)) {
            count += 1;
        }
    }
    return count;
}

fn expectLineOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countExactLines(haystack, needle));
}

fn expectOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var previous: usize = 0;
    for (needles, 0..) |needle, ordinal| {
        const start = if (ordinal == 0) 0 else previous + 1;
        const index = std.mem.indexOfPos(u8, haystack, start, needle) orelse return error.MissingOrderedMarker;
        try std.testing.expect(index >= previous);
        previous = index;
    }
}

fn validateWorkflow(text: []const u8) !void {
    for (ordered_workflow_steps) |step| {
        try expectLineOnce(text, step);
    }
    try expectOrdered(text, &ordered_workflow_steps);
}

fn validateRouteSummaryChecker(text: []const u8) !void {
    for (checker_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, text, marker) != null);
    }
}

fn validateTestsReadme(text: []const u8) !void {
    for (tests_readme_markers) |marker| {
        try expectOnce(text, marker);
    }
}

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(1024 * 1024),
    );
}

pub fn validateRepository(paths: ContractPaths, allocator: std.mem.Allocator) !void {
    const workflow = try readFile(allocator, paths.workflow);
    defer allocator.free(workflow);
    const route_summary_checker = try readFile(allocator, paths.route_summary_checker);
    defer allocator.free(route_summary_checker);
    const tests_readme = try readFile(allocator, paths.tests_readme);
    defer allocator.free(tests_readme);

    try validateWorkflow(workflow);
    try validateRouteSummaryChecker(route_summary_checker);
    try validateTestsReadme(tests_readme);
}

test "phase1 route summary gate stays ordered before shared smoke" {
    const workflow =
        \\run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test
        \\run: python3 scripts/zigux/check-phase1-route-summary-counts.py
        \\run: python3 scripts/zigux/check-phase1-bench.py --self-test
        \\run: python3 scripts/zigux/check-phase1-bench.py
        \\run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test
        \\run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py
        \\run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
        \\run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py
        \\run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test
        \\run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py
        \\run: python3 scripts/zigux/validate-phase1-closure.py --self-test
        \\run: python3 scripts/zigux/validate-phase1-closure.py
        \\run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig
        \\
    ;
    try validateWorkflow(workflow);
}

test "phase1 route summary checker still owns the workflow and absent make-route markers" {
    const checker =
        \\"run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test"
        \\"run: python3 scripts/zigux/check-phase1-route-summary-counts.py"
        \\"run: python3 scripts/zigux/check-phase1-bench.py --self-test"
        \\"run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig"
        \\"phase1-route-summary:"
        \\"phase1-validate:"
        \\"phase1-test:"
        \\"phase1-bench:"
        \\"phase1:"
        \\PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=pass
        \\PHASE1_ROUTE_SUMMARY_COUNTS=pass
        \\
    ;
    try validateRouteSummaryChecker(checker);
}

test "tests readme keeps shared smoke route and historical wrapper boundary explicit" {
    const readme =
        \\current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
        \\older Phase 1 wrapper names remain historical packet members rather than active tests-root proof
        \\the thirteen helper ports remain closed through the committed manifest
        \\only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`
        \\
    ;
    try validateTestsReadme(readme);
}

test "live repository Phase 1 route summary and shared smoke workflow contract" {
    try validateRepository(configured_paths, std.testing.allocator);
}
