const std = @import("std");

const max_file_size = 1024 * 1024;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(max_file_size));
}

fn expectContains(text: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, text, marker) != null);
}

fn countOccurrences(text: []const u8, marker: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, text, offset, marker)) |index| {
        count += 1;
        offset = index + marker.len;
    }
    return count;
}

fn expectOccursOnce(text: []const u8, marker: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(text, marker));
}

test "artifact-diff note keeps Phase 2 consumer boundary explicit" {
    const allocator = std.testing.allocator;
    const note = try readRepoFile(allocator, "Documentation/zigux/artifact-diff.md");
    defer allocator.free(note);

    try expectOccursOnce(note, "## Current Phase 2 use");
    try expectContains(note, "scripts/zigux/artifact_diff.py");
    try expectContains(
        note,
        "Phase 2 still routes focused host-tool fixture comparisons through the same helper family when validating `fixdep` and the kconfig bridge packet.",
    );
    try expectContains(
        note,
        "The current `genksyms` bridge packet keeps its fixture comparisons local to `scripts/zigux/check-genksyms-bridge.py`.",
    );
}

test "artifact-tools manifest mirrors the Phase 2 note scope" {
    const allocator = std.testing.allocator;
    const manifest = try readRepoFile(allocator, "zigux/tests/fixtures/phase2_artifact_tools_manifest.json");
    defer allocator.free(manifest);

    try expectContains(manifest, "\"phase\": \"Phase 2\"");
    try expectContains(manifest, "\"status\": \"active\"");
    try expectContains(manifest, "\"scope\": \"artifact-diff support for fixture-backed scripts/zigux validation\"");
    try expectContains(manifest, "\"scripts/zigux/artifact_diff.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-kconfig-bridge.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-fixdep-diff.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-artifact-tools-manifest.py\"");
    try expectContains(manifest, "\"text\"");
    try expectContains(manifest, "\"json\"");
    try expectContains(manifest, "\"bytes\"");
    try expectContains(
        manifest,
        "The artifact diff helper provides deterministic comparison output for fixture-backed scripts-root checks in both the kconfig bridge and fixdep parity packets.",
    );
    try expectContains(
        manifest,
        "Keep the legacy `sha256` compatibility alias explicit as the path that normalizes to the shipped `bytes` comparison surface in `scripts/zigux/artifact_diff.py`.",
    );
}

test "artifact-tools checker still guards the helper and live consumers" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase2-artifact-tools-manifest.py");
    defer allocator.free(checker);

    try expectContains(checker, "PRIMARY_TOOL = Path(\"scripts/zigux/artifact_diff.py\")");
    try expectContains(checker, "\"scripts/zigux/check-kconfig-bridge.py\"");
    try expectContains(checker, "\"scripts/zigux/check-fixdep-diff.py\"");
    try expectContains(checker, "\"supported_modes\": [\"text\", \"json\", \"bytes\"]");
    try expectContains(checker, "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}");
    try expectContains(checker, "PHASE2_ARTIFACT_TOOLS_MANIFEST=pass");
    try expectContains(checker, "PHASE2_ARTIFACT_TOOLS_MANIFEST_SELF_TEST=pass");
}

test "primary artifact-diff helper retains the documented Phase 2 surface" {
    const allocator = std.testing.allocator;
    const helper = try readRepoFile(allocator, "scripts/zigux/artifact_diff.py");
    defer allocator.free(helper);

    try expectContains(helper, "MODE_CHOICES = (\"text\", \"json\", \"bytes\")");
    try expectContains(helper, "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}");
    try expectContains(helper, "\"legacy_sha256_alias\",");
    try expectContains(helper, "def normalize_mode(mode: str) -> str:");
    try expectContains(helper, "return LEGACY_MODE_ALIASES.get(mode, mode)");
    try expectContains(helper, "ARTIFACT_DIFF_SELF_TEST=pass");
    try expectContains(helper, "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=");
}
