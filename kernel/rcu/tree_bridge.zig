const std = @import("std");

pub const Ownership = enum {
    boundary_map_only,
    stay_in_c,
};

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    posture: []const u8,
    provides_boundary_map: bool,
    provides_concurrency_audit_outline: bool,
    provides_stay_in_c_decisions: bool,
    touches_live_gp_state: bool,
    touches_live_nocb_state: bool,
    touches_live_hotplug_state: bool,
};

pub const BoundaryArea = struct {
    id: []const u8,
    summary: []const u8,
    ownership: Ownership,
    anchor_symbols: []const []const u8,
    rationale: []const u8,
};

pub const BoundaryMap = struct {
    anchor: []const u8,
    posture: []const u8,
    areas: []const BoundaryArea,
};

pub const AuditGuard = enum {
    gp_seq_publication_chain,
    memory_ordering_lock_network,
    expedited_funnel_and_wait,
    nocb_wakeup_handoff,
    idle_watch_dyntick_snapshot,
    quiescent_state_callback_acceleration,
    callback_enqueue_and_batch_invocation,
    public_wait_and_barrier_contract,
    cpu_hotplug_callback_migration,
};

pub const AuditCheckpoint = struct {
    id: []const u8,
    anchor_symbol: []const u8,
    summary: []const u8,
    guard: AuditGuard,
    observed_fields: []const []const u8,
    blocked_by: []const u8,
    ownership: Ownership,
};

pub const ConcurrencyAudit = struct {
    anchor: []const u8,
    posture: []const u8,
    checkpoints: []const AuditCheckpoint,
    blocked_live_behaviors: []const []const u8,
    next_step: []const u8,
};

const boundary_areas = [_]BoundaryArea{
    .{
        .id = "grace-period-sequence-publication",
        .summary = "Record grace-period startup and sequence publication as reviewable boundary evidence, not a live bridge claim.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "rcu_start_this_gp", "rcu_gp_init", "__note_gp_changes" },
        .rationale = "The grace-period core still couples gp_seq advancement to the rcu_node hierarchy, qsmask state, and memory-ordering guarantees, so this surface stays in C even though Zigux can now catalog it directly.",
    },
    .{
        .id = "memory-ordering-lock-network",
        .summary = "Keep the rcu_node lock network and GP publication stores in C while the review-only bridge names the ordering contract.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "raw_spin_lock_rcu_node", "smp_mb__after_unlock_lock", "smp_store_release" },
        .rationale = "Tree RCU's ordering guarantee still depends on the documented lock network, publication stores, and polling semantics shared across tree.c, update.c, and CPU-hotplug paths.",
    },
    .{
        .id = "expedited-funnel-and-stall-path",
        .summary = "Treat expedited CPU selection, waits, and sequence completion as explicit stay-in-C boundaries.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "sync_rcu_exp_select_cpus", "synchronize_rcu_expedited_wait_once", "rcu_exp_gp_seq_end" },
        .rationale = "The expedited path still funnels IPI-driven forcing, timeout handling, and sequence serialization through tightly coupled tree_exp.h logic rather than a detachable helper seam.",
    },
    .{
        .id = "nocb-offload-wakeup-handoff",
        .summary = "Keep NOCB bypass pressure, grace-period wakeups, and deferred wake policy in C.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "rcu_nocb_bypass_lock", "wake_nocb_gp_defer", "do_nocb_deferred_wakeup" },
        .rationale = "Callback offload still relies on bypass-list pressure, kthread wakeup policy, and deferred GP signaling across tree.c and tree_nocb.h, so this review-only bridge stops short of live ownership.",
    },
    .{
        .id = "idle-watch-reentry-and-core-invocation",
        .summary = "Keep idle-watch snapshots and re-entry decisions in C while exposing the boundary markers.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "rcu_is_watching", "rcu_watching_snap_save", "invoke_rcu_core" },
        .rationale = "Extended-quiescent-state detection still depends on per-CPU watching state, remote dyntick snapshot ordering, and the live choice between softirq and rcuc-kthread wakeups.",
    },
    .{
        .id = "quiescent-state-propagation-and-callback-acceleration",
        .summary = "Keep quiescent-state propagation and callback acceleration inside the locked hierarchy.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "rcu_report_qs_rnp", "note_gp_changes", "rcu_accelerate_cbs" },
        .rationale = "Quiescent-state reporting still climbs the locked rcu_node tree and folds GP changes into per-CPU callback state, so the bridge remains descriptive rather than executable.",
    },
    .{
        .id = "callback-enqueue-and-batch-invocation",
        .summary = "Keep callback enqueue, GP kicks, and batch invocation explicitly in C.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "__call_rcu_common", "call_rcu_core", "rcu_do_batch" },
        .rationale = "Callback lifecycle ownership still depends on segmented callback lists, overload tracking, NOCB offload state, and time-bounded batch execution under the existing Tree RCU core.",
    },
};

