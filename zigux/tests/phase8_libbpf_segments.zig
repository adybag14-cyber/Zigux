const std = @import("std");

const current_surveyed_commit = "a6fab7a6b89bdd0d0ee3c0892eaab1ad264ecb89";

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
