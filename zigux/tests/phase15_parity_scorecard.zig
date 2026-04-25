const std = @import("std");

const EvidenceArchive = struct {
    decision_record_path: []const u8,
    linked_evidence: []const []const u8,
    benchmark_notes_status: []const u8,
    replay_command: []const u8,
    latest_blocker_disposition: []const u8,
};

const AnchorScorecard = struct {
    path: []const u8,
    status: []const u8,
    line_count: usize,
    phase14_evidence_present: bool,
    council_inputs: []const []const u8,
    evidence_thresholds: []const []const u8,
    validation_gates: []const []const u8,
    rollback_owner: []const u8,
    evidence_archive: EvidenceArchive,
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

const ReviewProcess = struct {
    decision_record_required: bool,
    required_record_fields: []const []const u8,
    retirement_rule: []const u8,
    archive_requirements: []const []const u8,
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
    anchors: []const AnchorScorecard,
    repo_evidence: RepoEvidence,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_stay_in_c_evidence");
}

test "phase 15 parity scorecard manifest records all freeze-map anchors and evidence-archive reporting" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_parity_scorecard.json",
        std.testing.allocator,
        .limited(40 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P15-L10", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("36f313d5bd0b3be22beb3284730a98dff5e7f335", manifest.surveyed_commit);
    try std.testing.expect(manifest.review_process.decision_record_required);
    try std.testing.expectEqual(@as(usize, 6), manifest.review_process.required_record_fields.len);
    try std.testing.expect(std.mem.indexOf(u8, manifest.review_process.retirement_rule, "active discussion") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.review_process.retirement_rule, "evidence archive path") != null);
    try std.testing.expectEqual(@as(usize, 3), manifest.review_process.archive_requirements.len);
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
    try std.testing.expectEqual(@as(usize, 11), manifest.gaps.len);

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
        try std.testing.expect(std.mem.startsWith(u8, anchor.evidence_archive.decision_record_path, "Documentation/zigux/phase15-evidence-archives/"));
        try std.testing.expect(anchor.evidence_archive.linked_evidence.len >= 2);
        try std.testing.expect(std.mem.indexOf(u8, anchor.evidence_archive.benchmark_notes_status, "pending") != null);
        try std.testing.expectEqualStrings("zig build test --build-file zigux/tests/phase15_build.zig", anchor.evidence_archive.replay_command);
        try std.testing.expect(std.mem.indexOf(u8, anchor.evidence_archive.latest_blocker_disposition, "blocked") != null);

        if (std.mem.eql(u8, anchor.path, "kernel/sched/core.c")) {
            saw_sched = true;
            try std.testing.expect(anchor.line_count >= 11000);
            try std.testing.expect(!anchor.phase14_evidence_present);
            try std.testing.expect(std.mem.indexOf(u8, anchor.evidence_thresholds[1], "hotplug") != null);
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md", anchor.evidence_archive.decision_record_path);
        } else if (std.mem.eql(u8, anchor.path, "mm/page_alloc.c")) {
            saw_page_alloc = true;
            try std.testing.expect(anchor.line_count >= 7700);
            try std.testing.expect(!anchor.phase14_evidence_present);
            try std.testing.expect(std.mem.indexOf(u8, anchor.evidence_thresholds[1], "watermarks") != null);
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md", anchor.evidence_archive.decision_record_path);
        } else if (std.mem.eql(u8, anchor.path, "kernel/rcu/tree.c")) {
            saw_rcu = true;
            try std.testing.expect(anchor.phase14_evidence_present);
            try std.testing.expect(std.mem.indexOf(u8, anchor.evidence_thresholds[1], "expedited-GP") != null);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-rcu-tree-survey.md", anchor.evidence_archive.linked_evidence[0]);
        } else if (std.mem.eql(u8, anchor.path, "net/core/skbuff.c")) {
            saw_skbuff = true;
            try std.testing.expect(anchor.phase14_evidence_present);
            try std.testing.expect(std.mem.indexOf(u8, anchor.evidence_thresholds[1], "segmentation") != null);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-skbuff-bridge-survey.md", anchor.evidence_archive.linked_evidence[0]);
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
        .limited(40 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const gaps = parsed.value.gaps;
    var landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_scorecard_note = false;
    var saw_council_review_gate = false;
    var saw_archive_reporting = false;
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
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-parity-scorecard.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "evidence-archive reporting block") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase15-council-review-gate")) {
            saw_council_review_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "decision record") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "evidence archive path") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase15-evidence-archive-reporting")) {
            saw_archive_reporting = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "benchmark-notes status") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "replay command") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase15-decision-record-template-followup")) {
            saw_followup = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "template packet headings") != null);
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

    try std.testing.expectEqual(@as(usize, 9), landed_count);
    try std.testing.expectEqual(@as(usize, 1), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_scorecard_note);
    try std.testing.expect(saw_council_review_gate);
    try std.testing.expect(saw_archive_reporting);
    try std.testing.expect(saw_followup);
    try std.testing.expect(saw_blocker);
}

test "phase 15 council review gate stays aligned between the scorecard and checklist" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_parity_scorecard.json",
        std.testing.allocator,
        .limited(40 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const scorecard_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-parity-scorecard.md",
        std.testing.allocator,
        .limited(28 * 1024),
    );
    defer std.testing.allocator.free(scorecard_doc);

    const review_checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(review_checklist);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    try std.testing.expect(std.mem.indexOf(u8, scorecard_doc, "## Architecture Council Review Gate") != null);
    try std.testing.expect(std.mem.indexOf(u8, scorecard_doc, "## Evidence Archive Reporting Standard") != null);
    try std.testing.expect(std.mem.indexOf(u8, scorecard_doc, "decision record ID") != null);
    try std.testing.expect(std.mem.indexOf(u8, scorecard_doc, "lane owner") != null);
    try std.testing.expect(std.mem.indexOf(u8, scorecard_doc, "evidence archive path") != null);
    try std.testing.expect(std.mem.indexOf(u8, scorecard_doc, "latest blocker disposition") != null);
    try std.testing.expect(std.mem.indexOf(u8, scorecard_doc, "benchmark notes") != null);
    try std.testing.expect(std.mem.indexOf(u8, scorecard_doc, "replay command") != null);
    try std.testing.expect(std.mem.indexOf(u8, scorecard_doc, "leaves active discussion only after") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "decision record ID, lane owner, evidence archive path, latest blocker disposition, benchmark notes, and replay command explicit") != null);

    for (parsed.value.review_process.required_record_fields) |field| {
        const field_expected_in_checklist =
            !std.mem.eql(u8, field, "validation gate set") and
            !std.mem.eql(u8, field, "rollback owner");

        try std.testing.expect(std.mem.indexOf(u8, scorecard_doc, field) != null);
        if (field_expected_in_checklist) {
            try std.testing.expect(std.mem.indexOf(u8, review_checklist, field) != null);
        }
    }

    for (parsed.value.review_process.archive_requirements) |item| {
        try std.testing.expect(std.mem.indexOf(u8, scorecard_doc, item) != null);
        try std.testing.expect(std.mem.indexOf(u8, review_checklist, item) != null or !std.mem.eql(u8, item, "benchmark notes"));
    }
}
