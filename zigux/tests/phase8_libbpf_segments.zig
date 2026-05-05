const std = @import("std");

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

test "phase 8 libbpf segment manifest records the roadmap gap and bounded next slices" {
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
    try std.testing.expectEqualStrings("P8-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 8", manifest.phase);
    try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c", manifest.anchor);
    try std.testing.expect(manifest.survey_summary.libbpf_c_lines >= 14000);
    try std.testing.expect(!manifest.survey_summary.preexisting_zigux_segments_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase8_libbpf_note_present);
    try std.testing.expect(manifest.survey_summary.companion_c_files.len >= 5);
    try std.testing.expectEqual(@as(usize, 6), manifest.segments.len);

    var ready_next_count: usize = 0;
    var starter_landed_count: usize = 0;
    var blocked_on_object_model_count: usize = 0;
    var deferred_high_risk_count: usize = 0;
    var saw_logging_segment = false;
    var saw_pin_path_segment = false;
    var saw_cpu_mask_segment = false;

    for (manifest.segments, 0..) |segment, i| {
        try std.testing.expect(segment.id.len > 0);
        try std.testing.expect(segment.slug.len > 0);
        try std.testing.expect(segment.kind.len > 0);
        try std.testing.expect(segment.anchor_ranges.len > 0);
        try std.testing.expect(segment.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(segment.status));
        try std.testing.expect(std.mem.startsWith(u8, segment.zigux_destination, "tools/lib/bpf/zigux_segments/"));

        if (std.mem.eql(u8, segment.status, "ready_next")) {
            ready_next_count += 1;
        }
        if (std.mem.eql(u8, segment.status, "starter_landed")) {
            starter_landed_count += 1;
        }
        if (std.mem.eql(u8, segment.status, "blocked_on_object_model")) {
            blocked_on_object_model_count += 1;
        }
        if (std.mem.eql(u8, segment.status, "deferred_high_risk")) {
            deferred_high_risk_count += 1;
        }
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

        for (manifest.segments[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, segment.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, segment.slug, other.slug));
        }
    }

    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 3), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_on_object_model_count);
    try std.testing.expectEqual(@as(usize, 2), deferred_high_risk_count);
    try std.testing.expect(saw_logging_segment);
    try std.testing.expect(saw_pin_path_segment);
    try std.testing.expect(saw_cpu_mask_segment);
}

test "phase 8 libbpf helper slice notes stay parked once the shared tooling bundle lands" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

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

    try expectContains(cpu_mask_note, "PHASE8_STATUS=parked");
    try expectContains(cpu_mask_note, "tools/lib/bpf/zigux_segments/cpu_mask.zig");
    try expectContains(cpu_mask_note, "zigux/tests/phase8_build.zig");

    try expectContains(type_names_note, "PHASE8_STATUS=parked");
    try expectContains(type_names_note, "tools/lib/bpf/zigux_segments/type_names.zig");
    try expectContains(type_names_note, "zigux/tests/phase8_build.zig");
}
