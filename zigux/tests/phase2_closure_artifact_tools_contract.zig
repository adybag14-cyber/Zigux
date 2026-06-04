const std = @import("std");
const testing = std.testing;

const artifact_tool_manifest = "zigux/tests/fixtures/phase2_artifact_tools_manifest.json";
const artifact_tool_checker = "scripts/zigux/check-phase2-artifact-tools-manifest.py";
const artifact_diff_helper = "scripts/zigux/artifact_diff.py";

const artifact_tool_modes = [_][]const u8{
    "\"text\"",
    "\"json\"",
    "\"bytes\"",
};

fn readText(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        path,
        testing.allocator,
        .limited(1024 * 1024),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireMissing(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

fn requireExactOnce(haystack: []const u8, needle: []const u8) !void {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    try testing.expectEqual(@as(usize, 1), count);
}

test "phase2 closure note keeps artifact tools out of repo-reality gaps" {
    const closure = try readText("Documentation/zigux/phase2-closure.md");
    defer testing.allocator.free(closure);

    try requireContains(closure, "## Current Shared Repo-Tooling Evidence");
    try requireContains(
        closure,
        "`scripts/zigux/artifact_diff.py` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` remain the current artifact-support reminder pair instead of falling back into repo-reality-gap wording.",
    );
    try requireContains(closure, artifact_tool_checker);
    try requireContains(closure, "python3 scripts/zigux/check-phase2-artifact-tools-manifest.py");
    try requireContains(closure, artifact_tool_manifest);
    try requireContains(closure, artifact_diff_helper);
    try requireExactOnce(closure, "`scripts/zigux/artifact_diff.py` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` remain the current artifact-support reminder pair");
    try requireOrdered(closure, "scripts/zigux/check-phase2-tool-manifest.py", artifact_tool_checker);
    try requireOrdered(closure, artifact_tool_checker, "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py");
    try requireMissing(closure, "artifact-tools packet remains missing");
}

test "phase2 artifact tools manifest and checker agree on helper surface" {
    const manifest = try readText(artifact_tool_manifest);
    defer testing.allocator.free(manifest);
    const checker = try readText(artifact_tool_checker);
    defer testing.allocator.free(checker);
    const helper = try readText(artifact_diff_helper);
    defer testing.allocator.free(helper);

    try requireContains(manifest, "\"phase\": \"Phase 2\"");
    try requireContains(manifest, "\"status\": \"active\"");
    try requireContains(manifest, "\"scope\": \"artifact-diff support for fixture-backed scripts/zigux validation\"");
    try requireContains(manifest, artifact_diff_helper);
    try requireContains(manifest, artifact_tool_checker);
    try requireContains(manifest, "scripts/zigux/check-kconfig-bridge.py");
    try requireContains(manifest, "scripts/zigux/check-fixdep-diff.py");
    for (artifact_tool_modes) |mode| {
        try requireContains(manifest, mode);
    }
    try requireContains(manifest, "Keep the legacy `sha256` compatibility alias explicit");

    try requireContains(checker, "MANIFEST = Path(\"zigux/tests/fixtures/phase2_artifact_tools_manifest.json\")");
    try requireContains(checker, "PRIMARY_TOOL = Path(\"scripts/zigux/artifact_diff.py\")");
    try requireContains(checker, "\"supported_modes\": [\"text\", \"json\", \"bytes\"]");
    try requireContains(checker, "PHASE2_ARTIFACT_TOOLS_MANIFEST=pass");
    try requireContains(checker, "PHASE2_ARTIFACT_TOOLS_MANIFEST_REQUIRED_TOOL_PATH_COUNT=");

    try requireContains(helper, "MODE_CHOICES = (\"text\", \"json\", \"bytes\")");
    try requireContains(helper, "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}");
    try requireContains(helper, "\"legacy_sha256_alias\"");
    try requireContains(helper, "def normalize_mode(mode: str) -> str:");
    try requireOrdered(helper, "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}", "def normalize_mode(mode: str) -> str:");
}

test "phase2 tests readme mirrors the closure artifact tools packet" {
    const tests_readme = try readText("zigux/tests/README.md");
    defer testing.allocator.free(tests_readme);
    const closure = try readText("Documentation/zigux/phase2-closure.md");
    defer testing.allocator.free(closure);

    try requireContains(tests_readme, "## Phase 2 review packet");
    try requireContains(tests_readme, artifact_tool_checker);
    try requireContains(tests_readme, artifact_tool_manifest);
    try requireContains(tests_readme, "fixture-backed tool-manifest and artifact-tools-manifest guards");
    try requireContains(tests_readme, "Keep the fixture-backed tool-manifest and artifact-tools-manifest guards");
    try requireOrdered(tests_readme, "scripts/zigux/check-phase2-tool-manifest.py", artifact_tool_checker);
    try requireOrdered(tests_readme, artifact_tool_checker, "scripts/zigux/check-phase2-required-make-routes.py");

    try requireContains(closure, artifact_tool_checker);
    try requireContains(closure, artifact_tool_manifest);
    try requireMissing(tests_readme, "PHASE2_ARTIFACT_TOOLS=missing");
}
