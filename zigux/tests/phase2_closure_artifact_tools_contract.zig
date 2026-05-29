const std = @import("std");

const closure_note_path = "Documentation/zigux/phase2-closure.md";
const artifact_checker_path = "scripts/zigux/check-phase2-artifact-tools-manifest.py";
const artifact_manifest_path = "zigux/tests/fixtures/phase2_artifact_tools_manifest.json";

const artifact_tool_paths = [_][]const u8{
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
};

const supported_modes = [_][]const u8{
    "\"text\"",
    "\"json\"",
    "\"bytes\"",
};

const required_note_markers = [_][]const u8{
    "The artifact diff helper provides deterministic comparison output for fixture-backed scripts-root checks in both the kconfig bridge and fixdep parity packets.",
    "Keep `scripts/zigux/check-phase2-artifact-tools-manifest.py` explicit so the bounded Phase 2 artifact-support manifest fails closed beside the broader Phase 2 tool packet.",
    "Keep future Phase 2 artifact-diff follow-up bounded to live consumers like `scripts/zigux/check-kconfig-bridge.py` and `scripts/zigux/check-fixdep-diff.py` plus directly readable fixture packets before widening into broader closure routes.",
    "Keep the legacy `sha256` compatibility alias explicit as the path that normalizes to the shipped `bytes` comparison surface in `scripts/zigux/artifact_diff.py`.",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    return try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase2 closure note keeps artifact-support checker and manifest explicit" {
    const allocator = std.testing.allocator;
    const closure_note = try readRepoFile(allocator, closure_note_path);
    defer allocator.free(closure_note);

    try expectContains(closure_note, "PHASE2_STATUS=parked");
    try expectContains(closure_note, "## Current Shared Repo-Tooling Evidence");
    try expectContains(closure_note, "scripts/zigux/check-phase2-artifact-tools-manifest.py");
    try expectContains(closure_note, "scripts/zigux/artifact_diff.py");
    try expectContains(closure_note, "zigux/tests/fixtures/phase2_artifact_tools_manifest.json");
    try expectContains(closure_note, "PHASE2_SHARED_TOOLING_CHECKERS=");
    try expectContains(closure_note, "python3 scripts/zigux/check-phase2-artifact-tools-manifest.py");
}

test "artifact tools manifest preserves exact tool roster and mode order" {
    const allocator = std.testing.allocator;
    const manifest = try readRepoFile(allocator, artifact_manifest_path);
    defer allocator.free(manifest);

    try expectContains(manifest, "\"phase\": \"Phase 2\"");
    try expectContains(manifest, "\"status\": \"active\"");
    try expectContains(manifest, "\"scope\": \"artifact-diff support for fixture-backed scripts/zigux validation\"");
    for (artifact_tool_paths) |path| {
        try expectContains(manifest, path);
    }
    for (supported_modes) |mode| {
        try expectContains(manifest, mode);
    }
    try expectContains(manifest, "\"primary\": [");
    try expectContains(manifest, "\"consumers\": [");
    try expectContains(manifest, "\"checkers\": [");
}

test "artifact tools manifest notes stay aligned with checker contract" {
    const allocator = std.testing.allocator;
    const manifest = try readRepoFile(allocator, artifact_manifest_path);
    defer allocator.free(manifest);
    const checker = try readRepoFile(allocator, artifact_checker_path);
    defer allocator.free(checker);

    for (required_note_markers) |marker| {
        try expectContains(manifest, marker);
        try expectContains(checker, marker);
    }
    try expectContains(checker, "REQUIRED_NOTE_MARKERS");
    try expectContains(checker, "NOTE_ORDER_MISMATCH");
    try expectContains(checker, "DUPLICATE_NOTE_ENTRY");
}

test "artifact tools checker guards primary helper and consumer markers" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, artifact_checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "PRIMARY_TOOL_MARKERS");
    try expectContains(checker, "EXPECTED_CONSUMER_MARKERS");
    try expectContains(checker, "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}");
    try expectContains(checker, "def normalize_mode(mode: str) -> str:");
    try expectContains(checker, "PRIMARY_TOOL_SUPPORTED_MODES_MISMATCH");
    try expectContains(checker, "MISSING_CONSUMER_MARKER");
    try expectContains(checker, "PHASE2_ARTIFACT_TOOLS_MANIFEST=pass");
    try expectContains(checker, "PHASE2_ARTIFACT_TOOLS_MANIFEST_SELF_TEST=pass");
}
