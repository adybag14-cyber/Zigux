const std = @import("std");

fn loadFile(io: std.Io, path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, std.testing.allocator, .limited(limit));
}

fn loadDoc(io: std.Io, comptime path: []const u8, limit: usize) ![]u8 {
    return loadFile(io, "Documentation/zigux/" ++ path, limit) catch |err| switch (err) {
        error.FileNotFound => loadFile(io, "../../Documentation/zigux/" ++ path, limit),
        else => err,
    };
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "review checklist keeps phase15 freeze-map prompts explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const review_checklist = try loadDoc(io_instance.io(), "review-checklist.md", 256 * 1024);
    defer std.testing.allocator.free(review_checklist);

    try expectContains(review_checklist, "is the status bucket explicit: port now, port after substrate, dual implementation required, study only, or freeze in C initially?");
    try expectContains(review_checklist, "does the change avoid deep-core scope creep into scheduler, MM, RCU, or skbuff without an Architecture Council decision?");
    try expectContains(review_checklist, "required approver set, rollback owner, and evidence archive path");
    try expectContains(review_checklist, "retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording");
    try expectContains(review_checklist, "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context");
}

test "docs root and freeze map agree on shared reminder ownership" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const docs_readme = try loadDoc(io_instance.io(), "README.md", 256 * 1024);
    defer std.testing.allocator.free(docs_readme);
    const freeze_map = try loadDoc(io_instance.io(), "freeze-map.md", 128 * 1024);
    defer std.testing.allocator.free(freeze_map);

    try expectContains(docs_readme, "keep the shared reminder surfaces explicit here too: `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` may summarize the same bounded packet");
    try expectContains(docs_readme, "but they do not own freeze-map decisions or broader route recovery by themselves");
    try expectContains(freeze_map, "shared reminder surfaces that summarize freeze posture, especially `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md`");
    try expectContains(freeze_map, "must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md`");
}

test "study-only anchors remain boundary context, not delivery evidence" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const review_checklist = try loadDoc(io_instance.io(), "review-checklist.md", 256 * 1024);
    defer std.testing.allocator.free(review_checklist);
    const freeze_map = try loadDoc(io_instance.io(), "freeze-map.md", 128 * 1024);
    defer std.testing.allocator.free(freeze_map);
    const study_only_accounting = try loadDoc(io_instance.io(), "phase15-study-only-anchor-accounting.md", 64 * 1024);
    defer std.testing.allocator.free(study_only_accounting);

    try expectContains(freeze_map, "- `kernel/workqueue.c`");
    try expectContains(freeze_map, "- `kernel/trace/ring_buffer.c`");
    try expectContains(freeze_map, "must not present `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as active delivery targets before an Architecture Council reviewable record changes their status bucket");
    try expectContains(study_only_accounting, "kernel/workqueue.c");
    try expectContains(study_only_accounting, "kernel/trace/ring_buffer.c");
    try expectNotContains(review_checklist, "study-only anchors are active delivery targets");
}
