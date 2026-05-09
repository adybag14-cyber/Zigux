const std = @import("std");
const skbuff_bridge = @import("skbuff_bridge");

const SurveySummary = struct {
    skbuff_c_lines: usize,
    skbuff_h_lines: usize,
    datagram_c_lines: usize,
    freeze_map_lists_skbuff_c: bool,
    preexisting_phase14_build_present: bool,
    preexisting_phase14_make_target_present: bool,
    preexisting_phase14_workqueue_bridge_present: bool,
    preexisting_phase14_ring_buffer_manifest_present: bool,
    preexisting_phase14_skbuff_bridge_present: bool,
    preexisting_phase14_skbuff_test_present: bool,
    preexisting_phase14_skbuff_manifest_present: bool,
    preexisting_phase14_skbuff_slice_note_present: bool,
    preexisting_phase14_skbuff_survey_note_present: bool,
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
    roadmap_boundary_area_ids: []const []const u8,
    survey_summary: SurveySummary,
    decision_checklist: []const DecisionChecklistEntry,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_stay_in_c_evidence");
}

test "phase14 skbuff bridge manifest records the boundary-map foothold and frozen ownership gap" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_skbuff_bridge_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P14-L10", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("net/core/skbuff.c", manifest.anchor);
    try std.testing.expectEqualStrings("4f6dab5f88d8141ecd358d93fe9284bcc98dc1d7", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.roadmap_boundary_area_ids.len);
    try std.testing.expect(manifest.survey_summary.skbuff_c_lines >= 7400);
    try std.testing.expect(manifest.survey_summary.skbuff_h_lines >= 5400);
    try std.testing.expect(manifest.survey_summary.datagram_c_lines >= 1000);
    try std.testing.expect(manifest.survey_summary.freeze_map_lists_skbuff_c);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_make_target_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_workqueue_bridge_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_ring_buffer_manifest_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_skbuff_bridge_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_skbuff_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_skbuff_manifest_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_skbuff_slice_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_skbuff_survey_note_present);
    try std.testing.expectEqual(@as(usize, 5), manifest.decision_checklist.len);
    try std.testing.expectEqual(@as(usize, 15), manifest.gaps.len);
    try std.testing.expectEqual(@as(usize, 4), skbuff_bridge.SkbuffBridgeLab.roadmapBoundaryStudyAreaIds().len);

    var landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_boundary_map = false;
    var saw_boundary_map_query = false;
    var saw_audit_outline = false;
    var saw_decision_checklist = false;
    var saw_checksum_audit = false;
    var saw_segmentation_audit = false;
    var saw_tail_owner_audit = false;
    var saw_followup = false;
    var saw_blocker = false;

    for (manifest.roadmap_boundary_area_ids, 0..) |area_id, index| {
        const area = skbuff_bridge.SkbuffBridgeLab.boundaryAreaById(area_id) orelse return error.MissingBoundaryArea;
        try std.testing.expectEqualStrings(skbuff_bridge.SkbuffBridgeLab.roadmapBoundaryStudyAreaIds()[index], area_id);
        try std.testing.expect(area.ownership == .boundary_map_only);
        try std.testing.expect(skbuff_bridge.SkbuffBridgeLab.isRoadmapBoundaryStudyArea(area_id));
        try std.testing.expect(!skbuff_bridge.SkbuffBridgeLab.isStayInCBoundaryArea(area_id));
    }

    try std.testing.expectEqualStrings("allocation-entrypoints", manifest.roadmap_boundary_area_ids[0]);
    try std.testing.expectEqualStrings("clone-and-private-copy", manifest.roadmap_boundary_area_ids[1]);
    try std.testing.expectEqualStrings("headroom-and-linearization-mutation", manifest.roadmap_boundary_area_ids[2]);
    try std.testing.expectEqualStrings("checksum-and-segmentation-surface", manifest.roadmap_boundary_area_ids[3]);

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

        if (std.mem.eql(u8, gap.id, "phase14-skbuff-boundary-map-starter")) {
            saw_boundary_map = true;
            try std.testing.expectEqualStrings("net/core/skbuff_bridge.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__alloc_skb") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "consume_skb") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "stay-in-C") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-skbuff-boundary-map-roadmap-query")) {
            saw_boundary_map_query = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("boundary_map", gap.kind);
            try std.testing.expectEqualStrings("net/core/skbuff_bridge.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "exact four roadmap boundary-study area ids") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "structured packet-local data") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-skbuff-boundary-decision-checklist")) {
            saw_decision_checklist = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("governance", gap.kind);
            try std.testing.expectEqualStrings("zigux/tests/phase14_skbuff_bridge_manifest.json", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dataref ownership") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "consume_skb() teardown") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "qdisc-facing skb_segment() publication checkpoints") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-skbuff-concurrency-audit-outline")) {
            saw_audit_outline = true;
            try std.testing.expectEqualStrings("lifetime_audit", gap.kind);
            try std.testing.expectEqualStrings("net/core/skbuff_bridge.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dataref") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "destructor_arg") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "concurrency-sensitive checkpoint catalog") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "roadmap's concurrency-audit requirement") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-skbuff-checksum-state-audit")) {
            saw_checksum_audit = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lifetime_audit", gap.kind);
            try std.testing.expectEqualStrings("net/core/skbuff_bridge.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "skb->csum") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "skb_checksum_complete_unset") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-skbuff-segmentation-followup")) {
            saw_segmentation_audit = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lifetime_audit", gap.kind);
            try std.testing.expectEqualStrings("net/core/skbuff_bridge.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "skb_segment") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "skb_zerocopy_clone") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-skbuff-segmentation-tail-owner-followup")) {
            saw_tail_owner_audit = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lifetime_audit", gap.kind);
            try std.testing.expectEqualStrings("net/core/skbuff_bridge.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "SKB_GSO_PARTIAL") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "sock_wfree") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-skbuff-segmentation-csum-data-offset-followup")) {
            saw_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lifetime_audit", gap.kind);
            try std.testing.expectEqualStrings("net/core/skbuff_bridge.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "SKB_GSO_CB(nskb)->csum") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "remcsum_offload") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-skbuff-segs-prev-tail-publication-followup")) {
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lifetime_audit", gap.kind);
            try std.testing.expectEqualStrings("net/core/skbuff_bridge.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "segs->prev") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "validate_xmit_skb_list") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-skbuff-live-ownership-blocker")) {
            saw_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase14_skbuff_bridge.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dataref") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "segmentation") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 14), landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_boundary_map);
    try std.testing.expect(saw_boundary_map_query);
    try std.testing.expect(saw_audit_outline);
    try std.testing.expect(saw_decision_checklist);
    try std.testing.expect(saw_checksum_audit);
    try std.testing.expect(saw_segmentation_audit);
    try std.testing.expect(saw_tail_owner_audit);
    try std.testing.expect(saw_followup);
    try std.testing.expect(saw_blocker);
}

