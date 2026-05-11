const std = @import("std");

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const LifecycleBoundarySummary = struct {
    pre_execution_handoff_only: bool,
    requires_idle_registration_snapshot: bool,
    failed_exit_state_retained_until_drain: bool,
    metadata_only_registration_labels: []const []const u8,
    shared_request_surface: []const u8,
    live_registration_parity: []const u8,
    prepared_snapshot_owned_by_loader_request: bool = false,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    lifecycle_boundary_summary: LifecycleBoundarySummary,
    gaps: []const Gap,
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
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

fn findGap(gaps: []const Gap, id: []const u8) ?Gap {
    for (gaps) |gap| {
        if (std.mem.eql(u8, gap.id, id)) return gap;
    }
    return null;
}

test "phase 9 runtime kretprobe survey gate restores the shipped loader review packet" {
    const manifest_json = try readRepoFileAlloc(
        std.testing.allocator,
        "zigux/tests/runtime_kretprobe_manifest.json",
        32 * 1024,
    );
    defer std.testing.allocator.free(manifest_json);

    const phase9_build = try readRepoFileAlloc(
        std.testing.allocator,
        "zigux/tests/phase9_build.zig",
        96 * 1024,
    );
    defer std.testing.allocator.free(phase9_build);

    const runtime_loader_allocator_init_flow = try readRepoFileAlloc(
        std.testing.allocator,
        "zigux/tests/runtime_loader_allocator_init_flow.zig",
        96 * 1024,
    );
    defer std.testing.allocator.free(runtime_loader_allocator_init_flow);

    const runtime_kretprobe_loader = try readRepoFileAlloc(
        std.testing.allocator,
        "samples/zigux/runtime_kretprobe_loader.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(runtime_kretprobe_loader);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P9-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 9", manifest.phase);
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("zigux/tests/runtime_*", manifest.roadmap_destinations[0]);
    try std.testing.expectEqualStrings("samples/zigux/runtime_*", manifest.roadmap_destinations[1]);

    try std.testing.expect(manifest.lifecycle_boundary_summary.pre_execution_handoff_only);
    try std.testing.expect(manifest.lifecycle_boundary_summary.requires_idle_registration_snapshot);
    try std.testing.expect(manifest.lifecycle_boundary_summary.failed_exit_state_retained_until_drain);
    try std.testing.expect(manifest.lifecycle_boundary_summary.prepared_snapshot_owned_by_loader_request);
    try std.testing.expectEqualStrings(
        "zigux/kernel/runtime_loader.zig",
        manifest.lifecycle_boundary_summary.shared_request_surface,
    );
    try std.testing.expectEqualStrings(
        "blocked_on_runtime_substrate",
        manifest.lifecycle_boundary_summary.live_registration_parity,
    );
    try std.testing.expectEqual(@as(usize, 2), manifest.lifecycle_boundary_summary.metadata_only_registration_labels.len);
    try std.testing.expectEqualStrings(
        "register_kretprobe",
        manifest.lifecycle_boundary_summary.metadata_only_registration_labels[0],
    );
    try std.testing.expectEqualStrings(
        "unregister_kretprobe",
        manifest.lifecycle_boundary_summary.metadata_only_registration_labels[1],
    );

    const loader_plan_gap = findGap(manifest.gaps, "runtime-kretprobe-loader-plan") orelse return error.MissingLoaderPlanGap;
    try std.testing.expectEqualStrings("starter_landed", loader_plan_gap.status);
    try std.testing.expectEqualStrings("runtime_loader_scaffold", loader_plan_gap.kind);
    try std.testing.expectEqualStrings("samples/zigux/runtime_kretprobe_loader.zig", loader_plan_gap.zigux_destination);
    try expectContains(loader_plan_gap.why_now, "register_kretprobe");
    try expectContains(loader_plan_gap.why_now, "unregister_kretprobe");

    const substrate_gap = findGap(manifest.gaps, "runtime-kretprobe-substrate-handoff") orelse return error.MissingSubstrateGap;
    try std.testing.expectEqualStrings("blocked_on_runtime_substrate", substrate_gap.status);
    try std.testing.expectEqualStrings("runtime_substrate", substrate_gap.kind);
    try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", substrate_gap.zigux_destination);
    try expectContains(substrate_gap.why_now, "real register_kretprobe parity");

    try expectContains(phase9_build, ".root_source_file = b.path(\"runtime_kretprobe_survey.zig\")");
    try expectContains(phase9_build, ".name = \"phase9-runtime-kretprobe-survey-tests\"");
    try expectContains(phase9_build, "runtime_kretprobe_tests_step.dependOn(&run_runtime_kretprobe_survey_tests.step);");

    try expectContains(
        runtime_loader_allocator_init_flow,
        "samples/kprobes/kretprobe_example.c",
    );
    try expectContains(
        runtime_loader_allocator_init_flow,
        "\"runtime_kretprobe\", \"samples/kprobes/kretprobe_example.c\", \"zigux_runtime_kretprobe_init\", \"zigux_runtime_kretprobe_exit\", .kernel_heap",
    );

    try expectContains(
        runtime_kretprobe_loader,
        "test \"runtime kretprobe loader keeps initialized shared-request snapshots stable across later selftest activity\"",
    );
    try expectContains(
        runtime_kretprobe_loader,
        "test \"runtime kretprobe loader keeps selftest-complete shared-request snapshots stable across later exit activity\"",
    );
    try expectContains(
        runtime_kretprobe_loader,
        "test \"runtime kretprobe loader surfaces prepared shared selftest-hook drift before any live registration claim\"",
    );
    try expectContains(
        runtime_kretprobe_loader,
        "try std.testing.expectError(error.InvalidSelftestHookEvidence, loader.requestSharedRuntimeLoad(&shared_request));",
    );
    try expectContains(
        runtime_kretprobe_loader,
        "try std.testing.expectEqual(runtime_loader.HandoffStage.initialized, pending_plan.init_flow.handoff_stage);",
    );
    try expectContains(
        runtime_kretprobe_loader,
        "try std.testing.expectEqual(runtime_loader.HandoffStage.selftest_complete, pending_plan.init_flow.handoff_stage);",
    );
}
