const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 15 architecture council review-process doc and manifest stay aligned on the parked governance packet boundary" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-architecture-council-review-process.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(survey_doc);

    const manifest_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_architecture_council_review_process_manifest.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(manifest_doc);

    try expectContains(survey_doc, "## Trigger Conditions");
    try expectContains(survey_doc, "## Required Review Packet");
    try expectContains(survey_doc, "## Decision Buckets");
    try expectContains(survey_doc, "## Reopen Trigger Catalog");
    try expectContains(survey_doc, "## Current Approval Posture");
    try expectContains(
        survey_doc,
        "product boundary:\n  - `Documentation/zigux/freeze-map.md`",
    );
    try expectContains(survey_doc, "`Documentation/zigux/phase15-freeze-map-governance.md`");
    try expectContains(survey_doc, "`Documentation/zigux/phase15-architecture-council-review-process.md`");
    try expectContains(survey_doc, "`Documentation/zigux/phase15-parity-scorecard.md`");
    try expectContains(survey_doc, "`Documentation/zigux/phase15-indefinite-c-policy.md`");
    try expectContains(survey_doc, "`Documentation/zigux/review-checklist.md`");
    try expectContains(survey_doc, "`scripts/zigux/check-phase15-review-process-handoff.py`");
    try expectContains(survey_doc, "`zigux/tests/phase15_architecture_council_review_process_manifest.json`");
    try expectContains(survey_doc, "`zigux/tests/phase15_architecture_council_review_process.zig`");
    try expectContains(survey_doc, "`zigux/tests/phase15_build.zig`");
    try expectContains(survey_doc, "no Architecture Council approval is currently recorded for a freeze-map status change");
    try expectContains(survey_doc, "`retired_from_active_discussion`");

    try expectContains(manifest_doc, "\"current_repo_handoff\"");
    try expectContains(
        manifest_doc,
        "Documentation/zigux/phase15-architecture-council-review-process.md",
    );
    try expectContains(manifest_doc, "\"current_bounded_lane\"");
    try expectContains(manifest_doc, "scripts-root validator path");
    try expectContains(manifest_doc, "tests-root guidance path");
    try expectContains(manifest_doc, "dedicated handoff-checker route");
}
