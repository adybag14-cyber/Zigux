const std = @import("std");
const skbuff_bridge = @import("skbuff_bridge");

const ChecklistEntry = struct {
    id: []const u8,
    summary: []const u8,
    ownership: []const u8,
    anchor_symbols: []const []const u8,
    rationale: []const u8,
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
    decision_checklist: []const ChecklistEntry,
    gaps: []const Gap,
};

fn hasChecklistEntry(entries: []const ChecklistEntry, id: []const u8, symbols: []const []const u8) bool {
    for (entries) |entry| {
        if (!std.mem.eql(u8, entry.id, id)) continue;
        if (!std.mem.eql(u8, entry.ownership, "stay_in_c")) return false;
        for (symbols) |symbol| {
            var found = false;
            for (entry.anchor_symbols) |candidate| {
                if (std.mem.eql(u8, candidate, symbol)) {
                    found = true;
                    break;
                }
            }
            if (!found) return false;
        }
        return true;
    }
    return false;
}

fn hasGap(manifest: Manifest, id: []const u8, status: []const u8) bool {
    for (manifest.gaps) |gap| {
        if (std.mem.eql(u8, gap.id, id) and std.mem.eql(u8, gap.status, status)) {
            return true;
        }
    }
    return false;
}

test "phase14 skbuff bridge manifest records the live blocked ownership packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_skbuff_bridge_manifest.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P14-Y03", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("f05e02445443e7743c3675a6f8ca4f70f6e736fb", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("net/core/skbuff.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(hasGap(manifest, "phase14-skbuff-live-ownership-blocker", "blocked_on_stay_in_c_evidence"));
    try std.testing.expect(hasChecklistEntry(
        manifest.decision_checklist,
        "shared-info-refcount-ownership",
        &[_][]const u8{ "struct skb_shared_info", "dataref", "skb_header_cloned" },
    ));
    try std.testing.expect(hasChecklistEntry(
        manifest.decision_checklist,
        "destructor-and-free-path",
        &[_][]const u8{ "skb_release_head_state", "skb_release_data", "consume_skb" },
    ));
    try std.testing.expect(hasChecklistEntry(
        manifest.decision_checklist,
        "segmentation-partial-tail-owner-transfer",
        &[_][]const u8{ "skb_segment", "SKB_GSO_PARTIAL", "sock_wfree" },
    ));
    try std.testing.expect(hasChecklistEntry(
        manifest.decision_checklist,
        "segmentation-checksum-data-offset-crossover",
        &[_][]const u8{ "skb_segment", "SKB_GSO_CB", "remcsum_offload" },
    ));
    try std.testing.expect(hasChecklistEntry(
        manifest.decision_checklist,
        "segmentation-tail-publication-consumer-contract",
        &[_][]const u8{ "skb_segment", "segs->prev", "validate_xmit_skb_list" },
    ));
}

test "phase14 skbuff survey note keeps the blocker wording explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-skbuff-bridge-survey.md",
        std.testing.allocator,
        .limited(8 * 1024),
    );
    defer std.testing.allocator.free(note);

    try std.testing.expect(std.mem.indexOf(u8, note, "PHASE14_LANE_KEY=P14-Y03") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "phase14-skbuff-live-ownership-blocker") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "segs->prev") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "tail->next") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "validate_xmit_skb_list()") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "skb_mark_not_on_list()") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "tail = skb->prev") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "qdisc-facing publication") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "queue ownership") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "skb lifetime ownership") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "checksum ownership") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "destructor coordination") != null);
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
    try std.testing.expectEqual(@as(usize, 6), map.areas.len);
    try std.testing.expectEqual(@as(usize, 2), skbuff_bridge.SkbuffBridgeLab.stayInCDecisionCount());
    try std.testing.expectEqual(@as(usize, 9), audit.checkpoints.len);
    try std.testing.expectEqual(@as(usize, 9), audit.blocked_live_behaviors.len);
    try std.testing.expect(std.mem.indexOf(u8, skbuff_bridge.SkbuffBridgeLab.nextAuditFocus(), "No smaller review-only skbuff follow-up remains") != null);
    try std.testing.expect(std.mem.indexOf(u8, skbuff_bridge.SkbuffBridgeLab.nextAuditFocus(), "live ownership blocker") != null);
    try std.testing.expectEqualStrings("segmentation-tail-publication-consumer-contract", audit.checkpoints[8].id);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[8].blocked_by, "skb_mark_not_on_list()") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[8].blocked_by, "tail = skb->prev") != null);
}
