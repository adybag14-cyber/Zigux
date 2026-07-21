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

test "phase2 closure keeps artifact support and shared tooling packet explicit" {
    const closure = try readRepoFile("Documentation/zigux/phase2-closure.md", 128 * 1024);
    defer std.testing.allocator.free(closure);

    try expectContains(closure, "PHASE2_STATUS=parked");
    try expectContains(closure, "PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest");
    try expectContains(closure, "scripts\zigux/check_phase2_artifact_tools_manifest.zig");
    try expectContains(closure, "`scripts/zigux/artifact_diff.zig` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` remain the current artifact-support reminder pair");
    try expectContains(closure, "PHASE2_SHARED_TOOLING_CHECKERS=zig run scripts/zigux/check_phase2_tool_manifest.zig,zig run scripts/zigux/check_phase2_bootstrap_workflow_routes.zig,zig run scripts/zigux/check_phase2_artifact_tools_manifest.zig");
    try expectContains(closure, "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2");

    try expectOrder(
        closure,
        "## Current Genksyms Evidence",
        "## Current Shared Repo-Tooling Evidence",
    );
    try expectOrder(
        closure,
        "scripts\zigux/check_phase2_artifact_tools_manifest.zig",
        "PHASE2_SHARED_TOOLING_CHECKERS=",
    );
}

test "artifact diff note preserves phase2 comparison ownership boundary" {
    const artifact_note = try readRepoFile("Documentation/zigux/artifact-diff.md", 128 * 1024);
    defer std.testing.allocator.free(artifact_note);

    try expectContains(artifact_note, "## Current Phase 2 use");
    try expectContains(artifact_note, "Phase 2 still routes focused host-tool fixture comparisons through the same helper family when validating `fixdep` and the kconfig bridge packet.");
    try expectContains(artifact_note, "The current `genksyms` bridge packet keeps its fixture comparisons local to `scripts\zigux/check_genksyms_bridge.zig`.");
    try expectContains(artifact_note, "scripts/zigux/artifact_diff.zig");
    try expectContains(artifact_note, "text`, `json`, and `bytes` artifacts");

    try expectOrder(artifact_note, "## Current Phase 1 use", "## Current Phase 2 use");
    try expectOrder(artifact_note, "## Current Phase 2 use", "## Current Phase 3 use");
    try expectOrder(
        artifact_note,
        "Phase 2 still routes focused host-tool fixture comparisons",
        "The current `genksyms` bridge packet keeps its fixture comparisons local",
    );
}

test "scripts readme and bootstrap ledger keep the broadened phase2 tranche handoff aligned" {
    const scripts_readme = try readRepoFile("scripts/zigux/README.md", 256 * 1024);
    defer std.testing.allocator.free(scripts_readme);
    const ledger = try readRepoFile("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md", 128 * 1024);
    defer std.testing.allocator.free(ledger);

    try expectContains(scripts_readme, "Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker");
    try expectContains(scripts_readme, "scripts\zigux/check_phase2_docs_shared_reminder.zig");
    try expectContains(scripts_readme, "scripts\zigux/check_phase2_required_make_routes.zig");
    try expectContains(scripts_readme, "scripts\zigux/check_phase2_artifact_tools_manifest.zig");
    try expectContains(scripts_readme, "zigux/tests/fixtures/phase2_artifact_tools_manifest.json");
    try expectContains(scripts_readme, "make -C zigux phase2-toolchain");
    try expectContains(scripts_readme, "make -C zigux phase2");

    try expectContains(ledger, "25. `docs(zigux): reopen and close broadened Phase 2 tranche`");
    try expectContains(ledger, "Documentation/zigux/phase2-closure.md");
    try expectContains(ledger, "Documentation/zigux/artifact-diff.md");
    try expectContains(ledger, "scripts/zigux/README.md");
    try expectContains(ledger, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md");
    try expectContains(ledger, "This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.");

    try expectOrder(
        ledger,
        "22. `docs(zigux): close bounded Phase 2 toolchain tranche`",
        "25. `docs(zigux): reopen and close broadened Phase 2 tranche`",
    );
}
