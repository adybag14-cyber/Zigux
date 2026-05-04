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

fn isLowerHex40(value: []const u8) bool {
    if (value.len != 40) return false;
    for (value) |byte| {
        const is_digit = byte >= '0' and byte <= '9';
        const is_lower_hex = byte >= 'a' and byte <= 'f';
        if (!is_digit and !is_lower_hex) return false;
    }
    return true;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectArchiveTemplateContents(
    template: []const u8,
    anchor_path: []const u8,
    archive_path: []const u8,
    blocker_disposition: []const u8,
) !void {
    try expectContains(template, anchor_path);
    try expectContains(template, "phase: `Phase 15`");
    try expectContains(template, "current status bucket: `freeze_in_c`");
    try expectContains(template, "requested decision bucket: `pending_no_request`");
    try expectContains(template, "decision record ID: `pending_no_architecture_council_request`");
    try expectContains(template, archive_path);
    try expectContains(template, "Documentation/zigux/phase15-parity-scorecard.md");
    try expectContains(template, "validation gate summary");
    try expectContains(template, "replay command: `zig build test --build-file zigux/tests/phase15_build.zig`");
    try expectContains(template, blocker_disposition);
    try expectContains(template, "automatic return-to-blocked trigger");
    try expectContains(template, "Documentation/zigux/phase15-indefinite-c-policy.md");
    try expectContains(template, "current discussion state: `active_review_required_until_complete_packet_exists`");
    try expectContains(template, "retained discussion state after closeout: `retired_from_active_discussion`");
    try expectContains(template, "narrower_followup_answers_blocker");
    try expectContains(template, "evidence_packet_stale_or_contradictory");
    try expectContains(template, "ownership_or_validation_changed");
    try expectContains(template, "## Explicit Non-goals");
    try expectContains(template, "written rationale");
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
    try std.testing.expectEqualStrings("P15-Y04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expect(isLowerHex40(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("policy for code that remains in C indefinitely", manifest.roadmap_requirement);
    try std.testing.expectEqual(@as(usize, 4), manifest.anchors.len);
    try std.testing.expectEqual(@as(usize, 8), manifest.supporting_artifacts.len);
    try std.testing.expectEqual(@as(usize, 10), manifest.indefinite_c_requirements.len);
    try std.testing.expectEqualStrings("maintenance_mode", manifest.handoff.current_mode);
    try std.testing.expectEqual(@as(usize, 2), manifest.handoff.replay_commands.len);
    try std.testing.expectEqualStrings("zig build test --build-file zigux/tests/phase15_build.zig", manifest.handoff.replay_commands[0]);
    try std.testing.expectEqualStrings("make -C zigux phase15", manifest.handoff.replay_commands[1]);
    try std.testing.expectEqualStrings("deep_core_blocker_posture_change", manifest.handoff.blocker_posture_requirement);
    try std.testing.expectEqualStrings("wait for one of the named reopen triggers or the deep-core blocker posture to change before opening another Phase 15 slice", manifest.handoff.next_step);
    try std.testing.expectEqual(@as(usize, 12), manifest.gaps.len);

    try std.testing.expectEqualStrings("kernel/sched/core.c", manifest.anchors[0]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-parity-scorecard.md", manifest.supporting_artifacts[3]);
    try std.testing.expectEqualStrings("Documentation/zigux/README.md", manifest.supporting_artifacts[5]);
    try std.testing.expectEqualStrings("zigux/tests/phase15_build.zig", manifest.supporting_artifacts[6]);
    try std.testing.expectEqualStrings("zigux/Makefile", manifest.supporting_artifacts[7]);

    var saw_source_of_truth = false;
    var saw_recordkeeping = false;
    var saw_allowed_work = false;
    var saw_exception_path = false;
    var saw_exception_request_checklist = false;
    var saw_automatic_return_to_blocked = false;
    var saw_reopen_gate = false;
    var saw_reopen_evidence_matrix = false;
    var saw_reopen_trigger_catalog = false;
    var saw_current_gap_requirement = false;
    var saw_maintenance_handoff = false;
    var saw_current_gap_survey = false;
    var saw_automatic_return_to_blocked_gap = false;
    var saw_reopen_trigger_catalog_gap = false;

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
            try std.testing.expectEqualStrings("retained discussion state", requirement.required_terms[12]);
            try std.testing.expectEqualStrings("automatic return-to-blocked trigger", requirement.required_terms[13]);
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
        } else if (std.mem.eql(u8, requirement.id, "indefinite-c-exception-request-checklist")) {
            saw_exception_request_checklist = true;
            try std.testing.expectEqual(@as(usize, 10), requirement.required_terms.len);
            try std.testing.expectEqualStrings("named reopen-trigger catalog item", requirement.required_terms[0]);
            try std.testing.expectEqualStrings("trigger-specific refreshed evidence by path", requirement.required_terms[1]);
            try std.testing.expectEqualStrings("current blocker disposition", requirement.required_terms[2]);
            try std.testing.expectEqualStrings("decision record ID plus the current status bucket and requested decision bucket being changed", requirement.required_terms[3]);
            try std.testing.expectEqualStrings("automatic return-to-blocked trigger", requirement.required_terms[4]);
            try std.testing.expectEqualStrings("replay command reviewers should run", requirement.required_terms[5]);
            try std.testing.expectEqualStrings("parity scorecard link", requirement.required_terms[6]);
            try std.testing.expectEqualStrings("evidence-archive path", requirement.required_terms[7]);
            try std.testing.expectEqualStrings("lane owner and rollback owner", requirement.required_terms[8]);
            try std.testing.expectEqualStrings("C implementation remains the product source of truth unless the reopen request is approved", requirement.required_terms[9]);
        } else if (std.mem.eql(u8, requirement.id, "indefinite-c-automatic-return-to-blocked")) {
            saw_automatic_return_to_blocked = true;
            try std.testing.expectEqual(@as(usize, 3), requirement.required_terms.len);
            try std.testing.expectEqualStrings("automatic return-to-blocked trigger", requirement.required_terms[0]);
            try std.testing.expectEqualStrings("missing field, stale evidence, contradictory scorecard link, replay drift, blocker drift, or rollback-threshold breach", requirement.required_terms[1]);
            try std.testing.expectEqualStrings("returns to blocked review posture", requirement.required_terms[2]);
        } else if (std.mem.eql(u8, requirement.id, "indefinite-c-reopen-gate")) {
            saw_reopen_gate = true;
            try std.testing.expectEqual(@as(usize, 5), requirement.required_terms.len);
            try std.testing.expectEqualStrings("named reopen-trigger catalog item", requirement.required_terms[0]);
            try std.testing.expectEqualStrings("narrower_followup_answers_blocker", requirement.required_terms[1]);
            try std.testing.expectEqualStrings("evidence_packet_stale_or_contradictory", requirement.required_terms[2]);
            try std.testing.expectEqualStrings("ownership_or_validation_changed", requirement.required_terms[3]);
            try std.testing.expectEqualStrings("trigger-specific evidence refresh", requirement.required_terms[4]);
        } else if (std.mem.eql(u8, requirement.id, "indefinite-c-reopen-evidence-matrix")) {
            saw_reopen_evidence_matrix = true;
            try std.testing.expectEqual(@as(usize, 3), requirement.required_terms.len);
            try std.testing.expectEqualStrings("trigger-specific refreshed evidence by path", requirement.required_terms[0]);
            try std.testing.expectEqualStrings("current blocker disposition", requirement.required_terms[1]);
            try std.testing.expectEqualStrings("if multiple triggers are cited together, each trigger's minimum evidence must stay explicit", requirement.required_terms[2]);
        } else if (std.mem.eql(u8, requirement.id, "indefinite-c-reopen-trigger-catalog")) {
            saw_reopen_trigger_catalog = true;
            try std.testing.expectEqualStrings("narrower_followup_answers_blocker", requirement.required_terms[0]);
            try std.testing.expectEqualStrings("evidence_packet_stale_or_contradictory", requirement.required_terms[1]);
            try std.testing.expectEqualStrings("ownership_or_validation_changed", requirement.required_terms[2]);
        } else if (std.mem.eql(u8, requirement.id, "indefinite-c-current-gap-survey")) {
            saw_current_gap_requirement = true;
            try std.testing.expectEqual(@as(usize, 5), requirement.required_terms.len);
            try std.testing.expectEqualStrings("current roadmap-vs-repo policy gap", requirement.required_terms[0]);
            try std.testing.expectEqualStrings("no longer a missing local governance artifact", requirement.required_terms[1]);
            try std.testing.expectEqualStrings("docs root", requirement.required_terms[2]);
            try std.testing.expectEqualStrings("shared replay path", requirement.required_terms[3]);
            try std.testing.expectEqualStrings("deep-core blocker posture", requirement.required_terms[4]);
        }
    }

    try std.testing.expect(saw_source_of_truth);
    try std.testing.expect(saw_recordkeeping);
    try std.testing.expect(saw_allowed_work);
    try std.testing.expect(saw_exception_path);
    try std.testing.expect(saw_exception_request_checklist);
    try std.testing.expect(saw_automatic_return_to_blocked);
    try std.testing.expect(saw_reopen_gate);
    try std.testing.expect(saw_reopen_evidence_matrix);
    try std.testing.expect(saw_reopen_trigger_catalog);
    try std.testing.expect(saw_current_gap_requirement);

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
        } else if (std.mem.eql(u8, gap.id, "phase15-indefinite-c-automatic-return-to-blocked-gate")) {
            saw_automatic_return_to_blocked_gap = true;
            try std.testing.expectEqualStrings("policy", gap.kind);
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-indefinite-c-policy.md", gap.zigux_destination);
        } else if (std.mem.eql(u8, gap.id, "phase15-indefinite-c-reopen-trigger-catalog")) {
            saw_reopen_trigger_catalog_gap = true;
            try std.testing.expectEqualStrings("policy", gap.kind);
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-indefinite-c-policy.md", gap.zigux_destination);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expect(saw_maintenance_handoff);
    try std.testing.expect(saw_current_gap_survey);
    try std.testing.expect(saw_automatic_return_to_blocked_gap);
    try std.testing.expect(saw_reopen_trigger_catalog_gap);
    try std.testing.expectEqual(@as(usize, 11), landed_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
}

test "phase 15 indefinite-C policy note preserves stay-in-C boundary language" {
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

    const policy_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-indefinite-c-policy.md",
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

    const review_checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(review_checklist);

    const scorecard = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-parity-scorecard.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(scorecard);

    const docs_root = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/README.md",
        std.testing.allocator,
        .limited(48 * 1024),
    );
    defer std.testing.allocator.free(docs_root);

    const phase15_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_build.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(phase15_build);

    const makefile = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/Makefile",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(makefile);

    const kernel_sched_archive = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md",
        std.testing.allocator,
        .limited(12 * 1024),
    );
    defer std.testing.allocator.free(kernel_sched_archive);

    const mm_page_alloc_archive = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md",
        std.testing.allocator,
        .limited(12 * 1024),
    );
    defer std.testing.allocator.free(mm_page_alloc_archive);

    const kernel_rcu_tree_archive = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md",
        std.testing.allocator,
        .limited(12 * 1024),
    );
    defer std.testing.allocator.free(kernel_rcu_tree_archive);

    const net_core_skbuff_archive = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md",
        std.testing.allocator,
        .limited(12 * 1024),
    );
    defer std.testing.allocator.free(net_core_skbuff_archive);

    const expected_provenance = try std.fmt.allocPrint(
        std.testing.allocator,
        "survey provenance refreshed against verified `master` head {s}",
        .{manifest.surveyed_commit},
    );
    defer std.testing.allocator.free(expected_provenance);

    try expectContains(policy_note, expected_provenance);
    try expectContains(policy_note, "PHASE15_LANE_KEY=P15-Y04");
    try expectContains(policy_note, "## When the indefinite-C policy applies");
    try expectContains(policy_note, "## Required recorded fields");
    try expectContains(policy_note, "## Allowed work after an indefinite-C outcome");
    try expectContains(policy_note, "## Exception posture");
    try expectContains(policy_note, "## Exception request checklist");
    try expectContains(policy_note, "## Automatic Return-To-Blocked Rule");
    try expectContains(policy_note, "## Reopen conditions");
    try expectContains(policy_note, "## Reopen Evidence Matrix");
    try expectContains(policy_note, "## Reopen Trigger Catalog");
    try expectContains(policy_note, "## Current Policy Gap");
    try expectContains(policy_note, "## Maintenance-Mode Handoff");
    try expectContains(policy_note, "landed `phase15-indefinite-c-maintenance-handoff`");
    try expectContains(policy_note, "landed `phase15-indefinite-c-automatic-return-to-blocked-gate`");
    try expectContains(policy_note, "landed `phase15-indefinite-c-reopen-trigger-catalog`");
    try expectContains(policy_note, "Documentation/zigux/phase15-evidence-archives/");
    try expectContains(policy_note, "retired_from_active_discussion");
    try expectContains(policy_note, "no silent exception path");
    try expectContains(policy_note, "Architecture Council reopen request");
    try expectContains(policy_note, "existing blocker remains recorded");
    try expectContains(policy_note, "Every allowed exception request must stay reviewable as a bounded reopen packet instead of a policy waiver.");
    try expectContains(policy_note, "the exact named reopen-trigger catalog item or items being cited");
    try expectContains(policy_note, "the trigger-specific refreshed evidence by path for each cited trigger");
    try expectContains(policy_note, "the current blocker disposition the new evidence is trying to change");
    try expectContains(policy_note, "the decision record ID plus the current status bucket and requested decision bucket that the reopen request is attempting to change");
    try expectContains(policy_note, "the automatic return-to-blocked trigger that sends the anchor back to blocked review posture if review fields, linked evidence, scorecard state, replay commands, blocker posture, or rollback ownership drift");
    try expectContains(policy_note, "the parity scorecard link and the evidence-archive path tied to the same anchor");
    try expectContains(policy_note, "the lane owner and rollback owner, refreshed when the trigger is `ownership_or_validation_changed`");
    try expectContains(policy_note, "the C implementation remains the product source of truth unless the reopen request is approved");
    try expectContains(policy_note, "If any one of those fields is missing, the exception request is incomplete and the anchor remains in the recorded stay-in-C posture.");
    try expectContains(policy_note, "Every active exception or reopened stay-in-C review packet must keep one automatic return-to-blocked trigger explicit.");
    try expectContains(policy_note, "That trigger must name which missing field, stale evidence, contradictory scorecard link, replay drift, blocker drift, or rollback-threshold breach sends the anchor back to blocked review posture.");
    try expectContains(policy_note, "If the trigger is missing or any named drift is left unresolved, the exception packet is incomplete and the anchor returns to blocked review posture with the existing C implementation still the product source of truth.");
    try expectContains(policy_note, "named reopen-trigger catalog item");
    try expectContains(policy_note, "new bounded seam inventory");
    try expectContains(policy_note, "trigger-specific evidence");
    try expectContains(policy_note, "trigger-specific refreshed evidence by path");
    try expectContains(policy_note, "current blocker disposition");
    try expectContains(policy_note, "If multiple triggers are cited together");
    try expectContains(policy_note, "updated validation plan and rollback owner");
    try expectContains(policy_note, "refreshed linked evidence in the evidence archive");
    try expectContains(policy_note, "refreshed lane-owner, rollback-owner, or validation-gate evidence");
    try expectContains(policy_note, "current benchmark-notes status");
    try expectContains(policy_note, "current roadmap phase");
    try expectContains(policy_note, "replay command reviewers should use");
    try expectContains(policy_note, "automatic return-to-blocked trigger");
    try expectContains(policy_note, "reopen triggers and the parity scorecard link or blocker record");
    try expectContains(policy_note, "ownership_or_validation_changed");
    try expectContains(policy_note, "current lane posture: `maintenance_mode`");
    try expectContains(policy_note, "make -C zigux phase15");
    try expectContains(policy_note, "The current roadmap-vs-repo policy gap inside this lane is no longer a missing local governance artifact.");
    try expectContains(policy_note, "That keeps the current roadmap-vs-repo policy gap explicit at the docs root and the shared replay path instead of leaving the closure signal buried only in this note.");
    try expectContains(policy_note, "That closes the current policy gap for the roadmap requirement `policy for code that remains in C indefinitely`.");
    try expectContains(policy_note, "Documentation/zigux/README.md");
    try expectContains(policy_note, "zigux/Makefile");
    try expectContains(policy_note, "`kernel/sched/core.c`: `blocked_no_bounded_scheduler_seam`; no bounded scheduler seam is approved yet");
    try expectContains(policy_note, "`mm/page_alloc.c`: `blocked_no_bounded_allocator_seam`; no bounded allocator seam is approved yet");
    try expectContains(policy_note, "`kernel/rcu/tree.c`: `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`; the current RCU follow-up is still wider than the allowed seam");
    try expectContains(policy_note, "`net/core/skbuff.c`: `blocked_packet_lifetime_boundary_still_too_wide`; the current skbuff follow-up is still wider than the allowed packet-lifetime boundary");
    try expectContains(policy_note, "Those exact blocker dispositions match the current evidence-archive templates so the stay-in-C packet does not drift into looser prose than the blocker records reviewers must rely on later.");
    try expectContains(policy_note, "next future target: wait for one of the named reopen triggers or the deep-core blocker posture to change before opening another Phase 15 slice");

    try expectContains(docs_root, "Phase 15 notes");
    try expectContains(docs_root, "`Documentation/zigux/phase15-indefinite-c-policy.md`");
    try expectContains(docs_root, "the current roadmap-versus-repo indefinite-C policy gap is closed locally");
    try expectContains(docs_root, "`zig build test --build-file zigux/tests/phase15_build.zig` plus `make -C zigux phase15` replay path");
    try expectContains(docs_root, "`Documentation/zigux/phase15-evidence-archives/`");

    try expectContains(phase15_build, "phase15_indefinite_c_policy.zig");
    try expectContains(phase15_build, "phase15-indefinite-c-policy-tests");

    try expectContains(makefile, "phase15-test:");
    try expectContains(makefile, "build test --build-file zigux/tests/phase15_build.zig");
    try expectContains(makefile, "phase15: phase15-validate phase15-test");

    try expectContains(freeze_map, "product source of truth");
    try expectContains(freeze_map, "no silent exception path");
    try expectContains(review_process, "requested decision bucket");
    try expectContains(review_process, "decision record ID");
    try expectContains(review_process, "retained discussion state");
    try expectContains(review_process, "the explicit `Documentation/zigux/phase15-indefinite-c-policy.md` link");
    try expectContains(review_process, "the explicit note that the existing C implementation remains the product source of truth unless the Architecture Council approves the requested status change");
    try expectContains(review_process, "the trigger-specific refreshed evidence by path for every named reopen trigger");
    try expectContains(review_process, "refreshed lane-owner and rollback-owner evidence whenever the reopen trigger is `ownership_or_validation_changed`");
    try expectContains(review_checklist, "trigger-specific refreshed evidence by path");
    try expectContains(review_checklist, "current blocker disposition");
    try expectContains(scorecard, "retired_from_active_discussion");
    try expectContains(scorecard, "narrower_followup_answers_blocker");
    try expectContains(freeze_map, "fresh linked evidence");

    try expectArchiveTemplateContents(
        kernel_sched_archive,
        "kernel/sched/core.c",
        "Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md",
        "blocked_no_bounded_scheduler_seam",
    );
    try expectArchiveTemplateContents(
        mm_page_alloc_archive,
        "mm/page_alloc.c",
        "Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md",
        "blocked_no_bounded_allocator_seam",
    );
    try expectArchiveTemplateContents(
        kernel_rcu_tree_archive,
        "kernel/rcu/tree.c",
        "Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md",
        "blocked_phase14_followup_still_wider_than_allowed_rcu_seam",
    );
    try expectArchiveTemplateContents(
        net_core_skbuff_archive,
        "net/core/skbuff.c",
        "Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md",
        "blocked_packet_lifetime_boundary_still_too_wide",
    );
}
