const std = @import("std");
const cpu_mask = @import("cpu_mask");
const bpf_type_names = @import("bpf_type_names");
const logging = @import("logging");
const pin_path = @import("pin_path");
const file_path_handle_bridge = @import("file_path_handle_bridge");
const perf_buffer_poll = @import("perf_buffer_poll");

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    gaps: []const Gap,
};

const Snapshot = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    tracked_file_count: usize,
    tracked_paths: []const []const u8,
};

const LegacySegment = struct {
    id: []const u8,
    slug: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const LegacyManifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    segments: []const LegacySegment,
};

fn pathExists(io: std.Io, path: []const u8) !bool {
    std.Io.Dir.cwd().access(io, path, .{}) catch |err| switch (err) {
        error.FileNotFound => return false,
        else => return err,
    };
    return true;
}

test "phase12 libbpf reviewability gate matches the current zigux_segments file state" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase12_libbpf_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);
    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P12-L16", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 12", manifest.phase);
    try std.testing.expectEqualStrings("c0ae127363e3d4e5feeb36efb665a12ece3392c7", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 18), manifest.gaps.len);
    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var deferred_count: usize = 0;
    var saw_landed_manifest = false;
    var saw_landed_type_names = false;
    var saw_landed_cpu_mask = false;
    var saw_landed_perf_buffer_poll = false;
    var saw_landed_logging = false;
    var saw_landed_pin_path = false;
    var saw_fdinfo_ready_next = false;
    var saw_map_reuse_ready_next = false;
    var saw_file_path_handle_bridge = false;
    var saw_perf_buffer_online_cpu_routing = false;
    var saw_blocked_skeleton = false;
    var saw_blocked_object_loader = false;
    var saw_blocked_relocation = false;
    for (manifest.gaps, 0..) |gap, i| {
        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_object_model")) {
            blocked_count += 1;
        } else if (std.mem.eql(u8, gap.status, "deferred_high_risk")) {
            deferred_count += 1;
        }
        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
        if (!std.mem.startsWith(u8, gap.zigux_destination, "tools/lib/bpf/zigux_segments/")) {
            continue;
        }
        const exists = try pathExists(io_instance.io(), gap.zigux_destination);
        const shared_file_path_handle_destination =
            std.mem.eql(u8, gap.id, "phase12-libbpf-fdinfo-map-info-helper-ready-next") or
            std.mem.eql(u8, gap.id, "phase12-libbpf-map-reuse-compatibility-ready-next") or
            std.mem.eql(u8, gap.id, "phase12-libbpf-file-path-and-handle-bridge");
        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            try std.testing.expect(exists);
        } else if (shared_file_path_handle_destination or std.mem.eql(u8, gap.id, "phase12-libbpf-perf-buffer-online-cpu-routing")) {
            try std.testing.expect(exists);
        } else if (std.mem.eql(u8, gap.status, "ready_next") or std.mem.eql(u8, gap.status, "blocked_on_object_model") or std.mem.eql(u8, gap.status, "deferred_high_risk")) {
            try std.testing.expect(!exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-segment-manifest-foundation")) {
            saw_landed_manifest = true;
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-type-name-helper-foundation")) {
            saw_landed_type_names = true;
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-cpu-mask-helper-foundation")) {
            saw_landed_cpu_mask = true;
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-perf-buffer-poll-helper-foundation")) {
            saw_landed_perf_buffer_poll = true;
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-logging-helper-foundation")) {
            saw_landed_logging = true;
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-pin-path-helper-foundation")) {
            saw_landed_pin_path = true;
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-fdinfo-map-info-helper-ready-next")) {
            saw_fdinfo_ready_next = true;
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-map-reuse-compatibility-ready-next")) {
            saw_map_reuse_ready_next = true;
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-file-path-and-handle-bridge")) {
            saw_file_path_handle_bridge = true;
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-perf-buffer-online-cpu-routing")) {
            saw_perf_buffer_online_cpu_routing = true;
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-skeleton-population")) {
            saw_blocked_skeleton = true;
            try std.testing.expect(!exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-object-loader-and-program-load")) {
            saw_blocked_object_loader = true;
            try std.testing.expect(!exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-btf-relocation-and-program-load")) {
            saw_blocked_relocation = true;
            try std.testing.expect(!exists);
        }
    }
    try std.testing.expectEqual(@as(usize, 11), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 2), ready_next_count);
    try std.testing.expectEqual(@as(usize, 2), blocked_count);
    try std.testing.expectEqual(@as(usize, 3), deferred_count);
    try std.testing.expect(saw_landed_manifest);
    try std.testing.expect(saw_landed_type_names);
    try std.testing.expect(saw_landed_cpu_mask);
    try std.testing.expect(saw_landed_perf_buffer_poll);
    try std.testing.expect(saw_landed_logging);
    try std.testing.expect(saw_landed_pin_path);
    try std.testing.expect(saw_fdinfo_ready_next);
    try std.testing.expect(saw_map_reuse_ready_next);
    try std.testing.expect(saw_file_path_handle_bridge);
    try std.testing.expect(saw_perf_buffer_online_cpu_routing);
    try std.testing.expect(saw_blocked_skeleton);
    try std.testing.expect(saw_blocked_object_loader);
    try std.testing.expect(saw_blocked_relocation);
}

