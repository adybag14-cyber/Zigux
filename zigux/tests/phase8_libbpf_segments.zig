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

fn isLowerHexCommit(commit: []const u8) bool {
    if (commit.len != 40) return false;

    for (commit) |char| {
        if (!((char >= '0' and char <= '9') or (char >= 'a' and char <= 'f'))) {
            return false;
        }
    }

    return true;
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
    try std.testing.expectEqualStrings("P8-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 8", manifest.phase);
    try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c", manifest.anchor);
    try std.testing.expect(isLowerHexCommit(manifest.surveyed_commit));
    try std.testing.expect(!std.mem.eql(u8, manifest.surveyed_commit, "246d0135fa18a1af90bf7d6e516ae4a7b2ac262a"));
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
    var saw_file_path_handle_segment = false;
    var saw_interrupt_routing_segment = false;
    var saw_type_names_segment = false;

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
            try std.testing.expectEqual(@as(usize, 1), segment.anchor_ranges.len);
            try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c:4956-4987", segment.anchor_ranges[0]);
            try expectContains(segment.why_now, "fdinfo");
            try expectContains(segment.why_now, "path construction");
            try expectContains(segment.why_now, "text parsing");
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
    try std.testing.expect(saw_file_path_handle_segment);
    try std.testing.expect(saw_interrupt_routing_segment);
    try std.testing.expect(saw_type_names_segment);
}

test "phase 8 libbpf segment evidence still matches the live irq and cpumask anchors" {
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
}

test "phase 8 docs keep the deferred irq routing boundary explicit" {
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
    try expectContains(survey_note, "online CPU filtering");
    try expectContains(survey_note, "interrupt-routing-sensitive boundary");
    try expectContains(cpu_mask_note, "`libbpf_num_possible_cpus()` caching");
    try expectContains(cpu_mask_note, "`perf_buffer__new()` online CPU selection");
    try expectContains(cpu_mask_note, "per-CPU perf-buffer routing");
}
