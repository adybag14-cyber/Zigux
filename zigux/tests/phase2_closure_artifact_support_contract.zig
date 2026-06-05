const std = @import("std");

const testing = std.testing;

const ROOT = "";

const PHASE2_CLOSURE = ROOT ++ "Documentation/zigux/phase2-closure.md";
const PHASE2_TOOL_MANIFEST = ROOT ++ "zigux/tests/fixtures/phase2_tool_manifest.json";
const ARTIFACT_MANIFEST = ROOT ++ "zigux/tests/fixtures/phase2_artifact_tools_manifest.json";
const ARTIFACT_CHECKER = ROOT ++ "scripts/zigux/check-phase2-artifact-tools-manifest.py";
const ARTIFACT_DIFF = ROOT ++ "scripts/zigux/artifact_diff.py";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase2 closure note keeps artifact-support surface parked in the shared packet" {
    const allocator = testing.allocator;
    const closure = try readFile(allocator, PHASE2_CLOSURE);
    defer allocator.free(closure);

    try expectContains(
        closure,
        "`scripts/zigux/artifact_diff.py` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` remain the current artifact-support reminder pair",
    );
    try expectContains(closure, "python3 scripts/zigux/check-phase2-artifact-tools-manifest.py");
    try expectContains(
        closure,
        "PHASE2_SHARED_TOOLING_CHECKERS=python3 scripts/zigux/check-phase2-tool-manifest.py,python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py,python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    );
    try expectNotContains(closure, "sha256-only artifact diff");
}

test "phase2 tool manifest keeps artifact helper and checker visible beside closure tooling" {
    const allocator = testing.allocator;
    const manifest = try readFile(allocator, PHASE2_TOOL_MANIFEST);
    defer allocator.free(manifest);

    try expectContains(manifest, "\"artifact_support\"");
    try expectContains(manifest, "\"scripts/zigux/artifact_diff.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-artifact-tools-manifest.py\"");
    try expectContains(manifest, "\"zigux/tests/fixtures/phase2_artifact_tools_manifest.json\"");
    try expectContains(
        manifest,
        "Keep the dedicated manifest guards, the bootstrap workflow-routes guard, the primary artifact_diff helper",
    );
}

test "artifact-support manifest pins consumers, modes, and legacy alias note" {
    const allocator = testing.allocator;
    const manifest = try readFile(allocator, ARTIFACT_MANIFEST);
    defer allocator.free(manifest);

    try expectContains(manifest, "\"scope\": \"artifact-diff support for fixture-backed scripts/zigux validation\"");
    try expectContains(manifest, "\"scripts/zigux/check-kconfig-bridge.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-fixdep-diff.py\"");
    try expectContains(manifest, "\"supported_modes\": [\n      \"text\",\n      \"json\",\n      \"bytes\"\n    ]");
    try expectContains(
        manifest,
        "Keep the legacy `sha256` compatibility alias explicit as the path that normalizes to the shipped `bytes` comparison surface in `scripts/zigux/artifact_diff.py`.",
    );
}

test "artifact manifest checker and primary helper still agree on the compatibility surface" {
    const allocator = testing.allocator;
    const checker = try readFile(allocator, ARTIFACT_CHECKER);
    defer allocator.free(checker);
    const helper = try readFile(allocator, ARTIFACT_DIFF);
    defer allocator.free(helper);

    try expectContains(checker, "\"supported_modes\": [\"text\", \"json\", \"bytes\"]");
    try expectContains(checker, "'LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}'");
    try expectContains(checker, "\"legacy_sha256_alias\",");
    try expectContains(checker, "\"scripts/zigux/check-kconfig-bridge.py\"");
    try expectContains(checker, "\"scripts/zigux/check-fixdep-diff.py\"");

    try expectContains(helper, "MODE_CHOICES = (\"text\", \"json\", \"bytes\")");
    try expectContains(helper, "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}");
    try expectContains(helper, "return LEGACY_MODE_ALIASES.get(mode, mode)");
    try expectContains(helper, "\"legacy_sha256_alias\",");
}
