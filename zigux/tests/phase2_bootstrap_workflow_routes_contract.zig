const std = @import("std");

const routes = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
};

fn readRepoFile(path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
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

fn expectLineOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countExactLines(haystack, needle));
}

test "bootstrap workflow route checker keeps the current public contract explicit" {
    const checker = try readRepoFile("scripts/zigux/check-phase2-bootstrap-workflow-routes.py");
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "TOOLCHAIN_POLICY = Path(\"scripts/zigux/zig-toolchain-policy.json\")");
    try expectContains(checker, "BOOTSTRAP_NOTES = Path(\"Documentation/zigux/phase2-toolchain-bootstrap-notes.md\")");
    try expectContains(checker, "WORKFLOW = Path(\".github/workflows/zigux-bootstrap.yml\")");
    try expectContains(checker, "MAKEFILE = Path(\"zigux/Makefile\")");
    try expectContains(checker, "AGGREGATE_ROUTE = \"phase2\"");
    try expectContains(checker, "EXPECTED_SELF_TEST_CASE_COUNT = 24");
    try expectContains(checker, "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_SELF_TEST=pass");
    try expectContains(checker, "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES=pass");
    try expectContains(checker, "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_REQUIRED_ROUTE_COUNT");
    try expectContains(checker, "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_WORKFLOW_LINE_COUNT");
    try expectContains(checker, "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_MAKEFILE_LINE_COUNT");
    try expectContains(checker, "duplicate required_make_routes");
    try expectContains(checker, "phase2-future");
}

test "policy and bootstrap note preserve the Phase 2 make route roster" {
    const policy = try readRepoFile("scripts/zigux/zig-toolchain-policy.json");
    defer std.testing.allocator.free(policy);
    const note = try readRepoFile("Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    defer std.testing.allocator.free(note);

    try expectContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"required_make_routes\": [");
    try expectContains(note, "bootstrap workflow-route truthfulness");
    try expectContains(note, "The rematerialized make-wrapper packet is directly readable on current `master`");

    for (routes) |route| {
        try expectContains(policy, route);

        var note_marker: [128]u8 = undefined;
        const rendered_note_marker = try std.fmt.bufPrint(&note_marker, "`make -C zigux {s}`", .{route});
        try expectContains(note, rendered_note_marker);
    }

    try expectContains(note, "`make -C zigux phase2`");
    try expectNotContains(note, "older missing-route assumptions");
}

test "workflow runs the route checker and every rematerialized Phase 2 route once" {
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    try expectLineOnce(workflow, "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py --self-test");
    try expectLineOnce(workflow, "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py");

    for (routes) |route| {
        var route_line: [128]u8 = undefined;
        const rendered_route_line = try std.fmt.bufPrint(&route_line, "run: make -C zigux {s}", .{route});
        try expectLineOnce(workflow, rendered_route_line);
    }

    try expectLineOnce(workflow, "run: make -C zigux phase2");
}

test "Makefile keeps the route rules and aggregate dependency aligned" {
    const makefile = try readRepoFile("zigux/Makefile");
    defer std.testing.allocator.free(makefile);

    for (routes) |route| {
        try expectContains(makefile, route);
    }

    try expectLineOnce(makefile, "phase2-toolchain:");
    try expectLineOnce(makefile, "phase2-tools:");
    try expectLineOnce(makefile, "phase2-kconfig: phase2-toolchain");
    try expectLineOnce(makefile, "phase2-cross:");
    try expectLineOnce(makefile, "phase2-genksyms: phase2-toolchain");
    try expectLineOnce(makefile, "phase2-fixdep: phase2-toolchain");
    try expectLineOnce(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
    try expectLineOnce(makefile, "phase2: phase2-validate");
    try expectContains(makefile, "$(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py --self-test");
    try expectContains(makefile, "$(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py");
}
