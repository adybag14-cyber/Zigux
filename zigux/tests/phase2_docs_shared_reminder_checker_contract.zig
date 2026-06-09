const std = @import("std");

fn readFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, std.testing.allocator, .limited(1024 * 1024));
}

fn expectContains(text: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, text, needle) != null);
}

fn expectNotContains(text: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, text, needle) == null);
}

fn expectBefore(text: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, text, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, text, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn expectExactCount(text: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, text[offset..], needle)) |relative| {
        count += 1;
        offset += relative + needle.len;
    }
    try std.testing.expectEqual(expected, count);
}

test "docs shared reminder checker owns the full Phase 2 source roster" {
    const checker = try readFile("scripts/zigux/check-phase2-docs-shared-reminder.py");
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "DOCS_README = ROOT / \"Documentation\" / \"zigux\" / \"README.md\"");
    try expectContains(checker, "PHASE2_NOTES = ROOT / \"Documentation\" / \"zigux\" / \"phase2-toolchain-bootstrap-notes.md\"");
    try expectContains(checker, "REVIEW_CHECKLIST = ROOT / \"Documentation\" / \"zigux\" / \"review-checklist.md\"");
    try expectContains(checker, "SCRIPTS_README = ROOT / \"scripts\" / \"zigux\" / \"README.md\"");
    try expectContains(checker, "TESTS_README = ROOT / \"zigux\" / \"tests\" / \"README.md\"");
    try expectContains(checker, "THIRD_PARTY_README = ROOT / \"third_party\" / \"README.md\"");

    try expectContains(checker, "DOCS_README_MARKERS = (");
    try expectContains(checker, "PHASE2_NOTES_MARKERS = (");
    try expectContains(checker, "REVIEW_CHECKLIST_MARKERS = (");
    try expectContains(checker, "SCRIPTS_README_MARKERS = (");
    try expectContains(checker, "TESTS_README_MARKERS = (");
    try expectContains(checker, "THIRD_PARTY_README_MARKERS = (");
    try expectContains(checker, "PHASE2_NOTES_FORBIDDEN_MARKERS = (");
    try expectContains(checker, "REVIEW_CHECKLIST_FORBIDDEN_MARKERS = (");
    try expectContains(checker, "SCRIPTS_README_FORBIDDEN_MARKERS = (");
    try expectContains(checker, "collect_missing_markers");
}

test "bootstrap notes keep docs reminder runnable beside Phase 2 route packet" {
    const notes = try readFile("Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    defer std.testing.allocator.free(notes);

    try expectContains(notes, "`scripts/zigux/check-phase2-docs-shared-reminder.py`");
    try expectContains(notes, "`python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test`");
    try expectContains(notes, "`python3 scripts/zigux/check-phase2-docs-shared-reminder.py`");
    try expectContains(notes, "`make -C zigux phase2-toolchain`");
    try expectContains(notes, "`make -C zigux phase2-tools`");
    try expectContains(notes, "`make -C zigux phase2-kconfig`");
    try expectContains(notes, "`make -C zigux phase2-cross`");
    try expectContains(notes, "`make -C zigux phase2-genksyms`");
    try expectContains(notes, "`make -C zigux phase2-fixdep`");
    try expectContains(notes, "`make -C zigux phase2-validate`");
    try expectContains(notes, "`make -C zigux phase2`");
    try expectContains(notes, "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive");

    try expectBefore(notes, "`python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test`", "`python3 scripts/zigux/check-phase2-docs-shared-reminder.py`");
    try expectNotContains(notes, "historical packet members until same-lane work rematerializes them on `master`");
}

test "scripts and tests README keep the docs-reminder packet visible" {
    const scripts_readme = try readFile("scripts/zigux/README.md");
    defer std.testing.allocator.free(scripts_readme);
    const tests_readme = try readFile("zigux/tests/README.md");
    defer std.testing.allocator.free(tests_readme);

    try expectContains(scripts_readme, "`scripts/zigux/check-phase2-docs-shared-reminder.py`");
    try expectContains(scripts_readme, "`scripts/zigux/check-phase2-required-make-routes.py`");
    try expectContains(scripts_readme, "`zigux/Makefile`");
    try expectContains(scripts_readme, "`scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit");
    try expectContains(scripts_readme, "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`");
    try expectNotContains(scripts_readme, "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`");

    try expectContains(tests_readme, "`scripts/zigux/check-phase2-docs-shared-reminder.py`");
    try expectContains(tests_readme, "the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route");
    try expectContains(tests_readme, "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`");
    try expectContains(tests_readme, "current `master` now directly materializes `scripts/zigux/install-zig.py`");
}

test "review checklist and third-party archive stay tied to the same docs reminder" {
    const review = try readFile("Documentation/zigux/review-checklist.md");
    defer std.testing.allocator.free(review);
    const third_party = try readFile("third_party/README.md");
    defer std.testing.allocator.free(third_party);

    try expectContains(review, "if the change touches the shared Phase 2 toolchain packet");
    try expectContains(review, "`scripts/zigux/check-phase2-docs-shared-reminder.py`");
    try expectContains(review, "`third_party/README.md`");
    try expectContains(review, "`scripts/zigux/check-lane05-local-first-archive-workflow.py`");
    try expectContains(review, "`scripts/zigux/check-lane05-local-archive-readme.py`");
    try expectContains(review, "current directly readable Phase 2 local-first archive, toolchain, installer, direct cross-route");
    try expectContains(review, "`make -C zigux phase2`");

    try expectContains(third_party, "## Current pinned Zig archive contract");
    try expectContains(third_party, "- target: `x86_64-linux`");
    try expectContains(third_party, "- channel: `0.17.0-dev.758+748e7c5e3`");
    try expectContains(third_party, "- sha256: `0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6`");
    try expectContains(third_party, "- size: `59410844` bytes");
    try expectContains(third_party, "`scripts/zigux/stage-pinned-zig-archive.py`");
    try expectContains(third_party, "`scripts/zigux/check-lane05-local-first-archive-workflow.py` and `scripts/zigux/check-lane05-local-archive-readme.py`");
    try expectExactCount(third_party, "zig-x86_64-linux-0.17.0-dev.758+748e7c5e3 (1).tar.xz", 1);
}
