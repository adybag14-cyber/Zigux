const std = @import("std");

const AnchorScorecard = struct {
    path: []const u8,
    status: []const u8,
    line_count: usize,
    phase14_evidence_present: bool,
    council_inputs: []const []const u8,
    evidence_thresholds: []const []const u8,
    validation_gates: []const []const u8,
    rollback_owner: []const u8,
};

const RepoEvidence = struct {
    freeze_map_present: bool,
    review_checklist_present: bool,
    phase14_rcu_survey_present: bool,
    phase14_skbuff_survey_present: bool,
    phase15_scorecard_note_present: bool,
    phase15_scorecard_test_present: bool,
    phase15_scorecard_manifest_present: bool,
    phase15_build_present: bool,
    phase15_make_target_present: bool,
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
    anchors: []const AnchorScorecard,
    repo_evidence: RepoEvidence,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_stay_in_c_evidence");
}

test "phase 15 parity scorecard manifest records all freeze-map anchors and governance gates" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_parity_scorecard.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P15-L03", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("07d53ee63ae7cb8d148ca38b93e7e7a6d867603c", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 4), manifest.anchors.len);
    try std.testing.expect(manifest.repo_evidence.freeze_map_present);
    try std.testing.expect(manifest.repo_evidence.review_checklist_present);
    try std.testing.expect(manifest.repo_evidence.phase14_rcu_survey_present);
    try std.testing.expect(manifest.repo_evidence.phase14_skbuff_survey_present);
    try std.testing.expect(manifest.repo_evidence.phase15_scorecard_note_present);
    try std.testing.expect(manifest.repo_evidence.phase15_scorecard_test_present);
    try std.testing.expect(manifest.repo_evidence.phase15_scorecard_manifest_present);
    try std.testing.expect(manifest.repo_evidence.phase15_build_present);
    try std.testing.expect(manifest.repo_evidence.phase15_make_target_present);
    try std.testing.expectEqual(@as(usize, 9), manifest.gaps.len);

    var saw_sched = false;
    var saw_page_alloc = false;
    var saw_rcu = false;
    var saw_skbuff = false;

    for (manifest.anchors) |anchor| {
        try std.testing.expectEqualStrings("freeze_in_c", anchor.status);
        try std.testing.expect(anchor.line_count >= 4900);
        try std.testing.expect(anchor.council_inputs.len >= 3);
        try std.testing.expect(anchor.evidence_thresholds.len >= 3);
        try std.testing.expect(anchor.validation_gates.len >= 3);
        try std.testing.expect(anchor.rollback_owner.len > 0);

        if (std.mem.eql(u8, anchor.path, "kernel/sched/core.c")) {
            saw_sched = true;
            try std.testing.expect(anchor.line_count >= 11000);
            try std.testing.expect(!anchor.phase14_evidence_present);
            try std.testing.expect(std.mem.indexOf(u8, anchor.evidence_thresholds[1], "hotplug") != null);
        } else if (std.mem.eql(u8, anchor.path, "mm/page_alloc.c")) {
            saw_page_alloc = true;
            try std.testing.expect(anchor.line_count >= 7700);
            try std.testing.expect(!anchor.phase14_evidence_present);
            try std.testing.expect(std.mem.indexOf(u8, anchor.evidence_thresholds[1], "watermarks") != null);
        } else if (std.mem.eql(u8, anchor.path, "kernel/rcu/tree.c")) {
            saw_rcu = true;
            try std.testing.expect(anchor.phase14_evidence_present);
            try std.testing.expect(std.mem.indexOf(u8, anchor.evidence_thresholds[1], "expedited-GP") != null);
        } else if (std.mem.eql(u8, anchor.path, "net/core/skbuff.c")) {
            saw_skbuff = true;
            try std.testing.expect(anchor.phase14_evidence_present);
            try std.testing.expect(std.mem.indexOf(u8, anchor.evidence_thresholds[1], "segmentation") != null);
        }
    }

    try std.testing.expect(saw_sched);
    try std.testing.expect(saw_page_alloc);
    try std.testing.expect(saw_rcu);
    try std.testing.expect(saw_skbuff);
}

test "phase 15 parity scorecard gaps stay bounded and blocker-focused" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_parity_scorecard.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const gaps = parsed.value.gaps;
    var landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_scorecard_note = false;
    var saw_followup = false;
    var saw_blocker = false;

    for (gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_stay_in_c_evidence")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase15-parity-scorecard-note")) {
            saw_scorecard_note = true;
            try std.testing.expectEqualStrings(
                "Documentation/zigux/phase15-parity-scorecard.md",
                gap.zigux_destination,
            );
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "council inputs") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase15-stay-in-c-policy-followup")) {
            saw_followup = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "active discussion") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase15-deep-core-status-change-blocker")) {
            saw_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "freeze-in-C set") != null);
        }

        for (gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 7), landed_count);
    try std.testing.expectEqual(@as(usize, 1), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_scorecard_note);
    try std.testing.expect(saw_followup);
    try std.testing.expect(saw_blocker);
}