const std = @import("std");

const expected_surveyed_commit = "897cdd2f62c4428d2a050275a187950e161b66eb";

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
    anchor_range_count: usize,
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

const expected_segments = [_]ExpectedSegment{
    .{
        .id = "P8-L15-S01",
        .slug = "logging-version-and-errno",
        .status = "starter_landed",
        .kind = "helper_first",
        .zigux_destination = "tools/lib/bpf/zigux_segments/logging.zig",
        .anchor_range_count = 2,
    },
    .{
        .id = "P8-L15-S02",
        .slug = "pin-path-helpers",
        .status = "starter_landed",
        .kind = "helper_first",
        .zigux_destination = "tools/lib/bpf/zigux_segments/pin_path.zig",
        .anchor_range_count = 2,
    },
    .{
        .id = "P8-L15-S03",
        .slug = "cpu-mask-parsing",
        .status = "starter_landed",
        .kind = "helper_first",
        .zigux_destination = "tools/lib/bpf/zigux_segments/cpu_mask.zig",
        .anchor_range_count = 1,
    },
    .{
        .id = "P8-L15-S04",
        .slug = "type-name-helpers",
        .status = "starter_landed",
        .kind = "helper_first",
        .zigux_destination = "tools/lib/bpf/zigux_segments/type_names.zig",
        .anchor_range_count = 1,
    },
    .{
        .id = "P8-L15-S05",
        .slug = "fdinfo-map-info-helpers",
        .status = "ready_next",
        .kind = "helper_first",
        .zigux_destination = "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        .anchor_range_count = 1,
    },
    .{
        .id = "P8-L15-S06",
        .slug = "map-reuse-compatibility",
        .status = "ready_next",
        .kind = "helper_first",
        .zigux_destination = "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        .anchor_range_count = 1,
    },
    .{
        .id = "P8-L15-S07",
        .slug = "file-path-and-handle-bridge",
        .status = "deferred_high_risk",
        .kind = "resource_boundary",
        .zigux_destination = "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        .anchor_range_count = 1,
    },
    .{
        .id = "P8-L15-S08",
        .slug = "perf-buffer-online-cpu-routing",
        .status = "deferred_high_risk",
        .kind = "interrupt_routing",
        .zigux_destination = "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        .anchor_range_count = 1,
    },
    .{
        .id = "P8-L15-S09",
        .slug = "skeleton-population",
        .status = "blocked_on_object_model",
        .kind = "object_adjacent",
        .zigux_destination = "tools/lib/bpf/zigux_segments/skeleton.zig",
        .anchor_range_count = 1,
    },
    .{
        .id = "P8-L15-S10",
        .slug = "object-and-elf-loader",
        .status = "deferred_high_risk",
        .kind = "core_loader",
        .zigux_destination = "tools/lib/bpf/zigux_segments/object_loader.zig",
        .anchor_range_count = 2,
    },
    .{
        .id = "P8-L15-S11",
        .slug = "btf-relocation-and-program-load",
        .status = "deferred_high_risk",
        .kind = "verifier_facing",
        .zigux_destination = "tools/lib/bpf/zigux_segments/relocation.zig",
        .anchor_range_count = 2,
    },
    .{
        .id = "P8-L15-S12",
        .slug = "perf-buffer-poll-bookkeeping",
        .status = "starter_landed",
        .kind = "helper_adjacent",
        .zigux_destination = "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        .anchor_range_count = 1,
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

fn expectCompanionCatalog(companion_c_files: []const CompanionFile) !void {
    try std.testing.expectEqual(expected_companion_c_files.len, companion_c_files.len);

    for (expected_companion_c_files, companion_c_files) |expected_companion, actual_companion| {
        try std.testing.expectEqualStrings(expected_companion.path, actual_companion.path);
        try std.testing.expectEqual(expected_companion.lines, actual_companion.lines);
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
        try std.testing.expectEqual(expected_segment.anchor_range_count, actual_segment.anchor_ranges.len);
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

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
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
    try expectSegmentCatalog(manifest.segments);
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

    const bridge_boundary_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(bridge_boundary_note);

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
    try expectContains(phase8_note, "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md");
    try expectContains(phase8_note, "zigux/tests/phase8_file_path_handle_bridge.zig");
    try expectContains(phase8_note, "zigux/tests/phase8_bpf_type_names.zig");
    try expectContains(phase8_note, "zigux/tests/phase8_perf_buffer_poll.zig");
    try expectContains(phase8_note, "zigux/tests/phase8_perf_buffer_poll_only_build.zig");
    try expectContainsExactlyOnce(
        product_boundary,
        "  - `zigux/tests/phase8_libbpf_segments_only_build.zig`\n",
    );
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
    try expectContains(phase8_note, "no longer because the bridge packet paths are missing");
    try expectContains(phase8_note, "bounded fdinfo helper packet");
    try expectContains(phase8_note, "fdinfo-only surface");
    try expectContains(phase8_note, "resource-boundary packet still stays deferred");
    try expectContains(phase8_note, "standalone timer or clockevent helper behavior");

    try expectContains(cpu_mask_note, "PHASE8_STATUS=parked");
    try expectContains(cpu_mask_note, "tools/lib/bpf/zigux_segments/cpu_mask.zig");
    try expectContains(cpu_mask_note, "zigux/tests/phase8_build.zig");
    try expectContains(cpu_mask_note, "perf-buffer or feature-probe integration");

    try expectContains(type_names_note, "PHASE8_STATUS=parked");
    try expectContains(type_names_note, "tools/lib/bpf/zigux_segments/type_names.zig");
    try expectContains(type_names_note, "zigux/tests/phase8_build.zig");

    try expectContains(bridge_boundary_note, "PHASE8_STATUS=parked");
    try expectContains(bridge_boundary_note, "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig");
    try expectContains(bridge_boundary_note, "make -C zigux phase8-validate");
    try expectContains(bridge_boundary_note, "zig build test --build-file zigux/tests/phase8_file_path_handle_bridge_only_build.zig --summary all");
    try expectContains(bridge_boundary_note, "zig build test --build-file zigux/tests/phase8_build.zig --summary all");
    try expectContains(bridge_boundary_note, "perf-buffer-online-cpu-routing");
    try expectContains(bridge_boundary_note, "/sys/devices/system/cpu/online");
    try expectContains(bridge_boundary_note, "cached `/sys/devices/system/cpu/possible` counts via `libbpf_num_possible_cpus()`");
    try expectContains(bridge_boundary_note, "online CPU filtering");
    try expectContains(bridge_boundary_note, "per-CPU perf-event-array map updates");
    try expectContains(bridge_boundary_note, "per-CPU `perf_event_open()` setup");
    try expectContains(bridge_boundary_note, "perf-buffer ring `mmap()` setup");
    try expectContains(bridge_boundary_note, "`PERF_EVENT_IOC_ENABLE` enablement");
    try expectContains(bridge_boundary_note, "epoll-backed perf FD registration");
    try expectContains(bridge_boundary_note, "poll waits");
    try expectContains(bridge_boundary_note, "fd close or ownership semantics");
}