const audit_checkpoints = [_]AuditCheckpoint{
    .{
        .id = "grace-period-sequence-publication",
        .anchor_symbol = "rcu_start_this_gp/rcu_gp_init/__note_gp_changes",
        .summary = "Track gp_seq startup and publication across the live hierarchy before any wrapper claim.",
        .guard = .gp_seq_publication_chain,
        .observed_fields = &[_][]const u8{ "rcu_state.gp_seq", "rnp->gp_seq", "rnp->qsmask" },
        .blocked_by = "Grace-period startup still publishes gp_seq into the live rcu_node hierarchy while qsmask state and note_gp_changes() remain coupled to the same ordering contract, so Zigux should audit the chain rather than own it.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "memory-ordering-lock-network",
        .anchor_symbol = "raw_spin_lock_rcu_node/smp_mb__after_unlock_lock/smp_store_release",
        .summary = "Track the ordering network shared by GP setup, polling, and CPU-hotplug publication.",
        .guard = .memory_ordering_lock_network,
        .observed_fields = &[_][]const u8{ "rcu_state.gp_kthread", "rcu_state.ncpus", "rnp->lock" },
        .blocked_by = "Tree RCU's ordering guarantee still depends on the rcu_node lock network, smp_mb__after_unlock_lock pairing, and smp_store_release publication in GP and hotplug paths, so that contract stays in C.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "expedited-funnel-and-stall-path",
        .anchor_symbol = "sync_rcu_exp_select_cpus/synchronize_rcu_expedited_wait_once/rcu_exp_gp_seq_end",
        .summary = "Track expedited CPU selection, forced quiescent-state waiting, and sequence completion as one coupled boundary.",
        .guard = .expedited_funnel_and_wait,
        .observed_fields = &[_][]const u8{ "rcu_state.expedited_sequence", "rnp->expmask", "sync_rcu_exp_select_cpus()" },
        .blocked_by = "The expedited path still combines CPU selection, IPI-driven forcing, timeout handling, and final sequence publication across tree_exp.h rather than a small wrapper contract.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "nocb-offload-wakeup-handoff",
        .anchor_symbol = "call_rcu_nocb/nocb_gp_wait/rcu_nocb_flush_deferred_wakeup",
        .summary = "Track callback-offload enqueue, GP wait selection, and deferred wakeup flushing as one stay-in-C packet.",
        .guard = .nocb_wakeup_handoff,
        .observed_fields = &[_][]const u8{ "rdp->nocb_bypass", "rdp->nocb_gp_rdp", "rdp->nocb_defer_wakeup" },
        .blocked_by = "NOCB handling still relies on bypass pressure, grace-period wait selection, and deferred wake policy tied to live rcu_data and shared wake locks, so this bridge only records the handoff.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "idle-watch-reentry-and-core-invocation",
        .anchor_symbol = "rcu_is_watching/rcu_watching_snap_save/invoke_rcu_core",
        .summary = "Track per-CPU watching state, dyntick snapshots, and core re-entry policy without claiming execution ownership.",
        .guard = .idle_watch_dyntick_snapshot,
        .observed_fields = &[_][]const u8{ "rdp->dynticks", "rdp->dynticks_snap", "rcu_is_watching()" },
        .blocked_by = "Idle-watch transitions still depend on per-CPU watching state, remote dyntick snapshot ordering, and the softirq-versus-rcuc wake choice, so the live behavior remains in C.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "quiescent-state-propagation-and-callback-acceleration",
        .anchor_symbol = "rcu_report_qs_rnp/note_gp_changes/rcu_accelerate_cbs",
        .summary = "Track quiescent-state propagation and callback acceleration through the locked hierarchy.",
        .guard = .quiescent_state_callback_acceleration,
        .observed_fields = &[_][]const u8{ "rnp->qsmask", "rdp->gp_seq", "rdp->cblist" },
        .blocked_by = "Quiescent-state propagation still climbs the locked rcu_node hierarchy while callback acceleration depends on segmented callback lists and offload state, so the bridge remains review-only.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "callback-enqueue-and-batch-invocation",
        .anchor_symbol = "__call_rcu_common/call_rcu_core/rcu_do_batch",
        .summary = "Track callback enqueue, GP forcing, and batch execution under the existing callback lifecycle.",
        .guard = .callback_enqueue_and_batch_invocation,
        .observed_fields = &[_][]const u8{ "rdp->cblist", "rdp->qlen_last_fqs_check", "rdp->blimit" },
        .blocked_by = "Callback enqueue still routes through per-CPU segmented callback lists, overload tracking, NOCB selection, and batch invocation limits, so Zigux should not claim live ownership here.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "public-wait-and-barrier-contract",
        .anchor_symbol = "synchronize_rcu/start_poll_synchronize_rcu/poll_state_synchronize_rcu_full/rcu_barrier",
        .summary = "Track public wait, polling-cookie, and callback-barrier ownership as an explicit stay-in-C contract.",
        .guard = .public_wait_and_barrier_contract,
        .observed_fields = &[_][]const u8{ "rcu_state.gp_seq", "rcu_state.barrier_sequence", "rcu_state.barrier_completion" },
        .blocked_by = "Public wait and barrier APIs still choose between normal and expedited machinery, lock live root-node state when polling starts a new GP, and drain callbacks across online, offline, and offloaded CPUs, so the behavior remains in C.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "cpu-hotplug-callback-migration",
        .anchor_symbol = "rcutree_prepare_cpu/rcutree_report_cpu_dead/rcutree_migrate_callbacks",
        .summary = "Track CPU enrollment, teardown, and callback migration as one hotplug-owned boundary.",
        .guard = .cpu_hotplug_callback_migration,
        .observed_fields = &[_][]const u8{ "rcu_state.ncpus", "rnp->ffmask", "rdp->cblist" },
        .blocked_by = "CPU hotplug still rewires the live hierarchy, quiescent-state bookkeeping, and callback ownership between CPUs while preserving the same wakeup and ordering guarantees as normal execution, so Zigux should leave it in C.",
        .ownership = .stay_in_c,
    },
};

