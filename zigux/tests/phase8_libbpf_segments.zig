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

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn countSegmentsWithStatus(segments: []const Segment, status: []const u8) usize {
    var count: usize = 0;
    for (segments) |segment| {
        if (std.mem.eql(u8, segment.status, status)) count += 1;
    }
    return count;
}

fn findSegmentBySlug(segments: []const Segment, slug: []const u8) ?Segment {
    for (segments) |segment| {
        if (std.mem.eql(u8, segment.slug, slug)) return segment;
    }
    return null;
}

fn readFileAlloc(
    io: std.Io,
    allocator: std.mem.Allocator,
    path: []const u8,
    limit: usize,
) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, allocator, .limited(limit));
}

test "phase 8 libbpf manifest records the landed helper packet and deferred routing boundary" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try readFileAlloc(
        io_instance.io(),
        std.testing.allocator,
        "tools/lib/bpf/zigux_segments/manifest.json",
        64 * 1024,
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(
        Manifest,
        std.testing.allocator,
        manifest_json,
        .{ .ignore_unknown_fields = true },
    );
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P8-L15", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 8", manifest.phase);
    try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 14771), manifest.survey_summary.libbpf_c_lines);
    try std.testing.expect(manifest.survey_summary.preexisting_zigux_segments_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase8_libbpf_note_present);
    try std.testing.expectEqual(@as(usize, 8), manifest.survey_summary.companion_c_files.len);
    try std.testing.expectEqual(@as(usize, 12), manifest.segments.len);
    try std.testing.expectEqual(@as(usize, 7), countSegmentsWithStatus(manifest.segments, "starter_landed"));
    try std.testing.expectEqual(@as(usize, 4), countSegmentsWithStatus(manifest.segments, "deferred_high_risk"));
    try std.testing.expectEqual(@as(usize, 1), countSegmentsWithStatus(manifest.segments, "blocked_on_object_model"));

    const fdinfo_helpers = findSegmentBySlug(manifest.segments, "fdinfo-map-info-helpers") orelse
        return error.MissingFdinfoHelpersSegment;
    try std.testing.expectEqualStrings("starter_landed", fdinfo_helpers.status);
    try std.testing.expectEqualStrings(
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        fdinfo_helpers.zigux_destination,
    );

    const map_reuse = findSegmentBySlug(manifest.segments, "map-reuse-compatibility") orelse
        return error.MissingMapReuseSegment;
    try std.testing.expectEqualStrings("starter_landed", map_reuse.status);
    try std.testing.expectEqualStrings(
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        map_reuse.zigux_destination,
    );

    const routing = findSegmentBySlug(manifest.segments, "perf-buffer-online-cpu-routing") orelse
        return error.MissingRoutingSegment;
    try std.testing.expectEqualStrings("deferred_high_risk", routing.status);
    try std.testing.expectEqualStrings(
        "tools/lib/bpf/zigux_segments/online_cpu_routing.zig",
        routing.zigux_destination,
    );
    try expectContains(routing.why_now, "online_cpu_routing.zig");
    try expectContains(routing.why_now, "cursor and routing-summary helper");

    const perf_buffer_poll = findSegmentBySlug(manifest.segments, "perf-buffer-poll-bookkeeping") orelse
        return error.MissingPerfBufferPollSegment;
    try std.testing.expectEqualStrings("starter_landed", perf_buffer_poll.status);
    try std.testing.expectEqualStrings(
        "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        perf_buffer_poll.zigux_destination,
    );
}

test "phase 8 libbpf survey note keeps the current landed count and helper-local routing evidence explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const phase8_note = try readFileAlloc(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase8-libbpf-segment-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(phase8_note);

    try expectContains(
        phase8_note,
        "The manifest currently records twelve bounded segments: seven landed helper or helper-adjacent slices and five deferred or blocked follow-ons.",
    );
    try expectContains(
        phase8_note,
        "The seven landed bounded slices are `logging-version-and-errno`, `pin-path-helpers`, `cpu-mask-parsing`, `type-name-helpers`, `fdinfo-map-info-helpers`, `map-reuse-compatibility`, and `perf-buffer-poll-bookkeeping`.",
    );
    try expectContains(
        phase8_note,
        "current `master` also carries helper-local routing evidence in `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`",
    );
    try expectContains(phase8_note, "advanceOnlineCpuCursor()");
    try expectContains(phase8_note, "summarizeOnlineCpuRouting()");
    try expectContains(
        phase8_note,
        "The real current gap is now survey truthfulness about the already-landed checker packet and helper-local routing evidence, not a missing checker rule or docs-root summary.",
    );
    try expectContains(
        phase8_note,
        "That same checker packet should also keep the landed `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` helper-local evidence explicit",
    );
    try expectContains(phase8_note, "standalone timer or clockevent helper behavior");
    try expectContains(phase8_note, "broader timeout-sensitive routing behavior");
}

test "phase 8 libbpf survey note does not regress to the older ready-next wording" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const phase8_note = try readFileAlloc(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase8-libbpf-segment-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(phase8_note);

    try expectNotContains(phase8_note, "five landed bounded slices");
    try expectNotContains(phase8_note, "stay queued helper-first catalog entries");
    try expectNotContains(phase8_note, "no longer because the bridge packet paths are missing");
    try expectNotContains(phase8_note, "fdinfo-only surface");
}
