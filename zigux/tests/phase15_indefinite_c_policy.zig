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

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_stay_in_c_evidence");
}

test "phase 15 indefinite-C policy manifest records current policy, exception, and blocker evidence" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_indefinite_c_policy.json",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P15-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("65cb45dda5ca7fc760207a4ca711397bc7894e9e", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("policy for code that remains in C indefinitely", manifest.roadmap_requirement);
    try std.testing.expectEqual(@as(usize, 4), manifest.anchors.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.supporting_artifacts.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.indefinite_c_requirements.len);
    try std.testing.expectEqualStrings("maintenance_mode", manifest.handoff.current_mode);
    try std.testing.expectEqual(@as(usize, 2), manifest.handoff.replay_commands.len);
    try std.testing.expectEqualStrings("zig build test --build-file zigux/tests/phase15_build.zig", manifest.handoff.replay_commands[0]);
    try std.testing.expectEqualStrings("make -C zigux phase15", manifest.handoff.replay_commands[1]);
    try std.testing.expectEqualStrings("deep_core_blocker_posture_change", manifest.handoff.blocker_posture_requirement);
    try std.testing.expectEqualStrings("wait for one of the named reopen triggers or the deep-core blocker posture to change before opening another Phase 15 slice", manifest.handoff.next_step);
    try std.testing.expectEqual(@as(usize, 8), manifest.gaps.len);

    try std.testing.expectEqualStrings("kernel/sched/core.c", manifest.anchors[0]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-parity-scorecard.md", manifest.supporting_artifacts[3]);

    var saw_source_of_truth = false;
    var saw_recordkeeping = false;
    var saw_allowed_work = false;
    var saw_exception_path = false;
    var saw_reopen_gate = false;
    var saw_reopen_trigger_catalog = false;
    var saw_maintenance_handoff = false;
    var saw_current_gap_survey = false;

    for (manifest.indefinite_c_requirements) |requirement| {
        try std.testing.expect(requirement.id.len > 0);
        try std.testing.expect(requirement.summary.len > 0);
        try std.testing.expect(requirement.required_terms.len >= 2);

        if (std.mem.eql(u8, requirement.id, "indefinite-c-source-of-truth")) {
            saw_source_of_truth = true;
            try std.testing.expectEqualStrings("product source of truth", requirement.required_terms[0]);
            try std.testing.expectEqualStrings("remains in C indefinitely", requirement.required_terms[1]);
        } else if (std.mem.eql(u8, requirement.id, "indefinite-c-recordkeeping")) {
            saw_recordkeeping = true;
            try std.testing.expectEqual(@as(usize, 18), requirement.required_terms.len);
            try std.testing.expectEqualStrings("Linux anchor path", requirement.required_terms[0]);
            try std.testing.expectEqualStrings("current roadmap phase", requirement.required_terms[1]);
            try std.testing.expectEqualStrings("current status bucket", requirement.required_terms[2]);
            try std.testing.expectEqualStrings("requested decision bucket", requirement.required_terms[3]);
            try std.testing.expectEqualStrings("decision record ID", requirement.required_terms[4]);
            try std.testing.expectEqualStrings("owner", requirement.required_terms[5]);
            try std.testing.expectEqualStrings("rollback owner", requirement.required_terms[6]);
            try std.testing.expectEqualStrings("validation gate summary", requirement.required_terms[7]);
            try std.testing.expectEqualStrings("benchmark notes", requirement.required_terms[8]);
            try std.testing.expectEqualStrings("evidence archive path", requirement.required_terms[9]);
            try std.testing.expectEqualStrings("replay command", requirement.required_terms[10]);
            try std.testing.expectEqualStrings("latest blocker disposition", requirement.required_terms[11]);
            try std.testing.expectEqualStrings("automatic return-to-blocked trigger", requirement.required_terms[12]);
            try std.testing.expectEqualStrings("retained discussion state", requirement.required_terms[13]);
            try std.testing.expectEqualStrings("reopen triggers", requirement.required_terms[14]);
            try std.testing.expectEqualStrings("parity scorecard link or blocker record", requirement.required_terms[15]);
            try std.testing.expectEqualStrings("explicit non-goals", requirement.required_terms[16]);
            try std.testing.expectEqualStrings("written rationale", requirement.required_terms[17]);
        } else if (std.mem.eql(u8, requirement.id, "indefinite-c-allowed-work")) {
            saw_allowed_work = true;
            try std.testing.expectEqualStrings("survey notes, boundary manifests, validation gates, and explicit non-goal records", requirement.required_terms[0]);
            try std.testing.expectEqualStrings("explicit stay-in-C outcome", requirement.required_terms[1]);
        } else if (std.mem.eql(u8, requirement.id, "indefinite-c-exception-path")) {
            saw_exception_path = true;
            try std.testing.expectEqualStrings("no silent exception path", requirement.required_terms[0]);
            try std.testing.expectEqualStrings("Architecture Council reopen request", requirement.required_terms[1]);
            try std.testing.expectEqualStrings("existing blocker remains recorded", requirement.required_terms[2]);
        } else if (std.mem.eql(u8, requirement.id, "indefinite-c-reopen-gate")) {
            saw_reopen_gate = true;
            try std.testing.expectEqual(@as(usize, 5), requirement.required_terms.len);
            try std.testing.expectEqualStrings("named reopen-trigger catalog item", requirement.required_terms[0]);
            try std.testing.expectEqualStrings("narrower_followup_answers_blocker", requirement.required_terms[1]);
            try std.testing.expectEqualStrings("evidence_packet_stale_or_contradictory", requirement.required_terms[2]);
            try std.testing.expectEqualStrings("ownership_or_validation_changed", requirement.required_terms[3]);
            try std.testing.expectEqualStrings("trigger-specific evidence refresh", requirement.required_terms[4]);
        } else if (std.mem.eql(u8, requirement.id, "indefinite-c-reopen-trigger-catalog")) {
            saw_reopen_trigger_catalog = true;
            try std.testing.expectEqualStrings("narrower_followup_answers_blocker", requirement.required_terms[0]);
            try std.testing.expectEqualStrings("evidence_packet_stale_or_contradictory", requirement.required_terms[1]);
            try std.testing.expectEqualStrings("ownership_or_validation_changed", requirement.required_terms[2]);
        }
    }

    try std.testing.expect(saw_source_of_truth);
    try std.testing.expect(saw_recordkeeping);
    try std.testing.expect(saw_allowed_work);
    try std.testing.expect(saw_exception_path);
    try std.testing.expect(saw_reopen_gate);
    try std.testing.expect(saw_reopen_trigger_catalog);

    var landed_count: usize = 0;
    var blocked_count: usize = 0;
    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(isAllowedStatus(gap.status));
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.zigux_destination.len > 0);
        try std.testing.expect(gap.why_now.len > 0);

        if (std.mem.eql(u8, gap.status, "starter_landed")) landed_count += 1;
        if (std.mem.eql(u8, gap.status, "blocked_on_stay_in_c_evidence")) blocked_count += 1;

        if (std.mem.eql(u8, gap.id, "phase15-indefinite-c-maintenance-handoff")) {
            saw_maintenance_handoff = true;
            try std.testing.expectEqualStrings("handoff", gap.kind);
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-indefinite-c-policy.md", gap.zigux_destination);
        } else if (std.mem.eql(u8, gap.id, "phase15-indefinite-c-current-gap-survey")) {
            saw_current_gap_survey = true;
            try std.testing.expectEqualStrings("survey", gap.kind);
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-indefinite-c-policy.md", gap.zigux_destination);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expect(saw_maintenance_handoff);
    try std.testing.expect(saw_current_gap_survey);
    try std.testing.expectEqual(@as(usize, 7), landed_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
}

test "phase 15 indefinite-C policy note preserves stay-in-C boundary language" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const policy_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-indefinite_c_policy.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(policy_note);

    const freeze_map = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/freeze-map.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(freeze_map);

    const review_process = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-architecture-council-review-process.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(review_process);

    const scorecard = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-parity-scorecard.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(scorecard);

    try std.testing.expect(std.mem.indexOf(u8, policy_note, "## When the indefinite-C policy applies") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "## Required recorded fields") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "## Allowed work after an indefinite-C outcome") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "## Exception posture") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "## Reopen conditions") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "## Reopen Trigger Catalog") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "## Current Policy Gap") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "## Maintenance-Mode Handoff") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "retired_from_active_discussion") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "no silent exception path") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "Architecture Council reopen request") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "existing blocker remains recorded") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "named reopen-trigger catalog item") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "new bounded seam inventory") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "trigger-specific evidence") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "updated validation plan and rollback owner") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "refreshed linked evidence in the evidence archive") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "refreshed lane-owner, rollback-owner, or validation-gate evidence") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "current benchmark-notes status") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "current roadmap phase") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "replay command reviewers should use") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "automatic return-to-blocked trigger") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "back to blocked review posture") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "reopen triggers and the parity scorecard link or blocker record") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "ownership_or_validation_changed") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "current lane posture: `maintenance_mode`") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "make -C zigux phase15") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "The current roadmap-vs-repo policy gap inside this lane is no longer a missing local governance artifact.") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "That closes the current policy gap for the roadmap requirement `policy for code that remains in C indefinitely`.") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "no bounded scheduler seam is approved yet") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "next future target: wait for one of the named reopen triggers or the deep-core blocker posture to change before opening another Phase 15 slice") != null);

    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "product source of truth") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "no silent exception path") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "retained discussion state") != null);
    try std.testing.expect(std.mem.indexOf(u8, scorecard, "retired_from_active_discussion") != null);
    try std.testing.expect(std.mem.indexOf(u8, scorecard, "narrower_followup_answers_blocker") != null);
}
