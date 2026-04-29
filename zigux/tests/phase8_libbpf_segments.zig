const std = @import("std");

const current_surveyed_commit = "ba507b1f2e16af8983c61802e07bcbc95592aef4";

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

const AnchorRange = struct {
    path: []const u8,
    start_line: usize,
    end_line: usize,
};

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

fn workspacePathExists(path: []const u8) bool {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const file = std.Io.Dir.cwd().openFile(io_instance.io(), path, .{}) catch return false;
    file.close(io_instance.io());
    return true;
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
        if (std.mem.eql(u8, segment.slug, slug)) {
            return segment;
        }
    }
    return null;
}

test "phase 8 libbpf segment manifest records the roadmap gap and bounded next slices" {
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
    try std.testing.expect(manifest.segments.len >= 9);

    var ready_next_count: usize = 0;
    var starter_landed_count: usize = 0;
    var blocked_on_object_model_count: usize = 0;
    var deferred_high_risk_count: usize = 0;
    var saw_logging_segment = false;
    var saw_pin_path_segment = false;
    var saw_cpu_mask_segment = false;
    var saw_fdinfo_helper_segment = false;
    var saw_map_reuse_segment = false;
    var saw_file_path_handle_segment = false;
    var saw_interrupt_routing_segment = false;
    var saw_type_names_segment = false;

    for (manifest.segments, 0..) |segment, i| {
        try std.testing.expect(segment.id.len > 0);
        try std.testing.expect(std.mem.startsWith(u8, segment.id, "P8-L15-S"));
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
        if (std.mem.eql(u8, segment.slug, "type-name-helpers")) {
            saw_type_names_segment = true;
            try std.testing.expectEqualStrings("starter_landed", segment.status);
            try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/type_names.zig", segment.zigux_destination);
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
        if (std.mem.eql(u8, segment.slug, "fdinfo-map-info-helpers")) {
            saw_fdinfo_helper_segment = true;
            try std.testing.expectEqualStrings("starter_landed", segment.status);
            try std.testing.expectEqualStrings("helper_first", segment.kind);
            try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig", segment.zigux_destination);
            try std.testing.expectEqual(@as(usize, 2), segment.anchor_ranges.len);
            try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c:4956-4987", segment.anchor_ranges[0]);
            try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c:4976-4994", segment.anchor_ranges[1]);
            try expectContains(segment.why_now, "fdinfo");
            try expectContains(segment.why_now, "path construction");
            try expectContains(segment.why_now, "text parsing");
            try expectContains(segment.why_now, "reused-map-name chooser");
        }
        if (std.mem.eql(u8, segment.slug, "map-reuse-compatibility")) {
            saw_map_reuse_segment = true;
            try std.testing.expectEqualStrings("starter_landed", segment.status);
            try std.testing.expectEqualStrings("helper_first", segment.kind);
            try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig", segment.zigux_destination);
            try std.testing.expectEqual(@as(usize, 1), segment.anchor_ranges.len);
            try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c:5220-5251", segment.anchor_ranges[0]);
            try expectContains(segment.why_now, "pure field-and-flag check");
            try expectContains(segment.why_now, "DEVMAP readonly-flag exception");
        }
        if (std.mem.eql(u8, segment.slug, "file-path-and-handle-bridge")) {
            saw_file_path_handle_segment = true;
            try std.testing.expectEqualStrings("deferred_high_risk", segment.status);
            try std.testing.expectEqualStrings("resource_boundary", segment.kind);
            try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig", segment.zigux_destination);
            try std.testing.expectEqual(@as(usize, 2), segment.anchor_ranges.len);
            try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c:5112-5157", segment.anchor_ranges[0]);
            try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c:5255-5286", segment.anchor_ranges[1]);
            try expectContains(segment.why_now, "bpffs path opens");
            try expectContains(segment.why_now, "token creation");
            try expectContains(segment.why_now, "pinned-object reopen flows");
            try expectContains(segment.why_now, "fd ownership");
            try expectContains(segment.why_now, "token-preparation planner");
        }
        if (std.mem.eql(u8, segment.slug, "perf-buffer-online-cpu-routing")) {
            saw_interrupt_routing_segment = true;
            try std.testing.expectEqualStrings("deferred_high_risk", segment.status);
            try std.testing.expectEqualStrings("interrupt_routing_boundary", segment.kind);
            try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/cpu_mask.zig", segment.zigux_destination);
            try std.testing.expectEqual(@as(usize, 2), segment.anchor_ranges.len);
            try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c:14049-14110", segment.anchor_ranges[0]);
            try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c:14429-14480", segment.anchor_ranges[1]);
            try expectContains(segment.why_now, "online CPU filtering");
            try expectContains(segment.why_now, "perf-event-array map updates");
            try expectContains(segment.why_now, "timeout-driven perf-buffer polling");
            try expectContains(segment.why_now, "interrupt-routing contract");
        }

        for (manifest.segments[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, segment.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, segment.slug, other.slug));
        }
    }

    try std.testing.expect(ready_next_count == 0);
    try std.testing.expect(starter_landed_count >= 5);
    try std.testing.expect(blocked_on_object_model_count >= 1);
    try std.testing.expect(deferred_high_risk_count >= 3);
    try std.testing.expect(saw_logging_segment);
    try std.testing.expect(saw_pin_path_segment);
    try std.testing.expect(saw_cpu_mask_segment);
    try std.testing.expect(saw_fdinfo_helper_segment);
    try std.testing.expect(saw_map_reuse_segment);
    try std.testing.expect(saw_file_path_handle_segment);
    try std.testing.expect(saw_interrupt_routing_segment);
    try std.testing.expect(saw_type_names_segment);
}

