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
    provides_lifetime_audit_outline: bool,
    provides_stay_in_c_decisions: bool,
    touches_live_allocators: bool,
    touches_live_refcounts: bool,
    touches_live_destructors: bool,
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
    header_write_requires_private_data,
    clone_or_reallocate_before_mutation,
    destructor_before_frag_release,
    checksum_complete_state_cache,
    segmentation_orphan_and_zerocopy_handoff,
    segmentation_checksum_metadata_handoff,
    segmentation_partial_tail_owner_transfer,
    segmentation_checksum_data_offset_crossover,
    segmentation_tail_publication_consumer_contract,
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

pub const LifetimeAudit = struct {
    anchor: []const u8,
    posture: []const u8,
    checkpoints: []const AuditCheckpoint,
    blocked_live_behaviors: []const []const u8,
    next_step: []const u8,
};

pub const FreezeGuardrail = struct {
    anchor: []const u8,
    status_bucket: []const u8,
    named_owner: []const u8,
    validation_gate: []const u8,
    rollback_owner: []const u8,
    rollback_threshold: []const u8,
    blocked_gap_id: []const u8,
    next_step_posture: []const u8,
    required_evidence: []const []const u8,
    automatic_return_to_blocked_triggers: []const []const u8,
};

pub const DecisionChecklistEntry = struct {
    id: []const u8,
    summary: []const u8,
    ownership: Ownership,
    anchor_symbols: []const []const u8,
    rationale: []const u8,
};

const boundary_areas = [_]BoundaryArea{
    .{
        .id = "allocation-entrypoints",
        .summary = "Record the main skb allocation entrypoints without claiming allocator or cache ownership.",
        .ownership = .boundary_map_only,
        .anchor_symbols = &[_][]const u8{ "__alloc_skb", "napi_alloc_skb", "build_skb" },
        .rationale = "The first honest skbuff foothold is to name where callers enter the allocation surface, while leaving the slab, page-frag, NAPI, and truesize accounting machinery in C.",
    },
    .{
        .id = "clone-and-private-copy",
        .summary = "Map clone and private-copy helpers as reviewable wrapper candidates only.",
        .ownership = .boundary_map_only,
        .anchor_symbols = &[_][]const u8{ "skb_clone", "skb_copy", "__pskb_copy_fclone" },
        .rationale = "Clone and copy entrypoints are visible seams for future wrapper discussion, but the real behavior still depends on skb_shared_info.dataref, headerless skb rules, and frag ownership that should remain in C.",
    },
    .{
        .id = "headroom-and-linearization-mutation",
        .summary = "Capture headroom growth and in-header carve paths as mutation seams, not live rewrite candidates.",
        .ownership = .boundary_map_only,
        .anchor_symbols = &[_][]const u8{ "pskb_expand_head", "skb_copy_expand", "pskb_carve_inside_header" },
        .rationale = "These helpers mutate skb geometry and copy state across shared heads, so Phase 14 should record their boundary without pretending Zig now owns the mutation path.",
    },
    .{
        .id = "checksum-and-segmentation-surface",
        .summary = "Document checksum completion and segmentation as metadata-heavy boundaries before any wrapper claim touches them.",
        .ownership = .boundary_map_only,
        .anchor_symbols = &[_][]const u8{ "__skb_checksum_complete", "skb_segment" },
        .rationale = "Checksum and segmentation are caller-visible surfaces, but they are tightly coupled to csum metadata, frag layout, and GSO bookkeeping that should stay in the existing C implementation for now.",
    },
    .{
        .id = "shared-info-refcount-ownership",
        .summary = "Keep skb_shared_info refcount splits and header-write eligibility explicitly in C.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "struct skb_shared_info", "dataref", "skb_header_cloned" },
        .rationale = "The split dataref model and header-clone rules decide whether headers may be mutated at all, so they are core ownership logic rather than a safe Phase 14 wrapper target.",
    },
    .{
        .id = "destructor-and-free-path",
        .summary = "Keep destructor callbacks and final release ordering explicitly in C.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "skb_release_head_state", "skb_release_data", "consume_skb" },
        .rationale = "Teardown crosses destructor callbacks, destructor_arg payloads, frag lists, and final consume or free paths, which is exactly the kind of lifetime ownership Phase 14 should record and leave in C.",
    },
};

