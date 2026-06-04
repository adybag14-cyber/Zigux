const std = @import("std");

const phase2_workflow_order = [_][]const u8{
    "Setup pinned Zig toolchain",
    "Self-test current Phase 2 fixdep gate checker",
    "Check current Phase 2 fixdep gate packet",
    "Run current Phase 2 fixdep unit tests",
    "Self-test current kconfig bridge checker",
    "Check current kconfig bridge packet",
    "Run current Phase 2 conf bridge unit tests",
    "Run current Phase 2 confdata bridge unit tests",
    "Self-test current Phase 2 kconfig bridge checker",
    "Check current Phase 2 kconfig bridge packet",
    "Self-test current Phase 2 kconfig allconfig helper checker",
    "Check current Phase 2 kconfig allconfig helper packet",
    "Self-test current Phase 2 kbuild routes checker",
    "Check current Phase 2 kbuild packet",
    "Self-test current Phase 2 tests README checker",
    "Check current Phase 2 tests README packet",
    "Self-test current Phase 2 cross checker",
    "Check current Phase 2 direct cross-route packet",
    "Self-test current Phase 2 cross selftest alignment checker",
    "Check current Phase 2 cross alignment packet",
    "Self-test current Phase 2 toolchain pinning checker",
    "Check current Phase 2 toolchain pinning packet",
    "Self-test current Phase 2 toolchain pin-scope checker",
    "Check current Phase 2 toolchain pin-scope packet",
    "Self-test current Phase 2 bootstrap workflow routes checker",
    "Check current Phase 2 bootstrap workflow routes packet",
    "Run current Phase 2 toolchain make route",
    "Run current Phase 2 tools make route",
    "Run current Phase 2 kconfig make route",
    "Run current Phase 2 fixdep make route",
    "Run current Phase 2 cross make route",
    "Self-test current Phase 2 required-make-routes checker",
    "Check current Phase 2 required-make-routes packet",
    "Self-test current Phase 2 shared reminder checker",
    "Check current Phase 2 shared reminder packet",
    "Self-test current Phase 2 tool manifest checker",
    "Check current Phase 2 tool manifest packet",
    "Self-test current Phase 2 artifact tools manifest checker",
    "Check current Phase 2 artifact tools manifest packet",
    "Self-test current Phase 2 genksyms bridge checker",
    "Check current Phase 2 genksyms bridge packet",
    "Run current Phase 2 genksyms unit replay",
    "Self-test current Phase 2 genksyms alignment checker",
    "Check current Phase 2 genksyms alignment packet",
    "Self-test current Phase 2 genksyms survey guard",
    "Check current Phase 2 genksyms survey packet",
    "Run current Phase 2 genksyms make route",
    "Run current Phase 2 validate make route",
    "Run current Phase 2 aggregate make route",
    "Validate current Phase 2 tool packet",
    "Self-test current Phase 2 closure validator",
    "Check current Phase 2 closure packet",
    "Self-test current Phase 1 direct-owner checker",
};

const make_route_steps = [_][]const u8{
    "Run current Phase 2 toolchain make route",
    "Run current Phase 2 tools make route",
    "Run current Phase 2 kconfig make route",
    "Run current Phase 2 fixdep make route",
    "Run current Phase 2 cross make route",
    "Run current Phase 2 genksyms make route",
    "Run current Phase 2 validate make route",
    "Run current Phase 2 aggregate make route",
};

const closure_make_routes = [_][]const u8{
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
};

const closure_validator_commands = [_][]const u8{
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py",
};

const workflow_run_commands = [_][]const u8{
    "python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py --self-test",
    "python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py --self-test",
    "python3 scripts/zigux/validate-phase2-closure.py",
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "phase 2 workflow keeps closure packet order before phase 1 handoff" {
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml", 384 * 1024);
    defer std.testing.allocator.free(workflow);

    var last_index: usize = 0;
    inline for (phase2_workflow_order, 0..) |marker, index| {
        const marker_index = std.mem.indexOf(u8, workflow, marker) orelse return error.MissingWorkflowStep;
        if (index != 0) try std.testing.expect(last_index < marker_index);
        last_index = marker_index;
    }
}

test "phase 2 closure make routes match workflow run commands" {
    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 96 * 1024);
    defer std.testing.allocator.free(closure_note);

    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml", 384 * 1024);
    defer std.testing.allocator.free(workflow);

    const manifest = try readRepoFile("zigux/tests/fixtures/phase2_tool_manifest.json", 256 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(closure_note, "PHASE2_SHARED_MAKE_ROUTES=");
    inline for (closure_make_routes) |route| {
        try expectContains(closure_note, route);
        try expectContains(manifest, route);
        try expectContains(workflow, route);
    }

    inline for (make_route_steps) |step_name| {
        try expectContains(workflow, step_name);
    }
}

test "phase 2 closure validators run after aggregate make wrapper" {
    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 96 * 1024);
    defer std.testing.allocator.free(closure_note);

    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml", 384 * 1024);
    defer std.testing.allocator.free(workflow);

    try expectContains(closure_note, "PHASE2_CLOSURE_VALIDATORS=");
    inline for (closure_validator_commands) |command| {
        try expectContains(closure_note, command);
    }

    inline for (workflow_run_commands) |command| {
        try expectContains(workflow, command);
    }

    try expectOrder(workflow, "Run current Phase 2 aggregate make route", "Validate current Phase 2 tool packet");
    try expectOrder(workflow, "Validate current Phase 2 tool packet", "Self-test current Phase 2 closure validator");
    try expectOrder(workflow, "Self-test current Phase 2 closure validator", "Check current Phase 2 closure packet");
    try expectOrder(workflow, "Check current Phase 2 closure packet", "Self-test current Phase 1 direct-owner checker");
}
