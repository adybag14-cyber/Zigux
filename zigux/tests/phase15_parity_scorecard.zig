const std = @import("std");

const EvidenceArchive = struct {
    decision_record_path: []const u8,
    linked_evidence: []const []const u8,
    benchmark_notes_status: []const u8,
    replay_command: []const u8,
    latest_blocker_disposition: []const u8,
    rollback_threshold: []const u8,
};

const AnchorScorecard = struct {
    path: []const u8,
    status: []const u8,
    line_count: usize,
    phase14_evidence_present: bool,
    lane_owner: []const u8,
    council_inputs: []const []const u8,
    evidence_thresholds: []const []const u8,
    validation_gates: []const []const u8,
    rollback_owner: []const u8,
    evidence_archive: EvidenceArchive,
};

const ReviewProcess = struct {
    decision_record_required: bool,
    required_record_fields: []const []const u8,
    reopen_trigger_catalog: []const []const u8,
    retirement_rule: []const u8,
    archive_requirements: []const []const u8,
};

const HandoffEvidence = struct {
    roadmap_source: []const u8,
    roadmap_requirements: []const []const u8,
    bootstrap_ledger_anchor: []const u8,
    current_repo_handoff: []const u8,
    maintenance_mode_next_step: []const u8,
};

const CurrentParityTrackingGap = struct {
    roadmap_requirement: []const u8,
    current_gap: []const u8,
    repo_state: []const u8,
    closure_signal: []const u8,
    remaining_blocker: []const u8,
};

const RepoEvidence = struct {
    freeze_map_present: bool,
    review_checklist_present: bool,
    phase15_review_process_note_present: bool,
    phase15_indefinite_c_policy_note_present: bool,
    phase14_rcu_survey_present: bool,
    phase14_skbuff_survey_present: bool,
    phase15_readme_reviewability_present: bool,
    phase15_scorecard_note_present: bool,
    phase15_evidence_archive_templates_present: bool,
    phase15_anchor_owner_tracking_present: bool,
    phase15_handoff_checker_present: bool,
    phase15_docs_root_reviewability_guard_present: bool,
    phase15_scorecard_test_present: bool,
    phase15_scorecard_manifest_present: bool,
    phase15_build_present: bool,
    phase15_make_target_present: bool,
    phase15_workflow_replay_present: bool,
};

const ScorecardMetrics = struct {
    freeze_in_c_anchor_count: usize,
    anchors_with_phase14_survey_evidence: usize,
    reserved_evidence_archive_templates: usize,
    anchors_with_explicit_blocker_dispositions: usize,
    anchors_with_explicit_owner_and_rollback_owner: usize,
    required_review_process_record_fields: usize,
    reopen_trigger_catalog_entries: usize,
    repo_evidence_checks_green: usize,
    landed_scorecard_gaps: usize,
    blocked_scorecard_gaps: usize,
    replay_surfaces_available: usize,
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
    review_process: ReviewProcess,
    handoff_evidence: HandoffEvidence,
    current_parity_tracking_gap: CurrentParityTrackingGap,
    repo_evidence: RepoEvidence,
    gaps: []const Gap,
    scorecard_metrics: ScorecardMetrics,
    anchors: []const AnchorScorecard,
};

fn readAlloc(io: std.Io, path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, std.testing.allocator, .limited(limit));
}

