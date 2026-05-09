const std = @import("std");

const expected_surveyed_commit = "c11221dc7a68d7511ae1c69d64b3f08528287ed8";

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

const SegmentationNote = struct {
    destination: []const u8,
    landed_scope: []const []const u8,
    queued_scope: []const []const u8,
    why_now: []const u8,
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
    segmentation_notes: []const SegmentationNote,
    segments: []const Segment,
};

const ExpectedCompanionFile = struct {
    path: []const u8,
    lines: usize,
};

const ExpectedSegmentationNote = struct {
    destination: []const u8,
    landed_scope: []const []const u8,
    queued_scope: []const []const u8,
    why_now_fragment: []const u8,
};

const ExpectedSegment = struct {
    id: []const u8,
    slug: []const u8,
    status: []const u8,
    kind: []const u8,
    anchor_ranges: []const []const u8,
    zigux_destination: []const u8,
};

const expected_companion_c_files = [_]ExpectedCompanionFile{
    .{ .path = "tools/lib/bpf/bpf.c", .lines = 1419 },
    .{ .path = "tools/lib/bpf/btf.c", .lines = 6360 },
    .{ .path = "tools/lib/bpf/features.c", .lines = 727 },
    .{ .path = "tools/lib/bpf/libbpf_utils.c", .lines = 256 },
    .{ .path = "tools/lib/bpf/linker.c", .lines = 3116 },
    .{ .path = "tools/lib/bpf/netlink.c", .lines = 938 },
    .{ .path = "tools/lib/bpf/nlattr.c", .lines = 194 },
    .{ .path = "tools/lib/bpf/ringbuf.c", .lines = 684 },
};

const expected_file_path_landed_scope = [_][]const u8{
    "buildProcFdinfoPath() bounded /proc/<pid>/fdinfo/<fd> pathname shaping",
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
};

const expected_file_path_queued_scope = [_][]const u8{
    "direct procfs reads and descriptor ownership flow",
    "token creation, bpffs reopen flow, and other fd-handle bridge side effects",
};

const expected_segmentation_notes = [_]ExpectedSegmentationNote{
    .{
        .destination = "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        .landed_scope = expected_file_path_landed_scope[0..],
        .queued_scope = expected_file_path_queued_scope[0..],
        .why_now_fragment = "future surveys can keep promoting bounded bridge behavior",
    },
};

