const std = @import("std");

const GovernanceRequirement = struct {
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

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_freeze_in_c_targets: []const []const u8,
    roadmap_study_only_targets: []const []const u8,
    freeze_in_c_targets: []const []const u8,
    study_only_targets: []const []const u8,
    repo_reality_evidence_paths: []const []const u8,
    current_blockers: []const []const u8,
    governance_requirements: []const GovernanceRequirement,
    gaps: []const Gap,
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
    try std.testing.expectEqualStrings("P15-L04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("ba15a15ff4f0becd063b9b12aeea73df5307e6ef", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 4), manifest.roadmap_freeze_in_c_targets.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_study_only_targets.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.freeze_in_c_targets.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.study_only_targets.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.repo_reality_evidence_paths.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.current_blockers.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.governance_requirements.len);
    try std.testing.expectEqual(@as(usize, 9), manifest.gaps.len);

    try std.testing.expectEqualStrings("kernel/sched/core.c", manifest.roadmap_freeze_in_c_targets[0]);
    try std.testing.expectEqualStrings("mm/page_alloc.c", manifest.roadmap_freeze_in_c_targets[1]);
    try std.testing.expectEqualStrings("kernel/rcu/tree.c", manifest.roadmap_freeze_in_c_targets[2]);
    try std.testing.expectEqualStrings("net/core/skbuff.c", manifest.roadmap_freeze_in_c_targets[3]);
    try std.testing.expectEqualStrings("kernel/workqueue.c", manifest.roadmap_study_only_targets[0]);
    try std.testing.expectEqualStrings("kernel/trace/ring_buffer.c", manifest.roadmap_study_only_targets[1]);
    try std.testing.expectEqualStrings("kernel/sched/core.c", manifest.freeze_in_c_targets[0]);
    try std.testing.expectEqualStrings("mm/page_alloc.c", manifest.freeze_in_c_targets[1]);
    try std.testing.expectEqualStrings("kernel/rcu/tree.c", manifest.freeze_in_c_targets[2]);
    try std.testing.expectEqualStrings("net/core/skbuff.c", manifest.freeze_in_c_targets[3]);
    try std.testing.expectEqualStrings("kernel/workqueue.c", manifest.study_only_targets[0]);
    try std.testing.expectEqualStrings("kernel/trace/ring_buffer.c", manifest.study_only_targets[1]);
    try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", manifest.repo_reality_evidence_paths[0]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-parity-scorecard.md", manifest.repo_reality_evidence_paths[1]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase14-rcu-tree-survey.md", manifest.repo_reality_evidence_paths[2]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase14-skbuff-bridge-survey.md", manifest.repo_reality_evidence_paths[3]);
    try std.testing.expectEqualStrings("kernel/sched/core.c: blocked_no_bounded_scheduler_seam", manifest.current_blockers[0]);
    try std.testing.expectEqualStrings("mm/page_alloc.c: blocked_no_bounded_allocator_seam", manifest.current_blockers[1]);
    try std.testing.expectEqualStrings("kernel/rcu/tree.c: blocked_phase14_followup_still_wider_than_allowed_rcu_seam", manifest.current_blockers[2]);
    try std.testing.expectEqualStrings("net/core/skbuff.c: blocked_packet_lifetime_boundary_still_too_wide", manifest.current_blockers[3]);

    var landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_freeze_doc = false;
    var saw_note = false;
    var saw_build = false;
    var saw_make = false;
    var saw_closeout_sync = false;
    var saw_governance_family_alignment = false;
    var saw_drift_gate = false;
    var saw_roadmap_vs_repo_reality = false;
    var saw_blocker = false;

    for (manifest.gaps, 0..) |gap, i| {
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

        if (std.mem.eql(u8, gap.id, "phase15-freeze-map-governance-doc")) {
            saw_freeze_doc = true;
            try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "freeze-in-C") != null);
        } 