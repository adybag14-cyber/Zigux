const std = @import("std");

const closure_note_path = "Documentation/zigux/phase2-closure.md";

const shared_tooling_checkers = [_][]const u8{
    "python3 scripts/zigux/check-phase2-tool-manifest.py",
    "python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "python3 scripts/zigux/check-phase2-cross.py",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "python3 scripts/zigux/check-fixdep-diff.py",
};

const shared_tooling_surfaces = [_][]const u8{
    "## Current Shared Repo-Tooling Evidence",
    "shared manifest, workflow-route, and artifact-support packet",
    "helper-local kconfig, direct cross-route, and fixdep governance/parity packet",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "scripts/zigux/artifact_diff.py",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "instead of falling back into repo-reality-gap wording",
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

fn readClosureNote(allocator: std.mem.Allocator) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        closure_note_path,
        allocator,
        .limited(24 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase2 closure keeps shared repo-tooling surfaces explicit" {
    const closure_note = try readClosureNote(std.testing.allocator);
    defer std.testing.allocator.free(closure_note);

    for (shared_tooling_surfaces) |needle| {
        try expectContains(closure_note, needle);
    }
}

test "phase2 closure names the exact shared tooling checker roster" {
    const closure_note = try readClosureNote(std.testing.allocator);
    defer std.testing.allocator.free(closure_note);

    const roster_marker = "PHASE2_SHARED_TOOLING_CHECKERS=";
    const roster_start = std.mem.indexOf(u8, closure_note, roster_marker) orelse return error.MissingRoster;
    const roster_end = std.mem.indexOfScalarPos(u8, closure_note, roster_start, 10) orelse closure_note.len;
    const roster_line = closure_note[roster_start..roster_end];

    for (shared_tooling_checkers) |needle| {
        try expectContains(roster_line, needle);
    }
}

test "phase2 closure keeps shared replay routes and validators paired" {
    const closure_note = try readClosureNote(std.testing.allocator);
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "## Shared Replay Routes");
    try expectContains(closure_note, "PHASE2_SHARED_MAKE_ROUTES=");
    try expectContains(closure_note, "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py");

    for (shared_make_routes) |needle| {
        try expectContains(closure_note, needle);
    }
}
