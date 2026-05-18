const std = @import("std");

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    template_path: []const u8,
    surveyed_commit_mode: []const u8,
    surveyed_commit_placeholder: []const u8,
    supporting_artifacts: []const []const u8,
    record_metadata_fields: []const []const u8,
    anchor_and_ownership_fields: []const []const u8,
    validation_and_evidence_fields: []const []const u8,
    stay_in_c_closeout_fields: []const []const u8,
    reopen_evidence_fields: []const []const u8,
    supporting_context_fields: []const []const u8,
    review_outcome_fields: []const []const u8,
    usage_rules_required_terms: []const []const u8,
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAllTerms(haystack: []const u8, terms: []const []const u8) !void {
    for (terms) |term| {
        try expectContains(haystack, term);
    }
}

fn expectListContains(list: []const []const u8, needle: []const u8) !void {
    for (list) |item| {
        if (std.mem.eql(u8, item, needle)) return;
    }
    return error.TestUnexpectedResult;
}

test "phase 15 decision record template keeps the required Architecture Council review fields explicit" {
    const template = try readRepoFile("Documentation/zigux/phase15-architecture-council-decision-record-template.md", 24 * 1024);
    defer std.testing.allocator.free(template);

    const manifest_json = try readRepoFile("zigux/tests/phase15_architecture_council_decision_record_template_manifest.json", 24 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P15-L08", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-architecture-council-decision-record-template.md", manifest.template_path);
    try std.testing.expectEqualStrings("dated_master_readback", manifest.surveyed_commit_mode);
    try std.testing.expectEqualStrings("current-master-readback-YYYY-MM-DD", manifest.surveyed_commit_placeholder);
    try std.testing.expectEqual(@as(usize, 5), manifest.supporting_artifacts.len);
    try std.testing.expectEqual(@as(usize, 8), manifest.record_metadata_fields.len);
    try std.testing.expectEqual(@as(usize, 7), manifest.anchor_and_ownership_fields.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.validation_and_evidence_fields.len);
    try std.testing.expectEqual(@as(usize, 8), manifest.stay_in_c_closeout_fields.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.reopen_evidence_fields.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.supporting_context_fields.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.review_outcome_fields.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.usage_rules_required_terms.len);

    try expectListContains(manifest.supporting_artifacts, "Documentation/zigux/phase15-freeze-map-governance.md");
    try expectListContains(manifest.supporting_artifacts, "Documentation/zigux/phase15-parity-scorecard.md");
    try expectListContains(manifest.supporting_artifacts, "Documentation/zigux/phase15-architecture-council-review-process.md");
    try expectListContains(manifest.supporting_artifacts, "Documentation/zigux/phase15-indefinite-c-policy.md");
    try expectListContains(manifest.supporting_artifacts, "Documentation/zigux/review-checklist.md");

    try expectContains(template, "This is a review packet template, not approval by itself.");
    try expectContains(template, "## Record Metadata");
    try expectContains(template, "## Anchor And Ownership");
    try expectContains(template, "## Validation And Evidence");
    try expectContains(template, "## Stay-In-C Closeout");
    try expectContains(template, "## Reopen Evidence");
    try expectContains(template, "## Supporting Context");
    try expectContains(template, "## Review Outcome");
    try expectContains(template, "## Usage Rules");
    try expectContains(template, "PHASE15_PROVENANCE_MODE=dated_master_readback");
    try expectContains(template, "SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD");

    try expectAllTerms(template, manifest.record_metadata_fields);
    try expectAllTerms(template, manifest.anchor_and_ownership_fields);
    try expectAllTerms(template, manifest.validation_and_evidence_fields);
    try expectAllTerms(template, manifest.stay_in_c_closeout_fields);
    try expectAllTerms(template, manifest.reopen_evidence_fields);
    try expectAllTerms(template, manifest.supporting_context_fields);
    try expectAllTerms(template, manifest.review_outcome_fields);
    try expectAllTerms(template, manifest.usage_rules_required_terms);
}
