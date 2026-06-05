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

const shared_make_routes = [_][]const u8{
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
};

const closure_validators = [_][]const u8{
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py",
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

fn expectLineContainsAll(haystack: []const u8, line_prefix: []const u8, needles: []const []const u8) !void {
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (!std.mem.startsWith(u8, std.mem.trim(u8, line, " \t-`"), line_prefix)) {
            continue;
        }
        for (needles) |needle| {
            try expectContains(line, needle);
        }
        return;
    }

    try std.testing.expect(false);
}

fn makefileRouteTarget(route: []const u8) []const u8 {
    const prefix = "make -C zigux ";
    std.debug.assert(std.mem.startsWith(u8, route, prefix));
    return route[prefix.len..];
}

fn pythonCommandPath(command: []const u8) []const u8 {
    const prefix = "python3 ";
    std.debug.assert(std.mem.startsWith(u8, command, prefix));
    return command[prefix.len..];
}

test "phase 2 closure shared checker roster matches the manifest and make routes" {
    const closure = try readRepoFile("Documentation/zigux/phase2-closure.md", 128 * 1024);
    defer std.testing.allocator.free(closure);

    const manifest = try readRepoFile("zigux/tests/fixtures/phase2_tool_manifest.json", 512 * 1024);
    defer std.testing.allocator.free(manifest);

    const makefile = try readRepoFile("zigux/Makefile", 128 * 1024);
    defer std.testing.allocator.free(makefile);

    try expectLineContainsAll(closure, "PHASE2_SHARED_TOOLING_CHECKERS=", shared_tooling_commands[0..]);
    for (shared_tooling_commands) |command| {
        try expectContains(manifest, pythonCommandPath(command));
        if (std.mem.eql(u8, command, "python3 scripts/zigux/check-phase2-tool-manifest.py")) {
            try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py");
        } else if (std.mem.eql(u8, command, "python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py")) {
            try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py");
        } else if (std.mem.eql(u8, command, "python3 scripts/zigux/check-phase2-artifact-tools-manifest.py")) {
            try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py");
        } else if (std.mem.eql(u8, command, "python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py")) {
            try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py");
        } else if (std.mem.eql(u8, command, "python3 scripts/zigux/check-phase2-cross.py")) {
            try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py");
        } else if (std.mem.eql(u8, command, "python3 scripts/zigux/check-phase2-fixdep-gate.py")) {
            try expectContains(makefile, "scripts/zigux/check-phase2-fixdep-gate.py");
        } else if (std.mem.eql(u8, command, "python3 scripts/zigux/check-fixdep-diff.py")) {
            try expectContains(makefile, "scripts/zigux/check-fixdep-diff.py");
        }
    }
}

test "phase 2 closure shared make routes stay explicit across closure note, manifest, and Makefile" {
    const closure = try readRepoFile("Documentation/zigux/phase2-closure.md", 128 * 1024);
    defer std.testing.allocator.free(closure);

    const manifest = try readRepoFile("zigux/tests/fixtures/phase2_tool_manifest.json", 512 * 1024);
    defer std.testing.allocator.free(manifest);

    const makefile = try readRepoFile("zigux/Makefile", 128 * 1024);
    defer std.testing.allocator.free(makefile);

    try expectLineContainsAll(closure, "PHASE2_SHARED_MAKE_ROUTES=", shared_make_routes[0..]);
    for (shared_make_routes) |route| {
        try expectContains(manifest, route);
        try expectContains(makefile, makefileRouteTarget(route));
    }

    try expectContains(makefile, "phase2: phase2-validate");
    try expectContains(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
}

test "phase 2 closure validator pair stays directly named by closure and Makefile routes" {
    const closure = try readRepoFile("Documentation/zigux/phase2-closure.md", 128 * 1024);
    defer std.testing.allocator.free(closure);

    const manifest = try readRepoFile("zigux/tests/fixtures/phase2_tool_manifest.json", 512 * 1024);
    defer std.testing.allocator.free(manifest);

    const makefile = try readRepoFile("zigux/Makefile", 128 * 1024);
    defer std.testing.allocator.free(makefile);

    try expectLineContainsAll(closure, "PHASE2_CLOSURE_VALIDATORS=", closure_validators[0..]);
    for (closure_validators) |validator| {
        try expectContains(manifest, pythonCommandPath(validator));
    }
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py");
}
