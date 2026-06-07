const std = @import("std");
const testing = std.testing;

const max_doc_bytes = 256 * 1024;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(max_doc_bytes));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

test "bootstrap ledger keeps Lane 25 as the last bounded early-train item" {
    const ledger = try readRepoFile(testing.allocator, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md");
    defer testing.allocator.free(ledger);

    try expectContains(ledger, "25. `docs(zigux): reopen and close broadened Phase 2 tranche`");
    try expectContains(ledger, "- `Documentation/zigux/phase2-closure.md`");
    try expectContains(ledger, "- `Documentation/zigux/artifact-diff.md`");
    try expectContains(ledger, "- `scripts/zigux/README.md`");
    try expectContains(ledger, "- `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`");
    try expectContains(ledger, "- This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.");
    try expectContains(ledger, "- Keep this ledger authoritative for the reviewed bootstrap commit train through item 25 only.");
    try expectOrdered(
        ledger,
        "25. `docs(zigux): reopen and close broadened Phase 2 tranche`",
        "## Release-Planning Continuation",
    );
    try expectNotContains(ledger, "26. `");
}

test "ledger continuation points later work at live docs-root and sample packets" {
    const ledger = try readRepoFile(testing.allocator, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md");
    defer testing.allocator.free(ledger);

    try expectContains(ledger, "## Release-Planning Continuation");
    try expectContains(ledger, "- Do not backfill later release-planning state here as synthetic commit history when the live repo already exposes the active PMO packet directly.");
    try expectContains(ledger, "- `Documentation/zigux/README.md`");
    try expectContains(ledger, "- `Documentation/zigux/phase12-release-sequencing.md`");
    try expectContains(ledger, "- `Documentation/zigux/phase14-release-boundary-survey.md`");
    try expectContains(ledger, "- For the active Phase 5 non-runtime sample tranche, treat the landed closure note as the ledger-side handoff instead of inventing synthetic later-train commit entries:");
    try expectContains(ledger, "- `Documentation/zigux/phase5-closure.md`");
    try expectContains(ledger, "- use this ledger when the question is which reviewed bootstrap tranche changes landed through the bounded early train");
    try expectContains(ledger, "- use the docs-root PMO packet when the question is which release-planning surfaces currently govern later-phase release work on `master`");
    try expectContains(ledger, "- use the Phase 5 closure note plus its two shared reminder companions when the question is which active non-runtime sample tranche evidence currently governs the bounded Phase 5 lane on `master`");
}

test "companion docs keep the broadened Phase 2 tranche anchors live" {
    const closure = try readRepoFile(testing.allocator, "Documentation/zigux/phase2-closure.md");
    defer testing.allocator.free(closure);
    const artifact_diff = try readRepoFile(testing.allocator, "Documentation/zigux/artifact-diff.md");
    defer testing.allocator.free(artifact_diff);
    const scripts_readme = try readRepoFile(testing.allocator, "scripts/zigux/README.md");
    defer testing.allocator.free(scripts_readme);

    try expectContains(closure, "PHASE2_STATUS=parked");
    try expectContains(closure, "PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest");
    try expectContains(closure, "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2");

    try expectContains(artifact_diff, "# Zigux Artifact-Diff Notes");
    try expectContains(artifact_diff, "Phase 2 still routes focused host-tool fixture comparisons through the same helper family when validating `fixdep` and the kconfig bridge packet.");
    try expectContains(artifact_diff, "The current `genksyms` bridge packet keeps its fixture comparisons local to `scripts/zigux/check-genksyms-bridge.py`.");

    try expectContains(scripts_readme, "## Phase 2");
    try expectContains(scripts_readme, "Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet, tool-manifest packet, artifact-support packet, `scripts/zigux/check-genksyms-bridge.py`, fixdep packet, and returned make wrappers");
    try expectContains(scripts_readme, "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, and `zigux/tests/fixtures/kconfig_bridge/cases.json` keep the manifest-backed kconfig fixture roster explicit beside the pinned `phase2-kconfig` route.");
}