const audit_checkpoints = [_]AuditCheckpoint{
    .{
        .id = "dataref-header-write-split",
        .anchor_symbol = "skb_cloned/skb_header_cloned",
        .summary = "Record that header writes are blocked until shared-data ownership collapses to a private head.",
        .guard = .header_write_requires_private_data,
        .observed_fields = &[_][]const u8{ "skb->cloned", "skb_shinfo(skb)->dataref", "skb->hdr_len" },
        .blocked_by = "The split dataref model and headerless skb rules decide whether the header may be written at all, so Zigux should audit that ownership boundary rather than claim a live clone or mutate wrapper.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "clone-before-expand-mutation",
        .anchor_symbol = "pskb_expand_head",
        .summary = "Track the clone-or-reallocate handoff before headroom mutation touches shared data.",
        .guard = .clone_or_reallocate_before_mutation,
        .observed_fields = &[_][]const u8{ "skb->cloned", "skb_shinfo(skb)->dataref", "skb_shinfo(skb)->frag_list" },
        .blocked_by = "pskb_expand_head() conditionally clones frag lists, releases old shared data, and rewrites skb geometry, so Phase 14 should keep the mutation handoff in C while only naming the checkpoint.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "destructor-before-data-release",
        .anchor_symbol = "skb_release_head_state/skb_release_data",
        .summary = "Capture destructor callbacks and frag-list release ordering before final consume or free paths run.",
        .guard = .destructor_before_frag_release,
        .observed_fields = &[_][]const u8{ "skb->destructor", "skb_shinfo(skb)->destructor_arg", "skb_shinfo(skb)->frag_list" },
        .blocked_by = "The release path can run destructor callbacks, detach socket state, and then free frags or frag lists, so Zigux should keep that teardown ordering in C rather than pretend it already owns skb lifetime.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "checksum-complete-state-cache",
        .anchor_symbol = "__skb_checksum_complete/skb_checksum_complete_unset",
        .summary = "Keep checksum-complete caching and invalidation tied to skb-owned state fields.",
        .guard = .checksum_complete_state_cache,
        .observed_fields = &[_][]const u8{ "skb->csum", "skb->ip_summed", "skb->csum_valid", "skb->csum_complete_sw" },
        .blocked_by = "__skb_checksum_complete() stores checksum state back into the skb when it is not shared, and skb_checksum_complete_unset() invalidates that cache after packet mutation, so Zigux should record the ownership boundary without claiming live checksum-state control.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "segmentation-orphan-and-zerocopy-handoff",
        .anchor_symbol = "skb_segment/skb_orphan_frags/skb_zerocopy_clone",
        .summary = "Track the orphan-frag gate and zerocopy carryover before segmented outputs reuse page-backed payload state.",
        .guard = .segmentation_orphan_and_zerocopy_handoff,
        .observed_fields = &[_][]const u8{ "skb_shinfo(head_skb)->frag_list", "skb_shinfo(head_skb)->flags", "skb_shinfo(nskb)->flags", "skb_shinfo(nskb)->nr_frags" },
        .blocked_by = "skb_segment() first forces skb_orphan_frags(head_skb, GFP_ATOMIC) for zerocopy-backed input, then propagates SKBFL_SHARED_FRAG state and calls skb_zerocopy_clone() across frag_skb and frag_list members, so Zigux should keep that frag-ownership transfer in C while only naming the boundary.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "segmentation-checksum-metadata-handoff",
        .anchor_symbol = "skb_segment/SKB_GSO_CB",
        .summary = "Record where segmented outputs reset or recompute checksum metadata as GSO state moves onto each new skb.",
        .guard = .segmentation_checksum_metadata_handoff,
        .observed_fields = &[_][]const u8{ "nskb->remcsum_offload", "nskb->ip_summed", "SKB_GSO_CB(nskb)->csum", "SKB_GSO_CB(nskb)->csum_start", "skb_shinfo(head_skb)->gso_size" },
        .blocked_by = "skb_segment() can clear ip_summed to CHECKSUM_NONE, copy checksum bytes through skb_copy_and_csum_bits(), or recompute checksum state through skb_checksum() before it seeds SKB_GSO_CB(nskb), so Zigux should keep checksum and GSO metadata ownership in C while only recording the handoff.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "segmentation-partial-tail-owner-transfer",
        .anchor_symbol = "skb_segment/SKB_GSO_PARTIAL/sock_wfree",
        .summary = "Track partial-GSO metadata rewrites and the final sock-owned tail transfer before segmented output ownership leaves the bridge study boundary.",
        .guard = .segmentation_partial_tail_owner_transfer,
        .observed_fields = &[_][]const u8{
            "skb_shinfo(iter)->gso_size",
            "skb_shinfo(iter)->gso_segs",
            "skb_shinfo(iter)->gso_type",
            "SKB_GSO_CB(iter)->data_offset",
            "tail->truesize",
            "tail->destructor",
            "tail->sk",
        },
        .blocked_by = "skb_segment() promotes NETIF_F_GSO_PARTIAL into SKB_GSO_PARTIAL, clears SKB_GSO_DODGY, rewrites each segment's gso_size, gso_segs, gso_type, and SKB_GSO_CB(iter)->data_offset, then transfers sock-owned backpressure state by swapping the tail skb truesize, destructor, and sk with head_skb when head_skb->destructor == sock_wfree, so Zigux should keep both the partial-seg metadata path and the tail-owner transfer in C while only naming the handoff.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "segmentation-checksum-data-offset-crossover",
        .anchor_symbol = "skb_segment/SKB_GSO_CB/remcsum_offload",
        .summary = "Track the checksum-to-data-offset crossover that seeds each output skb before later tail publication.",
        .guard = .segmentation_checksum_data_offset_crossover,
        .observed_fields = &[_][]const u8{
            "SKB_GSO_CB(nskb)->csum",
            "SKB_GSO_CB(nskb)->csum_start",
            "SKB_GSO_CB(iter)->data_offset",
            "remcsum_offload",
            "segs->prev",
        },
        .blocked_by = "skb_segment() carries checksum state forward by seeding SKB_GSO_CB(nskb)->csum and SKB_GSO_CB(nskb)->csum_start, rewrites SKB_GSO_CB(iter)->data_offset as the remaining bytes shrink, and only later publishes the tail chain through segs->prev with remcsum_offload in play, so Zigux should keep this checksum-to-publication crossover in C while only recording the boundary.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "segmentation-tail-publication-consumer-contract",
        .anchor_symbol = "skb_segment/segs->prev/validate_xmit_skb_list",
        .summary = "Record the exported tail-list publication contract before segmented output leaves skb_segment() for xmit-list consumers.",
        .guard = .segmentation_tail_publication_consumer_contract,
        .observed_fields = &[_][]const u8{
            "segs->prev",
            "tail->next",
            "skb_shinfo(tail)->gso_size",
            "skb_shinfo(tail)->gso_segs",
            "validate_xmit_skb_list()",
        },
        .blocked_by = "skb_segment() only publishes the accumulated list tail after wiring segs->prev and finalizing the last segment's gso_size or gso_segs clamp, then hands that exported list to validate_xmit_skb_list() under the existing qdisc and xmit ownership model, so Zigux should keep tail publication and downstream consumer coordination in C while only recording the contract.",
        .ownership = .stay_in_c,
    },
};

