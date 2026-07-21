const std = @import("std");

fn readRepoFile(io: std.Io, path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "review checklist routes Architecture Council prompts to owner notes" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const checklist = try readRepoFile(io_instance.io(), "Documentation/zigux/review-checklist.md", 96 * 1024);
    defer std.testing.allocator.free(checklist);

    try expectContains(checklist, "if a freeze-map anchor is entering Architecture Council status review");
    try expectContains(checklist, "required approver set");
    try expectContains(checklist, "rollback owner");
    try expectContains(checklist, "validator-first maintenance gate");
    try expectContains(checklist, "evidence archive path");
    try expectContains(checklist, "exact Architecture Council field inventory");
    try expectContains(checklist, "reopen-evidence details");
    try expectContains(checklist, "Documentation/zigux/phase15-architecture-council-review-process.md");
    try expectContains(checklist, "Documentation/zigux/phase15-architecture-council-decision-record-template.md");
    try expectContains(checklist, "Documentation/zigux/phase15-indefinite-c-policy.md");
    try expectContains(checklist, "scripts\\zigux/validate_phase15.zig");
}

test "review process owns exact fields and no approval posture" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const review_process = try readRepoFile(io_instance.io(), "Documentation/zigux/phase15-architecture-council-review-process.md", 64 * 1024);
    defer std.testing.allocator.free(review_process);

    try expectContains(review_process, "This note records the bounded Phase 15 review-policy packet");
    try expectContains(review_process, "Any freeze-map anchor entering Architecture Council status review");
    try expectContains(review_process, "decision record ID");
    try expectContains(review_process, "requested decision bucket");
    try expectContains(review_process, "required approver set");
    try expectContains(review_process, "automatic return-to-blocked trigger");
    try expectContains(review_process, "trigger-specific evidence refresh");
    try expectContains(review_process, "explicit non-goals");
    try expectContains(review_process, "written rationale");
    try expectContains(review_process, "no Architecture Council approval is currently recorded for a freeze-map status change");
    try expectContains(review_process, "Documentation/zigux/review-checklist.md");
    try expectContains(review_process, "Documentation/zigux/phase15-architecture-council-decision-record-template.md");
}

test "freeze map and template keep the closeout record path explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const freeze_map = try readRepoFile(io_instance.io(), "Documentation/zigux/freeze-map.md", 64 * 1024);
    defer std.testing.allocator.free(freeze_map);
    const template = try readRepoFile(io_instance.io(), "Documentation/zigux/phase15-architecture-council-decision-record-template.md", 32 * 1024);
    defer std.testing.allocator.free(template);

    try expectContains(freeze_map, "changes to either list require an explicit Architecture Council decision with written rationale");
    try expectContains(freeze_map, "freeze-map status-change requests must route through `Documentation/zigux/phase15-architecture-council-review-process.md`");
    try expectContains(freeze_map, "Documentation/zigux/phase15-architecture-council-decision-record-template.md");
    try expectContains(freeze_map, "retired_from_active_discussion");
    try expectContains(freeze_map, "trigger-specific evidence refresh");

    try expectContains(template, "This is a review packet template, not approval by itself.");
    try expectContains(template, "REVIEW_STATUS=<blocked_review|stay_in_c|approved_status_bucket_change>");
    try expectContains(template, "required approver set:");
    try expectContains(template, "evidence archive path:");
    try expectContains(template, "retired_from_active_discussion");
    try expectContains(template, "A stay-in-C closeout must keep");
    try expectContains(template, "A reopen request must cite");
}
