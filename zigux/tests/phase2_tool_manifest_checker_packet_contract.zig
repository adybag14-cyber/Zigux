const std = @import("std");
const testing = std.testing;

const max_file_size = 1024 * 1024;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(max_file_size));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

test "phase2 tool manifest checker keeps the full manifest packet explicit" {
    const allocator = testing.allocator;
    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase2-tool-manifest.py");
    defer allocator.free(checker);

    try expectContains(checker, "MANIFEST = Path(\"zigux/tests/fixtures/phase2_tool_manifest.json\")");
    try expectContains(checker, "\"scope\": \"current directly readable scripts-root toolchain, local-archive, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, fixdep, and tranche-closure reminder packet\"");
    try expectContains(checker, "\"scripts/zigux/check-phase2-tool-manifest.py\"");
    try expectContains(checker, "\"scripts/zigux/check-phase2-bootstrap-workflow-routes.py\"");
    try expectContains(checker, "\"scripts/zigux/check-phase2-artifact-tools-manifest.py\"");
    try expectContains(checker, "\"scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py\"");
    try expectContains(checker, "\"scripts/zigux/check-phase2-genksyms-selftest-alignment.py\"");
    try expectContains(checker, "\"scripts/zigux/check-phase2-fixdep-gate.py\"");
    try expectContains(checker, "\"scripts/zigux/check-fixdep-diff.py\"");
    try expectContains(checker, "\"make -C zigux phase2-toolchain\"");
    try expectContains(checker, "\"make -C zigux phase2-validate\"");
    try expectContains(checker, "\"make -C zigux phase2\"");
    try expectContains(checker, "PHASE2_TOOL_MANIFEST_SELF_TEST=pass");
    try expectContains(checker, "PHASE2_TOOL_MANIFEST=pass");
    try expectOrdered(checker, "ARCHIVE_SUPPORT_FIXED_PREFIX", "ARCHIVE_SUPPORT_ALTERNATIVES");
    try expectOrdered(checker, "\"review_surfaces\"", "\"make_wrappers\"");
}

test "phase2 manifest, closure note, and reminder surfaces name the same checker packet" {
    const allocator = testing.allocator;
    const manifest = try readRepoFile(allocator, "zigux/tests/fixtures/phase2_tool_manifest.json");
    defer allocator.free(manifest);
    const closure = try readRepoFile(allocator, "Documentation/zigux/phase2-closure.md");
    defer allocator.free(closure);
    const scripts_readme = try readRepoFile(allocator, "scripts/zigux/README.md");
    defer allocator.free(scripts_readme);
    const tests_readme = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_readme);

    try expectContains(manifest, "\"checker_ids\"");
    try expectContains(manifest, "\"check-phase2-tool-manifest\"");
    try expectContains(manifest, "\"repo_reality_gaps\": []");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-tool-manifest.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-bootstrap-workflow-routes.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-artifact-tools-manifest.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-genksyms-selftest-alignment.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-fixdep-gate.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-fixdep-diff.py\"");

    try expectContains(closure, "`scripts/zigux/check-phase2-tool-manifest.py`");
    try expectContains(closure, "`python3 scripts/zigux/check-phase2-tool-manifest.py`");
    try expectContains(closure, "PHASE2_SHARED_TOOLING_CHECKERS=python3 scripts/zigux/check-phase2-tool-manifest.py");
    try expectContains(closure, "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2");
    try expectOrdered(closure, "## Current Shared Repo-Tooling Evidence", "## Shared Replay Routes");

    try expectContains(scripts_readme, "`scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit");
    try expectContains(tests_readme, "`scripts/zigux/check-phase2-tool-manifest.py`");
    try expectContains(tests_readme, "`zigux/tests/fixtures/phase2_tool_manifest.json`");
}

test "phase2 workflow, make route, and validators replay the tool manifest checker" {
    const allocator = testing.allocator;
    const workflow = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);
    const makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);
    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase2.py");
    defer allocator.free(validator);
    const closure_validator = try readRepoFile(allocator, "scripts/zigux/validate-phase2-closure.py");
    defer allocator.free(closure_validator);

    try expectContains(workflow, "run: python3 scripts/zigux/check-phase2-tool-manifest.py --self-test");
    try expectContains(workflow, "run: python3 scripts/zigux/check-phase2-tool-manifest.py");
    try expectOrdered(workflow, "Self-test current Phase 2 tool manifest checker", "Check current Phase 2 tool manifest packet");
    try expectOrdered(workflow, "Check current Phase 2 tool manifest packet", "Self-test current Phase 2 artifact tools manifest checker");

    try expectContains(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py --self-test");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py");
    try expectContains(makefile, "phase2: phase2-validate");

    try expectContains(validator, "\"scripts/zigux/check-phase2-tool-manifest.py\"");
    try expectContains(validator, "\"run: python3 scripts/zigux/check-phase2-tool-manifest.py --self-test\"");
    try expectContains(validator, "\"run: python3 scripts/zigux/check-phase2-tool-manifest.py\"");
    try expectContains(validator, "\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py\"");
    try expectContains(closure_validator, "SHARED_TOOLING_COMMANDS");
    try expectContains(closure_validator, "\"python3 scripts/zigux/check-phase2-tool-manifest.py\"");
}