const decision_checklist = [_]DecisionChecklistEntry{
    .{
        .id = boundary_areas[4].id,
        .summary = boundary_areas[4].summary,
        .ownership = boundary_areas[4].ownership,
        .anchor_symbols = boundary_areas[4].anchor_symbols,
        .rationale = boundary_areas[4].rationale,
    },
    .{
        .id = boundary_areas[5].id,
        .summary = boundary_areas[5].summary,
        .ownership = boundary_areas[5].ownership,
        .anchor_symbols = boundary_areas[5].anchor_symbols,
        .rationale = boundary_areas[5].rationale,
    },
    .{
        .id = audit_checkpoints[6].id,
        .summary = audit_checkpoints[6].summary,
        .ownership = audit_checkpoints[6].ownership,
        .anchor_symbols = &[_][]const u8{ "skb_segment", "SKB_GSO_PARTIAL", "sock_wfree" },
        .rationale = audit_checkpoints[6].blocked_by,
    },
    .{
        .id = audit_checkpoints[7].id,
        .summary = audit_checkpoints[7].summary,
        .ownership = audit_checkpoints[7].ownership,
        .anchor_symbols = &[_][]const u8{ "skb_segment", "SKB_GSO_CB", "remcsum_offload" },
        .rationale = audit_checkpoints[7].blocked_by,
    },
    .{
        .id = audit_checkpoints[8].id,
        .summary = audit_checkpoints[8].summary,
        .ownership = audit_checkpoints[8].ownership,
        .anchor_symbols = &[_][]const u8{ "skb_segment", "segs->prev", "validate_xmit_skb_list" },
        .rationale = audit_checkpoints[8].blocked_by,
    },
};

const roadmap_boundary_study_area_ids = [_][]const u8{
    "allocation-entrypoints",
    "clone-and-private-copy",
    "headroom-and-linearization-mutation",
    "checksum-and-segmentation-surface",
};

const stay_in_c_boundary_area_ids = [_][]const u8{
    "shared-info-refcount-ownership",
    "destructor-and-free-path",
};

const blocked_live_behaviors = [_][]const u8{
    "live skbuff allocation and cache ownership",
    "shared-data refcount transitions",
    "destructor callback and frag-list teardown",
    "checksum-complete state transitions",
    "segmentation orphan-frag and zerocopy ownership handoff",
    "segmentation checksum metadata recompute and GSO handoff",
    "segmentation partial-seg metadata and tail-owner transfer",
    "segmentation checksum and data-offset crossover before tail publication",
    "segmentation tail-list publication and validate_xmit_skb_list consumer coordination",
};

const concurrency_sensitive_checkpoint_ids = [_][]const u8{
    "segmentation-partial-tail-owner-transfer",
    "segmentation-checksum-data-offset-crossover",
    "segmentation-tail-publication-consumer-contract",
};

const concurrency_sensitive_blocked_behaviors = [_][]const u8{
    "segmentation partial-seg metadata and tail-owner transfer",
    "segmentation checksum and data-offset crossover before tail publication",
    "segmentation tail-list publication and validate_xmit_skb_list consumer coordination",
};

const freeze_required_evidence = [_][]const u8{
    "explicit stay-in-C wording for `segs->prev`, `tail->next`, and `validate_xmit_skb_list()`",
    "the blocked `phase14-skbuff-live-ownership-blocker` kept visible beside the no-smaller-follow-up posture",
    "explicit wording that qdisc-facing publication, queue ownership, skb lifetime ownership, checksum ownership, and destructor coordination remain in C",
};

const freeze_return_to_blocked_triggers = [_][]const u8{
    "any edit that drops the named validation gate or rollback owner",
    "missing freeze-in-C or stay-in-C wording for the exported tail-publication checkpoint",
    "any manifest refresh that changes the blocked live-ownership gap without refreshing this survey note",
    "any edit that weakens the explicit no-smaller-follow-up stance and silently implies a fresh skbuff wrapper step",
};