const expected_segments = [_]ExpectedSegment{
    .{
        .id = "P8-L15-S01",
        .slug = "logging-version-and-errno",
        .status = "starter_landed",
        .kind = "helper_first",
        .anchor_ranges = &.{
            "tools/lib/bpf/libbpf.c:233-364",
            "tools/lib/bpf/libbpf_utils.c:31-84",
        },
        .zigux_destination = "tools/lib/bpf/zigux_segments/logging.zig",
    },
    .{
        .id = "P8-L15-S02",
        .slug = "pin-path-helpers",
        .status = "starter_landed",
        .kind = "helper_first",
        .anchor_ranges = &.{
            "tools/lib/bpf/libbpf.c:2538-2565",
            "tools/lib/bpf/libbpf.c:9054-9352",
        },
        .zigux_destination = "tools/lib/bpf/zigux_segments/pin_path.zig",
    },
    .{
        .id = "P8-L15-S03",
        .slug = "cpu-mask-parsing",
        .status = "starter_landed",
        .kind = "helper_first",
        .anchor_ranges = &.{
            "tools/lib/bpf/libbpf.c:14379-14480",
        },
        .zigux_destination = "tools/lib/bpf/zigux_segments/cpu_mask.zig",
    },
    .{
        .id = "P8-L15-S04",
        .slug = "type-name-helpers",
        .status = "starter_landed",
        .kind = "helper_first",
        .anchor_ranges = &.{
            "tools/lib/bpf/libbpf.c: exported attach, link, map, and program type string tables",
        },
        .zigux_destination = "tools/lib/bpf/zigux_segments/type_names.zig",
    },
    .{
        .id = "P8-L15-S05",
        .slug = "fdinfo-map-info-helpers",
        .status = "starter_landed",
        .kind = "helper_first",
        .anchor_ranges = &.{
            "tools/lib/bpf/libbpf.c: bpf_get_map_info_from_fdinfo() pathname and fdinfo text parsing",
        },
        .zigux_destination = "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    },
    .{
        .id = "P8-L15-S06",
        .slug = "map-reuse-compatibility",
        .status = "starter_landed",
        .kind = "helper_first",
        .anchor_ranges = &.{
            "tools/lib/bpf/libbpf.c: bpf_map__reuse_fd() name selection and bpf_object__reuse_map() compatibility checks",
        },
        .zigux_destination = "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    },
    .{
        .id = "P8-L15-S07",
        .slug = "file-path-and-handle-bridge",
        .status = "deferred_high_risk",
        .kind = "resource_boundary",
        .anchor_ranges = &.{
            "tools/lib/bpf/libbpf.c: bpf_object_prepare_token() and bpf_object__reuse_map() handle-bridging paths",
        },
        .zigux_destination = "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    },
    .{
        .id = "P8-L15-S08",
        .slug = "perf-buffer-online-cpu-routing",
        .status = "deferred_high_risk",
        .kind = "interrupt_routing",
        .anchor_ranges = &.{
            "tools/lib/bpf/libbpf.c: perf_buffer__new() online-CPU routing and perf_event setup",
        },
        .zigux_destination = "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    },
    .{
        .id = "P8-L15-S09",
        .slug = "skeleton-population",
        .status = "blocked_on_object_model",
        .kind = "object_adjacent",
        .anchor_ranges = &.{
            "tools/lib/bpf/libbpf.c:14482-14771",
        },
        .zigux_destination = "tools/lib/bpf/zigux_segments/skeleton.zig",
    },
    .{
        .id = "P8-L15-S10",
        .slug = "object-and-elf-loader",
        .status = "deferred_high_risk",
        .kind = "core_loader",
        .anchor_ranges = &.{
            "tools/lib/bpf/libbpf.c:1514-2065",
            "tools/lib/bpf/libbpf.c:3705-4514",
        },
        .zigux_destination = "tools/lib/bpf/zigux_segments/object_loader.zig",
    },
    .{
        .id = "P8-L15-S11",
        .slug = "btf-relocation-and-program-load",
        .status = "deferred_high_risk",
        .kind = "verifier_facing",
        .anchor_ranges = &.{
            "tools/lib/bpf/libbpf.c:3325-3609",
            "tools/lib/bpf/libbpf.c:4572-9049",
        },
        .zigux_destination = "tools/lib/bpf/zigux_segments/relocation.zig",
    },
    .{
        .id = "P8-L15-S12",
        .slug = "perf-buffer-poll-bookkeeping",
        .status = "starter_landed",
        .kind = "helper_adjacent",
        .anchor_ranges = &.{
            "tools/lib/bpf/libbpf.c: perf_buffer__poll() wait-result classification and ordered process_records bookkeeping",
        },
        .zigux_destination = "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    },
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    if (needle.len == 0) return 0;

    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }

    return count;
}

fn expectContainsExactlyOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(haystack, needle));
}

fn requireSection(haystack: []const u8, start_marker: []const u8, end_marker: []const u8) ![]const u8 {
    const start = std.mem.indexOf(u8, haystack, start_marker) orelse return error.MissingSectionStart;
    const content_start = start + start_marker.len;
    const end = std.mem.indexOfPos(u8, haystack, content_start, end_marker) orelse return error.MissingSectionEnd;
    return haystack[content_start..end];
}

fn expectStringSliceCatalog(expected: []const []const u8, actual: []const []const u8) !void {
    try std.testing.expectEqual(expected.len, actual.len);
    for (expected, actual) |expected_item, actual_item| {
        try std.testing.expectEqualStrings(expected_item, actual_item);
    }
}

fn expectCompanionCatalog(companion_c_files: []const CompanionFile) !void {
    try std.testing.expectEqual(expected_companion_c_files.len, companion_c_files.len);

    for (expected_companion_c_files, companion_c_files) |expected_companion, actual_companion| {
        try std.testing.expectEqualStrings(expected_companion.path, actual_companion.path);
        try std.testing.expectEqual(expected_companion.lines, actual_companion.lines);
    }
}

fn expectSegmentationNotes(segmentation_notes: []const SegmentationNote) !void {
    try std.testing.expectEqual(expected_segmentation_notes.len, segmentation_notes.len);

    for (expected_segmentation_notes, segmentation_notes) |expected_note, actual_note| {
        try std.testing.expectEqualStrings(expected_note.destination, actual_note.destination);
        try expectStringSliceCatalog(expected_note.landed_scope, actual_note.landed_scope);
        try expectStringSliceCatalog(expected_note.queued_scope, actual_note.queued_scope);
        try expectContains(actual_note.why_now, expected_note.why_now_fragment);
    }
}

fn expectSegmentCatalog(segments: []const Segment) !void {
    try std.testing.expectEqual(expected_segments.len, segments.len);

    for (expected_segments, segments) |expected_segment, actual_segment| {
        try std.testing.expectEqualStrings(expected_segment.id, actual_segment.id);
        try std.testing.expectEqualStrings(expected_segment.slug, actual_segment.slug);
        try std.testing.expectEqualStrings(expected_segment.status, actual_segment.status);
        try std.testing.expectEqualStrings(expected_segment.kind, actual_segment.kind);
        try std.testing.expectEqualStrings(expected_segment.zigux_destination, actual_segment.zigux_destination);
        try expectStringSliceCatalog(expected_segment.anchor_ranges, actual_segment.anchor_ranges);
        try std.testing.expect(actual_segment.why_now.len > 0);
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

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{ .ignore_unknown_fields = true });
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P8-L15", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 8", manifest.phase);
    try std.testing.expectEqualStrings(expected_surveyed_commit, manifest.surveyed_commit);
    try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 14771), manifest.survey_summary.libbpf_c_lines);
    try std.testing.expect(!manifest.survey_summary.preexisting_zigux_segments_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase8_libbpf_note_present);
    try expectCompanionCatalog(manifest.survey_summary.companion_c_files);
    try expectSegmentationNotes(manifest.segmentation_notes);
    try expectSegmentCatalog(manifest.segments);
    try expectContains(manifest_json, "next explicit promotable helper slice");
    try expectContains(manifest_json, "shared bridge packet now covers the reused-map name chooser");
    try expectContains(manifest_json, "bounded fdinfo helper foundation plus the helper-only reuse packet");
    try expectContains(manifest_json, "stays deferred beside the bounded perf-buffer poll bookkeeping adjunct");
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

