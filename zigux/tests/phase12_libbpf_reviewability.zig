const std = @import("std");
const cpu_mask = @import("cpu_mask");
const bpf_type_names = @import("bpf_type_names");
const file_path_handle_bridge = @import("file_path_handle_bridge");
const logging = @import("logging");
const pin_path = @import("pin_path");

const linux_errno = std.os.linux.E;

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

const Phase12LegacyPair = struct {
    phase12_gap_id: []const u8,
    legacy_slug: []const u8,
    expected_status: []const u8,
    expected_destination: []const u8,
};

const phase12_legacy_pairs = [_]Phase12LegacyPair{
    .{
        .phase12_gap_id = "phase12-libbpf-logging-helper-foundation",
        .legacy_slug = "logging-version-and-errno",
        .expected_status = "starter_landed",
        .expected_destination = "tools/lib/bpf/zigux_segments/logging.zig",
    },
    .{
        .phase12_gap_id = "phase12-libbpf-pin-path-helper-foundation",
        .legacy_slug = "pin-path-helpers",
        .expected_status = "starter_landed",
        .expected_destination = "tools/lib/bpf/zigux_segments/pin_path.zig",
    },
    .{
        .phase12_gap_id = "phase12-libbpf-cpu-mask-helper-foundation",
        .legacy_slug = "cpu-mask-parsing",
        .expected_status = "starter_landed",
        .expected_destination = "tools/lib/bpf/zigux_segments/cpu_mask.zig",
    },
    .{
        .phase12_gap_id = "phase12-libbpf-file-path-handle-helper-foundation",
        .legacy_slug = "fdinfo-map-info-helpers",
        .expected_status = "starter_landed",
        .expected_destination = "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    },
    .{
        .phase12_gap_id = "phase12-libbpf-map-reuse-compatibility-helper-foundation",
        .legacy_slug = "map-reuse-compatibility",
        .expected_status = "starter_landed",
        .expected_destination = "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    },
    .{
        .phase12_gap_id = "phase12-libbpf-file-path-and-handle-bridge-boundary",
        .legacy_slug = "file-path-and-handle-bridge",
        .expected_status = "deferred_high_risk",
        .expected_destination = "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    },
    .{
        .phase12_gap_id = "phase12-libbpf-perf-buffer-online-cpu-routing-boundary",
        .legacy_slug = "perf-buffer-online-cpu-routing",
        .expected_status = "deferred_high_risk",
        .expected_destination = "tools/lib/bpf/zigux_segments/cpu_mask.zig",
    },
    .{
        .phase12_gap_id = "phase12-libbpf-skeleton-population",
        .legacy_slug = "skeleton-population",
        .expected_status = "blocked_on_object_model",
        .expected_destination = "tools/lib/bpf/zigux_segments/skeleton.zig",
    },
    .{
        .phase12_gap_id = "phase12-libbpf-object-and-elf-loader",
        .legacy_slug = "object-and-elf-loader",
        .expected_status = "deferred_high_risk",
        .expected_destination = "tools/lib/bpf/zigux_segments/object_loader.zig",
    },
    .{
        .phase12_gap_id = "phase12-libbpf-btf-relocation-and-program-load",
        .legacy_slug = "btf-relocation-and-program-load",
        .expected_status = "deferred_high_risk",
        .expected_destination = "tools/lib/bpf/zigux_segments/relocation.zig",
    },
};

fn sharesDeferredBoundaryWithLandedHelper(gap_id: []const u8) bool {
    return std.mem.eql(u8, gap_id, "phase12-libbpf-file-path-and-handle-bridge-boundary") or
        std.mem.eql(u8, gap_id, "phase12-libbpf-perf-buffer-online-cpu-routing-boundary");
}

fn findPhase12Gap(manifest: Manifest, gap_id: []const u8) ?Gap {
    for (manifest.gaps) |gap| {
        if (std.mem.eql(u8, gap.id, gap_id)) {
            return gap;
        }
    }
    return null;
}

fn findLegacySegment(manifest: LegacyManifest, slug: []const u8) ?LegacySegment {
    for (manifest.segments) |segment| {
        if (std.mem.eql(u8, segment.slug, slug)) {
            return segment;
        }
    }
    return null;
}

fn pathExists(io: std.Io, path: []const u8) !bool {
    std.Io.Dir.cwd().access(io, path, .{}) catch |err| switch (err) {
        error.FileNotFound => return false,
        else => return err,
    };
    return true;
}

test "phase12 libbpf reviewability gate pins the committed snapshot fixture packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase12_libbpf_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const manifest_parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer manifest_parsed.deinit();

    const snapshot_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/fixtures/phase12_libbpf_snapshot.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(snapshot_json);

    const snapshot_parsed = try std.json.parseFromSlice(SnapshotFixture, std.testing.allocator, snapshot_json, .{
        .ignore_unknown_fields = true,
    });
    defer snapshot_parsed.deinit();

    const expected_paths = [_][]const u8{
        "zigux/tests/phase12_libbpf_manifest.json",
        "zigux/tests/phase12_libbpf_segments.zig",
        "zigux/tests/phase12_libbpf_reviewability.zig",
        "Documentation/zigux/phase12-libbpf-segment-survey.md",
        "tools/lib/bpf/zigux_segments/manifest.json",
    };

    const manifest = manifest_parsed.value;
    const snapshot = snapshot_parsed.value;
    try std.testing.expectEqualStrings(manifest.lane_key, snapshot.lane_key);
    try std.testing.expectEqualStrings(manifest.phase, snapshot.phase);
    try std.testing.expectEqualStrings(manifest.surveyed_commit, snapshot.surveyed_commit);
    try std.testing.expectEqual(expected_paths.len, snapshot.tracked_file_count);
    try std.testing.expectEqual(expected_paths.len, snapshot.files.len);

    for (snapshot.files, expected_paths) |entry, expected_path| {
        const live_bytes = try std.Io.Dir.cwd().readFileAlloc(
            io_instance.io(),
            expected_path,
            std.testing.allocator,
            .limited(64 * 1024),
        );
        defer std.testing.allocator.free(live_bytes);

        try std.testing.expectEqualStrings(expected_path, entry.path);
        try std.testing.expectEqual(live_bytes.len, entry.bytes);

        var live_sha256: [std.crypto.hash.sha2.Sha256.digest_length]u8 = undefined;
        std.crypto.hash.sha2.Sha256.hash(live_bytes, &live_sha256, .{});

        var live_sha256_hex: [std.crypto.hash.sha2.Sha256.digest_length * 2]u8 = undefined;
        const live_sha256_text = try std.fmt.bufPrint(
            &live_sha256_hex,
            "{}",
            .{std.fmt.fmtSliceHexLower(&live_sha256)},
        );
        try std.testing.expectEqualStrings(live_sha256_text, entry.sha256);
    }
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

    var saw_landed_manifest = false;
    var saw_landed_type_names = false;
    var saw_landed_cpu_mask = false;
    var saw_landed_logging = false;
    var saw_landed_pin_path = false;
    var saw_landed_file_path_handle_bridge = false;
    var saw_landed_map_reuse = false;
    var saw_deferred_file_path_handle_boundary = false;
    var saw_deferred_perf_buffer_routing_boundary = false;
    var saw_blocked_skeleton = false;
    var saw_blocked_object_loader = false;
    var saw_blocked_relocation = false;

    for (manifest.gaps) |gap| {
        if (!std.mem.startsWith(u8, gap.zigux_destination, "tools/lib/bpf/zigux_segments/")) {
            continue;
        }

        const exists = try pathExists(io_instance.io(), gap.zigux_destination);
        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            try std.testing.expect(exists);
        } else if (std.mem.eql(u8, gap.status, "blocked_on_object_model")) {
            try std.testing.expect(!exists);
        } else if (std.mem.eql(u8, gap.status, "deferred_high_risk")) {
            if (sharesDeferredBoundaryWithLandedHelper(gap.id)) {
                try std.testing.expect(exists);
            } else {
                try std.testing.expect(!exists);
            }
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
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
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-logging-helper-foundation")) {
            saw_landed_logging = true;
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-pin-path-helper-foundation")) {
            saw_landed_pin_path = true;
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-file-path-handle-helper-foundation")) {
            saw_landed_file_path_handle_bridge = true;
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-map-reuse-compatibility-helper-foundation")) {
            saw_landed_map_reuse = true;
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-file-path-and-handle-bridge-boundary")) {
            saw_deferred_file_path_handle_boundary = true;
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-perf-buffer-online-cpu-routing-boundary")) {
            saw_deferred_perf_buffer_routing_boundary = true;
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-skeleton-population")) {
            saw_blocked_skeleton = true;
            try std.testing.expect(!exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-object-and-elf-loader")) {
            saw_blocked_object_loader = true;
            try std.testing.expect(!exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-btf-relocation-and-program-load")) {
            saw_blocked_relocation = true;
            try std.testing.expect(!exists);
        }
    }

    try std.testing.expect(saw_landed_manifest);
    try std.testing.expect(saw_landed_type_names);
    try std.testing.expect(saw_landed_cpu_mask);
    try std.testing.expect(saw_landed_logging);
    try std.testing.expect(saw_landed_pin_path);
    try std.testing.expect(saw_landed_file_path_handle_bridge);
    try std.testing.expect(saw_landed_map_reuse);
    try std.testing.expect(saw_deferred_file_path_handle_boundary);
    try std.testing.expect(saw_deferred_perf_buffer_routing_boundary);
    try std.testing.expect(saw_blocked_skeleton);
    try std.testing.expect(saw_blocked_object_loader);
    try std.testing.expect(saw_blocked_relocation);
}

test "phase12 libbpf reviewability gate still compiles the landed helper foundations" {
    const parsed = try cpu_mask.parseCpuMaskString(std.testing.allocator, "0-1,3");
    defer parsed.deinit(std.testing.allocator);
    const fdinfo_map_info = try file_path_handle_bridge.parseMapInfoFromFdinfo(
        "map_type:\t2\n" ++
            "key_size:\t8\n" ++
            "value_size:\t16\n" ++
            "max_entries:\t64\n" ++
            "map_flags:\t0x400\n",
    );
    var fdinfo_path_buffer: [32]u8 = undefined;
    var path_buffer: [64]u8 = undefined;
    var error_buffer: [64]u8 = undefined;

    try std.testing.expectEqual(@as(usize, 3), cpu_mask.countPossibleCpus(parsed.values));
    try std.testing.expectEqual(@as(usize, 3), cpu_mask.derivePerfBufferAutoCpuCount(6, 3));
    try std.testing.expectEqual(@as(usize, 6), cpu_mask.derivePerfBufferAutoCpuCount(6, 0));
    try std.testing.expectEqualStrings("xdp", bpf_type_names.libbpfBpfAttachTypeStr(37).?);
    try std.testing.expectEqualStrings("ringbuf", bpf_type_names.libbpfBpfMapTypeStr(27).?);
    try std.testing.expectEqual(@as(u32, 2), fdinfo_map_info.map_type);
    try std.testing.expectEqualStrings(
        "/proc/321/fdinfo/7",
        try file_path_handle_bridge.buildFdinfoPath(&fdinfo_path_buffer, 321, 7),
    );
    try std.testing.expectEqualStrings(
        "process_pinned_map",
        file_path_handle_bridge.chooseReusedMapName("process_pinned_map", "process_pinned_"),
    );
    const optional_missing_delegation = file_path_handle_bridge.classifyTokenPreparationFailure(
        file_path_handle_bridge.planTokenPreparation(null),
        .token_create,
        -@as(i32, @intFromEnum(linux_errno.NOENT)),
    );
    const mandatory_failure = file_path_handle_bridge.classifyTokenPreparationFailure(
        file_path_handle_bridge.planTokenPreparation("/custom/bpffs"),
        .bpffs_open,
        -@as(i32, @intFromEnum(linux_errno.ACCES)),
    );
    const missing_pinned_map = file_path_handle_bridge.classifyReusePinnedMapOpenFailure(
        -@as(i32, @intFromEnum(linux_errno.NOENT)),
    );
    const denied_pinned_map = file_path_handle_bridge.classifyReusePinnedMapOpenFailure(
        -@as(i32, @intFromEnum(linux_errno.PERM)),
    );
    try std.testing.expectEqualStrings("v1.8", logging.libbpfVersionString());
    try std.testing.expectEqualStrings(
        "Internal error in libbpf",
        try logging.formatErrorString(&error_buffer, -4004),
    );
    try std.testing.expectEqual(
        file_path_handle_bridge.TokenPreparationFailureDisposition.skip_optional_missing_delegation,
        optional_missing_delegation.disposition,
    );
    try std.testing.expect(optional_missing_delegation.shouldContinueWithoutToken());
    try std.testing.expectEqualStrings("", optional_missing_delegation.message_suffix);
    try std.testing.expectEqual(
        file_path_handle_bridge.TokenPreparationFailureDisposition.fail,
        mandatory_failure.disposition,
    );
    try std.testing.expect(!mandatory_failure.shouldContinueWithoutToken());
    try std.testing.expectEqualStrings("", mandatory_failure.message_suffix);
    try std.testing.expectEqual(
        file_path_handle_bridge.ReusePinnedMapOpenFailureDisposition.skip_missing_pinned_map,
        missing_pinned_map.disposition,
    );
    try std.testing.expect(missing_pinned_map.shouldContinueWithoutReuse());
    try std.testing.expectEqual(file_path_handle_bridge.TokenPreparationLogLevel.debug, missing_pinned_map.log_level);
    try std.testing.expectEqual(
        file_path_handle_bridge.ReusePinnedMapOpenFailureDisposition.fail,
        denied_pinned_map.disposition,
    );
    try std.testing.expect(!denied_pinned_map.shouldContinueWithoutReuse());
    try std.testing.expectEqual(file_path_handle_bridge.TokenPreparationLogLevel.warn, denied_pinned_map.log_level);
    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/demo_map",
        try pin_path.buildValidatedSanitizedMapPinPath(&path_buffer, null, "demo.map"),
    );
    try std.testing.expect(file_path_handle_bridge.isMapReuseCompatible(.{
        .map_type = file_path_handle_bridge.bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 32,
        .map_flags = 0,
        .map_extra = 9,
    }, .{
        .map_type = file_path_handle_bridge.bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 32,
        .map_flags = file_path_handle_bridge.bpf_f_rdonly_prog,
        .map_extra = 9,
    }));
    try std.testing.expectError(
        error.InvalidName,
        pin_path.buildValidatedSanitizedMapPinPath(&path_buffer, null, "demo/map"),
    );
    try std.testing.expectError(
        error.InvalidRootPath,
        pin_path.buildValidatedSanitizedMapPinPath(&path_buffer, "tmp/bpf", "demo.map"),
    );

    const OversizeReader = struct {
        returned: bool = false,

        fn read(context: ?*anyopaque, buffer: []u8) !?usize {
            const self: *@This() = @ptrCast(@alignCast(context.?));
            if (self.returned) {
                return null;
            }

            self.returned = true;
            @memset(buffer, '1');
            return buffer.len;
        }
    };

    var oversize_reader = OversizeReader{};
    var cpu_mask_buffer: [cpu_mask.cpu_mask_file_read_limit + 1]u8 = undefined;
    try std.testing.expectError(
        error.InputTooLarge,
        cpu_mask.parseCpuMaskFromReader(std.testing.allocator, &cpu_mask_buffer, .{
            .context = &oversize_reader,
            .readFn = OversizeReader.read,
        }),
    );
}

test "phase12 libbpf reviewability gate cross-checks the legacy segment catalog" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const phase12_manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase12_libbpf_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(phase12_manifest_json);

    const phase12_parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, phase12_manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer phase12_parsed.deinit();

    const legacy_manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "tools/lib/bpf/zigux_segments/manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(legacy_manifest_json);

    const legacy_parsed = try std.json.parseFromSlice(LegacyManifest, std.testing.allocator, legacy_manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer legacy_parsed.deinit();

    const phase12_manifest = phase12_parsed.value;
    const legacy_manifest = legacy_parsed.value;
    try std.testing.expectEqualStrings("P12-L16", phase12_manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 12", phase12_manifest.phase);
    try std.testing.expectEqualStrings("P8-L15", legacy_manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 8", legacy_manifest.phase);

    for (phase12_legacy_pairs) |pair| {
        const phase12_gap = findPhase12Gap(phase12_manifest, pair.phase12_gap_id) orelse return error.TestUnexpectedResult;
        const legacy_segment = findLegacySegment(legacy_manifest, pair.legacy_slug) orelse return error.TestUnexpectedResult;
        const exists = try pathExists(io_instance.io(), pair.expected_destination);

        try std.testing.expectEqualStrings(pair.expected_status, phase12_gap.status);
        try std.testing.expectEqualStrings(pair.expected_destination, phase12_gap.zigux_destination);
        try std.testing.expectEqualStrings(pair.expected_status, legacy_segment.status);
        try std.testing.expectEqualStrings(pair.expected_destination, legacy_segment.zigux_destination);
        try std.testing.expect(legacy_segment.why_now.len > 0);

        if (std.mem.eql(u8, pair.legacy_slug, "cpu-mask-parsing")) {
            try std.testing.expect(std.mem.indexOf(u8, legacy_segment.why_now, "chunk-reader interface") != null);
            try std.testing.expect(std.mem.indexOf(u8, legacy_segment.why_now, "perf-buffer CPU-budget clamp") != null);
        } else if (std.mem.eql(u8, pair.legacy_slug, "fdinfo-map-info-helpers")) {
            try std.testing.expect(std.mem.indexOf(u8, legacy_segment.why_now, "token-preparation recovery classification") != null);
        } else if (std.mem.eql(u8, pair.legacy_slug, "map-reuse-compatibility")) {
            try std.testing.expect(std.mem.indexOf(u8, legacy_segment.why_now, "DEVMAP readonly-flag exception") != null);
        }

        if (std.mem.eql(u8, pair.expected_status, "starter_landed")) {
            try std.testing.expect(exists);
        } else if (std.mem.eql(u8, pair.expected_status, "blocked_on_object_model")) {
            try std.testing.expect(!exists);
        } else if (std.mem.eql(u8, pair.expected_status, "deferred_high_risk")) {
            if (sharesDeferredBoundaryWithLandedHelper(pair.phase12_gap_id)) {
                try std.testing.expect(exists);
            } else {
                try std.testing.expect(!exists);
            }
        }
    }
}
