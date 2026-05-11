const std = @import("std");

const Requirement = struct {
    id: []const u8,
    summary: []const u8,
    required_terms: []const []const u8,
};

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
    anchors: []const []const u8,
    supporting_artifacts: []const []const u8,
    indefinite_c_requirements: []const Requirement,
    handoff: Handoff,
    gaps: []const Gap,
};

fn readText(io: std.Io, path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_stay_in_c_evidence");
}

test "phase 15 indefinite-C policy manifest records the restored stay-in-C packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try readText(io_instance.io(), "zigux/tests/phase15_indefinite_c_policy.json", 24 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P15-L02", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("current-master-readback-2026-05-11", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("policy for code that remains in C indefinitely", manifest.roadmap_requirement);
    try std.testing.expectEqual(@as(usize, 4), manifest.anchors.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.supporting_artifacts.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.indefinite_c_requirements.len);
    try std.testing.expectEqualStrings("maintenance_mode", manifest.handoff.current_mode);
    try std.testing.expectEqual(@as(usize, 3), manifest.handoff.replay_commands.len);
    try std.testing.expectEqualStrings("make -C zigux phase15-validate", manifest.handoff.replay_commands[0]);
    try std.testing.expectEqualStrings("make -C zigux phase15-test", manifest.handoff.replay_commands[1]);
    try std.testing.expectEqualStrings("make -C zigux phase15", manifest.handoff.replay_commands[2]);
    try std.testing.expectEqualStrings("deep_core_blocker_posture_change", manifest.handoff.blocker_posture_requirement);
    try std.testing.expectEqualStrings("wait for one of the named reopen triggers or the deep-core blocker posture to change before opening another Phase 15 slice", manifest.handoff.next_step);
    try std.testing.expectEqual(@as(usize, 6), manifest.gaps.len);

    var saw_source_of_truth = false;
    var saw_recordkeeping = false;
    var saw_allowed_work = false;
    var saw_exception_path = false;
    var saw_reopen_gate = false;
    var saw_reopen_trigger_catalog = false;
    var landed_count: usize = 0;
    var blocked_count: usize = 0;

    for (manifest.indefinite_c_requirements) |requirement| {
        try std.testing.expect(requirement.id.len > 0);
        try std.testing.expect(requirement.summary.len > 0);
        try std.testing.expect(requirement.required_terms.len >= 2);

        if (std.mem.eql(u8, requirement.id, "indefinite-c-source-of-truth")) saw_source_of_truth = true;
        if (std.mem.eql(u8, requirement.id, "indefinite-c-recordkeeping")) {
            saw_recordkeeping = true;

            var saw_named_owner = false;
            var saw_required_approver_set = false;
            var saw_rollback_owner = false;
            for (requirement.required_terms) |term| {
                if (std.mem.eql(u8, term, "named owner")) saw_named_owner = true;
                if (std.mem.eql(u8, term, "required approver set")) saw_required_approver_set = true;
                if (std.mem.eql(u8, term, "rollback owner")) saw_rollback_owner = true;
            }
            try std.testing.expect(saw_named_owner);
            try std.testing.expect(saw_required_approver_set);
            try std.testing.expect(saw_rollback_owner);
        }
        if (std.mem.eql(u8, requirement.id, "indefinite-c-allowed-work")) saw_allowed_work = true;
        if (std.mem.eql(u8, requirement.id, "indefinite-c-exception-path")) saw_exception_path = true;
        if (std.mem.eql(u8, requirement.id, "indefinite-c-reopen-gate")) saw_reopen_gate = true;
        if (std.mem.eql(u8, requirement.id, "indefinite-c-reopen-trigger-catalog")) saw_reopen_trigger_catalog = true;
    }

    try std.testing.expect(saw_source_of_truth);
    try std.testing.expect(saw_recordkeeping);
    try std.testing.expect(saw_allowed_work);
    try std.testing.expect(saw_exception_path);
    try std.testing.expect(saw_reopen_gate);
    try std.testing.expect(saw_reopen_trigger_catalog);

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(isAllowedStatus(gap.status));
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.zigux_destination.len > 0);
        try std.testing.expect(gap.why_now.len > 0);

        if (std.mem.eql(u8, gap.status, "starter_landed")) landed_count += 1;
        if (std.mem.eql(u8, gap.status, "blocked_on_stay_in_c_evidence")) blocked_count += 1;

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 5), landed_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
}