pub const SkbuffBridgeLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "skbuff_boundary_map_lab",
            .anchor = "net/core/skbuff.c",
            .posture = "boundary_map_only",
            .provides_boundary_map = true,
            .provides_lifetime_audit_outline = true,
            .provides_stay_in_c_decisions = true,
            .touches_live_allocators = false,
            .touches_live_refcounts = false,
            .touches_live_destructors = false,
        };
    }

    pub fn boundaryMap() BoundaryMap {
        return .{
            .anchor = descriptor().anchor,
            .posture = descriptor().posture,
            .areas = boundary_areas[0..],
        };
    }

    pub fn lifetimeAudit() LifetimeAudit {
        return .{
            .anchor = descriptor().anchor,
            .posture = descriptor().posture,
            .checkpoints = audit_checkpoints[0..],
            .blocked_live_behaviors = blocked_live_behaviors[0..],
            .next_step = nextAuditFocus(),
        };
    }

    pub fn freezeGuardrail() FreezeGuardrail {
        return .{
            .anchor = descriptor().anchor,
            .status_bucket = "freeze_in_c",
            .named_owner = "Core-Adjacent Pod",
            .validation_gate = "zig build test --build-file zigux/tests/phase14_build.zig --summary all plus make -C zigux phase14",
            .rollback_owner = "Repo Tooling Pod",
            .rollback_threshold = "keep this packet in freeze_in_c posture and return it to blocked skbuff-packet maintenance if the validation gate, rollback owner, blocked live-ownership gap, or explicit stay-in-C wording around qdisc-facing publication stops being visible in the same survey packet.",
            .blocked_gap_id = "phase14-skbuff-live-ownership-blocker",
            .next_step_posture = nextAuditFocus(),
            .required_evidence = freeze_required_evidence[0..],
            .automatic_return_to_blocked_triggers = freeze_return_to_blocked_triggers[0..],
        };
    }

    pub fn decisionChecklist() []const DecisionChecklistEntry {
        return decision_checklist[0..];
    }

    pub fn decisionChecklistCount() usize {
        return decision_checklist.len;
    }

    pub fn decisionChecklistEntryById(id: []const u8) ?DecisionChecklistEntry {
        for (decision_checklist) |entry| {
            if (std.mem.eql(u8, entry.id, id)) {
                return entry;
            }
        }
        return null;
    }

    pub fn boundaryAreaCount() usize {
        return boundary_areas.len;
    }

    pub fn boundaryAreaById(id: []const u8) ?BoundaryArea {
        for (boundary_areas) |area| {
            if (std.mem.eql(u8, area.id, id)) {
                return area;
            }
        }
        return null;
    }

    pub fn roadmapBoundaryStudyAreaIds() []const []const u8 {
        return roadmap_boundary_study_area_ids[0..];
    }

    pub fn roadmapBoundaryStudyAreaCount() usize {
        return roadmap_boundary_study_area_ids.len;
    }

    pub fn isRoadmapBoundaryStudyArea(id: []const u8) bool {
        for (roadmap_boundary_study_area_ids) |area_id| {
            if (std.mem.eql(u8, area_id, id)) {
                return true;
            }
        }
        return false;
    }

    pub fn stayInCBoundaryAreaIds() []const []const u8 {
        return stay_in_c_boundary_area_ids[0..];
    }

    pub fn stayInCBoundaryAreaCount() usize {
        return stay_in_c_boundary_area_ids.len;
    }

    pub fn isStayInCBoundaryArea(id: []const u8) bool {
        for (stay_in_c_boundary_area_ids) |area_id| {
            if (std.mem.eql(u8, area_id, id)) {
                return true;
            }
        }
        return false;
    }

    pub fn stayInCDecisionCount() usize {
        var count: usize = 0;
        for (boundary_areas) |area| {
            if (area.ownership == .stay_in_c) {
                count += 1;
            }
        }
        return count;
    }

    pub fn auditCheckpointCount() usize {
        return audit_checkpoints.len;
    }

    pub fn checkpointById(id: []const u8) ?AuditCheckpoint {
        for (audit_checkpoints) |checkpoint| {
            if (std.mem.eql(u8, checkpoint.id, id)) {
                return checkpoint;
            }
        }
        return null;
    }

    pub fn hasAuditGuard(guard: AuditGuard) bool {
        for (audit_checkpoints) |checkpoint| {
            if (checkpoint.guard == guard) {
                return true;
            }
        }
        return false;
    }

    pub fn blockedBehaviorIndex(behavior: []const u8) ?usize {
        for (blocked_live_behaviors, 0..) |blocked_behavior, index| {
            if (std.mem.eql(u8, blocked_behavior, behavior)) {
                return index;
            }
        }
        return null;
    }

    pub fn blocksLiveBehavior(behavior: []const u8) bool {
        return blockedBehaviorIndex(behavior) != null;
    }

    pub fn concurrencySensitiveCheckpointIds() []const []const u8 {
        return concurrency_sensitive_checkpoint_ids[0..];
    }

    pub fn concurrencySensitiveCheckpointCount() usize {
        return concurrency_sensitive_checkpoint_ids.len;
    }

    pub fn isConcurrencySensitiveCheckpoint(id: []const u8) bool {
        for (concurrency_sensitive_checkpoint_ids) |checkpoint_id| {
            if (std.mem.eql(u8, checkpoint_id, id)) {
                return true;
            }
        }
        return false;
    }

    pub fn concurrencySensitiveBlockedBehaviors() []const []const u8 {
        return concurrency_sensitive_blocked_behaviors[0..];
    }

    pub fn freezeCriticalChecklistCoverageCount() usize {
        var count: usize = 0;
        for (concurrency_sensitive_checkpoint_ids) |checkpoint_id| {
            if (decisionChecklistEntryById(checkpoint_id) != null) {
                count += 1;
            }
        }
        return count;
    }

    pub fn hasFullFreezeCriticalChecklistCoverage() bool {
        return freezeCriticalChecklistCoverageCount() == concurrency_sensitive_checkpoint_ids.len;
    }

    pub fn freezeCriticalBlockedBehaviorCoverageCount() usize {
        var count: usize = 0;
        for (concurrency_sensitive_blocked_behaviors) |behavior| {
            if (blocksLiveBehavior(behavior)) {
                count += 1;
            }
        }
        return count;
    }

    pub fn hasFullFreezeCriticalBlockedBehaviorCoverage() bool {
        return freezeCriticalBlockedBehaviorCoverageCount() == concurrency_sensitive_blocked_behaviors.len;
    }

    pub fn requiredFreezeEvidenceCount() usize {
        return freeze_required_evidence.len;
    }

    pub fn hasRequiredFreezeEvidence(evidence: []const u8) bool {
        for (freeze_required_evidence) |required_evidence| {
            if (std.mem.eql(u8, required_evidence, evidence)) {
                return true;
            }
        }
        return false;
    }

    pub fn automaticReturnToBlockedTriggerCount() usize {
        return freeze_return_to_blocked_triggers.len;
    }

    pub fn hasAutomaticReturnToBlockedTrigger(trigger: []const u8) bool {
        for (freeze_return_to_blocked_triggers) |blocked_trigger| {
            if (std.mem.eql(u8, blocked_trigger, trigger)) {
                return true;
            }
        }
        return false;
    }

    pub fn nextAuditFocus() []const u8 {
        return "No smaller review-only skbuff checkpoint remains after the exported tail-publication audit; keep live allocation, dataref, checksum, segmentation, qdisc publication, and destructor ownership in C until stronger stay-in-C evidence exists.";
    }
};

