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

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    survey_summary: SurveySummary,
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

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-rcu-tree-survey.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P14-L16", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("kernel/rcu/tree.c", manifest.anchor);
    try std.testing.expectEqualStrings("4c889233d157960514b241bcd5aff7cac5fda312", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
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
    try std.testing.expectEqual(@as(usize, 7), manifest.decision_checklist.len);
    try std.testing.expectEqual(@as(usize, 15), manifest.gaps.len);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_LANE_KEY=P14-L16") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_SURVEYED_COMMIT=4c889233d157960514b241bcd5aff7cac5fda312") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "landed `phase14-rcu-tree-callback-offload-followup`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "landed `phase14-rcu-tree-idle-watch-followup`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "landed `phase14-rcu-tree-public-wait-and-barrier-followup`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "landed `phase14-rcu-tree-cpu-hotplug-followup`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "landed `phase14-rcu-tree-memory-ordering-followup`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "landed `phase14-rcu-tree-rollback-threshold-guardrail`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "blocked `phase14-rcu-tree-bridge-blocker`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "ready-next `phase14-rcu-tree-callback-offload-followup`") == null);

    var landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_freeze_note = false;
    var saw_survey_gate = false;
    var saw_decision_checklist = false;
    var saw_quiescent_followup = false;
    var saw_callback_followup = false;
    var saw_callback_offload_followup = false;
    var saw_idle_watch_followup = false;
    var saw_public_wait_followup = false;
    var saw_cpu_hotplug_followup = false;
    var saw_memory_ordering_followup = false;
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
            saw_quiescent_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-rcu-tree-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rcu_report_qs_rnp()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "note_gp_changes()") != null);
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
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rcu_nocb_flush_deferred_wakeup()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-idle-watch-followup")) {
            saw_idle_watch_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-rcu-tree-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rcu_is_watching()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "invoke_rcu_core()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-public-wait-and-barrier-followup")) {
            saw_public_wait_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-rcu-tree-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "synchronize_rcu()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rcu_barrier()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-cpu-hotplug-followup")) {
            saw_cpu_hotplug_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-rcu-tree-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rcutree_prepare_cpu()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rcutree_migrate_callbacks()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-memory-ordering-followup")) {
            saw_memory_ordering_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-rcu-tree-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "raw_spin_lock_rcu_node()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "smp_mb__after_unlock_lock()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "smp_store_release()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-rollback-threshold-guardrail")) {
            saw_rollback_guardrail = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-rcu-tree-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Architecture Council reopen record") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rollback owner") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-rcu-tree-bridge-blocker")) {
            saw_bridge_blocker = true;
            try std.testing.expectEqualStrings("kernel/rcu/tree_bridge.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "public wait-and-barrier") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "CPU hotplug") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 14), landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_freeze_note);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_decision_checklist);
    try std.testing.expect(saw_quiescent_followup);
    try std.testing.expect(saw_callback_followup);
    try std.testing.expect(saw_callback_offload_followup);
    try std.testing.expect(saw_idle_watch_followup);
    try std.testing.expect(saw_public_wait_followup);
    try std.testing.expect(saw_cpu_hotplug_followup);
    try std.testing.expect(saw_memory_ordering_followup);
    try std.testing.expect(saw_rollback_guardrail);
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
    try std.testing.expect(std.mem.indexOf(u8, checklist[1].rationale, "lock network") != null);

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
    try std.testing.expect(std.mem.indexOf(u8, checklist[4].rationale, "dyntick") != null);

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

test "phase 14 rcu tree survey keeps the memory-ordering boundary explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-rcu-tree-survey.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const tree_c = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "kernel/rcu/tree.c",
        std.testing.allocator,
        .limited(256 * 1024),
    );
    defer std.testing.allocator.free(tree_c);

    const update_c = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "kernel/rcu/update.c",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(update_c);

    const memory_order_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/RCU/Design/Memory-Ordering/Tree-RCU-Memory-Ordering.rst",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(memory_order_doc);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "## Memory-ordering network follow-up") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "raw_spin_lock_rcu_node()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "smp_mb__after_unlock_lock()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "smp_store_release()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "poll_state_synchronize_rcu_full()") != null);
    try std.testing.expect(std.mem.indexOf(u8, memory_order_doc, "raw_spin_lock_rcu_node()") != null);
    try std.testing.expect(std.mem.indexOf(u8, memory_order_doc, "smp_mb__after_unlock_lock()") != null);
    try std.testing.expect(std.mem.indexOf(u8, memory_order_doc, "poll_state_synchronize_rcu()") != null);
    try std.testing.expect(std.mem.indexOf(u8, memory_order_doc, "CPU-Hotplug Interface") != null);
    try std.testing.expect(std.mem.indexOf(u8, tree_c, "smp_store_release(&rcu_state.ncpus, rcu_state.ncpus + newcpu);") != null);
    try std.testing.expect(std.mem.indexOf(u8, tree_c, "smp_store_release(&rcu_state.gp_kthread, t);") != null);
    try std.testing.expect(std.mem.indexOf(u8, update_c, "synchronize_rcu()") != null);
    try std.testing.expect(std.mem.indexOf(u8, update_c, "start_poll_synchronize_rcu()") != null);
    try std.testing.expect(std.mem.indexOf(u8, update_c, "poll_state_synchronize_rcu_full()") != null);
}
