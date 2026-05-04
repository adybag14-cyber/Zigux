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

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    survey_summary: SurveySummary,
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
    try std.testing.expectEqualStrings("P14-L12", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("net/core/skbuff.c", manifest.anchor);
    try std.testing.expectEqualStrings("02264a3240cd30ce45c9a932047a0204b7ab5029", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
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
    try std.testing.expectEqual(@as(usize, 17), manifest.gaps.len);

    var landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_boundary_map = false;
    var saw_audit_outline = false;
    var saw_checksum_audit = false;
    var saw_segmentation_audit = false;
    var saw_tail_owner_audit = false;
    var saw_followup = false;
    var saw_tail_publication_audit = false;
    var saw_validate_xmit_audit = false;
    var saw_validate_xmit_followup = false;
    var saw_governance_note = false;
    var saw_direct_xmit_followup = false;
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

        if (std.mem.eql(u8, gap.id, "phase14-skbuff-boundary-map-starter")) {
            saw_boundary_map = true;
            try std.testing.expectEqualStrings("net/core/skbuff_bridge.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__alloc_skb") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "consume_skb") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "stay-in-C") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-skbuff-lifetime-audit-outline")) {
            saw_audit_outline = true;
            try std.testing.expectEqualStrings("net/core/skbuff_bridge.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dataref") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "destructor_arg") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-skbuff-checksum-state-audit")) {
            saw_checksum_audit = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("net/core/skbuff_bridge.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "skb->csum") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "skb_checksum_complete_unset") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-skbuff-segmentation-followup")) {
            saw_segmentation_audit = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("net/core/skbuff_bridge.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "skb_segment") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "skb_zerocopy_clone") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-skbuff-segmentation-tail-owner-followup")) {
            saw_tail_owner_audit = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("net/core/skbuff_bridge.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "SKB_GSO_PARTIAL") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "sock_wfree") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-skbuff-segmentation-csum-data-offset-followup")) {
            saw_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("net/core/skbuff_bridge.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "SKB_GSO_CB(nskb)->csum") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "remcsum_offload") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-skbuff-segs-prev-tail-publication-followup")) {
            saw_tail_publication_audit = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("net/core/skbuff_bridge.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "segs->prev") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "validate_xmit_skb_list") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "gso_size") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "gso_segs") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-skbuff-direct-xmit-governance-note")) {
            saw_governance_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-skbuff-bridge-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__dev_direct_xmit()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "skb != orig_skb") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "qdisc publication") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue ownership") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-skbuff-live-ownership-blocker")) {
            saw_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase14_skbuff_bridge.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dataref") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "segmentation") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-skbuff-validate-xmit-list-reset-followup")) {
            saw_validate_xmit_audit = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("net/core/skbuff_bridge.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "skb_mark_not_on_list") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "skb->prev = skb") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tail = skb->prev") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-skbuff-validate-xmit-republish-followup")) {
            saw_validate_xmit_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("net/core/skbuff_bridge.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "head = skb") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tail->next = skb") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "validate_xmit_skb()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-skbuff-direct-xmit-identity-drop-followup")) {
            saw_direct_xmit_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("net/core/skbuff_bridge.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__dev_direct_xmit()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "skb != orig_skb") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "drop path") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 16), landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_boundary_map);
    try std.testing.expect(saw_audit_outline);
    try std.testing.expect(saw_checksum_audit);
    try std.testing.expect(saw_segmentation_audit);
    try std.testing.expect(saw_tail_owner_audit);
    try std.testing.expect(saw_followup);
    try std.testing.expect(saw_tail_publication_audit);
    try std.testing.expect(saw_validate_xmit_audit);
    try std.testing.expect(saw_validate_xmit_followup);
    try std.testing.expect(saw_governance_note);
    try std.testing.expect(saw_direct_xmit_followup);
    try std.testing.expect(saw_blocker);
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
    try std.testing.expectEqual(@as(usize, 2), skbuff_bridge.SkbuffBridgeLab.stayInCDecisionCount());
    try std.testing.expectEqual(@as(usize, 12), audit.checkpoints.len);
    try std.testing.expectEqual(@as(usize, 12), audit.blocked_live_behaviors.len);
    try std.testing.expectEqual(@as(usize, 12), skbuff_bridge.SkbuffBridgeLab.auditCheckpointCount());
    try std.testing.expect(std.mem.indexOf(u8, skbuff_bridge.SkbuffBridgeLab.nextAuditFocus(), "__dev_direct_xmit()") != null);
    try std.testing.expect(std.mem.indexOf(u8, skbuff_bridge.SkbuffBridgeLab.nextAuditFocus(), "skb != orig_skb") != null);
    try std.testing.expectEqualStrings("shared-info-refcount-ownership", map.areas[4].id);
    try std.testing.expectEqualStrings("destructor-and-free-path", map.areas[5].id);
    try std.testing.expect(audit.checkpoints[0].guard == .header_write_requires_private_data);
    try std.testing.expectEqualStrings("skb_shinfo(skb)->destructor_arg", audit.checkpoints[2].observed_fields[1]);
    try std.testing.expect(audit.checkpoints[3].guard == .checksum_complete_state_cache);
    try std.testing.expect(audit.checkpoints[4].guard == .segmentation_orphan_and_zerocopy_handoff);
    try std.testing.expect(audit.checkpoints[5].guard == .segmentation_checksum_metadata_handoff);
    try std.testing.expect(audit.checkpoints[6].guard == .segmentation_partial_tail_owner_transfer);
    try std.testing.expect(audit.checkpoints[7].guard == .segmentation_checksum_data_offset_crossover);
    try std.testing.expect(audit.checkpoints[8].guard == .segmentation_tail_publication_contract);
    try std.testing.expect(audit.checkpoints[9].guard == .validate_xmit_list_consumer_reset_contract);
    try std.testing.expect(audit.checkpoints[10].guard == .validate_xmit_list_republish_contract);
    try std.testing.expect(audit.checkpoints[11].guard == .direct_xmit_identity_drop_contract);
}

test "phase14 skbuff bridge notes record the direct-xmit governance boundary" {
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
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(slice_note);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_LANE_KEY=P14-L12") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_SLICE=skbuff-direct-xmit-identity-drop") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_SURVEYED_COMMIT=02264a3240cd30ce45c9a932047a0204b7ab5029") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "tail->next = skb") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "validate_xmit_skb()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase14-skbuff-direct-xmit-governance-note") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase14-skbuff-direct-xmit-identity-drop-followup") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "observational-only") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "qdisc publication, queue ownership, and skb lifetime ownership remain in C") != null);

    try std.testing.expect(std.mem.indexOf(u8, slice_note, "direct-xmit governance note") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "identity-drop checkpoint") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "observational only") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "qdisc publication, queue ownership, and skb lifetime ownership remain explicitly in C") != null);
}

