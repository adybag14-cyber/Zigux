const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 15 indefinite-C blocker posture stays visible in the docs root family" {
    const docs_root = try readRepoFile("Documentation/zigux/README.md", 160 * 1024);
    defer std.testing.allocator.free(docs_root);

    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 24 * 1024);
    defer std.testing.allocator.free(freeze_map);

    const review_checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 96 * 1024);
    defer std.testing.allocator.free(review_checklist);

    const policy_note = try readRepoFile("Documentation/zigux/phase15-indefinite-c-policy.md", 32 * 1024);
    defer std.testing.allocator.free(policy_note);

    try expectContains(docs_root, "Documentation/zigux/freeze-map.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-indefinite-c-policy.md");
    try expectContains(docs_root, "Documentation/zigux/review-checklist.md");
    try expectContains(freeze_map, "explicit Architecture Council decision");
    try expectContains(freeze_map, "the existing C implementation remains the product source of truth");
    try expectContains(review_checklist, "if a freeze-map anchor is closing review with a stay-in-C outcome");
    try expectContains(review_checklist, "retained discussion state");
    try expectContains(review_checklist, "current blocker");
    try expectContains(review_checklist, "reopen triggers");
    try expectContains(policy_note, "PHASE15_STATUS=indefinite_c_policy_packet_landed");
    try expectContains(policy_note, "PHASE15_PROVENANCE_MODE=dated_master_readback");
    try expectContains(policy_note, "phase15-deep-core-status-change-blocker");
    try expectContains(policy_note, "C implementation remains the product source of truth");
}

test "phase 15 blocker posture requires fresh evidence before reopening stay-in-C outcomes" {
    const freeze_governance = try readRepoFile("Documentation/zigux/phase15-freeze-map-governance.md", 40 * 1024);
    defer std.testing.allocator.free(freeze_governance);

    const policy_note = try readRepoFile("Documentation/zigux/phase15-indefinite-c-policy.md", 32 * 1024);
    defer std.testing.allocator.free(policy_note);

    const review_process = try readRepoFile("Documentation/zigux/phase15-architecture-council-review-process.md", 64 * 1024);
    defer std.testing.allocator.free(review_process);

    try expectContains(freeze_governance, "direct Zig bridge or port claims for a freeze-in-C anchor stay blocked");
    try expectContains(freeze_governance, "Architecture Council records why the status can change");
    try expectContains(freeze_governance, "the same current stay-in-C policy family");
    try expectContains(policy_note, "named reopen-trigger catalog item");
    try expectContains(policy_note, "trigger-specific evidence refresh");
    try expectContains(policy_note, "the existing blocker remains recorded");
    try expectContains(review_process, "required approver set");
    try expectContains(review_process, "latest blocker disposition");
    try expectContains(review_process, "trigger-specific evidence refresh");
}