test "phase14 skbuff bridge manifest exposes the landed stay-in-c decision checklist" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_skbuff_bridge_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const checklist = parsed.value.decision_checklist;
    try std.testing.expectEqualStrings("shared-info-refcount-ownership", checklist[0].id);
    try std.testing.expectEqualStrings("stay_in_c", checklist[0].ownership);
    try std.testing.expectEqualStrings("struct skb_shared_info", checklist[0].anchor_symbols[0]);
    try std.testing.expectEqualStrings("dataref", checklist[0].anchor_symbols[1]);
    try std.testing.expectEqualStrings("skb_header_cloned", checklist[0].anchor_symbols[2]);
    try std.testing.expect(std.mem.indexOf(u8, checklist[0].rationale, "header-clone rules") != null);
    try std.testing.expectEqualStrings(skbuff_bridge.SkbuffBridgeLab.boundaryMap().areas[4].id, checklist[0].id);
    try std.testing.expectEqualStrings(skbuff_bridge.SkbuffBridgeLab.boundaryMap().areas[4].summary, checklist[0].summary);
    try std.testing.expectEqualStrings(skbuff_bridge.SkbuffBridgeLab.boundaryMap().areas[4].rationale, checklist[0].rationale);

    try std.testing.expectEqualStrings("destructor-and-free-path", checklist[1].id);
    try std.testing.expectEqualStrings("skb_release_head_state", checklist[1].anchor_symbols[0]);
    try std.testing.expectEqualStrings("skb_release_data", checklist[1].anchor_symbols[1]);
    try std.testing.expectEqualStrings("consume_skb", checklist[1].anchor_symbols[2]);
    try std.testing.expect(std.mem.indexOf(u8, checklist[1].rationale, "destructor callbacks") != null);
    try std.testing.expectEqualStrings(skbuff_bridge.SkbuffBridgeLab.boundaryMap().areas[5].id, checklist[1].id);
    try std.testing.expectEqualStrings(skbuff_bridge.SkbuffBridgeLab.boundaryMap().areas[5].summary, checklist[1].summary);
    try std.testing.expectEqualStrings(skbuff_bridge.SkbuffBridgeLab.boundaryMap().areas[5].rationale, checklist[1].rationale);

    const tail_owner = skbuff_bridge.SkbuffBridgeLab.checkpointById("segmentation-partial-tail-owner-transfer") orelse return error.MissingCheckpoint;
    try std.testing.expectEqualStrings("segmentation-partial-tail-owner-transfer", checklist[2].id);
    try std.testing.expectEqualStrings("skb_segment", checklist[2].anchor_symbols[0]);
    try std.testing.expectEqualStrings("SKB_GSO_PARTIAL", checklist[2].anchor_symbols[1]);
    try std.testing.expectEqualStrings("sock_wfree", checklist[2].anchor_symbols[2]);
    try std.testing.expectEqualStrings(tail_owner.id, checklist[2].id);
    try std.testing.expectEqualStrings(tail_owner.summary, checklist[2].summary);
    try std.testing.expectEqualStrings(tail_owner.blocked_by, checklist[2].rationale);

    const checksum_crossover = skbuff_bridge.SkbuffBridgeLab.checkpointById("segmentation-checksum-data-offset-crossover") orelse return error.MissingCheckpoint;
    try std.testing.expectEqualStrings("segmentation-checksum-data-offset-crossover", checklist[3].id);
    try std.testing.expectEqualStrings("skb_segment", checklist[3].anchor_symbols[0]);
    try std.testing.expectEqualStrings("SKB_GSO_CB", checklist[3].anchor_symbols[1]);
    try std.testing.expectEqualStrings("remcsum_offload", checklist[3].anchor_symbols[2]);
    try std.testing.expectEqualStrings(checksum_crossover.id, checklist[3].id);
    try std.testing.expectEqualStrings(checksum_crossover.summary, checklist[3].summary);
    try std.testing.expectEqualStrings(checksum_crossover.blocked_by, checklist[3].rationale);

    const tail_publication = skbuff_bridge.SkbuffBridgeLab.checkpointById("segmentation-tail-publication-consumer-contract") orelse return error.MissingCheckpoint;
    try std.testing.expectEqualStrings("segmentation-tail-publication-consumer-contract", checklist[4].id);
    try std.testing.expectEqualStrings("skb_segment", checklist[4].anchor_symbols[0]);
    try std.testing.expectEqualStrings("segs->prev", checklist[4].anchor_symbols[1]);
    try std.testing.expectEqualStrings("validate_xmit_skb_list", checklist[4].anchor_symbols[2]);
    try std.testing.expectEqualStrings(tail_publication.id, checklist[4].id);
    try std.testing.expectEqualStrings(tail_publication.summary, checklist[4].summary);
    try std.testing.expectEqualStrings(tail_publication.blocked_by, checklist[4].rationale);
}

