const std = @import("std");

pub const BoundaryCoupling = enum {
    concurrency_coupled,
    public_wait_surface,
};

pub const BridgeBoundary = struct {
    id: []const u8,
    summary: []const u8,
    anchor_symbols: []const []const u8,
    rationale: []const u8,
    coupling: BoundaryCoupling,
};

pub const lane_key = "P14-L16";
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
    "Documentation/zigux/phase14-core-boundary-traceability.md",
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
    "zigux/tests/phase14_end_to_end_smoke_manifest.json",
    "scripts/zigux/check-phase14-rcu-compile-route.py",
    "scripts/zigux/check-phase14-rcu-rollback-guardrail.py",
};

pub const blocked_boundaries = [_]BridgeBoundary{
    .{
        .id = "grace_period_sequence_publication",
        .summary = "Keep grace-period start, publication, and per-node propagation in C.",
        .anchor_symbols = &.{ "rcu_start_this_gp", "rcu_gp_init", "__note_gp_changes" },
        .rationale = "The gp_seq publication path still shares the live rcu_node hierarchy, qsmask state, and ordering guarantees.",
        .coupling = .concurrency_coupled,
    },
    .{
        .id = "memory_ordering_lock_network",
        .summary = "Keep the lock-ordering network and publication stores in C.",
        .anchor_symbols = &.{ "raw_spin_lock_rcu_node", "smp_mb__after_unlock_lock", "smp_store_release" },
        .rationale = "The documented Tree RCU lock network remains a live ordering contract rather than a detachable wrapper seam.",
        .coupling = .concurrency_coupled,
    },
    .{
        .id = "expedited_funnel_and_stall_path",
        .summary = "Keep expedited CPU selection, wait serialization, and sequence completion in C.",
        .anchor_symbols = &.{ "sync_rcu_exp_select_cpus", "synchronize_rcu_expedited_wait_once", "rcu_exp_gp_seq_end" },
        .rationale = "The expedited path still couples CPU forcing, stall-sensitive waiting, and sequence completion through live tree_exp.h coordination instead of a small bridge seam.",
        .coupling = .concurrency_coupled,
    },
    .{
        .id = "nocb_offload_wakeup_handoff",
        .summary = "Keep NOCB bypass locking, deferred wakeups, and callback-offload handoff in C.",
        .anchor_symbols = &.{ "rcu_nocb_bypass_lock", "wake_nocb_gp_defer", "do_nocb_deferred_wakeup" },
        .rationale = "The NOCB path still relies on bypass-list pressure, deferred wakeup policy, and callback-offload coordination across tree.c and tree_nocb.h instead of a small bridge seam.",
        .coupling = .concurrency_coupled,
    },
    .{
        .id = "idle_watch_reentry_and_core_invocation",
        .summary = "Keep idle-watch re-entry, dyntick snapshot ordering, and core invocation in C.",
        .anchor_symbols = &.{ "rcu_is_watching", "rcu_watching_snap_save", "invoke_rcu_core" },
        .rationale = "Extended-quiescent-state detection still depends on per-CPU watching state, remote dyntick ordering, and the live choice between softirq and rcuc wakeups, so this dyntick boundary remains coupled to live Tree RCU state.",
        .coupling = .concurrency_coupled,
    },
    .{
        .id = "quiescent_state_propagation_and_callback_acceleration",
        .summary = "Keep quiescent-state propagation, per-node GP updates, and callback acceleration in C.",
        .anchor_symbols = &.{ "rcu_report_qs_rnp", "note_gp_changes", "rcu_accelerate_cbs" },
        .rationale = "Quiescent-state reporting still climbs the rcu_node hierarchy under lock, note_gp_changes() still folds gp-sequence changes into per-CPU callback state, and callback acceleration still depends on segmented callback lists and offload state.",
        .coupling = .concurrency_coupled,
    },
    .{
        .id = "callback_enqueue_and_batch_invocation",
        .summary = "Keep callback enqueue, grace-period kick decisions, and batch invocation in C.",
        .anchor_symbols = &.{ "__call_rcu_common", "call_rcu_core", "rcu_do_batch" },
        .rationale = "Callback enqueue still routes through per-CPU segmented callback lists, overload tracking, NOCB offload selection, grace-period forcing, and time-bounded batch execution rather than a narrow bridge contract.",
        .coupling = .concurrency_coupled,
    },
    .{
        .id = "force_quiescent_state_and_gp_wake_escalation",
        .summary = "Keep force-quiescent-state escalation, stall-escalation wake coordination, and FQS looping in C.",
        .anchor_symbols = &.{ "rcu_force_quiescent_state", "rcu_gp_kthread_wake", "rcu_gp_fqs_loop" },
        .rationale = "Force-quiescent-state escalation still couples root-node gp_flags, grace-period kthread wake sequencing, stall-escalation wakeups, and the FQS loop through live rcu_state and rcu_node ownership rather than a narrow bridge seam.",
        .coupling = .concurrency_coupled,
    },
    .{
        .id = "poll_cookie_and_sync_waithead_rollover",
        .summary = "Keep poll-cookie sequencing, polled grace-period completion, synchronize_rcu wait-head rollover, and completion cleanup handoff in C as one public wait-state boundary.",
        .anchor_symbols = &.{ "rcu_poll_gp_seq_start_unlocked", "rcu_poll_gp_seq_end_unlocked", "rcu_sr_normal_gp_init", "rcu_sr_normal_gp_cleanup_work" },
        .rationale = "Poll-cookie visibility still shares gp_seq_polled snapshots, root-node grace-period sequencing, synchronize_rcu wait-head rollover, and the later workqueue cleanup plus completion handoff inside the live Tree RCU public wait-state machine rather than a narrow bridge seam.",
        .coupling = .public_wait_surface,
    },
    .{
        .id = "public_wait_and_callback_barrier",
        .summary = "Keep public wait, polling-cookie visibility, and callback-barrier ownership in C.",
        .anchor_symbols = &.{ "synchronize_rcu", "get_state_synchronize_rcu", "poll_state_synchronize_rcu", "rcu_barrier" },
        .rationale = "Public wait helpers still couple blocking waits, polling-cookie visibility, and callback-drain guarantees to deep-core Tree RCU sequencing and barrier coordination.",
        .coupling = .public_wait_surface,
    },
    .{
        .id = "cpu_hotplug_callback_migration",
        .summary = "Keep CPU enrollment, teardown, and callback migration in C.",
        .anchor_symbols = &.{ "rcutree_prepare_cpu", "rcutree_offline_cpu", "rcutree_migrate_callbacks" },
        .rationale = "CPU hotplug callback migration still shares live rcu_data and rcu_node ownership instead of a small bridge boundary.",
        .coupling = .concurrency_coupled,
    },
};

