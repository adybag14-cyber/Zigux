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

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectExactLineCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), needle)) count += 1;
    }
    try std.testing.expectEqual(expected, count);
}

fn expectRouteInPolicy(policy: []const u8, route: []const u8) !void {
    var buffer: [128]u8 = undefined;
    const marker = try std.fmt.bufPrint(&buffer, "\"{s}\"", .{route});
    try expectContains(policy, marker);
}

fn expectRouteInNotes(notes: []const u8, route: []const u8) !void {
    var buffer: [128]u8 = undefined;
    const marker = try std.fmt.bufPrint(&buffer, "`make -C zigux {s}`", .{route});
    try expectContains(notes, marker);
}

fn expectWorkflowRunsRouteOnce(workflow: []const u8, route: []const u8) !void {
    var buffer: [128]u8 = undefined;
    const marker = try std.fmt.bufPrint(&buffer, "run: make -C zigux {s}", .{route});
    try expectExactLineCount(workflow, marker, 1);
}

fn expectMakefileDefinesRouteOnce(makefile: []const u8, route: []const u8) !void {
    var buffer: [128]u8 = undefined;
    const marker = try std.fmt.bufPrint(&buffer, "{s}:", .{route});
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, makefile, '\n');
    while (lines.next()) |line| {
        if (std.mem.startsWith(u8, std.mem.trim(u8, line, " \t\r"), marker)) count += 1;
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

test "phase 2 bootstrap workflow routes stay wired through policy, docs, workflow, make, and checker surfaces" {
    const policy = try readRepoFile("scripts/zigux/zig-toolchain-policy.json", 16 * 1024);
    defer std.testing.allocator.free(policy);
    const notes = try readRepoFile("Documentation/zigux/phase2-toolchain-bootstrap-notes.md", 96 * 1024);
    defer std.testing.allocator.free(notes);
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml", 96 * 1024);
    defer std.testing.allocator.free(workflow);
    const makefile = try readRepoFile("zigux/Makefile", 96 * 1024);
    defer std.testing.allocator.free(makefile);
    const checker = try readRepoFile("scripts/zigux/check-phase2-bootstrap-workflow-routes.py", 32 * 1024);
    defer std.testing.allocator.free(checker);

    try expectContains(policy, "\"required_make_routes\"");
    try expectContains(policy, "\"channel\": \"0.17.0-dev.87+9b177a7d2\"");
    try expectContains(policy, "\"archive_target_scope\"");
    try expectContains(policy, "\"x86_64-linux\"");

    try expectContains(checker, "EXPECTED_SELF_TEST_CASE_COUNT = 24");
    try expectContains(checker, "AGGREGATE_ROUTE = \"phase2\"");
    try expectContains(checker, "workflow_lines(routes)");
    try expectContains(checker, "makefile_rule_lines(routes)");
    try expectContains(checker, "note_markers(routes)");
    try expectContains(checker, "load_required_routes(root)");
    try expectContains(checker, "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES=pass");
    try expectContains(makefile, "check-phase2-bootstrap-workflow-routes.py --self-test");
    try expectContains(makefile, "check-phase2-bootstrap-workflow-routes.py");

    for (required_routes) |route| {
        try expectRouteInPolicy(policy, route);
        try expectRouteInNotes(notes, route);
        try expectWorkflowRunsRouteOnce(workflow, route);
        try expectMakefileDefinesRouteOnce(makefile, route);
    }

    try expectRouteInNotes(notes, "phase2");
    try expectWorkflowRunsRouteOnce(workflow, "phase2");
    try expectExactLineCount(makefile, "phase2: phase2-validate", 1);
    try expectContains(makefile, ".PHONY:");
    try expectContains(makefile, "phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2");
}
