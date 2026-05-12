const std = @import("std");

const SurveySummary = struct {
    tree_c_lines: usize,
    tree_plugin_h_lines: usize,
    tree_exp_h_lines: usize,
    tree_nocb_h_lines: usize,
    update_c_lines: usize,
    requirements_doc_lines: usize,
    memory_order_doc_lines: usize,
    freeze_map_lists_tree_c: bool,
    preexisting_phase14_build_present: bool,
    preexisting_phase14_make_target_present: bool,
    preexisting_phase14_workqueue_bridge_present: bool,
    preexisting_phase14_ring_buffer_manifest_present: bool,
    preexisting_phase14_skbuff_bridge_present: bool,
    preexisting_tree_bridge_zig_present: bool,
    preexisting_phase14_rcu_tree_manifest_present: bool,
    preexisting_phase14_rcu_tree_survey_test_present: bool,
    preexisting_phase14_rcu_tree_survey_note_present: bool,
    rollback_threshold_note_present: bool,
    rollback_threshold_checklist_present: bool,
    rollback_threshold_freeze_map_rule_present: bool,
};

const BoundaryMapEntry = struct {
    roadmap_destination: []const u8,
    current_state: []const u8,
    reviewable_artifact: []const u8,
    blocker: []const u8,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const DecisionChecklistEntry = struct {
    id: []const u8,
    summary: []const u8,
    ownership: []const u8,
    anchor_symbols: []const []const u8,
    rationale: []const u8,
};

const RollbackThreshold = struct {
    status_bucket: []const u8,
    review_blocker_status: []const u8,
    owner: []const u8,
    rollback_owner: []const u8,
    required_evidence: []const []const u8,
    rollback_triggers: []const []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    boundary_map: []const BoundaryMapEntry,
    survey_summary: SurveySummary,
    rollback_threshold: RollbackThreshold,
    decision_checklist: []const DecisionChecklistEntry,
    gaps: []const Gap,
};

const LoadedManifest = struct {
    parsed: std.json.Parsed(Manifest),
    source: []u8,

    fn deinit(self: *LoadedManifest, allocator: std.mem.Allocator) void {
        self.parsed.deinit();
        allocator.free(self.source);
    }
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_missing_review_artifact") or
        std.mem.eql(u8, status, "blocked_on_stay_in_c_evidence");
}

fn loadManifest(allocator: std.mem.Allocator) !LoadedManifest {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_rcu_tree_manifest.json",
        allocator,
        .limited(64 * 1024),
    );
    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_json, .{});
    return .{
        .parsed = parsed,
        .source = manifest_json,
    };
}

fn loadSurveyNote(allocator: std.mem.Allocator) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-rcu-tree-survey.md",
        allocator,
        .limited(32 * 1024),
    );
}

fn loadBridgeMap(allocator: std.mem.Allocator) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "kernel/rcu/tree_bridge.zig",
        allocator,
        .limited(32 * 1024),
    );
}

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

