const std = @import("std");
const cpu_mask = @import("cpu_mask");
const bpf_type_names = @import("bpf_type_names");
const logging = @import("logging");
const pin_path = @import("pin_path");
const file_path_handle_bridge = @import("file_path_handle_bridge");

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

const SnapshotEntry = struct {
    path: []const u8,
    bytes: usize,
    sha256: []const u8,
};

const SnapshotFixture = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    tracked_file_count: usize,
    files: []const SnapshotEntry,
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

fn findGap(manifest: Manifest, id: []const u8) ?Gap {
    for (manifest.gaps) |gap| {
        if (std.mem.eql(u8, gap.id, id)) return gap;
    }
    return null;
}

fn findLegacySegment(manifest: LegacyManifest, slug: []const u8) ?LegacySegment {
    for (manifest.segments) |segment| {
        if (std.mem.eql(u8, segment.slug, slug)) return segment;
    }
    return null;
}

fn expectGap(manifest: Manifest, id: []const u8, status: []const u8, kind: []const u8, destination: []const u8) !void {
    const gap = findGap(manifest, id) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings(status, gap.status);
    try std.testing.expectEqualStrings(kind, gap.kind);
    try std.testing.expectEqualStrings(destination, gap.zigux_destination);
    try std.testing.expect(gap.why_now.len > 0);
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

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_object_model")) {
            blocked_count += 1;
        } else if (std.mem.eql(u8, gap.status, "deferred_high_risk")) {
            deferred_count += 1;
        } else {
            return error.TestUnexpectedResult;
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }

        if (!std.mem.startsWith(u8, gap.zigux_destination, "tools/lib/bpf/zigux_segments/")) continue;

        const exists = try pathExists(io_instance.io(), gap.zigux_destination);
        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            try std.testing.expect(exists);
        } else if (std.mem.eql(u8, gap.id, "phase12-libbpf-file-path-and-handle-bridge-boundary") or
            std.mem.eql(u8, gap.id, "phase12-libbpf-perf-buffer-online-cpu-routing-boundary"))
        {
            try std.testing.expect(exists);
        } else {
            try std.testing.expect(!exists);
        }
    }

    try std.testing.expectEqual(@as(usize, 13), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expectEqual(@as(usize, 4), deferred_count);
}

test "phase12 libbpf reviewability gate exact-checks the live helper and boundary ids" {
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
    try expectGap(manifest, "phase12-libbpf-file-path-handle-helper-foundation", "starter_landed", "helper_first", "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig");
    try expectGap(manifest, "phase12-libbpf-map-reuse-compatibility-helper-foundation", "starter_landed", "helper_first", "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig");
    try expectGap(manifest, "phase12-libbpf-file-path-and-handle-bridge-boundary", "deferred_high_risk", "resource_boundary", "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig");
    try expectGap(manifest, "phase12-libbpf-perf-buffer-online-cpu-routing-boundary", "deferred_high_risk", "interrupt_routing", "tools/lib/bpf/zigux_segments/cpu_mask.zig");
    try expectGap(manifest, "phase12-libbpf-skeleton-population", "blocked_on_object_model", "object_adjacent", "tools/lib/bpf/zigux_segments/skeleton.zig");
    try expectGap(manifest, "phase12-libbpf-object-and-elf-loader", "deferred_high_risk", "core_loader", "tools/lib/bpf/zigux_segments/object_loader.zig");
    try expectGap(manifest, "phase12-libbpf-btf-relocation-and-program-load", "deferred_high_risk", "verifier_facing", "tools/lib/bpf/zigux_segments/relocation.zig");
}

test "phase12 libbpf reviewability gate pins the current snapshot fixture packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const snapshot_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/fixtures/phase12_libbpf_snapshot.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(snapshot_json);

    const parsed = try std.json.parseFromSlice(SnapshotFixture, std.testing.allocator, snapshot_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const snapshot = parsed.value;
    const expected_paths = [_][]const u8{
        "zigux/tests/phase12_libbpf_manifest.json",
        "zigux/tests/phase12_libbpf_segments.zig",
        "zigux/tests/phase12_libbpf_reviewability.zig",
        "Documentation/zigux/phase12-libbpf-segment-survey.md",
        "tools/lib/bpf/zigux_segments/manifest.json",
    };

    try std.testing.expectEqualStrings("P12-L16", snapshot.lane_key);
    try std.testing.expectEqualStrings("Phase 12", snapshot.phase);
    try std.testing.expectEqualStrings("c0ae127363e3d4e5feeb36efb665a12ece3392c7", snapshot.surveyed_commit);
    try std.testing.expectEqual(expected_paths.len, snapshot.tracked_file_count);
    try std.testing.expectEqual(expected_paths.len, snapshot.files.len);

    for (snapshot.files, expected_paths) |entry, expected_path| {
        try std.testing.expectEqualStrings(expected_path, entry.path);
        try std.testing.expect(entry.bytes > 0);
        try std.testing.expectEqual(@as(usize, 64), entry.sha256.len);
    }
}

