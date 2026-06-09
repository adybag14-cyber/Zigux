const std = @import("std");
const testing = std.testing;

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readDoc(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, path, allocator, .limited(1024 * 1024));
}

test "docs root keeps Phase 8 addendum tied to current helper routes" {
    const docs_root = try readDoc(testing.allocator, "Documentation/zigux/README.md");
    defer testing.allocator.free(docs_root);

    try expectContains(docs_root, "Phase 8 Notes");
    try expectContains(docs_root, "`scripts/zigux/validate-phase8.py`");
    try expectContains(docs_root, "`tools/lib/subcmd/exec-cmd.zig`");
    try expectContains(docs_root, "`tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`");
    try expectContains(docs_root, "`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`");
    try expectContains(docs_root, "`Documentation/zigux/phase8-exec-cmd-slice.md`");
    try expectContains(docs_root, "`make -C zigux phase8-exec-cmd-test`");
    try expectContains(docs_root, "`make -C zigux phase8-file-path-handle-bridge-test`");
    try expectContains(docs_root, "`make -C zigux phase8-validate`");
}

test "review checklist keeps Phase 8 shared packet bounded" {
    const review_checklist = try readDoc(testing.allocator, "Documentation/zigux/review-checklist.md");
    defer testing.allocator.free(review_checklist);

    try expectContains(review_checklist, "if the change touches the shared Phase 8 userspace-adjacent tooling packet");
    try expectContains(review_checklist, "`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`");
    try expectContains(review_checklist, "`Documentation/zigux/phase8-exec-cmd-slice.md`");
    try expectContains(review_checklist, "`scripts/zigux/check-phase8-libbpf-shard-routes.py`");
    try expectContains(review_checklist, "`tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`");
    try expectContains(review_checklist, "`zigux/tests/phase8_file_path_handle_bridge.zig`");
    try expectContains(review_checklist, "`make -C zigux phase8-file-path-handle-bridge-test`");
    try expectContains(review_checklist, "`make -C zigux phase8-perf-buffer-poll-test`");
    try expectContains(review_checklist, "`make -C zigux phase8-test`");
}

test "freeze map keeps Phase 8 reminders below study-only core ownership" {
    const freeze_map = try readDoc(testing.allocator, "Documentation/zigux/freeze-map.md");
    defer testing.allocator.free(freeze_map);

    try expectContains(freeze_map, "## Study / Boundary Only");
    try expectContains(freeze_map, "`kernel/workqueue.c`");
    try expectContains(freeze_map, "`kernel/trace/ring_buffer.c`");
    try expectContains(freeze_map, "Architecture Council");
    try expectContains(freeze_map, "study-only anchors");
    try expectContains(freeze_map, "without an explicit Architecture Council decision");
}
