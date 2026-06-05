const std = @import("std");

const RepoFile = enum {
    artifact_note,
    phase2_closure,
    docs_readme,
    scripts_readme,
    tests_readme,
    artifact_helper,
    artifact_manifest,
    artifact_manifest_checker,
};

fn pathFor(file: RepoFile) []const u8 {
    return switch (file) {
        .artifact_note => "Documentation/zigux/artifact-diff.md",
        .phase2_closure => "Documentation/zigux/phase2-closure.md",
        .docs_readme => "Documentation/zigux/README.md",
        .scripts_readme => "scripts/zigux/README.md",
        .tests_readme => "zigux/tests/README.md",
        .artifact_helper => "scripts/zigux/artifact_diff.py",
        .artifact_manifest => "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
        .artifact_manifest_checker => "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    };
}

fn readRepoFile(file: RepoFile) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        pathFor(file),
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(source: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, marker) != null);
}

fn expectContainsOnce(source: []const u8, marker: []const u8) !void {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, source, offset, marker)) |index| {
        count += 1;
        offset = index + marker.len;
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

fn expectOrder(source: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, source, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "phase2 artifact-diff docs keep the current support packet bounded" {
    const artifact_note = try readRepoFile(.artifact_note);
    defer std.testing.allocator.free(artifact_note);
    const phase2_closure = try readRepoFile(.phase2_closure);
    defer std.testing.allocator.free(phase2_closure);
    const docs_readme = try readRepoFile(.docs_readme);
    defer std.testing.allocator.free(docs_readme);

    try expectContains(artifact_note, "## Current Phase 2 use");
    try expectContains(artifact_note, "Phase 2 still routes focused host-tool fixture comparisons through the same helper family when validating `fixdep` and the kconfig bridge packet.");
    try expectContains(artifact_note, "The current `genksyms` bridge packet keeps its fixture comparisons local to `scripts/zigux/check-genksyms-bridge.py`.");
    try expectContains(artifact_note, "scripts/zigux/artifact_diff.py");
    try expectContains(artifact_note, "scripts/zigux/check-artifact-diff-contract.py");
    try expectContains(artifact_note, "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23");
    try expectContains(artifact_note, "legacy `sha256 -> bytes` alias");
    try expectOrder(
        artifact_note,
        "## Current Phase 2 use",
        "## Current Phase 3 use",
    );

    try expectContains(phase2_closure, "scripts/zigux/artifact_diff.py");
    try expectContains(phase2_closure, "zigux/tests/fixtures/phase2_artifact_tools_manifest.json");
    try expectContains(phase2_closure, "scripts/zigux/check-phase2-artifact-tools-manifest.py");
    try expectContains(phase2_closure, "PHASE2_SHARED_TOOLING_CHECKERS=");

    try expectContains(docs_readme, "scripts/zigux/check-phase2-artifact-tools-manifest.py");
    try expectContains(docs_readme, "zigux/tests/fixtures/phase2_artifact_tools_manifest.json");
}

test "phase2 scripts and tests reminders agree on artifact-diff current consumers" {
    const scripts_readme = try readRepoFile(.scripts_readme);
    defer std.testing.allocator.free(scripts_readme);
    const tests_readme = try readRepoFile(.tests_readme);
    defer std.testing.allocator.free(tests_readme);
    const artifact_manifest = try readRepoFile(.artifact_manifest);
    defer std.testing.allocator.free(artifact_manifest);

    try expectContains(scripts_readme, "scripts/zigux/check-phase2-artifact-tools-manifest.py");
    try expectContains(scripts_readme, "zigux/tests/fixtures/phase2_artifact_tools_manifest.json");
    try expectContains(scripts_readme, "supported_modes");
    try expectContains(scripts_readme, "artifact-support reminder pair");

    try expectContains(tests_readme, "scripts/zigux/check-phase2-artifact-tools-manifest.py");
    try expectContains(tests_readme, "zigux/tests/fixtures/phase2_artifact_tools_manifest.json");
    try expectContains(tests_readme, "scripts/zigux/check-kconfig-bridge.py");
    try expectContains(tests_readme, "scripts/zigux/check-fixdep-diff.py");

    try expectContains(artifact_manifest, "\"phase\": \"Phase 2\"");
    try expectContains(artifact_manifest, "\"status\": \"active\"");
    try expectContains(artifact_manifest, "\"scope\": \"artifact-diff support for fixture-backed scripts/zigux validation\"");
    try expectContains(artifact_manifest, "\"scripts/zigux/artifact_diff.py\"");
    try expectContains(artifact_manifest, "\"scripts/zigux/check-kconfig-bridge.py\"");
    try expectContains(artifact_manifest, "\"scripts/zigux/check-fixdep-diff.py\"");
    try expectContains(artifact_manifest, "\"scripts/zigux/check-phase2-artifact-tools-manifest.py\"");
    try expectContains(artifact_manifest, "\"text\"");
    try expectContains(artifact_manifest, "\"json\"");
    try expectContains(artifact_manifest, "\"bytes\"");
    try expectContains(artifact_manifest, "legacy `sha256` compatibility alias");
}

test "artifact helper and manifest checker keep mode and alias markers explicit" {
    const artifact_helper = try readRepoFile(.artifact_helper);
    defer std.testing.allocator.free(artifact_helper);
    const manifest_checker = try readRepoFile(.artifact_manifest_checker);
    defer std.testing.allocator.free(manifest_checker);

    try expectContainsOnce(artifact_helper, "MODE_CHOICES = (\"text\", \"json\", \"bytes\")");
    try expectContainsOnce(artifact_helper, "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}");
    try expectContains(artifact_helper, "\"legacy_sha256_alias\"");
    try expectContains(artifact_helper, "EXPECTED_SHA256=");
    try expectContains(artifact_helper, "ACTUAL_SHA256=");
    try expectContains(artifact_helper, "EXPECTED_UTF8_ERROR=");
    try expectContains(artifact_helper, "ACTUAL_UTF8_ERROR=");

    try expectContains(manifest_checker, "REQUIRED_TOOLING");
    try expectContains(manifest_checker, "\"supported_modes\": [\"text\", \"json\", \"bytes\"]");
    try expectContains(manifest_checker, "PRIMARY_TOOL_MARKERS");
    try expectContains(manifest_checker, "EXPECTED_CONSUMER_MARKERS");
    try expectContains(manifest_checker, "REQUIRED_NOTE_MARKERS");
    try expectContains(manifest_checker, "scripts/zigux/check-kconfig-bridge.py");
    try expectContains(manifest_checker, "scripts/zigux/check-fixdep-diff.py");
}
