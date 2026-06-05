const std = @import("std");

const required_routes = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
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

fn requireExactLineOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countExactLines(haystack, needle));
}

fn requireExactLineOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    var before_index: ?usize = null;
    var after_index: ?usize = null;
    var line_index: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| : (line_index += 1) {
        const trimmed = std.mem.trim(u8, line, " \t\r");
        if (before_index == null and std.mem.eql(u8, trimmed, before)) {
            before_index = line_index;
        }
        if (after_index == null and std.mem.eql(u8, trimmed, after)) {
            after_index = line_index;
        }
    }

    try std.testing.expect(before_index != null);
    try std.testing.expect(after_index != null);
    try std.testing.expect(before_index.? < after_index.?);
}

test "workflow route checker keeps policy driven bootstrap surfaces explicit" {
    const allocator = std.testing.allocator;
    const checker_source = try readRepoFile(allocator, "scripts/zigux/check-phase2-bootstrap-workflow-routes.py");
    defer allocator.free(checker_source);

    try requireContains(checker_source, "Guard the current Phase 2 bootstrap make-route packet.");
    try requireContains(checker_source, "TOOLCHAIN_POLICY = Path(\"scripts/zigux/zig-toolchain-policy.json\")");
    try requireContains(checker_source, "BOOTSTRAP_NOTES = Path(\"Documentation/zigux/phase2-toolchain-bootstrap-notes.md\")");
    try requireContains(checker_source, "WORKFLOW = Path(\".github/workflows/zigux-bootstrap.yml\")");
    try requireContains(checker_source, "MAKEFILE = Path(\"zigux/Makefile\")");
    try requireContains(checker_source, "AGGREGATE_ROUTE = \"phase2\"");
    try requireContains(checker_source, "EXPECTED_SELF_TEST_CASE_COUNT = 24");
    try requireContains(checker_source, "def load_required_routes(root: Path) -> tuple[str, ...]:");
    try requireContains(checker_source, "duplicate required_make_routes");
    try requireContains(checker_source, "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES=pass");
}

test "policy docs workflow and makefile expose the same phase2 route roster" {
    const allocator = std.testing.allocator;
    const policy_source = try readRepoFile(allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer allocator.free(policy_source);
    const bootstrap_notes = try readRepoFile(allocator, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    defer allocator.free(bootstrap_notes);
    const workflow_source = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow_source);
    const makefile_source = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile_source);

    for (required_routes) |route| {
        try requireContains(policy_source, route);
        try requireContains(bootstrap_notes, route);
        try requireContains(workflow_source, route);
        try requireContains(makefile_source, route);
    }

    try requireContains(bootstrap_notes, "`make -C zigux phase2`");
    try requireExactLineOnce(workflow_source, "run: make -C zigux phase2-toolchain");
    try requireExactLineOnce(workflow_source, "run: make -C zigux phase2-tools");
    try requireExactLineOnce(workflow_source, "run: make -C zigux phase2-kconfig");
    try requireExactLineOnce(workflow_source, "run: make -C zigux phase2-cross");
    try requireExactLineOnce(workflow_source, "run: make -C zigux phase2-genksyms");
    try requireExactLineOnce(workflow_source, "run: make -C zigux phase2-fixdep");
    try requireExactLineOnce(workflow_source, "run: make -C zigux phase2-validate");
    try requireExactLineOnce(workflow_source, "run: make -C zigux phase2");
}

test "workflow and Makefile keep the route checker in the phase2 tools packet" {
    const allocator = std.testing.allocator;
    const workflow_source = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow_source);
    const makefile_source = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile_source);

    try requireExactLineOrder(
        workflow_source,
        "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py --self-test",
        "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    );
    try requireExactLineOrder(
        workflow_source,
        "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
        "run: make -C zigux phase2-toolchain",
    );
    try requireExactLineOrder(
        makefile_source,
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py",
    );
    try requireExactLineOrder(
        makefile_source,
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py --self-test",
    );
}

test "phase2 aggregate route stays closed to the current required route packet" {
    const allocator = std.testing.allocator;
    const checker_source = try readRepoFile(allocator, "scripts/zigux/check-phase2-bootstrap-workflow-routes.py");
    defer allocator.free(checker_source);
    const policy_source = try readRepoFile(allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer allocator.free(policy_source);
    const workflow_source = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow_source);
    const makefile_source = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile_source);

    try requireContains(makefile_source, ".PHONY:");
    try requireContains(makefile_source, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
    try requireContains(makefile_source, "phase2: phase2-validate");
    try requireContains(checker_source, "phase2-future");
    try requireNotContains(policy_source, "phase2-future");
    try requireNotContains(workflow_source, "run: make -C zigux phase2-future");
    try requireNotContains(makefile_source, "phase2-future:");
}