test "phase 14 rcu tree survey manifest records the current freeze-boundary packet" {
    var loaded = try loadManifest(std.testing.allocator);
    defer loaded.deinit(std.testing.allocator);
    const manifest = loaded.parsed.value;

    try std.testing.expectEqualStrings("P14-L14", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("4c889233d157960514b241bcd5aff7cac5fda312", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("kernel/rcu/tree.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.boundary_map.len);

    try std.testing.expect(manifest.survey_summary.tree_c_lines >= 4900);
    try std.testing.expect(manifest.survey_summary.tree_plugin_h_lines >= 1300);
    try std.testing.expect(manifest.survey_summary.tree_exp_h_lines >= 1100);
    try std.testing.expect(manifest.survey_summary.tree_nocb_h_lines >= 1700);
    try std.testing.expect(manifest.survey_summary.update_c_lines >= 700);
    try std.testing.expect(manifest.survey_summary.requirements_doc_lines >= 2800);
    try std.testing.expect(manifest.survey_summary.memory_order_doc_lines >= 600);
    try std.testing.expect(manifest.survey_summary.freeze_map_lists_tree_c);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_make_target_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_workqueue_bridge_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_ring_buffer_manifest_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_skbuff_bridge_present);
    try std.testing.expect(manifest.survey_summary.preexisting_tree_bridge_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_rcu_tree_manifest_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_rcu_tree_survey_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_rcu_tree_survey_note_present);
    try std.testing.expect(manifest.survey_summary.rollback_threshold_note_present);
    try std.testing.expect(manifest.survey_summary.rollback_threshold_checklist_present);
    try std.testing.expect(manifest.survey_summary.rollback_threshold_freeze_map_rule_present);

    try std.testing.expectEqual(@as(usize, 8), manifest.decision_checklist.len);
    try std.testing.expectEqual(@as(usize, 15), manifest.gaps.len);

    var landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_build_gate = false;
    var saw_survey_gate = false;
    var saw_note_gap = false;
    var saw_memory_ordering = false;
    var saw_idle_watch = false;
    var saw_public_wait = false;
    var saw_cpu_hotplug = false;
    var saw_rollback_guardrail = false;
    var saw_bridge_blocker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_missing_review_artifact")) {
            blocked_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_stay_in_c_evidence")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase14-build-gate")) {
            saw_build_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase14_build.zig", gap.zigux_destination);
            try std.testing.expect(contains(gap.why_now, "full-bundle compile matrix"));
        }

        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase14_rcu_tree_survey.zig", gap.zigux_destination);
            try std.testing.expect(contains(gap.why_now, "reviewable"));
        }

        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-survey-note")) {
            saw_note_gap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-rcu-tree-survey.md", gap.zigux_destination);
            try std.testing.expect(contains(gap.why_now, "republishes the dedicated RCU survey note"));
            try std.testing.expect(contains(gap.why_now, "P14-L14"));
        }

        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-memory-ordering-followup")) {
            saw_memory_ordering = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-rcu-tree-survey.md", gap.zigux_destination);
            try std.testing.expect(contains(gap.why_now, "raw_spin_lock_rcu_node()"));
            try std.testing.expect(contains(gap.why_now, "smp_store_release()"));
        }

        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-idle-watch-followup")) {
            saw_idle_watch = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(contains(gap.why_now, "rcu_is_watching()"));
            try std.testing.expect(contains(gap.why_now, "invoke_rcu_core()"));
        }

        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-public-wait-and-barrier-followup")) {
            saw_public_wait = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(contains(gap.why_now, "synchronize_rcu()"));
            try std.testing.expect(contains(gap.why_now, "get_state_synchronize_rcu()"));
            try std.testing.expect(contains(gap.why_now, "poll_state_synchronize_rcu()"));
            try std.testing.expect(contains(gap.why_now, "rcu_barrier()"));
            try std.testing.expect(contains(gap.why_now, "polling-cookie"));
        }

        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-cpu-hotplug-followup")) {
            saw_cpu_hotplug = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(contains(gap.why_now, "rcutree_prepare_cpu()"));
            try std.testing.expect(contains(gap.why_now, "rcutree_migrate_callbacks()"));
        }

        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-rollback-threshold-guardrail")) {
            saw_rollback_guardrail = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase14_rcu_tree_manifest.json", gap.zigux_destination);
            try std.testing.expect(contains(gap.why_now, "Architecture Council reopen record"));
            try std.testing.expect(contains(gap.why_now, "rollback threshold"));
        }

        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-bridge-blocker")) {
            saw_bridge_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", gap.status);
            try std.testing.expectEqualStrings("kernel/rcu/tree_bridge.zig", gap.zigux_destination);
            try std.testing.expect(contains(gap.why_now, "public wait, polling-cookie, and callback-barrier APIs"));
            try std.testing.expect(contains(gap.why_now, "CPU hotplug migration"));
            try std.testing.expect(contains(gap.why_now, "memory-ordering rules"));
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 14), landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_note_gap);
    try std.testing.expect(saw_memory_ordering);
    try std.testing.expect(saw_idle_watch);
    try std.testing.expect(saw_public_wait);
    try std.testing.expect(saw_cpu_hotplug);
    try std.testing.expect(saw_rollback_guardrail);
    try std.testing.expect(saw_bridge_blocker);

    try std.testing.expectEqualStrings(
        "reviewable_survey_landed",
        manifest.boundary_map[0].current_state,
    );
    try std.testing.expectEqualStrings(
        "zigux/tests/phase14_rcu_tree_survey.zig",
        manifest.boundary_map[0].reviewable_artifact,
    );
    try std.testing.expectEqualStrings("", manifest.boundary_map[0].blocker);
    try std.testing.expectEqualStrings(
        "reviewable_survey_landed",
        manifest.boundary_map[1].current_state,
    );
    try std.testing.expectEqualStrings("", manifest.boundary_map[1].blocker);
    try std.testing.expectEqualStrings(
        "blocked_on_stay_in_c_evidence",
        manifest.boundary_map[2].current_state,
    );
    try std.testing.expect(contains(manifest.boundary_map[2].blocker, "public wait plus polling-cookie APIs"));
}

