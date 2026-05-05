const std = @import("std");

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const HandoffEvidence = struct {
    current_repo_handoff: []const u8,
    current_bounded_lane: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    roadmap_requirement: []const u8,
    anchor: []const u8,
    current_approval_state: []const u8,
    ownership_evidence_fields: []const []const u8,
    trigger_conditions: []const []const u8,
    required_review_packet_fields: []const []const u8,
    reopen_trigger_catalog: []const []const u8,
    decision_buckets: []const []const u8,
    handoff_evidence: HandoffEvidence,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next");
}

test "phase 15 architecture council review-process manifest records the bounded governance slice" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_architecture_council_review_process_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P15-L14", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("3eac40e856ac7673f705447a1d6025f3d0193b5e", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("Architecture Council review process", manifest.roadmap_requirement);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-architecture-council-review-process.md", manifest.anchor);
    try std.testing.expectEqualStrings("no_freeze_map_status_change_approved", manifest.current_approval_state);
    try std.testing.expectEqual(@as(usize, 10), manifest.ownership_evidence_fields.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.trigger_conditions.len);
    try std.testing.expectEqual(@as(usize, 17), manifest.required_review_packet_fields.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.reopen_trigger_catalog.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.decision_buckets.len);
    try std.testing.expectEqual(@as(usize, 9), manifest.gaps.len);

    try std.testing.expectEqualStrings("owner", manifest.ownership_evidence_fields[0]);
    try std.testing.expectEqualStrings("rollback owner", manifest.ownership_evidence_fields[1]);
    try std.testing.expectEqualStrings("evidence archive path", manifest.ownership_evidence_fields[3]);
    try std.testing.expectEqualStrings("latest blocker disposition", manifest.ownership_evidence_fields[4]);
    try std.testing.expectEqualStrings("benchmark notes", manifest.ownership_evidence_fields[5]);
    try std.testing.expectEqualStrings("replay command", manifest.ownership_evidence_fields[6]);
    try std.testing.expectEqualStrings("retained discussion state", manifest.ownership_evidence_fields[7]);
    try std.testing.expectEqualStrings("reopen triggers", manifest.ownership_evidence_fields[8]);
    try std.testing.expectEqualStrings("freeze-map list change", manifest.trigger_conditions[0]);
    try std.testing.expectEqualStrings("current status bucket", manifest.required_review_packet_fields[2]);
    try std.testing.expectEqualStrings("requested decision bucket", manifest.required_review_packet_fields[3]);
    try std.testing.expectEqualStrings("decision record ID", manifest.required_review_packet_fields[4]);
    try std.testing.expectEqualStrings("latest blocker disposition", manifest.required_review_packet_fields[9]);
    try std.testing.expectEqualStrings("benchmark notes", manifest.required_review_packet_fields[10]);
    try std.testing.expectEqualStrings("replay command", manifest.required_review_packet_fields[11]);
    try std.testing.expectEqualStrings("narrower_followup_answers_blocker", manifest.reopen_trigger_catalog[0]);
    try std.testing.expectEqualStrings("evidence_packet_stale_or_contradictory", manifest.reopen_trigger_catalog[1]);
    try std.testing.expectEqualStrings("ownership_or_validation_changed", manifest.reopen_trigger_catalog[2]);
    try std.testing.expectEqualStrings("keep_in_c", manifest.decision_buckets[0]);
    try std.testing.expectEqualStrings("bounded_dual_implementation", manifest.decision_buckets[2]);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.current_repo_handoff, "Documentation/zigux/phase15-architecture-council-review-process.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.current_bounded_lane, "scripts-root validator path") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.current_bounded_lane, "tests-root guidance path") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.current_bounded_lane, "dedicated handoff-checker route") != null);

    var landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var saw_doc = false;
    var saw_manifest = false;
    var saw_test = false;
    var saw_checklist = false;
    var saw_build = false;
    var saw_parity_baseline = false;
    var saw_archive_followup = false;
    var saw_retirement_rule = false;
    var saw_reopen_followup = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase15-architecture-council-review-process-doc")) {
            saw_doc = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-architecture-council-review-process.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Architecture Council review process") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase15-architecture-council-review-process-manifest")) {
            saw_manifest = true;
            try std.testing.expectEqualStrings("zigux/tests/phase15_architecture_council_review_process_manifest.json", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase15-architecture-council-review-process-test")) {
            saw_test = true;
            try std.testing.expectEqualStrings("zigux/tests/phase15_architecture_council_review_process.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase15-review-checklist-hook")) {
            saw_checklist = true;
            try std.testing.expectEqualStrings("Documentation/zigux/review-checklist.md", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase15-build-gate-review-process")) {
            saw_build = true;
            try std.testing.expectEqualStrings("zigux/tests/phase15_build.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase15-parity-scorecard-baseline")) {
            saw_parity_baseline = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-parity-scorecard.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "live evidence attachment point") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase15-evidence-archive-followup")) {
            saw_archive_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-architecture-council-review-process.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Council decision records") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase15-stay-in-c-retirement-rule")) {
            saw_retirement_rule = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "retired_from_active_discussion") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase15-reopen-trigger-catalog-followup")) {
            saw_reopen_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "reopen-trigger catalog") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 9), landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expect(saw_doc);
    try std.testing.expect(saw_manifest);
    try std.testing.expect(saw_test);
    try std.testing.expect(saw_checklist);
    try std.testing.expect(saw_build);
    try std.testing.expect(saw_parity_baseline);
    try std.testing.expect(saw_archive_followup);
    try std.testing.expect(saw_retirement_rule);
    try std.testing.expect(saw_reopen_followup);
}

test "phase 15 architecture council review-process doc records the required process language" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-architecture-council-review-process.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(survey_doc);

    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "## Trigger Conditions") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "## Required Review Packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "## Decision Buckets") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "## Reopen Trigger Catalog") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "## Current Approval Posture") != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        survey_doc,
        "product boundary:\n  - `Documentation/zigux/phase15-architecture-council-review-process.md`",
    ) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`Documentation/zigux/review-checklist.md`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`zigux/tests/phase15_architecture_council_review_process_manifest.json`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`zigux/tests/phase15_architecture_council_review_process.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`zigux/tests/phase15_build.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "no Architecture Council approval is currently recorded for a freeze-map status change") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "current review-process evidence is limited to named `owner`, `rollback owner`, evidence archive, blocker-disposition, benchmark-notes, replay-command, retained-discussion-state, and reopen-trigger records") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "retained discussion state") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "reopen triggers") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "narrower_followup_answers_blocker") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "evidence_packet_stale_or_contradictory") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "ownership_or_validation_changed") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`retired_from_active_discussion`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "current status bucket and the requested decision bucket") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "decision record ID") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "evidence archive path") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "latest blocker disposition") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "current benchmark-notes status") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "replay command reviewers should run") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "written rationale") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "parity scorecard link, or an explicit blocker record") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`keep_in_c`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`study_only_followup`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`bounded_dual_implementation`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`defer_or_reject`") != null);
}

test "phase 15 review checklist stays aligned with the council review-process hook" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const review_checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(review_checklist);

    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "Architecture Council decision") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "parity scorecard evidence or blocker state explicit") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "Architecture Council review record linked") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "current status bucket plus requested decision bucket explicit") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "decision record ID, lane owner, rollback owner, validation gate summary, evidence archive path, latest blocker disposition, benchmark notes, and replay command explicit") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "retained discussion state and reopen triggers explicit") != null);
}
