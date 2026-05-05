const std = @import("std");

const expected_surveyed_commit = "7361ac51374149a96b7a7a2c6ea3c995d8cc1231";

const CompanionFile = struct {
    path: []const u8,
    lines: usize,
};

const SurveySummary = struct {
    libbpf_c_lines: usize,
    preexisting_zigux_segments_present: bool,
    preexisting_phase8_libbpf_note_present: bool,
    companion_c_files: []const CompanionFile,
};

const Segment = struct {
    id: []const u8,
    slug: []const u8,
    status: []const u8,
    kind: []const u8,
    anchor_ranges: []const []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    survey_summary: SurveySummary,
    segments: []const Segment,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "blocked_on_object_model") or
        std.mem.eql(u8, status, "deferred_high_risk");
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectCompanionCatalog(companion_c_files: []const CompanionFile) !void {
    const expected_paths = [_][]const u8{
        "tools/lib/bpf/bpf.c",
        "tools/lib/bpf/btf.c",
        "tools/lib/bpf/features.c",
        "tools/lib/bpf/libbpf_utils.c",
        "tools/lib/bpf/linker.c",
        "tools/lib/bpf/netlink.c",
        "tools/lib/bpf/nlattr.c",
        "tools/lib/bpf/ringbuf.c",
    };

    try std.testing.expectEqual(expected_paths.len, companion_c_files.len);

    for (expected_paths, 0..) |expected_path, index| {
        const companion = companion_c_files[index];
        try std.testing.expectEqualStrings(expected_path, companion.path);
        try std.testing.expect(companion.lines > 0);

        for (companion_c_files[index + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, companion.path, other.path));
        }
    }
}

test "phase 8 libbpf segment manifest records the current helper-first catalog" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "tools/lib/bpf/zigux_segments/manifest.json",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P8-L15", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 8", manifest.phase);
    try std.testing.expectEqualStrings(expected_surveyed_commit, manifest.surveyed_commit);
    try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c", manifest.anchor);
    try std.testing.expect(manifest.survey_summary.libbpf_c_lines >= 14000);
    try std.testing.expect(!manifest.survey_summary.preexisting_zigux_segments_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase8_libbpf_note_present);
    try expectCompanionCatalog(manifest.survey_summary.companion_c_files);
    try std.testing.expectEqual(@as(usize, 12), manifest.segments.len);

    var ready_next_count: usize = 0;
    var starter_landed_count: usize = 0;
    var blocked_on_object_model_count: usize = 0;
    var deferred_high_risk_count: usize = 0;
    var saw_logging_segment = false;
    var saw_pin_path_segment = false;
    var saw_cpu_mask_segment = false;
    var saw_type_names_segment = false;
    var saw_fdinfo_segment = false;
    var saw_map_reuse_segment = false;
    var saw_file_path_boundary = false;
    var saw_perf_buffer_boundary = false;
    var saw_perf_buffer_poll_segment = false;

    for (manifest.segments, 0..) |segment, i| {
        try std.testing.expect(segment.id.len > 0);
        try std.testing.expect(segment.slug.len > 0);
        try std.testing.expect(segment.kind.len > 0);
        try std.testing.expect(segment.anchor_ranges.len > 0);
        try std.testing.expect(segment.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(segment.status));
        try std.testing.expect(std.mem.startsWith(u8, segment.zigux_destination, "tools/lib/bpf/zigux_segments/"));

        if (std.mem.eql(u8, segment.status, "ready_next")) ready_next_count += 1;
        if (std.mem.eql(u8, segment.status, "starter_landed")) starter_landed_count += 1;
        if (std.mem.eql(u8, segment.status, "blocked_on_object_model")) blocked_on_object_model_count += 1;
        if (std.mem.eql(u8, segment.status, "deferred_high_risk")) deferred_high_risk_count += 1;

        if (std.mem.eql(u8, segment.slug, "cpu-mask-parsing")) {
            saw_cpu_mask_segment = true;
            try std.testing.expectEqualStrings("starter_landed", segment.status);
            try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/cpu_mask.zig", segment.zigux_destination);
        }
        if (std.mem.eql(u8, segment.slug, "logging-version-and-errno")) {
            saw_logging_segment = true;
            try std.testing.expectEqualStrings("starter_landed", segment.status);
            try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/logging.zig", segment.zigux_destination);
        }
        if (std.mem.eql(u8, segment.slug, "pin-path-helpers")) {
            saw_pin_path_segment = true;
            try std.testing.expectEqualStrings("starter_landed", segment.status);
            try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/pin_path.zig", segment.zigux_destination);
        }
        if (std.mem.eql(u8, segment.slug, "type-name-helpers")) {
            saw_type_names_segment = true;
            try std.testing.expectEqualStrings("starter_landed", segment.status);
            try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/type_names.zig", segment.zigux_destination);
        }
        if (std.mem.eql(u8, segment.slug, "fdinfo-map-info-helpers")) {
            saw_fdinfo_segment = true;
            try std.testing.expectEqualStrings("ready_next", segment.status);
            try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig", segment.zigux_destination);
        }
        if (std.mem.eql(u8, segment.slug, "map-reuse-compatibility")) {
            saw_map_reuse_segment = true;
            try std.testing.expectEqualStrings("ready_next", segment.status);
            try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig", segment.zigux_destination);
        }
        if (std.mem.eql(u8, segment.slug, "file-path-and-handle-bridge")) {
            saw_file_path_boundary = true;
            try std.testing.expectEqualStrings("deferred_high_risk", segment.status);
        }
        if (std.mem.eql(u8, segment.slug, "perf-buffer-online-cpu-routing")) {
            saw_perf_buffer_boundary = true;
            try std.testing.expectEqualStrings("deferred_high_risk", segment.status);
        }
        if (std.mem.eql(u8, segment.slug, "perf-buffer-poll-bookkeeping")) {
            saw_perf_buffer_poll_segment = true;
            try std.testing.expectEqualStrings("starter_landed", segment.status);
            try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/perf_buffer_poll.zig", segment.zigux_destination);
        }

        for (manifest.segments[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, segment.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, segment.slug, other.slug));
        }
    }

    try std.testing.expectEqual(@as(usize, 2), ready_next_count);
    try std.testing.expectEqual(@as(usize, 5), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_on_object_model_count);
    try std.testing.expectEqual(@as(usize, 4), deferred_high_risk_count);
    try std.testing.expect(saw_logging_segment);
    try std.testing.expect(saw_pin_path_segment);
    try std.testing.expect(saw_cpu_mask_segment);
    try std.testing.expect(saw_type_names_segment);
    try std.testing.expect(saw_fdinfo_segment);
    try std.testing.expect(saw_map_reuse_segment);
    try std.testing.expect(saw_file_path_boundary);
    try std.testing.expect(saw_perf_buffer_boundary);
    try std.testing.expect(saw_perf_buffer_poll_segment);
}

