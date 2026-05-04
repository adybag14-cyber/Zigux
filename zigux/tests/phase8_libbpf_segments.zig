const std = @import("std");

const current_surveyed_commit = "897cdd2f62c4428d2a050275a187950e161b66eb";

const expected_companion_files = [_]CompanionFile{
    .{ .path = "tools/lib/bpf/bpf.c", .lines = 1419 },
    .{ .path = "tools/lib/bpf/btf.c", .lines = 6360 },
    .{ .path = "tools/lib/bpf/features.c", .lines = 727 },
    .{ .path = "tools/lib/bpf/libbpf_utils.c", .lines = 256 },
    .{ .path = "tools/lib/bpf/linker.c", .lines = 3116 },
    .{ .path = "tools/lib/bpf/netlink.c", .lines = 938 },
    .{ .path = "tools/lib/bpf/nlattr.c", .lines = 194 },
    .{ .path = "tools/lib/bpf/ringbuf.c", .lines = 684 },
};

const expected_segment_ids = [_][]const u8{
    "P8-L15-S01",
    "P8-L15-S02",
    "P8-L15-S03",
    "P8-L15-S04",
    "P8-L15-S08",
    "P8-L15-S11",
    "P8-L15-S09",
    "P8-L15-S10",
    "P8-L15-S05",
    "P8-L15-S06",
    "P8-L15-S07",
};

const expected_segment_slugs = [_][]const u8{
    "logging-version-and-errno",
    "pin-path-helpers",
    "cpu-mask-parsing",
    "type-name-helpers",
    "fdinfo-map-info-helpers",
    "map-reuse-compatibility",
    "file-path-and-handle-bridge",
    "perf-buffer-online-cpu-routing",
    "skeleton-population",
    "object-and-elf-loader",
    "btf-relocation-and-program-load",
};

const expected_segment_statuses = [_][]const u8{
    "starter_landed",
    "starter_landed",
    "starter_landed",
    "starter_landed",
    "starter_landed",
    "starter_landed",
    "deferred_high_risk",
    "deferred_high_risk",
    "blocked_on_object_model",
    "deferred_high_risk",
    "deferred_high_risk",
};

const expected_segment_kinds = [_][]const u8{
    "helper_first",
    "helper_first",
    "helper_first",
    "helper_first",
    "helper_first",
    "helper_first",
    "resource_boundary",
    "interrupt_routing_boundary",
    "object_adjacent",
    "core_loader",
    "verifier_facing",
};

const expected_segment_destinations = [_][]const u8{
    "tools/lib/bpf/zigux_segments/logging.zig",
    "tools/lib/bpf/zigux_segments/pin_path.zig",
    "tools/lib/bpf/zigux_segments/cpu_mask.zig",
    "tools/lib/bpf/zigux_segments/type_names.zig",
    "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    "tools/lib/bpf/zigux_segments/cpu_mask.zig",
    "tools/lib/bpf/zigux_segments/skeleton.zig",
    "tools/lib/bpf/zigux_segments/object_loader.zig",
    "tools/lib/bpf/zigux_segments/relocation.zig",
};

const expected_segment_anchor_range_counts = [_]usize{
    2,
    2,
    1,
    1,
    2,
    1,
    2,
    2,
    1,
    2,
    2,
};

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

const AnchorRange = struct {
    path: []const u8,
    start_line: usize,
    end_line: usize,
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readWorkspaceFile(allocator: std.mem.Allocator, path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(limit),
    );
}

fn parseAnchorRange(text: []const u8) !AnchorRange {
    const colon = std.mem.lastIndexOfScalar(u8, text, ':') orelse return error.InvalidAnchorRange;
    const dash = std.mem.indexOfScalar(u8, text[colon + 1 ..], '-') orelse return error.InvalidAnchorRange;
    const dash_index = colon + 1 + dash;
    const start_line = std.fmt.parseUnsigned(usize, text[colon + 1 .. dash_index], 10) catch return error.InvalidAnchorRange;
    const end_line = std.fmt.parseUnsigned(usize, text[dash_index + 1 ..], 10) catch return error.InvalidAnchorRange;

    if (start_line == 0 or end_line < start_line) return error.InvalidAnchorRange;

    return .{
        .path = text[0..colon],
        .start_line = start_line,
        .end_line = end_line,
    };
}

