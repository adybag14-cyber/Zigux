const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 15 indefinite-C lane owner alignment stays coupled to the direct policy packet" {
    const policy_note = try readRepoFile("Documentation/zigux/phase15-indefinite-c-policy.md", 24 * 1024);
    defer std.testing.allocator.free(policy_note);

    const review_process = try readRepoFile("Documentation/zigux/phase15-architecture-council-review-process.md", 24 * 1024);
    defer std.testing.allocator.free(review_process);

    const decision_record_template = try readRepoFile("Documentation/zigux/phase15-architecture-council-decision-record-template.md", 16 * 1024);
    defer std.testing.allocator.free(decision_record_template);

    const manifest_json = try readRepoFile("zigux/tests/phase15_indefinite_c_policy.json", 24 * 1024);
    defer std.testing.allocator.free(manifest_json);

    try expectContains(policy_note, "PHASE15_LANE_KEY=P15-L16");
    try expectContains(policy_note, "Documentation/zigux/phase15-architecture-council-decision-record-template.md");
    try expectContains(policy_note, "same reviewable ownership vocabulary");
    try expectContains(policy_note, "lane owner");
    try expectContains(policy_note, "required approver set");
    try expectContains(policy_note, "rollback owner");
    try expectContains(policy_note, "exact-head provenance exception note");
    try expectContains(policy_note, "dated master readback is insufficient");

    try expectContains(review_process, "lane owner");
    try expectContains(review_process, "required approver set");
    try expectContains(review_process, "rollback owner");
    try expectContains(review_process, "current status bucket");
    try expectContains(review_process, "requested decision bucket");
    try expectContains(review_process, "Documentation/zigux/phase15-indefinite-c-policy.md");

    try expectContains(decision_record_template, "lane owner:");
    try expectContains(decision_record_template, "required approver set:");
    try expectContains(decision_record_template, "rollback owner:");
    try expectContains(decision_record_template, "current status bucket:");
    try expectContains(decision_record_template, "requested decision bucket:");
    try expectContains(decision_record_template, "retired_from_active_discussion");
    try expectContains(decision_record_template, "exact-head provenance exception note:");
    try expectContains(decision_record_template, "dated master readback is insufficient");
    try expectContains(decision_record_template, "lane owner, rollback owner, and required approver set explicit");

    try expectContains(manifest_json, "\"lane_key\": \"P15-L16\"");
    try expectContains(manifest_json, "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig");
    try expectContains(manifest_json, "phase15-indefinite-c-exact-head-exception-ownership-sync");
}