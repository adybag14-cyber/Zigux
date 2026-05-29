const std = @import("std");

const closure_note_path = "Documentation/zigux/phase2-closure.md";
const bootstrap_note_path = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md";

const shared_phase2_routes = [_][]const u8{
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
};

const shared_checker_roster = [_][]const u8{
    "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(96 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase2 closure points at the bootstrap note and validator pair" {
    const closure_note = try readRepoFile(std.testing.allocator, closure_note_path);
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "PHASE2_STATUS=parked");
    try expectContains(closure_note, "PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest");
    try expectContains(closure_note, "shared note: `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`");
    try expectContains(closure_note, "shared validator pair: `python3 scripts/zigux/validate-phase2.py` and `python3 scripts/zigux/validate-phase2-closure.py`");
}

test "bootstrap note keeps the closure and validator packet visible" {
    const bootstrap_note = try readRepoFile(std.testing.allocator, bootstrap_note_path);
    defer std.testing.allocator.free(bootstrap_note);

    try expectContains(bootstrap_note, "Documentation/zigux/phase2-closure.md");
    try expectContains(bootstrap_note, "scripts/zigux/validate-phase2.py");
    try expectContains(bootstrap_note, "scripts/zigux/validate-phase2-closure.py");
    try expectContains(bootstrap_note, "bounded closure-side, closure-validator, validator-entrypoint");
    try expectContains(bootstrap_note, "without widening back into older validator-first claims");
}

test "closure and bootstrap notes agree on shared Phase 2 replay routes" {
    const closure_note = try readRepoFile(std.testing.allocator, closure_note_path);
    defer std.testing.allocator.free(closure_note);
    const bootstrap_note = try readRepoFile(std.testing.allocator, bootstrap_note_path);
    defer std.testing.allocator.free(bootstrap_note);

    try expectContains(closure_note, "PHASE2_SHARED_MAKE_ROUTES=");
    try expectContains(bootstrap_note, "The rematerialized make-wrapper packet is directly readable on current `master`");
    for (shared_phase2_routes) |route| {
        try expectContains(closure_note, route);
        try expectContains(bootstrap_note, route);
    }
}

test "closure and bootstrap notes agree on shared checker handoff" {
    const closure_note = try readRepoFile(std.testing.allocator, closure_note_path);
    defer std.testing.allocator.free(closure_note);
    const bootstrap_note = try readRepoFile(std.testing.allocator, bootstrap_note_path);
    defer std.testing.allocator.free(bootstrap_note);

    try expectContains(closure_note, "## Current Shared Repo-Tooling Evidence");
    try expectContains(closure_note, "PHASE2_SHARED_TOOLING_CHECKERS=");
    try expectContains(bootstrap_note, "Phase 2 reminder, parity, archive-staging, and alignment guards visible on `master`");
    for (shared_checker_roster) |checker| {
        try expectContains(closure_note, checker);
        try expectContains(bootstrap_note, checker);
    }
}