test "phase 8 libbpf survey note stays aligned with the landed helper packet and workflow shards" {
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

    const logging_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase8-logging-slice.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(logging_note);

    const type_names_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase8-bpf-type-names-slice.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(type_names_note);

    const bridge_boundary_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(bridge_boundary_note);

    const perf_buffer_poll_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(perf_buffer_poll_note);

    const workflow_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        ".github/workflows/zigux-bootstrap.yml",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(workflow_note);

    const makefile_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/Makefile",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(makefile_note);

    const cpu_mask_only_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase8_cpu_mask_only_build.zig",
        std.testing.allocator,
        .limited(8 * 1024),
    );
    defer std.testing.allocator.free(cpu_mask_only_build);

    const product_boundary = try requireSection(
        phase8_note,
        "product boundary:\n",
        "\n## Why this slice exists",
    );

    try expectContains(phase8_note, expected_surveyed_commit);
    try expectContains(phase8_note, "PHASE8_STATUS=parked");
    try expectContains(phase8_note, "tools/lib/bpf/zigux_segments/manifest.json");
    try expectContains(phase8_note, "tools/lib/bpf/zigux_segments/cpu_mask.zig");
    try expectContains(phase8_note, "tools/lib/bpf/zigux_segments/logging.zig");
    try expectContains(phase8_note, "tools/lib/bpf/zigux_segments/pin_path.zig");
    try expectContains(phase8_note, "tools/lib/bpf/zigux_segments/type_names.zig");
    try expectContains(phase8_note, "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig");
    try expectContains(phase8_note, "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig");
    try expectContains(phase8_note, "tools/lib/bpf/zigux_segments/verify.zig");
    try expectContains(phase8_note, "Documentation/zigux/phase8-logging-slice.md");
    try expectContains(phase8_note, "Documentation/zigux/phase8-file-path-handle-bridge-slice.md");
    try expectContains(phase8_note, "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md");
    try expectContains(phase8_note, "zigux/tests/phase8_cpu_mask_only_build.zig");
    try expectContains(phase8_note, "zigux/tests/phase8_file_path_handle_bridge.zig");
    try expectContains(phase8_note, "zigux/tests/phase8_bpf_type_names.zig");
    try expectContains(phase8_note, "zigux/tests/phase8_perf_buffer_poll.zig");
    try expectContains(phase8_note, "zigux/tests/phase8_perf_buffer_poll_only_build.zig");
    try expectContainsExactlyOnce(
        product_boundary,
        "  - `zigux/tests/phase8_libbpf_segments_only_build.zig`\n",
    );
    try expectContains(phase8_note, "make -C zigux phase8-cpu-mask-test");
    try expectContains(phase8_note, "zig build test --build-file zigux/tests/phase8_cpu_mask_only_build.zig --summary all");
    try expectContains(phase8_note, "make -C zigux phase8-libbpf-segments-test");
    try expectContains(phase8_note, "zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all");
    try expectContains(phase8_note, "make -C zigux phase8-file-path-handle-bridge-test");
    try expectContains(phase8_note, "zig build test --build-file zigux/tests/phase8_file_path_handle_bridge_only_build.zig --summary all");
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
    try expectContains(phase8_note, "six landed bounded slices");
    try expectContains(phase8_note, "four helper-first starters, one shared file-path bridge helper packet, and one perf-buffer poll adjunct");
    try expectContains(phase8_note, "`fdinfo-map-info-helpers` has now joined the landed bridge packet");
    try expectContains(phase8_note, "`map-reuse-compatibility` has now joined the landed bridge packet");
    try expectContains(phase8_note, "helper-only reused-map name resolution");
    try expectContains(phase8_note, "bounded fdinfo helper packet");
    try expectContains(phase8_note, "resource-boundary packet still stays deferred");
    try expectContains(phase8_note, "standalone timer or clockevent helper behavior");
    try expectContains(phase8_note, "the logging helper now also carries a dedicated parked slice note at `Documentation/zigux/phase8-logging-slice.md`");

    try expectContains(cpu_mask_note, "PHASE8_STATUS=parked");
    try expectContains(cpu_mask_note, "tools/lib/bpf/zigux_segments/cpu_mask.zig");
    try expectContains(cpu_mask_note, "make -C zigux phase8-cpu-mask-test");
    try expectContains(cpu_mask_note, "zigux/tests/phase8_cpu_mask_only_build.zig");
    try expectContains(cpu_mask_note, "zig build test --build-file zigux/tests/phase8_cpu_mask_only_build.zig --summary all");
    try expectContains(cpu_mask_note, "zigux/tests/phase8_build.zig");
    try expectContains(cpu_mask_note, "perf-buffer or feature-probe integration");

    try expectContains(logging_note, "PHASE8_STATUS=parked");
    try expectContains(logging_note, "tools/lib/bpf/zigux_segments/logging.zig");
    try expectContains(logging_note, "zigux/tests/phase8_logging.zig");
    try expectContains(logging_note, "zig test tools/lib/bpf/zigux_segments/logging.zig");
    try expectContains(logging_note, "make -C zigux phase8-test");
    try expectContains(logging_note, "libbpf-specific custom error text only");
    try expectContains(logging_note, "direct environment reads, stderr output, or print callbacks");

    try expectContains(type_names_note, "PHASE8_STATUS=parked");
    try expectContains(type_names_note, "tools/lib/bpf/zigux_segments/type_names.zig");
    try expectContains(type_names_note, "zigux/tests/phase8_build.zig");

    try expectContains(bridge_boundary_note, "PHASE8_STATUS=parked");
    try expectContains(bridge_boundary_note, "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig");
    try expectContains(bridge_boundary_note, "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig");
    try expectContains(bridge_boundary_note, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    try expectContains(bridge_boundary_note, "zigux/tests/phase8_perf_buffer_poll.zig");
    try expectContains(bridge_boundary_note, "make -C zigux phase8-validate");
    try expectContains(bridge_boundary_note, "make -C zigux phase8-file-path-handle-bridge-test");
    try expectContains(bridge_boundary_note, "make -C zigux phase8-perf-buffer-poll-test");
    try expectContains(bridge_boundary_note, "zig build test --build-file zigux/tests/phase8_file_path_handle_bridge_only_build.zig --summary all");
    try expectContains(bridge_boundary_note, "zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all");
    try expectContains(bridge_boundary_note, "zig build test --build-file zigux/tests/phase8_build.zig --summary all");
    try expectContains(bridge_boundary_note, "make -C zigux phase8");
    try expectContains(bridge_boundary_note, "perf-buffer-online-cpu-routing");
    try expectContains(bridge_boundary_note, "/sys/devices/system/cpu/online");
    try expectContains(bridge_boundary_note, "cached `/sys/devices/system/cpu/possible` counts via `libbpf_num_possible_cpus()`");
    try expectContains(bridge_boundary_note, "online CPU filtering");
    try expectContains(bridge_boundary_note, "per-CPU perf-event-array map updates");
    try expectContains(bridge_boundary_note, "per-CPU `perf_event_open()` setup");
    try expectContains(bridge_boundary_note, "perf-buffer ring `mmap()` setup");
    try expectContains(bridge_boundary_note, "`PERF_EVENT_IOC_ENABLE` enablement");
    try expectContains(bridge_boundary_note, "epoll-backed perf FD registration");
    try expectContains(bridge_boundary_note, "poll-loop ownership beyond the bounded `perf_buffer__poll(timeout_ms)` helper packet");
    try expectContains(bridge_boundary_note, "standalone timer or clockevent helper behavior");
    try expectContains(bridge_boundary_note, "fd close or ownership semantics");

    try expectContains(perf_buffer_poll_note, "PHASE8_STATUS=parked");
    try expectContains(perf_buffer_poll_note, "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig");
    try expectContains(perf_buffer_poll_note, "make -C zigux phase8-perf-buffer-poll-test");
    try expectContains(perf_buffer_poll_note, "no standalone timer helper");
    try expectContains(perf_buffer_poll_note, "no standalone clockevent helper");

    try expectContains(workflow_note, "Validate Phase 8 tooling packet");
    try expectContains(workflow_note, "Run focused Phase 8 help and kallsyms tests");
    try expectContains(workflow_note, "Run focused Phase 8 libbpf shard tests");
    try expectContains(workflow_note, "make -C zigux phase8-file-path-handle-bridge-test");
    try expectContains(workflow_note, "make -C zigux phase8-libbpf-segments-test");
    try expectContains(workflow_note, "make -C zigux phase8-perf-buffer-poll-test");
    try expectContains(workflow_note, "Run Phase 8 tooling tests");
    try expectContains(workflow_note, "zig build test --build-file zigux/tests/phase8_build.zig --summary all");

    try expectContains(makefile_note, "phase8-cpu-mask-test:");
    try expectContains(makefile_note, "$(ZIG) build test --build-file zigux/tests/phase8_cpu_mask_only_build.zig --summary all");
    try expectContains(makefile_note, "phase8: phase8-validate phase8-test phase8-cpu-mask-test phase8-file-path-handle-bridge-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test");

    try expectContains(cpu_mask_only_build, "../../tools/lib/bpf/zigux_segments/cpu_mask.zig");
    try expectContains(cpu_mask_only_build, "phase8_cpu_mask.zig");
    try expectContains(cpu_mask_only_build, "phase8-cpu-mask-tests");
    try expectContains(cpu_mask_only_build, "Run focused Phase 8 cpu-mask tests");
}
