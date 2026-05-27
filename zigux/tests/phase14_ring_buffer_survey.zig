const std = @import("std");

const SurveySummary = struct {
    preexisting_phase14_build_present: bool,
    preexisting_phase14_make_target_present: bool,
    preexisting_phase14_workqueue_bridge_present: bool,
    preexisting_ring_buffer_zig_present: bool,
    preexisting_phase14_ring_buffer_manifest_present: bool,
    preexisting_phase14_ring_buffer_survey_test_present: bool,
    preexisting_phase14_ring_buffer_survey_note_present: bool,
};

const Governance = struct {
    status_bucket: []const u8,
    ready_next_gap: []const u8,
    last_closed_followup: []const u8,
    blocked_gap: []const u8,
    lane_reopen_scope: []const u8,
    why_now: []const u8,
};

const MaintenanceHandoff = struct {
    current_lane_posture: []const u8,
    replay_before_trusting: []const []const u8,
    replay_vocabulary_only_until_paths_return: bool,
    reopen_conditions: []const []const u8,
    next_future_target: []const u8,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const DecisionChecklist = struct {
    id: []const u8,
    ownership: []const u8,
    summary: []const u8,
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
    study_only_governance: Governance,
    maintenance_handoff: MaintenanceHandoff,
    decision_checklist: []const DecisionChecklist,
    gaps: []const Gap,
};

const SharedCompileShard = struct {
    label: []const u8,
    root_source: []const u8,
    coverage: []const u8,
};

const SharedSmokeManifest = struct {
    shared_smoke_surfaces: []const []const u8,
    smoke_shard_commands: []const []const u8,
    compile_shards: []const SharedCompileShard,
};

fn containsString(items: []const []const u8, needle: []const u8) bool {
    for (items) |item| {
        if (std.mem.eql(u8, item, needle)) return true;
    }
    return false;
}

fn hasGap(manifest: Manifest, id: []const u8, status: []const u8, kind: []const u8, destination: []const u8, why_now_fragment: []const u8) bool {
    for (manifest.gaps) |gap| {
        if (!std.mem.eql(u8, gap.id, id)) continue;
        if (!std.mem.eql(u8, gap.status, status)) continue;
        if (!std.mem.eql(u8, gap.kind, kind)) continue;
        if (!std.mem.eql(u8, gap.zigux_destination, destination)) continue;
        if (std.mem.indexOf(u8, gap.why_now, why_now_fragment) == null) continue;
        return true;
    }
    return false;
}

fn hasDecisionChecklist(manifest: Manifest, id: []const u8, ownership: []const u8, summary_fragment: []const u8, anchor_symbol: []const u8, rationale_fragment: []const u8) bool {
    for (manifest.decision_checklist) |entry| {
        if (!std.mem.eql(u8, entry.id, id)) continue;
        if (!std.mem.eql(u8, entry.ownership, ownership)) continue;
        if (std.mem.indexOf(u8, entry.summary, summary_fragment) == null) continue;
        if (!containsString(entry.anchor_symbols, anchor_symbol)) continue;
        if (std.mem.indexOf(u8, entry.rationale, rationale_fragment) == null) continue;
        return true;
    }
    return false;
}

fn hasCompileShard(manifest: SharedSmokeManifest, label: []const u8, root_source: []const u8, coverage: []const u8) bool {
    for (manifest.compile_shards) |entry| {
        if (!std.mem.eql(u8, entry.label, label)) continue;
        if (!std.mem.eql(u8, entry.root_source, root_source)) continue;
        if (!std.mem.eql(u8, entry.coverage, coverage)) continue;
        return true;
    }
    return false;
}

test "phase14 ring-buffer manifest tracks the parked study packet with its full schema" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_ring_buffer_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P14-L08", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("99cd3249c4bab05b74227ed7ca3869284e818588", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("kernel/trace/ring_buffer.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(containsString(manifest.roadmap_destinations, "zigux/tests/"));
    try std.testing.expect(containsString(manifest.roadmap_destinations, "Documentation/zigux/"));
    try std.testing.expect(containsString(manifest.roadmap_destinations, "kernel/trace/ring_buffer.zig"));
    try std.testing.expectEqual(false, manifest.survey_summary.preexisting_phase14_build_present);
    try std.testing.expectEqual(false, manifest.survey_summary.preexisting_phase14_make_target_present);
    try std.testing.expectEqual(true, manifest.survey_summary.preexisting_phase14_workqueue_bridge_present);
    try std.testing.expectEqual(false, manifest.survey_summary.preexisting_ring_buffer_zig_present);
    try std.testing.expectEqual(true, manifest.survey_summary.preexisting_phase14_ring_buffer_manifest_present);
    try std.testing.expectEqual(true, manifest.survey_summary.preexisting_phase14_ring_buffer_survey_test_present);
    try std.testing.expectEqual(true, manifest.survey_summary.preexisting_phase14_ring_buffer_survey_note_present);
    try std.testing.expectEqualStrings("study_only", manifest.study_only_governance.status_bucket);
    try std.testing.expectEqualStrings("", manifest.study_only_governance.ready_next_gap);
    try std.testing.expectEqualStrings("phase14-ring-buffer-maintenance-handoff", manifest.study_only_governance.last_closed_followup);
    try std.testing.expectEqualStrings("phase14-ring-buffer-zig-port-blocker", manifest.study_only_governance.blocked_gap);
    try std.testing.expectEqualStrings("same_packet_truthfulness_repairs_only", manifest.study_only_governance.lane_reopen_scope);
    try std.testing.expect(std.mem.indexOf(u8, manifest.study_only_governance.why_now, "shared Phase 14 build shard") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.study_only_governance.why_now, "shared-smoke vocabulary") != null);
    try std.testing.expectEqualStrings("maintenance_mode", manifest.maintenance_handoff.current_lane_posture);
    try std.testing.expectEqual(true, manifest.maintenance_handoff.replay_vocabulary_only_until_paths_return);
    try std.testing.expectEqual(@as(usize, 1), manifest.maintenance_handoff.replay_before_trusting.len);
    try std.testing.expectEqualStrings("zig test zigux/tests/phase14_ring_buffer_survey.zig", manifest.maintenance_handoff.replay_before_trusting[0]);
    try std.testing.expectEqual(@as(usize, 3), manifest.maintenance_handoff.reopen_conditions.len);
    try std.testing.expect(std.mem.indexOf(u8, manifest.maintenance_handoff.reopen_conditions[0], "replay-route wording") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.maintenance_handoff.next_future_target, "historical vocabulary until zigux/tests/phase14_build.zig itself returns through direct readback") != null);
    try std.testing.expect(hasDecisionChecklist(manifest, "tracefs-mapping-limitations", "stay_in_c", "shared tracefs lockout boundary", "rb_remove_pages", "page-lifetime contract"));
    try std.testing.expect(hasDecisionChecklist(manifest, "read-page-extraction-boundary", "stay_in_c", "partial-copy fallback", "ring_buffer_read_page", "commit-page visibility"));
    try std.testing.expect(hasDecisionChecklist(manifest, "tracefs-reader-serialization-boundary", "stay_in_c", "consumed-page lifetime", "tracing_buffers_splice_read", "pipe-buffer references"));
    try std.testing.expect(hasDecisionChecklist(manifest, "remote-reader-metadata", "stay_in_c", "callback boundary", "rb_read_remote_meta_page", "callback-driven metadata refresh"));
    try std.testing.expect(hasGap(manifest, "phase14-build-gate-current-master-gap", "exact_readback_gap", "validation", "zigux/tests/phase14_build.zig", "shared Phase 14 build shard"));
    try std.testing.expect(hasGap(manifest, "phase14-make-target", "resolved_as_drift_retired", "validation", "zigux/Makefile", "does not ship a dedicated `make -C zigux phase14` convenience route"));
    try std.testing.expect(hasGap(manifest, "phase14-ring-buffer-mapped-reader-ioctl-followup", "starter_landed", "boundary_audit", "Documentation/zigux/phase14-ring-buffer-survey.md", "TRACE_MMAP_IOCTL_GET_READER"));
    try std.testing.expect(hasGap(manifest, "phase14-ring-buffer-remote-reader-followup", "starter_landed", "boundary_audit", "Documentation/zigux/phase14-ring-buffer-survey.md", "rb_read_remote_meta_page()"));
    try std.testing.expect(hasGap(manifest, "phase14-ring-buffer-maintenance-handoff", "starter_landed", "maintenance_handoff", "Documentation/zigux/phase14-ring-buffer-survey.md", "explicit reopen conditions"));
    try std.testing.expect(hasGap(manifest, "phase14-ring-buffer-zig-port-blocker", "blocked_on_stay_in_c_evidence", "freeze_map", "kernel/trace/ring_buffer.zig", "years of evidence justify it"));
}

