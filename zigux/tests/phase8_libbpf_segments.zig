const std = @import("std");

const surveyed_commit = "089188c96b86c0da16088e916094a7c977d0cfc6";

const Segment = struct {
    slug: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: ?[]const u8 = null,
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
    segments: []const Segment,
    segmentation_notes: []const SegmentationNote,
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn readFileAlloc(
    io: std.Io,
    allocator: std.mem.Allocator,
    path: []const u8,
    limit: usize,
) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, allocator, .limited(limit));
}

fn findSegmentBySlug(segments: []const Segment, slug: []const u8) ?Segment {
    for (segments) |segment| {
        if (std.mem.eql(u8, segment.slug, slug)) return segment;
    }
    return null;
}

test "phase 8 libbpf manifest keeps the current helper-first segment catalog aligned with the survey" {
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
    try std.testing.expectEqualStrings(surveyed_commit, manifest.surveyed_commit);
    try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 12), manifest.segments.len);
    try std.testing.expectEqual(@as(usize, 1), manifest.segmentation_notes.len);

    const fdinfo = findSegmentBySlug(manifest.segments, "fdinfo-map-info-helpers") orelse
        return error.MissingFdinfoSegment;
    try std.testing.expectEqualStrings("starter_landed", fdinfo.status);
    try std.testing.expectEqualStrings("helper_first", fdinfo.kind);
    try std.testing.expectEqualStrings(
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        fdinfo.zigux_destination,
    );

    const bridge = findSegmentBySlug(manifest.segments, "file-path-and-handle-bridge") orelse
        return error.MissingBridgeSegment;
    try std.testing.expectEqualStrings("deferred_high_risk", bridge.status);
    try std.testing.expectEqualStrings("resource_boundary", bridge.kind);

    const routing = findSegmentBySlug(manifest.segments, "perf-buffer-online-cpu-routing") orelse
        return error.MissingRoutingSegment;
    try std.testing.expectEqualStrings("deferred_high_risk", routing.status);
    try std.testing.expectEqualStrings("interrupt_routing", routing.kind);
    try std.testing.expectEqualStrings(
        "tools/lib/bpf/zigux_segments/online_cpu_routing.zig",
        routing.zigux_destination,
    );
    try expectContains(routing.why_now orelse return error.MissingRoutingWhyNow, "online_cpu_routing.zig");
    try expectContains(routing.why_now orelse return error.MissingRoutingWhyNow, "cursor and routing-summary helper");

    const poll = findSegmentBySlug(manifest.segments, "perf-buffer-poll-bookkeeping") orelse
        return error.MissingPollSegment;
    try std.testing.expectEqualStrings("starter_landed", poll.status);
    try std.testing.expectEqualStrings("helper_adjacent", poll.kind);

    const bridge_note = manifest.segmentation_notes[0];
    try std.testing.expectEqualStrings(
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        bridge_note.destination,
    );
    try expectContains(bridge_note.why_now, "reviewable landed helper slice");
    try expectContains(bridge_note.why_now, "live descriptor or reopen side effects");
}

