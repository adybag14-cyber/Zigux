const std = @import("std");

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Handoff = struct {
    current_mode: []const u8,
    replay_commands: []const []const u8,
    blocker_posture_requirement: []const u8,
    next_step: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    roadmap_requirement: []const u8,
    anchor: []const u8,
    review_packet_template: []const u8,
    current_approval_state: []const u8,
    directly_coupled_evidence_surfaces: []const []const u8,
    ownership_evidence_fields: []const []const u8,
    trigger_conditions: []const []const u8,
    required_review_packet_fields: []const []const u8,
    reopen_trigger_catalog: []const []const u8,
    decision_buckets: []const []const u8,
    handoff: Handoff,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "open") or
        std.mem.eql(u8, status, "blocked_on_shared_summaries");
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 15 architecture council review-process manifest records the current bounded governance slice" {
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
    try std.testing.expectEqualStrings("P15-L08", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("current-master-readback-2026-05-16", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("Architecture Council review process", manifest.roadmap_requirement);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-architecture-council-review-process.md", manifest.anchor);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-architecture-council-decision-record-template.md", manifest.review_packet_template);
    try std.testing.expectEqualStrings("no_freeze_map_status_change_approved", manifest.current_approval_state);
    try std.testing.expectEqual(@as(usize, 7), manifest.directly_coupled_evidence_surfaces.len);
    try std.testing.expectEqual(@as(usize, 15), manifest.ownership_evidence_fields.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.trigger_conditions.len);
    try std.testing.expectEqual(@as(usize, 23), manifest.required_review_packet_fields.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.reopen_trigger_catalog.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.decision_buckets.len);
    try std.testing.expectEqual(@as(usize, 11), manifest.gaps.len);

    try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", manifest.directly_coupled_evidence_surfaces[0]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-freeze-map-governance.md", manifest.directly_coupled_evidence_surfaces[1]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-parity-scorecard.md", manifest.directly_coupled_evidence_surfaces[2]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-indefinite-c-policy.md", manifest.directly_coupled_evidence_surfaces[3]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-readiness-gate-survey.md", manifest.directly_coupled_evidence_surfaces[4]);
    try std.testing.expectEqualStrings("Documentation/zigux/review-checklist.md", manifest.directly_coupled_evidence_surfaces[5]);
    try std.testing.expectEqualStrings("zigux/tests/phase15_build.zig", manifest.directly_coupled_evidence_surfaces[6]);

    try std.testing.expectEqualStrings("owner", manifest.ownership_evidence_fields[0]);
    try std.testing.expectEqualStrings("required approver set", manifest.ownership_evidence_fields[1]);
    try std.testing.expectEqualStrings("rollback owner", manifest.ownership_evidence_fields[2]);
    try std.testing.expectEqualStrings("validation gate summary", manifest.ownership_evidence_fields[3]);
    try std.testing.expectEqualStrings("evidence archive path", manifest.ownership_evidence_fields[4]);
    try std.testing.expectEqualStrings("latest blocker disposition", manifest.ownership_evidence_fields[5]);
    try std.testing.expectEqualStrings("automatic return-to-blocked trigger", manifest.ownership_evidence_fields[6]);
    try std.testing.expectEqualStrings("benchmark notes", manifest.ownership_evidence_fields[7]);
    try std.testing.expectEqualStrings("replay command", manifest.ownership_evidence_fields[8]);
    try std.testing.expectEqualStrings("rollback threshold", manifest.ownership_evidence_fields[9]);
    try std.testing.expectEqualStrings("retained discussion state", manifest.ownership_evidence_fields[10]);
    try std.testing.expectEqualStrings("reopen triggers", manifest.ownership_evidence_fields[11]);
    try std.testing.expectEqualStrings("trigger-specific evidence refresh", manifest.ownership_evidence_fields[12]);
    try std.testing.expectEqualStrings("parity scorecard link or blocker record", manifest.ownership_evidence_fields[13]);
    try std.testing.expectEqualStrings("indefinite-C policy link or non-applicability note", manifest.ownership_evidence_fields[14]);

    try std.testing.expectEqualStrings("freeze-map list change", manifest.trigger_conditions[0]);
    try std.testing.expectEqualStrings("freeze-map status-bucket change", manifest.trigger_conditions[1]);
    try std.testing.expectEqualStrings("bounded dual-implementation request for a deep-core study target", manifest.trigger_conditions[2]);
    try std.testing.expectEqualStrings("contradictory validation needing a written council decision", manifest.trigger_conditions[3]);

    try std.testing.expectEqualStrings("decision record ID", manifest.required_review_packet_fields[4]);
    try std.testing.expectEqualStrings("completed decision-record template or exact equivalent artifact", manifest.required_review_packet_fields[5]);
    try std.testing.expectEqualStrings("required approver set", manifest.required_review_packet_fields[7]);
    try std.testing.expectEqualStrings("automatic return-to-blocked trigger", manifest.required_review_packet_fields[12]);
    try std.testing.expectEqualStrings("rollback threshold", manifest.required_review_packet_fields[15]);
    try std.testing.expectEqualStrings("trigger-specific evidence refresh", manifest.required_review_packet_fields[18]);
    try std.testing.expectEqualStrings("written rationale", manifest.required_review_packet_fields[22]);

    try std.testing.expectEqualStrings("narrower_followup_answers_blocker", manifest.reopen_trigger_catalog[0]);
    try std.testing.expectEqualStrings("evidence_packet_stale_or_contradictory", manifest.reopen_trigger_catalog[1]);
    try std.testing.expectEqualStrings("ownership_or_validation_changed", manifest.reopen_trigger_catalog[2]);

    try std.testing.expectEqualStrings("keep_in_c", manifest.decision_buckets[0]);
    try std.testing.expectEqualStrings("study_only_followup", manifest.decision_buckets[1]);
    try std.testing.expectEqualStrings("bounded_dual_implementation", manifest.decision_buckets[2]);
    try std.testing.expectEqualStrings("defer_or_reject", manifest.decision_buckets[3]);

    try std.testing.expectEqualStrings("maintenance_mode", manifest.handoff.current_mode);
    try std.testing.expectEqual(@as(usize, 4), manifest.handoff.replay_commands.len);
    try std.testing.expectEqualStrings("make -C zigux phase15-validate", manifest.handoff.replay_commands[0]);
    try std.testing.expectEqualStrings("make -C zigux phase15-test", manifest.handoff.replay_commands[1]);
    try std.testing.expectEqualStrings("zig build test --build-file zigux/tests/phase15_build.zig", manifest.handoff.replay_commands[2]);
    try std.testing.expectEqualStrings("make -C zigux phase15", manifest.handoff.replay_commands[3]);
    try std.testing.expectEqualStrings("deep_core_blocker_posture_change", manifest.handoff.blocker_posture_requirement);
    try expectContains(manifest.handoff.next_step, "stay in maintenance mode unless a named reopen trigger or deep-core blocker posture change fires first");
    try expectContains(manifest.handoff.next_step, "Documentation/zigux/phase15-architecture-council-review-process.md");
    try expectContains(manifest.handoff.next_step, "Documentation/zigux/phase15-architecture-council-decision-record-template.md");
    try expectContains(manifest.handoff.next_step, "Documentation/zigux/phase15-governance-lane-sequencing.md");
    try expectContains(manifest.handoff.next_step, "zigux/tests/phase15_architecture_council_review_process_manifest.json");

    var landed_count: usize = 0;
    var saw_template_gap = false;
    var saw_field_sync = false;

    for (manifest.gaps) |gap| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "landed")) landed_count += 1;

        if (std.mem.eql(u8, gap.id, "phase15-decision-record-template")) {
            saw_template_gap = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-architecture-council-decision-record-template.md", gap.zigux_destination);
            try expectContains(gap.why_now, "reusable fill-in artifact");
        }

        if (std.mem.eql(u8, gap.id, "phase15-review-packet-field-sync")) {
            saw_field_sync = true;
            try expectContains(gap.why_now, "rollback-threshold");
            try expectContains(gap.why_now, "indefinite-C-policy fields");
        }
    }

    try std.testing.expectEqual(@as(usize, 11), landed_count);
    try std.testing.expect(saw_template_gap);
    try std.testing.expect(saw_field_sync);
}

