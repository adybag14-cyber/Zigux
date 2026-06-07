const std = @import("std");

const shared_tooling_commands = [_][]const u8{
    "python3 scripts/zigux/check-phase2-tool-manifest.py",
    "python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "python3 scripts/zigux/check-phase2-cross.py",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "python3 scripts/zigux/check-fixdep-diff.py",
};

const shared_tooling_paths = [_][]const u8{
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
};

const shared_tooling_line =
    "PHASE2_SHARED_TOOLING_CHECKERS=python3 scripts/zigux/check-phase2-tool-manifest.py,python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py,python3 scripts/zigux/check-phase2-artifact-tools-manifest.py,python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py,python3 scripts/zigux/check-phase2-cross.py,python3 scripts/zigux/check-phase2-fixdep-gate.py,python3 scripts/zigux/check-fixdep-diff.py";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectQuotedContains(haystack: []const u8, marker: []const u8) !void {
    var quoted_buffer: [256]u8 = undefined;
    const quoted = try std.fmt.bufPrint(&quoted_buffer, "\"{s}\"", .{marker});
    try expectContains(haystack, quoted);
}

fn expectTrimmedLineCount(source: []const u8, expected_line: []const u8, expected_count: usize) !void {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, source, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), expected_line)) {
            count += 1;
        }
    }
    try std.testing.expectEqual(expected_count, count);
}

test "phase2 closure note keeps the shared tooling checker line exact" {
    const closure_note = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase2-closure.md");
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, shared_tooling_line);
    for (shared_tooling_commands) |command| {
        try expectContains(closure_note, command);
    }
}

test "phase2 closure validator derives the same shared tooling line" {
    const validator = try readRepoFile(std.testing.allocator, "scripts/zigux/validate-phase2-closure.py");
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "SHARED_TOOLING_COMMANDS = (");
    try expectContains(validator, "expected_shared_tooling_line = \"PHASE2_SHARED_TOOLING_CHECKERS=\"");
    try expectContains(validator, "issues.append((\"MISSING_CLOSURE_LINE\", expected_shared_tooling_line))");
    for (shared_tooling_commands) |command| {
        try expectQuotedContains(validator, command);
    }
}

test "phase2 tool manifest keeps shared tooling paths visible in checker surfaces" {
    const manifest = try readRepoFile(std.testing.allocator, "zigux/tests/fixtures/phase2_tool_manifest.json");
    defer std.testing.allocator.free(manifest);

    try expectContains(manifest, "\"checkers\": [");
    for (shared_tooling_paths) |path| {
        try expectQuotedContains(manifest, path);
    }
}

test "scripts and tests readmes both name the shared tooling packet" {
    const scripts_readme = try readRepoFile(std.testing.allocator, "scripts/zigux/README.md");
    defer std.testing.allocator.free(scripts_readme);
    const tests_readme = try readRepoFile(std.testing.allocator, "zigux/tests/README.md");
    defer std.testing.allocator.free(tests_readme);

    try expectContains(scripts_readme, "Phase 2 flow - the current scripts-root bridge packet");
    try expectContains(tests_readme, "current direct-readback Phase 2 kconfig, genksyms, and fixdep packet");

    for (shared_tooling_paths) |path| {
        try expectContains(scripts_readme, path);
        try expectContains(tests_readme, path);
    }

    try expectTrimmedLineCount(tests_readme, "* `scripts/zigux/check-phase2-tool-manifest.py`", 1);
    try expectTrimmedLineCount(tests_readme, "* `scripts/zigux/check-phase2-bootstrap-workflow-routes.py`", 1);
    try expectTrimmedLineCount(tests_readme, "* `scripts/zigux/check-phase2-artifact-tools-manifest.py`", 1);
}