test "phase 8 libbpf survey note keeps segmented helper-first rollout explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const phase8_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase8-libbpf-segment-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(phase8_note);

    try expectContains(phase8_note, "segmented rollout instead of a single-file port attempt");
    try expectContains(phase8_note, "helper-first clusters with stable text or path behavior");
    try expectContains(phase8_note, "first realistic Zigux entry points are helper-first clusters");
    try expectContains(phase8_note, "This survey slice does not yet claim:");
    try expectContains(phase8_note, "any direct Zig port of `tools/lib/bpf/libbpf.c`");
}

test "phase 8 libbpf survey note stays aligned with the landed helper packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const phase8_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase8-libbpf-segment-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(phase8_note);

    const cpu_mask_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase8-libbpf-cpu-mask-slice.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(cpu_mask_note);

    const type_names_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase8-bpf-type-names-slice.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(type_names_note);

    try expectContains(phase8_note, expected_surveyed_commit);
    try expectContains(phase8_note, "PHASE8_STATUS=parked");
    try expectContains(phase8_note, "tools/lib/bpf/zigux_segments/manifest.json");
    try expectContains(phase8_note, "tools/lib/bpf/zigux_segments/cpu_mask.zig");
    try expectContains(phase8_note, "tools/lib/bpf/zigux_segments/logging.zig");
    try expectContains(phase8_note, "tools/lib/bpf/zigux_segments/pin_path.zig");
    try expectContains(phase8_note, "tools/lib/bpf/zigux_segments/type_names.zig");
    try expectContains(phase8_note, "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig");
    try expectContains(phase8_note, "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig");
    try expectContains(phase8_note, "zigux/tests/phase8_file_path_handle_bridge.zig");
    try expectContains(phase8_note, "zigux/tests/phase8_bpf_type_names.zig");
    try expectContains(phase8_note, "zigux/tests/phase8_perf_buffer_poll.zig");
    try expectContains(phase8_note, "zigux/tests/phase8_perf_buffer_poll_only_build.zig");
    try expectContains(phase8_note, "make -C zigux phase8-libbpf-segments-test");
    try expectContains(phase8_note, "zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all");
    try expectContains(phase8_note, "make -C zigux phase8-perf-buffer-poll-test");
    try expectContains(phase8_note, "zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all");
    try expectContains(phase8_note, "make -C zigux phase8-test");
    try expectContains(phase8_note, "zig build test --build-file zigux/tests/phase8_build.zig --summary all");
    try expectContains(phase8_note, "fdinfo-map-info-helpers");
    try expectContains(phase8_note, "map-reuse-compatibility");
    try expectContains(phase8_note, "file-path-and-handle-bridge");
    try expectContains(phase8_note, "perf-buffer-online-cpu-routing");
    try expectContains(phase8_note, "perf-buffer-poll-bookkeeping");
    try expectContains(phase8_note, "The manifest currently records twelve bounded segments");
    try expectContains(phase8_note, "five landed bounded slices");
    try expectContains(phase8_note, "stay queued helper-first catalog entries");
    try expectContains(phase8_note, "standalone timer or clockevent helper behavior");

    try expectContains(cpu_mask_note, "PHASE8_STATUS=parked");
    try expectContains(cpu_mask_note, "tools/lib/bpf/zigux_segments/cpu_mask.zig");
    try expectContains(cpu_mask_note, "zigux/tests/phase8_build.zig");
    try expectContains(cpu_mask_note, "perf-buffer or feature-probe integration");

    try expectContains(type_names_note, "PHASE8_STATUS=parked");
    try expectContains(type_names_note, "tools/lib/bpf/zigux_segments/type_names.zig");
    try expectContains(type_names_note, "zigux/tests/phase8_build.zig");
}