test "phase14 skbuff bridge compile contract stays wired into the shared bundle" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const phase14_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_build.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(phase14_build);

    const smoke_manifest = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_end_to_end_smoke_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(smoke_manifest);

    try std.testing.expect(std.mem.indexOf(u8, phase14_build, ".root_source_file = b.path(\"../../net/core/skbuff_bridge.zig\")") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase14_build, ".root_source_file = b.path(\"phase14_skbuff_bridge.zig\")") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase14_build, "phase14_skbuff_bridge_module.addImport(\"skbuff_bridge\", skbuff_bridge_module);") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase14_build, ".name = \"phase14-skbuff-bridge-tests\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase14_build, "test_step.dependOn(&run_phase14_skbuff_bridge_tests.step);") != null);

    try std.testing.expect(std.mem.indexOf(u8, smoke_manifest, "\"lane_key\": \"P14-L01\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_manifest, "\"artifact_name\": \"phase14-skbuff-bridge-tests\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_manifest, "\"root_source_file\": \"phase14_skbuff_bridge.zig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_manifest, "\"bridge_import\": \"skbuff_bridge\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_manifest, "\"bridge_source_file\": \"../../net/core/skbuff_bridge.zig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_manifest, "\"coverage_mode\": \"full_bundle_only\"") != null);
}