test "phase 8 libbpf segment evidence still matches the live irq and reuse compatibility anchors" {
    const libbpf_c = try readWorkspaceFile(
        std.testing.allocator,
        "tools/lib/bpf/libbpf.c",
        1024 * 1024,
    );
    defer std.testing.allocator.free(libbpf_c);

    try expectContains(libbpf_c, "pb->cpu_cnt = libbpf_num_possible_cpus();");
    try expectContains(libbpf_c, "err = parse_cpu_mask_file(online_cpus_file, &online, &n);");
    try expectContains(libbpf_c, "if (p->cpu_cnt <= 0 && (cpu >= n || !online[cpu]))");
    try expectContains(libbpf_c, "int parse_cpu_mask_file(const char *fcpu, bool **mask, int *mask_sz)");
    try expectContains(libbpf_c, "int libbpf_num_possible_cpus(void)");
    try expectContains(libbpf_c, "name_len = strlen(info.name);");
    try expectContains(libbpf_c, "if (name_len == BPF_OBJ_NAME_LEN - 1 && strncmp(map->name, info.name, name_len) == 0)");
    try expectContains(libbpf_c, "new_name = strdup(map->name);");
    try expectContains(libbpf_c, "if (map->def.type == BPF_MAP_TYPE_DEVMAP || map->def.type == BPF_MAP_TYPE_DEVMAP_HASH)");
    try expectContains(libbpf_c, "map_info.map_flags &= ~BPF_F_RDONLY_PROG;");
    try expectContains(libbpf_c, "map_info.map_flags == map->def.map_flags");
}

