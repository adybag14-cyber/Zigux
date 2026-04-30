const std = @import("std");

const current_surveyed_commit = "d7c67f13bab842e26bc2a1016c31722776b7fd3b";

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

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "blocked_on_object_model") or
        std.mem.eql(u8, status, "deferred_high_risk");
}

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
    try std.testing.expect(manifest.survey_summary.libbpf_c_lines >= 14000);
    try std.testing.expect(!manifest.survey_summary.preexisting_zigux_segments_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase8_libbpf_note_present);
    try std.testing.expect(manifest.survey_summary.companion_c_files.len >= 5);
    try std.testing.expect(manifest.segments.len >= 11);

    var starter_landed_count: usize = 0;
    var blocked_on_object_model_count: usize = 0;
    var deferred_high_risk_count: usize = 0;

    for (manifest.segments, 0..) |segment, i| {
        try std.testing.expect(segment.id.len > 0);
        try std.testing.expect(std.mem.startsWith(u8, segment.id, "P8-L15-S"));
        try std.testing.expect(segment.slug.len > 0);
        try std.testing.expect(segment.kind.len > 0);
        try std.testing.expect(segment.anchor_ranges.len > 0);
        try std.testing.expect(segment.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(segment.status));
        try std.testing.expect(std.mem.startsWith(u8, segment.zigux_destination, "tools/lib/bpf/zigux_segments/"));

        if (std.mem.eql(u8, segment.status, "starter_landed")) starter_landed_count += 1;
        if (std.mem.eql(u8, segment.status, "blocked_on_object_model")) blocked_on_object_model_count += 1;
        if (std.mem.eql(u8, segment.status, "deferred_high_risk")) deferred_high_risk_count += 1;

        for (manifest.segments[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, segment.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, segment.slug, other.slug));
        }
    }

    try std.testing.expect(starter_landed_count >= 6);
    try std.testing.expect(blocked_on_object_model_count >= 1);
    try std.testing.expect(deferred_high_risk_count >= 4);

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

    const cpu_mask_note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-libbpf-cpu-mask-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(cpu_mask_note);

    try expectContains(survey_note, "perf-buffer-online-cpu-routing");
    try expectContains(survey_note, "interrupt-routing-sensitive timing boundary");
    try expectContains(survey_note, "no standalone timer helper");
    try expectContains(survey_note, "no standalone clockevent helper");
    try expectContains(cpu_mask_note, "`libbpf_num_possible_cpus()` caching");
    try expectContains(cpu_mask_note, "`perf_buffer__new()` online CPU selection");
    try expectContains(cpu_mask_note, "per-CPU perf-buffer routing");
}