test "phase 14 rcu tree survey note matches the live manifest-backed owner and blocker posture" {
    const note = try loadSurveyNote(std.testing.allocator);
    defer std.testing.allocator.free(note);

    try std.testing.expect(contains(note, "PHASE14_LANE_KEY=P14-L14"));
    try std.testing.expect(contains(note, "PHASE14_STATUS_BUCKET=freeze_in_c"));
    try std.testing.expect(contains(note, "PHASE14_BLOCKED_GAP=phase14-rcu-tree-bridge-blocker"));
    try std.testing.expect(contains(note, "NOCB wakeup handoff still stays in C"));
    try std.testing.expect(contains(note, "quiescent-state propagation and callback acceleration still stay in C"));
    try std.testing.expect(contains(note, "callback enqueue and batch invocation still stay in C"));
    try std.testing.expect(contains(note, "public wait and callback-barrier ownership still stay in C"));
    try std.testing.expect(contains(note, "poll_state_synchronize_rcu"));
    try std.testing.expect(contains(note, "CPU hotplug callback migration still stays in C"));
    try std.testing.expect(contains(note, "memory-ordering lock network still stays in C"));
    try std.testing.expect(contains(note, "`zigux/tests/phase14_end_to_end_smoke_manifest.json`"));
    try std.testing.expect(contains(note, "`Documentation/zigux/phase14-core-boundary-traceability.md`"));
    try std.testing.expect(contains(note, "`kernel/rcu/tree_bridge.zig` remains blocked"));
    try std.testing.expect(contains(note, "Architecture Council reopen request"));
}

test "phase 14 rcu tree bridge boundary map exists as review-only evidence" {
    const bridge = try loadBridgeMap(std.testing.allocator);
    defer std.testing.allocator.free(bridge);

    try std.testing.expect(contains(bridge, "pub const lane_key = \"P14-L14\""));
    try std.testing.expect(contains(bridge, "pub const status_bucket = \"freeze_in_c\""));
    try std.testing.expect(contains(bridge, "pub const blocked_gap = \"phase14-rcu-tree-bridge-blocker\""));
    try std.testing.expect(contains(bridge, "public_wait_and_callback_barrier"));
    try std.testing.expect(contains(bridge, "cpu_hotplug_callback_migration"));
    try std.testing.expect(contains(bridge, "live_bridge_claim = false"));
}

