const std = @import("std");

const validator_path = "scripts/zigux/validate-phase2-closure.py";
const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const self_test_markers = [_][]const u8{
    "def run_self_test() -> int:",
    "PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass",
    "PHASE2_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT={checks_run}",
    "build_self_test_root(root)",
    "assert collect_issues(root) == []",
};

const fail_closed_issue_markers = [_][]const u8{
    "MISSING_MANIFEST_SURFACE",
    "MISSING_CLOSURE_LINE",
    "MISSING_CLOSURE_MARKER",
    "UNEXPECTED_MANIFEST_GAPS",
    "fixture_roster:zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json",
    "PHASE2_SHARED_TOOLING_CHECKERS=",
    "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=",
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse {
        try std.testing.expect(false);
        return;
    };
    const later_index = std.mem.indexOf(u8, haystack, later) orelse {
        try std.testing.expect(false);
        return;
    };
    try std.testing.expect(earlier_index < later_index);
}

fn exactLineIndex(haystack: []const u8, needle: []const u8) ?usize {
    var index: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| : (index += line.len + 1) {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t"), needle)) {
            return index;
        }
    }
    return null;
}

fn expectExactLineBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = exactLineIndex(haystack, earlier) orelse {
        try std.testing.expect(false);
        return;
    };
    const later_index = exactLineIndex(haystack, later) orelse {
        try std.testing.expect(false);
        return;
    };
    try std.testing.expect(earlier_index < later_index);
}

test "phase 2 closure validator exposes a deterministic self-test envelope" {
    const validator = try readRepoFile(validator_path, 1024 * 1024);
    defer std.testing.allocator.free(validator);

    for (self_test_markers) |marker| {
        try expectContains(validator, marker);
    }

    try expectBefore(
        validator,
        "PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass",
        "PHASE2_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT={checks_run}",
    );
}

test "phase 2 closure validator self-test keeps fail-closed issue vocabulary" {
    const validator = try readRepoFile(validator_path, 1024 * 1024);
    defer std.testing.allocator.free(validator);

    for (fail_closed_issue_markers) |marker| {
        try expectContains(validator, marker);
    }

    try expectBefore(
        validator,
        "\"MISSING_CLOSURE_LINE\",",
        "\"PHASE2_SHARED_TOOLING_CHECKERS=\"",
    );
    try expectBefore(
        validator,
        "\"MISSING_CLOSURE_MARKER\",",
        "\"scripts/zigux/check-phase2-tool-manifest.py\"",
    );
}

test "phase 2 closure validator CLI keeps self-test before normal validation" {
    const validator = try readRepoFile(validator_path, 1024 * 1024);
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "parser.add_argument(\"--self-test\", action=\"store_true\"");
    try expectBefore(validator, "if args.self_test:", "issues = collect_issues(args.root.resolve())");
    try expectBefore(validator, "return run_self_test()", "PHASE2_CLOSURE_VALIDATION=pass");
    try expectContains(validator, "PHASE2_CLOSURE_REMAINING_GAPS=");
}

test "bootstrap workflow runs phase 2 closure self-test before live closure check" {
    const workflow = try readRepoFile(workflow_path, 1024 * 1024);
    defer std.testing.allocator.free(workflow);

    const aggregate_make = "Run current Phase 2 aggregate make route";
    const validate_phase2 = "Validate current Phase 2 tool packet";
    const self_test_step = "Self-test current Phase 2 closure validator";
    const check_step = "Check current Phase 2 closure packet";
    const self_test_command = "run: python3 scripts/zigux/validate-phase2-closure.py --self-test";
    const check_command = "run: python3 scripts/zigux/validate-phase2-closure.py";

    try expectBefore(workflow, aggregate_make, validate_phase2);
    try expectBefore(workflow, validate_phase2, self_test_step);
    try expectBefore(workflow, self_test_step, check_step);
    try expectExactLineBefore(workflow, self_test_command, check_command);
}
