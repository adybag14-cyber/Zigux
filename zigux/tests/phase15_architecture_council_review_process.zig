const std = @import("std");

const ReviewProcessManifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    surveyed_commit_mode: []const u8,
    review_process_note: []const u8,
    decision_record_template: []const u8,
    decision_index_note: []const u8,
    indefinite_c_policy_note: []const u8,
    handoff_note: []const u8,
    shared_summary_gap_note: []const u8,
    checker: []const u8,
    build_gate: []const u8,
    review_checklist_entry_prompt: []const u8,
    review_checklist_boundary_rule: []const u8,
    review_checklist_stay_in_c_policy_boundary_rule: []const u8,
    review_checklist_entry_prompt_required_markers: []const []const u8,
    required_review_fields: []const []const u8,
    stay_in_c_closeout_fields: []const []const u8,
    reopen_evidence_fields: []const []const u8,
    supporting_context_fields: []const []const u8,
    review_outcome_fields: []const []const u8,
    review_outcome_markers: []const []const u8,
    indefinite_c_policy_required_markers: []const []const u8,
    decision_record_template_required_markers: []const []const u8,
    study_only_anchor_review_markers: []const []const u8,
    decision_record_template_study_only_rule: []const u8,
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
    try std.testing.expectEqualStrings("current-master-readback-2026-05-26", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("dated_master_readback", manifest.surveyed_commit_mode);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-architecture-council-review-process.md", manifest.review_process_note);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-architecture-council-decision-record-template.md", manifest.decision_record_template);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-architecture-council-decision-index.md", manifest.decision_index_note);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-indefinite-c-policy.md", manifest.indefinite_c_policy_note);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-handoff-next-steps-survey.md", manifest.handoff_note);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-shared-summary-gap.md", manifest.shared_summary_gap_note);
    try std.testing.expectEqualStrings("scripts/zigux/check-phase15-review-process-handoff.py", manifest.checker);
    try std.testing.expectEqualStrings("zigux/tests/phase15_architecture_council_review_process_build.zig", manifest.build_gate);
    try std.testing.expectEqualStrings("if a freeze-map anchor is entering Architecture Council status review", manifest.review_checklist_entry_prompt);
    try expectContains(manifest.review_checklist_boundary_rule, "exact Architecture Council field inventory stays owned by this note");
    try std.testing.expectEqualStrings(
        "`Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording",
        manifest.review_checklist_stay_in_c_policy_boundary_rule,
    );
    try std.testing.expectEqualStrings(
        "Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.",
        manifest.decision_record_template_study_only_rule,
    );
    try std.testing.expectEqual(@as(usize, 6), manifest.review_checklist_entry_prompt_required_markers.len);
    try std.testing.expectEqual(@as(usize, 24), manifest.required_review_fields.len);
    try std.testing.expectEqual(@as(usize, 9), manifest.stay_in_c_closeout_fields.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.reopen_evidence_fields.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.supporting_context_fields.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.review_outcome_fields.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.review_outcome_markers.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.indefinite_c_policy_required_markers.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.decision_record_template_required_markers.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.study_only_anchor_review_markers.len);
    try std.testing.expectEqual(@as(usize, 28), manifest.handoff_required_markers.len);
    try std.testing.expectEqual(@as(usize, 30), manifest.shared_gap_expected_present_paths.len);
    try std.testing.expectEqual(@as(usize, 0), manifest.shared_gap_expected_missing_paths.len);

    try expectSliceContains(manifest.review_checklist_entry_prompt_required_markers, "required approver set");
    try expectSliceContains(manifest.review_checklist_entry_prompt_required_markers, "rollback owner");
    try expectSliceContains(manifest.review_checklist_entry_prompt_required_markers, "evidence archive path");
    try expectSliceContains(manifest.review_checklist_entry_prompt_required_markers, "retained blocker posture");
    try expectSliceContains(manifest.review_checklist_entry_prompt_required_markers, "trigger-specific evidence refresh");
    try expectSliceContains(manifest.review_checklist_entry_prompt_required_markers, "return-to-blocked wording");
    try expectSliceContains(manifest.required_review_fields, "governance lane sequencing link or explicit scope note");
    try expectSliceContains(manifest.required_review_fields, "study-only anchor accounting link or explicit freeze-map-anchor confirmation");
    try expectSliceContains(manifest.stay_in_c_closeout_fields, "governance lane sequencing link or explicit scope note");
    try expectSliceContains(manifest.supporting_context_fields, "governance lane sequencing link or explicit scope note");
    try expectSliceContains(manifest.supporting_context_fields, "study-only anchor accounting link or explicit freeze-map-anchor confirmation");
    try expectSliceContains(manifest.review_outcome_fields, "closeout result");
    try expectSliceContains(manifest.review_outcome_fields, "follow-up owner");
    try expectSliceContains(manifest.review_outcome_fields, "next bounded step");
    try expectSliceContains(manifest.review_outcome_markers, "keep the anchor in `freeze_in_c`");
    try expectSliceContains(manifest.review_outcome_markers, "reopen review later with narrower evidence");
    try expectSliceContains(manifest.review_outcome_markers, "approve a status-bucket change in a separately linked decision record");
    try expectSliceContains(manifest.indefinite_c_policy_required_markers, "required approver set");
    try expectSliceContains(manifest.indefinite_c_policy_required_markers, "automatic return-to-blocked trigger");
    try expectSliceContains(manifest.indefinite_c_policy_required_markers, "trigger-specific evidence refresh");
    try expectSliceContains(manifest.indefinite_c_policy_required_markers, "parity scorecard link or blocker record");
    try expectSliceContains(manifest.study_only_anchor_review_markers, "`kernel/workqueue.c`");
    try expectSliceContains(manifest.study_only_anchor_review_markers, "not candidates for a freeze-in-C status review through this note");
    try expectSliceContains(manifest.handoff_required_markers, "`Documentation/zigux/phase15-architecture-council-decision-index.md`");
    try expectSliceContains(manifest.handoff_required_markers, "`Documentation/zigux/phase15-deep-core-blocker-survey.md`");
    try expectSliceContains(manifest.handoff_required_markers, "`zigux/tests/phase15_freeze_map_governance.zig`");
    try expectSliceContains(manifest.handoff_required_markers, "`zigux/tests/phase15_parity_scorecard.json`");
    try expectSliceContains(manifest.handoff_required_markers, "`zigux/tests/phase15_parity_scorecard.zig`");
    try expectSliceContains(manifest.handoff_required_markers, "`zigux/tests/phase15_handoff_next_steps_manifest.json`");
    try expectSliceContains(manifest.handoff_required_markers, "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`");
    try expectSliceContains(manifest.handoff_required_markers, "`scripts/zigux/check-phase15-docs-readme-alignment.py`");
    try expectSliceContains(manifest.handoff_required_markers, "`scripts/zigux/check-phase15-readiness-gate-packet.py`");
    try expectSliceContains(manifest.handoff_required_markers, "`scripts/zigux/check-phase15-handoff-note-alignment.py`");
    try expectSliceContains(manifest.handoff_required_markers, "`scripts/zigux/check-phase15-shared-summary-gap.py`");
    try expectSliceContains(manifest.shared_gap_expected_present_paths, "`Documentation/zigux/phase15-architecture-council-review-process.md`");
    try expectSliceContains(manifest.shared_gap_expected_present_paths, "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`");
    try expectSliceContains(manifest.shared_gap_expected_present_paths, "`Documentation/zigux/phase15-architecture-council-decision-index.md`");
    try expectSliceContains(manifest.shared_gap_expected_present_paths, "`Documentation/zigux/phase15-deep-core-blocker-survey.md`");
    try expectSliceContains(manifest.shared_gap_expected_present_paths, "`scripts/zigux/check-phase15-docs-readme-alignment.py`");
    try expectSliceContains(manifest.shared_gap_expected_present_paths, "`scripts/zigux/check-phase15-scripts-readme-alignment.py`");
    try expectSliceContains(manifest.shared_gap_expected_present_paths, "`scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`");
    try expectSliceContains(manifest.shared_gap_expected_present_paths, "`scripts/zigux/check-phase15-readiness-gate-packet.py`");
    try expectSliceContains(manifest.shared_gap_expected_present_paths, "`scripts/zigux/check-phase15-shared-summary-gap.py`");
    try expectSliceContains(manifest.shared_gap_expected_present_paths, "`zigux/tests/phase15_parity_scorecard.json`");
    try expectSliceContains(manifest.shared_gap_expected_present_paths, "`zigux/tests/phase15_governance_lane_sequencing_manifest.json`");
    try expectSliceContains(manifest.shared_gap_expected_present_paths, "`zigux/tests/phase15_governance_lane_sequencing.zig`");
    try expectSliceContains(manifest.shared_gap_expected_present_paths, "`zigux/tests/phase15_readiness_gate_manifest.json`");
    try expectSliceContains(manifest.shared_gap_expected_present_paths, "`zigux/tests/phase15_architecture_council_review_process.zig`");
    try expectSliceContains(manifest.shared_gap_expected_present_paths, "`zigux/tests/phase15_architecture_council_review_process_build.zig`");
    try expectSliceContains(manifest.shared_gap_expected_present_paths, "`zigux/tests/phase15_handoff_next_steps_manifest.json`");
    try expectSliceContains(manifest.shared_gap_expected_present_paths, "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`");
    try expectSliceContains(manifest.shared_gap_expected_present_paths, "`scripts/zigux/check-phase15-handoff-note-alignment.py`");
    try expectSliceContains(manifest.shared_gap_expected_present_paths, "`scripts/zigux/validate-phase15.py`");
}

