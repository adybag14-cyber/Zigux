const std = @import("std");
const Io = std.Io;

const docs_root_path = "Documentation/zigux/README.md";
const review_checklist_path = "Documentation/zigux/review-checklist.md";
const freeze_map_path = "Documentation/zigux/freeze-map.md";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(4 * 1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectExactlyOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, haystack, needle));
}

test "shared review prompts keep Architecture Council handoff fields explicit" {
    const allocator = std.testing.allocator;
    const docs_root = try readFile(allocator, docs_root_path);
    defer allocator.free(docs_root);
    const review_checklist = try readFile(allocator, review_checklist_path);
    defer allocator.free(review_checklist);
    const freeze_map = try readFile(allocator, freeze_map_path);
    defer allocator.free(freeze_map);

    try expectContains(review_checklist, "Architecture Council status review");
    try expectContains(review_checklist, "required approver set");
    try expectContains(review_checklist, "rollback owner");
    try expectContains(review_checklist, "evidence archive path");
    try expectContains(review_checklist, "stay-in-C closeout");

    try expectContains(freeze_map, "requested decision bucket");
    try expectContains(freeze_map, "decision record ID");
    try expectContains(freeze_map, "required approver set");
    try expectContains(freeze_map, "rollback owner");
    try expectContains(freeze_map, "evidence archive path");
    try expectContains(freeze_map, "automatic return-to-blocked trigger");
    try expectContains(freeze_map, "trigger-specific evidence refresh");

    try expectContains(docs_root, "bounded below any Architecture Council approval claim");
    try expectContains(docs_root, "freeze-map status change");
    try expectContains(docs_root, "shared reminder surfaces");
}

test "study-only anchor routing stays aligned across shared surfaces" {
    const allocator = std.testing.allocator;
    const docs_root = try readFile(allocator, docs_root_path);
    defer allocator.free(docs_root);
    const review_checklist = try readFile(allocator, review_checklist_path);
    defer allocator.free(review_checklist);
    const freeze_map = try readFile(allocator, freeze_map_path);
    defer allocator.free(freeze_map);

    for ([_][]const u8{
        "kernel/workqueue.c",
        "kernel/trace/ring_buffer.c",
        "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    }) |marker| {
        try expectContains(docs_root, marker);
        try expectContains(review_checklist, marker);
        try expectContains(freeze_map, marker);
    }

    try expectExactlyOnce(freeze_map, "- `kernel/workqueue.c`");
    try expectExactlyOnce(freeze_map, "- `kernel/trace/ring_buffer.c`");
    try expectContains(review_checklist, "study-only boundary context rather than runtime-substrate or bridge-readiness evidence");
    try expectContains(freeze_map, "study-only boundary into delivery-ready runtime-substrate evidence");
}

test "no silent status-change or reopen path is advertised" {
    const allocator = std.testing.allocator;
    const docs_root = try readFile(allocator, docs_root_path);
    defer allocator.free(docs_root);
    const review_checklist = try readFile(allocator, review_checklist_path);
    defer allocator.free(review_checklist);
    const freeze_map = try readFile(allocator, freeze_map_path);
    defer allocator.free(freeze_map);

    try expectContains(freeze_map, "there is no silent exception path around the stay-in-C policy");
    try expectContains(freeze_map, "only an explicit Architecture Council reopen request with fresh linked evidence");
    try expectContains(freeze_map, "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked");

    try expectContains(review_checklist, "retained blocker posture");
    try expectContains(review_checklist, "return-to-blocked wording");
    try expectContains(docs_root, "Architecture Council approval is currently recorded");
    try expectContains(docs_root, "no Architecture Council approval is currently recorded for a freeze-map status change");
}
