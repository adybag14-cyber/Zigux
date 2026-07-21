const std = @import("std");

const phase2_closure_artifact_support =
    \\- `scripts/zigux/artifact_diff.zig` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` remain the current artifact-support reminder pair instead of falling back into repo-reality-gap wording.
    \\- `zig run scripts/zigux/check_phase2_artifact_tools_manifest.zig`
;

const artifact_diff_phase2_note =
    \\Phase 2 still routes focused host-tool fixture comparisons through the same helper family when validating `fixdep` and the kconfig bridge packet. The current `genksyms` bridge packet keeps its fixture comparisons local to `scripts\zigux/check_genksyms_bridge.zig`.
;

const scripts_readme_phase2_packet =
    \\`scripts\zigux/check_phase2_artifact_tools_manifest.zig`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/install_zig.zig`, `zig run scripts/zigux/install_zig.zig -- --self-test`, `zig run scripts/zigux/check_phase2_cross.zig -- --self-test`, `zig run scripts/zigux/check_phase2_cross.zig`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`
;

const bootstrap_ledger_lane25 =
    \\25. `docs(zigux): reopen and close broadened Phase 2 tranche`
    \\- `Documentation/zigux/phase2-closure.md`
    \\- `Documentation/zigux/artifact-diff.md`
    \\- `scripts/zigux/README.md`
    \\- `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`
;

const artifact_support_manifest = "zigux/tests/fixtures/phase2_artifact_tools_manifest.json";
const artifact_diff_helper = "scripts/zigux/artifact_diff.zig";
const artifact_manifest_checker = "scripts\zigux/check_phase2_artifact_tools_manifest.zig";

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase2 closure keeps artifact support as current reminder evidence" {
    try expectContains(phase2_closure_artifact_support, artifact_diff_helper);
    try expectContains(phase2_closure_artifact_support, artifact_support_manifest);
    try expectContains(phase2_closure_artifact_support, artifact_manifest_checker);
    try expectContains(phase2_closure_artifact_support, "current artifact-support reminder pair");
    try expectContains(phase2_closure_artifact_support, "instead of falling back into repo-reality-gap wording");
}

test "artifact diff note keeps Phase 2 scope bounded to fixdep and kconfig comparisons" {
    try expectContains(artifact_diff_phase2_note, "Phase 2 still routes focused host-tool fixture comparisons");
    try expectContains(artifact_diff_phase2_note, "validating `fixdep` and the kconfig bridge packet");
    try expectContains(artifact_diff_phase2_note, "genksyms` bridge packet keeps its fixture comparisons local");
    try expectContains(artifact_diff_phase2_note, "scripts\zigux/check_genksyms_bridge.zig");
    try expectNotContains(artifact_diff_phase2_note, "standalone artifact replay entrypoints");
}

test "scripts README and bootstrap ledger name the same broadened Phase 2 docs packet" {
    try expectContains(scripts_readme_phase2_packet, artifact_manifest_checker);
    try expectContains(scripts_readme_phase2_packet, artifact_support_manifest);
    try expectContains(scripts_readme_phase2_packet, "directly readable on current `master`");
    try expectContains(bootstrap_ledger_lane25, "docs(zigux): reopen and close broadened Phase 2 tranche");
    try expectContains(bootstrap_ledger_lane25, "Documentation/zigux/phase2-closure.md");
    try expectContains(bootstrap_ledger_lane25, "Documentation/zigux/artifact-diff.md");
    try expectContains(bootstrap_ledger_lane25, "scripts/zigux/README.md");
    try expectContains(bootstrap_ledger_lane25, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md");
}