test "phase 15 indefinite-C policy note preserves the restored stay-in-C record" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const policy_note = try readText(io_instance.io(), "Documentation/zigux/phase15-indefinite-c-policy.md", 24 * 1024);
    defer std.testing.allocator.free(policy_note);

    const freeze_map = try readText(io_instance.io(), "Documentation/zigux/freeze-map.md", 8 * 1024);
    defer std.testing.allocator.free(freeze_map);

    const review_process = try readText(io_instance.io(), "Documentation/zigux/phase15-architecture-council-review-process.md", 12 * 1024);
    defer std.testing.allocator.free(review_process);

    const review_checklist = try readText(io_instance.io(), "Documentation/zigux/review-checklist.md", 8 * 1024);
    defer std.testing.allocator.free(review_checklist);

    try expectContains(policy_note, "PHASE15_STATUS=indefinite_c_policy_packet_restored");
    try expectContains(policy_note, "PHASE15_LANE_KEY=P15-L02");
    try expectContains(policy_note, "PHASE15_PROVENANCE_MODE=dated_master_readback");
    try expectContains(policy_note, "current-master-readback-2026-05-11");
    try expectContains(policy_note, "## Current Policy Gap");
    try expectContains(policy_note, "missing local governance artifact");
    try expectContains(policy_note, "shared Phase 15 summaries, validator wiring, and governance-lane sequencing");
    try expectContains(policy_note, "## When the indefinite-C policy applies");
    try expectContains(policy_note, "## Required Recorded Fields");
    try expectContains(policy_note, "required approver set");
    try expectContains(policy_note, "automatic return-to-blocked trigger");
    try expectContains(policy_note, "retired_from_active_discussion");
    try expectContains(policy_note, "## Allowed Work After an Indefinite-C Outcome");
    try expectContains(policy_note, "survey notes, boundary manifests, validation gates, and explicit non-goal records");
    try expectContains(policy_note, "## Exception Posture");
    try expectContains(policy_note, "no silent exception path");
    try expectContains(policy_note, "Architecture Council reopen request");
    try expectContains(policy_note, "existing blocker remains recorded");
    try expectContains(policy_note, "## Reopen Conditions");
    try expectContains(policy_note, "named reopen-trigger catalog item");
    try expectContains(policy_note, "trigger-specific evidence refresh");
    try expectContains(policy_note, "new bounded seam inventory");
    try expectContains(policy_note, "updated validation plan and rollback owner");
    try expectContains(policy_note, "## Reopen Trigger Catalog");
    try expectContains(policy_note, "narrower_followup_answers_blocker");
    try expectContains(policy_note, "evidence_packet_stale_or_contradictory");
    try expectContains(policy_note, "ownership_or_validation_changed");
    try expectContains(policy_note, "## Maintenance-Mode Handoff");
    try expectContains(policy_note, "current lane posture: `maintenance_mode`");
    try expectContains(policy_note, "make -C zigux phase15-validate");
    try expectContains(policy_note, "make -C zigux phase15-test");
    try expectContains(policy_note, "make -C zigux phase15");
    try expectContains(policy_note, "This slice closes that local governance gap");
    try expectContains(policy_note, "The remaining blocked work is not another missing policy artifact.");

    try expectContains(freeze_map, "product source of truth");
    try expectContains(freeze_map, "no silent exception path");
    try expectContains(review_process, "required approver set");
    try expectContains(review_process, "retained discussion state");
    try expectContains(review_process, "reopen triggers");
    try expectContains(review_process, "indefinite-C policy link");
    try expectContains(review_checklist, "current status bucket plus requested decision bucket explicit");
    try expectContains(review_checklist, "required approver set");
    try expectContains(review_checklist, "retained discussion state");
    try expectContains(review_checklist, "reopen triggers explicit");
}