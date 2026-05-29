const std = @import("std");

const max_file_size = 1024 * 1024;

const phase2_docs_root_markers = [_][]const u8{
    "Phase 2 notes",
    "`Documentation/zigux/phase2-closure.md`",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/README.md`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
};

const shared_toolchain_markers = [_][]const u8{
    "0.17.0-dev.87+9b177a7d2",
    "x86_64-linux",
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
};

const scripts_root_fixdep_markers = [_][]const u8{
    "Phase 2 flow - the current fixdep packet stays reviewable",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`make -C zigux phase2-fixdep`",
};

test "docs root names the current Phase 2 packet surfaces" {
    const docs_readme = try readRepoFile("Documentation/zigux/README.md");
    defer std.testing.allocator.free(docs_readme);

    try expectAllPresent(docs_readme, &phase2_docs_root_markers);
}

test "toolchain reminder packet stays aligned across owner surfaces" {
    const docs_readme = try readRepoFile("Documentation/zigux/README.md");
    defer std.testing.allocator.free(docs_readme);
    const bootstrap_notes = try readRepoFile("Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    defer std.testing.allocator.free(bootstrap_notes);
    const review_checklist = try readRepoFile("Documentation/zigux/review-checklist.md");
    defer std.testing.allocator.free(review_checklist);
    const third_party_readme = try readRepoFile("third_party/README.md");
    defer std.testing.allocator.free(third_party_readme);

    try expectAllPresent(docs_readme, &shared_toolchain_markers);
    try expectAllPresent(bootstrap_notes, &shared_toolchain_markers);
    try expectAllPresent(review_checklist, &shared_toolchain_markers);
    try expectAllPresent(third_party_readme, &[_][]const u8{
        "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
        "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
        "58159088",
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux",
    });
}

test "scripts root keeps the Phase 2 reminder bounded to fixdep" {
    const scripts_readme = try readRepoFile("scripts/zigux/README.md");
    defer std.testing.allocator.free(scripts_readme);

    try expectAllPresent(scripts_readme, &scripts_root_fixdep_markers);
    try std.testing.expect(std.mem.indexOf(u8, scripts_readme, "widening into unrelated Phase 2 surfaces") != null);
}

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, std.testing.allocator, .limited(max_file_size));
}

fn expectAllPresent(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
    }
}