test "phase 14 rcu tree survey exposes the landed freeze-boundary checklist and rollback guardrail" {
    var loaded = try loadManifest(std.testing.allocator);
    defer loaded.deinit(std.testing.allocator);
    const manifest = loaded.parsed.value;
    const checklist = manifest.decision_checklist;
    const rollback = manifest.rollback_threshold;

    try std.testing.expectEqualStrings("freeze_in_c", rollback.status_bucket);
    try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", rollback.review_blocker_status);
    try std.testing.expectEqualStrings("Core-Adjacent Pod", rollback.owner);
    try std.testing.expectEqualStrings("Repo Tooling Pod", rollback.rollback_owner);
    try std.testing.expectEqual(@as(usize, 3), rollback.required_evidence.len);
    try std.testing.expectEqual(@as(usize, 3), rollback.rollback_triggers.len);
    try std.testing.expect(contains(rollback.required_evidence[0], "Architecture Council reopen record"));
    try std.testing.expect(contains(rollback.rollback_triggers[0], "kernel/rcu/tree_bridge.zig"));

    try std.testing.expectEqualStrings("grace-period-sequence-publication", checklist[0].id);
    try std.testing.expectEqualStrings("stay_in_c", checklist[0].ownership);
    try std.testing.expectEqualStrings("rcu_start_this_gp", checklist[0].anchor_symbols[0]);
    try std.testing.expectEqualStrings("rcu_gp_init", checklist[0].anchor_symbols[1]);
    try std.testing.expectEqualStrings("__note_gp_changes", checklist[0].anchor_symbols[2]);
    try std.testing.expect(contains(checklist[0].rationale, "gp_seq"));

    try std.testing.expectEqualStrings("memory-ordering-lock-network", checklist[1].id);
    try std.testing.expectEqualStrings("raw_spin_lock_rcu_node", checklist[1].anchor_symbols[0]);
    try std.testing.expectEqualStrings("smp_mb__after_unlock_lock", checklist[1].anchor_symbols[1]);
    try std.testing.expectEqualStrings("smp_store_release", checklist[1].anchor_symbols[2]);
    try std.testing.expect(contains(checklist[1].rationale, "lock network"));

    try std.testing.expectEqualStrings("expedited-funnel-and-stall-path", checklist[2].id);
    try std.testing.expectEqualStrings("sync_rcu_exp_select_cpus", checklist[2].anchor_symbols[0]);
    try std.testing.expectEqualStrings("synchronize_rcu_expedited_wait_once", checklist[2].anchor_symbols[1]);
    try std.testing.expectEqualStrings("rcu_exp_gp_seq_end", checklist[2].anchor_symbols[2]);

    try std.testing.expectEqualStrings("nocb-offload-wakeup-handoff", checklist[3].id);
    try std.testing.expectEqualStrings("rcu_nocb_bypass_lock", checklist[3].anchor_symbols[0]);
    try std.testing.expectEqualStrings("wake_nocb_gp_defer", checklist[3].anchor_symbols[1]);
    try std.testing.expectEqualStrings("do_nocb_deferred_wakeup", checklist[3].anchor_symbols[2]);

    try std.testing.expectEqualStrings("idle-watch-reentry-and-core-invocation", checklist[4].id);
    try std.testing.expectEqualStrings("rcu_is_watching", checklist[4].anchor_symbols[0]);
    try std.testing.expectEqualStrings("rcu_watching_snap_save", checklist[4].anchor_symbols[1]);
    try std.testing.expectEqualStrings("invoke_rcu_core", checklist[4].anchor_symbols[2]);

    try std.testing.expectEqualStrings("quiescent-state-propagation-and-callback-acceleration", checklist[5].id);
    try std.testing.expectEqualStrings("rcu_report_qs_rnp", checklist[5].anchor_symbols[0]);
    try std.testing.expectEqualStrings("note_gp_changes", checklist[5].anchor_symbols[1]);
    try std.testing.expectEqualStrings("rcu_accelerate_cbs", checklist[5].anchor_symbols[2]);

    try std.testing.expectEqualStrings("callback-enqueue-and-batch-invocation", checklist[6].id);
    try std.testing.expectEqualStrings("__call_rcu_common", checklist[6].anchor_symbols[0]);
    try std.testing.expectEqualStrings("call_rcu_core", checklist[6].anchor_symbols[1]);
    try std.testing.expectEqualStrings("rcu_do_batch", checklist[6].anchor_symbols[2]);

    try std.testing.expectEqualStrings("cpu-hotplug-callback-migration", checklist[7].id);
    try std.testing.expectEqualStrings("rcutree_prepare_cpu", checklist[7].anchor_symbols[0]);
    try std.testing.expectEqualStrings("rcutree_offline_cpu", checklist[7].anchor_symbols[1]);
    try std.testing.expectEqualStrings("rcu_migrate_callbacks", checklist[7].anchor_symbols[2]);
    try std.testing.expect(contains(checklist[7].rationale, "callback migration"));
}
