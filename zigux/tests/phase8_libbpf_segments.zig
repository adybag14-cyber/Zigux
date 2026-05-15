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

const SegmentationNote = struct {
    destination: []const u8,
    landed_scope: []const []const u8,
    queued_scope: []const []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    survey_summary: SurveySummary,
    segments: []const Segment,
    segmentation_notes: []const SegmentationNote,
};

const ExpectedCompanionFile = struct {
    path: []const u8,
    lines: usize,
};

const ExpectedSegment = struct {
    id: []const u8,
    slug: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    anchor_ranges: []const []const u8,
};

const ExpectedSegmentationNote = struct {
    destination: []const u8,
    landed_scope: []const []const u8,
    queued_scope: []const []const u8,
    why_now: []const u8,
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

fn expectCompanionFilesEqual(
    actual: []const CompanionFile,
    expected: []const ExpectedCompanionFile,
) !void {
    try std.testing.expectEqual(expected.len, actual.len);
    for (expected, actual) |expected_file, actual_file| {
        try std.testing.expectEqualStrings(expected_file.path, actual_file.path);
        try std.testing.expectEqual(expected_file.lines, actual_file.lines);
    }
}

fn expectStringListsEqual(actual: []const []const u8, expected: []const []const u8) !void {
    try std.testing.expectEqual(expected.len, actual.len);
    for (expected, actual) |expected_item, actual_item| {
        try std.testing.expectEqualStrings(expected_item, actual_item);
    }
}

fn expectSegmentsEqual(actual: []const Segment, expected: []const ExpectedSegment) !void {
    try std.testing.expectEqual(expected.len, actual.len);
    for (expected, actual) |expected_segment, actual_segment| {
        try std.testing.expectEqualStrings(expected_segment.id, actual_segment.id);
        try std.testing.expectEqualStrings(expected_segment.slug, actual_segment.slug);
        try std.testing.expectEqualStrings(expected_segment.status, actual_segment.status);
        try std.testing.expectEqualStrings(expected_segment.kind, actual_segment.kind);
        try std.testing.expectEqualStrings(
            expected_segment.zigux_destination,
            actual_segment.zigux_destination,
        );
        try std.testing.expectEqual(expected_segment.anchor_ranges.len, actual_segment.anchor_ranges.len);
        for (expected_segment.anchor_ranges, actual_segment.anchor_ranges) |expected_anchor_range, actual_anchor_range| {
            try std.testing.expectEqualStrings(expected_anchor_range, actual_anchor_range);
        }
    }
}

fn expectSegmentationNotesEqual(
    actual: []const SegmentationNote,
    expected: []const ExpectedSegmentationNote,
) !void {
    try std.testing.expectEqual(expected.len, actual.len);
    for (expected, actual) |expected_note, actual_note| {
        try std.testing.expectEqualStrings(expected_note.destination, actual_note.destination);
        try expectStringListsEqual(actual_note.landed_scope, expected_note.landed_scope);
        try expectStringListsEqual(actual_note.queued_scope, expected_note.queued_scope);
        try std.testing.expectEqualStrings(expected_note.why_now, actual_note.why_now);
    }
}

fn readFileAlloc(
    io: std.Io,
    allocator: std.mem.Allocator,
    path: []const u8,
    limit: usize,
) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, allocator, .limited(limit));
}

