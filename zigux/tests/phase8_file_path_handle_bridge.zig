const std = @import("std");
const file_path_handle_bridge = @import("file_path_handle_bridge");

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

test "phase 8 file-path handle bridge docs keep the bounded fdinfo helper explicit" {
    const note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(note);

    try expectContains(note, "\"/proc/%d/fdinfo/%d\"");
    try expectContains(note, "map_type");
    try expectContains(note, "key_size");
    try expectContains(note, "value_size");
    try expectContains(note, "max_entries");
    try expectContains(note, "map_flags");
    try expectContains(note, "map_extra");
    try expectContains(note, "bounded reuse-pinned-map attempt planning");
    try expectContains(note, "helper-only reused-map compatibility packet");
    try expectContains(note, "broader bridge follow-through queued");
    try expectContains(note, "planning-only reopen-attempt disposition");
    try expectContains(note, "no direct procfs reads");
    try expectContains(note, "no `fopen()` or `fgets()` parity");
    try expectContains(note, "no `bpf_map_get_info_by_fd()` fallback control flow");
    try expectContains(note, "no actual bpffs opens or `bpf_obj_get()` reopen calls");
    try expectContains(note, "no fd duplication or `F_DUPFD_CLOEXEC` handling");
    try expectContains(note, "no token materialization or handle transfer");
}

test "phase 8 userspace-kernel bridge boundary survey keeps queued bridge work explicit" {
    const survey = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(survey);

    try expectContains(survey, "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig");
    try expectContains(survey, "zigux/tests/phase8_file_path_handle_bridge.zig");
    try expectContains(survey, "zigux/tests/phase8_file_path_handle_bridge_only_build.zig");
    try expectContains(survey, "Documentation/zigux/phase8-file-path-handle-bridge-slice.md");
    try expectContains(survey, "planTokenPreparation()");
    try expectContains(survey, "resolveReusePinnedMapAttempt()");
    try expectContains(survey, "planning-only gate");
    try expectContains(survey, "non-empty pinned path plus compatible fdinfo-derived map info");
    try expectContains(survey, "token materialization or capability handoff");
    try expectContains(survey, "map reopen or bpffs compatibility closure");
    try expectContains(survey, "fd close or ownership semantics");
    try expectContains(survey, "deferred `perf-buffer-online-cpu-routing` packet");
    try expectContains(survey, "/sys/devices/system/cpu/online");
    try expectContains(survey, "cached `/sys/devices/system/cpu/possible` counts via `libbpf_num_possible_cpus()`");
    try expectContains(survey, "online CPU filtering");
    try expectContains(survey, "per-CPU perf-event-array map updates");
    try expectContains(survey, "per-CPU `perf_event_open()` setup");
    try expectContains(survey, "perf-buffer ring `mmap()` setup");
    try expectContains(survey, "`PERF_EVENT_IOC_ENABLE` enablement");
    try expectContains(survey, "epoll-backed perf FD registration");
    try expectContains(survey, "poll waits");
    try expectContains(survey, "make -C zigux phase8-validate");
}

test "phase 8 file-path handle bridge helper stays wired into its focused Phase 8 build shard" {
    const focused_build_file = try readWorkspaceFile(
        std.testing.allocator,
        "zigux/tests/phase8_file_path_handle_bridge_only_build.zig",
        16 * 1024,
    );
    defer std.testing.allocator.free(focused_build_file);

    try expectContains(focused_build_file, "../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig");
    try expectContains(focused_build_file, "phase8_file_path_handle_bridge.zig");
    try expectContains(focused_build_file, "phase8-file-path-handle-bridge-tests");
}

test "phase 8 file-path handle bridge helper stays wired into the shared Phase 8 build shard" {
    const shared_build_file = try readWorkspaceFile(
        std.testing.allocator,
        "zigux/tests/phase8_build.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(shared_build_file);

    try expectContains(shared_build_file, "../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig");
    try expectContains(shared_build_file, "phase8_file_path_handle_bridge.zig");
    try expectContains(shared_build_file, "phase8-file-path-handle-bridge-tests");
}

test "phase 8 file-path handle bridge helper keeps proc fdinfo path formatting explicit" {
    var buffer: [64]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/proc/777/fdinfo/9",
        try file_path_handle_bridge.buildProcFdinfoPath(&buffer, 777, 9),
    );
}

