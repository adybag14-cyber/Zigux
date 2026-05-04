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
    preexisting_phase14_rcu_tree_review_checklist_present: bool,
    rollback_threshold_note_present: bool,
    rollback_threshold_checklist_present: bool,
    rollback_threshold_freeze_map_rule_present: bool,
};

const RollbackThreshold = struct {
    status_bucket: []const u8,
    review_blocker_status: []const u8,
    owner: []const u8,
    rollback_owner: []const u8,
    fallback_path: []const u8,
    required_evidence: []const []const u8,
    rollback_triggers: []const []const u8,
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

const BoundaryMapEntry = struct {
    roadmap_destination: []const u8,
    current_state: []const u8,
    reviewable_artifact: []const u8,
    blocker: []const u8,
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

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_stay_in_c_evidence");
}

test "phase 14 rcu tree survey manifest records the freeze-boundary gap without inventing a bridge" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_rcu_tree_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P14-Y04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("kernel/rcu/tree.c", manifest.anchor);
    try std.testing.expectEqualStrings("355b71d89807a217a6b7c405c996cbd623c48ca0", manifest.surveyed_commit);
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
    try std.testing.expect(!manifest.survey_summary.preexisting_tree_bridge_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_rcu_tree_manifest_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_rcu_tree_survey_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_rcu_tree_survey_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_rcu_tree_review_checklist_present);
    try std.testing.expect(manifest.survey_summary.rollback_threshold_note_present);
    try std.testing.expect(manifest.survey_summary.rollback_threshold_checklist_present);
    try std.testing.expect(manifest.survey_summary.rollback_threshold_freeze_map_rule_present);
    try std.testing.expectEqualStrings("freeze_in_c", manifest.rollback_threshold.status_bucket);
    try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", manifest.rollback_threshold.review_blocker_status);
    try std.testing.expectEqualStrings("Core-Adjacent Pod", manifest.rollback_threshold.owner);
    try std.testing.expectEqualStrings("Repo Tooling Pod", manifest.rollback_threshold.rollback_owner);
    try std.testing.expect(std.mem.indexOf(u8, manifest.rollback_threshold.fallback_path, "product source of truth") != null);
    try std.testing.expectEqual(@as(usize, 3), manifest.rollback_threshold.required_evidence.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.rollback_threshold.rollback_triggers.len);
    try std.testing.expectEqual(@as(usize, 7), manifest.decision_checklist.len);
    try std.testing.expectEqual(@as(usize, 17), manifest.gaps.len);

    var landed_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_freeze_note = false;
    var saw_survey_gate = false;
    var saw_decision_checklist = false;
    var saw_followup = false;
    var saw_memory_ordering_followup = false;
    var saw_callback_followup = false;
    var saw_callback_offload_followup = false;
    var saw_gp_kthread_fqs_followup = false;
    var saw_idle_watch_followup = false;
    var saw_public_wait_followup = false;
    var saw_cpu_hotplug_followup = false;
    var saw_review_checklist_followup = false;
    var saw_rollback_threshold_guardrail = false;
    var saw_bridge_blocker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_stay_in_c_evidence")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase14-freeze-map-note")) {
            saw_freeze_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "freeze") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase14_rcu_tree_survey.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "survey gate") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-boundary-decision-checklist")) {
            saw_decision_checklist = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase14_rcu_tree_manifest.json", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "grace-period") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "NOCB") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-quiescent-state-followup")) {
            saw_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-rcu-tree-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rcu_report_qs_rnp()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "note_gp_changes()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-memory-ordering-followup")) {
            saw_memory_ordering_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-rcu-tree-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "raw_spin_lock_rcu_node()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "smp_mb__after_unlock_lock()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "smp_store_release()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-callback-enqueue-followup")) {
            saw_callback_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-rcu-tree-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__call_rcu_common()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rcu_do_batch()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-callback-offload-followup")) {
            saw_callback_offload_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-rcu-tree-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "call_rcu_nocb()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "nocb_gp_wait()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rcu_nocb_flush_deferred_wakeup()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-gp-kthread-fqs-followup")) {
            saw_gp_kthread_fqs_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-rcu-tree-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rcu_gp_kthread_wake()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rcu_gp_fqs_loop()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "force_qs_rnp()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-idle-watch-followup")) {
            saw_idle_watch_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-rcu-tree-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rcu_is_watching()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rcu_watching_snap_save()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "invoke_rcu_core()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-public-wait-and-barrier-followup")) {
            saw_public_wait_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-rcu-tree-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "synchronize_rcu()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "poll_state_synchronize_rcu_full()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rcu_barrier()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-cpu-hotplug-followup")) {
            saw_cpu_hotplug_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-rcu-tree-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rcutree_prepare_cpu()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rcutree_report_cpu_dead()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rcutree_migrate_callbacks()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-review-checklist-followup")) {
            saw_review_checklist_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("reviewability", gap.kind);
            try std.testing.expectEqualStrings("Documentation/zigux/review-checklist.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "surveyed commit pin") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "automatic return-to-blocked triggers") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "placeholder-wrapper non-goal") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-rollback-threshold-guardrail")) {
            saw_rollback_threshold_guardrail = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("rollback_guardrail", gap.kind);
            try std.testing.expectEqualStrings("zigux/tests/phase14_rcu_tree_manifest.json", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Architecture Council reopen record") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "placeholder wrapper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rollback owner") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-bridge-blocker")) {
            saw_bridge_blocker = true;
            try std.testing.expectEqualStrings("kernel/rcu/tree_bridge.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "placeholder wrapper") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 16), landed_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_freeze_note);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_decision_checklist);
    try std.testing.expect(saw_followup);
    try std.testing.expect(saw_memory_ordering_followup);
    try std.testing.expect(saw_callback_followup);
    try std.testing.expect(saw_callback_offload_followup);
    try std.testing.expect(saw_gp_kthread_fqs_followup);
    try std.testing.expect(saw_idle_watch_followup);
    try std.testing.expect(saw_public_wait_followup);
    try std.testing.expect(saw_cpu_hotplug_followup);
    try std.testing.expect(saw_review_checklist_followup);
    try std.testing.expect(saw_rollback_threshold_guardrail);
    try std.testing.expect(saw_bridge_blocker);
}

test "phase 14 rcu tree survey exposes the landed freeze-boundary checklist" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_rcu_tree_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const checklist = parsed.value.decision_checklist;
    try std.testing.expectEqualStrings("grace-period-sequence-publication", checklist[0].id);
    try std.testing.expectEqualStrings("stay_in_c", checklist[0].ownership);
    try std.testing.expectEqualStrings("rcu_start_this_gp", checklist[0].anchor_symbols[0]);
    try std.testing.expectEqualStrings("rcu_gp_init", checklist[0].anchor_symbols[1]);
    try std.testing.expectEqualStrings("__note_gp_changes", checklist[0].anchor_symbols[2]);
    try std.testing.expect(std.mem.indexOf(u8, checklist[0].rationale, "gp_seq") != null);

    try std.testing.expectEqualStrings("memory-ordering-lock-network", checklist[1].id);
    try std.testing.expectEqualStrings("raw_spin_lock_rcu_node", checklist[1].anchor_symbols[0]);
    try std.testing.expectEqualStrings("smp_mb__after_unlock_lock", checklist[1].anchor_symbols[1]);
    try std.testing.expectEqualStrings("smp_store_release", checklist[1].anchor_symbols[2]);
    try std.testing.expect(std.mem.indexOf(u8, checklist[1].rationale, "memory-ordering behavior") != null);

    try std.testing.expectEqualStrings("expedited-funnel-and-stall-path", checklist[2].id);
    try std.testing.expectEqualStrings("sync_rcu_exp_select_cpus", checklist[2].anchor_symbols[0]);
    try std.testing.expectEqualStrings("synchronize_rcu_expedited_wait_once", checklist[2].anchor_symbols[1]);
    try std.testing.expectEqualStrings("rcu_exp_gp_seq_end", checklist[2].anchor_symbols[2]);
    try std.testing.expect(std.mem.indexOf(u8, checklist[2].rationale, "IPI") != null);

    try std.testing.expectEqualStrings("nocb-offload-wakeup-handoff", checklist[3].id);
    try std.testing.expectEqualStrings("rcu_nocb_bypass_lock", checklist[3].anchor_symbols[0]);
    try std.testing.expectEqualStrings("wake_nocb_gp_defer", checklist[3].anchor_symbols[1]);
    try std.testing.expectEqualStrings("do_nocb_deferred_wakeup", checklist[3].anchor_symbols[2]);
    try std.testing.expect(std.mem.indexOf(u8, checklist[3].rationale, "bypass") != null);

    try std.testing.expectEqualStrings("idle-watch-reentry-and-core-invocation", checklist[4].id);
    try std.testing.expectEqualStrings("rcu_is_watching", checklist[4].anchor_symbols[0]);
    try std.testing.expectEqualStrings("rcu_watching_snap_save", checklist[4].anchor_symbols[1]);
    try std.testing.expectEqualStrings("invoke_rcu_core", checklist[4].anchor_symbols[2]);
    try std.testing.expect(std.mem.indexOf(u8, checklist[4].rationale, "softirq") != null);

    try std.testing.expectEqualStrings("quiescent-state-propagation-and-callback-acceleration", checklist[5].id);
    try std.testing.expectEqualStrings("rcu_report_qs_rnp", checklist[5].anchor_symbols[0]);
    try std.testing.expectEqualStrings("note_gp_changes", checklist[5].anchor_symbols[1]);
    try std.testing.expectEqualStrings("rcu_accelerate_cbs", checklist[5].anchor_symbols[2]);
    try std.testing.expect(std.mem.indexOf(u8, checklist[5].rationale, "segmented callback lists") != null);

    try std.testing.expectEqualStrings("callback-enqueue-and-batch-invocation", checklist[6].id);
    try std.testing.expectEqualStrings("__call_rcu_common", checklist[6].anchor_symbols[0]);
    try std.testing.expectEqualStrings("call_rcu_core", checklist[6].anchor_symbols[1]);
    try std.testing.expectEqualStrings("rcu_do_batch", checklist[6].anchor_symbols[2]);
    try std.testing.expect(std.mem.indexOf(u8, checklist[6].rationale, "NOCB offload") != null);
}

