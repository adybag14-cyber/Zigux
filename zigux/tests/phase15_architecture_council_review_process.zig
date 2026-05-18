const std = @import("std");

const ReviewProcessManifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    review_process_note: []const u8,
    decision_record_template: []const u8,
    handoff_note: []const u8,
    shared_summary_gap_note: []const u8,
    checker: []const u8,
    required_review_fields: []const []const u8,
    stay_in_c_closeout_fields: []const []const u8,
    reopen_evidence_fields: []const []const u8,
    decision_record_template_required_markers: []const []const u8,
    handoff_required_markers: []const []const u8,
    shared_gap_expected_present_paths: []const []const u8,
    shared_gap_expected_missing_paths: []const []const u8,
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectSliceContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |entry| {
        if (std.mem.eql(u8, entry, needle)) return;
    }
    return error.TestUnexpectedResult;
}

test "phase 15 review-process manifest records the focused replay as materialized evidence" {
    const manifest_json = try readRepoFile("zigux/tests/phase15_architecture_council_review_process_manifest.json", 24 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(ReviewProcessManifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P15-L08", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("current-master-readback-2026-05-18", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-architecture-council-review-process.md", manifest.review_process_note);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-architecture-council-decision-record-template.md", manifest.decision_record_template);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-handoff-next-steps-survey.md", manifest.handoff_note);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-shared-summary-gap.md", manifest.shared_summary_gap_note);
    try std.testing.expectEqualStrings("scripts/zigux/check-phase15-review-process-handoff.py", manifest.checker);
    try std.testing.expectEqual(@as(usize, 22), manifest.required_review_fields.len);
    try std.testing.expectEqual(@as(usize, 8), manifest.stay_in_c_closeout_fields.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.reopen_evidence_fields.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.decision_record_template_required_markers.len);
    try std.testing.expectEqual(@as(usize, 9), manifest.handoff_required_markers.len);
    try std.testing.expectEqual(@as(usize, 11), manifest.shared_gap_expected_present_paths.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.shared_gap_expected_missing_paths.len);

    try expectSliceContains(
        manifest.shared_gap_expected_present_paths,
        "`zigux/tests/phase15_architecture_council_review_process.zig`",
    );
    try expectSliceContains(
        manifest.shared_gap_expected_missing_paths,
        "`zigux/tests/phase15_build.zig`",
    );
}

test "phase 15 review-process note stays aligned with the focused replay packet" {
    const review_process = try readRepoFile("Documentation/zigux/phase15-architecture-council-review-process.md", 20 * 1024);
    defer std.testing.allocator.free(review_process);

    const decision_record_template = try readRepoFile("Documentation/zigux/phase15-architecture-council-decision-record-template.md", 16 * 1024);
    defer std.testing.allocator.free(decision_record_template);

    const handoff_note = try readRepoFile("Documentation/zigux/phase15-handoff-next-steps-survey.md", 20 * 1024);
    defer std.testing.allocator.free(handoff_note);

    const gap_note = try readRepoFile("Documentation/zigux/phase15-shared-summary-gap.md", 20 * 1024);
    defer std.testing.allocator.free(gap_note);

    const manifest_json = try readRepoFile("zigux/tests/phase15_architecture_council_review_process_manifest.json", 24 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(ReviewProcessManifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    try expectContains(review_process, "PHASE15_STATUS=architecture_council_review_process_landed");
    try expectContains(review_process, manifest.surveyed_commit);
    try expectContains(review_process, "`zigux/tests/phase15_architecture_council_review_process_manifest.json`");
    try expectContains(review_process, "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`");
    try expectContains(review_process, "`scripts/zigux/check-phase15-review-process-handoff.py`");
    try expectContains(review_process, "`zigux/tests/phase15_architecture_council_review_process.zig`");
    try expectContains(review_process, "the focused Zig replay are landed");
    try expectContains(review_process, "broader validator-first shared-summary surfaces remain gap-tracked");
    try expectContains(review_process, "focused review-process replay");
    try expectContains(review_process, "defaults that record to dated-master-readback provenance");

    for (manifest.required_review_fields) |field| {
        try expectContains(review_process, field);
    }
    for (manifest.stay_in_c_closeout_fields) |field| {
        try expectContains(review_process, field);
        try expectContains(decision_record_template, field);
    }
    for (manifest.reopen_evidence_fields) |field| {
        try expectContains(review_process, field);
    }
    for (manifest.decision_record_template_required_markers) |marker| {
        try expectContains(decision_record_template, marker);
    }
    for (manifest.handoff_required_markers) |marker| {
        try expectContains(handoff_note, marker);
    }
    for (manifest.shared_gap_expected_present_paths) |marker| {
        try expectContains(gap_note, marker);
    }
    for (manifest.shared_gap_expected_missing_paths) |marker| {
        try expectContains(gap_note, marker);
    }
}

test "phase 15 review-process handoff checker fails closed on missing present paths" {
    const checker = try readRepoFile("scripts/zigux/check-phase15-review-process-handoff.py", 24 * 1024);
    defer std.testing.allocator.free(checker);

    const review_process = try readRepoFile("Documentation/zigux/phase15-architecture-council-review-process.md", 20 * 1024);
    defer std.testing.allocator.free(review_process);

    const gap_note = try readRepoFile("Documentation/zigux/phase15-shared-summary-gap.md", 20 * 1024);
    defer std.testing.allocator.free(gap_note);

    try expectContains(checker, "shared-summary gap note claims materialized path is missing from repo");
    try expectContains(checker, "focused review-process Zig replay is missing from repo");
    try expectContains(checker, "repo_path = _marker_to_repo_path(marker)");
    try expectContains(checker, "zigux/tests/phase15_architecture_council_review_process.zig");
    try expectContains(checker, "PHASE15_REVIEW_PROCESS_HANDOFF_SELF_TEST=pass");
    try expectContains(checker, "current-master-readback-2026-05-18");
    try expectContains(review_process, "current-master-readback-2026-05-18");
    try expectContains(gap_note, "`zigux/tests/phase15_architecture_council_review_process.zig`");
    try expectContains(gap_note, "`zigux/tests/phase15_build.zig`");
}