test "phase14 skbuff bridge descriptor stays at boundary-map posture" {
    const descriptor = skbuff_bridge.SkbuffBridgeLab.descriptor();
    const map = skbuff_bridge.SkbuffBridgeLab.boundaryMap();
    const audit = skbuff_bridge.SkbuffBridgeLab.lifetimeAudit();

    try std.testing.expectEqualStrings("skbuff_boundary_map_lab", descriptor.name);
    try std.testing.expectEqualStrings("net/core/skbuff.c", descriptor.anchor);
    try std.testing.expectEqualStrings("boundary_map_only", descriptor.posture);
    try std.testing.expect(descriptor.provides_boundary_map);
    try std.testing.expect(descriptor.provides_lifetime_audit_outline);
    try std.testing.expect(descriptor.provides_stay_in_c_decisions);
    try std.testing.expect(!descriptor.touches_live_allocators);
    try std.testing.expect(!descriptor.touches_live_refcounts);
    try std.testing.expect(!descriptor.touches_live_destructors);

    try std.testing.expectEqual(@as(usize, 6), map.areas.len);
    try std.testing.expectEqual(@as(usize, 6), skbuff_bridge.SkbuffBridgeLab.boundaryAreaCount());
    try std.testing.expectEqual(@as(usize, 4), skbuff_bridge.SkbuffBridgeLab.roadmapBoundaryStudyAreaCount());
    try std.testing.expectEqual(@as(usize, 2), skbuff_bridge.SkbuffBridgeLab.stayInCBoundaryAreaCount());
    try std.testing.expectEqual(@as(usize, 2), skbuff_bridge.SkbuffBridgeLab.stayInCDecisionCount());
    try std.testing.expectEqual(@as(usize, 9), audit.checkpoints.len);
    try std.testing.expectEqual(@as(usize, 9), audit.blocked_live_behaviors.len);
    try std.testing.expectEqual(@as(usize, 9), skbuff_bridge.SkbuffBridgeLab.auditCheckpointCount());
    try std.testing.expect(std.mem.indexOf(u8, skbuff_bridge.SkbuffBridgeLab.nextAuditFocus(), "qdisc publication") != null);
    try std.testing.expect(std.mem.indexOf(u8, skbuff_bridge.SkbuffBridgeLab.nextAuditFocus(), "stay-in-C evidence") != null);
    try std.testing.expectEqualStrings("shared-info-refcount-ownership", map.areas[4].id);
    try std.testing.expectEqualStrings("destructor-and-free-path", map.areas[5].id);
    try std.testing.expect(audit.checkpoints[0].guard == .header_write_requires_private_data);
    try std.testing.expectEqualStrings("skb_shinfo(skb)->destructor_arg", audit.checkpoints[2].observed_fields[1]);
    try std.testing.expect(audit.checkpoints[3].guard == .checksum_complete_state_cache);
    try std.testing.expect(audit.checkpoints[4].guard == .segmentation_orphan_and_zerocopy_handoff);
    try std.testing.expect(audit.checkpoints[5].guard == .segmentation_checksum_metadata_handoff);
    try std.testing.expect(audit.checkpoints[6].guard == .segmentation_partial_tail_owner_transfer);
    try std.testing.expect(audit.checkpoints[7].guard == .segmentation_checksum_data_offset_crossover);
    try std.testing.expect(audit.checkpoints[8].guard == .segmentation_tail_publication_consumer_contract);

    for (skbuff_bridge.SkbuffBridgeLab.roadmapBoundaryStudyAreaIds()) |area_id| {
        const area = skbuff_bridge.SkbuffBridgeLab.boundaryAreaById(area_id) orelse return error.MissingBoundaryArea;
        try std.testing.expect(area.ownership == .boundary_map_only);
    }

    for (skbuff_bridge.SkbuffBridgeLab.stayInCBoundaryAreaIds()) |area_id| {
        const area = skbuff_bridge.SkbuffBridgeLab.boundaryAreaById(area_id) orelse return error.MissingBoundaryArea;
        try std.testing.expect(area.ownership == .stay_in_c);
    }
}