test "phase12 libbpf reviewability gate snapshot matches the tracked helper set" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    const snapshot_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/fixtures/phase12_libbpf_snapshot.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(snapshot_json);
    const parsed = try std.json.parseFromSlice(Snapshot, std.testing.allocator, snapshot_json, .{});
    defer parsed.deinit();
    const snapshot = parsed.value;
    try std.testing.expectEqualStrings("P12-L16", snapshot.lane_key);
    try std.testing.expectEqualStrings("Phase 12", snapshot.phase);
    try std.testing.expectEqualStrings("c0ae127363e3d4e5feeb36efb665a12ece3392c7", snapshot.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 5), snapshot.tracked_file_count);
    try std.testing.expectEqual(snapshot.tracked_file_count, snapshot.tracked_paths.len);

    var saw_type_names = false;
    var saw_cpu_mask = false;
    var saw_logging = false;
    var saw_pin_path = false;
    var saw_perf_buffer_poll = false;

    for (snapshot.tracked_paths, 0..) |tracked_path, i| {
        try std.testing.expect(try pathExists(io_instance.io(), tracked_path));
        try std.testing.expect(std.mem.startsWith(u8, tracked_path, "tools/lib/bpf/zigux_segments/"));
        for (snapshot.tracked_paths[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, tracked_path, other));
        }
        if (std.mem.eql(u8, tracked_path, "tools/lib/bpf/zigux_segments/type_names.zig")) {
            saw_type_names = true;
        }
        if (std.mem.eql(u8, tracked_path, "tools/lib/bpf/zigux_segments/cpu_mask.zig")) {
            saw_cpu_mask = true;
        }
        if (std.mem.eql(u8, tracked_path, "tools/lib/bpf/zigux_segments/logging.zig")) {
            saw_logging = true;
        }
        if (std.mem.eql(u8, tracked_path, "tools/lib/bpf/zigux_segments/pin_path.zig")) {
            saw_pin_path = true;
        }
        if (std.mem.eql(u8, tracked_path, "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig")) {
            saw_perf_buffer_poll = true;
        }
    }

    try std.testing.expect(saw_type_names);
    try std.testing.expect(saw_cpu_mask);
    try std.testing.expect(saw_logging);
    try std.testing.expect(saw_pin_path);
    try std.testing.expect(saw_perf_buffer_poll);
}

test "phase12 libbpf reviewability gate still compiles the landed helper foundations and the shared bridge destination" {
    const parsed = try cpu_mask.parseCpuMaskString(std.testing.allocator, "0-1,3");
    defer parsed.deinit(std.testing.allocator);
    var path_buffer: [64]u8 = undefined;
    var error_buffer: [64]u8 = undefined;
    var fdinfo_path_buffer: [64]u8 = undefined;
    const ready_buffers = [_]perf_buffer_poll.BufferObservation{
        .{ .ready = true },
        .{ .error_code = -11 },
    };
    try std.testing.expectEqual(@as(usize, 3), cpu_mask.countPossibleCpus(parsed.values));
    try std.testing.expectEqualStrings("xdp", bpf_type_names.libbpfBpfAttachTypeStr(37).?);
    try std.testing.expectEqualStrings("ringbuf", bpf_type_names.libbpfBpfMapTypeStr(27).?);
    try std.testing.expectEqualStrings("v1.8", logging.libbpfVersionString());
    try std.testing.expectEqualStrings(
        "Internal error in libbpf",
        try logging.formatErrorString(&error_buffer, -4004),
    );
    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/demo_map",
        try pin_path.buildValidatedSanitizedMapPinPath(&path_buffer, null, "demo.map"),
    );
    try std.testing.expectError(
        error.InvalidName,
        pin_path.buildValidatedSanitizedMapPinPath(&path_buffer, null, "demo/map"),
    );
    try std.testing.expectError(
        error.InvalidRootPath,
        pin_path.buildValidatedSanitizedMapPinPath(&path_buffer, "tmp/bpf", "demo.map"),
    );
    try std.testing.expectEqualStrings(
        "/proc/42/fdinfo/7",
        try file_path_handle_bridge.buildProcFdinfoPath(&fdinfo_path_buffer, 42, 7),
    );
    const parsed_fdinfo = try file_path_handle_bridge.parseFdinfoMapInfo(
        \\map_type: 14
        \\key_size: 4
        \\value_size: 8
        \\max_entries: 64
        \\map_flags: 0x20
        \\map_extra: 7
    );
    try std.testing.expectEqual(@as(?u32, 14), parsed_fdinfo.map_type);
    const resolved_name = file_path_handle_bridge.resolveReusedMapName(
        "process_pinned_map",
        "process_pinned_",
    );
    try std.testing.expectEqual(
        file_path_handle_bridge.ReusedMapNameSource.object_name,
        resolved_name.source,
    );
    try std.testing.expectEqualStrings("process_pinned_map", resolved_name.value);
    try std.testing.expectEqualDeep(
        perf_buffer_poll.WaitObservation{ .ready_events = 2 },
        perf_buffer_poll.classifyObservedWaitResult(2),
    );
    const poll_summary = try perf_buffer_poll.summarizePoll(7, .{ .ready_events = 2 }, &ready_buffers);
    try std.testing.expectEqual(perf_buffer_poll.WaitClass.bounded, poll_summary.wait_class);
    try std.testing.expectEqual(perf_buffer_poll.PollOutcome.ready, poll_summary.outcome);
    try std.testing.expectEqual(@as(usize, 1), poll_summary.ready_count);
    try std.testing.expectEqual(@as(?i32, -11), poll_summary.first_error);
}