test "skbuff bridge descriptor stays boundary-map only" {
    const descriptor = SkbuffBridgeLab.descriptor();

    try std.testing.expectEqualStrings("skbuff_boundary_map_lab", descriptor.name);
    try std.testing.expectEqualStrings("net/core/skbuff.c", descriptor.anchor);
    try std.testing.expectEqualStrings("boundary_map_only", descriptor.posture);
    try std.testing.expect(descriptor.provides_boundary_map);
    try std.testing.expect(descriptor.provides_lifetime_audit_outline);
    try std.testing.expect(descriptor.provides_stay_in_c_decisions);
    try std.testing.expect(!descriptor.touches_live_allocators);
    try std.testing.expect(!descriptor.touches_live_refcounts);
    try std.testing.expect(!descriptor.touches_live_destructors);
}

test "skbuff bridge boundary map records stay-in-c lifetime decisions" {
    const map = SkbuffBridgeLab.boundaryMap();

    try std.testing.expectEqualStrings("net/core/skbuff.c", map.anchor);
    try std.testing.expectEqualStrings("boundary_map_only", map.posture);
    try std.testing.expectEqual(@as(usize, 6), map.areas.len);
    try std.testing.expectEqual(@as(usize, 6), SkbuffBridgeLab.boundaryAreaCount());
    try std.testing.expectEqual(@as(usize, 2), SkbuffBridgeLab.stayInCDecisionCount());
    try std.testing.expect(std.mem.indexOf(u8, SkbuffBridgeLab.nextAuditFocus(), "qdisc publication") != null);
    try std.testing.expect(std.mem.indexOf(u8, SkbuffBridgeLab.nextAuditFocus(), "stay-in-C evidence") != null);

    try std.testing.expectEqualStrings("allocation-entrypoints", map.areas[0].id);
    try std.testing.expect(map.areas[0].ownership == .boundary_map_only);
    try std.testing.expectEqualStrings("__alloc_skb", map.areas[0].anchor_symbols[0]);
    try std.testing.expectEqualStrings("napi_alloc_skb", map.areas[0].anchor_symbols[1]);

    try std.testing.expectEqualStrings("shared-info-refcount-ownership", map.areas[4].id);
    try std.testing.expect(map.areas[4].ownership == .stay_in_c);
    try std.testing.expect(std.mem.indexOf(u8, map.areas[4].rationale, "dataref") != null);

    try std.testing.expectEqualStrings("destructor-and-free-path", map.areas[5].id);
    try std.testing.expect(map.areas[5].ownership == .stay_in_c);
    try std.testing.expectEqualStrings("consume_skb", map.areas[5].anchor_symbols[2]);
}

test "skbuff bridge decision checklist exposes the stay-in-c review packet" {
    const checklist = SkbuffBridgeLab.decisionChecklist();

    try std.testing.expectEqual(@as(usize, 5), checklist.len);
    try std.testing.expectEqual(@as(usize, 5), SkbuffBridgeLab.decisionChecklistCount());

    const refcount = SkbuffBridgeLab.decisionChecklistEntryById("shared-info-refcount-ownership") orelse return error.MissingChecklistEntry;
    try std.testing.expect(refcount.ownership == .stay_in_c);
    try std.testing.expectEqualStrings(boundary_areas[4].summary, refcount.summary);
    try std.testing.expectEqualStrings("struct skb_shared_info", refcount.anchor_symbols[0]);
    try std.testing.expectEqualStrings("dataref", refcount.anchor_symbols[1]);
    try std.testing.expectEqualStrings("skb_header_cloned", refcount.anchor_symbols[2]);

    const tail_owner = SkbuffBridgeLab.decisionChecklistEntryById("segmentation-partial-tail-owner-transfer") orelse return error.MissingChecklistEntry;
    try std.testing.expect(tail_owner.ownership == .stay_in_c);
    try std.testing.expectEqualStrings(audit_checkpoints[6].summary, tail_owner.summary);
    try std.testing.expectEqualStrings("skb_segment", tail_owner.anchor_symbols[0]);
    try std.testing.expectEqualStrings("SKB_GSO_PARTIAL", tail_owner.anchor_symbols[1]);
    try std.testing.expectEqualStrings("sock_wfree", tail_owner.anchor_symbols[2]);

    const tail_publication = SkbuffBridgeLab.decisionChecklistEntryById("segmentation-tail-publication-consumer-contract") orelse return error.MissingChecklistEntry;
    try std.testing.expectEqualStrings(audit_checkpoints[8].blocked_by, tail_publication.rationale);
    try std.testing.expectEqualStrings("segs->prev", tail_publication.anchor_symbols[1]);
    try std.testing.expectEqualStrings("validate_xmit_skb_list", tail_publication.anchor_symbols[2]);

    try std.testing.expect(SkbuffBridgeLab.decisionChecklistEntryById("missing-checklist-entry") == null);
}

