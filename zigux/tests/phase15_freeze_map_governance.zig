const std = @import("std");

const GovernanceRequirement = struct {
    id: []const u8,
    summary: []const u8,
    required_terms: []const []const u8,
};

const BlockerOwnership = struct {
    anchor: []const u8,
    owner: []const u8,
    phase: []const u8,
    status_bucket: []const u8,
    validation_gate: []const u8,
    rollback_owner: []const u8,
    evidence_archive_path: []const u8,
    benchmark_notes: []const u8,
    replay_command: []const u8,
    latest_blocker_disposition: []const u8,
};

const DeepCoreBlockerSurvey = struct {
    anchor: []const u8,
    roadmap_basis: []const u8,
    repo_reality: []const u8,
    current_blocker: []const u8,
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
    anchor: []const u8,
    freeze_in_c_targets: []const []const u8,
    study_only_targets: []const []const u8,
    governance_requirements: []const GovernanceRequirement,
    blocker_ownership: []const BlockerOwnership,
    deep_core_blocker_survey: []const DeepCoreBlockerSurvey,
    gaps: []const Gap,
};

const ScorecardEvidenceArchive = struct {
    decision_record_path: []const u8,
    linked_evidence: []const []const u8,
    benchmark_notes_status: []const u8,
    replay_command: []const u8,
    latest_blocker_disposition: []const u8,
};

const ScorecardAnchor = struct {
    path: []const u8,
    lane_owner: []const u8,
    rollback_owner: []const u8,
    evidence_archive: ScorecardEvidenceArchive,
};

const ScorecardManifest = struct {
    anchors: []const ScorecardAnchor,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_stay_in_c_evidence");
}

test "phase 15 freeze-map governance manifest records the bounded governance slice" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_freeze_map_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P15-L01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("4fc891b380cdd2991dff7676ade7f844df1b55fd", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 4), manifest.freeze_in_c_targets.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.study_only_targets.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.governance_requirements.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.blocker_ownership.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.deep_core_blocker_survey.len);
    try std.testing.expectEqual(@as(usize, 12), manifest.gaps.len);

    for (manifest.deep_core_blocker_survey, 0..) |survey, i| {
        try std.testing.expectEqualStrings(manifest.freeze_in_c_targets[i], survey.anchor);
        try std.testing.expect(survey.roadmap_basis.len > 0);
        try std.testing.expect(survey.repo_reality.len > 0);
        try std.testing.expect(survey.current_blocker.len > 0);

        if (std.mem.eql(u8, survey.anchor, "kernel/sched/core.c")) {
            try std.testing.expect(std.mem.indexOf(u8, survey.roadmap_basis, "freeze-in-C anchor") != null);
            try std.testing.expect(std.mem.indexOf(u8, survey.repo_reality, "no carried-forward Phase 14 blocker survey") != null);
            try std.testing.expectEqualStrings("blocked_no_bounded_scheduler_seam", survey.current_blocker);
        } else if (std.mem.eql(u8, survey.anchor, "mm/page_alloc.c")) {
            try std.testing.expect(std.mem.indexOf(u8, survey.roadmap_basis, "freeze-in-C anchor") != null);
            try std.testing.expect(std.mem.indexOf(u8, survey.repo_reality, "no carried-forward Phase 14 blocker survey") != null);
            try std.testing.expectEqualStrings("blocked_no_bounded_allocator_seam", survey.current_blocker);
        } else if (std.mem.eql(u8, survey.anchor, "kernel/rcu/tree.c")) {
            try std.testing.expect(std.mem.indexOf(u8, survey.roadmap_basis, "narrower-than-freeze") != null);
            try std.testing.expect(std.mem.indexOf(u8, survey.repo_reality, "P14-L13") != null);
            try std.testing.expect(std.mem.indexOf(u8, survey.repo_reality, "phase14-rcu-tree-bridge-blocker") != null);
            try std.testing.expectEqualStrings("blocked_phase14_followup_still_wider_than_allowed_rcu_seam", survey.current_blocker);
        } else if (std.mem.eql(u8, survey.anchor, "net/core/skbuff.c")) {
            try std.testing.expect(std.mem.indexOf(u8, survey.roadmap_basis, "narrower-than-lifetime") != null);
            try std.testing.expect(std.mem.indexOf(u8, survey.repo_reality, "P14-L09") != null);
            try std.testing.expect(std.mem.indexOf(u8, survey.repo_reality, "phase14-skbuff-live-ownership-blocker") != null);
            try std.testing.expectEqualStrings("blocked_packet_lifetime_boundary_still_too_wide", survey.current_blocker);
        }

        for (manifest.deep_core_blocker_survey[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, survey.anchor, other.anchor));
        }
    }
}

