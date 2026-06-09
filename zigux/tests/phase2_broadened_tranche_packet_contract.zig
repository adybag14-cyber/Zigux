const std = @import("std");

const allocator = std.testing.allocator;
const max_file_size = 1024 * 1024;

fn readRepoFile(path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(max_file_size));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "bootstrap ledger item 25 still names the broadened Phase 2 tranche handoff" {
    const ledger = try readRepoFile("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md");
    defer allocator.free(ledger);

    try expectContains(ledger, "25. `docs(zigux): reopen and close broadened Phase 2 tranche`");
    try expectContains(ledger, "- `Documentation/zigux/phase2-closure.md`");
    try expectContains(ledger, "- `Documentation/zigux/artifact-diff.md`");
    try expectContains(ledger, "- `scripts/zigux/README.md`");
    try expectContains(ledger, "- `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`");
    try expectContains(ledger, "This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.");
    try expectContains(ledger, "Keep this ledger authoritative for the reviewed bootstrap commit train through item 25 only.");
}

test "Phase 2 closure packet keeps shared tooling and replay routes explicit" {
    const closure = try readRepoFile("Documentation/zigux/phase2-closure.md");
    defer allocator.free(closure);

    try expectContains(closure, "PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest");
    try expectContains(closure, "PHASE2_CURRENT_GENKSYMS_BRIDGE_PACKET=");
    try expectContains(closure, "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=");
    try expectContains(closure, "PHASE2_SHARED_TOOLING_CHECKERS=python3 scripts/zigux/check-phase2-tool-manifest.py");
    try expectContains(closure, "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2");
    try expectContains(closure, "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py");
    try expectContains(closure, "PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md");
}

test "artifact, scripts-root, and manifest surfaces still mirror the Phase 2 tool packet" {
    const artifact = try readRepoFile("Documentation/zigux/artifact-diff.md");
    defer allocator.free(artifact);
    const scripts_readme = try readRepoFile("scripts/zigux/README.md");
    defer allocator.free(scripts_readme);
    const manifest = try readRepoFile("zigux/tests/fixtures/phase2_tool_manifest.json");
    defer allocator.free(manifest);

    try expectContains(artifact, "Phase 2 still routes focused host-tool fixture comparisons through the same helper family when validating `fixdep` and the kconfig bridge packet.");
    try expectContains(artifact, "The current `genksyms` bridge packet keeps its fixture comparisons local to `scripts/zigux/check-genksyms-bridge.py`.");
    try expectContains(scripts_readme, "Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker");
    try expectContains(scripts_readme, "`scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit");
    try expectContains(scripts_readme, "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, and `zigux/tests/fixtures/kconfig_bridge/cases.json` keep the manifest-backed kconfig fixture roster explicit");
    try expectContains(manifest, "\"phase\": \"Phase 2\"");
    try expectContains(manifest, "\"status\": \"active\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-fixdep-gate.py\"");
    try expectContains(manifest, "\"make -C zigux phase2\"");
}
