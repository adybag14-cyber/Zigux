const std = @import("std");

const Governance = struct {
    status_bucket: []const u8,
    ready_next_gap: []const u8,
    last_closed_followup: []const u8,
    blocked_gap: []const u8,
    lane_reopen_scope: []const u8,
    why_now: []const u8,
};

const ChecklistEntry = struct {
    id: []const u8,
    ownership: []const u8,
    anchor_symbols: []const []const u8,
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
    study_only_governance: Governance,
    decision_checklist: []const ChecklistEntry,
    gaps: []const Gap,
};

fn hasChecklistEntry(entries: []const ChecklistEntry, id: []const u8) bool {
    for (entries) |entry| {
        if (std.mem.eql(u8, entry.id, id) and std.mem.eql(u8, entry.ownership, "stay_in_c")) {
            return true;
        }
    }
    return false;
}

fn hasString(entries: []const []const u8, value: []const u8) bool {
    for (entries) |entry| {
        if (std.mem.eql(u8, entry, value)) {
            return true;
        }
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

test "phase14 ring-buffer survey manifest records the current study-only packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_ring_buffer_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P14-L08", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("99cd3249c4bab05b74227ed7ca3869284e818588", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("kernel/trace/ring_buffer.c", manifest.anchor);
    try std.testing.expect(hasString(manifest.roadmap_destinations, "kernel/trace/ring_buffer.zig"));
    try std.testing.expectEqualStrings("study_only", manifest.study_only_governance.status_bucket);
    try std.testing.expectEqualStrings("", manifest.study_only_governance.ready_next_gap);
    try std.testing.expectEqualStrings("phase14-ring-buffer-zig-port-blocker", manifest.study_only_governance.blocked_gap);
    try std.testing.expectEqualStrings("phase14-ring-buffer-tracefs-reader-serialization-followup", manifest.study_only_governance.last_closed_followup);
    try std.testing.expectEqualStrings("same_packet_truthfulness_repairs_only", manifest.study_only_governance.lane_reopen_scope);
    try std.testing.expect(std.mem.indexOf(u8, manifest.study_only_governance.why_now, "parked study-only governance") != null);
    try std.testing.expectEqual(@as(usize, 6), manifest.decision_checklist.len);
    try std.testing.expect(hasChecklistEntry(manifest.decision_checklist, "reserve-commit-publication"));
    try std.testing.expect(hasChecklistEntry(manifest.decision_checklist, "reader-page-consume-boundary"));
    try std.testing.expect(hasGap(manifest, "phase14-ring-buffer-read-page-extraction-followup", "starter_landed"));
    try std.testing.expect(hasGap(manifest, "phase14-ring-buffer-tracefs-reader-serialization-followup", "starter_landed"));
    try std.testing.expect(hasGap(manifest, "phase14-ring-buffer-zig-port-blocker", "blocked_on_stay_in_c_evidence"));
}

test "phase14 ring-buffer survey note keeps the parked study-only posture explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-ring-buffer-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(note);

    try std.testing.expect(std.mem.indexOf(u8, note, "PHASE14_STATUS=study_only") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "boundary-study target first, not a rewrite target") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "only appropriate if years of evidence justify it") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "phase14-ring-buffer-zig-port-blocker") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "phase14-ring-buffer-read-page-extraction-followup") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "phase14-ring-buffer-tracefs-reader-serialization-followup") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "kernel/trace/ring_buffer.zig") != null);
}
