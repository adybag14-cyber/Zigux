const std = @import("std");

fn readRepoFile(path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "freeze map keeps phase9 packet as governance evidence only" {
    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md");
    defer std.testing.allocator.free(freeze_map);

    try expectContains(
        freeze_map,
        "the shared Phase 9 freeze-boundary packet is governance evidence only",
    );
    try expectContains(
        freeze_map,
        "must not be cited as proof that `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, blocked publication paths, install-root paths, or deeper runtime-loader substrate work became delivery-ready",
    );
    try expectContains(
        freeze_map,
        "historical blocked-boundary vocabulary unless a fresh repo reread proves they returned",
    );
}

test "review checklist blocks phase9 publication and install-root promotion claims" {
    const review_checklist = try readRepoFile("Documentation/zigux/review-checklist.md");
    defer std.testing.allocator.free(review_checklist);

    try expectContains(
        review_checklist,
        "if the change touches the shared Phase 9 runtime-pilot packet",
    );
    try expectContains(
        review_checklist,
        "without turning this checklist into proof that blocked publication, install-root, or depmod surfaces are complete",
    );
    try expectContains(
        review_checklist,
        "the older `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_survey.zig`, and `samples/zigux/runtime_trace_events_loader.zig` stay historical wider-family vocabulary",
    );
}

test "docs root preserves phase9 freeze anchor and route split" {
    const docs_readme = try readRepoFile("Documentation/zigux/README.md");
    defer std.testing.allocator.free(docs_readme);

    try expectContains(
        docs_readme,
        "Phase 9 reviewer prompt:",
    );
    try expectContains(
        docs_readme,
        "kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain study-only anchors",
    );
    try expectContains(
        docs_readme,
        "keep `scripts\\zigux/check_phase9_trace_events_direct_summary.zig` and `scripts\\zigux/check_phase9_trace_events_summary_preservation.zig` explicit",
    );
}
