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

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P9-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 9", manifest.phase);
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.kretprobe_example_c_lines >= 100);
    try std.testing.expectEqual(@as(usize, 3), manifest.survey_summary.preexisting_runtime_kretprobe_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_runtime_kretprobe_sample_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase9_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_runtime_kretprobe_doc_present);
    try std.testing.expect(manifest.lifecycle_boundary_summary.pre_execution_handoff_only);
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
