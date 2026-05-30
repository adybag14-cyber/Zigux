const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

const routes = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    try std.testing.expectEqual(expected, std.mem.count(u8, haystack, needle));
}

fn makeRoute(buffer: []u8, prefix: []const u8, route: []const u8) ![]const u8 {
    return try std.fmt.bufPrint(buffer, "{s}{s}", .{ prefix, route });
}

test "closure note names the bootstrap workflow-route checker and shared route packet" {
    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 64 * 1024);
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "scripts/zigux/check-phase2-bootstrap-workflow-routes.py");
    try expectContains(closure_note, "PHASE2_SHARED_MAKE_ROUTES=");
    try expectContains(closure_note, "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py");

    var route_buffer: [96]u8 = undefined;
    for (routes) |route| {
        try expectContains(closure_note, try makeRoute(&route_buffer, "make -C zigux ", route));
    }
    try expectContains(closure_note, "make -C zigux phase2");
}

test "bootstrap note keeps the workflow-route checker beside returned make wrappers" {
    const bootstrap_note = try readRepoFile("Documentation/zigux/phase2-toolchain-bootstrap-notes.md", 128 * 1024);
    defer std.testing.allocator.free(bootstrap_note);

    try expectContains(bootstrap_note, "scripts/zigux/check-phase2-bootstrap-workflow-routes.py");
    try expectContains(bootstrap_note, "bootstrap workflow-route truthfulness");
    try expectContains(bootstrap_note, "The rematerialized make-wrapper packet is directly readable on current `master`");

    var route_buffer: [96]u8 = undefined;
    for (routes) |route| {
        try expectContains(bootstrap_note, try makeRoute(&route_buffer, "`make -C zigux ", route));
    }
    try expectContains(bootstrap_note, "`make -C zigux phase2`");
}

test "workflow and makefile execute the checker and the route set once" {
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml", 128 * 1024);
    defer std.testing.allocator.free(workflow);
    const makefile = try readRepoFile("zigux/Makefile", 128 * 1024);
    defer std.testing.allocator.free(makefile);

    try expectCount(workflow, "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py --self-test", 1);
    try expectCount(workflow, "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py\n", 1);
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py --self-test");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py");

    var workflow_buffer: [96]u8 = undefined;
    var makefile_buffer: [96]u8 = undefined;
    for (routes) |route| {
        try expectCount(workflow, try makeRoute(&workflow_buffer, "run: make -C zigux ", route), 1);
        try expectCount(makefile, try makeRoute(&makefile_buffer, "\n", route), 1);
    }
    try expectCount(workflow, "run: make -C zigux phase2\n", 1);
    try expectContains(makefile, "phase2: phase2-validate");
}

test "checker source and policy agree on the route contract boundary" {
    const checker = try readRepoFile("scripts/zigux/check-phase2-bootstrap-workflow-routes.py", 64 * 1024);
    defer std.testing.allocator.free(checker);
    const policy = try readRepoFile("scripts/zigux/zig-toolchain-policy.json", 32 * 1024);
    defer std.testing.allocator.free(policy);

    try expectContains(checker, "EXPECTED_SELF_TEST_CASE_COUNT = 24");
    try expectContains(checker, "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_SELF_TEST=pass");
    try expectContains(checker, "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES=pass");
    try expectContains(checker, "WORKFLOW = Path(\".github/workflows/zigux-bootstrap.yml\")");
    try expectContains(checker, "MAKEFILE = Path(\"zigux/Makefile\")");
    try expectContains(checker, "BOOTSTRAP_NOTES = Path(\"Documentation/zigux/phase2-toolchain-bootstrap-notes.md\")");

    for (routes) |route| {
        try expectContains(policy, route);
        try expectContains(checker, route);
    }
    try expectContains(policy, "\"required_make_routes\"");
}
