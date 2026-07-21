const std = @import("std");
const testing = std.testing;

const DocFile = struct {
    contents: []u8,
};

fn readFile(path: []const u8, limit: usize) !DocFile {
    return .{
        .contents = try std.Io.Dir.cwd().readFileAlloc(
            testing.io,
            path,
            testing.allocator,
            .limited(limit),
        ),
    };
}

fn unloadFile(file: DocFile) void {
    testing.allocator.free(file.contents);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

test "lane 25 ledger pins the broadened phase 2 reconciliation packet" {
    const bootstrap_ledger = try readFile("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md", 256 * 1024);
    defer unloadFile(bootstrap_ledger);

    try expectContains(bootstrap_ledger.contents, "25. `docs(zigux): reopen and close broadened Phase 2 tranche`");
    try expectContains(bootstrap_ledger.contents, "- `Documentation/zigux/phase2-closure.md`");
    try expectContains(bootstrap_ledger.contents, "- `Documentation/zigux/artifact-diff.md`");
    try expectContains(bootstrap_ledger.contents, "- `scripts/zigux/README.md`");
    try expectContains(bootstrap_ledger.contents, "- `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`");
    try expectContains(bootstrap_ledger.contents, "This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.");
    try testing.expectEqual(@as(usize, 1), countOccurrences(bootstrap_ledger.contents, "reopen and close broadened Phase 2 tranche"));
}

test "phase 2 closure and scripts root share the required replay packet" {
    const phase2_closure = try readFile("Documentation/zigux/phase2-closure.md", 512 * 1024);
    defer unloadFile(phase2_closure);
    const scripts_readme = try readFile("scripts/zigux/README.md", 1024 * 1024);
    defer unloadFile(scripts_readme);

    const required_routes = [_][]const u8{
        "make -C zigux phase2-toolchain",
        "make -C zigux phase2-tools",
        "make -C zigux phase2-kconfig",
        "make -C zigux phase2-cross",
        "make -C zigux phase2-genksyms",
        "make -C zigux phase2-fixdep",
        "make -C zigux phase2-validate",
        "make -C zigux phase2",
    };

    try expectContains(phase2_closure.contents, "PHASE2_STATUS=parked");
    try expectContains(phase2_closure.contents, "PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest");
    try expectContains(phase2_closure.contents, "PHASE2_SHARED_MAKE_ROUTES=");
    try expectContains(scripts_readme.contents, "scripts\zigux/check_phase2_required_make_routes.zig");

    for (required_routes) |route| {
        try expectContains(phase2_closure.contents, route);
        try expectContains(scripts_readme.contents, route);
    }
}

test "artifact diff phase 2 scope stays aligned with the closure reminder" {
    const phase2_closure = try readFile("Documentation/zigux/phase2-closure.md", 512 * 1024);
    defer unloadFile(phase2_closure);
    const artifact_diff_note = try readFile("Documentation/zigux/artifact-diff.md", 512 * 1024);
    defer unloadFile(artifact_diff_note);

    try expectContains(phase2_closure.contents, "scripts/zigux/artifact_diff.zig");
    try expectContains(phase2_closure.contents, "zigux/tests/fixtures/phase2_artifact_tools_manifest.json");
    try expectContains(phase2_closure.contents, "zig run scripts/zigux/check_phase2_artifact_tools_manifest.zig");

    try expectContains(artifact_diff_note.contents, "## Current Phase 2 use");
    try expectContains(artifact_diff_note.contents, "Phase 2 still routes focused host-tool fixture comparisons through the same helper family when validating `fixdep` and the kconfig bridge packet.");
    try expectContains(artifact_diff_note.contents, "The current `genksyms` bridge packet keeps its fixture comparisons local to `scripts\zigux/check_genksyms_bridge.zig`.");
    try expectContains(artifact_diff_note.contents, "text`, `json`, and `bytes` artifacts");

    try expectNotContains(artifact_diff_note.contents, "Phase 2 no longer");
}
