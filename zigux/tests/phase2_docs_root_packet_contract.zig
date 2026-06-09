const std = @import("std");
const testing = std.testing;

fn readRepoFile(path: []const u8) ![]const u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, path, testing.allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

test "docs root keeps the current Phase 2 packet explicit" {
    const docs_root = try readRepoFile("Documentation/zigux/README.md");
    defer testing.allocator.free(docs_root);

    try expectContains(docs_root, "Phase 2 notes");
    try expectContains(docs_root, "Documentation/zigux/phase2-closure.md");
    try expectContains(docs_root, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    try expectContains(docs_root, "Documentation/zigux/review-checklist.md");
    try expectContains(docs_root, "zigux/tests/README.md");
    try expectContains(docs_root, "scripts/zigux/README.md");
    try expectContains(docs_root, "zigux/tests/fixtures/phase2_tool_manifest.json");
    try expectContains(docs_root, "zigux/tests/fixtures/phase2_artifact_tools_manifest.json");
    try expectContains(docs_root, "zigux/tests/fixtures/phase2_cross_targets.json");
    try expectContains(docs_root, "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json");
    try expectContains(docs_root, "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json");
    try expectContains(docs_root, "scripts/zigux/kconfig/conf_bridge.zig");
    try expectContains(docs_root, "scripts/zigux/kconfig/confdata_bridge.zig");
    try expectContains(docs_root, "scripts/zigux/genksyms.zig");
    try expectContains(docs_root, "scripts/zigux/fixdep.zig");
    try expectContains(docs_root, "make -C zigux phase2-toolchain");
    try expectContains(docs_root, "make -C zigux phase2-fixdep");
    try expectContains(docs_root, "make -C zigux phase2");
    try expectBefore(docs_root, "Phase 2 notes", "Phase 3 notes");
}

test "review checklist keeps Phase 2 reviewer prompts aligned" {
    const review_checklist = try readRepoFile("Documentation/zigux/review-checklist.md");
    defer testing.allocator.free(review_checklist);

    try expectContains(review_checklist, "if the change touches the shared Phase 2 toolchain packet");
    try expectContains(review_checklist, "Documentation/zigux/README.md");
    try expectContains(review_checklist, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    try expectContains(review_checklist, "Documentation/zigux/phase2-closure.md");
    try expectContains(review_checklist, "scripts/zigux/validate-phase2.py");
    try expectContains(review_checklist, "scripts/zigux/validate-phase2-closure.py");
    try expectContains(review_checklist, "scripts/zigux/check-phase2-docs-shared-reminder.py");
    try expectContains(review_checklist, "scripts/zigux/check-phase2-tool-manifest.py");
    try expectContains(review_checklist, "scripts/zigux/check-phase2-artifact-tools-manifest.py");
    try expectContains(review_checklist, "scripts/zigux/check-genksyms-bridge.py");
    try expectContains(review_checklist, "scripts/zigux/check-phase2-fixdep-gate.py");
    try expectContains(review_checklist, "scripts/zigux/kconfig/conf_bridge.zig");
    try expectContains(review_checklist, "scripts/zigux/kconfig/confdata_bridge.zig");
    try expectContains(review_checklist, "zigux/tests/fixtures/fixdep/cases.json");
    try expectContains(review_checklist, "python3 scripts/zigux/check-phase2-tool-manifest.py");
    try expectContains(review_checklist, "make -C zigux phase2-genksyms");
    try expectContains(review_checklist, "make -C zigux phase2-fixdep");
    try expectBefore(review_checklist, "if the change touches the shared Phase 2 toolchain packet", "if the change touches the shared Phase 3 ABI/runtime packet");
}

test "direct Phase 2 companion surfaces name the same docs-root packet" {
    const tests_readme = try readRepoFile("zigux/tests/README.md");
    defer testing.allocator.free(tests_readme);
    const scripts_readme = try readRepoFile("scripts/zigux/README.md");
    defer testing.allocator.free(scripts_readme);
    const phase2_closure = try readRepoFile("Documentation/zigux/phase2-closure.md");
    defer testing.allocator.free(phase2_closure);

    try expectContains(tests_readme, "## Phase 2 review packet");
    try expectContains(tests_readme, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    try expectContains(tests_readme, "Documentation/zigux/phase2-closure.md");
    try expectContains(tests_readme, "scripts/zigux/check-phase2-docs-shared-reminder.py");
    try expectContains(tests_readme, "scripts/zigux/check-phase2-bootstrap-workflow-routes.py");
    try expectContains(tests_readme, "scripts/zigux/check-phase2-required-make-routes.py");
    try expectContains(tests_readme, "scripts/zigux/check-genksyms-bridge.py");
    try expectContains(tests_readme, "scripts/zigux/check-fixdep-diff.py");
    try expectContains(tests_readme, "make -C zigux phase2");

    try expectContains(scripts_readme, "## Phase 2");
    try expectContains(scripts_readme, "Phase 2 flow");
    try expectContains(scripts_readme, "scripts/zigux/check-phase2-docs-shared-reminder.py");
    try expectContains(scripts_readme, "scripts/zigux/check-phase2-required-make-routes.py");
    try expectContains(scripts_readme, "scripts/zigux/check-phase2-tool-manifest.py");
    try expectContains(scripts_readme, "scripts/zigux/check-phase2-artifact-tools-manifest.py");
    try expectContains(scripts_readme, "scripts/zigux/check-phase2-fixdep-gate.py");
    try expectContains(scripts_readme, "make -C zigux phase2-kconfig");

    try expectContains(phase2_closure, "PHASE2_STATUS=parked");
    try expectContains(phase2_closure, "PHASE2_SHARED_TOOLING_CHECKERS=");
    try expectContains(phase2_closure, "PHASE2_SHARED_MAKE_ROUTES=");
    try expectContains(phase2_closure, "PHASE2_CLOSURE_VALIDATORS=");
    try expectContains(phase2_closure, "PHASE2_CURRENT_GENKSYMS_BRIDGE_PACKET=");
    try expectContains(phase2_closure, "PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT=16");
    try expectContains(phase2_closure, "PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT=36");
}
