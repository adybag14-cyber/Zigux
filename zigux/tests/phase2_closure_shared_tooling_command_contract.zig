const std = @import("std");

const closure_path = "Documentation/zigux/phase2-closure.md";
const validator_path = "scripts/zigux/validate-phase2-closure.py";
const manifest_path = "zigux/tests/fixtures/phase2_tool_manifest.json";

const shared_tooling_commands = [_][]const u8{
    "python3 scripts/zigux/check-phase2-tool-manifest.py",
    "python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "python3 scripts/zigux/check-phase2-cross.py",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "python3 scripts/zigux/check-fixdep-diff.py",
};

const manifest_checker_paths = [_][]const u8{
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
};

fn readRepoFile(path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(256 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    return count;
}

fn sharedToolingLine() []const u8 {
    return "PHASE2_SHARED_TOOLING_CHECKERS=python3 scripts/zigux/check-phase2-tool-manifest.py,python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py,python3 scripts/zigux/check-phase2-artifact-tools-manifest.py,python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py,python3 scripts/zigux/check-phase2-cross.py,python3 scripts/zigux/check-phase2-fixdep-gate.py,python3 scripts/zigux/check-fixdep-diff.py";
}

test "phase2 closure note keeps shared tooling commands explicit and ordered" {
    const closure = try readRepoFile(closure_path);
    defer std.testing.allocator.free(closure);

    try expectContains(closure, "## Current Shared Repo-Tooling Evidence");
    try expectContains(closure, sharedToolingLine());
    try expectOrdered(closure, "## Current Shared Repo-Tooling Evidence", sharedToolingLine());
    try expectOrdered(closure, sharedToolingLine(), "## Shared Replay Routes");

    for (shared_tooling_commands) |command| {
        try expectContains(closure, command);
        try std.testing.expect(countOccurrences(closure, command) >= 2);
    }

    try expectContains(closure, "scripts/zigux/artifact_diff.py");
    try expectContains(closure, "zigux/tests/fixtures/phase2_artifact_tools_manifest.json");
    try expectContains(closure, "make -C zigux phase2-fixdep");
}

test "phase2 closure validator derives the same shared tooling command packet" {
    const validator = try readRepoFile(validator_path);
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "SHARED_TOOLING_COMMANDS = (");
    try expectContains(validator, "SHARED_TOOLING_REQUIRED_NOTE_MARKERS = (");
    try expectOrdered(validator, "SHARED_TOOLING_COMMANDS = (", "SHARED_TOOLING_REQUIRED_NOTE_MARKERS = (");

    for (shared_tooling_commands) |command| {
        try expectContains(validator, command);
    }
    for (manifest_checker_paths) |path| {
        try expectContains(validator, path);
    }

    try expectContains(validator, "\"PHASE2_SHARED_TOOLING_CHECKERS=\"");
    try expectContains(validator, "SHARED_TOOLING_COMMANDS");
    try expectNotContains(validator, "PHASE2_SHARED_TOOLING_CHECKERS=python3 scripts/zigux/check-phase2-tool-manifest.py,python3 scripts/zigux/check-phase2-cross.py");
}

test "phase2 tool manifest still carries the shared tooling checker roster" {
    const manifest = try readRepoFile(manifest_path);
    defer std.testing.allocator.free(manifest);

    try expectContains(manifest, "\"checkers\"");
    try expectContains(manifest, "\"artifact_support\"");
    try expectContains(manifest, "\"cross_route_support\"");
    try expectContains(manifest, "\"fixdep_support\"");

    for (manifest_checker_paths) |path| {
        try expectContains(manifest, path);
    }

    try expectContains(manifest, "scripts/zigux/artifact_diff.py");
    try expectContains(manifest, "zigux/tests/fixtures/phase2_artifact_tools_manifest.json");
    try expectContains(manifest, "zigux/tests/fixtures/phase2_cross_targets.json");
    try expectContains(manifest, "zigux/tests/fixtures/fixdep/cases.json");
}
