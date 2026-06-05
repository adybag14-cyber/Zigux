const std = @import("std");

const GateFile = struct {
    path: []const u8,
    contents: []u8,
};

const required_routes = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
};

const workflow_route_lines = [_][]const u8{
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-validate",
    "run: make -C zigux phase2",
};

const makefile_rule_lines = [_][]const u8{
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig: phase2-toolchain",
    "phase2-cross:",
    "phase2-genksyms: phase2-toolchain",
    "phase2-fixdep: phase2-toolchain",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "phase2: phase2-validate",
};

fn readFile(path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn loadGateFile(path: []const u8, limit: usize) !GateFile {
    return .{
        .path = path,
        .contents = try readFile(path, limit),
    };
}

fn unloadGateFile(file: GateFile) void {
    std.testing.allocator.free(file.contents);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectFileContains(file: GateFile, needle: []const u8) !void {
    _ = file.path;
    try expectContains(file.contents, needle);
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

fn expectExactLineOnce(file: GateFile, line: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countExactLines(file.contents, line));
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.EarlierMarkerMissing;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.LaterMarkerMissing;
    try std.testing.expect(earlier_index < later_index);
}

fn exactLineIndex(haystack: []const u8, needle: []const u8) ?usize {
    var offset: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), needle)) {
            return offset;
        }
        offset += line.len + 1;
    }
    return null;
}

fn expectExactLineBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = exactLineIndex(haystack, earlier) orelse return error.EarlierMarkerMissing;
    const later_index = exactLineIndex(haystack, later) orelse return error.LaterMarkerMissing;
    try std.testing.expect(earlier_index < later_index);
}

test "phase2 bootstrap workflow routes checker keeps public contract markers" {
    const checker = try loadGateFile("scripts/zigux/check-phase2-bootstrap-workflow-routes.py", 192 * 1024);
    defer unloadGateFile(checker);

    const checker_markers = [_][]const u8{
        "Guard the current Phase 2 bootstrap make-route packet.",
        "EXPECTED_SELF_TEST_CASE_COUNT = 24",
        "TOOLCHAIN_POLICY = Path(\"scripts/zigux/zig-toolchain-policy.json\")",
        "BOOTSTRAP_NOTES = Path(\"Documentation/zigux/phase2-toolchain-bootstrap-notes.md\")",
        "WORKFLOW = Path(\".github/workflows/zigux-bootstrap.yml\")",
        "MAKEFILE = Path(\"zigux/Makefile\")",
        "AGGREGATE_ROUTE = \"phase2\"",
        "required_make_routes",
        "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES=pass",
        "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_REQUIRED_ROUTE_COUNT",
        "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_WORKFLOW_LINE_COUNT",
        "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_MAKEFILE_LINE_COUNT",
        "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_SELF_TEST=pass",
        "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_SELF_TEST_CASE_COUNT",
        "missing_file:",
        "invalid_policy:",
        "expected_once:actual_count=",
        "phase2-future",
    };
    inline for (checker_markers) |marker| {
        try expectFileContains(checker, marker);
    }

    inline for (required_routes) |route| {
        try expectContains(checker.contents, route);
    }
    inline for (workflow_route_lines) |line| {
        try expectContains(checker.contents, line);
    }
    inline for (makefile_rule_lines) |line| {
        try expectContains(checker.contents, line);
    }
}

test "phase2 bootstrap workflow routes stay exposed through closure notes and manifest" {
    const closure_note = try loadGateFile("Documentation/zigux/phase2-closure.md", 128 * 1024);
    defer unloadGateFile(closure_note);
    const bootstrap_note = try loadGateFile("Documentation/zigux/phase2-toolchain-bootstrap-notes.md", 128 * 1024);
    defer unloadGateFile(bootstrap_note);
    const manifest = try loadGateFile("zigux/tests/fixtures/phase2_tool_manifest.json", 512 * 1024);
    defer unloadGateFile(manifest);
    const policy = try loadGateFile("scripts/zigux/zig-toolchain-policy.json", 64 * 1024);
    defer unloadGateFile(policy);

    const checker_command = "python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py";
    try expectFileContains(closure_note, checker_command);
    try expectFileContains(manifest, "scripts/zigux/check-phase2-bootstrap-workflow-routes.py");
    try expectFileContains(manifest, "\"make_wrappers\"");
    try expectFileContains(policy, "\"required_make_routes\"");

    inline for (required_routes) |route| {
        const make_prefix = "make -C zigux ";
        var buffer: [64]u8 = undefined;
        const route_marker = try std.fmt.bufPrint(&buffer, "{s}{s}", .{ make_prefix, route });
        try expectContains(bootstrap_note.contents, route_marker);
        try expectContains(manifest.contents, route_marker);
        try expectContains(policy.contents, route);
    }

    try expectFileContains(bootstrap_note, "`make -C zigux phase2`");
    try expectFileContains(closure_note, "PHASE2_SHARED_MAKE_ROUTES=");
    try expectFileContains(closure_note, "PHASE2_SHARED_TOOLING_CHECKERS=");
    try expectFileContains(manifest, "\"repo_reality_gaps\": []");
}

test "phase2 bootstrap workflow routes stay wired through workflow and Makefile" {
    const workflow = try loadGateFile(".github/workflows/zigux-bootstrap.yml", 768 * 1024);
    defer unloadGateFile(workflow);
    const makefile = try loadGateFile("zigux/Makefile", 512 * 1024);
    defer unloadGateFile(makefile);

    const workflow_checker_selftest = "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py --self-test";
    const workflow_checker_live = "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py";
    try expectExactLineOnce(workflow, workflow_checker_selftest);
    try expectExactLineOnce(workflow, workflow_checker_live);
    try expectExactLineBefore(workflow.contents, workflow_checker_selftest, workflow_checker_live);

    inline for (workflow_route_lines) |line| {
        try expectExactLineOnce(workflow, line);
    }
    try expectBefore(workflow.contents, workflow_checker_live, "run: make -C zigux phase2-toolchain");
    try expectExactLineBefore(workflow.contents, "run: make -C zigux phase2-validate", "run: make -C zigux phase2");

    inline for (makefile_rule_lines) |line| {
        try expectExactLineOnce(makefile, line);
    }
    try expectExactLineOnce(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py --self-test");
    try expectExactLineOnce(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py");
    try expectFileContains(makefile, ".PHONY:");
    inline for (required_routes) |route| {
        try expectFileContains(makefile, route);
    }
}