const blocked_live_behaviors = [_][]const u8{
    "grace-period sequence publication and rcu_node propagation",
    "memory-ordering lock-network publication across GP, polling, and hotplug paths",
    "expedited grace-period CPU selection, waits, and stall handling",
    "NOCB offload enqueue, GP wait selection, and deferred wakeups",
    "idle-watch transitions and dyntick re-entry decisions",
    "quiescent-state propagation and callback acceleration",
    "callback enqueue, GP forcing, and batch invocation ownership",
    "public wait, polling-cookie, and callback-barrier ownership",
    "CPU hotplug enrollment, teardown, and callback migration",
};

pub const RcuTreeBridgeLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "rcu_tree_boundary_map_lab",
            .anchor = "kernel/rcu/tree.c",
            .posture = "boundary_map_only",
            .provides_boundary_map = true,
            .provides_concurrency_audit_outline = true,
            .provides_stay_in_c_decisions = true,
            .touches_live_gp_state = false,
            .touches_live_nocb_state = false,
            .touches_live_hotplug_state = false,
        };
    }

    pub fn boundaryMap() BoundaryMap {
        return .{
            .anchor = descriptor().anchor,
            .posture = descriptor().posture,
            .areas = boundary_areas[0..],
        };
    }

    pub fn concurrencyAudit() ConcurrencyAudit {
        return .{
            .anchor = descriptor().anchor,
            .posture = descriptor().posture,
            .checkpoints = audit_checkpoints[0..],
            .blocked_live_behaviors = blocked_live_behaviors[0..],
            .next_step = nextAuditFocus(),
        };
    }

    pub fn stayInCDecisionCount() usize {
        var count: usize = 0;
        for (boundary_areas) |area| {
            if (area.ownership == .stay_in_c) count += 1;
        }
        return count;
    }

    pub fn auditCheckpointCount() usize {
        return audit_checkpoints.len;
    }

    pub fn checkpointById(id: []const u8) ?AuditCheckpoint {
        for (audit_checkpoints) |checkpoint| {
            if (std.mem.eql(u8, checkpoint.id, id)) return checkpoint;
        }
        return null;
    }

    pub fn hasAuditGuard(guard: AuditGuard) bool {
        for (audit_checkpoints) |checkpoint| {
            if (checkpoint.guard == guard) return true;
        }
        return false;
    }

    pub fn blockedBehaviorIndex(behavior: []const u8) ?usize {
        for (blocked_live_behaviors, 0..) |blocked_behavior, index| {
            if (std.mem.eql(u8, blocked_behavior, behavior)) return index;
        }
        return null;
    }

    pub fn blocksLiveBehavior(behavior: []const u8) bool {
        return blockedBehaviorIndex(behavior) != null;
    }

    pub fn nextAuditFocus() []const u8 {
        return "Keep kernel/rcu/tree_bridge.zig review-only; no smaller truthful followup remains before the blocked live bridge boundary around GP publication, public wait and barrier APIs, NOCB offload, and CPU-hotplug callback migration.";
    }
};