test "phase 8 libbpf survey note stays grounded in the current helper-plus-build packet" {
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
        "survey checkpoint: refreshed against inspected `master` head `" ++ surveyed_commit ++ "`",
    );
    try expectContains(
        phase8_note,
        "`Documentation/zigux/README.md` now names the live `Documentation/zigux/phase8-file-path-handle-bridge-slice.md` note in the broad Phase 8 docs summary, public Phase 8 readback still serves `Documentation/zigux/phase8-bpf-type-names-slice.md`, and `scripts/zigux/README.md` keeps the broader Phase 8 libbpf helper packet visible through the shared sequencing, bridge-boundary, bridge-slice, checker, and build-surface reminders.",
    );
    try expectContains(
        phase8_note,
        "`zigux/tests/phase8_build.zig` still wires the current libbpf helper-first shard packet",
    );
    try expectContains(
        phase8_note,
        "targeted readable helper blobs still include `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, and `tools/lib/bpf/zigux_segments/type_names.zig`, while `zigux/tests/phase8_pin_path.zig` remains readable even though authenticated contents reads from this environment still return `404` for `Documentation/zigux/phase8-pin-path-slice.md` and `tools/lib/bpf/zigux_segments/pin_path.zig`",
    );
    try expectContains(
        phase8_note,
        "current shared reminder surfaces already keep the landed bridge-plus-build packet explicit through `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_libbpf_segments_only_build.zig`, `zigux/tests/phase8_build.zig`, `zigux/Makefile`, and `scripts/zigux/validate-phase8.py`.",
    );
    try expectContains(
        phase8_note,
        "current `master` also carries helper-local routing evidence in `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`",
    );
    try expectContains(phase8_note, "advanceOnlineCpuCursor()");
    try expectContains(phase8_note, "summarizeNextOnlineCpuRoute()");
    try expectContains(phase8_note, "summarizeOnlineCpuRouting()");
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
        "The real current gap is now survey truthfulness about the already-landed checker packet, helper-local routing evidence, and the landed bridge-plus-build packet itself, not environment-specific contents-route flakiness or a missing checker rule.",
    );
    try expectContains(
        phase8_note,
        "The older mixed-source caveat is now too weak for this packet.",
    );
    try expectContains(
        phase8_note,
        "Current repo-facing reminder surfaces already keep the bridge helper, the focused bridge build shard, the focused libbpf-segment shard, and the shared Phase 8 build replay explicit on `master`, while that same checker packet already keeps the landed `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` helper-local evidence explicit.",
    );
    try expectContains(
        phase8_note,
        "Keep the libbpf survey packet parked after this survey-and-route sync unless a fresh shared reminder-surface drift reappears against the current helper-plus-build evidence.",
    );

    try expectNotContains(
        phase8_note,
        "current authenticated contents readback from this environment returns `404` for `tools/lib/bpf/zigux_segments/verify.zig`",
    );
    try expectNotContains(
        phase8_note,
        "they do not currently confirm the bridge helper, the focused bridge build shard, the focused libbpf-segment build shard, or the broader Phase 8 build replay.",
    );
}

test "phase 8 libbpf survey keeps routing helper and perf-buffer boundary explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const routing_helper = try readFileAlloc(
        io_instance.io(),
        std.testing.allocator,
        "tools/lib/bpf/zigux_segments/online_cpu_routing.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(routing_helper);

    try expectContains(routing_helper, "pub fn advanceOnlineCpuCursor(");
    try expectContains(routing_helper, "pub fn summarizeNextOnlineCpuRoute(");
    try expectContains(routing_helper, "pub fn summarizeOnlineCpuRouting(");
    try expectContains(
        routing_helper,
        "test \"summarizeOnlineCpuRouting reports the first routed online CPU whose fd slot is empty\" {",
    );

    const boundary_note = try readFileAlloc(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(boundary_note);
    try expectContains(boundary_note, "`python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py`");
    try expectContains(boundary_note, "`make -C zigux phase8-perf-buffer-poll-test`");
    try expectContains(boundary_note, "standalone timer helper behavior");
    try expectContains(boundary_note, "clockevent helper behavior");
    try expectContains(
        boundary_note,
        "It likewise does not claim standalone timer helper behavior or standalone\nclockevent helper behavior.",
    );

    const poll_note = try readFileAlloc(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(poll_note);
    try expectContains(poll_note, "- no standalone timer helper behavior");
    try expectContains(poll_note, "- no standalone clockevent helper behavior");
    try expectContains(poll_note, "`make -C zigux phase8-perf-buffer-poll-test`");
    try expectContains(
        poll_note,
        "If it reopens, keep follow-up smaller than full routing, epoll, timer, clockevent, object-model, or ring-lifecycle work.",
    );

    const phase8_note = try readFileAlloc(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase8-libbpf-segment-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(phase8_note);
    try expectContains(phase8_note, "`Documentation/zigux/phase8-perf-buffer-poll-slice.md`");
    try expectContains(phase8_note, "standalone timer or clockevent helper behavior");
    try expectContains(phase8_note, "broader timeout-sensitive routing behavior");
}
