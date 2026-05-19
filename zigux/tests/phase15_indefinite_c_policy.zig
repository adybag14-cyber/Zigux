const std = @import("std");

const Requirement = struct {
    id: []const u8,
    summary: []const u8,
    required_terms: []const []const u8,
};

const MaintenanceHandoff = struct {
    current_lane_posture: []const u8,
    replay_before_trusting: []const []const u8,
    reopen_conditions: []const []const u8,
    next_future_target: []const u8,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    surveyed_commit_mode: []const u8,
    roadmap_requirement: []const u8,
    anchors: []const []const u8,
    supporting_artifacts: []const []const u8,
    indefinite_c_requirements: []const Requirement,
    maintenance_handoff: MaintenanceHandoff,
    gaps: []const Gap,
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectListContains(list: []const []const u8, needle: []const u8) !void {
    for (list) |item| {
        if (std.mem.eql(u8, item, needle)) return;
    }
    return error.TestUnexpectedResult;
}

fn findRequirement(requirements: []const Requirement, id: []const u8) ?Requirement {
    for (requirements) |requirement| {
        if (std.mem.eql(u8, requirement.id, id)) return requirement;
    }
    return null;
}

fn findGap(gaps: []const Gap, id: []const u8) ?Gap {
    for (gaps) |gap| {
        if (std.mem.eql(u8, gap.id, id)) return gap;
    }
    return null;
}

test "phase 15 indefinite-C policy packet restores the roadmap-required stay-in-C note and matches its live companions" {
    const policy_note = try readRepoFile("Documentation/zigux/phase15-indefinite-c-policy.md", 24 * 1024);
    defer std.testing.allocator.free(policy_note);

    const review_process = try readRepoFile("Documentation/zigux/phase15-architecture-council-review-process.md", 24 * 1024);
    defer std.testing.allocator.free(review_process);

    const decision_record_template = try readRepoFile("Documentation/zigux/phase15-architecture-council-decision-record-template.md", 24 * 1024);
    defer std.testing.allocator.free(decision_record_template);

    const parity_scorecard = try readRepoFile("Documentation/zigux/phase15-parity-scorecard.md", 24 * 1024);
    defer std.testing.allocator.free(parity_scorecard);

    const manifest_json = try readRepoFile("zigux/tests/phase15_indefinite_c_policy.json", 24 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P15-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("current-master-readback-2026-05-19", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("dated_master_readback", manifest.surveyed_commit_mode);
    try std.testing.expectEqualStrings("policy for code that remains in C indefinitely", manifest.roadmap_requirement);
    try std.testing.expectEqual(@as(usize, 4), manifest.anchors.len);
    try std.testing.expectEqual(@as(usize, 7), manifest.supporting_artifacts.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.indefinite_c_requirements.len);
    try std.testing.expectEqualStrings("maintenance_mode", manifest.maintenance_handoff.current_lane_posture);
    try std.testing.expectEqual(@as(usize, 1), manifest.maintenance_handoff.replay_before_trusting.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.maintenance_handoff.reopen_conditions.len);
    try std.testing.expectEqual(@as(usize, 7), manifest.gaps.len);

    try expectListContains(manifest.supporting_artifacts, "Documentation/zigux/freeze-map.md");
    try expectListContains(manifest.supporting_artifacts, "Documentation/zigux/review-checklist.md");
    try expectListContains(manifest.supporting_artifacts, "Documentation/zigux/phase15-freeze-map-governance.md");
    try expectListContains(manifest.supporting_artifacts, "Documentation/zigux/phase15-architecture-council-review-process.md");
    try expectListContains(manifest.supporting_artifacts, "Documentation/zigux/phase15-architecture-council-decision-record-template.md");
    try expectListContains(manifest.supporting_artifacts, "Documentation/zigux/phase15-parity-scorecard.md");
    try expectListContains(manifest.supporting_artifacts, "Documentation/zigux/README.md");

    try expectContains(policy_note, "PHASE15_STATUS=indefinite_c_policy_packet_landed");
    try expectContains(policy_note, "PHASE15_LANE_KEY=P15-L13");
    try expectContains(policy_note, "current-master-readback-2026-05-19");
    try expectContains(policy_note, "roadmap-required Phase 15 stay-in-C policy surface");
    try expectContains(policy_note, "the C implementation remains the source of truth");
    try expectContains(policy_note, "evidence archive path");
    try expectContains(policy_note, "automatic return-to-blocked trigger");
    try expectContains(policy_note, "retired_from_active_discussion");
    try expectContains(policy_note, "trigger-specific evidence refresh");
    try expectContains(policy_note, "There is no silent exception path around the indefinite-C policy.");
    try expectContains(policy_note, "Documentation/zigux/phase15-architecture-council-decision-record-template.md");
    try expectContains(policy_note, "same reviewable ownership vocabulary");
    try expectContains(policy_note, "zig test zigux/tests/phase15_indefinite_c_policy.zig");
    try expectContains(policy_note, "phase15-indefinite-c-review-process-companion-sync");
    try expectContains(policy_note, "phase15-indefinite-c-ownership-template-sync");

    try expectContains(review_process, "`Documentation/zigux/phase15-indefinite-c-policy.md` keeps the stay-in-C policy companion explicit");
    try expectContains(review_process, "indefinite-C policy link or explicit non-applicability note");
    try expectContains(review_process, "retired_from_active_discussion");

    try expectContains(decision_record_template, "## Anchor And Ownership");
    try expectContains(decision_record_template, "lane owner:");
    try expectContains(decision_record_template, "rollback owner:");
    try expectContains(decision_record_template, "validation gate summary:");
    try expectContains(decision_record_template, "indefinite-C policy link or explicit non-applicability note:");

    try expectContains(parity_scorecard, "blocked status-change anchor count: `4`");
    try expectContains(parity_scorecard, "Architecture Council approvals recorded for status change: `0`");
    try expectContains(parity_scorecard, "the indefinite-C policy aligned around the same blocked posture");

    const recordkeeping = findRequirement(manifest.indefinite_c_requirements, "indefinite-c-recordkeeping") orelse return error.MissingRequirement;
    try std.testing.expectEqual(@as(usize, 20), recordkeeping.required_terms.len);
    try std.testing.expectEqualStrings("lane owner", recordkeeping.required_terms[5]);
    try std.testing.expectEqualStrings("required approver set", recordkeeping.required_terms[6]);
    try std.testing.expectEqualStrings("rollback owner", recordkeeping.required_terms[7]);
    try std.testing.expectEqualStrings("evidence archive path", recordkeeping.required_terms[12]);
    try std.testing.expectEqualStrings("automatic return-to-blocked trigger", recordkeeping.required_terms[13]);
    try std.testing.expectEqualStrings("retired_from_active_discussion state", recordkeeping.required_terms[14]);
    try std.testing.expectEqualStrings("reopen triggers", recordkeeping.required_terms[15]);
    try std.testing.expectEqualStrings("trigger-specific evidence refresh", recordkeeping.required_terms[16]);

    const exception_path = findRequirement(manifest.indefinite_c_requirements, "indefinite-c-exception-path") orelse return error.MissingRequirement;
    try std.testing.expectEqual(@as(usize, 3), exception_path.required_terms.len);
    try expectContains(exception_path.required_terms[0], "no silent exception path");
    try expectContains(exception_path.required_terms[1], "Architecture Council reopen request");

    const reopen_catalog = findRequirement(manifest.indefinite_c_requirements, "indefinite-c-reopen-trigger-catalog") orelse return error.MissingRequirement;
    try std.testing.expectEqual(@as(usize, 3), reopen_catalog.required_terms.len);
    try std.testing.expectEqualStrings("narrower_followup_answers_blocker", reopen_catalog.required_terms[0]);
    try std.testing.expectEqualStrings("evidence_packet_stale_or_contradictory", reopen_catalog.required_terms[1]);
    try std.testing.expectEqualStrings("ownership_or_validation_changed", reopen_catalog.required_terms[2]);

    const roadmap_gap = findGap(manifest.gaps, "phase15-indefinite-c-roadmap-gap-restoration") orelse return error.MissingGap;
    try std.testing.expectEqualStrings("landed", roadmap_gap.status);
    try std.testing.expectEqualStrings("roadmap_alignment", roadmap_gap.kind);
    try expectContains(roadmap_gap.why_now, "roadmap");

    const review_process_sync = findGap(manifest.gaps, "phase15-indefinite-c-review-process-companion-sync") orelse return error.MissingGap;
    try std.testing.expectEqualStrings("landed", review_process_sync.status);
    try std.testing.expectEqualStrings("companion_sync", review_process_sync.kind);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-architecture-council-review-process.md", review_process_sync.zigux_destination);

    const ownership_template_sync = findGap(manifest.gaps, "phase15-indefinite-c-ownership-template-sync") orelse return error.MissingGap;
    try std.testing.expectEqualStrings("landed", ownership_template_sync.status);
    try std.testing.expectEqualStrings("companion_sync", ownership_template_sync.kind);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-architecture-council-decision-record-template.md", ownership_template_sync.zigux_destination);
    try expectContains(ownership_template_sync.why_now, "ownership");

    const blocker_gap = findGap(manifest.gaps, "phase15-deep-core-status-change-blocker") orelse return error.MissingGap;
    try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", blocker_gap.status);
    try std.testing.expectEqualStrings("freeze_map", blocker_gap.kind);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-parity-scorecard.md", blocker_gap.zigux_destination);
}