test "phase 15 freeze-map governance doc records the required gating language" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const freeze_map = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/freeze-map.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(freeze_map);

    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "## Governance For Freeze-Map Changes") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "Architecture Council") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "owner, phase, status bucket, validation gate summary, and rollback owner") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "exact Linux anchor path") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "current status bucket") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "evidence archive path") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "benchmark notes") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "replay command") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "latest blocker disposition") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "parity scorecard") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "rollback threshold") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "explicit non-goals") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "written rationale") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "## Stay-In-C Policy") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "keep the code in C and record the blocker") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "retired_from_active_discussion") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "reopen triggers") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "no silent exception path") != null);
}

test "phase 15 freeze-map governance doc records the current blocker posture honestly" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const governance_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-freeze-map-governance.md",
        std.testing.allocator,
        .limited(20 * 1024),
    );
    defer std.testing.allocator.free(governance_note);

    try std.testing.expect(std.mem.indexOf(u8, governance_note, "PHASE15_LANE_KEY=P15-L01") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "PHASE15_SLICE=freeze-map-deep-core-blocker-roadmap-reality-survey") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "verified `master` head `4fc891b380cdd2991dff7676ade7f844df1b55fd` observed on May 8, 2026") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "## Freeze-In-C Anchor Governance Inventory") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "Architecture Council + PMO / Release Management") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "Architecture Council + Validation and Perf Team") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "Architecture Council + ABI and Runtime Team") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "Architecture Council + Shared Subsystems Pod") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "pending_until_bounded_scheduler_seam_exists") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "pending_until_bounded_allocator_seam_exists") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "pending_until_rcu_followup_is_narrower_than_freeze_boundary") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "pending_until_skbuff_followup_is_narrower_than_lifetime_boundary") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "## Current blocker posture") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "blocked_no_bounded_scheduler_seam") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "blocked_no_bounded_allocator_seam") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "blocked_phase14_followup_still_wider_than_allowed_rcu_seam") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "blocked_packet_lifetime_boundary_still_too_wide") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "match the newer shared governance head `4fc891b380cdd2991dff7676ade7f844df1b55fd`") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "## Deep-core blockers versus roadmap and repo reality") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "no carried-forward Phase 14 blocker survey") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "lane P14-L13 still records blocked phase14-rcu-tree-bridge-blocker") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "lane P14-L09 still records blocked phase14-skbuff-live-ownership-blocker") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "maintenance mode") != null);
}

