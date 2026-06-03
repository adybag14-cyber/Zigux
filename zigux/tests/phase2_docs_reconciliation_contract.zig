const std = @import("std");
const testing = std.testing;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_thread: std.Io.Threaded = .init(allocator, .{});
    defer io_thread.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_thread.io(), path, allocator, .limited(1024 * 1024));
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const relative = std.mem.indexOf(u8, haystack[cursor..], needle);
        try testing.expect(relative != null);
        cursor += relative.? + needle.len;
    }
}

test "phase2 closure note owns the broadened shared tooling packet" {
    const phase2_closure = try readRepoFile(testing.allocator, "Documentation/zigux/phase2-closure.md");
    defer testing.allocator.free(phase2_closure);

    try requireContains(phase2_closure, "PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest");
    try requireContains(phase2_closure, "manifest: `zigux/tests/fixtures/phase2_tool_manifest.json`");
    try requireContains(phase2_closure, "shared note: `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`");
    try requireContains(phase2_closure, "PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT=16");
    try requireContains(phase2_closure, "PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT=36");
    try requireContains(phase2_closure, "scripts/zigux/artifact_diff.py and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`");
    try requireContains(phase2_closure, "PHASE2_SHARED_TOOLING_CHECKERS=python3 scripts/zigux/check-phase2-tool-manifest.py,python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py,python3 scripts/zigux/check-phase2-artifact-tools-manifest.py,python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py,python3 scripts/zigux/check-phase2-cross.py,python3 scripts/zigux/check-phase2-fixdep-gate.py,python3 scripts/zigux/check-fixdep-diff.py");
    try requireContains(phase2_closure, "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2");

    try requireOrdered(phase2_closure, &.{
        "## Current Genksyms Evidence",
        "## Current Shared Repo-Tooling Evidence",
        "## Shared Replay Routes",
        "## Repo-Reality Gaps",
        "## Next Step",
    });
}

test "artifact diff note stays aligned with the Phase 2 reconciliation boundary" {
    const artifact_diff_note = try readRepoFile(testing.allocator, "Documentation/zigux/artifact-diff.md");
    defer testing.allocator.free(artifact_diff_note);

    try requireContains(artifact_diff_note, "## Current Phase 2 use");
    try requireContains(artifact_diff_note, "Phase 2 still routes focused host-tool fixture comparisons through the same helper family when validating `fixdep` and the kconfig bridge packet.");
    try requireContains(artifact_diff_note, "The current `genksyms` bridge packet keeps its fixture comparisons local to `scripts/zigux/check-genksyms-bridge.py`.");
    try requireContains(artifact_diff_note, "text`, `json`, and `bytes` artifacts");
    try requireContains(artifact_diff_note, "legacy `sha256 -> bytes` alias");
}

test "scripts README and bootstrap ledger point at the same Lane 25 packet" {
    const scripts_readme = try readRepoFile(testing.allocator, "scripts/zigux/README.md");
    defer testing.allocator.free(scripts_readme);
    const bootstrap_ledger = try readRepoFile(testing.allocator, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md");
    defer testing.allocator.free(bootstrap_ledger);

    try requireContains(scripts_readme, "## Phase 2");
    try requireContains(scripts_readme, "Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet, tool-manifest packet, artifact-support packet, `scripts/zigux/check-genksyms-bridge.py`, fixdep packet, and returned make wrappers");
    try requireContains(scripts_readme, "scripts/zigux/check-phase2-artifact-tools-manifest.py");
    try requireContains(scripts_readme, "make -C zigux phase2-toolchain");
    try requireContains(scripts_readme, "scripts/zigux/check-phase2-kconfig-selftest-alignment.py");

    try requireOrdered(bootstrap_ledger, &.{
        "22. `docs(zigux): close bounded Phase 2 toolchain tranche`",
        "23. `feat(scripts/zigux): add bounded Phase 2 genksyms wrapper lane`",
        "24. `ci(zigux): widen Phase 2 closure matrix`",
        "25. `docs(zigux): reopen and close broadened Phase 2 tranche`",
        "- `Documentation/zigux/phase2-closure.md`",
        "- `Documentation/zigux/artifact-diff.md`",
        "- `scripts/zigux/README.md`",
        "- `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`",
    });
    try requireContains(bootstrap_ledger, "This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.");
}
