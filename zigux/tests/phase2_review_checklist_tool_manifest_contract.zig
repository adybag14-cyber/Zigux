const std = @import("std");

const docs_readme_path = "Documentation/zigux/README.md";
const review_checklist_path = "Documentation/zigux/review-checklist.md";
const closure_path = "Documentation/zigux/phase2-closure.md";
const manifest_path = "zigux/tests/fixtures/phase2_tool_manifest.json";
const checker_path = "scripts/zigux/check-phase2-tool-manifest.py";
const makefile_path = "zigux/Makefile";

fn readRepoFile(path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "review checklist keeps phase 2 tool manifest runnable gate explicit" {
    const checklist = try readRepoFile(review_checklist_path);
    defer std.testing.allocator.free(checklist);

    try expectContains(checklist, "keep `python3 scripts/zigux/check-phase2-tool-manifest.py` explicit as the runnable shared Phase 2 tool-manifest gate whenever the review checklist names `zigux/tests/fixtures/phase2_tool_manifest.json`.");
    try expectContains(checklist, "Documentation/zigux/README.md");
    try expectContains(checklist, "Documentation/zigux/phase2-closure.md");
    try expectContains(checklist, "scripts/zigux/validate-phase2-closure.py");
    try expectContains(checklist, "zigux/tests/fixtures/phase2_tool_manifest.json");
    try expectContains(checklist, "scripts/zigux/check-phase2-tool-manifest.py");
    try expectContains(checklist, "make -C zigux phase2-toolchain");
    try expectContains(checklist, "make -C zigux phase2-validate");
    try expectContains(checklist, "make -C zigux phase2");
    try expectOrder(
        checklist,
        "zigux/tests/fixtures/phase2_tool_manifest.json",
        "keep `python3 scripts/zigux/check-phase2-tool-manifest.py` explicit as the runnable shared Phase 2 tool-manifest gate",
    );
}

test "docs root, closure note, and manifest keep the same phase 2 tool packet visible" {
    const docs_readme = try readRepoFile(docs_readme_path);
    defer std.testing.allocator.free(docs_readme);
    const closure = try readRepoFile(closure_path);
    defer std.testing.allocator.free(closure);
    const manifest = try readRepoFile(manifest_path);
    defer std.testing.allocator.free(manifest);

    try expectContains(docs_readme, "scripts/zigux/check-phase2-tool-manifest.py");
    try expectContains(docs_readme, "zigux/tests/fixtures/phase2_tool_manifest.json");
    try expectContains(docs_readme, "make -C zigux phase2-validate");
    try expectContains(docs_readme, "make -C zigux phase2");

    try expectContains(closure, "PHASE2_SHARED_TOOLING_CHECKERS=python3 scripts/zigux/check-phase2-tool-manifest.py");
    try expectContains(closure, "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2");
    try expectContains(closure, "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py");

    try expectContains(manifest, "\"phase\": \"Phase 2\"");
    try expectContains(manifest, "\"repo_reality_gaps\": []");
    try expectContains(manifest, "\"review_surfaces\"");
    try expectContains(manifest, "\"make_wrappers\"");
    try expectContains(manifest, "\"validators\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-tool-manifest.py\"");
    try expectContains(manifest, "\"scripts/zigux/validate-phase2-closure.py\"");
    try expectContains(manifest, "\"make -C zigux phase2-validate\"");
}

test "manifest checker and makefile keep the review checklist gate replayable" {
    const checker = try readRepoFile(checker_path);
    defer std.testing.allocator.free(checker);
    const makefile = try readRepoFile(makefile_path);
    defer std.testing.allocator.free(makefile);

    try expectContains(checker, "MANIFEST = Path(\"zigux/tests/fixtures/phase2_tool_manifest.json\")");
    try expectContains(checker, "\"review_surfaces\"");
    try expectContains(checker, "\"make_wrappers\"");
    try expectContains(checker, "\"validators\"");
    try expectContains(checker, "\"scripts/zigux/validate-phase2-closure.py\"");
    try expectContains(checker, "\"scripts/zigux/check-phase2-tool-manifest.py\"");
    try expectContains(checker, "\"scripts/zigux/check-phase2-artifact-tools-manifest.py\"");
    try expectContains(checker, "\"scripts/zigux/check-phase2-fixdep-gate.py\"");

    try expectContains(makefile, ".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2");
    try expectContains(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py --self-test");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py");
}