fn countLines(io: std.Io, path: []const u8, limit: usize) !usize {
    const bytes = try readAlloc(io, path, limit);
    defer std.testing.allocator.free(bytes);

    if (bytes.len == 0) return 0;

    var total = std.mem.count(u8, bytes, "\n");
    if (bytes[bytes.len - 1] != '\n') total += 1;
    return total;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectTemplate(io: std.Io, anchor: AnchorScorecard) !void {
    const template_doc = try readAlloc(io, anchor.evidence_archive.decision_record_path, 12 * 1024);
    defer std.testing.allocator.free(template_doc);

    try expectContains(template_doc, anchor.path);
    try expectContains(template_doc, "decision record ID");
    try expectContains(template_doc, "requested decision bucket");
    try expectContains(template_doc, anchor.lane_owner);
    try expectContains(template_doc, anchor.rollback_owner);
    try expectContains(template_doc, anchor.evidence_archive.replay_command);
    try expectContains(template_doc, anchor.evidence_archive.latest_blocker_disposition);
    try expectContains(template_doc, "automatic return-to-blocked trigger");
    try expectContains(template_doc, "rollback threshold");
    try expectContains(template_doc, anchor.evidence_archive.rollback_threshold);
    try expectContains(template_doc, "phase15-indefinite-c-policy.md");
    try expectContains(template_doc, "narrower_followup_answers_blocker");
    try expectContains(template_doc, "evidence_packet_stale_or_contradictory");
    try expectContains(template_doc, "ownership_or_validation_changed");
    try expectContains(template_doc, "no Architecture Council approval claim");
    try expectContains(template_doc, "written rationale");
}

fn countAnchorsWithExplicitOwnerCoverage(anchors: []const AnchorScorecard) usize {
    var total: usize = 0;
    for (anchors) |anchor| {
        if (anchor.lane_owner.len > 0 and anchor.rollback_owner.len > 0) total += 1;
    }
    return total;
}

fn countRepoEvidenceGreen(repo_evidence: RepoEvidence) usize {
    var total: usize = 0;
    inline for ([_]bool{
        repo_evidence.freeze_map_present,
        repo_evidence.review_checklist_present,
        repo_evidence.phase15_review_process_note_present,
        repo_evidence.phase15_indefinite_c_policy_note_present,
        repo_evidence.phase14_rcu_survey_present,
        repo_evidence.phase14_skbuff_survey_present,
        repo_evidence.phase15_readme_reviewability_present,
        repo_evidence.phase15_scorecard_note_present,
        repo_evidence.phase15_evidence_archive_templates_present,
        repo_evidence.phase15_anchor_owner_tracking_present,
        repo_evidence.phase15_handoff_checker_present,
        repo_evidence.phase15_docs_root_reviewability_guard_present,
        repo_evidence.phase15_scorecard_test_present,
        repo_evidence.phase15_scorecard_manifest_present,
        repo_evidence.phase15_build_present,
        repo_evidence.phase15_make_target_present,
        repo_evidence.phase15_workflow_replay_present,
    }) |present| {
        if (present) total += 1;
    }
    return total;
}

test "phase 15 parity scorecard manifest tracks the current roadmap gap honestly" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try readAlloc(io_instance.io(), "zigux/tests/phase15_parity_scorecard.json", 48 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P15-L04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("02264a3240cd30ce45c9a932047a0204b7ab5029", manifest.surveyed_commit);
    try std.testing.expect(manifest.review_process.decision_record_required);
    try std.testing.expectEqual(@as(usize, 15), manifest.review_process.required_record_fields.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.review_process.reopen_trigger_catalog.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.review_process.archive_requirements.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.handoff_evidence.roadmap_requirements.len);
    try std.testing.expectEqualStrings("parity scorecard", manifest.current_parity_tracking_gap.roadmap_requirement);
    try expectContains(manifest.current_parity_tracking_gap.current_gap, "lane identity");
    try expectContains(manifest.current_parity_tracking_gap.current_gap, "surveyed-master provenance");
    try expectContains(manifest.current_parity_tracking_gap.current_gap, "rollback-threshold");
    try expectContains(manifest.current_parity_tracking_gap.current_gap, "focused handoff-checker route");
    try expectContains(manifest.current_parity_tracking_gap.current_gap, "docs-root reviewability guard");
    try expectContains(manifest.handoff_evidence.current_repo_handoff, "Documentation/zigux/README.md");
    try expectContains(manifest.handoff_evidence.current_repo_handoff, "Documentation/zigux/phase15-handoff-next-steps-survey.md");
    try expectContains(manifest.handoff_evidence.current_repo_handoff, "scripts/zigux/README.md");
    try expectContains(manifest.handoff_evidence.current_repo_handoff, "scripts/zigux/check-phase15-review-process-handoff.py");
    try expectContains(manifest.handoff_evidence.current_repo_handoff, "scripts/zigux/validate-phase15.py");
    try expectContains(manifest.handoff_evidence.current_repo_handoff, "zigux/tests/README.md");
    try expectContains(manifest.handoff_evidence.current_repo_handoff, "zigux/tests/phase15_docs_root_reviewability.zig");
    try expectContains(manifest.current_parity_tracking_gap.repo_state, "scripts/zigux/README.md");
    try expectContains(manifest.current_parity_tracking_gap.repo_state, "scripts/zigux/check-phase15-review-process-handoff.py");
    try expectContains(manifest.current_parity_tracking_gap.repo_state, "scripts/zigux/validate-phase15.py");
    try expectContains(manifest.current_parity_tracking_gap.repo_state, "zigux/tests/README.md");
    try expectContains(manifest.current_parity_tracking_gap.repo_state, "zigux/tests/phase15_docs_root_reviewability.zig");
    try expectContains(manifest.current_parity_tracking_gap.repo_state, "make -C zigux phase15");
    try expectContains(manifest.current_parity_tracking_gap.closure_signal, "parity-tracking gap");
    try expectContains(manifest.current_parity_tracking_gap.remaining_blocker, "deep-core status-change blocker");

    try std.testing.expect(manifest.repo_evidence.freeze_map_present);
    try std.testing.expect(manifest.repo_evidence.review_checklist_present);
    try std.testing.expect(manifest.repo_evidence.phase15_review_process_note_present);
    try std.testing.expect(manifest.repo_evidence.phase15_indefinite_c_policy_note_present);
    try std.testing.expect(manifest.repo_evidence.phase14_rcu_survey_present);
    try std.testing.expect(manifest.repo_evidence.phase14_skbuff_survey_present);
    try std.testing.expect(manifest.repo_evidence.phase15_readme_reviewability_present);
    try std.testing.expect(manifest.repo_evidence.phase15_scorecard_note_present);
    try std.testing.expect(manifest.repo_evidence.phase15_evidence_archive_templates_present);
    try std.testing.expect(manifest.repo_evidence.phase15_anchor_owner_tracking_present);
    try std.testing.expect(manifest.repo_evidence.phase15_handoff_checker_present);
    try std.testing.expect(manifest.repo_evidence.phase15_docs_root_reviewability_guard_present);
    try std.testing.expect(manifest.repo_evidence.phase15_scorecard_test_present);
    try std.testing.expect(manifest.repo_evidence.phase15_scorecard_manifest_present);
    try std.testing.expect(manifest.repo_evidence.phase15_build_present);
    try std.testing.expect(manifest.repo_evidence.phase15_make_target_present);
    try std.testing.expect(manifest.repo_evidence.phase15_workflow_replay_present);
    try std.testing.expectEqual(@as(usize, 17), countRepoEvidenceGreen(manifest.repo_evidence));

    try std.testing.expectEqual(@as(usize, 4), manifest.anchors.len);
    try std.testing.expectEqual(@as(usize, 20), manifest.gaps.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.scorecard_metrics.freeze_in_c_anchor_count);
    try std.testing.expectEqual(@as(usize, 2), manifest.scorecard_metrics.anchors_with_phase14_survey_evidence);
    try std.testing.expectEqual(@as(usize, 4), manifest.scorecard_metrics.anchors_with_explicit_owner_and_rollback_owner);
    try std.testing.expectEqual(manifest.scorecard_metrics.anchors_with_explicit_owner_and_rollback_owner, countAnchorsWithExplicitOwnerCoverage(manifest.anchors));
    try std.testing.expectEqual(@as(usize, 17), manifest.scorecard_metrics.repo_evidence_checks_green);
    try std.testing.expectEqual(manifest.scorecard_metrics.repo_evidence_checks_green, countRepoEvidenceGreen(manifest.repo_evidence));
    try std.testing.expectEqual(@as(usize, 19), manifest.scorecard_metrics.landed_scorecard_gaps);
    try std.testing.expectEqual(@as(usize, 1), manifest.scorecard_metrics.blocked_scorecard_gaps);
    try std.testing.expectEqual(@as(usize, 15), manifest.scorecard_metrics.required_review_process_record_fields);
    try std.testing.expectEqualStrings("current roadmap phase", manifest.review_process.required_record_fields[0]);
    try std.testing.expectEqualStrings("automatic return-to-blocked trigger", manifest.review_process.required_record_fields[7]);
    try std.testing.expectEqualStrings("rollback threshold", manifest.review_process.required_record_fields[8]);
    try std.testing.expectEqualStrings("indefinite-C policy link or applicability note", manifest.review_process.required_record_fields[9]);
    try std.testing.expectEqualStrings("trigger-specific refreshed evidence by path", manifest.review_process.required_record_fields[12]);
    try std.testing.expectEqualStrings("refreshed ownership records when `ownership_or_validation_changed` is cited", manifest.review_process.required_record_fields[13]);
    try std.testing.expectEqualStrings("written rationale", manifest.review_process.required_record_fields[14]);
    try expectContains(manifest.review_process.retirement_rule, "current roadmap phase");
    try expectContains(manifest.review_process.retirement_rule, "automatic return-to-blocked trigger");
    try expectContains(manifest.review_process.retirement_rule, "rollback threshold");
    try expectContains(manifest.review_process.retirement_rule, "indefinite-C policy link or applicability note");
    try expectContains(manifest.review_process.retirement_rule, "trigger-specific refreshed evidence by path");
    try expectContains(manifest.review_process.retirement_rule, "ownership_or_validation_changed");
    try expectContains(manifest.review_process.retirement_rule, "written rationale");

    const sched_lines = try countLines(io_instance.io(), "kernel/sched/core.c", 1024 * 1024);
    const page_alloc_lines = try countLines(io_instance.io(), "mm/page_alloc.c", 1024 * 1024);
    const rcu_lines = try countLines(io_instance.io(), "kernel/rcu/tree.c", 1024 * 1024);
    const skbuff_lines = try countLines(io_instance.io(), "net/core/skbuff.c", 1024 * 1024);

    var saw_blocked_gap = false;

    for (manifest.gaps) |gap| {
        if (std.mem.eql(u8, gap.id, "phase15-deep-core-status-change-blocker")) {
            saw_blocked_gap = true;
            try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", gap.status);
        }
    }
    try std.testing.expect(saw_blocked_gap);

    for (manifest.anchors) |anchor| {
        try std.testing.expectEqualStrings("freeze_in_c", anchor.status);
        try std.testing.expect(anchor.council_inputs.len >= 3);
        try std.testing.expect(anchor.evidence_thresholds.len >= 3);
        try std.testing.expect(anchor.validation_gates.len >= 3);
        try std.testing.expect(anchor.lane_owner.len > 0);
        try std.testing.expect(anchor.rollback_owner.len > 0);
        try std.testing.expect(anchor.evidence_archive.linked_evidence.len >= 2);
        try std.testing.expectEqualStrings("zig build test --build-file zigux/tests/phase15_build.zig", anchor.evidence_archive.replay_command);
        try expectContains(anchor.evidence_archive.latest_blocker_disposition, "blocked");
        try expectContains(anchor.evidence_archive.rollback_threshold, "blocked review posture");
        try expectTemplate(io_instance.io(), anchor);

        if (std.mem.eql(u8, anchor.path, "kernel/sched/core.c")) {
            try std.testing.expectEqual(sched_lines, anchor.line_count);
            try std.testing.expect(!anchor.phase14_evidence_present);
        } else if (std.mem.eql(u8, anchor.path, "mm/page_alloc.c")) {
            try std.testing.expectEqual(page_alloc_lines, anchor.line_count);
            try std.testing.expect(!anchor.phase14_evidence_present);
        } else if (std.mem.eql(u8, anchor.path, "kernel/rcu/tree.c")) {
            try std.testing.expectEqual(rcu_lines, anchor.line_count);
            try std.testing.expect(anchor.phase14_evidence_present);
        } else if (std.mem.eql(u8, anchor.path, "net/core/skbuff.c")) {
            try std.testing.expectEqual(skbuff_lines, anchor.line_count);
            try std.testing.expect(anchor.phase14_evidence_present);
        } else {
            return error.UnexpectedAnchor;
        }
    }
}

test "phase 15 parity scorecard docs keep the parity-tracking survey aligned" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const scorecard_doc = try readAlloc(io_instance.io(), "Documentation/zigux/phase15-parity-scorecard.md", 32 * 1024);
    defer std.testing.allocator.free(scorecard_doc);

    const review_process_doc = try readAlloc(io_instance.io(), "Documentation/zigux/phase15-architecture-council-review-process.md", 32 * 1024);
    defer std.testing.allocator.free(review_process_doc);

    const indefinite_c_policy_doc = try readAlloc(io_instance.io(), "Documentation/zigux/phase15-indefinite-c-policy.md", 32 * 1024);
    defer std.testing.allocator.free(indefinite_c_policy_doc);

    const docs_readme = try readAlloc(io_instance.io(), "Documentation/zigux/README.md", 32 * 1024);
    defer std.testing.allocator.free(docs_readme);

    const makefile = try readAlloc(io_instance.io(), "zigux/Makefile", 64 * 1024);
    defer std.testing.allocator.free(makefile);

    const bootstrap_workflow = try readAlloc(io_instance.io(), ".github/workflows/zigux-bootstrap.yml", 64 * 1024);
    defer std.testing.allocator.free(bootstrap_workflow);

    try expectContains(scorecard_doc, "PHASE15_LANE_KEY=P15-L04");
    try expectContains(scorecard_doc, "survey provenance refreshed against verified `master` head `02264a3240cd30ce45c9a932047a0204b7ab5029`");
    try expectContains(scorecard_doc, "## Current Parity-Tracking Gap");
    try expectContains(scorecard_doc, "That closes the current parity-tracking gap for the roadmap requirement `parity scorecard`.");
    try expectContains(scorecard_doc, "lane identity, surveyed-master provenance, roadmap wording, rollback-threshold field sync, focused handoff-checker route, dedicated docs-root reviewability guard, and replay-backed evidence packet current");
    try expectContains(scorecard_doc, "Documentation/zigux/README.md");
    try expectContains(scorecard_doc, "Documentation/zigux/phase15-handoff-next-steps-survey.md");
    try expectContains(scorecard_doc, "scripts/zigux/README.md");
    try expectContains(scorecard_doc, "scripts/zigux/check-phase15-review-process-handoff.py");
    try expectContains(scorecard_doc, "scripts/zigux/validate-phase15.py");
    try expectContains(scorecard_doc, "zigux/tests/README.md");
    try expectContains(scorecard_doc, "zigux/tests/phase15_docs_root_reviewability.zig");
    try expectContains(scorecard_doc, "shared replay path");
    try expectContains(scorecard_doc, "anchors with explicit lane-owner plus rollback-owner coverage: `4 / 4`");
    try expectContains(scorecard_doc, "required review-process record fields tracked in the manifest: `15`");
    try expectContains(scorecard_doc, "repo evidence checks currently green: `17 / 17`");
    try expectContains(scorecard_doc, "landed scorecard gaps: `19 / 20`");
    try expectContains(scorecard_doc, "blocked scorecard gaps: `1 / 20`");
    try expectContains(scorecard_doc, "the current roadmap phase, the decision record ID, and the lane owner");
    try expectContains(scorecard_doc, "the automatic return-to-blocked trigger that sends the anchor back to blocked review posture");
    try expectContains(scorecard_doc, "the rollback threshold that names which stale, missing, contradictory, or widened evidence returns the anchor to blocked review posture");
    try expectContains(scorecard_doc, "the indefinite-C policy link, or an explicit note saying why the packet is not yet entering that policy posture");
    try expectContains(scorecard_doc, "the trigger-specific refreshed evidence by path, together with the current blocker disposition restatement, for every cited reopen trigger");
    try expectContains(scorecard_doc, "refreshed lane-owner and rollback-owner evidence whenever the cited reopen trigger is `ownership_or_validation_changed`");
    try expectContains(scorecard_doc, "the written rationale for why the current product state needs council attention now");
    try expectContains(scorecard_doc, "phase15-scorecard-review-packet-field-sync");
    try expectContains(scorecard_doc, "focused handoff-checker route");
    try expectContains(scorecard_doc, "dedicated docs-root reviewability guard");
    try expectContains(scorecard_doc, "shared bootstrap workflow now runs the landed Phase 15 governance bundle through `make -C zigux phase15`");
    try expectContains(scorecard_doc, "every freeze-in-C anchor still carries both a current lane owner and a rollback owner");
    try expectContains(review_process_doc, "trigger-specific refreshed evidence by path");
    try expectContains(review_process_doc, "ownership_or_validation_changed");
    try expectContains(review_process_doc, "rollback-threshold");
    try expectContains(review_process_doc, "parity scorecard");
    try expectContains(indefinite_c_policy_doc, "parity scorecard");
    try expectContains(docs_readme, "Phase 15 notes");
    try expectContains(docs_readme, "phase15-parity-scorecard.md");
    try expectContains(makefile, "PHONY += phase15-validate phase15-test phase15");
    try expectContains(makefile, "phase15-test:");
    try expectContains(makefile, "zig build test --build-file zigux/tests/phase15_build.zig");
    try expectContains(makefile, "phase15: phase15-validate phase15-test");
    try expectContains(bootstrap_workflow, "Run Phase 15 governance tests");
    try expectContains(bootstrap_workflow, "run: make -C zigux phase15");
}