test "phase14 skbuff bridge notes and code agree the live ownership blocker is next" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-skbuff-bridge-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-skbuff-bridge-slice.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(slice_note);

    try std.testing.expect(std.mem.indexOf(
        u8,
        skbuff_bridge.SkbuffBridgeLab.nextAuditFocus(),
        "No smaller review-only skbuff checkpoint remains",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        skbuff_bridge.SkbuffBridgeLab.nextAuditFocus(),
        "qdisc publication",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        survey_note,
        "PHASE14_STATUS=freeze_in_c",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        survey_note,
        "PHASE14_SURVEYED_COMMIT=4f6dab5f88d8141ecd358d93fe9284bcc98dc1d7",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        survey_note,
        "PHASE14_LANE_KEY=P14-L10",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        survey_note,
        "PHASE14_SLICE=skbuff-boundary-map-roadmap-query",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        survey_note,
        "machine-checkable roadmap boundary-study helpers",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        survey_note,
        "roadmap's concurrency-audit requirement",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        survey_note,
        "machine-checkable roadmap boundary-study helpers",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        survey_note,
        "no smaller review-only skbuff follow-up remains before the live ownership blocker",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        survey_note,
        "blocked `phase14-skbuff-live-ownership-blocker`",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        survey_note,
        "named owner: `Core-Adjacent Pod`",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        survey_note,
        "status bucket: `freeze_in_c`",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        survey_note,
        "validation gate: `zig build test --build-file zigux/tests/phase14_build.zig --summary all` plus `make -C zigux phase14`",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        survey_note,
        "rollback owner: `Repo Tooling Pod`",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        survey_note,
        "keep this packet in `freeze_in_c` posture",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        survey_note,
        "explicit stay-in-C wording for `segs->prev`, `tail->next`, and `validate_xmit_skb_list()`",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        survey_note,
        "qdisc-facing publication, queue ownership, skb lifetime ownership, checksum ownership, and destructor coordination remain in C",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        survey_note,
        "any edit that drops the named validation gate or rollback owner",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        survey_note,
        "missing freeze-in-C or stay-in-C wording for the exported tail-publication checkpoint",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        survey_note,
        "any manifest refresh that changes the blocked live-ownership gap without refreshing this survey note",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        survey_note,
        "any edit that weakens the explicit no-smaller-follow-up stance and silently implies a fresh skbuff wrapper step",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        slice_note,
        "machine-checkable helper queries for the four roadmap boundary-study areas",
    ) != null);
    try std.testing.expectEqual(@as(usize, 3), skbuff_bridge.SkbuffBridgeLab.concurrencySensitiveCheckpointCount());
    try std.testing.expect(skbuff_bridge.SkbuffBridgeLab.isConcurrencySensitiveCheckpoint("segmentation-tail-publication-consumer-contract"));
    try std.testing.expect(std.mem.indexOf(
        u8,
        slice_note,
        "qdisc-facing publication",
    ) != null);
}