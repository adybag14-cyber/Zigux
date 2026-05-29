const std = @import("std");

const closure_note_path = "Documentation/zigux/phase2-closure.md";
const manifest_checker_path = "scripts/zigux/check-phase2-tool-manifest.py";
const manifest_path = "zigux/tests/fixtures/phase2_tool_manifest.json";

const shared_checkers = [_][]const u8{
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

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    return try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase2 closure note keeps the shared manifest checker packet parked and replayable" {
    const allocator = std.testing.allocator;
    const closure_note = try readRepoFile(allocator, closure_note_path);
    defer allocator.free(closure_note);

    try expectContains(closure_note, "PHASE2_STATUS=parked");
    try expectContains(closure_note, "## Current Shared Repo-Tooling Evidence");
    try expectContains(closure_note, "scripts/zigux/check-phase2-tool-manifest.py");
    try expectContains(closure_note, "scripts/zigux/check-phase2-bootstrap-workflow-routes.py");
    try expectContains(closure_note, "scripts/zigux/check-phase2-artifact-tools-manifest.py");
    try expectContains(closure_note, "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py");
    try expectContains(closure_note, "scripts/zigux/check-phase2-cross.py");
    try expectContains(closure_note, "scripts/zigux/check-phase2-fixdep-gate.py");
    try expectContains(closure_note, "scripts/zigux/check-fixdep-diff.py");
    try expectContains(closure_note, "PHASE2_SHARED_TOOLING_CHECKERS=");
    try expectContains(closure_note, "PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md");
}

test "phase2 closure note and manifest checker agree on shared checker roster" {
    const allocator = std.testing.allocator;
    const closure_note = try readRepoFile(allocator, closure_note_path);
    defer allocator.free(closure_note);
    const manifest_checker = try readRepoFile(allocator, manifest_checker_path);
    defer allocator.free(manifest_checker);

    for (shared_checkers) |checker| {
        const script_path = checker["python3 ".len..];
        try expectContains(closure_note, checker);
        try expectContains(manifest_checker, script_path);
    }
}

test "phase2 closure make routes match the manifest checker required route set" {
    const allocator = std.testing.allocator;
    const closure_note = try readRepoFile(allocator, closure_note_path);
    defer allocator.free(closure_note);
    const manifest_checker = try readRepoFile(allocator, manifest_checker_path);
    defer allocator.free(manifest_checker);

    try expectContains(closure_note, "PHASE2_SHARED_MAKE_ROUTES=");
    for (shared_make_routes) |route| {
        try expectContains(closure_note, route);
        if (!std.mem.eql(u8, route, "make -C zigux phase2")) {
            try expectContains(manifest_checker, route["make -C zigux ".len..]);
        }
    }
}

test "phase2 tool manifest keeps tranche closure scope and workflow identity explicit" {
    const allocator = std.testing.allocator;
    const manifest = try readRepoFile(allocator, manifest_path);
    defer allocator.free(manifest);

    try expectContains(manifest, "\"phase\": \"Phase 2\"");
    try expectContains(manifest, "\"status\": \"active\"");
    try expectContains(manifest, "tranche-closure reminder packet");
    try expectContains(manifest, "\"workflow\": \".github/workflows/zigux-bootstrap.yml\"");
}