test "rcu tree bridge descriptor stays boundary-map only" {
    const descriptor = RcuTreeBridgeLab.descriptor();

    try std.testing.expectEqualStrings("rcu_tree_boundary_map_lab", descriptor.name);
    try std.testing.expectEqualStrings("kernel/rcu/tree.c", descriptor.anchor);
    try std.testing.expectEqualStrings("boundary_map_only", descriptor.posture);
    try std.testing.expect(descriptor.provides_boundary_map);
    try std.testing.expect(descriptor.provides_concurrency_audit_outline);
    try std.testing.expect(descriptor.provides_stay_in_c_decisions);
    try std.testing.expect(!descriptor.touches_live_gp_state);
    try std.testing.expect(!descriptor.touches_live_nocb_state);
    try std.testing.expect(!descriptor.touches_live_hotplug_state);
}

test "rcu tree bridge boundary map records the stay-in-c decision packet" {
    const map = RcuTreeBridgeLab.boundaryMap();

    try std.testing.expectEqualStrings("kernel/rcu/tree.c", map.anchor);
    try std.testing.expectEqualStrings("boundary_map_only", map.posture);
    try std.testing.expectEqual(@as(usize, 7), map.areas.len);
    try std.testing.expectEqual(@as(usize, 7), RcuTreeBridgeLab.stayInCDecisionCount());
    try std.testing.expect(std.mem.indexOf(u8, RcuTreeBridgeLab.nextAuditFocus(), "review-only") != null);
    try std.testing.expect(std.mem.indexOf(u8, RcuTreeBridgeLab.nextAuditFocus(), "CPU-hotplug callback migration") != null);

    try std.testing.expectEqualStrings("grace-period-sequence-publication", map.areas[0].id);
    try std.testing.expect(map.areas[0].ownership == .stay_in_c);
    try std.testing.expectEqualStrings("rcu_start_this_gp", map.areas[0].anchor_symbols[0]);

    try std.testing.expectEqualStrings("memory-ordering-lock-network", map.areas[1].id);
    try std.testing.expectEqualStrings("smp_store_release", map.areas[1].anchor_symbols[2]);

    try std.testing.expectEqualStrings("nocb-offload-wakeup-handoff", map.areas[3].id);
    try std.testing.expect(std.mem.indexOf(u8, map.areas[3].rationale, "deferred GP signaling") != null);

    try std.testing.expectEqualStrings("callback-enqueue-and-batch-invocation", map.areas[6].id);
    try std.testing.expectEqualStrings("rcu_do_batch", map.areas[6].anchor_symbols[2]);
}