pub fn blockedBoundaryCount() usize {
    return blocked_boundaries.len;
}

pub fn concurrencyCoupledBoundaryCount() usize {
    var count: usize = 0;
    for (blocked_boundaries) |boundary| {
        if (boundary.coupling == .concurrency_coupled) {
            count += 1;
        }
    }
    return count;
}

pub fn publicWaitSurfaceBoundaryCount() usize {
    var count: usize = 0;
    for (blocked_boundaries) |boundary| {
        if (boundary.coupling == .public_wait_surface) {
            count += 1;
        }
    }
    return count;
}

pub fn findBoundaryById(id: []const u8) ?*const BridgeBoundary {
    for (&blocked_boundaries) |*boundary| {
        if (std.mem.eql(u8, boundary.id, id)) {
            return boundary;
        }
    }
    return null;
}

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

test "tree bridge boundary map stays review-only" {
    try std.testing.expectEqualStrings("P14-L16", lane_key);
    try std.testing.expectEqualStrings("freeze_in_c", status_bucket);
    try std.testing.expectEqualStrings("kernel/rcu/tree.c", anchor);
    try std.testing.expectEqualStrings("kernel/rcu/tree_bridge.zig", roadmap_destination);
    try std.testing.expectEqualStrings("phase14-rcu-tree-bridge-blocker", blocked_gap);
    try std.testing.expect(!live_bridge_claim);
    try std.testing.expectEqual(@as(usize, 9), review_packet.len);
    try std.testing.expectEqualStrings("zigux/tests/phase14_rcu_tree_manifest.json", review_packet[0]);
    try std.testing.expectEqualStrings("zigux/tests/phase14_rcu_tree_survey.zig", review_packet[1]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase14-rcu-tree-survey.md", review_packet[2]);
    try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", review_packet[3]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase14-core-boundary-traceability.md", review_packet[4]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase14-end-to-end-smoke-survey.md", review_packet[5]);
    try std.testing.expectEqualStrings("zigux/tests/phase14_end_to_end_smoke_manifest.json", review_packet[6]);
    try std.testing.expectEqualStrings("scripts/zigux/check-phase14-rcu-compile-route.py", review_packet[7]);
    try std.testing.expectEqualStrings("scripts/zigux/check-phase14-rcu-rollback-guardrail.py", review_packet[8]);
    try std.testing.expectEqual(@as(usize, 11), blockedBoundaryCount());
    try std.testing.expectEqual(@as(usize, 9), concurrencyCoupledBoundaryCount());
    try std.testing.expectEqual(@as(usize, 2), publicWaitSurfaceBoundaryCount());

    const grace_period_publication = findBoundaryById("grace_period_sequence_publication").?;
    try std.testing.expectEqualStrings("grace_period_sequence_publication", grace_period_publication.id);
    try std.testing.expectEqualStrings("rcu_start_this_gp", grace_period_publication.anchor_symbols[0]);
    try std.testing.expectEqualStrings("rcu_gp_init", grace_period_publication.anchor_symbols[1]);
    try std.testing.expectEqualStrings("__note_gp_changes", grace_period_publication.anchor_symbols[2]);
    try std.testing.expect(contains(grace_period_publication.rationale, "gp_seq"));
    try std.testing.expectEqual(BoundaryCoupling.concurrency_coupled, grace_period_publication.coupling);

    const lock_network = findBoundaryById("memory_ordering_lock_network").?;
    try std.testing.expectEqualStrings("raw_spin_lock_rcu_node", lock_network.anchor_symbols[0]);
    try std.testing.expectEqualStrings("smp_mb__after_unlock_lock", lock_network.anchor_symbols[1]);
    try std.testing.expectEqualStrings("smp_store_release", lock_network.anchor_symbols[2]);
    try std.testing.expect(contains(lock_network.summary, "lock-ordering"));
    try std.testing.expect(contains(lock_network.rationale, "ordering contract"));
    try std.testing.expectEqual(BoundaryCoupling.concurrency_coupled, lock_network.coupling);

    const expedited = findBoundaryById("expedited_funnel_and_stall_path").?;
    try std.testing.expectEqualStrings("sync_rcu_exp_select_cpus", expedited.anchor_symbols[0]);
    try std.testing.expectEqualStrings("synchronize_rcu_expedited_wait_once", expedited.anchor_symbols[1]);
    try std.testing.expectEqualStrings("rcu_exp_gp_seq_end", expedited.anchor_symbols[2]);
    try std.testing.expect(contains(expedited.summary, "wait serialization"));
    try std.testing.expect(contains(expedited.rationale, "stall-sensitive"));

    const nocb = findBoundaryById("nocb_offload_wakeup_handoff").?;
    try std.testing.expectEqualStrings("rcu_nocb_bypass_lock", nocb.anchor_symbols[0]);
    try std.testing.expectEqualStrings("wake_nocb_gp_defer", nocb.anchor_symbols[1]);
    try std.testing.expectEqualStrings("do_nocb_deferred_wakeup", nocb.anchor_symbols[2]);
    try std.testing.expect(contains(nocb.summary, "callback-offload"));
    try std.testing.expect(contains(nocb.rationale, "bypass-list pressure"));

    const idle_watch = findBoundaryById("idle_watch_reentry_and_core_invocation").?;
    try std.testing.expect(contains(idle_watch.summary, "idle-watch"));

    const quiescent = findBoundaryById("quiescent_state_propagation_and_callback_acceleration").?;
    try std.testing.expect(contains(quiescent.summary, "callback acceleration"));

    const callback_batch = findBoundaryById("callback_enqueue_and_batch_invocation").?;
    try std.testing.expect(contains(callback_batch.summary, "batch invocation"));

    const force_qs = findBoundaryById("force_quiescent_state_and_gp_wake_escalation").?;
    try std.testing.expectEqualStrings("rcu_force_quiescent_state", force_qs.anchor_symbols[0]);
    try std.testing.expectEqualStrings("rcu_gp_kthread_wake", force_qs.anchor_symbols[1]);
    try std.testing.expectEqualStrings("rcu_gp_fqs_loop", force_qs.anchor_symbols[2]);
    try std.testing.expect(contains(force_qs.summary, "force-quiescent-state"));
    try std.testing.expect(contains(force_qs.summary, "stall-escalation"));
    try std.testing.expect(contains(force_qs.summary, "FQS"));
    try std.testing.expect(contains(force_qs.rationale, "gp_flags"));

    const poll_cookie = findBoundaryById("poll_cookie_and_sync_waithead_rollover").?;
    try std.testing.expectEqualStrings("rcu_poll_gp_seq_start_unlocked", poll_cookie.anchor_symbols[0]);
    try std.testing.expectEqualStrings("rcu_poll_gp_seq_end_unlocked", poll_cookie.anchor_symbols[1]);
    try std.testing.expectEqualStrings("rcu_sr_normal_gp_init", poll_cookie.anchor_symbols[2]);
    try std.testing.expectEqualStrings("rcu_sr_normal_gp_cleanup_work", poll_cookie.anchor_symbols[3]);
    try std.testing.expect(contains(poll_cookie.summary, "public wait-state boundary"));
    try std.testing.expect(contains(poll_cookie.summary, "completion cleanup"));
    try std.testing.expect(contains(poll_cookie.rationale, "gp_seq_polled"));
    try std.testing.expect(contains(poll_cookie.rationale, "public wait-state machine"));
    try std.testing.expectEqual(BoundaryCoupling.public_wait_surface, poll_cookie.coupling);

    const public_wait = findBoundaryById("public_wait_and_callback_barrier").?;
    try std.testing.expect(contains(public_wait.summary, "polling-cookie visibility"));
    try std.testing.expect(contains(public_wait.summary, "callback-barrier"));
    try std.testing.expect(contains(public_wait.rationale, "polling-cookie visibility"));
    try std.testing.expectEqual(BoundaryCoupling.public_wait_surface, public_wait.coupling);

    const hotplug = findBoundaryById("cpu_hotplug_callback_migration").?;
    try std.testing.expect(contains(hotplug.summary, "callback migration"));
    try std.testing.expectEqual(BoundaryCoupling.concurrency_coupled, hotplug.coupling);
}