test "phase12 libbpf reviewability gate still compiles the landed helper foundations" {
    const parsed_mask = try cpu_mask.parseCpuMaskString(std.testing.allocator, "0-1,3");
    defer parsed_mask.deinit(std.testing.allocator);

    var pin_path_buffer: [64]u8 = undefined;
    var error_buffer: [64]u8 = undefined;
    var fdinfo_path_buffer: [64]u8 = undefined;

    try std.testing.expectEqual(@as(usize, 3), cpu_mask.countPossibleCpus(parsed_mask.values));
    try std.testing.expectEqualStrings("xdp", bpf_type_names.libbpfBpfAttachTypeStr(37).?);
    try std.testing.expectEqualStrings("ringbuf", bpf_type_names.libbpfBpfMapTypeStr(27).?);
    try std.testing.expectEqualStrings("v1.8", logging.libbpfVersionString());
    try std.testing.expectEqualStrings(
        "Internal error in libbpf",
        try logging.formatErrorString(&error_buffer, -4004),
    );
    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/demo_map",
        try pin_path.buildValidatedSanitizedMapPinPath(&pin_path_buffer, null, "demo.map"),
    );
    try std.testing.expectEqualStrings(
        "/proc/42/fdinfo/7",
        try file_path_handle_bridge.buildProcFdinfoPath(&fdinfo_path_buffer, 42, 7),
    );
    const parsed_fdinfo = try file_path_handle_bridge.parseFdinfoMapInfo(
        "map_type: 14\n" ++
            "key_size: 4\n" ++
            "value_size: 8\n" ++
            "max_entries: 64\n" ++
            "map_flags: 0x20\n" ++
            "map_extra: 7\n",
    );
    try std.testing.expectEqual(@as(?u32, 14), parsed_fdinfo.map_type);
    const resolved_name = file_path_handle_bridge.resolveReusedMapName("process_pinned_map", "process_pinned_");
    try std.testing.expectEqual(file_path_handle_bridge.ReusedMapNameSource.object_name, resolved_name.source);
    try std.testing.expectEqualStrings("process_pinned_map", resolved_name.value);
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
    try std.testing.expectEqual(@as(usize, 12), manifest.segments.len);

    const landed_slugs = [_][]const u8{
        "logging-version-and-errno",
        "pin-path-helpers",
        "cpu-mask-parsing",
        "type-name-helpers",
        "perf-buffer-poll-bookkeeping",
        "fdinfo-map-info-helpers",
        "map-reuse-compatibility",
    };
    for (landed_slugs) |slug| {
        const segment = findLegacySegment(manifest, slug) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("starter_landed", segment.status);
        try std.testing.expect(try pathExists(io_instance.io(), segment.zigux_destination));
    }

    const file_path_boundary = findLegacySegment(manifest, "file-path-and-handle-bridge") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("deferred_high_risk", file_path_boundary.status);
    try std.testing.expect(try pathExists(io_instance.io(), file_path_boundary.zigux_destination));

    const perf_routing_boundary = findLegacySegment(manifest, "perf-buffer-online-cpu-routing") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("deferred_high_risk", perf_routing_boundary.status);
    try std.testing.expect(try pathExists(io_instance.io(), perf_routing_boundary.zigux_destination));

    const skeleton = findLegacySegment(manifest, "skeleton-population") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("blocked_on_object_model", skeleton.status);
    try std.testing.expect(!try pathExists(io_instance.io(), skeleton.zigux_destination));

    const object_loader = findLegacySegment(manifest, "object-and-elf-loader") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("deferred_high_risk", object_loader.status);
    try std.testing.expect(!try pathExists(io_instance.io(), object_loader.zigux_destination));

    const relocation = findLegacySegment(manifest, "btf-relocation-and-program-load") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("deferred_high_risk", relocation.status);
    try std.testing.expect(!try pathExists(io_instance.io(), relocation.zigux_destination));
}