test "phase 8 libbpf manifest records the landed helper packet, deferred routing boundary, and segmentation note contract" {
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
    const expected_companion_files = [_]ExpectedCompanionFile{
        .{ .path = "tools/lib/bpf/bpf.c", .lines = 1419 },
        .{ .path = "tools/lib/bpf/btf.c", .lines = 6360 },
        .{ .path = "tools/lib/bpf/features.c", .lines = 727 },
        .{ .path = "tools/lib/bpf/libbpf_utils.c", .lines = 256 },
        .{ .path = "tools/lib/bpf/linker.c", .lines = 3116 },
        .{ .path = "tools/lib/bpf/netlink.c", .lines = 938 },
        .{ .path = "tools/lib/bpf/nlattr.c", .lines = 194 },
        .{ .path = "tools/lib/bpf/ringbuf.c", .lines = 684 },
    };
    const expected_segments = [_]ExpectedSegment{
        .{ .id = "P8-L15-S01", .slug = "logging-version-and-errno", .status = "starter_landed", .kind = "helper_first", .zigux_destination = "tools/lib/bpf/zigux_segments/logging.zig", .anchor_ranges = &[_][]const u8{ "tools/lib/bpf/libbpf.c:233-364", "tools/lib/bpf/libbpf_utils.c:31-84", }, },
        .{ .id = "P8-L15-S02", .slug = "pin-path-helpers", .status = "starter_landed", .kind = "helper_first", .zigux_destination = "tools/lib/bpf/zigux_segments/pin_path.zig", .anchor_ranges = &[_][]const u8{ "tools/lib/bpf/libbpf.c:2538-2565", "tools/lib/bpf/libbpf.c:9054-9352", }, },
        .{ .id = "P8-L15-S03", .slug = "cpu-mask-parsing", .status = "starter_landed", .kind = "helper_first", .zigux_destination = "tools/lib/bpf/zigux_segments/cpu_mask.zig", .anchor_ranges = &[_][]const u8{ "tools/lib/bpf/libbpf.c:14379-14480", }, },
        .{ .id = "P8-L15-S04", .slug = "type-name-helpers", .status = "starter_landed", .kind = "helper_first", .zigux_destination = "tools/lib/bpf/zigux_segments/type_names.zig", .anchor_ranges = &[_][]const u8{ "tools/lib/bpf/libbpf.c: exported attach, link, map, and program type string tables", }, },
        .{ .id = "P8-L15-S05", .slug = "fdinfo-map-info-helpers", .status = "starter_landed", .kind = "helper_first", .zigux_destination = "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig", .anchor_ranges = &[_][]const u8{ "tools/lib/bpf/libbpf.c: bpf_get_map_info_from_fdinfo() pathname and fdinfo text parsing", }, },
        .{ .id = "P8-L15-S06", .slug = "map-reuse-compatibility", .status = "starter_landed", .kind = "helper_first", .zigux_destination = "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig", .anchor_ranges = &[_][]const u8{ "tools/lib/bpf/libbpf.c: bpf_map__reuse_fd() name selection and bpf_object__reuse_map() compatibility checks", }, },
        .{ .id = "P8-L15-S07", .slug = "file-path-and-handle-bridge", .status = "deferred_high_risk", .kind = "resource_boundary", .zigux_destination = "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig", .anchor_ranges = &[_][]const u8{ "tools/lib/bpf/libbpf.c: bpf_object_prepare_token() and bpf_object__reuse_map() handle-bridging paths", }, },
        .{ .id = "P8-L15-S08", .slug = "perf-buffer-online-cpu-routing", .status = "deferred_high_risk", .kind = "interrupt_routing", .zigux_destination = "tools/lib/bpf/zigux_segments/online_cpu_routing.zig", .anchor_ranges = &[_][]const u8{ "tools/lib/bpf/libbpf.c: perf_buffer__new() online-CPU routing and perf_event setup", }, },
        .{ .id = "P8-L15-S09", .slug = "skeleton-population", .status = "blocked_on_object_model", .kind = "object_adjacent", .zigux_destination = "tools/lib/bpf/zigux_segments/skeleton.zig", .anchor_ranges = &[_][]const u8{ "tools/lib/bpf/libbpf.c:14482-14771", }, },
        .{ .id = "P8-L15-S10", .slug = "object-and-elf-loader", .status = "deferred_high_risk", .kind = "core_loader", .zigux_destination = "tools/lib/bpf/zigux_segments/object_loader.zig", .anchor_ranges = &[_][]const u8{ "tools/lib/bpf/libbpf.c:1514-2065", "tools/lib/bpf/libbpf.c:3705-4514", }, },
        .{ .id = "P8-L15-S11", .slug = "btf-relocation-and-program-load", .status = "deferred_high_risk", .kind = "verifier_facing", .zigux_destination = "tools/lib/bpf/zigux_segments/relocation.zig", .anchor_ranges = &[_][]const u8{ "tools/lib/bpf/libbpf.c:3325-3609", "tools/lib/bpf/libbpf.c:4572-9049", }, },
        .{ .id = "P8-L15-S12", .slug = "perf-buffer-poll-bookkeeping", .status = "starter_landed", .kind = "helper_adjacent", .zigux_destination = "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig", .anchor_ranges = &[_][]const u8{ "tools/lib/bpf/libbpf.c: perf_buffer__poll() wait-result classification and ordered process_records bookkeeping", }, },
    };
    const expected_segmentation_notes = [_]ExpectedSegmentationNote{
        .{
            .destination = "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
            .landed_scope = &[_][]const u8{
                "buildProcFdinfoPath() bounded /proc//fdinfo/ pathname shaping",
                "parseFdinfoLine() field splitting and trimming",
                "applyFdinfoMapInfoLine() numeric field decoding for map_type/key_size/value_size/max_entries/map_flags/map_extra",
                "parseFdinfoMapInfo() line-by-line fdinfo map metadata parsing",
                "summarizeFdinfoMapInfo() bounded completion reporting for the parsed map info packet",
                "mapReuseObservationFromFdinfo() helper-only conversion from parsed fdinfo metadata into a reusable comparison observation",
                "resolveReusedMapName() object-name retention for truncated reused-map names",
                "normalizeObservedReuseMapFlags() devmap readonly-prog normalization for reuse comparison",
                "summarizeMapReuseCompatibility() mismatch reporting for helper-only reused-map compatibility checks",
                "isMapReuseCompatible() helper-only reused-map compatibility comparison",
                "resolveReusePinnedMapAttempt() helper-only pinned-map reuse planning without procfs, bpffs, or fd side effects",
            },
            .queued_scope = &[_][]const u8{
                "direct procfs reads and descriptor ownership flow",
                "token creation, bpffs reopen flow, and other fd-handle bridge side effects",
            },
            .why_now = "The shared file-path bridge destination now records the fdinfo parsing foundation, helper-only observation shaping, reused-map compatibility summaries, and pinned-map reuse planning packet as a reviewable landed helper slice, so future surveys can keep promoting bounded bridge behavior without crossing into live descriptor or reopen side effects.",
        },
    };

    try std.testing.expectEqualStrings("P8-L15", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 8", manifest.phase);
    try std.testing.expectEqualStrings("37d0ccdc93587eab8eed84de29ad9d659c623aea", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 14771), manifest.survey_summary.libbpf_c_lines);
    try std.testing.expect(manifest.survey_summary.preexisting_zigux_segments_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase8_libbpf_note_present);
    try expectCompanionFilesEqual(manifest.survey_summary.companion_c_files, expected_companion_files[0..]);
    try expectSegmentsEqual(manifest.segments, expected_segments[0..]);
    try expectSegmentationNotesEqual(manifest.segmentation_notes, expected_segmentation_notes[0..]);
    try std.testing.expectEqual(@as(usize, 7), countSegmentsWithStatus(manifest.segments, "starter_landed"));
    try std.testing.expectEqual(@as(usize, 4), countSegmentsWithStatus(manifest.segments, "deferred_high_risk"));
    try std.testing.expectEqual(@as(usize, 1), countSegmentsWithStatus(manifest.segments, "blocked_on_object_model"));

    const routing = findSegmentBySlug(manifest.segments, "perf-buffer-online-cpu-routing") orelse return error.MissingRoutingSegment;
    try expectContains(routing.why_now, "online_cpu_routing.zig");
    try expectContains(routing.why_now, "cursor and routing-summary helper");
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

    try expectContains(phase8_note, "The manifest currently records twelve bounded segments: seven landed helper or helper-adjacent slices and five deferred or blocked follow-ons.");
    try expectContains(phase8_note, "The seven landed bounded slices are `logging-version-and-errno`, `pin-path-helpers`, `cpu-mask-parsing`, `type-name-helpers`, `fdinfo-map-info-helpers`, `map-reuse-compatibility`, and `perf-buffer-poll-bookkeeping`.");
    try expectContains(phase8_note, "current `master` also carries helper-local routing evidence in `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`");
    try expectContains(phase8_note, "advanceOnlineCpuCursor()");
    try expectContains(phase8_note, "summarizeNextOnlineCpuRoute()");
    try expectContains(phase8_note, "summarizeOnlineCpuRouting()");
    try expectContains(phase8_note, "The real current gap is now survey truthfulness about the already-landed checker packet, helper-local routing evidence, and the still-mixed contents-route stability for the landed bridge-plus-build packet, not a missing checker rule or docs-root summary.");
    try expectContains(phase8_note, "That same checker packet already keeps the landed `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` helper-local evidence explicit");
    try expectContains(phase8_note, "standalone timer or clockevent helper behavior");
    try expectContains(phase8_note, "broader timeout-sensitive routing behavior");
}

