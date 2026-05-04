const std = @import("std");

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const HandoffEvidence = struct {
    roadmap_source: []const u8,
    roadmap_handoff: []const u8,
    bootstrap_ledger_anchor: []const u8,
    current_repo_handoff: []const u8,
    current_bounded_lane: []const u8,
    maintenance_mode_next_step: []const u8,
};

const Handoff = struct {
    current_mode: []const u8,
    replay_commands: []const []const u8,
    blocker_posture_requirement: []const u8,
    next_step: []const u8,
};

fn expectTemplateEvidence(
    io: std.Io,
    path: []const u8,
    lane_owner: []const u8,
    rollback_owner: []const u8,
) !void {
    const template_doc = try std.Io.Dir.cwd().readFileAlloc(
        io,
        path,
        std.testing.allocator,
        .limited(12 * 1024),
    );
    defer std.testing.allocator.free(template_doc);

    try std.testing.expect(std.mem.indexOf(u8, template_doc, "requested decision bucket: `pending_no_request`") != null);
    try std.testing.expect(std.mem.indexOf(u8, template_doc, "decision record ID: `pending_no_architecture_council_request`") != null);
    try std.testing.expect(std.mem.indexOf(u8, template_doc, "no Architecture Council approval claim") != null);
    try std.testing.expect(std.mem.indexOf(u8, template_doc, lane_owner) != null);
    try std.testing.expect(std.mem.indexOf(u8, template_doc, rollback_owner) != null);
    try std.testing.expect(std.mem.indexOf(u8, template_doc, "rollback threshold") != null);
    try std.testing.expect(std.mem.indexOf(u8, template_doc, "retired_from_active_discussion") != null);
    try std.testing.expect(std.mem.indexOf(u8, template_doc, "ownership_or_validation_changed") != null);
}

fn expectOccurrenceCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var start: usize = 0;

    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }

    try std.testing.expectEqual(expected, count);
}

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    roadmap_requirement: []const u8,
    anchor: []const u8,
    current_approval_state: []const u8,
    approval_evidence_fields: []const []const u8,
    approval_evidence_paths: []const []const u8,
    ownership_evidence_fields: []const []const u8,
    ownership_evidence_paths: []const []const u8,
    trigger_conditions: []const []const u8,
    required_review_packet_fields: []const []const u8,
    reopen_trigger_catalog: []const []const u8,
    ownership_refresh_trigger: []const u8,
    ownership_refresh_fields: []const []const u8,
    decision_buckets: []const []const u8,
    handoff_evidence: HandoffEvidence,
    handoff: Handoff,
    gaps: []const Gap,
};

const expected_lane_key = "P15-L08";

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_stay_in_c_evidence");
}

fn isLowerHex40(value: []const u8) bool {
    if (value.len != 40) return false;
    for (value) |byte| {
        const is_digit = byte >= '0' and byte <= '9';
        const is_lower_hex = byte >= 'a' and byte <= 'f';
        if (!is_digit and !is_lower_hex) return false;
    }
    return true;
}

