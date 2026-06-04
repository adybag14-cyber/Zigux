const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrder(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.EarlierMarkerMissing;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.LaterMarkerMissing;
    try std.testing.expect(earlier_index < later_index);
}

test "phase2 closure keeps artifact support paired with shared tooling evidence" {
    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 128 * 1024);
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "## Current Shared Repo-Tooling Evidence");
    try expectContains(closure_note, "scripts/zigux/artifact_diff.py");
    try expectContains(closure_note, "zigux/tests/fixtures/phase2_artifact_tools_manifest.json");
    try expectContains(closure_note, "scripts/zigux/check-phase2-artifact-tools-manifest.py");
    try expectContains(closure_note, "remain the current artifact-support reminder pair");
    try expectContains(closure_note, "PHASE2_SHARED_TOOLING_CHECKERS=python3 scripts/zigux/check-phase2-tool-manifest.py,python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py,python3 scripts/zigux/check-phase2-artifact-tools-manifest.py");

    try expectOrder(
        closure_note,
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        "PHASE2_SHARED_TOOLING_CHECKERS=",
    );
    try expectOrder(
        closure_note,
        "## Current Shared Repo-Tooling Evidence",
        "## Shared Replay Routes",
    );
}

test "artifact diff note keeps phase2 consumer scope narrow and mode surface explicit" {
    const artifact_note = try readRepoFile("Documentation/zigux/artifact-diff.md", 128 * 1024);
    defer std.testing.allocator.free(artifact_note);

    try expectContains(artifact_note, "## Current Phase 2 use");
    try expectContains(artifact_note, "Phase 2 still routes focused host-tool fixture comparisons through the same helper family when validating `fixdep` and the kconfig bridge packet.");
    try expectContains(artifact_note, "The current `genksyms` bridge packet keeps its fixture comparisons local to `scripts/zigux/check-genksyms-bridge.py`.");
    try expectContains(artifact_note, "The helper now compares `text`, `json`, and `bytes` artifacts");
    try expectContains(artifact_note, "keeps the legacy `sha256 -> bytes` alias for compatibility");
    try expectContains(artifact_note, "ARTIFACT_DIFF_RESULT_LINES=ARTIFACT_DIFF,MODE,EXPECTED,ACTUAL[,SHA256|EXPECTED_EXISTS|ACTUAL_EXISTS|EXPECTED_JSON_ERROR|ACTUAL_JSON_ERROR|EXPECTED_UTF8_ERROR|ACTUAL_UTF8_ERROR]");

    try expectOrder(
        artifact_note,
        "## Current Phase 2 use",
        "## Current Phase 3 use",
    );
    try expectOrder(
        artifact_note,
        "The helper now compares `text`, `json`, and `bytes` artifacts",
        "The current helper self-test packet keeps these comparison and parser coverage families explicit:",
    );
}

test "scripts readme and bootstrap ledger keep broadened phase2 tranche bounded" {
    const scripts_readme = try readRepoFile("scripts/zigux/README.md", 256 * 1024);
    defer std.testing.allocator.free(scripts_readme);

    const ledger = try readRepoFile("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md", 128 * 1024);
    defer std.testing.allocator.free(ledger);

    try expectContains(scripts_readme, "## Phase 2");
    try expectContains(scripts_readme, "scripts/zigux/check-phase2-artifact-tools-manifest.py");
    try expectContains(scripts_readme, "zigux/tests/fixtures/phase2_artifact_tools_manifest.json");
    try expectContains(scripts_readme, "keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit");
    try expectContains(scripts_readme, "make -C zigux phase2-toolchain");
    try expectContains(scripts_readme, "make -C zigux phase2");

    try expectContains(ledger, "25. `docs(zigux): reopen and close broadened Phase 2 tranche`");
    try expectContains(ledger, "Documentation/zigux/phase2-closure.md");
    try expectContains(ledger, "Documentation/zigux/artifact-diff.md");
    try expectContains(ledger, "scripts/zigux/README.md");
    try expectContains(ledger, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md");
    try expectContains(ledger, "This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.");
    try expectContains(ledger, "Do not backfill later release-planning state here as synthetic commit history");
}

test "artifact tools checker and manifest keep phase2 artifact support details aligned" {
    const checker = try readRepoFile("scripts/zigux/check-phase2-artifact-tools-manifest.py", 128 * 1024);
    defer std.testing.allocator.free(checker);

    const manifest = try readRepoFile("zigux/tests/fixtures/phase2_artifact_tools_manifest.json", 64 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(checker, "PRIMARY_TOOL = Path(\"scripts/zigux/artifact_diff.py\")");
    try expectContains(checker, "\"supported_modes\": [\"text\", \"json\", \"bytes\"]");
    try expectContains(checker, "\"scripts/zigux/check-kconfig-bridge.py\"");
    try expectContains(checker, "\"scripts/zigux/check-fixdep-diff.py\"");
    try expectContains(checker, "\"PHASE2_ARTIFACT_TOOLS_MANIFEST=pass\"");
    try expectContains(checker, "\"PHASE2_ARTIFACT_TOOLS_MANIFEST_SELF_TEST_CASE_COUNT={checks_run}\"");

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
    try expectContains(manifest, "Keep future Phase 2 artifact-diff follow-up bounded to live consumers like `scripts/zigux/check-kconfig-bridge.py` and `scripts/zigux/check-fixdep-diff.py`");
    try expectContains(manifest, "Keep the legacy `sha256` compatibility alias explicit");
}
