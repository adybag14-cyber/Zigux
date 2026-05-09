const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectSliceContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |entry| {
        if (std.mem.eql(u8, entry, needle)) return;
    }
    try std.testing.expect(false);
}

fn isLowerHex40(text: []const u8) bool {
    if (text.len != 40) return false;
    for (text) |char| {
        if (!((char >= '0' and char <= '9') or (char >= 'a' and char <= 'f'))) return false;
    }
    return true;
}

const HandoffEvidence = struct {
    current_repo_handoff: []const u8,
    current_bounded_lane: []const u8,
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
    surveyed_commit_mode: []const u8,
    surveyed_commit_mode_reason: []const u8,
    roadmap_requirement: []const u8,
    anchor: []const u8,
    current_approval_state: []const u8,
    ownership_evidence_fields: []const []const u8,
    trigger_conditions: []const []const u8,
    required_review_packet_fields: []const []const u8,
    reopen_trigger_catalog: []const []const u8,
    decision_buckets: []const []const u8,
    handoff: Handoff,
    handoff_evidence: HandoffEvidence,
};

test "phase 15 architecture council review-process packet stays aligned on parked governance truthfulness" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const docs_readme = try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), "Documentation/zigux/README.md", std.testing.allocator, .limited(64 * 1024));
    defer std.testing.allocator.free(docs_readme);
    const review_checklist = try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), "Documentation/zigux/review-checklist.md", std.testing.allocator, .limited(64 * 1024));
    defer std.testing.allocator.free(review_checklist);
    const survey_doc = try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), "Documentation/zigux/phase15-architecture-council-review-process.md", std.testing.allocator, .limited(32 * 1024));
    defer std.testing.allocator.free(survey_doc);
    const script_readme = try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), "scripts/zigux/README.md", std.testing.allocator, .limited(64 * 1024));
    defer std.testing.allocator.free(script_readme);
    const tests_readme = try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), "zigux/tests/README.md", std.testing.allocator, .limited(64 * 1024));
    defer std.testing.allocator.free(tests_readme);
    const makefile = try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), "zigux/Makefile", std.testing.allocator, .limited(64 * 1024));
    defer std.testing.allocator.free(makefile);
    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), "zigux/tests/phase15_architecture_council_review_process_manifest.json", std.testing.allocator, .limited(24 * 1024));
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{ .ignore_unknown_fields = true });
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P15-L07", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("Architecture Council review process", manifest.roadmap_requirement);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-architecture-council-review-process.md", manifest.anchor);
    try std.testing.expectEqualStrings("no_freeze_map_status_change_approved", manifest.current_approval_state);
    try std.testing.expectEqual(@as(usize, 15), manifest.ownership_evidence_fields.len);
    try std.testing.expectEqual(@as(usize, 20), manifest.required_review_packet_fields.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.reopen_trigger_catalog.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.trigger_conditions.len);
    try std.testing.expectEqualStrings("maintenance_mode", manifest.handoff.current_mode);
    try std.testing.expectEqual(@as(usize, 5), manifest.handoff.replay_commands.len);
    try std.testing.expectEqualStrings("deep_core_blocker_posture_change", manifest.handoff.blocker_posture_requirement);

    try expectSliceContains(manifest.required_review_packet_fields, "required approver set");
    try expectSliceContains(manifest.required_review_packet_fields, "rollback threshold");
    try expectSliceContains(manifest.required_review_packet_fields, "parity scorecard link or blocker record");
    try expectSliceContains(manifest.required_review_packet_fields, "indefinite-C policy link or non-applicability note");
    try expectSliceContains(manifest.required_review_packet_fields, "explicit non-goals");
    try expectSliceContains(manifest.required_review_packet_fields, "written rationale");

    try expectSliceContains(manifest.ownership_evidence_fields, "required approver set");
    try expectSliceContains(manifest.ownership_evidence_fields, "rollback threshold");
    try expectSliceContains(manifest.ownership_evidence_fields, "parity scorecard link or blocker record");
    try expectSliceContains(manifest.ownership_evidence_fields, "indefinite-C policy link or non-applicability note");

    if (std.mem.eql(u8, manifest.surveyed_commit_mode, "verified_master_head")) {
        try std.testing.expect(isLowerHex40(manifest.surveyed_commit));
        try expectContains(manifest.surveyed_commit_mode_reason, "exact verified master-head SHA");
        try expectContains(survey_doc, "`PHASE15_PROVENANCE_MODE=verified_master_head`");
        try expectContains(survey_doc, "exact branch-head parity is now recorded for this packet");
    } else if (std.mem.eql(u8, manifest.surveyed_commit_mode, "dated_master_readback")) {
        try expectContains(manifest.surveyed_commit, "current-master-readback-");
        try expectContains(manifest.surveyed_commit_mode_reason, "dated readback marker");
        try expectContains(manifest.surveyed_commit_mode_reason, "4fc891b380cdd2991dff7676ade7f844df1b55fd");
        try expectContains(survey_doc, "`PHASE15_PROVENANCE_MODE=dated_master_readback`");
        try expectContains(survey_doc, "exact branch-head parity is not recorded for this packet");
        try expectContains(survey_doc, "previously recorded verified head `4fc891b380cdd2991dff7676ade7f844df1b55fd`");
        try expectContains(survey_doc, "landed `phase15-dated-readback-provenance-refresh`");
    } else {
        try std.testing.expect(false);
    }

    try expectContains(docs_readme, "Phase 15 notes");
    try expectContains(docs_readme, "`Documentation/zigux/phase15-architecture-council-review-process.md`");
    try expectContains(docs_readme, "`scripts/zigux/check-phase15-review-process-handoff.py`");
    try expectContains(docs_readme, "`zigux/tests/phase15_architecture_council_review_process_manifest.json`");
    try expectContains(docs_readme, "`zigux/tests/phase15_architecture_council_review_process.zig`");
    try expectContains(docs_readme, "no Architecture Council approval is recorded yet");

    try expectContains(review_checklist, "if the change touches the shared Phase 15 governance packet");
    try expectContains(review_checklist, "scripts/zigux/check-phase15-review-process-handoff.py");
    try expectContains(review_checklist, "zigux/tests/phase15_architecture_council_review_process_manifest.json");
    try expectContains(review_checklist, "if a freeze-map anchor is entering Architecture Council status review, are the decision record ID, lane owner, required approver set, rollback owner, validation gate summary, evidence archive path, latest blocker disposition, benchmark notes, replay command, rollback threshold, parity scorecard link or blocker record, indefinite-C policy link or non-applicability note, explicit non-goals, and written rationale explicit?");
    try expectContains(review_checklist, "if a freeze-map anchor is closing review with a stay-in-C outcome, are the retained discussion state, the current blocker, and reopen triggers explicit?");

    try expectContains(survey_doc, "## Trigger Conditions");
    try expectContains(survey_doc, "## Required Review Packet");
    try expectContains(survey_doc, "## Decision Buckets");
    try expectContains(survey_doc, "## Reopen Trigger Catalog");
    try expectContains(survey_doc, "## Current Approval Posture");
    try expectContains(survey_doc, "## Maintenance-Mode Handoff");
    try expectContains(survey_doc, "`PHASE15_LANE_KEY=P15-L07`");
    try expectContains(survey_doc, "workflow-backed replay anchor `.github/workflows/zigux-bootstrap.yml`");
    try expectContains(survey_doc, "dedicated `make -C zigux phase15-test` route");
    try expectContains(survey_doc, "current lane posture: `maintenance_mode`");
    try expectContains(survey_doc, "`make -C zigux phase15-validate`");
    try expectContains(survey_doc, "`zig build test --build-file zigux/tests/phase15_build.zig`");
    try expectContains(survey_doc, "`make -C zigux phase15`");
    try expectContains(survey_doc, "landed `phase15-roadmap-minimum-field-sync`");
    try expectContains(survey_doc, "landed `phase15-lane-owner-alignment-replay-visible`");
    try expectContains(survey_doc, "landed `phase15-workflow-replay-anchor-visible`");
    try expectContains(survey_doc, "landed `phase15-dedicated-make-test-replay-visible`");

    try expectContains(script_readme, "Phase 15 flow");
    try expectContains(script_readme, "check-phase15-review-process-handoff.py");
    try expectContains(script_readme, "phase15_architecture_council_review_process.zig");

    try expectContains(tests_readme, "keep the parked Phase 15 governance packet explicit in the tests root too");
    try expectContains(tests_readme, "Documentation/zigux/phase15-architecture-council-review-process.md");
    try expectContains(tests_readme, "zigux/tests/phase15_architecture_council_review_process.zig");
    try expectContains(tests_readme, "make -C zigux phase15");

    try expectContains(makefile, "PHONY += phase15-validate phase15-test phase15");
    try expectContains(makefile, "scripts/zigux/check-phase15-review-process-handoff.py --self-test");
    try expectContains(makefile, "scripts/zigux/check-phase15-review-process-handoff.py");

    try expectContains(manifest_json, "\"lane_key\": \"P15-L07\"");
    try expectContains(manifest_json, "\"handoff\"");
    try expectContains(manifest_json, "make -C zigux phase15-validate");
    try expectContains(manifest_json, ".github/workflows/zigux-bootstrap.yml");
    try expectContains(manifest_json, "make -C zigux phase15-test");
    try expectContains(manifest_json, "zig build test --build-file zigux/tests/phase15_build.zig");
    try expectContains(manifest_json, "deep_core_blocker_posture_change");
    try expectContains(manifest.handoff_evidence.current_repo_handoff, "Documentation/zigux/phase15-governance-lane-sequencing.md");
    try expectContains(manifest.handoff_evidence.current_repo_handoff, "zigux/tests/phase15_indefinite_c_blocker_evidence.zig");
    try expectContains(manifest.handoff_evidence.current_repo_handoff, "zigux/tests/phase15_handoff_next_steps_manifest.json");
    try expectContains(manifest.handoff_evidence.current_repo_handoff, "zigux/tests/phase15_readiness_gate_manifest.json");
    try expectContains(manifest.handoff_evidence.current_bounded_lane, "dedicated `make -C zigux phase15-test` route");
    try expectContains(manifest.handoff_evidence.current_bounded_lane, "direct `zig build test --build-file zigux/tests/phase15_build.zig` route");
}