test "phase 15 parity scorecard gap inventory stays bounded" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try readAlloc(io_instance.io(), "zigux/tests/phase15_parity_scorecard.json", 48 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    try std.testing.expectEqual(parsed.value.scorecard_metrics.repo_evidence_checks_green, countRepoEvidenceGreen(parsed.value.repo_evidence));

    var landed: usize = 0;
    var blocked: usize = 0;
    var saw_owner_tracking = false;
    var saw_handoff_sync = false;
    var saw_review_packet_field_sync = false;

    for (parsed.value.gaps) |gap| {
        if (std.mem.eql(u8, gap.status, "starter_landed")) landed += 1;
        if (std.mem.eql(u8, gap.status, "blocked_on_stay_in_c_evidence")) blocked += 1;
        if (std.mem.eql(u8, gap.id, "phase15-anchor-owner-tracking")) saw_owner_tracking = true;
        if (std.mem.eql(u8, gap.id, "phase15-maintenance-mode-handoff-sync")) saw_handoff_sync = true;
        if (std.mem.eql(u8, gap.id, "phase15-scorecard-review-packet-field-sync")) {
            saw_review_packet_field_sync = true;
            try expectContains(gap.why_now, "rollback threshold");
        }
    }

    try std.testing.expectEqual(@as(usize, 19), landed);
    try std.testing.expectEqual(@as(usize, 1), blocked);
    try std.testing.expect(saw_owner_tracking);
    try std.testing.expect(saw_handoff_sync);
    try std.testing.expect(saw_review_packet_field_sync);
}