test "phase 14 rcu tree survey keeps the roadmap boundary map explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_rcu_tree_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-rcu-tree-survey.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const boundary_map = parsed.value.boundary_map;
    try std.testing.expectEqualStrings("zigux/tests/", boundary_map[0].roadmap_destination);
    try std.testing.expectEqualStrings("reviewable_survey_landed", boundary_map[0].current_state);
    try std.testing.expectEqualStrings("zigux/tests/phase14_rcu_tree_survey.zig", boundary_map[0].reviewable_artifact);
    try std.testing.expectEqualStrings("", boundary_map[0].blocker);

    try std.testing.expectEqualStrings("Documentation/zigux/", boundary_map[1].roadmap_destination);
    try std.testing.expectEqualStrings("reviewable_survey_landed", boundary_map[1].current_state);
    try std.testing.expectEqualStrings("Documentation/zigux/phase14-rcu-tree-survey.md", boundary_map[1].reviewable_artifact);
    try std.testing.expectEqualStrings("", boundary_map[1].blocker);

    try std.testing.expectEqualStrings("kernel/rcu/tree_bridge.zig", boundary_map[2].roadmap_destination);
    try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", boundary_map[2].current_state);
    try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", boundary_map[2].reviewable_artifact);
    try std.testing.expect(std.mem.indexOf(u8, boundary_map[2].blocker, "kernel/rcu/tree.c") != null);
    try std.testing.expect(std.mem.indexOf(u8, boundary_map[2].blocker, "freeze-in-C") != null);
    try std.testing.expect(std.mem.indexOf(u8, boundary_map[2].blocker, "public wait-and-barrier APIs") != null);
    try std.testing.expect(std.mem.indexOf(u8, boundary_map[2].blocker, "placeholder wrapper") != null);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "## Roadmap boundary map") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "bounded Phase 14 survey lane `P14-L16` around `kernel/rcu/tree.c`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "The honest move for this lane is therefore not to start `kernel/rcu/tree_bridge.zig`.") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_LANE_KEY=P14-L16") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_SURVEYED_COMMIT=355b71d89807a217a6b7c405c996cbd623c48ca0") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "survey provenance refreshed against verified `master` head `355b71d89807a217a6b7c405c996cbd623c48ca0`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`kernel/rcu/tree_bridge.zig`: `blocked_on_stay_in_c_evidence`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "without overstating progress or sneaking in a placeholder wrapper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "current freeze-in-C blocker") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`Documentation/zigux/review-checklist.md`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "## Shared review checklist follow-up") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "the Phase 14 RCU tree survey packet directly") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "## Memory-ordering network follow-up") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "raw_spin_lock_rcu_node()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "smp_mb__after_unlock_lock()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "smp_store_release()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "polling-order semantics remain explicitly in C") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "## Idle-watch and core-invocation follow-up") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "idle-watch transitions, dyntick snapshot ordering, and core re-entry remain explicitly in C") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "## Grace-period kthread wake and force-QS follow-up") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "rcu_gp_kthread_wake()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "rcu_gp_fqs_loop()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "force_qs_rnp()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "GP-kthread wakeups, force-QS timing, and quiescent-state forcing remain explicitly in C") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "## Public wait and barrier follow-up") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "public wait, polling, and callback-barrier surfaces remain explicitly in C") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "## CPU hotplug and callback migration follow-up") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "rcutree_prepare_cpu()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "CPU hotplug enrollment, teardown, and callback migration remain explicitly in C") != null);
}