test "phase 15 architecture council review-process manifest records current trigger, packet, and handoff behavior" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_architecture_council_review_process_manifest.json",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings(expected_lane_key, manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expect(isLowerHex40(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("Architecture Council review process", manifest.roadmap_requirement);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-architecture-council-review-process.md", manifest.anchor);
    try std.testing.expectEqualStrings("no_freeze_map_status_change_approved", manifest.current_approval_state);
    try std.testing.expectEqual(@as(usize, 13), manifest.ownership_evidence_fields.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.approval_evidence_fields.len);
    try std.testing.expectEqual(@as(usize, 8), manifest.approval_evidence_paths.len);
    try std.testing.expectEqual(@as(usize, 7), manifest.ownership_evidence_paths.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.trigger_conditions.len);
    try std.testing.expectEqual(@as(usize, 22), manifest.required_review_packet_fields.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.reopen_trigger_catalog.len);
    try std.testing.expectEqualStrings("ownership_or_validation_changed", manifest.ownership_refresh_trigger);
    try std.testing.expectEqual(@as(usize, 2), manifest.ownership_refresh_fields.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.decision_buckets.len);
    try std.testing.expectEqual(@as(usize, 22), manifest.gaps.len);

    try std.testing.expectEqualStrings("requested decision bucket", manifest.approval_evidence_fields[0]);
    try std.testing.expectEqualStrings("decision record ID", manifest.approval_evidence_fields[1]);
    try std.testing.expectEqualStrings("no Architecture Council approval claim", manifest.approval_evidence_fields[2]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-architecture-council-review-process.md", manifest.approval_evidence_paths[0]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-freeze-map-governance.md", manifest.approval_evidence_paths[1]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-parity-scorecard.md", manifest.approval_evidence_paths[2]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-indefinite-c-policy.md", manifest.approval_evidence_paths[3]);
    try std.testing.expectEqualStrings("owner", manifest.ownership_evidence_fields[0]);
    try std.testing.expectEqualStrings("rollback owner", manifest.ownership_evidence_fields[1]);
    try std.testing.expectEqualStrings("retained discussion state", manifest.ownership_evidence_fields[7]);
    try std.testing.expectEqualStrings("automatic return-to-blocked trigger", manifest.ownership_evidence_fields[8]);
    try std.testing.expectEqualStrings("rollback threshold", manifest.ownership_evidence_fields[9]);
    try std.testing.expectEqualStrings("indefinite-C policy link or applicability note", manifest.ownership_evidence_fields[10]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-freeze-map-governance.md", manifest.ownership_evidence_paths[0]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-parity-scorecard.md", manifest.ownership_evidence_paths[1]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-indefinite-c-policy.md", manifest.ownership_evidence_paths[2]);
    try std.testing.expectEqualStrings("freeze-map list change", manifest.trigger_conditions[0]);
    try std.testing.expectEqualStrings("freeze-map status-bucket change", manifest.trigger_conditions[1]);
    try std.testing.expectEqualStrings("linux anchor path", manifest.required_review_packet_fields[0]);
    try std.testing.expectEqualStrings("decision record ID", manifest.required_review_packet_fields[4]);
    try std.testing.expectEqualStrings("automatic return-to-blocked trigger", manifest.required_review_packet_fields[13]);
    try std.testing.expectEqualStrings("rollback threshold", manifest.required_review_packet_fields[14]);
    try std.testing.expectEqualStrings("indefinite-C policy link or applicability note", manifest.required_review_packet_fields[15]);
    try std.testing.expectEqualStrings("explicit source-of-truth note", manifest.required_review_packet_fields[16]);
    try std.testing.expectEqualStrings("trigger-specific refreshed evidence by path", manifest.required_review_packet_fields[18]);
    try std.testing.expectEqualStrings("explicit non-goals", manifest.required_review_packet_fields[20]);
    try std.testing.expectEqualStrings("written rationale", manifest.required_review_packet_fields[21]);
    try std.testing.expectEqualStrings("narrower_followup_answers_blocker", manifest.reopen_trigger_catalog[0]);
    try std.testing.expectEqualStrings("evidence_packet_stale_or_contradictory", manifest.reopen_trigger_catalog[1]);
    try std.testing.expectEqualStrings("ownership_or_validation_changed", manifest.reopen_trigger_catalog[2]);
    try std.testing.expectEqualStrings("owner", manifest.ownership_refresh_fields[0]);
    try std.testing.expectEqualStrings("rollback owner", manifest.ownership_refresh_fields[1]);
    try std.testing.expectEqualStrings("keep_in_c", manifest.decision_buckets[0]);
    try std.testing.expectEqualStrings("study_only_followup", manifest.decision_buckets[1]);
    try std.testing.expectEqualStrings("bounded_dual_implementation", manifest.decision_buckets[2]);
    try std.testing.expectEqualStrings("defer_or_reject", manifest.decision_buckets[3]);

    try std.testing.expectEqualStrings(
        "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md#phase-15-full-parity-blockers-and-long-term-governance",
        manifest.handoff_evidence.roadmap_source,
    );
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.roadmap_handoff, "freeze map") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.roadmap_handoff, "parity scorecard") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.roadmap_handoff, "indefinite-C policy") != null);
    try std.testing.expectEqualStrings(
        "docs(zigux): add documentation root, review checklist, and freeze map",
        manifest.handoff_evidence.bootstrap_ledger_anchor,
    );
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.current_repo_handoff, "Documentation/zigux/README.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.current_repo_handoff, "Documentation/zigux/review-checklist.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.current_repo_handoff, "Documentation/zigux/phase15-indefinite-c-policy.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.current_repo_handoff, "Documentation/zigux/phase15-handoff-next-steps-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.current_repo_handoff, "scripts/zigux/README.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.current_repo_handoff, "scripts/zigux/validate-phase15.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.current_repo_handoff, "zigux/tests/README.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.current_repo_handoff, "zigux/tests/phase15_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.current_repo_handoff, "make -C zigux phase15") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.current_bounded_lane, expected_lane_key) != null);
    const expected_handoff_lane_provenance = try std.fmt.allocPrint(
        std.testing.allocator,
        "as last reviewed at master head {s}",
        .{manifest.surveyed_commit},
    );
    defer std.testing.allocator.free(expected_handoff_lane_provenance);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.current_bounded_lane, expected_handoff_lane_provenance) != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.current_bounded_lane, "governance, approval, and ownership evidence verification") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.current_bounded_lane, "current parked maintenance-mode Phase 15 packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.current_bounded_lane, "scripts-root validator path") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.current_bounded_lane, "tests-root guidance path") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.current_bounded_lane, "neighboring governance slices") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.maintenance_mode_next_step, "named reopen triggers") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.maintenance_mode_next_step, "shared Phase 15 replay drift") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff_evidence.maintenance_mode_next_step, "deep-core blocker posture") != null);

    try std.testing.expectEqualStrings("maintenance_mode", manifest.handoff.current_mode);
    try std.testing.expectEqual(@as(usize, 2), manifest.handoff.replay_commands.len);
    try std.testing.expectEqualStrings("zig build test --build-file zigux/tests/phase15_build.zig", manifest.handoff.replay_commands[0]);
    try std.testing.expectEqualStrings("make -C zigux phase15", manifest.handoff.replay_commands[1]);
    try std.testing.expectEqualStrings("deep_core_blocker_posture_change", manifest.handoff.blocker_posture_requirement);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff.next_step, "named reopen triggers") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff.next_step, "shared Phase 15 replay drift") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff.next_step, "deep-core blocker posture") != null);

    for (manifest.approval_evidence_paths) |path| {
        try std.testing.expect(std.mem.startsWith(u8, path, "Documentation/zigux/"));
    }

    for (manifest.ownership_evidence_paths) |path| {
        try std.testing.expect(std.mem.startsWith(u8, path, "Documentation/zigux/"));
    }

    var landed_count: usize = 0;
    var saw_lane_identity_provenance_refresh = false;
    var saw_source_of_truth_field_gate = false;
    var saw_indefinite_c_evidence_sync = false;
    var saw_ownership_evidence_rollback_threshold_sync = false;
    var saw_freeze_map_governance_handoff_sync = false;
    var saw_scripts_tests_root_handoff_sync = false;
    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(isAllowedStatus(gap.status));
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.zigux_destination.len > 0);
        try std.testing.expect(gap.why_now.len > 0);

        if (std.mem.eql(u8, gap.status, "starter_landed")) landed_count += 1;
        if (std.mem.eql(u8, gap.id, "phase15-review-process-lane-identity-provenance-refresh")) {
            saw_lane_identity_provenance_refresh = true;
            try std.testing.expectEqualStrings("ownership_gate", gap.kind);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "active-lane identities") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "active scheduled lane") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase15-review-process-source-of-truth-field-gate")) {
            saw_source_of_truth_field_gate = true;
            try std.testing.expectEqualStrings("policy_gate", gap.kind);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "source-of-truth reminder") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "required request field") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase15-review-process-indefinite-c-evidence-path-sync")) {
            saw_indefinite_c_evidence_sync = true;
            try std.testing.expectEqualStrings("governance_sync", gap.kind);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "indefinite-C policy") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "evidence-path inventory") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase15-review-process-ownership-evidence-rollback-threshold-sync")) {
            saw_ownership_evidence_rollback_threshold_sync = true;
            try std.testing.expectEqualStrings("governance_sync", gap.kind);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rollback threshold") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ownership-evidence inventory") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase15-review-process-freeze-map-governance-handoff-sync")) {
            saw_freeze_map_governance_handoff_sync = true;
            try std.testing.expectEqualStrings("handoff_sync", gap.kind);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "freeze-map-governance companion") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "maintenance mode") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase15-review-process-scripts-tests-root-handoff-sync")) {
            saw_scripts_tests_root_handoff_sync = true;
            try std.testing.expectEqualStrings("handoff_sync", gap.kind);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "scripts-root") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tests-root") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared release-discipline route") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 22), landed_count);
    try std.testing.expect(saw_lane_identity_provenance_refresh);
    try std.testing.expect(saw_source_of_truth_field_gate);
    try std.testing.expect(saw_indefinite_c_evidence_sync);
    try std.testing.expect(saw_ownership_evidence_rollback_threshold_sync);
    try std.testing.expect(saw_freeze_map_governance_handoff_sync);
    try std.testing.expect(saw_scripts_tests_root_handoff_sync);
}

