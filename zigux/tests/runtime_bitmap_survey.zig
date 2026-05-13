const std = @import("std");

const expected_surveyed_commit = "00b92f22991e9124aefb308d7eb0e90f14923338";
const direct_phase5_reference_anchors = [_][]const u8{
    "`samples/zigux/bytestream_fifo.zig`",
    "`samples/zigux/kretprobe_example.zig`",
    "`samples/zigux/trace_events_sample.zig`",
};
const phase5_kobject_packet_markers = [_][]const u8{
    "`Documentation/zigux/phase5-kobject-sample-survey.md`",
    "`zigux/tests/phase5_kobject_example.zig`",
    "`zigux/tests/phase5_kobject_example_manifest.json`",
};
const runtime_bitmap_family_files = [_][]const u8{
    "`samples/zigux/runtime_bitmap.zig`",
    "`samples/zigux/runtime_bitmap_loader.zig`",
    "`samples/zigux/runtime_bitmap_top_bit_contract.zig`",
};

const DeliveryEvidence = struct {
    id: []const u8,
    kind: []const u8,
    path: []const u8,
    why_now: []const u8,
};

const OwnershipEntry = struct {
    surface: []const u8,
    role: []const u8,
    owner: []const u8,
    boundary: []const u8,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const RoadmapGapSummary = struct {
    roadmap_phase_goal: []const u8,
    landed_pilot_state: []const u8,
    missing_capability: []const u8,
    blocked_deliverable: []const u8,
    next_gate: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    roadmap_gap_summary: RoadmapGapSummary,
    delivery_evidence_catalog: []const DeliveryEvidence,
    ownership_map: []const OwnershipEntry,
    gaps: []const Gap,
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn isLowerHexCommit(commit: []const u8) bool {
    if (commit.len != 40) return false;
    for (commit) |char| {
        if (!((char >= '0' and char <= '9') or (char >= 'a' and char <= 'f'))) return false;
    }
    return true;
}

fn expectSurveyedCommitMarker(text: []const u8, commit: []const u8) !void {
    var marker_buffer: [96]u8 = undefined;
    const marker = try std.fmt.bufPrint(&marker_buffer, "`PHASE9_SURVEYED_COMMIT={s}`", .{commit});
    try expectContains(text, marker);
}

fn readRepoFileAlloc(allocator: std.mem.Allocator, path: []const u8, max_bytes: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(max_bytes),
    );
}

fn findDeliveryEvidence(entries: []const DeliveryEvidence, id: []const u8) ?DeliveryEvidence {
    for (entries) |entry| {
        if (std.mem.eql(u8, entry.id, id)) return entry;
    }
    return null;
}

fn findOwnershipEntry(entries: []const OwnershipEntry, surface: []const u8) ?OwnershipEntry {
    for (entries) |entry| {
        if (std.mem.eql(u8, entry.surface, surface)) return entry;
    }
    return null;
}

fn findGap(gaps: []const Gap, id: []const u8) ?Gap {
    for (gaps) |gap| {
        if (std.mem.eql(u8, gap.id, id)) return gap;
    }
    return null;
}

test "phase 9 runtime bitmap survey gate keeps the manifest and review packet aligned" {
    const manifest_json = try readRepoFileAlloc(
        std.testing.allocator,
        "zigux/tests/runtime_bitmap_manifest.json",
        64 * 1024,
    );
    defer std.testing.allocator.free(manifest_json);

    const survey_note = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase9-runtime-bitmap-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(survey_note);

    const module_slice = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase9-runtime-bitmap-module-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(module_slice);

    const sample_root_readme = try readRepoFileAlloc(
        std.testing.allocator,
        "samples/zigux/README.md",
        96 * 1024,
    );
    defer std.testing.allocator.free(sample_root_readme);

    const runtime_bitmap_sample = try readRepoFileAlloc(
        std.testing.allocator,
        "samples/zigux/runtime_bitmap.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(runtime_bitmap_sample);

    const top_bit_contract_source = try readRepoFileAlloc(
        std.testing.allocator,
        "samples/zigux/runtime_bitmap_top_bit_contract.zig",
        24 * 1024,
    );
    defer std.testing.allocator.free(top_bit_contract_source);

    const runtime_bitmap_loader = try readRepoFileAlloc(
        std.testing.allocator,
        "samples/zigux/runtime_bitmap_loader.zig",
        128 * 1024,
    );
    defer std.testing.allocator.free(runtime_bitmap_loader);

    const phase9_build = try readRepoFileAlloc(
        std.testing.allocator,
        "zigux/tests/phase9_build.zig",
        96 * 1024,
    );
    defer std.testing.allocator.free(phase9_build);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P9-L08", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 9", manifest.phase);
    try std.testing.expectEqualStrings(expected_surveyed_commit, manifest.surveyed_commit);
    try std.testing.expect(isLowerHexCommit(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("lib/test_bitmap.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("zigux/tests/runtime_*", manifest.roadmap_destinations[0]);
    try std.testing.expectEqualStrings("samples/zigux/runtime_*", manifest.roadmap_destinations[1]);
    try std.testing.expectEqualStrings(
        "first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity",
        manifest.roadmap_gap_summary.roadmap_phase_goal,
    );
    try std.testing.expectEqualStrings(
        "starter_landed_without_loadable_runtime_substrate",
        manifest.roadmap_gap_summary.landed_pilot_state,
    );
    try std.testing.expectEqualStrings(
        "shared runtime substrate that can turn the bounded bitmap loader scaffold into a real loadable module path",
        manifest.roadmap_gap_summary.missing_capability,
    );
    try std.testing.expectEqualStrings(
        "loadable Phase 9 runtime bitmap pilot module parity",
        manifest.roadmap_gap_summary.blocked_deliverable,
    );
    try std.testing.expectEqualStrings(
        "keep the loader scaffold, top-bit companion contract, prepared-plan drift guard, and shared-request lifecycle proof explicit until the shared runtime loader substrate can consume the handoff plan",
        manifest.roadmap_gap_summary.next_gate,
    );
    try std.testing.expectEqual(@as(usize, 13), manifest.delivery_evidence_catalog.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.ownership_map.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.gaps.len);

    const module_gate = findDeliveryEvidence(manifest.delivery_evidence_catalog, "runtime-bitmap-module-gate") orelse return error.MissingModuleGate;
    try std.testing.expectEqualStrings("zigux/tests/runtime_bitmap_module.zig", module_gate.path);
    const survey_gate = findDeliveryEvidence(manifest.delivery_evidence_catalog, "runtime-bitmap-survey-gate") orelse return error.MissingSurveyGate;
    try std.testing.expectEqualStrings("zigux/tests/runtime_bitmap_survey.zig", survey_gate.path);
    const sample_root_summary_entry = findDeliveryEvidence(manifest.delivery_evidence_catalog, "runtime-bitmap-sample-root-summary") orelse return error.MissingSampleRootSummary;
    try std.testing.expectEqualStrings("samples/zigux/README.md", sample_root_summary_entry.path);
    try expectContains(sample_root_summary_entry.why_now, "separate Phase 9 runtime bitmap family");
    try expectContains(sample_root_summary_entry.why_now, "top-bit companion replay");
    try expectContains(sample_root_summary_entry.why_now, "phase9-runtime-loader-shared-tests");
    const survey_note_entry = findDeliveryEvidence(manifest.delivery_evidence_catalog, "runtime-bitmap-survey-note") orelse return error.MissingSurveyNote;
    try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-bitmap-survey.md", survey_note_entry.path);
    const module_slice_entry = findDeliveryEvidence(manifest.delivery_evidence_catalog, "runtime-bitmap-module-slice-note") orelse return error.MissingModuleSliceNote;
    try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-bitmap-module-slice.md", module_slice_entry.path);

    const manifest_owner = findOwnershipEntry(manifest.ownership_map, "zigux/tests/runtime_bitmap_manifest.json") orelse return error.MissingManifestOwner;
    try std.testing.expectEqualStrings("packet_truth_manifest", manifest_owner.role);
    try std.testing.expectEqualStrings("P9-L08", manifest_owner.owner);
    const build_owner = findOwnershipEntry(manifest.ownership_map, "zigux/tests/phase9_build.zig") orelse return error.MissingBuildOwner;
    try std.testing.expectEqualStrings("shared_build_bundle", build_owner.role);
    try std.testing.expectEqualStrings("P9-L11", build_owner.owner);

    const loader_gap = findGap(manifest.gaps, "runtime-bitmap-loader-scaffold") orelse return error.MissingLoaderGap;
    try std.testing.expectEqualStrings("starter_landed", loader_gap.status);
    try std.testing.expectEqualStrings("runtime_loader_scaffold", loader_gap.kind);
    try std.testing.expectEqualStrings("samples/zigux/runtime_bitmap_loader.zig", loader_gap.zigux_destination);
    const prepared_plan_gap = findGap(manifest.gaps, "runtime-bitmap-shared-prepared-plan-drift") orelse return error.MissingPreparedPlanGap;
    try std.testing.expectEqualStrings("starter_landed", prepared_plan_gap.status);
    try std.testing.expectEqualStrings("shared_loader_review_guard", prepared_plan_gap.kind);
    try std.testing.expectEqualStrings("samples/zigux/runtime_bitmap_loader.zig", prepared_plan_gap.zigux_destination);
    try expectContains(prepared_plan_gap.why_now, "prepared-plan drift explicit");
    try expectContains(prepared_plan_gap.why_now, "requestSharedRuntimeLoad");
    const substrate_gap = findGap(manifest.gaps, "runtime-bitmap-live-loader-binding") orelse return error.MissingSubstrateGap;
    try std.testing.expectEqualStrings("blocked_on_runtime_substrate", substrate_gap.status);
    try std.testing.expectEqualStrings("runtime_substrate", substrate_gap.kind);
    try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", substrate_gap.zigux_destination);

    try expectContains(survey_note, "`PHASE9_LANE_KEY=P9-L08`");
    try expectSurveyedCommitMarker(survey_note, manifest.surveyed_commit);
    try expectContains(survey_note, "`zig test zigux/tests/runtime_bitmap_survey.zig`");
    try expectContains(survey_note, "`zig build phase9-runtime-bitmap-top-bit-tests --build-file zigux/tests/phase9_build.zig`");
    try expectContains(survey_note, "`make -C zigux phase9-runtime-bitmap-top-bit-test`");
    try expectContains(survey_note, "`zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`");
    try expectContains(survey_note, "`make -C zigux phase9-runtime-loader-shared-tests`");
    try expectContains(survey_note, "`make -C zigux phase9`");
    try expectContains(survey_note, "no `samples/zigux/*bitmap*` Phase 5 reference sample");
    try expectContains(survey_note, "separate Phase 9 runtime bitmap family");
    try expectContains(survey_note, "rather than a fifth approved Phase 5 sample idiom");
    for (direct_phase5_reference_anchors) |marker| try expectContains(survey_note, marker);
    for (phase5_kobject_packet_markers) |marker| try expectContains(survey_note, marker);
    for (runtime_bitmap_family_files) |marker| try expectContains(survey_note, marker);

    try expectContains(sample_root_readme, "current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample");
    try expectContains(sample_root_readme, "`samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and the focused `samples/zigux/runtime_bitmap_top_bit_contract.zig` companion replay");
    try expectContains(sample_root_readme, "`phase9-runtime-bitmap-top-bit-tests` companion stays bitmap-local");
    try expectContains(sample_root_readme, "`make -C zigux phase9-runtime-bitmap-top-bit-test`");
    try expectContains(sample_root_readme, "`make -C zigux phase9-runtime-loader-shared-tests`");
    for (phase5_kobject_packet_markers) |marker| try expectContains(sample_root_readme, marker);

    try expectContains(runtime_bitmap_sample, "runtime bitmap sample review contract keeps bounded starter focus explicit");
    try expectContains(runtime_bitmap_sample, "runtime bitmap sample review contract stays aligned with the selftest packet");
    try expectContains(runtime_bitmap_sample, "runtime bitmap sample keeps bounded view summaries stable");
    try expectContains(runtime_bitmap_sample, "try std.testing.expectEqualStrings(\"runtime_bitmap\", descriptor.name);");
    try expectContains(runtime_bitmap_sample, "try std.testing.expectEqualStrings(\"lib/test_bitmap.c\", descriptor.anchor);");
    try expectContains(runtime_bitmap_sample, "try module.initWithSetBits(&.{ 0, 5, bitmap_view.bits_per_long, bitmap_view.bits_per_long + 6 });");
    try expectContains(runtime_bitmap_sample, "try std.testing.expectEqual(OperationFamily.clear_set, selftest.operation_families[0]);");
    try expectContains(runtime_bitmap_sample, "try std.testing.expect(selftest.checked_range_mutations);");
    try expectContains(runtime_bitmap_sample, "try std.testing.expect(selftest.checked_lifecycle_paths);");
    try expectContains(runtime_bitmap_sample, "try std.testing.expectEqual(@as(u32, 0), summary.first_set);");
    try expectContains(runtime_bitmap_sample, "try std.testing.expectEqual(@as(u32, 1), summary.first_zero);");
    try expectContains(runtime_bitmap_sample, "try std.testing.expectEqual(@as(u32, 4), summary.weight);");
    try expectContains(runtime_bitmap_sample, "try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, summary.nbits);");

    try expectContains(top_bit_contract_source, "runtime bitmap top-bit contract keeps the highest valid bit explicit");
    try expectContains(top_bit_contract_source, "runtime bitmap top-bit contract keeps boundary mutation and bounds checks reviewable");
    try expectContains(top_bit_contract_source, "runtime bitmap top-bit contract keeps exit-path lifecycle parity explicit");
    try expectContains(top_bit_contract_source, "summary.weight");
    try expectContains(top_bit_contract_source, "ModuleStage.initialized");
    try expectContains(top_bit_contract_source, "ModuleStage.exited");
    try expectContains(top_bit_contract_source, "BitRangeOutOfBounds");
    try expectContains(top_bit_contract_source, "InvalidLifecycleTransition");

    try expectContains(runtime_bitmap_loader, "runtime bitmap loader keeps initialized shared-request snapshots stable across later selftest activity");
    try expectContains(runtime_bitmap_loader, "runtime bitmap loader keeps selftest-complete shared-request snapshots stable across later exit activity");
    try expectContains(runtime_bitmap_loader, "runtime bitmap loader bridges the shared request lifecycle without widening bitmap claims");
    try expectContains(runtime_bitmap_loader, "runtime bitmap loader keeps shared release failures from desynchronizing loader state");
    try expectContains(runtime_bitmap_loader, "runtime bitmap loader rejects prepared shared selftest-hook drift before any local runtime handoff");
    try expectContains(runtime_bitmap_loader, "runtime bitmap loader rejects prepared shared allocator and init-flow drift before any local runtime handoff");
    try expectContains(runtime_bitmap_loader, "runtime bitmap loader rejects shared selftest-hook drift before any local runtime handoff");
    try expectContains(runtime_bitmap_loader, "runtime bitmap loader rejects shared-load-plan snapshot drift");
    try expectContains(runtime_bitmap_loader, "try std.testing.expectEqual(runtime_loader.HandoffStage.initialized, pending_plan.init_flow.handoff_stage);");
    try expectContains(runtime_bitmap_loader, "try std.testing.expectEqual(runtime_loader.HandoffStage.selftest_complete, pending_plan.init_flow.handoff_stage);");
    try expectContains(runtime_bitmap_loader, "try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, shared_request.state);");

    try expectContains(module_slice, "`zigux/tests/runtime_bitmap_module.zig`");
    try expectContains(module_slice, "`zigux/tests/runtime_bitmap_diff.zig`");
    try expectContains(module_slice, "`zigux/tests/runtime_bitmap_survey.zig`");
    try expectContains(module_slice, "`zigux/tests/runtime_bitmap_manifest.json`");
    try expectContains(module_slice, "The `zigux/tests/runtime_bitmap_diff.zig` gate owns the bounded `lib/test_bitmap.c` replay plus the selftest-complete and exit lifecycle guards");
    try expectContains(module_slice, "`zig build phase9-runtime-bitmap-top-bit-tests --build-file zigux/tests/phase9_build.zig`");
    try expectContains(module_slice, "`make -C zigux phase9-runtime-bitmap-top-bit-test`");
    try expectContains(module_slice, "bitmap-local review proof");
    try expectSurveyedCommitMarker(module_slice, manifest.surveyed_commit);
    try expectContains(module_slice, "The live runtime substrate is still missing");

    try expectContains(phase9_build, ".root_source_file = b.path(\"runtime_bitmap_module.zig\")");
    try expectContains(phase9_build, ".root_source_file = b.path(\"runtime_bitmap_diff.zig\")");
    try expectContains(phase9_build, ".root_source_file = b.path(\"runtime_bitmap_survey.zig\")");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-sample-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-module-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-diff-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-loader-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-survey-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-top-bit-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-loader-shared-tests\"");
}
