const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase 7 docs root and checklist keep rbtree parity packet bounded" {
    const docs_readme = try readRepoFile("Documentation/zigux/README.md", 192 * 1024);
    defer std.testing.allocator.free(docs_readme);

    const review_checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 256 * 1024);
    defer std.testing.allocator.free(review_checklist);

    try expectContains(docs_readme, "## Phase 7 Shared Surface Addendum");
    try expectContains(docs_readme, "zigux/tests/phase7_build.zig");
    try expectContains(docs_readme, "../../lib/rbtree.zig");
    try expectContains(docs_readme, "make -C zigux phase7-validate");
    try expectContains(docs_readme, "leaves broader wrapper routes outside this packet");

    try expectContains(review_checklist, "if the change touches the shared Phase 7 leaf-library packet");
    try expectContains(review_checklist, "Documentation/zigux/phase7-leaf-library-evidence-catalog.md");
    try expectContains(review_checklist, "scripts/zigux/check-phase7-rbtree-parity.py");
    try expectContains(review_checklist, "zigux/tests/phase7_build.zig");
    try expectContains(review_checklist, "lib/rbtree.zig");
    try expectContains(review_checklist, "make -C zigux phase7-validate");
    try expectContains(review_checklist, "keep broader wrapper families or deeper runtime validation claims out of the Phase 7 reminder packet");
}

test "phase 7 catalog and checker keep rbtree parity companions explicit" {
    const catalog = try readRepoFile("Documentation/zigux/phase7-leaf-library-evidence-catalog.md", 64 * 1024);
    defer std.testing.allocator.free(catalog);

    const checker = try readRepoFile("scripts/zigux/check-phase7-rbtree-parity.py", 128 * 1024);
    defer std.testing.allocator.free(checker);

    try expectContains(catalog, "- `scripts/zigux/check-phase7-rbtree-parity.py`");
    try expectContains(catalog, "- `lib/rbtree.zig`");
    try expectContains(catalog, "- `lib/rbtree.c`");
    try expectContains(catalog, "`zigux/tests/phase7_build.zig` keeps the shared `test` build step");
    try expectContains(catalog, "`zigux/Makefile` keeps the narrow `phase7-validate` foothold explicit while broader wrapper routes remain outside this packet.");
    try expectContains(catalog, "do not widen this packet into new helper semantics, workflow recovery claims, or deeper runtime-family validation routes");

    try expectContains(checker, "EXPECTED_MANIFEST_LANE_KEY = \"P7-L13\"");
    try expectContains(checker, "EXPECTED_MANIFEST_ANCHOR = \"lib/rbtree.c\"");
    try expectContains(checker, "zigux/tests/fixtures/phase7_rbtree.json");
    try expectContains(checker, "zigux/tests/fixtures/phase7_rbtree_c_harness.c");
    try expectContains(checker, "phase7-rbtree-test:");
    try expectContains(checker, "phase7-rbtree-survey:");
    try expectContains(checker, "PHASE7_RBTREE_PARITY=pass");
    try expectContains(checker, "PHASE7_RBTREE_PARITY_SELF_TEST=pass");
    try expectContains(checker, "non-leftmost cached erase, singleton cached erase, and plain erase-init reseed");
}

test "phase 7 build graph keeps rbtree wrapper boundary narrow" {
    const build = try readRepoFile("zigux/tests/phase7_build.zig", 96 * 1024);
    defer std.testing.allocator.free(build);

    const makefile = try readRepoFile("zigux/Makefile", 96 * 1024);
    defer std.testing.allocator.free(makefile);

    try expectContains(build, "../../lib/rbtree.zig");
    try expectContains(build, "phase7-rbtree-test");
    try expectContains(build, "phase7-rbtree-survey");
    try expectContains(build, "rbtree_survey_step.dependOn(&run_rbtree_survey_tests.step)");
    try expectContains(build, "Run the Phase 7 runtime helper tests");
    try expectContains(build, "test_step.dependOn(&run_rbtree_tests.step)");
    try expectContains(build, "test_step.dependOn(&run_rbtree_survey_tests.step)");

    try expectContains(makefile, "phase7-validate:");
    try expectContains(makefile, "phase7-rbtree-test:");
    try expectContains(makefile, "phase7-rbtree-survey:");
    try expectContains(makefile, "$(PYTHON) scripts/zigux/validate-phase7.py");
    try expectNotContains(makefile, "phase7-test:");
    try expectNotContains(makefile, "phase7:");
}