test "skbuff bridge roadmap boundary-study helpers stay aligned" {
    try std.testing.expectEqual(@as(usize, 4), SkbuffBridgeLab.roadmapBoundaryStudyAreaCount());
    try std.testing.expectEqual(@as(usize, 4), SkbuffBridgeLab.roadmapBoundaryStudyAreaIds().len);
    try std.testing.expectEqual(@as(usize, 2), SkbuffBridgeLab.stayInCBoundaryAreaCount());
    try std.testing.expectEqual(@as(usize, 2), SkbuffBridgeLab.stayInCBoundaryAreaIds().len);

    for (SkbuffBridgeLab.roadmapBoundaryStudyAreaIds()) |area_id| {
        const area = SkbuffBridgeLab.boundaryAreaById(area_id) orelse return error.MissingBoundaryArea;
        try std.testing.expect(area.ownership == .boundary_map_only);
        try std.testing.expect(SkbuffBridgeLab.isRoadmapBoundaryStudyArea(area_id));
        try std.testing.expect(!SkbuffBridgeLab.isStayInCBoundaryArea(area_id));
    }

    for (SkbuffBridgeLab.stayInCBoundaryAreaIds()) |area_id| {
        const area = SkbuffBridgeLab.boundaryAreaById(area_id) orelse return error.MissingBoundaryArea;
        try std.testing.expect(area.ownership == .stay_in_c);
        try std.testing.expect(SkbuffBridgeLab.isStayInCBoundaryArea(area_id));
        try std.testing.expect(!SkbuffBridgeLab.isRoadmapBoundaryStudyArea(area_id));
    }

    const checksum_surface = SkbuffBridgeLab.boundaryAreaById("checksum-and-segmentation-surface") orelse return error.MissingBoundaryArea;
    try std.testing.expectEqualStrings("__skb_checksum_complete", checksum_surface.anchor_symbols[0]);
    try std.testing.expectEqualStrings("skb_segment", checksum_surface.anchor_symbols[1]);
    try std.testing.expect(std.mem.indexOf(u8, checksum_surface.rationale, "GSO bookkeeping") != null);

    try std.testing.expect(SkbuffBridgeLab.boundaryAreaById("missing-boundary-area") == null);
    try std.testing.expect(!SkbuffBridgeLab.isRoadmapBoundaryStudyArea("segmentation-tail-publication-consumer-contract"));
    try std.testing.expect(!SkbuffBridgeLab.isStayInCBoundaryArea("allocation-entrypoints"));
}