test "phase 15 architecture council review-process doc records the current process language" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-architecture-council-review-process.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(survey_doc);

    try expectContains(survey_doc, "## Trigger Conditions");
    try expectContains(survey_doc, "## Required Review Packet");
    try expectContains(survey_doc, "## Decision Buckets");
    try expectContains(survey_doc, "## Reopen Trigger Catalog");
    try expectContains(survey_doc, "## Current Approval Posture");
    try expectContains(survey_doc, "## Maintenance-Mode Handoff");
    try expectContains(survey_doc, "PHASE15_LANE_KEY=P15-L08");
    try expectContains(survey_doc, "current-master-readback-2026-05-16");
    try expectContains(survey_doc, "exact branch-head parity is not recorded");
    try expectContains(survey_doc, "Documentation/zigux/phase15-architecture-council-decision-record-template.md");
    try expectContains(survey_doc, "completed `Documentation/zigux/phase15-architecture-council-decision-record-template.md` artifact");
    try expectContains(survey_doc, "automatic return-to-blocked trigger");
    try expectContains(survey_doc, "trigger-specific evidence refresh");
    try expectContains(survey_doc, "parity scorecard link, or an explicit blocker record");
    try expectContains(survey_doc, "no Architecture Council approval is currently recorded for a freeze-map status change");
    try expectContains(survey_doc, "current review-process evidence is limited to named `owner`, `required approver set`, `rollback owner`");
    try expectContains(survey_doc, "the reusable decision-record template");
    try expectContains(survey_doc, "named reopen triggers");
    try expectContains(survey_doc, "the deep-core blocker posture changes");
    try expectContains(survey_doc, "`keep_in_c`");
    try expectContains(survey_doc, "`study_only_followup`");
    try expectContains(survey_doc, "`bounded_dual_implementation`");
    try expectContains(survey_doc, "`defer_or_reject`");
}

