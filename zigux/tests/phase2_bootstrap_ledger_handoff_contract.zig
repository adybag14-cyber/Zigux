const std = @import("std");

const max_file_size = 512 * 1024;

const RootFiles = struct {
    ledger: []const u8,
    docs_root: []const u8,
    bootstrap_note: []const u8,
    scripts_readme: []const u8,
    tests_readme: []const u8,
};

fn readRootFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(max_file_size),
    );
}

fn loadRootFiles(allocator: std.mem.Allocator) !RootFiles {
    return .{
        .ledger = try readRootFile(allocator, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md"),
        .docs_root = try readRootFile(allocator, "Documentation/zigux/README.md"),
        .bootstrap_note = try readRootFile(allocator, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"),
        .scripts_readme = try readRootFile(allocator, "scripts/zigux/README.md"),
        .tests_readme = try readRootFile(allocator, "zigux/tests/README.md"),
    };
}

fn freeRootFiles(allocator: std.mem.Allocator, files: RootFiles) void {
    allocator.free(files.ledger);
    allocator.free(files.docs_root);
    allocator.free(files.bootstrap_note);
    allocator.free(files.scripts_readme);
    allocator.free(files.tests_readme);
}

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(contains(haystack, needle));
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(!contains(haystack, needle));
}

test "bootstrap ledger keeps Lane 25 item scoped to broadened Phase 2 docs" {
    const files = try loadRootFiles(std.testing.allocator);
    defer freeRootFiles(std.testing.allocator, files);

    try expectContains(files.ledger, "25. `docs(zigux): reopen and close broadened Phase 2 tranche`");
    try expectContains(files.ledger, "Documentation/zigux/phase2-closure.md");
    try expectContains(files.ledger, "Documentation/zigux/artifact-diff.md");
    try expectContains(files.ledger, "scripts/zigux/README.md");
    try expectContains(files.ledger, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md");
    try expectContains(files.ledger, "This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.");
}

test "ledger handoff points later release planning back to live documentation root" {
    const files = try loadRootFiles(std.testing.allocator);
    defer freeRootFiles(std.testing.allocator, files);

    try expectContains(files.ledger, "For current release sequencing, tranche-closure posture, and release-coordination follow-through on `master`, continue from the docs-root PMO packet instead:");
    try expectContains(files.ledger, "Documentation/zigux/README.md");
    try expectContains(files.ledger, "Documentation/zigux/phase12-release-sequencing.md");
    try expectContains(files.ledger, "Documentation/zigux/phase14-release-boundary-survey.md");
    try expectContains(files.ledger, "For the active Phase 5 non-runtime sample tranche, treat the landed closure note as the ledger-side handoff instead of inventing synthetic later-train commit entries:");

    try expectContains(files.docs_root, "Phase 2 notes");
    try expectContains(files.docs_root, "Documentation/zigux/phase2-closure.md");
    try expectContains(files.docs_root, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    try expectContains(files.docs_root, "scripts/zigux/validate-phase2.py");
    try expectContains(files.docs_root, "zigux/Makefile");
    try expectContains(files.docs_root, "Phase 12 notes");
    try expectContains(files.docs_root, "Phase 14 notes");
}

test "ledger stays an early-train authority without reviving stale Phase 2 gaps" {
    const files = try loadRootFiles(std.testing.allocator);
    defer freeRootFiles(std.testing.allocator, files);

    try expectContains(files.ledger, "Keep this ledger authoritative for the reviewed bootstrap commit train through item 25 only.");
    try expectContains(files.ledger, "Do not backfill later release-planning state here as synthetic commit history");
    try expectContains(files.ledger, "use this ledger when the question is which reviewed bootstrap tranche changes landed through the bounded early train");
    try expectContains(files.ledger, "use the docs-root PMO packet when the question is which release-planning surfaces currently govern later-phase release work on `master`");
    try expectNotContains(files.ledger, "26. `");

    try expectContains(files.bootstrap_note, "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.");
    try expectContains(files.scripts_readme, "make -C zigux phase2");
    try expectContains(files.tests_readme, "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`");
}