test "phase12 libbpf reviewability gate cross-checks the legacy segment catalog" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "tools/lib/bpf/zigux_segments/manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);
    const parsed = try std.json.parseFromSlice(LegacyManifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P8-L15", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 8", manifest.phase);
    try std.testing.expectEqualStrings("0e8ce03f80f631368bfa3c32452d615bb629e3db", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 12), manifest.segments.len);
    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var deferred_count: usize = 0;
    var saw_logging = false;
    var saw_pin_path = false;
    var saw_cpu_mask = false;
    var saw_type_names = false;
    var saw_perf_buffer_poll = false;
    var saw_fdinfo_map_info = false;
    var saw_map_reuse = false;
    var saw_file_path_handle_bridge = false;
    var saw_perf_buffer_online_cpu_routing = false;
    var saw_skeleton = false;
    var saw_object_loader = false;
    var saw_relocation = false;
    for (manifest.segments, 0..) |segment, i| {
        if (std.mem.eql(u8, segment.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, segment.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, segment.status, "blocked_on_object_model")) {
            blocked_count += 1;
        } else if (std.mem.eql(u8, segment.status, "deferred_high_risk")) {
            deferred_count += 1;
        }
        for (manifest.segments[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, segment.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, segment.slug, other.slug));
        }
        const exists = try pathExists(io_instance.io(), segment.zigux_destination);
        if (std.mem.eql(u8, segment.slug, "logging-version-and-errno")) {
            saw_logging = true;
            try std.testing.expectEqualStrings("starter_landed", segment.status);
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, segment.slug, "pin-path-helpers")) {
            saw_pin_path = true;
            try std.testing.expectEqualStrings("starter_landed", segment.status);
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, segment.slug, "cpu-mask-parsing")) {
            saw_cpu_mask = true;
            try std.testing.expectEqualStrings("starter_landed", segment.status);
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, segment.slug, "type-name-helpers")) {
            saw_type_names = true;
            try std.testing.expectEqualStrings("starter_landed", segment.status);
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, segment.slug, "perf-buffer-poll-bookkeeping")) {
            saw_perf_buffer_poll = true;
            try std.testing.expectEqualStrings("starter_landed", segment.status);
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, segment.slug, "fdinfo-map-info-helpers")) {
            saw_fdinfo_map_info = true;
            try std.testing.expectEqualStrings("starter_landed", segment.status);
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, segment.slug, "map-reuse-compatibility")) {
            saw_map_reuse = true;
            try std.testing.expectEqualStrings("starter_landed", segment.status);
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, segment.slug, "file-path-and-handle-bridge")) {
            saw_file_path_handle_bridge = true;
            try std.testing.expectEqualStrings("deferred_high_risk", segment.status);
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, segment.slug, "perf-buffer-online-cpu-routing")) {
            saw_perf_buffer_online_cpu_routing = true;
            try std.testing.expectEqualStrings("deferred_high_risk", segment.status);
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, segment.slug, "skeleton-population")) {
            saw_skeleton = true;
            try std.testing.expectEqualStrings("blocked_on_object_model", segment.status);
            try std.testing.expect(!exists);
        }
        if (std.mem.eql(u8, segment.slug, "object-and-elf-loader")) {
            saw_object_loader = true;
            try std.testing.expectEqualStrings("deferred_high_risk", segment.status);
            try std.testing.expect(!exists);
        }
        if (std.mem.eql(u8, segment.slug, "btf-relocation-and-program-load")) {
            saw_relocation = true;
            try std.testing.expectEqualStrings("deferred_high_risk", segment.status);
            try std.testing.expect(!exists);
        }
    }
    try std.testing.expectEqual(@as(usize, 7), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expectEqual(@as(usize, 4), deferred_count);
    try std.testing.expect(saw_logging);
    try std.testing.expect(saw_pin_path);
    try std.testing.expect(saw_cpu_mask);
    try std.testing.expect(saw_type_names);
    try std.testing.expect(saw_perf_buffer_poll);
    try std.testing.expect(saw_fdinfo_map_info);
    try std.testing.expect(saw_map_reuse);
    try std.testing.expect(saw_file_path_handle_bridge);
    try std.testing.expect(saw_perf_buffer_online_cpu_routing);
    try std.testing.expect(saw_skeleton);
    try std.testing.expect(saw_object_loader);
    try std.testing.expect(saw_relocation);
}
