const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

const phase2_ledger_files = [_][]const u8{
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/artifact-diff.md",
    "scripts/zigux/README.md",
    "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
};

const phase2_replay_routes = [_][]const u8{
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
};

const phase2_shared_checkers = [_][]const u8{
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py",
    "python3 scripts/zigux/check-phase2-tool-manifest.py",
    "python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "python3 scripts/zigux/check-phase2-cross.py",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "python3 scripts/zigux/check-fixdep-diff.py",
};

test "bootstrap ledger keeps the broadened phase 2 tranche bounded and explicit" {
    const ledger = try readRepoFile("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md", 96 * 1024);
    defer std.testing.allocator.free(ledger);

    try expectContains(ledger, "# Zigux Alpha Bootstrap Commit Ledger");
    try expectContains(ledger, "25. `docs(zigux): reopen and close broadened Phase 2 tranche`");
    for (phase2_ledger_files) |path| {
        try expectContains(ledger, path);
    }

    try expectContains(ledger, "This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.");
    try expectContains(ledger, "Keep this ledger authoritative for the reviewed bootstrap commit train through item 25 only.");
    try expectContains(ledger, "Do not backfill later release-planning state here as synthetic commit history when the live repo already exposes the active PMO packet directly.");
    try expectContains(ledger, "For current release sequencing, tranche-closure posture, and release-coordination follow-through on `master`, continue from the docs-root PMO packet instead:");
    try expectContains(ledger, "use this ledger when the question is which reviewed bootstrap tranche changes landed through the bounded early train");
    try expectContains(ledger, "use the docs-root PMO packet when the question is which release-planning surfaces currently govern later-phase release work on `master`");
    try expectContains(ledger, "use the Phase 5 closure note plus its two shared reminder companions when the question is which active non-runtime sample tranche evidence currently governs the bounded Phase 5 lane on `master`");

    try expectNotContains(ledger, "26. `");
}

test "phase 2 closure and docs root stay aligned with the ledger handoff" {
    const ledger = try readRepoFile("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md", 96 * 1024);
    defer std.testing.allocator.free(ledger);

    const closure = try readRepoFile("Documentation/zigux/phase2-closure.md", 128 * 1024);
    defer std.testing.allocator.free(closure);

    const docs_root = try readRepoFile("Documentation/zigux/README.md", 256 * 1024);
    defer std.testing.allocator.free(docs_root);

    try expectContains(closure, "PHASE2_STATUS=parked");
    try expectContains(closure, "PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest");
    try expectContains(closure, "manifest: `zigux/tests/fixtures/phase2_tool_manifest.json`");
    try expectContains(closure, "shared note: `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`");
    try expectContains(closure, "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md");
    try expectContains(closure, "Documentation/zigux/phase2-conf-bridge-survey.md");
    try expectContains(closure, "PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md");
    try expectContains(closure, "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py");
    for (phase2_replay_routes) |route| {
        try expectContains(closure, route);
    }
    for (phase2_shared_checkers) |checker| {
        try expectContains(closure, checker);
    }

    try expectContains(docs_root, "Phase 2 notes");
    try expectContains(docs_root, "Documentation/zigux/phase2-closure.md");
    try expectContains(docs_root, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    try expectContains(docs_root, "scripts/zigux/README.md");
    try expectContains(docs_root, "zigux/tests/fixtures/phase2_tool_manifest.json");
    try expectContains(docs_root, "zigux/tests/fixtures/phase2_artifact_tools_manifest.json");
    try expectContains(docs_root, "zigux/Makefile");
    try expectContains(docs_root, "current docs-root Phase 2 reminder packet should stay parked");
    for (phase2_replay_routes) |route| {
        try expectContains(docs_root, route);
    }

    try expectContains(ledger, "Documentation/zigux/phase2-closure.md");
    try expectContains(ledger, "scripts/zigux/README.md");
}

test "scripts and tests roots expose the same phase 2 replay packet" {
    const scripts_readme = try readRepoFile("scripts/zigux/README.md", 256 * 1024);
    defer std.testing.allocator.free(scripts_readme);

    const tests_readme = try readRepoFile("zigux/tests/README.md", 256 * 1024);
    defer std.testing.allocator.free(tests_readme);

    try expectContains(scripts_readme, "## Phase 2");
    try expectContains(scripts_readme, "scripts/zigux/check-zig-toolchain.py");
    try expectContains(scripts_readme, "scripts/zigux/check-phase2-kbuild-routes.py");
    try expectContains(scripts_readme, "scripts/zigux/check-phase2-docs-shared-reminder.py");
    try expectContains(scripts_readme, "scripts/zigux/check-phase2-required-make-routes.py");
    try expectContains(scripts_readme, "scripts/zigux/check-phase2-tool-manifest.py");
    try expectContains(scripts_readme, "scripts/zigux/check-phase2-artifact-tools-manifest.py");
    try expectContains(scripts_readme, "scripts/zigux/check-genksyms-bridge.py");
    try expectContains(scripts_readme, "scripts/zigux/check-phase2-fixdep-gate.py");
    try expectContains(scripts_readme, "scripts/zigux/check-fixdep-diff.py");
    try expectContains(scripts_readme, "scripts/zigux/kconfig/conf_bridge.zig");
    try expectContains(scripts_readme, "scripts/zigux/kconfig/confdata_bridge.zig");
    for (phase2_replay_routes) |route| {
        try expectContains(scripts_readme, route);
    }

    try expectContains(tests_readme, "## Phase 2 review packet");
    try expectContains(tests_readme, "current direct-readback Phase 2 kconfig, genksyms, and fixdep packet");
    try expectContains(tests_readme, "Documentation/zigux/phase2-closure.md");
    try expectContains(tests_readme, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    try expectContains(tests_readme, "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md");
    try expectContains(tests_readme, "scripts/zigux/README.md");
    try expectContains(tests_readme, "scripts/zigux/validate-phase2.py");
    try expectContains(tests_readme, "scripts/zigux/validate-phase2-closure.py");
    try expectContains(tests_readme, "zigux/tests/fixtures/phase2_tool_manifest.json");
    try expectContains(tests_readme, "zigux/tests/fixtures/phase2_artifact_tools_manifest.json");
    try expectContains(tests_readme, "zigux/tests/fixtures/phase2_cross_targets.json");
    try expectContains(tests_readme, "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json");
    try expectContains(tests_readme, "zigux/tests/fixtures/genksyms_bridge/manifest.json");
    try expectContains(tests_readme, "zigux/tests/fixtures/fixdep/cases.json");
    for (phase2_replay_routes) |route| {
        try expectContains(tests_readme, route);
    }
}
