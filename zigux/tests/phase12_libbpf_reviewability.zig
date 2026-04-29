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

fn sharesDeferredBoundaryWithLandedHelper(gap_id: []const u8) bool {
    return std.mem.eql(u8, gap_id, "phase12-libbpf-file-path-and-handle-bridge-boundary") or
        std.mem.eql(u8, gap_id, "phase12-libbpf-perf-buffer-online-cpu-routing-boundary");
}

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
    try std.testing.expectEqualStrings("P12-L13", manifest.lane_key);
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

    var saw_logging = false;
    var saw_pin_path = false;
    var saw_cpu_mask = false;
    var saw_fdinfo_map_info = false;
    var saw_map_reuse = false;
    var saw_file_path_handle_bridge_boundary = false;
    var saw_perf_buffer_routing_boundary = false;
    var saw_skeleton = false;
    var saw_object_loader = false;
    var saw_relocation = false;

    for (manifest.segments) |segment| {
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
            saw_file_path_handle_bridge_boundary = true;
            try std.testing.expectEqualStrings("deferred_high_risk", segment.status);
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, segment.slug, "perf-buffer-online-cpu-routing")) {
            saw_perf_buffer_routing_boundary = true;
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

    try std.testing.expect(saw_logging);
    try std.testing.expect(saw_pin_path);
    try std.testing.expect(saw_cpu_mask);
    try std.testing.expect(saw_fdinfo_map_info);
    try std.testing.expect(saw_map_reuse);
    try std.testing.expect(saw_file_path_handle_bridge_boundary);
    try std.testing.expect(saw_perf_buffer_routing_boundary);
    try std.testing.expect(saw_skeleton);
    try std.testing.expect(saw_object_loader);
    try std.testing.expect(saw_relocation);
}