test "phase 15 architecture council decision-record template carries the review packet fields in order" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const template_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(template_doc);

    try expectContains(template_doc, "## Required Header Fields");
    try expectContains(template_doc, "## Evidence Fields");
    try expectContains(template_doc, "## Decision Closeout Fields");
    try expectContains(template_doc, "DECISION_RECORD_ID=replace-with-stable-id");
    try expectContains(template_doc, "LINUX_ANCHOR_PATH=replace-with-linux-path");
    try expectContains(template_doc, "CURRENT_STATUS_BUCKET=freeze_in_c|study_only");
    try expectContains(template_doc, "REQUESTED_DECISION_BUCKET=keep_in_c|study_only_followup|bounded_dual_implementation|defer_or_reject");
    try expectContains(template_doc, "REQUIRED_APPROVER_SET=replace-with-approver-set");
    try expectContains(template_doc, "VALIDATION_GATE_SUMMARY=replace-with-summary-and-links");
    try expectContains(template_doc, "AUTOMATIC_RETURN_TO_BLOCKED_TRIGGER=replace-with-fail-closed-trigger");
    try expectContains(template_doc, "PARITY_SCORECARD_LINK_OR_BLOCKER_RECORD=replace-with-path-or-explicit-blocker");
    try expectContains(template_doc, "INDEFINITE_C_POLICY_LINK_OR_NON_APPLICABILITY_NOTE=replace-with-path-or-note");
    try expectContains(template_doc, "RETAINED_DISCUSSION_STATE=active_discussion|retired_from_active_discussion");
    try expectContains(template_doc, "TRIGGER_SPECIFIC_EVIDENCE_REFRESH=replace-with-required-reread-set");
    try expectContains(template_doc, "EXPLICIT_NON_GOALS=replace-with-bounded-non-goals");
    try expectContains(template_doc, "WRITTEN_RATIONALE=replace-with-rationale");
    try expectContains(template_doc, "If the outcome is `keep_in_c`, keep the blocker explicit");
    try expectContains(template_doc, "Keep the artifact narrow");
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

    try expectContains(review_checklist, "Architecture Council review record linked");
    try expectContains(review_checklist, "parity scorecard evidence or blocker state explicit");
    try expectContains(review_checklist, "current status bucket plus requested decision bucket explicit");
    try expectContains(review_checklist, "decision record ID, lane owner, required approver set, rollback owner, validation gate summary, evidence archive path, latest blocker disposition, benchmark notes, replay command, rollback threshold, parity scorecard link or blocker record, indefinite-C policy link or non-applicability note, explicit non-goals, and written rationale explicit");
    try expectContains(review_checklist, "retained discussion state, the current blocker, and reopen triggers explicit");
}
