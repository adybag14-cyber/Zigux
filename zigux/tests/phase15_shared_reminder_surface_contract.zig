const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 15 docs root keeps the shared reminder packet tied to freeze-map governance" {
    const docs_root = try readRepoFile("Documentation/zigux/README.md", 256 * 1024);
    defer std.testing.allocator.free(docs_root);

    try expectContains(docs_root, "Phase 15 notes");
    try expectContains(docs_root, "Documentation/zigux/freeze-map.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-freeze-map-governance.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-architecture-council-review-process.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-parity-scorecard.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-readiness-gate-survey.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-governance-lane-sequencing.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-handoff-next-steps-survey.md");
    try expectContains(docs_root, "scripts/zigux/validate-phase15.py");
    try expectContains(docs_root, "keep the Phase 15 reminder bounded below any Architecture Council approval claim");
    try expectContains(docs_root, "no Architecture Council approval is currently recorded");
    try expectContains(docs_root, "kernel/workqueue.c");
    try expectContains(docs_root, "kernel/trace/ring_buffer.c");
    try expectContains(docs_root, "shared reminder surfaces route those summaries back to the owning accounting note");
}

test "phase 15 review checklist routes study-only summaries back to the owning accounting note" {
    const checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 256 * 1024);
    defer std.testing.allocator.free(checklist);

    try expectContains(checklist, "shared reminder surface summarizes the study-only freeze-map anchors");
    try expectContains(checklist, "Documentation/zigux/freeze-map.md");
    try expectContains(checklist, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectContains(checklist, "kernel/workqueue.c");
    try expectContains(checklist, "kernel/trace/ring_buffer.c");
    try expectContains(checklist, "study-only boundary context rather than runtime-substrate or bridge-readiness evidence");
    try expectContains(checklist, "phase15-architecture-council-review-process.md");
    try expectContains(checklist, "phase15-indefinite-c-policy.md");
    try expectContains(checklist, "scripts/zigux/validate-phase15.py");
}

test "freeze map owns the shared reminder boundary and approval gate" {
    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 128 * 1024);
    defer std.testing.allocator.free(freeze_map);

    try expectContains(freeze_map, "shared reminder surfaces that summarize freeze posture");
    try expectContains(freeze_map, "Documentation/zigux/README.md");
    try expectContains(freeze_map, "Documentation/zigux/review-checklist.md");
    try expectContains(freeze_map, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectContains(freeze_map, "kernel/workqueue.c");
    try expectContains(freeze_map, "kernel/trace/ring_buffer.c");
    try expectContains(freeze_map, "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked");
    try expectContains(freeze_map, "Architecture Council records why the status can change");
    try expectContains(freeze_map, "there is no silent exception path around the stay-in-C policy");
}