test "skbuff bridge lifetime audit stays review-only" {
    const audit = SkbuffBridgeLab.lifetimeAudit();

    try std.testing.expectEqualStrings("net/core/skbuff.c", audit.anchor);
    try std.testing.expectEqualStrings("boundary_map_only", audit.posture);
    try std.testing.expectEqual(@as(usize, 9), audit.checkpoints.len);
    try std.testing.expectEqual(@as(usize, 9), audit.blocked_live_behaviors.len);
    try std.testing.expectEqual(@as(usize, 9), SkbuffBridgeLab.auditCheckpointCount());
    try std.testing.expect(std.mem.indexOf(u8, audit.next_step, "qdisc publication") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.next_step, "stay-in-C evidence") != null);

    try std.testing.expectEqualStrings("dataref-header-write-split", audit.checkpoints[0].id);
    try std.testing.expect(audit.checkpoints[0].guard == .header_write_requires_private_data);
    try std.testing.expectEqualStrings("skb->hdr_len", audit.checkpoints[0].observed_fields[2]);

    try std.testing.expectEqualStrings("clone-before-expand-mutation", audit.checkpoints[1].id);
    try std.testing.expect(audit.checkpoints[1].guard == .clone_or_reallocate_before_mutation);
    try std.testing.expectEqualStrings("skb_shinfo(skb)->frag_list", audit.checkpoints[1].observed_fields[2]);

    try std.testing.expectEqualStrings("destructor-before-data-release", audit.checkpoints[2].id);
    try std.testing.expect(audit.checkpoints[2].guard == .destructor_before_frag_release);
    try std.testing.expectEqualStrings("skb_shinfo(skb)->destructor_arg", audit.checkpoints[2].observed_fields[1]);

    try std.testing.expectEqualStrings("checksum-complete-state-cache", audit.checkpoints[3].id);
    try std.testing.expect(audit.checkpoints[3].guard == .checksum_complete_state_cache);
    try std.testing.expectEqualStrings("skb->csum_complete_sw", audit.checkpoints[3].observed_fields[3]);

    const orphan_handoff = SkbuffBridgeLab.checkpointById("segmentation-orphan-and-zerocopy-handoff") orelse return error.MissingCheckpoint;
    try std.testing.expect(orphan_handoff.guard == .segmentation_orphan_and_zerocopy_handoff);
    try std.testing.expectEqualStrings("skb_shinfo(nskb)->nr_frags", orphan_handoff.observed_fields[3]);
    try std.testing.expect(std.mem.indexOf(u8, orphan_handoff.blocked_by, "skb_orphan_frags(head_skb, GFP_ATOMIC)") != null);
    try std.testing.expect(std.mem.indexOf(u8, orphan_handoff.blocked_by, "SKBFL_SHARED_FRAG") != null);

    const checksum_handoff = SkbuffBridgeLab.checkpointById("segmentation-checksum-metadata-handoff") orelse return error.MissingCheckpoint;
    try std.testing.expect(checksum_handoff.guard == .segmentation_checksum_metadata_handoff);
    try std.testing.expectEqualStrings("SKB_GSO_CB(nskb)->csum_start", checksum_handoff.observed_fields[3]);
    try std.testing.expect(std.mem.indexOf(u8, checksum_handoff.blocked_by, "CHECKSUM_NONE") != null);
    try std.testing.expect(std.mem.indexOf(u8, checksum_handoff.blocked_by, "skb_checksum()") != null);

    const tail_owner = SkbuffBridgeLab.checkpointById("segmentation-partial-tail-owner-transfer") orelse return error.MissingCheckpoint;
    try std.testing.expect(tail_owner.guard == .segmentation_partial_tail_owner_transfer);
    try std.testing.expectEqualStrings("SKB_GSO_CB(iter)->data_offset", tail_owner.observed_fields[3]);
    try std.testing.expect(std.mem.indexOf(u8, tail_owner.blocked_by, "SKB_GSO_PARTIAL") != null);
    try std.testing.expect(std.mem.indexOf(u8, tail_owner.blocked_by, "sock_wfree") != null);

    const checksum_crossover = SkbuffBridgeLab.checkpointById("segmentation-checksum-data-offset-crossover") orelse return error.MissingCheckpoint;
    try std.testing.expect(checksum_crossover.guard == .segmentation_checksum_data_offset_crossover);
    try std.testing.expectEqualStrings("remcsum_offload", checksum_crossover.observed_fields[3]);
    try std.testing.expectEqualStrings("segs->prev", checksum_crossover.observed_fields[4]);
    try std.testing.expect(std.mem.indexOf(u8, checksum_crossover.blocked_by, "SKB_GSO_CB(nskb)->csum") != null);
    try std.testing.expect(std.mem.indexOf(u8, checksum_crossover.blocked_by, "tail chain") != null);

    const tail_publication = SkbuffBridgeLab.checkpointById("segmentation-tail-publication-consumer-contract") orelse return error.MissingCheckpoint;
    try std.testing.expect(tail_publication.guard == .segmentation_tail_publication_consumer_contract);
    try std.testing.expectEqualStrings("skb_shinfo(tail)->gso_size", tail_publication.observed_fields[2]);
    try std.testing.expectEqualStrings("validate_xmit_skb_list()", tail_publication.observed_fields[4]);
    try std.testing.expect(std.mem.indexOf(u8, tail_publication.blocked_by, "segs->prev") != null);
    try std.testing.expect(std.mem.indexOf(u8, tail_publication.blocked_by, "qdisc and xmit ownership model") != null);
}

test "skbuff bridge concurrency-sensitive checkpoint catalog stays anchored to the publication boundary" {
    try std.testing.expectEqual(@as(usize, 3), SkbuffBridgeLab.concurrencySensitiveCheckpointCount());
    try std.testing.expectEqual(@as(usize, 3), SkbuffBridgeLab.concurrencySensitiveCheckpointIds().len);
    try std.testing.expectEqual(@as(usize, 3), SkbuffBridgeLab.concurrencySensitiveBlockedBehaviors().len);
    try std.testing.expectEqual(@as(usize, 3), SkbuffBridgeLab.freezeCriticalChecklistCoverageCount());
    try std.testing.expect(SkbuffBridgeLab.hasFullFreezeCriticalChecklistCoverage());
    try std.testing.expectEqual(@as(usize, 3), SkbuffBridgeLab.freezeCriticalBlockedBehaviorCoverageCount());
    try std.testing.expect(SkbuffBridgeLab.hasFullFreezeCriticalBlockedBehaviorCoverage());

    for (SkbuffBridgeLab.concurrencySensitiveCheckpointIds()) |checkpoint_id| {
        const checkpoint = SkbuffBridgeLab.checkpointById(checkpoint_id) orelse return error.MissingCheckpoint;
        const checklist_entry = SkbuffBridgeLab.decisionChecklistEntryById(checkpoint_id) orelse return error.MissingChecklistEntry;
        try std.testing.expect(checkpoint.ownership == .stay_in_c);
        try std.testing.expect(SkbuffBridgeLab.isConcurrencySensitiveCheckpoint(checkpoint_id));
        try std.testing.expectEqualStrings(checkpoint.summary, checklist_entry.summary);
        try std.testing.expectEqualStrings(checkpoint.blocked_by, checklist_entry.rationale);
    }

    const tail_owner = SkbuffBridgeLab.checkpointById("segmentation-partial-tail-owner-transfer") orelse return error.MissingCheckpoint;
    try std.testing.expect(tail_owner.guard == .segmentation_partial_tail_owner_transfer);

    const checksum_crossover = SkbuffBridgeLab.checkpointById("segmentation-checksum-data-offset-crossover") orelse return error.MissingCheckpoint;
    try std.testing.expect(checksum_crossover.guard == .segmentation_checksum_data_offset_crossover);

    const tail_publication = SkbuffBridgeLab.checkpointById("segmentation-tail-publication-consumer-contract") orelse return error.MissingCheckpoint;
    try std.testing.expect(tail_publication.guard == .segmentation_tail_publication_consumer_contract);

    for (SkbuffBridgeLab.concurrencySensitiveBlockedBehaviors()) |behavior| {
        try std.testing.expect(SkbuffBridgeLab.blocksLiveBehavior(behavior));
    }

    try std.testing.expect(!SkbuffBridgeLab.isConcurrencySensitiveCheckpoint("checksum-complete-state-cache"));
}