test "phase 8 libbpf survey gate keeps the landed online CPU routing helper evidence replayable" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const routing_helper = try readFileAlloc(
        io_instance.io(),
        std.testing.allocator,
        "tools/lib/bpf/zigux_segments/online_cpu_routing.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(routing_helper);

    try expectContains(routing_helper, "pub const OnlineCpuRouteAttemptDisposition = enum {");
    try expectContains(routing_helper, "pub const OnlineCpuRoutingDisposition = enum {");
    try expectContains(routing_helper, "pub fn advanceOnlineCpuCursor(");
    try expectContains(routing_helper, "pub fn summarizeNextOnlineCpuRoute(");
    try expectContains(routing_helper, "pub fn summarizeOnlineCpuRouting(");
    try expectContains(routing_helper, "test \"summarizeNextOnlineCpuRoute keeps missing buffer slots and fds explicit\" {");
    try expectContains(routing_helper, "test \"summarizeOnlineCpuRouting keeps requested subsets explicit without inventing missing buffers\" {");
    try expectContains(routing_helper, "test \"summarizeOnlineCpuRouting keeps sparse missing-slot routing non-claiming when no buffer table exists\" {");
    try expectContains(routing_helper, "test \"summarizeOnlineCpuRouting reports the first routed online CPU whose fd slot is empty\" {");
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
