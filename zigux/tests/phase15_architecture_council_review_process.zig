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
    current_approval_state: []const u8,
    ownership_evidence_fields: []const []const u8,
    trigger_conditions: []const []const u8,
    required_review_packet_fields: []const []const u8,
    reopen_trigger_catalog: []const []const u8,
    ownership_refresh_trigger: []const u8,
    ownership_refresh_fields: []const []const u8,
    decision_buckets: []const []const u8,
    handoff: Handoff,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_stay_in_c_evidence");
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
    try std.testing.expectEqualStrings("P15-L14", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("3100cd107fa0dc45ad0b6bb740e60ffa8b94497a", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("Architecture Council review process", manifest.roadmap_requirement);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-architecture-council-review-process.md", manifest.anchor);
    try std.testing.expectEqualStrings("no_freeze_map_status_change_approved", manifest.current_approval_state);
    try std.testing.expectEqual(@as(usize, 10), manifest.ownership_evidence_fields.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.trigger_conditions.len);
    try std.testing.expectEqual(@as(usize, 17), manifest.required_review_packet_fields.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.reopen_trigger_catalog.len);
    try std.testing.expectEqualStrings("ownership_or_validation_changed", manifest.ownership_refresh_trigger);
    try std.testing.expectEqual(@as(usize, 2), manifest.ownership_refresh_fields.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.decision_buckets.len);
    try std.testing.expectEqual(@as(usize, 10), manifest.gaps.len);

    try std.testing.expectEqualStrings("owner", manifest.ownership_evidence_fields[0]);
    try std.testing.expectEqualStrings("rollback owner", manifest.ownership_evidence_fields[1]);
    try std.testing.expectEqualStrings("retained discussion state", manifest.ownership_evidence_fields[7]);
    try std.testing.expectEqualStrings("freeze-map list change", manifest.trigger_conditions[0]);
    try std.testing.expectEqualStrings("freeze-map status-bucket change", manifest.trigger_conditions[1]);
    try std.testing.expectEqualStrings("linux anchor path", manifest.required_review_packet_fields[0]);
    try std.testing.expectEqualStrings("decision record ID", manifest.required_review_packet_fields[4]);
    try std.testing.expectEqualStrings("explicit non-goals", manifest.required_review_packet_fields[15]);
    try std.testing.expectEqualStrings("written rationale", manifest.required_review_packet_fields[16]);
    try std.testing.expectEqualStrings("narrower_followup_answers_blocker", manifest.reopen_trigger_catalog[0]);
    try std.testing.expectEqualStrings("evidence_packet_stale_or_contradictory", manifest.reopen_trigger_catalog[1]);
    try std.testing.expectEqualStrings("ownership_or_validation_changed", manifest.reopen_trigger_catalog[2]);
    try std.testing.expectEqualStrings("owner", manifest.ownership_refresh_fields[0]);
    try std.testing.expectEqualStrings("rollback owner", manifest.ownership_refresh_fields[1]);
    try std.testing.expectEqualStrings("keep_in_c", manifest.decision_buckets[0]);
    try std.testing.expectEqualStrings("study_only_followup", manifest.decision_buckets[1]);
    try std.testing.expectEqualStrings("bounded_dual_implementation", manifest.decision_buckets[2]);
    try std.testing.expectEqualStrings("defer_or_reject", manifest.decision_buckets[3]);

    try std.testing.expectEqualStrings("maintenance_mode", manifest.handoff.current_mode);
    try std.testing.expectEqual(@as(usize, 2), manifest.handoff.replay_commands.len);
    try std.testing.expectEqualStrings("zig build test --build-file zigux/tests/phase15_build.zig", manifest.handoff.replay_commands[0]);
    try std.testing.expectEqualStrings("make -C zigux phase15", manifest.handoff.replay_commands[1]);
    try std.testing.expectEqualStrings("deep_core_blocker_posture_change", manifest.handoff.blocker_posture_requirement);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff.next_step, "named reopen triggers") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.handoff.next_step, "deep-core blocker posture") != null);

    var landed_count: usize = 0;
    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(isAllowedStatus(gap.status));
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.zigux_destination.len > 0);
        try std.testing.expect(gap.why_now.len > 0);

        if (std.mem.eql(u8, gap.status, "starter_landed")) landed_count += 1;

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 10), landed_count);
}

test "phase 15 architecture council review-process note stays aligned with checklist and handoff language" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

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
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(checklist);

    const docs_root = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/README.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(docs_root);

    try std.testing.expect(std.mem.indexOf(u8, review_process, "## Trigger Conditions") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "## Required Review Packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "## Decision Buckets") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "## Reopen Trigger Catalog") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "## Maintenance-Mode Handoff") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "current lane posture: `maintenance_mode`") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "make -C zigux phase15") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "retired_from_active_discussion") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "no Architecture Council approval is currently recorded") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "narrower_followup_answers_blocker") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "evidence_packet_stale_or_contradictory") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "ownership_or_validation_changed") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "refreshes both the current lane owner and the rollback owner") != null);

    try std.testing.expect(std.mem.indexOf(u8, checklist, "decision record ID, lane owner, rollback owner, validation gate summary, evidence archive path, latest blocker disposition, benchmark notes, and replay command explicit") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "does the packet refresh both the current lane owner and the rollback owner before active review resumes?") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "retained discussion state and reopen triggers explicit") != null);

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
}
