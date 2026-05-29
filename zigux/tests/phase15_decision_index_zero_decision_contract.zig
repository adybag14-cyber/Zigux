const std = @import("std");
const testing = std.testing;

const max_doc_bytes = 256 * 1024;

const decision_index_path = "Documentation/zigux/phase15-architecture-council-decision-index.md";
const freeze_map_path = "Documentation/zigux/freeze-map.md";
const review_process_path = "Documentation/zigux/phase15-architecture-council-review-process.md";
const decision_template_path = "Documentation/zigux/phase15-architecture-council-decision-record-template.md";

fn readDoc(io: std.Io, allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, allocator, .limited(max_doc_bytes)) catch |err| switch (err) {
        error.FileNotFound => blk: {
            const repo_root_path = try std.fs.path.join(allocator, &.{ "..", "..", path });
            defer allocator.free(repo_root_path);
            break :blk try std.Io.Dir.cwd().readFileAlloc(io, repo_root_path, allocator, .limited(max_doc_bytes));
        },
        else => return err,
    };
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "decision index keeps zero-decision posture explicit" {
    const allocator = testing.allocator;
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    const decision_index = try readDoc(io_instance.io(), allocator, decision_index_path);
    defer allocator.free(decision_index);

    try expectContains(decision_index, "PHASE15_STATUS=architecture_council_decision_index_landed");
    try expectContains(decision_index, "PHASE15_SLICE=decision-record-inventory");
    try expectContains(decision_index, "approved status-bucket changes recorded on current `master`: none");
    try expectContains(decision_index, "stay-in-C closeout decision records recorded on current `master`: none");
    try expectContains(decision_index, "no freeze-map anchor has an Architecture Council approval for a status change on current `master`");
    try expectContains(decision_index, "The freeze map, parity scorecard, and review-process packet therefore remain blocker-accounting and governance truthfulness evidence rather than approval evidence");
}

test "future decision records must route through the governance owner notes" {
    const allocator = testing.allocator;
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    const decision_index = try readDoc(io_instance.io(), allocator, decision_index_path);
    defer allocator.free(decision_index);

    try expectContains(decision_index, "every future Architecture Council decision record for a freeze-map anchor must be linked here");
    try expectContains(decision_index, "decision record ID, exact Linux anchor path, review outcome, evidence archive path, surveyed commit marker, and next bounded step");
    try expectContains(decision_index, "`Documentation/zigux/phase15-architecture-council-review-process.md`");
    try expectContains(decision_index, "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`");
    try expectContains(decision_index, "`Documentation/zigux/phase15-freeze-map-governance.md`");
    try expectContains(decision_index, "`Documentation/zigux/phase15-parity-scorecard.md`");
    try expectContains(decision_index, "if no reviewable Architecture Council decision record exists yet, keep this note at an explicit zero-decision inventory");
}

test "freeze map and review process still block status changes without explicit Council evidence" {
    const allocator = testing.allocator;
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    const freeze_map = try readDoc(io_instance.io(), allocator, freeze_map_path);
    defer allocator.free(freeze_map);
    const review_process = try readDoc(io_instance.io(), allocator, review_process_path);
    defer allocator.free(review_process);

    try expectContains(freeze_map, "This file records code that should not move into active Zigux delivery without an explicit Architecture Council decision.");
    try expectContains(freeze_map, "changes to either list require an explicit Architecture Council decision with written rationale");
    try expectContains(freeze_map, "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked until the repo carries a parity scorecard entry and the Architecture Council records why the status can change");
    try expectContains(review_process, "On current `master`, no freeze-map anchor has an Architecture Council approval for a status change.");
    try expectContains(review_process, "`Documentation/zigux/phase15-architecture-council-decision-index.md` keeps the current Architecture Council decision inventory explicit");
}

test "decision record template remains the future-record shape, not an approval claim" {
    const allocator = testing.allocator;
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    const decision_index = try readDoc(io_instance.io(), allocator, decision_index_path);
    defer allocator.free(decision_index);
    const decision_template = try readDoc(io_instance.io(), allocator, decision_template_path);
    defer allocator.free(decision_template);

    try expectContains(decision_index, "Use one flat entry per landed Architecture Council decision record");
    try expectContains(decision_index, "This note does not claim:");
    try expectContains(decision_index, "an Architecture Council approval for any freeze-map status change");
    try expectContains(decision_template, "This is a review packet template, not approval by itself.");
    try expectContains(decision_template, "If any required field above cannot be stated honestly, keep the request blocked and leave the C implementation as the product source of truth.");
}
