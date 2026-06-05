const std = @import("std");

const freeze_in_c_anchors = [_][]const u8{
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
};

const study_only_anchors = [_][]const u8{
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
};

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

test "docs root keeps Phase 15 approval boundary routed through decision owners" {
    const docs_root = try readRepoFile("Documentation/zigux/README.md", 192 * 1024);
    defer std.testing.allocator.free(docs_root);

    try expectContains(docs_root, "Phase 15 notes - `Documentation/zigux/freeze-map.md`");
    try expectContains(docs_root, "`Documentation/zigux/phase15-architecture-council-review-process.md`");
    try expectContains(docs_root, "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`");
    try expectContains(docs_root, "`Documentation/zigux/phase15-architecture-council-decision-index.md`");
    try expectContains(docs_root, "`Documentation/zigux/phase15-freeze-map-governance.md`");
    try expectContains(docs_root, "`Documentation/zigux/phase15-parity-scorecard.md`");
    try expectContains(docs_root, "`scripts/zigux/validate-phase15.py`");
    try expectContains(docs_root, "no Architecture Council approval is currently recorded for a freeze-map status change");
    try expectContains(docs_root, "below any Architecture Council approval claim");
    try expectContains(docs_root, "below any freeze-map status change");
}

test "docs root keeps every freeze and study anchor below status-change claims" {
    const docs_root = try readRepoFile("Documentation/zigux/README.md", 192 * 1024);
    defer std.testing.allocator.free(docs_root);

    for (freeze_in_c_anchors) |anchor| {
        try expectContains(docs_root, anchor);
    }
    for (study_only_anchors) |anchor| {
        try expectContains(docs_root, anchor);
    }

    try expectContains(docs_root, "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain study-only anchors");
    try expectContains(docs_root, "shared reminder surfaces route those summaries back to the owning accounting note");
    try expectContains(docs_root, "instead of treating them as delivery evidence");
    try expectNotContains(docs_root, "Phase 15 approval landed");
}

test "docs root keeps Phase 15 shared build evidence separate from blocked routes" {
    const docs_root = try readRepoFile("Documentation/zigux/README.md", 192 * 1024);
    defer std.testing.allocator.free(docs_root);

    try expectContains(docs_root, "`zigux/tests/phase15_build.zig` stays the directly readable shared build companion");
    try expectContains(docs_root, "`make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` remain blocked route vocabulary");
    try expectContains(docs_root, "`scripts/zigux/check-phase15-docs-readme-alignment.py`");
    try expectContains(docs_root, "`scripts/zigux/check-phase15-architecture-council-packet.py`");
    try expectContains(docs_root, "`scripts/zigux/validate-phase15.py`");
}
