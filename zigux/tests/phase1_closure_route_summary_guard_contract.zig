const std = @import("std");

const RepoFile = struct {
    path: []const u8,
    text: []const u8,
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) !RepoFile {
    const text = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(1024 * 1024),
    );
    return .{ .path = path, .text = text };
}

fn expectContains(file: RepoFile, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, file.text, needle) != null);
}

fn expectContainsOnce(file: RepoFile, needle: []const u8) !void {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, file.text[cursor..], needle)) |offset| {
        count += 1;
        cursor += offset + needle.len;
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

fn expectLineOnce(file: RepoFile, needle: []const u8) !void {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, file.text, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t"), needle)) {
            count += 1;
        }
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

fn expectAbsent(file: RepoFile, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, file.text, needle) == null);
}

fn lineIndex(file: RepoFile, needle: []const u8) !usize {
    var index: usize = 0;
    var lines = std.mem.splitScalar(u8, file.text, '\n');
    while (lines.next()) |line| : (index += 1) {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t"), needle)) {
            return index;
        }
    }
    return error.MissingLineMarker;
}

fn expectLineBefore(file: RepoFile, before: []const u8, after: []const u8) !void {
    const before_index = try lineIndex(file, before);
    const after_index = try lineIndex(file, after);
    try std.testing.expect(before_index < after_index);
}

test "phase1 closure note keeps route-summary guard adjacent to narrow closure validation" {
    const allocator = std.testing.allocator;
    const closure = try readRepoFile(allocator, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(closure.text);
    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase1-closure.py");
    defer allocator.free(validator.text);

    try expectContainsOnce(closure, "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`");
    try expectContainsOnce(closure, "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`");
    try expectContainsOnce(closure, "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`");
    try expectContains(closure, "route-summary checker stays an adjacent workflow and Makefile guard");
    try expectContains(closure, "It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`");
    try expectAbsent(closure, "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`");

    try expectContains(validator, "ROUTE_SUMMARY_CHECKER_REL = Path(\"scripts/zigux/check-phase1-route-summary-counts.py\")");
    try expectContains(validator, "\"route_summary_guard\": \"`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`\"");
    try expectContains(validator, "FORBIDDEN_MAKEFILE_MARKERS");
    try expectContains(validator, "\"phase1-validate:\"");
}

test "route-summary checker pins docs scripts tests makefile and workflow packet" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase1-route-summary-counts.py");
    defer allocator.free(checker.text);
    const makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile.text);

    try expectContains(checker, "Guard the current Phase 1 route-summary packet across closure, Makefile, and workflow.");
    try expectContains(checker, "\"Documentation/zigux/phase1-closure.md\"");
    try expectContains(checker, "\"scripts/zigux/README.md\"");
    try expectContains(checker, "\"zigux/tests/README.md\"");
    try expectContains(checker, "\"zigux/Makefile\"");
    try expectContains(checker, "\".github/workflows/zigux-bootstrap.yml\"");
    try expectContains(checker, "\"PHASE1_ROUTE_SUMMARY_COUNTS=pass\"");
    try expectContains(checker, "\"PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=pass\"");
    try expectContains(checker, "\"PHASE1_ROUTE_SUMMARY_COUNTS_REQUIRED_MARKER_COUNT=\"");
    try expectContains(checker, "\"phase1-route-summary:\"");
    try expectContains(checker, "\"phase1-validate:\"");
    try expectContains(checker, "\"phase1-test:\"");
    try expectContains(checker, "\"phase1-bench:\"");

    try expectContainsOnce(makefile, "phase1-route-summary:");
    try expectAbsent(makefile, "\nphase1-validate:");
    try expectAbsent(makefile, "\nphase1-test:");
    try expectAbsent(makefile, "\nphase1-bench:");
}

test "workflow runs route summary before bench and closure checks" {
    const allocator = std.testing.allocator;
    const workflow = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow.text);

    try expectLineOnce(workflow, "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test");
    try expectLineOnce(workflow, "run: python3 scripts/zigux/check-phase1-route-summary-counts.py");
    try expectLineOnce(workflow, "run: python3 scripts/zigux/check-phase1-bench.py --self-test");
    try expectLineOnce(workflow, "run: python3 scripts/zigux/validate-phase1-closure.py --self-test");
    try expectLineOnce(workflow, "run: python3 scripts/zigux/validate-phase1-closure.py");
    try expectLineBefore(workflow, "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test", "run: python3 scripts/zigux/check-phase1-route-summary-counts.py");
    try expectLineBefore(workflow, "run: python3 scripts/zigux/check-phase1-route-summary-counts.py", "run: python3 scripts/zigux/check-phase1-bench.py --self-test");
    try expectLineBefore(workflow, "run: python3 scripts/zigux/check-phase1-bench.py --self-test", "run: python3 scripts/zigux/validate-phase1-closure.py --self-test");
}

test "shared tests-root still exposes only the narrow Phase 1 smoke route" {
    const allocator = std.testing.allocator;
    const build_root = try readRepoFile(allocator, "zigux/tests/build.zig");
    defer allocator.free(build_root.text);

    try expectContains(build_root, "phase1-host-tools-smoke");
    try expectContains(build_root, "Run the shared Phase 1 host-tools smoke anchor from zigux/tests");
    try expectContains(build_root, "phase1-string-direct-anchor");
    try expectContains(build_root, "phase1_host_tools_smoke.zig");
    try expectAbsent(build_root, "phase1-validate");
    try expectAbsent(build_root, "phase1-bench");
}