test "phase 15 review-process note stays aligned with the focused replay packet" {
    const review_process = try readRepoFile("Documentation/zigux/phase15-architecture-council-review-process.md", 20 * 1024);
    defer std.testing.allocator.free(review_process);

    const decision_record_template = try readRepoFile("Documentation/zigux/phase15-architecture-council-decision-record-template.md", 16 * 1024);
    defer std.testing.allocator.free(decision_record_template);

    const decision_index = try readRepoFile("Documentation/zigux/phase15-architecture-council-decision-index.md", 16 * 1024);
    defer std.testing.allocator.free(decision_index);

    const indefinite_c_policy = try readRepoFile("Documentation/zigux/phase15-indefinite-c-policy.md", 16 * 1024);
    defer std.testing.allocator.free(indefinite_c_policy);

    const review_checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 48 * 1024);
    defer std.testing.allocator.free(review_checklist);

    const handoff_note = try readRepoFile("Documentation/zigux/phase15-handoff-next-steps-survey.md", 20 * 1024);
    defer std.testing.allocator.free(handoff_note);

    const gap_note = try readRepoFile("Documentation/zigux/phase15-shared-summary-gap.md", 20 * 1024);
    defer std.testing.allocator.free(gap_note);

    const tests_readme = try readRepoFile("zigux/tests/README.md", 96 * 1024);
    defer std.testing.allocator.free(tests_readme);

    const manifest_json = try readRepoFile("zigux/tests/phase15_architecture_council_review_process_manifest.json", 24 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(ReviewProcessManifest, std.testing.allocator, manifest_json, .{ .ignore_unknown_fields = true });
    defer parsed.deinit();
    const manifest = parsed.value;

    try expectContains(review_process, "PHASE15_STATUS=architecture_council_review_process_landed");
    try expectContains(review_process, manifest.surveyed_commit);
    try expectContains(review_process, "`zigux/tests/phase15_architecture_council_review_process_manifest.json`");
    try expectContains(review_process, "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`");
    try expectContains(review_process, manifest.decision_index_note);
    try expectContains(review_process, manifest.indefinite_c_policy_note);
    try expectContains(review_process, "`scripts/zigux/check-phase15-review-process-handoff.py`");
    try expectContains(review_process, "`scripts/zigux/check-phase15-tests-readme-alignment.py`");
    try expectContains(review_process, "`zigux/tests/phase15_architecture_council_review_process.zig`");
    try expectContains(review_process, "`zigux/tests/phase15_architecture_council_review_process_build.zig`");
    try expectContains(review_process, "the focused Zig replay, and the focused build-file replay are landed");
    try expectContains(review_process, "broader validator-first shared-summary surfaces remain gap-tracked");
    try expectContains(review_process, "focused review-process replay");
    try expectContains(review_process, "focused build-file replay");
    try expectContains(review_process, "defaults that record to dated-master-readback provenance");
    try expectContains(review_process, manifest.review_checklist_boundary_rule);
    try expectContains(decision_record_template, manifest.decision_record_template_study_only_rule);
    try expectContains(decision_index, manifest.review_process_note);
    try expectContains(decision_index, manifest.decision_record_template);
    try expectContains(review_checklist, manifest.review_checklist_entry_prompt);
    try expectContains(review_checklist, manifest.review_process_note);
    try expectContains(review_checklist, manifest.decision_record_template);
    try expectContains(review_checklist, manifest.review_checklist_stay_in_c_policy_boundary_rule);
    for (manifest.review_checklist_entry_prompt_required_markers) |marker| {
        try expectContains(review_checklist, marker);
    }
    try expectContains(handoff_note, manifest.decision_index_note);
    try expectContains(tests_readme, "## Phase 15 governance packet");
    try expectContains(tests_readme, "`scripts/zigux/check-phase15-review-process-handoff.py`");
    try expectContains(tests_readme, "`zigux/tests/phase15_architecture_council_review_process.zig`");
    try expectContains(tests_readme, "`zigux/tests/phase15_architecture_council_review_process_build.zig`");
    try expectContains(tests_readme, "Current `master` does materialize `zigux/tests/phase15_architecture_council_review_process_build.zig`, so keep that focused build-file replay in the directly readable governance packet instead of undercounting the Architecture Council review-process evidence.");
    try expectContains(tests_readme, "returned review-process build replay");

    for (manifest.required_review_fields) |field| {
        try expectContains(review_process, field);
        try expectContains(decision_record_template, field);
    }
    for (manifest.stay_in_c_closeout_fields) |field| {
        try expectContains(review_process, field);
        try expectContains(decision_record_template, field);
    }
    for (manifest.reopen_evidence_fields) |field| {
        try expectContains(review_process, field);
    }
    for (manifest.supporting_context_fields) |field| {
        try expectContains(review_process, field);
        try expectContains(decision_record_template, field);
    }
    for (manifest.review_outcome_fields) |field| {
        try expectContains(review_process, field);
        try expectContains(decision_record_template, field);
    }
    for (manifest.review_outcome_markers) |marker| {
        try expectContains(review_process, marker);
    }
    for (manifest.indefinite_c_policy_required_markers) |marker| {
        try expectContains(indefinite_c_policy, marker);
    }
    for (manifest.decision_record_template_required_markers) |marker| {
        try expectContains(decision_record_template, marker);
    }
    for (manifest.study_only_anchor_review_markers) |marker| {
        try expectContains(review_process, marker);
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

test "phase 15 review-process build gate stays aligned with the focused replay packet" {
    const build_gate = try readRepoFile("zigux/tests/phase15_architecture_council_review_process_build.zig", 8 * 1024);
    defer std.testing.allocator.free(build_gate);

    try expectContains(build_gate, "phase15_architecture_council_review_process.zig");
    try expectContains(build_gate, "phase15-architecture-council-review-process-tests");
    try expectContains(build_gate, "Run the focused Phase 15 Architecture Council review-process test");
    try expectContains(build_gate, "test_step.dependOn");
}

test "phase 15 review-process handoff checker fails closed on missing present paths" {
    const checker = try readRepoFile("scripts/zigux/check-phase15-review-process-handoff.py", 48 * 1024);
    defer std.testing.allocator.free(checker);

    const review_process = try readRepoFile("Documentation/zigux/phase15-architecture-council-review-process.md", 20 * 1024);
    defer std.testing.allocator.free(review_process);

    const gap_note = try readRepoFile("Documentation/zigux/phase15-shared-summary-gap.md", 20 * 1024);
    defer std.testing.allocator.free(gap_note);

    try expectContains(checker, "shared-summary gap note claims materialized path is missing from repo");
    try expectContains(checker, "focused review-process Zig replay is missing from repo");
    try expectContains(checker, "review-process note is missing the review-checklist boundary rule");
    try expectContains(checker, "review checklist entry prompt is missing required stay-in-C policy boundary marker");
    try expectContains(checker, "decision-record template is missing the study-only anchor boundary rule");
    try expectContains(checker, "review-process note is missing supporting context field");
    try expectContains(checker, "decision-record template is missing supporting context field");
    try expectContains(checker, "repo_path = _marker_to_repo_path(marker)");
    try expectContains(checker, "zigux/tests/phase15_architecture_council_review_process.zig");
    try expectContains(checker, "PHASE15_REVIEW_PROCESS_HANDOFF_SELF_TEST=pass");
    try expectContains(checker, "current-master-readback-2026-05-26");
    try expectContains(review_process, "current-master-readback-2026-05-26");
    try expectContains(gap_note, "`Documentation/zigux/phase15-architecture-council-decision-index.md`");
    try expectContains(gap_note, "`zigux/tests/phase15_architecture_council_review_process.zig`");
    try expectContains(gap_note, "`zigux/tests/phase15_architecture_council_review_process_build.zig`");
    try expectContains(gap_note, "`zigux/tests/phase15_handoff_next_steps_manifest.json`");
    try expectContains(gap_note, "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`");
    try expectContains(gap_note, "`scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`");
    try expectContains(gap_note, "`scripts/zigux/check-phase15-handoff-note-alignment.py`");
    try expectContains(gap_note, "`scripts/zigux/validate-phase15.py`");
    try expectContains(gap_note, "`zigux/tests/phase15_build.zig`");
}