test "phase14 shared smoke manifest keeps the ring-buffer compile shard explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_end_to_end_smoke_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(SharedSmokeManifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expect(containsString(manifest.shared_smoke_surfaces, "zigux/tests/phase14_ring_buffer_survey.zig"));
    try std.testing.expect(containsString(manifest.shared_smoke_surfaces, "zigux/tests/phase14_build.zig"));
    try std.testing.expectEqual(@as(usize, 1), manifest.smoke_shard_commands.len);
    try std.testing.expectEqualStrings(
        "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig",
        manifest.smoke_shard_commands[0],
    );
    try std.testing.expect(hasCompileShard(
        manifest,
        "phase14-ring-buffer-survey-tests",
        "phase14_ring_buffer_survey.zig",
        "full_bundle_only",
    ));
}

test "phase14 ring-buffer survey note keeps the exact compile-route posture explicit" {
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
    try std.testing.expect(std.mem.indexOf(u8, note, "current ring-buffer packet replay vocabulary") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`zigux/tests/phase14_ring_buffer_manifest.json`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`Documentation/zigux/phase14-core-boundary-traceability.md`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "current public raw-file readback now recovers `zigux/tests/phase14_ring_buffer_survey.zig`, while `zigux/tests/phase14_build.zig` still does not return through this lane's exact contents path") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`zig test zigux/tests/phase14_ring_buffer_survey.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "dedicated ring-buffer survey replay, backed by current public raw-file readback") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "shared smoke manifest vocabulary that still is not backed by a returned build file in this lane") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "current contents-path readback is still partial") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "keep the first route as returned ring-buffer-local replay vocabulary only, and keep the second route as shared-smoke manifest vocabulary only") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "missing dedicated `make -C zigux phase14` route") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "shared smoke manifest's focused build-shard command as historical vocabulary only until `zigux/tests/phase14_build.zig` itself returns through direct readback") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "phase14-ring-buffer-maintenance-handoff") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "phase14-ring-buffer-zig-port-blocker") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "checkout-capable attached-toolchain command examples") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "record the toolchain as environment context and do not claim a fresh local replay") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`/absolute/path/to/attached-zig/zig test zigux/tests/phase14_ring_buffer_survey.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`/absolute/path/to/attached-zig/zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "these examples stay subordinate to the same study-only, no-parity, no-wrapper-restoration posture") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "rb_remove_pages() keeps mapped-reader lifetime teardown in the same C-owned boundary") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "## Mapped-reader ioctl audit") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`TRACE_MMAP_IOCTL_GET_READER`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`ring_buffer_map_get_reader()`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "## Remote-reader metadata audit") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`rb_read_remote_meta_page()`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`__rb_get_reader_page_from_remote()`") != null);
}
