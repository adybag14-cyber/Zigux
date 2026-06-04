const std = @import("std");

const Source = struct {
    name: []const u8,
    text: []const u8,
};

fn readFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(512 * 1024),
    );
}

fn expectContains(source: Source, marker: []const u8) !void {
    if (!std.mem.containsAtLeast(u8, source.text, 1, marker)) {
        std.debug.print("missing Phase 2 shared review marker in {s}: {s}\n", .{
            source.name,
            marker,
        });
        return error.MissingPhase2SharedReviewMarker;
    }
}

test "docs root keeps the current Phase 2 shared review packet explicit" {
    const docs_root_text = try readFile("Documentation/zigux/README.md");
    defer std.testing.allocator.free(docs_root_text);

    const docs_root = Source{
        .name = "Documentation/zigux/README.md",
        .text = docs_root_text,
    };

    try expectContains(docs_root, "Phase 2 notes");
    try expectContains(docs_root, "`Documentation/zigux/review-checklist.md`");
    try expectContains(docs_root, "`zigux/tests/README.md`");
    try expectContains(docs_root, "`scripts/zigux/check-phase2-docs-shared-reminder.py`");
    try expectContains(docs_root, "`scripts/zigux/check-phase2-artifact-tools-manifest.py`");
    try expectContains(docs_root, "`scripts/zigux/check-phase2-fixdep-gate.py`");
    try expectContains(docs_root, "`make -C zigux phase2-genksyms`");
    try expectContains(docs_root, "`make -C zigux phase2-fixdep`");
}

test "review checklist keeps the Phase 2 reviewer prompt aligned" {
    const checklist_text = try readFile("Documentation/zigux/review-checklist.md");
    defer std.testing.allocator.free(checklist_text);

    const checklist = Source{
        .name = "Documentation/zigux/review-checklist.md",
        .text = checklist_text,
    };

    try expectContains(checklist, "if the change touches the shared Phase 2 toolchain packet");
    try expectContains(checklist, "`Documentation/zigux/README.md`");
    try expectContains(checklist, "`zigux/tests/README.md`");
    try expectContains(checklist, "`scripts/zigux/check-phase2-docs-shared-reminder.py`");
    try expectContains(checklist, "`scripts/zigux/check-phase2-artifact-tools-manifest.py`");
    try expectContains(checklist, "`scripts/zigux/check-phase2-required-make-routes.py`");
    try expectContains(checklist, "`scripts/zigux/check-phase2-fixdep-gate.py`");
    try expectContains(checklist, "`make -C zigux phase2-fixdep`");
}

test "tests root keeps the Phase 2 packet visible to Zig-facing validation" {
    const tests_readme_text = try readFile("zigux/tests/README.md");
    defer std.testing.allocator.free(tests_readme_text);

    const tests_readme = Source{
        .name = "zigux/tests/README.md",
        .text = tests_readme_text,
    };

    try expectContains(tests_readme, "## Phase 2 review packet");
    try expectContains(tests_readme, "`Documentation/zigux/review-checklist.md`");
    try expectContains(tests_readme, "`scripts/zigux/check-phase2-docs-shared-reminder.py`");
    try expectContains(tests_readme, "`scripts/zigux/check-phase2-artifact-tools-manifest.py`");
    try expectContains(tests_readme, "`scripts/zigux/check-phase2-required-make-routes.py`");
    try expectContains(tests_readme, "`scripts/zigux/check-phase2-fixdep-gate.py`");
    try expectContains(tests_readme, "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`");
    try expectContains(tests_readme, "`make -C zigux phase2-fixdep`");
}