fn lineRangeSlice(content: []const u8, anchor_range: AnchorRange) ![]const u8 {
    var line: usize = 1;
    var line_start: usize = 0;
    var slice_start: ?usize = null;
    var slice_end: ?usize = null;

    for (content, 0..) |char, index| {
        if (line == anchor_range.start_line and slice_start == null) {
            slice_start = line_start;
        }
        if (char == '\n') {
            if (line == anchor_range.end_line) {
                slice_end = index + 1;
                break;
            }
            line += 1;
            line_start = index + 1;
        }
    }

    if (slice_start == null and line == anchor_range.start_line) {
        slice_start = line_start;
    }
    if (slice_end == null and line == anchor_range.end_line) {
        slice_end = content.len;
    }
    if (slice_start == null or slice_end == null) {
        return error.AnchorRangeOutsideFile;
    }

    return content[slice_start.?..slice_end.?];
}

fn findSegmentBySlug(segments: []const Segment, slug: []const u8) ?Segment {
    for (segments) |segment| {
        if (std.mem.eql(u8, segment.slug, slug)) return segment;
    }
    return null;
}

test "phase 8 libbpf segment manifest records the current bounded catalog" {
    const manifest_json = try readWorkspaceFile(
        std.testing.allocator,
        "tools/lib/bpf/zigux_segments/manifest.json",
        64 * 1024,
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P8-L15", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 8", manifest.phase);
    try std.testing.expectEqualStrings(current_surveyed_commit, manifest.surveyed_commit);
    try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 14771), manifest.survey_summary.libbpf_c_lines);
    try std.testing.expect(!manifest.survey_summary.preexisting_zigux_segments_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase8_libbpf_note_present);
    try std.testing.expectEqual(expected_companion_files.len, manifest.survey_summary.companion_c_files.len);
    for (expected_companion_files, manifest.survey_summary.companion_c_files) |expected, actual| {
        try std.testing.expectEqualStrings(expected.path, actual.path);
        try std.testing.expectEqual(expected.lines, actual.lines);
    }
    try std.testing.expectEqual(expected_segment_ids.len, manifest.segments.len);

    var starter_landed_count: usize = 0;
    var blocked_on_object_model_count: usize = 0;
    var deferred_high_risk_count: usize = 0;

    for (manifest.segments, 0..) |segment, i| {
        try std.testing.expectEqualStrings(expected_segment_ids[i], segment.id);
        try std.testing.expectEqualStrings(expected_segment_slugs[i], segment.slug);
        try std.testing.expectEqualStrings(expected_segment_statuses[i], segment.status);
        try std.testing.expectEqualStrings(expected_segment_kinds[i], segment.kind);
        try std.testing.expectEqualStrings(expected_segment_destinations[i], segment.zigux_destination);
        try std.testing.expectEqual(expected_segment_anchor_range_counts[i], segment.anchor_ranges.len);
        try std.testing.expect(segment.why_now.len > 0);

        if (std.mem.eql(u8, segment.status, "starter_landed")) starter_landed_count += 1;
        if (std.mem.eql(u8, segment.status, "blocked_on_object_model")) blocked_on_object_model_count += 1;
        if (std.mem.eql(u8, segment.status, "deferred_high_risk")) deferred_high_risk_count += 1;

        for (manifest.segments[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, segment.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, segment.slug, other.slug));
        }
    }

    try std.testing.expectEqual(@as(usize, 6), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_on_object_model_count);
    try std.testing.expectEqual(@as(usize, 4), deferred_high_risk_count);

    const cpu_mask_segment = findSegmentBySlug(manifest.segments, "cpu-mask-parsing") orelse return error.MissingCpuMaskSegment;
    try std.testing.expectEqualStrings("starter_landed", cpu_mask_segment.status);
    try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/cpu_mask.zig", cpu_mask_segment.zigux_destination);
    try std.testing.expectEqual(@as(usize, 1), cpu_mask_segment.anchor_ranges.len);

    const fdinfo_segment = findSegmentBySlug(manifest.segments, "fdinfo-map-info-helpers") orelse return error.MissingFdinfoSegment;
    try std.testing.expectEqualStrings("starter_landed", fdinfo_segment.status);
    try std.testing.expectEqualStrings("helper_first", fdinfo_segment.kind);
    try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig", fdinfo_segment.zigux_destination);
    try std.testing.expectEqual(@as(usize, 2), fdinfo_segment.anchor_ranges.len);
    try expectContains(fdinfo_segment.why_now, "fdinfo");
    try expectContains(fdinfo_segment.why_now, "path construction");
    try expectContains(fdinfo_segment.why_now, "text parsing");
    try expectContains(fdinfo_segment.why_now, "map_extra");

    const map_reuse_segment = findSegmentBySlug(manifest.segments, "map-reuse-compatibility") orelse return error.MissingMapReuseSegment;
    try std.testing.expectEqualStrings("starter_landed", map_reuse_segment.status);
    try std.testing.expectEqualStrings("helper_first", map_reuse_segment.kind);
    try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig", map_reuse_segment.zigux_destination);
    try std.testing.expectEqual(@as(usize, 1), map_reuse_segment.anchor_ranges.len);
    try expectContains(map_reuse_segment.why_now, "DEVMAP");
    try expectContains(map_reuse_segment.why_now, "readonly-flag exception");

    const routing_segment = findSegmentBySlug(manifest.segments, "perf-buffer-online-cpu-routing") orelse return error.MissingRoutingSegment;
    try std.testing.expectEqualStrings("deferred_high_risk", routing_segment.status);
    try std.testing.expectEqualStrings("interrupt_routing_boundary", routing_segment.kind);
    try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/cpu_mask.zig", routing_segment.zigux_destination);
    try std.testing.expectEqual(@as(usize, 2), routing_segment.anchor_ranges.len);
    try expectContains(routing_segment.why_now, "online CPU filtering");
    try expectContains(routing_segment.why_now, "perf-event-array map updates");
    try expectContains(routing_segment.why_now, "interrupt-routing contract");
}

