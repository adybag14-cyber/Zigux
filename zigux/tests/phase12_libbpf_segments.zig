const std = @import("std");

const SurveySummary = struct {
    libbpf_c_lines: usize,
    preexisting_phase8_test_files: usize,
    preexisting_phase8_build_present: bool,
    preexisting_phase8_libbpf_manifest_present: bool,
    preexisting_phase8_libbpf_survey_present: bool,
    preexisting_phase8_libbpf_note_present: bool,
    preexisting_type_names_zig_present: bool,
    preexisting_cpu_mask_zig_present: bool,
    preexisting_logging_zig_present: bool,
    preexisting_pin_path_zig_present: bool,
    preexisting_phase12_build_present: bool,
    preexisting_phase12_libbpf_survey_present: bool,
    preexisting_phase12_survey_note_present: bool,
    preexisting_phase12_reviewability_gate_present: bool,
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
        std.mem.eql(u8, status, "blocked_on_object_model") or
        std.mem.eql(u8, status, "deferred_high_risk");
}

test "phase12 libbpf survey manifest records the heavy-helper segmentation gap" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase12_libbpf_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P12-L15", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 12", manifest.phase);
    try std.testing.expectEqualStrings("c0ae127363e3d4e5feeb36efb665a12ece3392c7", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.libbpf_c_lines >= 14000);
    try std.testing.expectEqual(@as(usize, 7), manifest.survey_summary.preexisting_phase8_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_phase8_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase8_libbpf_manifest_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase8_libbpf_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase8_libbpf_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_type_names_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_cpu_mask_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_logging_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_pin_path_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_libbpf_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_survey_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_reviewability_gate_present);
    try std.testing.expectEqual(@as(usize, 14), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var deferred_count: usize = 0;
    var saw_build_gate = false;
    var saw_make_target = false;
    var saw_manifest_foundation = false;
    var saw_type_names_foundation = false;
    var saw_cpu_mask_foundation = false;
    var saw_perf_buffer_poll_foundation = false;
    var saw_logging_foundation = false;
    var saw_pin_path_foundation = false;
    var saw_survey_gate = false;
    var saw_reviewability_gate = false;
    var saw_survey_note = false;
    var saw_skeleton_blocker = false;
    var saw_object_loader_blocker = false;
    var saw_relocation_blocker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_object_model")) {
            blocked_count += 1;
        } else if (std.mem.eql(u8, gap.status, "deferred_high_risk")) {
            deferred_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase12-build-gate")) {
            saw_build_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase12_build.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }

        if (std.mem.eql(u8, gap.id, "phase12-make-target")) {
            saw_make_target = true;
            try std.testing.expectEqualStrings("zigux/Makefile", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }

        if (std.mem.eql(u8, gap.id, "phase12-libbpf-segment-manifest-foundation")) {
            saw_manifest_foundation = true;
            try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/manifest.json", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "helper-first") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "high-risk clusters") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-libbpf-type-name-helper-foundation")) {
            saw_type_names_foundation = true;
            try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/type_names.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "stable output semantics") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-libbpf-cpu-mask-helper-foundation")) {
            saw_cpu_mask_foundation = true;
            try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/cpu_mask.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "chunk-reader interface") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "sysfs-style buffered input") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "perf-buffer") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "direct file I/O") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-libbpf-perf-buffer-poll-helper-foundation")) {
            saw_perf_buffer_poll_foundation = true;
            try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/perf_buffer_poll.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "wait-result normalization") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ready-buffer bookkeeping") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "per-buffer slot access") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "epoll wiring") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-libbpf-logging-helper-foundation")) {
            saw_logging_foundation = true;
            try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/logging.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "print-level parsing") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "errno-string") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "stderr output") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-libbpf-pin-path-helper-foundation")) {
            saw_pin_path_foundation = true;
            try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/pin_path.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "bpffs path joining") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dot-sanitization") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "object-loader") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-libbpf-skeleton-population")) {
            saw_skeleton_blocker = true;
            try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/skeleton.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("blocked_on_object_model", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared segment catalog") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "bpf_object") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "bpf_program") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-libbpf-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase12_libbpf_segments.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }

        if (std.mem.eql(u8, gap.id, "phase12-libbpf-reviewability-gate")) {
            saw_reviewability_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase12_libbpf_reviewability.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "manifest matches") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "older Phase 8 coverage") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-libbpf-survey-note")) {
            saw_survey_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase12-libbpf-segment-survey.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }

        if (std.mem.eql(u8, gap.id, "phase12-libbpf-object-loader-and-program-load")) {
            saw_object_loader_blocker = true;
            try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/object_loader.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("blocked_on_object_model", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "loader setup") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "skeleton-population") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "object-model progress") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-libbpf-btf-relocation-and-program-load")) {
            saw_relocation_blocker = true;
            try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/relocation.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("deferred_high_risk", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "BTF fixups") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "verifier interactions") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 11), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 2), blocked_count);
    try std.testing.expectEqual(@as(usize, 1), deferred_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_make_target);
    try std.testing.expect(saw_manifest_foundation);
    try std.testing.expect(saw_type_names_foundation);
    try std.testing.expect(saw_cpu_mask_foundation);
    try std.testing.expect(saw_perf_buffer_poll_foundation);
    try std.testing.expect(saw_logging_foundation);
    try std.testing.expect(saw_pin_path_foundation);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_reviewability_gate);
    try std.testing.expect(saw_survey_note);
    try std.testing.expect(saw_skeleton_blocker);
    try std.testing.expect(saw_object_loader_blocker);
    try std.testing.expect(saw_relocation_blocker);
}

test "phase12 libbpf survey note records the full landed helper set" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-libbpf-segment-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(note);

    try std.testing.expect(std.mem.indexOf(u8, note, "five landed helper slices") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`perf_buffer_poll.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "phase12-libbpf-perf-buffer-poll-helper-foundation") != null);
}
