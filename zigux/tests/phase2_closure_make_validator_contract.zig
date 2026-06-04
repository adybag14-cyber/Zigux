const std = @import("std");

const make_routes = [_][]const u8{
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
};

const make_targets = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
    "phase2",
};

const validator_commands = [_][]const u8{
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py",
};

const validator_paths = [_][]const u8{
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
};

const shared_checker_commands = [_][]const u8{
    "python3 scripts/zigux/check-phase2-tool-manifest.py",
    "python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "python3 scripts/zigux/check-phase2-cross.py",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "python3 scripts/zigux/check-fixdep-diff.py",
};

const shared_checker_paths = [_][]const u8{
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn indexOfTarget(haystack: []const u8, target: []const u8) ?usize {
    var target_buf: [64]u8 = undefined;
    const start_marker = std.fmt.bufPrint(&target_buf, "{s}:", .{target}) catch return null;
    if (std.mem.startsWith(u8, haystack, start_marker)) return 0;

    var line_buf: [64]u8 = undefined;
    const line_marker = std.fmt.bufPrint(&line_buf, "\n{s}:", .{target}) catch return null;
    return std.mem.indexOf(u8, haystack, line_marker);
}

fn expectTarget(haystack: []const u8, target: []const u8) !void {
    try std.testing.expect(indexOfTarget(haystack, target) != null);
}

fn expectTargetOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = indexOfTarget(haystack, before) orelse return error.MissingBeforeTarget;
    const after_index = indexOfTarget(haystack, after) orelse return error.MissingAfterTarget;
    try std.testing.expect(before_index < after_index);
}

fn expectOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "phase 2 closure keeps make wrapper roster synchronized" {
    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 96 * 1024);
    defer std.testing.allocator.free(closure_note);

    const tests_readme = try readRepoFile("zigux/tests/README.md", 256 * 1024);
    defer std.testing.allocator.free(tests_readme);

    const makefile = try readRepoFile("zigux/Makefile", 128 * 1024);
    defer std.testing.allocator.free(makefile);

    const manifest = try readRepoFile("zigux/tests/fixtures/phase2_tool_manifest.json", 256 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(closure_note, "PHASE2_SHARED_MAKE_ROUTES=");
    try expectContains(tests_readme, "Keep the rematerialized make-wrapper packet explicit through");
    try expectContains(manifest, "\"make_wrappers\"");

    inline for (make_routes) |route| {
        try expectContains(closure_note, route);
        try expectContains(tests_readme, route);
        try expectContains(manifest, route);
    }

    inline for (make_targets) |target| {
        try expectTarget(makefile, target);
    }

    try expectContains(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
    try expectContains(makefile, "phase2: phase2-validate");
}

test "phase 2 closure keeps validator and shared checker commands visible" {
    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 96 * 1024);
    defer std.testing.allocator.free(closure_note);

    const tests_readme = try readRepoFile("zigux/tests/README.md", 256 * 1024);
    defer std.testing.allocator.free(tests_readme);

    const makefile = try readRepoFile("zigux/Makefile", 128 * 1024);
    defer std.testing.allocator.free(makefile);

    const manifest = try readRepoFile("zigux/tests/fixtures/phase2_tool_manifest.json", 256 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(closure_note, "PHASE2_CLOSURE_VALIDATORS=");
    inline for (validator_commands) |command| {
        try expectContains(closure_note, command);
    }
    inline for (validator_paths) |path| {
        try expectContains(tests_readme, path);
        try expectContains(manifest, path);
        try expectContains(makefile, path);
    }

    try expectContains(closure_note, "PHASE2_SHARED_TOOLING_CHECKERS=");
    inline for (shared_checker_commands) |command| {
        try expectContains(closure_note, command);
    }
    inline for (shared_checker_paths) |path| {
        try expectContains(tests_readme, path);
        try expectContains(manifest, path);
        try expectContains(makefile, path);
    }
}

test "phase 2 makefile keeps closure checkers after route families" {
    const makefile = try readRepoFile("zigux/Makefile", 128 * 1024);
    defer std.testing.allocator.free(makefile);

    try expectTargetOrder(makefile, "phase2-toolchain", "phase2-tools");
    try expectTargetOrder(makefile, "phase2-tools", "phase2-kconfig");
    try expectTargetOrder(makefile, "phase2-kconfig", "phase2-cross");
    try expectTargetOrder(makefile, "phase2-cross", "phase2-genksyms");
    try expectTargetOrder(makefile, "phase2-genksyms", "phase2-fixdep");
    try expectTargetOrder(makefile, "phase2-fixdep", "phase2-validate");
    try expectTargetOrder(makefile, "phase2-validate", "phase2");
    try expectOrder(makefile, "check-phase2-tests-readme-alignment.py", "validate-phase2-closure.py");
}