test "phase 8 live irq and cpumask anchor ranges still match the deferred boundary" {
    const manifest_json = try readWorkspaceFile(
        std.testing.allocator,
        "tools/lib/bpf/zigux_segments/manifest.json",
        64 * 1024,
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const libbpf_c = try readWorkspaceFile(
        std.testing.allocator,
        "tools/lib/bpf/libbpf.c",
        1024 * 1024,
    );
    defer std.testing.allocator.free(libbpf_c);

    const cpu_mask_segment = findSegmentBySlug(parsed.value.segments, "cpu-mask-parsing") orelse return error.MissingCpuMaskSegment;
    const cpu_mask_range = try parseAnchorRange(cpu_mask_segment.anchor_ranges[0]);
    try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c", cpu_mask_range.path);
    const cpu_mask_slice = try lineRangeSlice(libbpf_c, cpu_mask_range);
    try expectContains(cpu_mask_slice, "int parse_cpu_mask_str(const char *s, bool **mask, int *mask_sz)");
    try expectContains(cpu_mask_slice, "int parse_cpu_mask_file(const char *fcpu, bool **mask, int *mask_sz)");
    try expectContains(cpu_mask_slice, "int libbpf_num_possible_cpus(void)");
    try expectContains(cpu_mask_slice, "WRITE_ONCE(cpus, tmp_cpus);");

    const routing_segment = findSegmentBySlug(parsed.value.segments, "perf-buffer-online-cpu-routing") orelse return error.MissingRoutingSegment;
    const setup_range = try parseAnchorRange(routing_segment.anchor_ranges[0]);
    const helper_range = try parseAnchorRange(routing_segment.anchor_ranges[1]);
    try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c", setup_range.path);
    try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c", helper_range.path);

    const setup_slice = try lineRangeSlice(libbpf_c, setup_range);
    const helper_slice = try lineRangeSlice(libbpf_c, helper_range);
    try expectContains(setup_slice, "pb->cpu_cnt = libbpf_num_possible_cpus();");
    try expectContains(setup_slice, "err = parse_cpu_mask_file(online_cpus_file, &online, &n);");
    try expectContains(setup_slice, "if (p->cpu_cnt <= 0 && (cpu >= n || !online[cpu]))");
    try expectContains(setup_slice, "err = bpf_map_update_elem(pb->map_fd, &map_key,");
    try expectContains(setup_slice, "epoll_ctl(pb->epoll_fd, EPOLL_CTL_ADD, cpu_buf->fd,");
    try expectContains(helper_slice, "int parse_cpu_mask_file(const char *fcpu, bool **mask, int *mask_sz)");
    try expectContains(helper_slice, "int libbpf_num_possible_cpus(void)");
}

test "phase 8 docs keep the deferred irq routing and timer boundary explicit" {
    const survey_note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-libbpf-segment-survey.md",
        64 * 1024,
    );
    defer std.testing.allocator.free(survey_note);

    const bridge_note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
        64 * 1024,
    );
    defer std.testing.allocator.free(bridge_note);

    const cpu_mask_note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-libbpf-cpu-mask-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(cpu_mask_note);

    const cpu_mask_helper = try readWorkspaceFile(
        std.testing.allocator,
        "tools/lib/bpf/zigux_segments/cpu_mask.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(cpu_mask_helper);

    const cpu_mask_test = try readWorkspaceFile(
        std.testing.allocator,
        "zigux/tests/phase8_cpu_mask.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(cpu_mask_test);

    try expectContains(
        survey_note,
        "- survey checkpoint: refreshed against inspected `master` head `" ++ current_surveyed_commit ++ "`",
    );
    try expectContains(
        survey_note,
        "scope: segment manifest plus six landed helper-first starter slices, the separate bounded perf-buffer poll bookkeeping adjunct, one deferred resource boundary, one deferred interrupt-routing boundary, one blocked object-model follow-on, and two deferred loader-facing follow-ons",
    );
    try expectContains(
        survey_note,
        "segmented rollout instead of a single-file port attempt",
    );
    try expectContains(
        survey_note,
        "helper-first clusters with stable text or path behavior",
    );
    try expectContains(
        survey_note,
        "That eleven-segment catalog intentionally excludes the separate `perf_buffer_poll.zig` adjunct packet",
    );
    try expectContains(
        survey_note,
        "historical `P8-L15-S..` prefix as a stable segment catalog identifier",
    );
    try expectContains(
        survey_note,
        "active scheduled ownership and cleanup lane for this packet is `P8-L15`",
    );
    try expectContains(survey_note, "perf-buffer-online-cpu-routing");
    try expectContains(survey_note, "per-CPU `perf_event_open()` setup");
    try expectContains(survey_note, "perf-buffer ring `mmap()` setup");
    try expectContains(survey_note, "`PERF_EVENT_IOC_ENABLE` enablement");
    try expectContains(survey_note, "interrupt-routing-sensitive timing boundary");
    try expectContains(survey_note, "no standalone timer helper");
    try expectContains(survey_note, "no standalone clockevent helper");
    try expectContains(survey_note, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    try expectContains(survey_note, "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig");
    try expectContains(survey_note, "zigux/tests/phase8_perf_buffer_poll.zig");
    try expectContains(survey_note, "wait-result classification");
    try expectContains(survey_note, "ready-buffer bookkeeping");
    try expectContains(survey_note, "ordered `perf_buffer__process_records()` pass reviewable as a bounded fail-fast summary helper");
    try expectContains(survey_note, "rejects impossible post-wait buffer state combinations");
    try expectContains(survey_note, "does not claim direct `epoll_wait()` parity");
    try expectContains(bridge_note, "perf_buffer__poll(timeout_ms)");
    try expectContains(bridge_note, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    try expectContains(bridge_note, "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig");
    try expectContains(bridge_note, "zigux/tests/phase8_perf_buffer_poll.zig");
    try expectContains(bridge_note, "wait-result classification");
    try expectContains(bridge_note, "ready-buffer bookkeeping");
    try expectContains(bridge_note, "ordered `perf_buffer__process_records()` fail-fast summary");
    try expectContains(bridge_note, "cumulative processed-record count returned before the first failing ready buffer only");
    try expectContains(bridge_note, "no standalone timer helper");
    try expectContains(bridge_note, "no standalone clockevent helper");
    try expectContains(bridge_note, "does not close the broader routing boundary");
    try expectContains(cpu_mask_note, "bounded perf-buffer auto-CPU sizing");
    try expectContains(cpu_mask_note, "`+N` and `+N-+M` signed-decimal token forms");
    try expectContains(cpu_mask_note, "a bounded auto-CPU count clamp that mirrors libbpf's perf-buffer map-budget sizing");
    try expectContains(cpu_mask_note, "a pure online-CPU eligibility predicate that mirrors libbpf's automatic-budget offline skip rule");
    try expectContains(cpu_mask_note, "`libbpf_num_possible_cpus()` caching");
    try expectContains(cpu_mask_note, "`perf_buffer__new()` online CPU selection");
    try expectContains(cpu_mask_note, "perf-buffer-online-cpu-routing");
    try expectContains(cpu_mask_note, "interrupt-routing-sensitive timing boundary");
    try expectContains(cpu_mask_note, "`perf_buffer__poll(timeout_ms)` timeout handling");
    try expectContains(cpu_mask_note, "no standalone timer helper");
    try expectContains(cpu_mask_note, "no standalone clockevent helper");
    try expectContains(cpu_mask_note, "per-CPU perf-buffer routing");
    try expectContains(cpu_mask_helper, "pub fn derivePerfBufferAutoCpuCount(possible_cpu_count: usize, map_max_entries: u32) usize {");
    try expectContains(cpu_mask_helper, "test \"parseCpuMaskString accepts the C helper's signed decimal token syntax when values stay non-negative\"");
    try expectContains(cpu_mask_helper, "test \"derivePerfBufferAutoCpuCount keeps perf-buffer auto sizing within the map budget\"");
    try expectContains(cpu_mask_test, "test \"phase 8 cpu mask starter slice accepts plus-prefixed CPU tokens like the live C helper\"");
    try expectContains(cpu_mask_test, "test \"phase 8 cpu mask reader interface keeps failures explicit\"");
}

test "phase 8 docs keep the bounded fdinfo map_extra parsing explicit" {
    const survey_note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-libbpf-segment-survey.md",
        64 * 1024,
    );
    defer std.testing.allocator.free(survey_note);

    try expectContains(survey_note, "`map_extra`");
    try expectContains(survey_note, "`map_flags`, and `map_extra`");
    try expectContains(survey_note, "explicit `map_flags` and `map_extra` bases");
}

test "phase 8 bridge boundary note keeps reuse-open and reuse-resolution planning explicit" {
    const bridge_note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
        64 * 1024,
    );
    defer std.testing.allocator.free(bridge_note);

    try expectContains(bridge_note, "classifyReusePinnedMapOpenFailure()");
    try expectContains(bridge_note, "resolveReusePinnedMapAttempt()");
    try expectContains(bridge_note, "missing pinned-map lookup versus hard open failure");
    try expectContains(bridge_note, "`reused`, `incompatible_map`, and `reuse_fd_failed`");
    try expectContains(bridge_note, "`should_close_pin_fd`");
    try expectContains(bridge_note, "`should_mark_map_pinned`");
}

test "phase 8 docs and manifest keep the deferred file-path resource boundary explicit" {
    const survey_note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-libbpf-segment-survey.md",
        64 * 1024,
    );
    defer std.testing.allocator.free(survey_note);

    const bridge_note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
        64 * 1024,
    );
    defer std.testing.allocator.free(bridge_note);

    const manifest_json = try readWorkspaceFile(
        std.testing.allocator,
        "tools/lib/bpf/zigux_segments/manifest.json",
        64 * 1024,
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const bridge_segment = findSegmentBySlug(parsed.value.segments, "file-path-and-handle-bridge") orelse return error.MissingFilePathHandleBridgeSegment;
    try std.testing.expectEqualStrings("deferred_high_risk", bridge_segment.status);
    try std.testing.expectEqualStrings("resource_boundary", bridge_segment.kind);
    try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig", bridge_segment.zigux_destination);
    try std.testing.expectEqual(@as(usize, 2), bridge_segment.anchor_ranges.len);
    try expectContains(bridge_segment.why_now, "token-preparation planner");
    try expectContains(bridge_segment.why_now, "real bpffs path opens");
    try expectContains(bridge_segment.why_now, "fd ownership");

    try expectContains(survey_note, "file-path-and-handle-bridge");
    try expectContains(survey_note, "real procfs reads");
    try expectContains(survey_note, "bpffs opens");
    try expectContains(survey_note, "fd close or ownership semantics");
    try expectContains(bridge_note, "skip_optional_missing_delegation");
    try expectContains(bridge_note, "bpf_obj_get()` reopen flows");
    try expectContains(bridge_note, "FD duplication or replacement behavior");
}
