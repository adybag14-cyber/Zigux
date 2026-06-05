const std = @import("std");
const Io = std.Io;

const repo_files = .{
    .docs_root = "Documentation/zigux/README.md",
    .review_checklist = "Documentation/zigux/review-checklist.md",
    .freeze_map = "Documentation/zigux/freeze-map.md",
    .phase15_build = "zigux/tests/phase15_build.zig",
    .makefile = "zigux/Makefile",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(2 * 1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "docs root and freeze map keep Phase 15 wrapper routes blocked" {
    const allocator = std.testing.allocator;

    const docs_root = try readRepoFile(allocator, repo_files.docs_root);
    defer allocator.free(docs_root);
    const freeze_map = try readRepoFile(allocator, repo_files.freeze_map);
    defer allocator.free(freeze_map);

    try expectContains(docs_root, "make -C zigux phase15-validate");
    try expectContains(docs_root, "make -C zigux phase15-test");
    try expectContains(docs_root, "make -C zigux phase15");
    try expectContains(docs_root, "blocked route vocabulary rather than shipped replay paths");
    try expectContains(docs_root, "no Architecture Council approval is currently recorded for a freeze-map status change");

    try expectContains(freeze_map, "dedicated `phase15*` wrapper routes");
    try expectContains(freeze_map, "repo-reality gaps on current `master`");
    try expectContains(freeze_map, "shared reminder surfaces that discuss Phase 15");
}

test "review checklist keeps Phase 15 governance review anchored to owners" {
    const allocator = std.testing.allocator;

    const review_checklist = try readRepoFile(allocator, repo_files.review_checklist);
    defer allocator.free(review_checklist);

    try expectContains(review_checklist, "freeze-map anchor is entering Architecture Council status review");
    try expectContains(review_checklist, "required approver set, rollback owner, and evidence archive path");
    try expectContains(review_checklist, "scripts/zigux/validate-phase15.py");
    try expectContains(review_checklist, "kernel/workqueue.c");
    try expectContains(review_checklist, "kernel/trace/ring_buffer.c");
    try expectContains(review_checklist, "study-only boundary context rather than runtime-substrate or bridge-readiness evidence");
}

test "shared build companion is Zig-only while Makefile lacks Phase 15 wrappers" {
    const allocator = std.testing.allocator;

    const phase15_build = try readRepoFile(allocator, repo_files.phase15_build);
    defer allocator.free(phase15_build);
    const makefile = try readRepoFile(allocator, repo_files.makefile);
    defer allocator.free(makefile);

    try expectContains(phase15_build, "phase15-freeze-map-governance");
    try expectContains(phase15_build, "phase15-architecture-council-review-process");
    try expectContains(phase15_build, "phase15-readiness-gate");
    try expectContains(phase15_build, "Run the shared Phase 15 governance test packet");

    try expectNotContains(makefile, "phase15-validate");
    try expectNotContains(makefile, "phase15-test");
    try expectNotContains(makefile, "phase15:");
}
