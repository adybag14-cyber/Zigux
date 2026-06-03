const std = @import("std");

const max_doc_size = 96 * 1024;
const max_tool_size = 128 * 1024;
const max_manifest_size = 16 * 1024;

fn readRepoFile(relative_path: []const u8, max_size: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        relative_path,
        std.testing.allocator,
        .limited(max_size),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "Phase 2 artifact-diff docs stay reconciled with the live support manifest" {
    const artifact_note = try readRepoFile("Documentation/zigux/artifact-diff.md", max_doc_size);
    defer std.testing.allocator.free(artifact_note);
    const bootstrap_note = try readRepoFile("Documentation/zigux/phase2-toolchain-bootstrap-notes.md", max_doc_size);
    defer std.testing.allocator.free(bootstrap_note);
    const manifest = try readRepoFile("zigux/tests/fixtures/phase2_artifact_tools_manifest.json", max_manifest_size);
    defer std.testing.allocator.free(manifest);
    const checker = try readRepoFile("scripts/zigux/check-phase2-artifact-tools-manifest.py", max_tool_size);
    defer std.testing.allocator.free(checker);

    try expectContains(
        artifact_note,
        "Phase 2 still routes focused host-tool fixture comparisons through the same helper family when validating `fixdep` and the kconfig bridge packet.",
    );
    try expectContains(
        artifact_note,
        "The current `genksyms` bridge packet keeps its fixture comparisons local to `scripts/zigux/check-genksyms-bridge.py`.",
    );

    const note_packet_markers = [_][]const u8{
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
        "scripts/zigux/artifact_diff.py",
        "scripts/zigux/check-kconfig-bridge.py",
        "scripts/zigux/check-fixdep-diff.py",
        "text",
        "json",
        "bytes",
        "sha256",
    };
    for (note_packet_markers) |marker| {
        try expectContains(bootstrap_note, marker);
    }

    try expectContains(
        manifest,
        "The artifact diff helper provides deterministic comparison output for fixture-backed scripts-root checks in both the kconfig bridge and fixdep parity packets.",
    );
    try expectContains(manifest, "scripts/zigux/check-phase2-artifact-tools-manifest.py");
    try expectContains(manifest, "scripts/zigux/artifact_diff.py");
    try expectContains(manifest, "scripts/zigux/check-kconfig-bridge.py");
    try expectContains(manifest, "scripts/zigux/check-fixdep-diff.py");
    try expectContains(manifest, "text");
    try expectContains(manifest, "json");
    try expectContains(manifest, "bytes");
    try expectContains(
        checker,
        "Keep future Phase 2 artifact-diff follow-up bounded to live consumers like `scripts/zigux/check-kconfig-bridge.py` and `scripts/zigux/check-fixdep-diff.py` plus directly readable fixture packets before widening into broader closure routes.",
    );
    try expectContains(checker, "scripts/zigux/artifact_diff.py");
    try expectContains(checker, "scripts/zigux/check-kconfig-bridge.py");
    try expectContains(checker, "scripts/zigux/check-fixdep-diff.py");
    try expectContains(checker, "text");
    try expectContains(checker, "json");
    try expectContains(checker, "bytes");
    try expectContains(checker, "sha256");
}

test "Phase 2 artifact-diff helper and consumers keep the documented comparison surface" {
    const helper = try readRepoFile("scripts/zigux/artifact_diff.py", max_tool_size);
    defer std.testing.allocator.free(helper);
    const kconfig_checker = try readRepoFile("scripts/zigux/check-kconfig-bridge.py", max_tool_size);
    defer std.testing.allocator.free(kconfig_checker);
    const fixdep_checker = try readRepoFile("scripts/zigux/check-fixdep-diff.py", max_tool_size);
    defer std.testing.allocator.free(fixdep_checker);

    const helper_markers = [_][]const u8{
        "MODE_CHOICES = (\"text\", \"json\", \"bytes\")",
        "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}",
        "\"legacy_sha256_alias\"",
        "def normalize_mode(mode: str) -> str:",
        "return LEGACY_MODE_ALIASES.get(mode, mode)",
    };
    for (helper_markers) |marker| {
        try expectContains(helper, marker);
    }

    try expectContains(kconfig_checker, "ARTIFACT_DIFF = ROOT / \"scripts\" / \"zigux\" / \"artifact_diff.py\"");
    try expectContains(kconfig_checker, "\"--mode\", \"json\"");
    try expectContains(fixdep_checker, "ARTIFACT_DIFF = ROOT / \"scripts\" / \"zigux\" / \"artifact_diff.py\"");
    try expectContains(fixdep_checker, "\"--mode\", \"text\"");
    try expectContains(fixdep_checker, "diff_text(expected_stdout, zig_actual)");
}