test "phase 8 file-path handle bridge helper keeps fdinfo map info parsing compact" {
    const parsed = try file_path_handle_bridge.parseFdinfoMapInfo(
        \\map_type: 5
        \\key_size: 8
        \\value_size: 16
        \\max_entries: 1024
        \\map_flags: 0x20
        \\map_extra: 0X2A
    );
    const summary = file_path_handle_bridge.summarizeFdinfoMapInfo(parsed);

    try std.testing.expectEqual(@as(?u32, 5), parsed.map_type);
    try std.testing.expectEqual(@as(?u32, 0x20), parsed.map_flags);
    try std.testing.expectEqual(@as(?u64, 42), parsed.map_extra);
    try std.testing.expectEqual(@as(usize, 6), summary.parsed_field_count);
    try std.testing.expect(summary.has_complete_legacy_fields);
    try std.testing.expect(summary.has_map_extra);
}

test "phase 8 file-path handle bridge helper keeps malformed fdinfo values explicit" {
    var info = file_path_handle_bridge.FdinfoMapInfo{};

    try std.testing.expectError(
        error.InvalidInteger,
        file_path_handle_bridge.applyFdinfoMapInfoLine(&info, "map_flags:\t-1"),
    );
    try std.testing.expectError(
        error.InvalidInteger,
        file_path_handle_bridge.applyFdinfoMapInfoLine(&info, "map_extra:\tnope"),
    );
    try std.testing.expectError(
        error.MissingSeparator,
        file_path_handle_bridge.parseFdinfoLine("map_type"),
    );
}

test "phase 8 file-path handle bridge helper keeps fdinfo observations reusable for planning-only compatibility" {
    try std.testing.expectEqual(
        @as(?file_path_handle_bridge.MapReuseObservation, null),
        file_path_handle_bridge.mapReuseObservationFromFdinfo("stats", .{
            .map_type = 5,
            .key_size = 8,
        }),
    );

    const expected = file_path_handle_bridge.MapReuseExpectation{
        .name = "stats_map",
        .map_type = file_path_handle_bridge.bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 64,
        .map_flags = 0x20,
        .map_extra = 7,
    };
    const observation = file_path_handle_bridge.mapReuseObservationFromFdinfo("stats_map", .{
        .map_type = file_path_handle_bridge.bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 64,
        .map_flags = 0x20 | file_path_handle_bridge.bpf_f_rdonly_prog,
        .map_extra = 7,
    }).?;
    const compatibility = file_path_handle_bridge.summarizeMapReuseCompatibility(expected, observation);

    try std.testing.expectEqualStrings("stats_map", observation.name);
    try std.testing.expectEqual(file_path_handle_bridge.MapReuseCompatibility.compatible, compatibility.outcome);
    try std.testing.expectEqual(@as(u32, 0x20), compatibility.normalized_observed_map_flags);
    try std.testing.expect(file_path_handle_bridge.isMapReuseCompatible(expected, observation));
}

test "phase 8 file-path handle bridge helper keeps planning-only reopen attempts explicit" {
    const expected = file_path_handle_bridge.MapReuseExpectation{
        .name = "process_pinned_map",
        .map_type = file_path_handle_bridge.bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 64,
        .map_flags = 0x20,
        .map_extra = 7,
    };

    const plan = file_path_handle_bridge.resolveReusePinnedMapAttempt("/sys/fs/bpf/stats", expected, .{
        .name = "process_pinned_",
        .map_type = file_path_handle_bridge.bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 64,
        .map_flags = 0x20 | file_path_handle_bridge.bpf_f_rdonly_prog,
        .map_extra = 7,
    });
    try std.testing.expectEqual(
        file_path_handle_bridge.ReusePinnedMapAttemptDisposition.ready_for_reopen_attempt,
        plan.disposition,
    );
    try std.testing.expectEqual(
        file_path_handle_bridge.ReusedMapNameSource.object_name,
        plan.resolved_name.?.source,
    );
    try std.testing.expectEqualStrings("process_pinned_map", plan.resolved_name.?.value);
    try std.testing.expectEqualStrings("/sys/fs/bpf/stats", plan.pinned_path.?);
    try std.testing.expect(plan.should_attempt_reopen);
}