test "phase 14 rcu tree survey keeps the rollback threshold guardrail explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const allocator = std.testing.allocator;

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_rcu_tree_manifest.json",
        allocator,
        .limited(32 * 1024),
    );
    defer allocator.free(manifest_json);

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-rcu-tree-survey.md",
        allocator,
        .limited(24 * 1024),
    );
    defer allocator.free(survey_note);

    const checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        allocator,
        .limited(32 * 1024),
    );
    defer allocator.free(checklist);

    const freeze_map = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/freeze-map.md",
        allocator,
        .limited(16 * 1024),
    );
    defer allocator.free(freeze_map);

    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_json, .{});
    defer parsed.deinit();

    const rollback_threshold = parsed.value.rollback_threshold;
    try std.testing.expectEqualStrings("freeze_in_c", rollback_threshold.status_bucket);
    try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", rollback_threshold.review_blocker_status);
    try std.testing.expectEqualStrings("Core-Adjacent Pod", rollback_threshold.owner);
    try std.testing.expectEqualStrings("Repo Tooling Pod", rollback_threshold.rollback_owner);
    try std.testing.expect(std.mem.indexOf(u8, rollback_threshold.fallback_path, "product source of truth") != null);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, rollback_threshold.fallback_path) != null);

    for (rollback_threshold.required_evidence) |required| {
        try std.testing.expect(std.mem.indexOf(u8, survey_note, required) != null);
    }
    for (rollback_threshold.rollback_triggers) |trigger| {
        try std.testing.expect(std.mem.indexOf(u8, survey_note, trigger) != null);
    }

    try std.testing.expect(std.mem.indexOf(u8, checklist, "rollback threshold") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "automatic return-to-blocked trigger") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "Phase 14 RCU tree survey packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "`blocked_on_stay_in_c_evidence` boundary-map status for `kernel/rcu/tree_bridge.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "placeholder bridge wrapper") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "rollback threshold that forces the anchor back to its blocked freeze posture") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "placeholder or empty `kernel/rcu/tree_bridge.zig` wrapper") != null);
}