test "rcu tree bridge concurrency audit stays review-only" {
    const audit = RcuTreeBridgeLab.concurrencyAudit();

    try std.testing.expectEqualStrings("kernel/rcu/tree.c", audit.anchor);
    try std.testing.expectEqualStrings("boundary_map_only", audit.posture);
    try std.testing.expectEqual(@as(usize, 9), audit.checkpoints.len);
    try std.testing.expectEqual(@as(usize, 9), audit.blocked_live_behaviors.len);
    try std.testing.expectEqual(@as(usize, 9), RcuTreeBridgeLab.auditCheckpointCount());

    const gp_publication = RcuTreeBridgeLab.checkpointById("grace-period-sequence-publication") orelse return error.MissingCheckpoint;
    try std.testing.expect(gp_publication.guard == .gp_seq_publication_chain);
    try std.testing.expectEqualStrings("rnp->qsmask", gp_publication.observed_fields[2]);

    const ordering = RcuTreeBridgeLab.checkpointById("memory-ordering-lock-network") orelse return error.MissingCheckpoint;
    try std.testing.expect(ordering.guard == .memory_ordering_lock_network);
    try std.testing.expect(std.mem.indexOf(u8, ordering.blocked_by, "smp_mb__after_unlock_lock") != null);

    const public_wait = RcuTreeBridgeLab.checkpointById("public-wait-and-barrier-contract") orelse return error.MissingCheckpoint;
    try std.testing.expect(public_wait.guard == .public_wait_and_barrier_contract);
    try std.testing.expectEqualStrings("rcu_state.barrier_sequence", public_wait.observed_fields[1]);
    try std.testing.expect(std.mem.indexOf(u8, public_wait.blocked_by, "online, offline, and offloaded CPUs") != null);

    const hotplug = RcuTreeBridgeLab.checkpointById("cpu-hotplug-callback-migration") orelse return error.MissingCheckpoint;
    try std.testing.expect(hotplug.guard == .cpu_hotplug_callback_migration);
    try std.testing.expectEqualStrings("rdp->cblist", hotplug.observed_fields[2]);

    try std.testing.expect(RcuTreeBridgeLab.hasAuditGuard(.nocb_wakeup_handoff));
    try std.testing.expect(RcuTreeBridgeLab.hasAuditGuard(.public_wait_and_barrier_contract));
    try std.testing.expect(RcuTreeBridgeLab.blocksLiveBehavior("public wait, polling-cookie, and callback-barrier ownership"));
    try std.testing.expectEqual(@as(?usize, 8), RcuTreeBridgeLab.blockedBehaviorIndex("CPU hotplug enrollment, teardown, and callback migration"));
    try std.testing.expect(!RcuTreeBridgeLab.blocksLiveBehavior("nonexistent rcu bridge behavior"));
}