test "phase 15 architecture council review-process note stays aligned with checklist and handoff language" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_architecture_council_review_process_manifest.json",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;

    const review_process = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-architecture-council-review-process.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(review_process);

    const checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(checklist);

    const docs_root = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/README.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(docs_root);

    const expected_provenance = try std.fmt.allocPrint(
        std.testing.allocator,
        "survey provenance last refreshed against reviewed `master` head `{s}`",
        .{manifest.surveyed_commit},
    );
    defer std.testing.allocator.free(expected_provenance);

    try std.testing.expect(std.mem.indexOf(u8, review_process, expected_provenance) != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "PHASE15_LANE_KEY=P15-L08") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "## Trigger Conditions") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "## Required Review Packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "## Decision Buckets") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "## Reopen Trigger Catalog") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "## Reopen Evidence Matrix") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "## Roadmap Handoff Evidence") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "## Maintenance-Mode Handoff") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "current lane posture: `maintenance_mode`") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "make -C zigux phase15") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "retired_from_active_discussion") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "no Architecture Council approval is currently recorded") != null);
    try expectOccurrenceCount(
        review_process,
        "no Architecture Council approval is currently recorded for a freeze-map status change",
        1,
    );
    try std.testing.expect(std.mem.indexOf(u8, review_process, "the current bounded evidence is the freeze map, `Documentation/zigux/phase15-freeze-map-governance.md`, this review-process note, the review checklist hook, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, and the reserved per-anchor templates under `Documentation/zigux/phase15-evidence-archives/`") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "current approval evidence is explicit negative evidence rather than silence") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "requested decision bucket: pending_no_request") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "decision record ID: pending_no_architecture_council_request") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "no Architecture Council approval claim") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "current ownership evidence is explicit in both the scorecard and the anchor templates") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "rollback threshold") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "Documentation/zigux/phase15-evidence-archives/") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "narrower_followup_answers_blocker") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "evidence_packet_stale_or_contradictory") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "ownership_or_validation_changed") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "trigger-specific refreshed evidence by path") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "restate the current blocker disposition") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "refresh both the current lane owner and the rollback owner") != null or std.mem.indexOf(u8, review_process, "refreshes both the current lane owner and the rollback owner") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "automatic return-to-blocked trigger") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "rollback threshold naming which decision-record, scorecard-evidence, benchmark-notes, replay-command, blocker-disposition, or rollback-owner drift forces the anchor back to blocked review posture") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "blocked review posture") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "phase15-indefinite-c-policy.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "indefinite-C policy link or applicability note") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "docs(zigux): add documentation root, review checklist, and freeze map") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "existing C implementation remains the product source of truth unless the Architecture Council approves the requested status change") != null);
    const expected_lane_line = try std.fmt.allocPrint(
        std.testing.allocator,
        "current bounded lane: `{s}`",
        .{expected_lane_key},
    );
    defer std.testing.allocator.free(expected_lane_line);
    try std.testing.expect(std.mem.indexOf(u8, review_process, expected_lane_line) != null);
    const expected_lane_handoff_provenance = try std.fmt.allocPrint(
        std.testing.allocator,
        "as last reviewed at `master` head `{s}`",
        .{manifest.surveyed_commit},
    );
    defer std.testing.allocator.free(expected_lane_handoff_provenance);
    try std.testing.expect(std.mem.indexOf(u8, review_process, expected_lane_handoff_provenance) != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "Documentation/zigux/phase15-handoff-next-steps-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "shared Phase 15 replay drift") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "phase15-review-process-lane-identity-provenance-refresh") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "phase15-review-process-indefinite-c-evidence-path-sync") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "phase15-review-process-ownership-evidence-rollback-threshold-sync") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "phase15-review-process-freeze-map-governance-handoff-sync") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "phase15-review-process-scripts-tests-root-handoff-sync") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "phase15-review-process-source-of-truth-field-gate") != null);

    try std.testing.expect(std.mem.indexOf(u8, checklist, "decision record ID, lane owner, rollback owner, validation gate summary, evidence archive path, latest blocker disposition, benchmark notes, and replay command explicit") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "does the packet name the automatic return-to-blocked trigger") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "current roadmap phase") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "written rationale") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "does the packet refresh both the current lane owner and the rollback owner before active review resumes?") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "trigger-specific refreshed evidence by path") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "retained discussion state, the indefinite-C policy link or explicit non-applicability note, and the reopen triggers explicit") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "does the evidence archive cite one or more named reopen-trigger catalog items so the parked packet stays reviewable later?") != null);
    try expectOccurrenceCount(
        checklist,
        "if the change touches the freeze-map governance packet, do `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-parity-scorecard.md`, and `Documentation/zigux/review-checklist.md` still keep the automatic return-to-blocked trigger, retained discussion state, reopen triggers, and the current maintenance-mode handoff aligned while the deep-core blocker posture stays explicit?",
        1,
    );
    try expectOccurrenceCount(
        checklist,
        "if the change touches the shared Phase 15 maintenance-mode handoff packet, do `Documentation/zigux/README.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `zigux/tests/phase15_docs_root_reviewability.zig`, and `scripts/zigux/validate-phase15.py` still keep the docs-root summary alignment, the dedicated docs-root reviewability guard, the named reopen triggers, and the unchanged `phase15-deep-core-status-change-blocker` explicit under the same `make -C zigux phase15` replay path?",
        1,
    );

    try std.testing.expect(std.mem.indexOf(u8, docs_root, "Phase 15 notes") != null);
    try std.testing.expect(std.mem.indexOf(u8, docs_root, "Documentation/zigux/freeze-map.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, docs_root, "Documentation/zigux/phase15-architecture-council-review-process.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, docs_root, "Documentation/zigux/phase15-parity-scorecard.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, docs_root, "Documentation/zigux/phase15-indefinite-c-policy.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, docs_root, "Documentation/zigux/phase15-evidence-archives/") != null);
    try std.testing.expect(std.mem.indexOf(u8, docs_root, "zigux/tests/phase15_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, docs_root, "make -C zigux phase15") != null);
    try std.testing.expect(std.mem.indexOf(u8, docs_root, "maintenance mode") != null);
    try std.testing.expect(std.mem.indexOf(u8, docs_root, "named reopen triggers") != null);
    try std.testing.expect(std.mem.indexOf(u8, docs_root, "deep-core blocker posture") != null);
    try expectTemplateEvidence(
        io_instance.io(),
        "Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md",
        "Architecture Council",
        "Architecture Council + PMO / Release Management",
    );
    try expectTemplateEvidence(
        io_instance.io(),
        "Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md",
        "Architecture Council",
        "Architecture Council + Validation and Perf Team",
    );
    try expectTemplateEvidence(
        io_instance.io(),
        "Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md",
        "ABI and Runtime Team",
        "Architecture Council + ABI and Runtime Team",
    );
    try expectTemplateEvidence(
        io_instance.io(),
        "Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md",
        "Shared Subsystems Pod",
        "Architecture Council + Shared Subsystems Pod",
    );
}
