const std = @import("std");

const SurveySummary = struct {
    kretprobe_example_c_lines: usize,
    preexisting_runtime_kretprobe_test_files: usize,
    preexisting_runtime_kretprobe_sample_present: bool,
    preexisting_phase9_build_present: bool,
    preexisting_runtime_kretprobe_doc_present: bool,
};

const LifecycleBoundarySummary = struct {
    pre_execution_handoff_only: bool,
    requires_idle_registration_snapshot: bool,
    failed_exit_state_retained_until_drain: bool,
    metadata_only_registration_labels: []const []const u8,
    shared_request_surface: []const u8,
    live_registration_parity: []const u8,
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
    lifecycle_boundary_summary: LifecycleBoundarySummary,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_runtime_substrate");
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 9 runtime kretprobe survey manifest records the landed loader plan and metadata-only registration boundary" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/runtime_kretprobe_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const survey_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase9-runtime-kretprobe-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_doc);

    const module_slice_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase9-runtime-kretprobe-module-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(module_slice_doc);

    const loader_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/runtime_kretprobe_loader.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(loader_source);

    const runtime_loader_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/kernel/runtime_loader.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(runtime_loader_source);

    const phase9_build_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase9_build.zig",
        std.testing.allocator,
        .limited(96 * 1024),
    );
    defer std.testing.allocator.free(phase9_build_source);

    const makefile_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/Makefile",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(makefile_source);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P9-L17", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 9", manifest.phase);
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.kretprobe_example_c_lines >= 100);
    try std.testing.expectEqual(@as(usize, 3), manifest.survey_summary.preexisting_runtime_kretprobe_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_runtime_kretprobe_sample_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase9_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_runtime_kretprobe_doc_present);
    try std.testing.expect(manifest.lifecycle_boundary_summary.pre_execution_handoff_only);
    try std.testing.expect(manifest.lifecycle_boundary_summary.requires_idle_registration_snapshot);
    try std.testing.expect(manifest.lifecycle_boundary_summary.failed_exit_state_retained_until_drain);
    try std.testing.expectEqual(@as(usize, 2), manifest.lifecycle_boundary_summary.metadata_only_registration_labels.len);
    try std.testing.expectEqualStrings(
        "register_kretprobe",
        manifest.lifecycle_boundary_summary.metadata_only_registration_labels[0],
    );
    try std.testing.expectEqualStrings(
        "unregister_kretprobe",
        manifest.lifecycle_boundary_summary.metadata_only_registration_labels[1],
    );
    try std.testing.expectEqualStrings(
        "zigux/kernel/runtime_loader.zig",
        manifest.lifecycle_boundary_summary.shared_request_surface,
    );
    try std.testing.expectEqualStrings(
        "blocked_on_runtime_substrate",
        manifest.lifecycle_boundary_summary.live_registration_parity,
    );
    try std.testing.expect(manifest.gaps.len >= 6);

    try expectContains(survey_doc, "PHASE9_SLICE=runtime-kretprobe-survey");
    try expectContains(survey_doc, "P9-L17");
    try expectContains(survey_doc, "samples/zigux/runtime_kretprobe_loader.zig");
    try expectContains(survey_doc, "zigux/kernel/runtime_loader.zig");
    try expectContains(survey_doc, "zigux/kernel/runtime_loader_contract.zig");
    try expectContains(survey_doc, "zigux/tests/runtime_loader_allocator_init_flow.zig");
    try expectContains(survey_doc, "metadata-only labels");
    try expectContains(survey_doc, "idle registration snapshot");
    try expectContains(survey_doc, "failed-exit state");
    try expectContains(survey_doc, "active probe drains");
    try expectContains(survey_doc, "make -C zigux phase9");

    try expectContains(module_slice_doc, "PHASE9_SLICE=runtime-kretprobe-module-starter");
    try expectContains(module_slice_doc, "samples/zigux/runtime_kretprobe_loader.zig");
    try expectContains(module_slice_doc, "zigux/kernel/runtime_loader.zig");
    try expectContains(module_slice_doc, "zigux/kernel/runtime_loader_contract.zig");
    try expectContains(module_slice_doc, "zigux/tests/runtime_loader_allocator_init_flow.zig");
    try expectContains(module_slice_doc, "register_kretprobe()");
    try expectContains(module_slice_doc, "unregister_kretprobe()");
    try expectContains(module_slice_doc, "idle registration snapshot");
    try expectContains(module_slice_doc, "failed-exit state");
    try expectContains(module_slice_doc, "active probe drains");

    try expectContains(loader_source, "error.OutstandingProbeStateForLoader");
    try expectContains(loader_source, "summary.active_instances != 0 or summary.entry_timestamp_armed");

    try expectContains(runtime_loader_source, "pub const AllocatorHandoff = contract.AllocatorHandoff;");
    try expectContains(runtime_loader_source, "pub const LoadPlan = contract.LoadPlan;");
    try expectContains(runtime_loader_source, "runtime loader facade keeps the shared loader contract reachable");

    try expectContains(phase9_build_source, "phase9-runtime-kretprobe-loader-tests");
    try expectContains(phase9_build_source, "phase9-runtime-loader-facade-tests");
    try expectContains(phase9_build_source, "phase9-runtime-loader-allocator-init-flow-tests");

    try expectContains(makefile_source, "phase9-test:");
    try expectContains(makefile_source, "phase9: phase9-test");

    var runtime_test_destination_count: usize = 0;
    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_sample_module = false;
    var saw_diff_gate = false;
    var saw_loader_plan = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.startsWith(u8, gap.zigux_destination, "zigux/tests/")) {
            runtime_test_destination_count += 1;
        } else {
            try std.testing.expect(
                std.mem.startsWith(u8, gap.zigux_destination, "samples/zigux/") or
                    std.mem.startsWith(u8, gap.zigux_destination, "zigux/kernel/"),
            );
        }

        if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_runtime_substrate")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "runtime-kretprobe-sample-module")) {
            saw_sample_module = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_kretprobe.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "runtime-kretprobe-diff-gate")) {
            saw_diff_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/runtime_kretprobe_diff.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "runtime-kretprobe-loader-plan")) {
            saw_loader_plan = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_kretprobe_loader.zig", gap.zigux_destination);
            try expectContains(gap.why_now, "idle registration snapshot");
            try expectContains(gap.why_now, "failed-exit state retention");
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, gap.zigux_destination, other.zigux_destination));
        }
    }

    for (manifest.lifecycle_boundary_summary.metadata_only_registration_labels, 0..) |label, i| {
        try std.testing.expect(label.len > 0);
        for (manifest.lifecycle_boundary_summary.metadata_only_registration_labels[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, label, other));
        }
    }

    try std.testing.expect(runtime_test_destination_count >= 4);
    try std.testing.expect(starter_landed_count >= 6);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expect(blocked_count >= 1);
    try std.testing.expect(saw_sample_module);
    try std.testing.expect(saw_diff_gate);
    try std.testing.expect(saw_loader_plan);
}