test "phase 15 governance manifest required terms stay aligned with the freeze map" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_freeze_map_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const freeze_map = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/freeze-map.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(freeze_map);

    const governance_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-freeze-map-governance.md",
        std.testing.allocator,
        .limited(20 * 1024),
    );
    defer std.testing.allocator.free(governance_note);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    for (parsed.value.governance_requirements) |requirement| {
        for (requirement.required_terms) |term| {
            try std.testing.expect(std.mem.indexOf(u8, freeze_map, term) != null);
        }
    }

    for (parsed.value.blocker_ownership) |ownership| {
        try std.testing.expect(std.mem.indexOf(u8, governance_note, ownership.anchor) != null);
        try std.testing.expect(std.mem.indexOf(u8, governance_note, ownership.owner) != null);
        try std.testing.expect(std.mem.indexOf(u8, governance_note, ownership.validation_gate) != null);
        try std.testing.expect(std.mem.indexOf(u8, governance_note, ownership.rollback_owner) != null);
        try std.testing.expect(std.mem.indexOf(u8, governance_note, ownership.evidence_archive_path) != null);
        try std.testing.expect(std.mem.indexOf(u8, governance_note, ownership.benchmark_notes) != null);
        try std.testing.expect(std.mem.indexOf(u8, governance_note, ownership.replay_command) != null);
        try std.testing.expect(std.mem.indexOf(u8, governance_note, ownership.latest_blocker_disposition) != null);
    }

    for (parsed.value.deep_core_blocker_survey) |survey| {
        try std.testing.expect(std.mem.indexOf(u8, governance_note, survey.anchor) != null);
        try std.testing.expect(std.mem.indexOf(u8, governance_note, survey.roadmap_basis) != null);
        try std.testing.expect(std.mem.indexOf(u8, governance_note, survey.repo_reality) != null);
        try std.testing.expect(std.mem.indexOf(u8, governance_note, survey.current_blocker) != null);
    }

    var saw_current_freeze_blocker_evidence_verify = false;
    var saw_deep_core_blocker_roadmap_reality_survey = false;
    for (parsed.value.gaps) |gap| {
        if (std.mem.eql(u8, gap.id, "phase15-current-freeze-blocker-evidence-verify")) {
            saw_current_freeze_blocker_evidence_verify = true;
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "newer exact head") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "freeze anchor set") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "blocker dispositions") != null);
        } else if (std.mem.eql(u8, gap.id, "phase15-deep-core-blocker-roadmap-reality-survey")) {
            saw_deep_core_blocker_roadmap_reality_survey = true;
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "anchor-by-anchor crosswalk") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "scheduler, page allocator, RCU, and skbuff") != null);
        }
    }
    try std.testing.expect(saw_current_freeze_blocker_evidence_verify);
    try std.testing.expect(saw_deep_core_blocker_roadmap_reality_survey);
}

test "phase 15 freeze-map governance note stays aligned with parity scorecard blocker evidence" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const governance_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-freeze-map-governance.md",
        std.testing.allocator,
        .limited(20 * 1024),
    );
    defer std.testing.allocator.free(governance_note);

    const scorecard_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-parity-scorecard.md",
        std.testing.allocator,
        .limited(36 * 1024),
    );
    defer std.testing.allocator.free(scorecard_doc);

    const scorecard_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_parity_scorecard.json",
        std.testing.allocator,
        .limited(40 * 1024),
    );
    defer std.testing.allocator.free(scorecard_json);

    const parsed = try std.json.parseFromSlice(ScorecardManifest, std.testing.allocator, scorecard_json, .{});
    defer parsed.deinit();

    for (parsed.value.anchors) |anchor| {
        try std.testing.expect(std.mem.indexOf(u8, scorecard_doc, anchor.lane_owner) != null);
        try std.testing.expect(std.mem.indexOf(u8, scorecard_doc, anchor.rollback_owner) != null);
        try std.testing.expect(std.mem.indexOf(u8, scorecard_doc, anchor.evidence_archive.decision_record_path) != null);
        try std.testing.expect(std.mem.indexOf(u8, scorecard_doc, anchor.evidence_archive.benchmark_notes_status) != null);
        try std.testing.expect(std.mem.indexOf(u8, scorecard_doc, anchor.evidence_archive.replay_command) != null);
        try std.testing.expect(std.mem.indexOf(u8, scorecard_doc, anchor.evidence_archive.latest_blocker_disposition) != null);
        try std.testing.expect(std.mem.indexOf(u8, governance_note, anchor.lane_owner) != null);
        try std.testing.expect(std.mem.indexOf(u8, governance_note, anchor.rollback_owner) != null);
        try std.testing.expect(std.mem.indexOf(u8, governance_note, anchor.evidence_archive.decision_record_path) != null);
        try std.testing.expect(std.mem.indexOf(u8, governance_note, anchor.evidence_archive.benchmark_notes_status) != null);
        try std.testing.expect(std.mem.indexOf(u8, governance_note, anchor.evidence_archive.replay_command) != null);
        try std.testing.expect(std.mem.indexOf(u8, governance_note, anchor.evidence_archive.latest_blocker_disposition) != null);
    }
}