test "skbuff bridge freeze guardrail stays machine-checkable" {
    const guardrail = SkbuffBridgeLab.freezeGuardrail();

    try std.testing.expectEqualStrings("net/core/skbuff.c", guardrail.anchor);
    try std.testing.expectEqualStrings("freeze_in_c", guardrail.status_bucket);
    try std.testing.expectEqualStrings("Core-Adjacent Pod", guardrail.named_owner);
    try std.testing.expectEqualStrings("Repo Tooling Pod", guardrail.rollback_owner);
    try std.testing.expectEqualStrings("phase14-skbuff-live-ownership-blocker", guardrail.blocked_gap_id);
    try std.testing.expect(std.mem.indexOf(u8, guardrail.validation_gate, "zigux/tests/phase14_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, guardrail.validation_gate, "make -C zigux phase14") != null);
    try std.testing.expect(std.mem.indexOf(u8, guardrail.rollback_threshold, "freeze_in_c posture") != null);
    try std.testing.expect(std.mem.indexOf(u8, guardrail.rollback_threshold, "qdisc-facing publication") != null);
    try std.testing.expect(std.mem.indexOf(u8, guardrail.next_step_posture, "No smaller review-only skbuff checkpoint remains") != null);
    try std.testing.expectEqual(@as(usize, 3), guardrail.required_evidence.len);
    try std.testing.expectEqual(@as(usize, 4), guardrail.automatic_return_to_blocked_triggers.len);
    try std.testing.expectEqual(@as(usize, 3), SkbuffBridgeLab.requiredFreezeEvidenceCount());
    try std.testing.expectEqual(@as(usize, 4), SkbuffBridgeLab.automaticReturnToBlockedTriggerCount());
    try std.testing.expect(SkbuffBridgeLab.hasRequiredFreezeEvidence("explicit stay-in-C wording for `segs->prev`, `tail->next`, and `validate_xmit_skb_list()`"));
    try std.testing.expect(SkbuffBridgeLab.hasRequiredFreezeEvidence("the blocked `phase14-skbuff-live-ownership-blocker` kept visible beside the no-smaller-follow-up posture"));
    try std.testing.expect(SkbuffBridgeLab.hasRequiredFreezeEvidence("explicit wording that qdisc-facing publication, queue ownership, skb lifetime ownership, checksum ownership, and destructor coordination remain in C"));
    try std.testing.expect(SkbuffBridgeLab.hasAutomaticReturnToBlockedTrigger("any edit that drops the named validation gate or rollback owner"));
    try std.testing.expect(SkbuffBridgeLab.hasAutomaticReturnToBlockedTrigger("missing freeze-in-C or stay-in-C wording for the exported tail-publication checkpoint"));
    try std.testing.expect(SkbuffBridgeLab.hasAutomaticReturnToBlockedTrigger("any manifest refresh that changes the blocked live-ownership gap without refreshing this survey note"));
    try std.testing.expect(SkbuffBridgeLab.hasAutomaticReturnToBlockedTrigger("any edit that weakens the explicit no-smaller-follow-up stance and silently implies a fresh skbuff wrapper step"));
    try std.testing.expect(!SkbuffBridgeLab.hasRequiredFreezeEvidence("nonexistent freeze evidence"));
    try std.testing.expect(!SkbuffBridgeLab.hasAutomaticReturnToBlockedTrigger("nonexistent return trigger"));
}

test "skbuff bridge lookup helpers keep the review-only catalog queryable" {
    try std.testing.expect(SkbuffBridgeLab.hasAuditGuard(.segmentation_checksum_data_offset_crossover));
    try std.testing.expect(SkbuffBridgeLab.hasAuditGuard(.segmentation_tail_publication_consumer_contract));
    try std.testing.expect(SkbuffBridgeLab.checkpointById("segmentation-tail-publication-consumer-contract") != null);
    try std.testing.expect(SkbuffBridgeLab.checkpointById("missing-skbuff-checkpoint") == null);
}

test "skbuff bridge blocked-behavior helpers stay aligned with the audit catalog" {
    try std.testing.expectEqual(@as(?usize, 7), SkbuffBridgeLab.blockedBehaviorIndex("segmentation checksum and data-offset crossover before tail publication"));
    try std.testing.expectEqual(@as(?usize, 8), SkbuffBridgeLab.blockedBehaviorIndex("segmentation tail-list publication and validate_xmit_skb_list consumer coordination"));
    try std.testing.expect(SkbuffBridgeLab.blocksLiveBehavior("segmentation checksum metadata recompute and GSO handoff"));
    try std.testing.expect(!SkbuffBridgeLab.blocksLiveBehavior("nonexistent skbuff bridge behavior"));
}
