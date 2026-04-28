const std = @import("std");

const SurveySummary = struct {
    kretprobe_example_c_lines: usize,
    preexisting_runtime_kretprobe_test_files: usize,
    preexisting_runtime_kretprobe_sample_present: bool,
    preexisting_phase9_build_present: bool,
    preexisting_runtime_kretprobe_doc_present: bool,
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

fn readWorkspaceFile(
    io: anytype,
    allocator: std.mem.Allocator,
    path: []const u8,
    limit: usize,
) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, allocator, .limited(limit));
}

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_runtime_substrate");
}

fn isLowerHexSha(value: []const u8) bool {
    if (value.len != 40) return false;
    for (value) |byte| {
        if (!std.ascii.isHex(byte) or std.ascii.isUpper(byte)) return false;
    }
    return true;
}

test "phase 9 runtime kretprobe survey manifest records the landed loader binding and the remaining shared control blocker" {
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
    try std.testing.expect(isLowerHexSha(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.kretprobe_example_c_lines >= 100);
    try std.testing.expectEqual(@as(usize, 2), manifest.survey_summary.preexisting_runtime_kretprobe_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_runtime_kretprobe_sample_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase9_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_runtime_kretprobe_doc_present);
    try std.testing.expect(manifest.gaps.len >= 6);

    var runtime_test_destination_count: usize = 0;
    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_sample_module = false;
    var saw_diff_gate = false;
    var saw_loader_scaffold = false;
    var saw_live_loader_binding = false;
    var saw_shared_loader_controls_blocker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.startsWith(u8, gap.zigux_destination, "zigux/tests/")) {
            runtime_test_destination_count += 1;
        } else if (std.mem.startsWith(u8, gap.zigux_destination, "samples/zigux/")) {
            // Sample-side starter and loader handoff scaffolds stay under samples.
        } else if (std.mem.startsWith(u8, gap.zigux_destination, "Documentation/zigux/")) {
            // Broader shared loader-control blockers are tracked by the canonical runtime-loader gap note.
        } else {
            try std.testing.expect(std.mem.startsWith(u8, gap.zigux_destination, "zigux/kernel/"));
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
        if (std.mem.eql(u8, gap.id, "runtime-kretprobe-loader-scaffold")) {
            saw_loader_scaffold = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_kretprobe_loader.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "requires_runtime_substrate") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-kretprobe-live-loader-binding")) {
            saw_live_loader_binding = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared runtime-loader request surface") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "kretprobe loader handoff") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-kretprobe-shared-loader-controls")) {
            saw_shared_loader_controls_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_runtime_substrate", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-loader-gap-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "command-name") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "argv-policy") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, gap.zigux_destination, other.zigux_destination));
        }
    }

    try std.testing.expect(runtime_test_destination_count >= 4);
    try std.testing.expect(starter_landed_count >= 7);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expect(blocked_count >= 1);
    try std.testing.expect(saw_sample_module);
    try std.testing.expect(saw_diff_gate);
    try std.testing.expect(saw_loader_scaffold);
    try std.testing.expect(saw_live_loader_binding);
    try std.testing.expect(saw_shared_loader_controls_blocker);
}

test "phase 9 runtime kretprobe docs keep the lifecycle-summary surface explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_doc = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase9-runtime-kretprobe-survey.md",
        16 * 1024,
    );
    defer std.testing.allocator.free(survey_doc);

    const module_doc = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase9-runtime-kretprobe-module-slice.md",
        16 * 1024,
    );
    defer std.testing.allocator.free(module_doc);

    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "RuntimeKretprobeSummary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "lifecycle stage") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`init_runs`, `selftest_runs`, `exit_runs`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "active-instance state") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "latest bounded probe results") != null);

    try std.testing.expect(std.mem.indexOf(u8, module_doc, "RuntimeKretprobeSummary") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "lifecycle stage") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "`init_runs`, `selftest_runs`, `exit_runs`") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "active-instance state") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "latest bounded probe results") != null);
}