const std = @import("std");

const RepoFile = struct {
    path: []const u8,
    contents: []u8,
};

const artifact_support_paths = [_][]const u8{
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
};

const artifact_consumers = [_][]const u8{
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-fixdep-diff.py",
};

const supported_modes = [_][]const u8{
    "\"text\"",
    "\"json\"",
    "\"bytes\"",
};

fn readFile(path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn loadRepoFile(path: []const u8, limit: usize) !RepoFile {
    return .{
        .path = path,
        .contents = try readFile(path, limit),
    };
}

fn unloadRepoFile(file: RepoFile) void {
    std.testing.allocator.free(file.contents);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectFileContains(file: RepoFile, needle: []const u8) !void {
    _ = file.path;
    try expectContains(file.contents, needle);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "scripts root keeps Phase 2 artifact support surfaced beside current tooling packet" {
    const scripts_readme = try loadRepoFile("scripts/zigux/README.md", 512 * 1024);
    defer unloadRepoFile(scripts_readme);
    const tool_manifest = try loadRepoFile("zigux/tests/fixtures/phase2_tool_manifest.json", 1024 * 1024);
    defer unloadRepoFile(tool_manifest);
    const artifact_manifest = try loadRepoFile("zigux/tests/fixtures/phase2_artifact_tools_manifest.json", 128 * 1024);
    defer unloadRepoFile(artifact_manifest);

    try expectFileContains(scripts_readme, "## Phase 2");
    try expectFileContains(scripts_readme, "Phase 2 flow - the current scripts-root bridge packet");
    try expectFileContains(scripts_readme, "tool-manifest packet, artifact-support packet");
    try expectFileContains(scripts_readme, "scripts/zigux/check-phase2-artifact-tools-manifest.py");
    try expectFileContains(scripts_readme, "zigux/tests/fixtures/phase2_artifact_tools_manifest.json");
    try expectFileContains(scripts_readme, "scripts/zigux/artifact_diff.py");

    inline for (artifact_support_paths) |path| {
        try expectContains(tool_manifest.contents, path);
    }

    try expectFileContains(tool_manifest, "\"artifact_support\"");
    try expectFileContains(tool_manifest, "\"scripts/zigux/check-phase2-artifact-tools-manifest.py\"");
    try expectFileContains(tool_manifest, "\"scripts/zigux/artifact_diff.py\"");
    try expectFileContains(tool_manifest, "\"Keep the dedicated manifest guards, the bootstrap workflow-routes guard, the primary artifact_diff helper");
    try expectFileContains(tool_manifest, "\"Keep scripts/zigux/README.md explicit as the shipped scripts-root reminder surface");

    try expectFileContains(artifact_manifest, "\"scope\": \"artifact-diff support for fixture-backed scripts/zigux validation\"");
    try expectFileContains(artifact_manifest, "\"primary\"");
    try expectFileContains(artifact_manifest, "\"consumers\"");
    try expectFileContains(artifact_manifest, "\"checkers\"");
}

test "artifact tools manifest keeps helper modes consumers and checker self-description aligned" {
    const artifact_manifest = try loadRepoFile("zigux/tests/fixtures/phase2_artifact_tools_manifest.json", 128 * 1024);
    defer unloadRepoFile(artifact_manifest);
    const checker = try loadRepoFile("scripts/zigux/check-phase2-artifact-tools-manifest.py", 256 * 1024);
    defer unloadRepoFile(checker);

    try expectFileContains(artifact_manifest, "\"phase\": \"Phase 2\"");
    try expectFileContains(artifact_manifest, "\"status\": \"active\"");
    try expectFileContains(artifact_manifest, "\"scripts/zigux/artifact_diff.py\"");
    try expectFileContains(artifact_manifest, "\"scripts/zigux/check-phase2-artifact-tools-manifest.py\"");

    inline for (artifact_consumers) |consumer| {
        try expectContains(artifact_manifest.contents, consumer);
        try expectContains(checker.contents, consumer);
    }

    inline for (supported_modes) |mode| {
        try expectContains(artifact_manifest.contents, mode);
    }

    try expectFileContains(checker, "\"PHASE2_ARTIFACT_TOOLS_MANIFEST=pass\"");
    try expectFileContains(checker, "PHASE2_ARTIFACT_TOOLS_MANIFEST_REQUIRED_NOTE_COUNT");
    try expectFileContains(checker, "PHASE2_ARTIFACT_TOOLS_MANIFEST_REQUIRED_TOOL_PATH_COUNT");
    try expectFileContains(checker, "PRIMARY_TOOL_MARKERS");
    try expectFileContains(checker, "EXPECTED_CONSUMER_MARKERS");
    try expectFileContains(checker, "REQUIRED_NOTE_MARKERS");
}

test "closure artifact-support wording stays narrower than unrelated Phase 2 bridge evidence" {
    const closure_note = try loadRepoFile("Documentation/zigux/phase2-closure.md", 256 * 1024);
    defer unloadRepoFile(closure_note);
    const artifact_note = try loadRepoFile("Documentation/zigux/artifact-diff.md", 256 * 1024);
    defer unloadRepoFile(artifact_note);

    try expectFileContains(closure_note, "scripts/zigux/check-phase2-artifact-tools-manifest.py");
    try expectFileContains(closure_note, "scripts/zigux/artifact_diff.py");
    try expectFileContains(closure_note, "zigux/tests/fixtures/phase2_artifact_tools_manifest.json");
    try expectFileContains(closure_note, "PHASE2_SHARED_TOOLING_CHECKERS=");
    try expectOrdered(
        closure_note.contents,
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        "PHASE2_SHARED_TOOLING_CHECKERS=",
    );

    try expectFileContains(artifact_note, "Phase 2 still routes focused host-tool fixture comparisons");
    try expectFileContains(artifact_note, "`fixdep` and the kconfig bridge packet");
    try expectFileContains(artifact_note, "current `genksyms` bridge packet keeps its fixture comparisons local");
    try expectFileContains(artifact_note, "scripts/zigux/check-genksyms-bridge.py");
}
