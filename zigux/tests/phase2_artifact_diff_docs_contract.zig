const std = @import("std");
const testing = std.testing;

const max_file_size = 256 * 1024;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.Io.Threaded.global_single_threaded.io(),
        path,
        allocator,
        .limited(max_file_size),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;

    try testing.expect(earlier_index < later_index);
}

test "artifact diff note keeps Phase 2 ownership bounded to fixdep and kconfig" {
    const artifact_note = try readRepoFile(testing.allocator, "Documentation/zigux/artifact-diff.md");
    defer testing.allocator.free(artifact_note);

    try expectContains(artifact_note, "## Current Phase 2 use");
    try expectContains(
        artifact_note,
        "Phase 2 still routes focused host-tool fixture comparisons through the same helper family when validating `fixdep` and the kconfig bridge packet.",
    );
    try expectContains(
        artifact_note,
        "The current `genksyms` bridge packet keeps its fixture comparisons local to `scripts/zigux/check-genksyms-bridge.py`.",
    );

    try expectBefore(
        artifact_note,
        "## Current Phase 2 use",
        "## Current Phase 3 use",
    );
    try expectBefore(
        artifact_note,
        "## Current Phase 2 use",
        "## Current Phase 4 use",
    );
}

test "closure and scripts reminders keep artifact support in the Phase 2 packet" {
    const closure_note = try readRepoFile(testing.allocator, "Documentation/zigux/phase2-closure.md");
    defer testing.allocator.free(closure_note);
    const scripts_readme = try readRepoFile(testing.allocator, "scripts/zigux/README.md");
    defer testing.allocator.free(scripts_readme);

    try expectContains(
        closure_note,
        "`scripts/zigux/artifact_diff.py` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` remain the current artifact-support reminder pair",
    );
    try expectContains(
        closure_note,
        "python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    );
    try expectContains(
        closure_note,
        "PHASE2_SHARED_TOOLING_CHECKERS=python3 scripts/zigux/check-phase2-tool-manifest.py,python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py,python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    );

    try expectContains(
        scripts_readme,
        "`scripts/zigux/check-phase2-artifact-tools-manifest.py`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/install-zig.py`",
    );
    try expectContains(
        scripts_readme,
        "keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
    );
}

test "tool manifest names artifact diff as current Phase 2 evidence" {
    const tool_manifest = try readRepoFile(testing.allocator, "zigux/tests/fixtures/phase2_tool_manifest.json");
    defer testing.allocator.free(tool_manifest);

    try expectContains(
        tool_manifest,
        "\"artifact_support\": [\n      \"scripts/zigux/artifact_diff.py\",\n      \"scripts/zigux/check-phase2-artifact-tools-manifest.py\",\n      \"zigux/tests/fixtures/phase2_artifact_tools_manifest.json\"\n    ]",
    );
    try expectContains(
        tool_manifest,
        "\"scripts/zigux/check-phase2-artifact-tools-manifest.py\"",
    );
    try expectContains(
        tool_manifest,
        "\"scripts/zigux/artifact_diff.py\"",
    );
    try expectContains(
        tool_manifest,
        "\"repo_reality_gaps\": []",
    );
}
