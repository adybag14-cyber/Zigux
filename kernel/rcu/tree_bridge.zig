const std = @import("std");

pub const BridgeBoundary = struct {
    id: []const u8,
    summary: []const u8,
    anchor_symbols: []const []const u8,
    rationale: []const u8,
};

pub const lane_key = "P14-L14";
pub const status_bucket = "freeze_in_c";
pub const anchor = "kernel/rcu/tree.c";
pub const roadmap_destination = "kernel/rcu/tree_bridge.zig";
pub const blocked_gap = "phase14-rcu-tree-bridge-blocker";
pub const live_bridge_claim = false;

pub const review_packet = [_][]const u8{
    "zigux/tests/phase14_rcu_tree_manifest.json",
    "zigux/tests/phase14_rcu_tree_survey.zig",
    "Documentation/zigux/phase14-rcu-tree-survey.md",
    "Documentation/zigux/freeze-map.md",
};

pub const blocked_boundaries = [_]BridgeBoundary{
    .{
        .id = "grace_period_sequence_publication",
        .summary = "Keep grace-period start, publication, and per-node propagation in C.",
        .anchor_symbols = &.{ "rcu_start_this_gp", "rcu_gp_init", "__note_gp_changes" },
        .rationale = "The gp_seq publication path still shares the live rcu_node hierarchy, qsmask state, and ordering guarantees.",
    },
    .{
        .id = "memory_ordering_lock_network",
        .summary = "Keep the lock-ordering network and publication stores in C.",
        .anchor_symbols = &.{ "raw_spin_lock_rcu_node", "smp_mb__after_unlock_lock", "smp_store_release" },
        .rationale = "The documented Tree RCU lock network remains a live ordering contract rather than a detachable wrapper seam.",
    },
    .{
        .id = "expedited_funnel_and_stall_path",
        .summary = "Keep expedited CPU selection, wait serialization, and sequence completion in C.",
        .anchor_symbols = &.{ "sync_rcu_exp_select_cpus", "synchronize_rcu_expedited_wait_once", "rcu_exp_gp_seq_end" },
        .rationale = "The expedited path still couples CPU forcing, stall-sensitive waiting, and sequence completion through live tree_exp.h coordination instead of a small bridge seam.",
    },
    .{
        .id = "nocb_offload_wakeup_handoff",
        .summary = "Keep NOCB bypass locking, deferred wakeups, and callback-offload handoff in C.",
        .anchor_symbols = &.{ "rcu_nocb_bypass_lock", "wake_nocb_gp_defer", "do_nocb_deferred_wakeup" },
        .rationale = "The NOCB path still relies on bypass-list pressure, deferred wakeup policy, and callback-offload coordination across tree.c and tree_nocb.h instead of a small bridge seam.",
    },
    .{
        .id = "idle_watch_reentry_and_core_invocation",
        .summary = "Keep idle-watch re-entry, dyntick snapshot ordering, and core invocation in C.",
        .anchor_symbols = &.{ "rcu_is_watching", "rcu_watching_snap_save", "invoke_rcu_core" },
        .rationale = "Extended-quiescent-state detection still depends on per-CPU watching state, remote dyntick ordering, and the live choice between softirq and rcuc wakeups, so this dyntick boundary remains coupled to live Tree RCU state.",
    },
    .{
        .id = "quiescent_state_propagation_and_callback_acceleration",
        .summary = "Keep quiescent-state propagation, per-node GP updates, and callback acceleration in C.",
        .anchor_symbols = &.{ "rcu_report_qs_rnp", "note_gp_changes", "rcu_accelerate_cbs" },
        .rationale = "Quiescent-state reporting still climbs the rcu_node hierarchy under lock, note_gp_changes() still folds gp-sequence changes into per-CPU callback state, and callback acceleration still depends on segmented callback lists and offload state.",
    },
    .{
        .id = "callback_enqueue_and_batch_invocation",
        .summary = "Keep callback enqueue, grace-period kick decisions, and batch invocation in C.",
        .anchor_symbols = &.{ "__call_rcu_common", "call_rcu_core", "rcu_do_batch" },
        .rationale = "Callback enqueue still routes through per-CPU segmented callback lists, overload tracking, NOCB offload selection, grace-period forcing, and time-bounded batch execution rather than a narrow bridge contract.",
    },
    .{
        .id = "public_wait_and_callback_barrier",
        .summary = "Keep public wait, polling-cookie, and callback-barrier ownership in C.",
        .anchor_symbols = &.{ "synchronize_rcu", "get_state_synchronize_rcu", "poll_state_synchronize_rcu", "rcu_barrier" },
        .rationale = "Public waiting and callback-drain guarantees still depend on deep-core Tree RCU sequencing and barrier coordination.",
    },
    .{
        .id = "cpu_hotplug_callback_migration",
        .summary = "Keep CPU enrollment, teardown, and callback migration in C.",
        .anchor_symbols = &.{ "rcutree_prepare_cpu", "rcutree_offline_cpu", "rcutree_migrate_callbacks" },
        .rationale = "CPU hotplug callback migration still shares live rcu_data and rcu_node ownership instead of a small bridge boundary.",
    },
};

pub fn blockedBoundaryCount() usize {
    return blocked_boundaries.len;
}

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

test "tree bridge boundary map stays review-only" {
    try std.testing.expectEqualStrings("P14-L14", lane_key);
    try std.testing.expectEqualStrings("freeze_in_c", status_bucket);
    try std.testing.expectEqualStrings("kernel/rcu/tree.c", anchor);
    try std.testing.expectEqualStrings("kernel/rcu/tree_bridge.zig", roadmap_destination);
    try std.testing.expectEqualStrings("phase14-rcu-tree-bridge-blocker", blocked_gap);
    try std.testing.expect(!live_bridge_claim);
    try std.testing.expectEqual(@as(usize, 9), blockedBoundaryCount());
    try std.testing.expectEqualStrings("idle_watch_reentry_and_core_invocation", blocked_boundaries[4].id);
    try std.testing.expect(contains(blocked_boundaries[4].summary, "idle-watch"));
    try std.testing.expectEqualStrings("quiescent_state_propagation_and_callback_acceleration", blocked_boundaries[5].id);
    try std.testing.expect(contains(blocked_boundaries[5].summary, "callback acceleration"));
    try std.testing.expectEqualStrings("callback_enqueue_and_batch_invocation", blocked_boundaries[6].id);
    try std.testing.expect(contains(blocked_boundaries[6].summary, "batch invocation"));
    try std.testing.expectEqualStrings("public_wait_and_callback_barrier", blocked_boundaries[7].id);
    try std.testing.expect(contains(blocked_boundaries[7].summary, "callback-barrier"));
    try std.testing.expectEqualStrings("cpu_hotplug_callback_migration", blocked_boundaries[8].id);
    try std.testing.expect(contains(blocked_boundaries[8].summary, "callback migration"));
}
