const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.EarlierMarkerMissing;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.LaterMarkerMissing;
    try std.testing.expect(earlier_index < later_index);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(512 * 1024));
}

test "phase 2 review checklist keeps closure packet runnable and explicit" {
    const allocator = std.testing.allocator;

    const checklist = try readRepoFile(allocator, "Documentation/zigux/review-checklist.md");
    defer allocator.free(checklist);

    try expectContains(checklist, "if the change touches the shared Phase 2 toolchain packet");
    try expectContains(checklist, "Documentation/zigux/phase2-closure.md");
    try expectContains(checklist, "scripts/zigux/validate-phase2.py");
    try expectContains(checklist, "scripts/zigux/validate-phase2-closure.py");
    try expectContains(checklist, "zigux/tests/fixtures/phase2_tool_manifest.json");
    try expectContains(checklist, "python3 scripts/zigux/check-phase2-tool-manifest.py");
    try expectContains(checklist, "python3 scripts/zigux/check-phase2-tool-manifest.py` explicit as the runnable shared Phase 2 tool-manifest gate");
    try expectContains(checklist, "make -C zigux phase2-toolchain");
    try expectContains(checklist, "make -C zigux phase2-tools");
    try expectContains(checklist, "make -C zigux phase2-kconfig");
    try expectContains(checklist, "make -C zigux phase2-cross");
    try expectContains(checklist, "make -C zigux phase2-genksyms");
    try expectContains(checklist, "make -C zigux phase2-fixdep");
    try expectContains(checklist, "make -C zigux phase2-validate");
    try expectContains(checklist, "make -C zigux phase2");
    try expectNotContains(checklist, "check-phase2-tool-manifest-packets.py");

    try expectBefore(checklist, "Documentation/zigux/phase2-closure.md", "scripts/zigux/validate-phase2.py");
    try expectBefore(checklist, "scripts/zigux/validate-phase2.py", "scripts/zigux/validate-phase2-closure.py");
    try expectBefore(checklist, "zigux/tests/fixtures/phase2_tool_manifest.json", "python3 scripts/zigux/check-phase2-tool-manifest.py");
}

test "phase 2 closure note and manifest name the same review checklist surface" {
    const allocator = std.testing.allocator;

    const checklist = try readRepoFile(allocator, "Documentation/zigux/review-checklist.md");
    defer allocator.free(checklist);
    const closure = try readRepoFile(allocator, "Documentation/zigux/phase2-closure.md");
    defer allocator.free(closure);
    const manifest = try readRepoFile(allocator, "zigux/tests/fixtures/phase2_tool_manifest.json");
    defer allocator.free(manifest);

    try expectContains(closure, "PHASE2_STATUS=parked");
    try expectContains(closure, "PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest");
    try expectContains(closure, "PHASE2_SHARED_TOOLING_CHECKERS=python3 scripts/zigux/check-phase2-tool-manifest.py");
    try expectContains(closure, "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2");
    try expectContains(closure, "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py");

    try expectContains(manifest, "\"phase\": \"Phase 2\"");
    try expectContains(manifest, "\"status\": \"active\"");
    try expectContains(manifest, "\"Documentation/zigux/review-checklist.md\"");
    try expectContains(manifest, "\"Documentation/zigux/phase2-closure.md\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-tool-manifest.py\"");
    try expectContains(manifest, "\"scripts/zigux/validate-phase2.py\"");
    try expectContains(manifest, "\"scripts/zigux/validate-phase2-closure.py\"");
    try expectContains(manifest, "\"make -C zigux phase2-validate\"");
    try expectContains(manifest, "\"make -C zigux phase2\"");
    try expectContains(manifest, "\"repo_reality_gaps\": []");

    try expectContains(checklist, "while `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`");
    try expectContains(checklist, "stay explicit as the current rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet");
}

test "phase 2 Makefile keeps review checklist routes replayable" {
    const allocator = std.testing.allocator;

    const makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);

    try expectContains(makefile, ".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2");
    try expectContains(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py --self-test");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py");
    try expectContains(makefile, "phase2: phase2-validate");
    try expectBefore(makefile, "phase2-toolchain:", "phase2-tools:");
    try expectBefore(makefile, "phase2-tools:", "phase2-kconfig:");
    try expectBefore(makefile, "phase2-kconfig:", "phase2-cross:");
    try expectBefore(makefile, "phase2-cross:", "phase2-genksyms:");
    try expectBefore(makefile, "phase2-genksyms:", "phase2-fixdep:");
    try expectBefore(makefile, "phase2-fixdep:", "phase2-validate:");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py --self-test\n\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py");
    try expectBefore(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py", "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py");
    try expectBefore(makefile, "phase2-validate:", "phase2: phase2-validate");
}