test "phase 8 deferred perf-buffer anchor ranges still point at the live routing packet" {
    const manifest_json = try readWorkspaceFile(
        std.testing.allocator,
        "tools/lib/bpf/zigux_segments/manifest.json",
        64 * 1024,
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const routing_segment = findSegmentBySlug(parsed.value.segments, "perf-buffer-online-cpu-routing") orelse return error.MissingRoutingSegment;
    try std.testing.expectEqual(@as(usize, 2), routing_segment.anchor_ranges.len);

    const libbpf_c = try readWorkspaceFile(
        std.testing.allocator,
        "tools/lib/bpf/libbpf.c",
        1024 * 1024,
    );
    defer std.testing.allocator.free(libbpf_c);

    const setup_range = try parseAnchorRange(routing_segment.anchor_ranges[0]);
    try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c", setup_range.path);
    const setup_slice = try lineRangeSlice(libbpf_c, setup_range);
    try expectContains(setup_slice, "pb->cpu_cnt = libbpf_num_possible_cpus();");
    try expectContains(setup_slice, "err = parse_cpu_mask_file(online_cpus_file, &online, &n);");
    try expectContains(setup_slice, "if (p->cpu_cnt <= 0 && (cpu >= n || !online[cpu]))");
    try expectContains(setup_slice, "err = bpf_map_update_elem(pb->map_fd, &map_key,");
    try expectContains(setup_slice, "epoll_ctl(pb->epoll_fd, EPOLL_CTL_ADD, cpu_buf->fd,");

    const parser_range = try parseAnchorRange(routing_segment.anchor_ranges[1]);
    try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c", parser_range.path);
    const parser_slice = try lineRangeSlice(libbpf_c, parser_range);
    try expectContains(parser_slice, "int parse_cpu_mask_file(const char *fcpu, bool **mask, int *mask_sz)");
    try expectContains(parser_slice, "fd = open(fcpu, O_RDONLY | O_CLOEXEC);");
    try expectContains(parser_slice, "return parse_cpu_mask_str(buf, mask, mask_sz);");
    try expectContains(parser_slice, "int libbpf_num_possible_cpus(void)");
    try expectContains(parser_slice, "WRITE_ONCE(cpus, tmp_cpus);");
    try expectContains(libbpf_c, "int perf_buffer__poll(struct perf_buffer *pb, int timeout_ms)");
    try expectContains(libbpf_c, "cnt = epoll_wait(pb->epoll_fd, pb->events, pb->cpu_cnt, timeout_ms);");
    try expectContains(libbpf_c, "return cnt;");
}

test "phase 8 docs keep the deferred libbpf boundaries explicit" {
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

    const bridge_boundary_note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(bridge_boundary_note);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, current_surveyed_commit) != null);
    try expectContains(survey_note, "Latest verification snapshot");
    try expectContains(survey_note, "zig test zigux/tests/phase8_libbpf_segments.zig");
    try expectContains(survey_note, "zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all");
    try expectContains(survey_note, "zig build test --build-file zigux/tests/phase8_build.zig --summary all");
    try expectContains(survey_note, "python3 scripts/zigux/validate-phase8.py");
    try expectContains(survey_note, "Build Summary: 20/20 steps succeeded; 63/63 tests passed");
    try expectContains(survey_note, "PHASE8_VALIDATION=pass");
    try expectContains(survey_note, "deferred resource boundary");
    try expectContains(survey_note, "file-path-and-handle-bridge");
    try expectContains(survey_note, "blocked object-model");
    try expectContains(survey_note, "skeleton");
    try expectContains(survey_note, "perf-buffer-online-cpu-routing");
    try expectContains(survey_note, "online CPU filtering");
    try expectContains(survey_note, "perf_buffer__poll(timeout_ms)");
    try expectContains(survey_note, "ready-buffer counts");
    try expectContains(survey_note, "no standalone timer helper");
    try expectContains(survey_note, "no standalone clockevent helper");
    try expectContains(survey_note, "interrupt-routing-sensitive timing boundary");
    try expectContains(survey_note, "reused-map-name chooser");
    try expectContains(survey_note, "map reuse compatibility");
    try expectContains(survey_note, "DEVMAP readonly-prog");
    try expectContains(survey_note, "token-preparation planning");
    try expectContains(survey_note, "classifyTokenPreparationFailure()");
    try expectContains(survey_note, "skip_optional_missing_delegation");
    try expectContains(survey_note, "mandatory token setup remains an explicit fail-fast boundary");
    try expectContains(cpu_mask_note, "`libbpf_num_possible_cpus()` caching");
    try expectContains(cpu_mask_note, "`perf_buffer__new()` online CPU selection");
    try expectContains(cpu_mask_note, "per-CPU perf-buffer routing");
    try expectContains(bridge_boundary_note, "perf-buffer-online-cpu-routing");
    try expectContains(bridge_boundary_note, "/sys/devices/system/cpu/online");
    try expectContains(bridge_boundary_note, "cached `/sys/devices/system/cpu/possible` counts");
    try expectContains(bridge_boundary_note, "libbpf_num_possible_cpus()");
    try expectContains(bridge_boundary_note, "per-CPU perf-event-array map updates");
    try expectContains(bridge_boundary_note, "epoll-backed perf FD registration");
    try expectContains(bridge_boundary_note, "perf_buffer__poll(timeout_ms)");
    try expectContains(bridge_boundary_note, "ready-buffer counts");
    try expectContains(bridge_boundary_note, "no standalone timer helper");
    try expectContains(bridge_boundary_note, "no standalone clockevent helper");
    try expectContains(bridge_boundary_note, "classifyTokenPreparationFailure()");
    try expectContains(bridge_boundary_note, "skip_optional_missing_delegation");
    try expectContains(bridge_boundary_note, "mandatory `fail`");
}

test "phase 8 deferred perf-buffer boundary still ships no standalone timer helper packet" {
    try std.testing.expect(!workspacePathExists("tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"));
    try std.testing.expect(!workspacePathExists("zigux/tests/phase8_perf_buffer_poll.zig"));
    try std.testing.expect(!workspacePathExists("Documentation/zigux/phase8-perf-buffer-poll-slice.md"));
}

test "phase 8 token-preparation failure boundary stays aligned between helper and docs" {
    const helper = try readWorkspaceFile(
        std.testing.allocator,
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(helper);

    const survey_note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-libbpf-segment-survey.md",
        64 * 1024,
    );
    defer std.testing.allocator.free(survey_note);

    const bridge_boundary_note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(bridge_boundary_note);

    try expectContains(helper, "pub fn classifyTokenPreparationFailure(");
    try expectContains(helper, ".skip_optional_missing_delegation");
    try expectContains(helper, ".skip_optional");
    try expectContains(helper, ".fail");
    try expectContains(helper, "token_create and err_code ==");
    try expectContains(helper, "shouldContinueWithoutToken");

    try expectContains(survey_note, "classifyTokenPreparationFailure()");
    try expectContains(survey_note, "skip_optional_missing_delegation");
    try expectContains(survey_note, "mandatory token setup remains an explicit fail-fast boundary");
    try expectContains(bridge_boundary_note, "classifyTokenPreparationFailure()");
    try expectContains(bridge_boundary_note, "skip_optional_missing_delegation");
    try expectContains(bridge_boundary_note, "mandatory `fail`");
}