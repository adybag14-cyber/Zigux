const std = @import("std");
const file_path_handle_bridge = @import("file_path_handle_bridge");

test "phase 8 file-path-handle bridge segment imports cleanly" {
    _ = file_path_handle_bridge;
}

test "phase 8 file-path-handle bridge builds proc fdinfo paths without widening into io" {
    var buffer: [64]u8 = undefined;
    var short_buffer: [8]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/proc/4321/fdinfo/9",
        try file_path_handle_bridge.buildFdinfoPath(&buffer, 4321, 9),
    );
    try std.testing.expectError(error.InvalidPid, file_path_handle_bridge.buildFdinfoPath(&buffer, 0, 9));
    try std.testing.expectError(error.InvalidFd, file_path_handle_bridge.buildFdinfoPath(&buffer, 4321, -3));
    try std.testing.expectError(error.PathTooLong, file_path_handle_bridge.buildFdinfoPath(&short_buffer, 4321, 9));
}

test "phase 8 file-path-handle bridge keeps the current-process fdinfo helper aligned" {
    var actual: [64]u8 = undefined;
    var expected: [64]u8 = undefined;

    try std.testing.expectEqualStrings(
        try std.fmt.bufPrint(&expected, "/proc/{d}/fdinfo/{d}", .{ std.os.linux.getpid(), 11 }),
        try file_path_handle_bridge.buildCurrentProcessFdinfoPath(&actual, 11),
    );
    try std.testing.expectError(error.InvalidFd, file_path_handle_bridge.buildCurrentProcessFdinfoPath(&actual, -1));
}

test "phase 8 file-path-handle bridge plans token preparation without claiming live bpffs io" {
    const prevented = file_path_handle_bridge.planTokenPreparation("");
    try std.testing.expectEqual(
        file_path_handle_bridge.TokenPreparationDisposition.prevented,
        prevented.disposition,
    );
    try std.testing.expectEqualStrings("", prevented.bpffs_path);
    try std.testing.expectEqual(@as(?file_path_handle_bridge.TokenPreparationLogLevel, null), prevented.log_level);
    try std.testing.expect(!prevented.requiresBpffsOpen());
    try std.testing.expect(!prevented.requiresTokenCreate());

    const optional = file_path_handle_bridge.planTokenPreparation(null);
    try std.testing.expectEqual(
        file_path_handle_bridge.TokenPreparationDisposition.optional_probe,
        optional.disposition,
    );
    try std.testing.expectEqualStrings(file_path_handle_bridge.default_bpf_fs_path, optional.bpffs_path);
    try std.testing.expectEqual(file_path_handle_bridge.TokenPreparationLogLevel.debug, optional.log_level.?);
    try std.testing.expect(optional.requiresBpffsOpen());
    try std.testing.expect(optional.requiresTokenCreate());

    const mandatory = file_path_handle_bridge.planTokenPreparation("/custom/bpffs");
    try std.testing.expectEqual(
        file_path_handle_bridge.TokenPreparationDisposition.mandatory_probe,
        mandatory.disposition,
    );
    try std.testing.expectEqualStrings("/custom/bpffs", mandatory.bpffs_path);
    try std.testing.expectEqual(file_path_handle_bridge.TokenPreparationLogLevel.warn, mandatory.log_level.?);
    try std.testing.expect(mandatory.requiresBpffsOpen());
    try std.testing.expect(mandatory.requiresTokenCreate());
}

test "phase 8 file-path-handle bridge keeps token failure recovery discipline explicit" {
    const prevented = file_path_handle_bridge.classifyTokenPreparationFailure(
        file_path_handle_bridge.planTokenPreparation(""),
        .bpffs_open,
        -@as(i32, @intFromEnum(std.os.linux.E.ACCES)),
    );
    try std.testing.expectEqual(
        file_path_handle_bridge.TokenPreparationFailureDisposition.skip_optional,
        prevented.disposition,
    );
    try std.testing.expectEqual(file_path_handle_bridge.TokenPreparationLogLevel.debug, prevented.log_level);
    try std.testing.expectEqualStrings(", skipping optional step...", prevented.message_suffix);
    try std.testing.expect(prevented.shouldContinueWithoutToken());

    const optional_missing_delegation = file_path_handle_bridge.classifyTokenPreparationFailure(
        file_path_handle_bridge.planTokenPreparation(null),
        .token_create,
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
    );
    try std.testing.expectEqual(
        file_path_handle_bridge.TokenPreparationFailureDisposition.skip_optional_missing_delegation,
        optional_missing_delegation.disposition,
    );
    try std.testing.expectEqual(file_path_handle_bridge.TokenPreparationLogLevel.debug, optional_missing_delegation.log_level);
    try std.testing.expectEqualStrings("", optional_missing_delegation.message_suffix);
    try std.testing.expect(optional_missing_delegation.shouldContinueWithoutToken());

    const mandatory_create = file_path_handle_bridge.classifyTokenPreparationFailure(
        file_path_handle_bridge.planTokenPreparation("/custom/bpffs"),
        .token_create,
        -@as(i32, @intFromEnum(std.os.linux.E.PERM)),
    );
    try std.testing.expectEqual(
        file_path_handle_bridge.TokenPreparationFailureDisposition.fail,
        mandatory_create.disposition,
    );
    try std.testing.expectEqual(file_path_handle_bridge.TokenPreparationLogLevel.warn, mandatory_create.log_level);
    try std.testing.expectEqualStrings("", mandatory_create.message_suffix);
    try std.testing.expect(!mandatory_create.shouldContinueWithoutToken());

    const missing_pinned_map = file_path_handle_bridge.classifyReusePinnedMapOpenFailure(
        -@as(i32, @intFromEnum(std.os.linux.E.NOENT)),
    );
    try std.testing.expectEqual(
        file_path_handle_bridge.ReusePinnedMapOpenFailureDisposition.skip_missing_pinned_map,
        missing_pinned_map.disposition,
    );
    try std.testing.expectEqual(file_path_handle_bridge.TokenPreparationLogLevel.debug, missing_pinned_map.log_level);
    try std.testing.expect(missing_pinned_map.shouldContinueWithoutReuse());

    const denied_pinned_map = file_path_handle_bridge.classifyReusePinnedMapOpenFailure(
        -@as(i32, @intFromEnum(std.os.linux.E.PERM)),
    );
    try std.testing.expectEqual(
        file_path_handle_bridge.ReusePinnedMapOpenFailureDisposition.fail,
        denied_pinned_map.disposition,
    );
    try std.testing.expectEqual(file_path_handle_bridge.TokenPreparationLogLevel.warn, denied_pinned_map.log_level);
    try std.testing.expect(!denied_pinned_map.shouldContinueWithoutReuse());
}

test "phase 8 file-path-handle bridge keeps token acquisition ownership planning explicit" {
    const no_cache = file_path_handle_bridge.resolveTokenPreparationAcquisition(false);
    try std.testing.expectEqual(
        file_path_handle_bridge.TokenPreparationAcquisitionDisposition.cache_allocation_failed,
        no_cache.disposition,
    );
    try std.testing.expectEqual(-@as(i32, @intFromEnum(std.os.linux.E.NOMEM)), no_cache.result_code);
    try std.testing.expect(no_cache.should_close_token_fd);
    try std.testing.expect(!no_cache.should_store_token_fd);
    try std.testing.expect(!no_cache.should_store_feat_cache_token_fd);
    try std.testing.expect(!no_cache.succeeded());

    const prepared = file_path_handle_bridge.resolveTokenPreparationAcquisition(true);
    try std.testing.expectEqual(
        file_path_handle_bridge.TokenPreparationAcquisitionDisposition.prepared,
        prepared.disposition,
    );
    try std.testing.expectEqual(@as(i32, 0), prepared.result_code);
    try std.testing.expect(!prepared.should_close_token_fd);
    try std.testing.expect(prepared.should_store_token_fd);
    try std.testing.expect(prepared.should_store_feat_cache_token_fd);
    try std.testing.expect(prepared.succeeded());
}

test "phase 8 file-path-handle bridge plans pinned-map reopen probes without claiming bpffs io" {
    const prevented_null = file_path_handle_bridge.planReusePinnedMapOpen(null);
    try std.testing.expectEqual(
        file_path_handle_bridge.ReusePinnedMapOpenDisposition.prevented,
        prevented_null.disposition,
    );
    try std.testing.expectEqualStrings("", prevented_null.pin_path);
    try std.testing.expect(!prevented_null.requiresPinnedMapOpen());

    const prevented_empty = file_path_handle_bridge.planReusePinnedMapOpen("");
    try std.testing.expectEqual(
        file_path_handle_bridge.ReusePinnedMapOpenDisposition.prevented,
        prevented_empty.disposition,
    );
    try std.testing.expectEqualStrings("", prevented_empty.pin_path);
    try std.testing.expect(!prevented_empty.requiresPinnedMapOpen());

    const planned = file_path_handle_bridge.planReusePinnedMapOpen("/sys/fs/bpf/reused_map");
    try std.testing.expectEqual(
        file_path_handle_bridge.ReusePinnedMapOpenDisposition.optional_probe,
        planned.disposition,
    );
    try std.testing.expectEqualStrings("/sys/fs/bpf/reused_map", planned.pin_path);
    try std.testing.expect(planned.requiresPinnedMapOpen());
}

test "phase 8 file-path-handle bridge keeps reuse-attempt ownership planning explicit" {
    const incompatible = file_path_handle_bridge.resolveReusePinnedMapAttempt(false, 0);
    try std.testing.expectEqual(
        file_path_handle_bridge.ReusePinnedMapResolutionDisposition.incompatible_map,
        incompatible.disposition,
    );
    try std.testing.expectEqual(-@as(i32, @intFromEnum(std.os.linux.E.INVAL)), incompatible.result_code);
    try std.testing.expect(incompatible.should_close_pin_fd);
    try std.testing.expect(!incompatible.should_mark_map_pinned);
    try std.testing.expect(!incompatible.succeeded());

    const reuse_failed = file_path_handle_bridge.resolveReusePinnedMapAttempt(
        true,
        -@as(i32, @intFromEnum(std.os.linux.E.PERM)),
    );
    try std.testing.expectEqual(
        file_path_handle_bridge.ReusePinnedMapResolutionDisposition.reuse_fd_failed,
        reuse_failed.disposition,
    );
    try std.testing.expectEqual(-@as(i32, @intFromEnum(std.os.linux.E.PERM)), reuse_failed.result_code);
    try std.testing.expect(reuse_failed.should_close_pin_fd);
    try std.testing.expect(!reuse_failed.should_mark_map_pinned);
    try std.testing.expect(!reuse_failed.succeeded());

    const reused = file_path_handle_bridge.resolveReusePinnedMapAttempt(true, 0);
    try std.testing.expectEqual(
        file_path_handle_bridge.ReusePinnedMapResolutionDisposition.reused,
        reused.disposition,
    );
    try std.testing.expectEqual(@as(i32, 0), reused.result_code);
    try std.testing.expect(reused.should_close_pin_fd);
    try std.testing.expect(reused.should_mark_map_pinned);
    try std.testing.expect(reused.succeeded());
}

test "phase 8 file-path-handle bridge parses bounded fdinfo map metadata" {
    const info = try file_path_handle_bridge.parseMapInfoFromFdinfo(
        "pos:\t0\n" ++
            "flags:\t02000002\n" ++
            "map_type:\t3\n" ++
            "key_size:\t4\n" ++
            "value_size:\t8\n" ++
            "max_entries:\t256\n" ++
            "map_flags:\t0x20\n" ++
            "map_extra:\t7\n",
    );

    try std.testing.expectEqual(@as(u32, 3), info.map_type);
    try std.testing.expectEqual(@as(u32, 4), info.key_size);
    try std.testing.expectEqual(@as(u32, 8), info.value_size);
    try std.testing.expectEqual(@as(u32, 256), info.max_entries);
    try std.testing.expectEqual(@as(u32, 0x20), info.map_flags);
    try std.testing.expectEqual(@as(u64, 7), info.map_extra);
}

test "phase 8 file-path-handle bridge accepts reordered fields and surrounding whitespace" {
    const info = try file_path_handle_bridge.parseMapInfoFromFdinfo(
        "map_flags:   512\r\n" ++
            "map_extra:\t0x10\r\n" ++
            "max_entries:\t128\r\n" ++
            "value_size:\t 8\r\n" ++
            "key_size:\t4\r\n" ++
            "map_type:\t1\r\n",
    );

    try std.testing.expectEqual(@as(u32, 0), info.map_id);
    try std.testing.expectEqual(@as(u32, 1), info.map_type);
    try std.testing.expectEqual(@as(u32, 4), info.key_size);
    try std.testing.expectEqual(@as(u32, 8), info.value_size);
    try std.testing.expectEqual(@as(u32, 128), info.max_entries);
    try std.testing.expectEqual(@as(u32, 512), info.map_flags);
    try std.testing.expectEqual(@as(u64, 0x10), info.map_extra);
}

test "phase 8 file-path-handle bridge keeps libbpf-style numeric bases explicit" {
    const info = try file_path_handle_bridge.parseMapInfoFromFdinfo(
        "map_type:\t1\r\n" ++
            "key_size:\t4\r\n" ++
            "value_size:\t8\r\n" ++
            "max_entries:\t16\r\n" ++
            "map_flags:\t010\r\n" ++
            "map_extra:\t0X2A\r\n",
    );

    try std.testing.expectEqual(@as(u32, 8), info.map_flags);
    try std.testing.expectEqual(@as(u64, 42), info.map_extra);
}

test "phase 8 file-path-handle bridge keeps reused-map name selection bounded and explicit" {
    try std.testing.expectEqualStrings(
        "process_pinned_map",
        file_path_handle_bridge.chooseReusedMapName("process_pinned_map", "process_pinned_"),
    );
    try std.testing.expectEqualStrings(
        "ringbuf_map",
        file_path_handle_bridge.chooseReusedMapName("ringbuf_map_local", "ringbuf_map"),
    );
    try std.testing.expectEqualStrings(
        "different_prefix",
        file_path_handle_bridge.chooseReusedMapName("process_pinned_map", "different_prefix"),
    );
    try std.testing.expectEqualStrings(
        "",
        file_path_handle_bridge.chooseReusedMapName("process_pinned_map", ""),
    );
}

test "phase 8 file-path-handle bridge mirrors libbpf zero-init and last-field-wins fdinfo fallback" {
    const info = try file_path_handle_bridge.parseMapInfoFromFdinfo(
        "map_id:\t1\n" ++
            "map_type:\t3\n" ++
            "key_size:\t4\n" ++
            "value_size:\t8\n" ++
            "map_extra:\t1\n" ++
            "map_id:\t9\n" ++
            "map_type:\t7\n" ++
            "map_extra:\t5\n" ++
            "map_flags:\t0x20\n" ++
            "map_flags:\t0x40\n",
    );

    try std.testing.expectEqual(@as(u32, 9), info.map_id);
    try std.testing.expectEqual(@as(u32, 7), info.map_type);
    try std.testing.expectEqual(@as(u32, 4), info.key_size);
    try std.testing.expectEqual(@as(u32, 8), info.value_size);
    try std.testing.expectEqual(@as(u32, 0), info.max_entries);
    try std.testing.expectEqual(@as(u32, 0x40), info.map_flags);
    try std.testing.expectEqual(@as(u64, 5), info.map_extra);
}

test "phase 8 file-path-handle bridge keeps malformed fdinfo values explicit" {
    try std.testing.expectError(error.InvalidValue, file_path_handle_bridge.parseMapInfoFromFdinfo(
        "map_id:\tbad\n" ++
            "map_type:\t3\n" ++
            "key_size:\t4\n" ++
            "value_size:\t8\n" ++
            "max_entries:\t256\n" ++
            "map_flags:\t32\n",
    ));
    try std.testing.expectError(error.InvalidValue, file_path_handle_bridge.parseMapInfoFromFdinfo(
        "map_type:\t3\n" ++
            "key_size:\tfour\n" ++
            "value_size:\t8\n" ++
            "max_entries:\t256\n" ++
            "map_flags:\t32\n",
    ));
    try std.testing.expectError(error.InvalidValue, file_path_handle_bridge.parseMapInfoFromFdinfo(
        "map_type:\t3\n" ++
            "key_size:\t4\n" ++
            "value_size:\t8\n" ++
            "max_entries:\t256\n" ++
            "map_flags:\t-1\n",
    ));
    try std.testing.expectError(error.InvalidValue, file_path_handle_bridge.parseMapInfoFromFdinfo(
        "map_type:\t3\n" ++
            "key_size:\t4\n" ++
            "value_size:\t8\n" ++
            "max_entries:\t256\n" ++
            "map_flags:\t0x100000000\n",
    ));
    try std.testing.expectError(error.InvalidValue, file_path_handle_bridge.parseMapInfoFromFdinfo(
        "map_type:\t3\n" ++
            "key_size:\t4\n" ++
            "value_size:\t8\n" ++
            "max_entries:\t256\n" ++
            "map_extra:\tbad\n",
    ));
}

test "phase 8 file-path-handle bridge keeps the DEVMAP readonly-prog compatibility exception explicit" {
    const expected = file_path_handle_bridge.FdInfoMapInfo{
        .map_type = file_path_handle_bridge.bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 4,
        .max_entries = 16,
        .map_flags = 0,
    };
    const actual = file_path_handle_bridge.FdInfoMapInfo{
        .map_type = file_path_handle_bridge.bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 4,
        .max_entries = 16,
        .map_flags = file_path_handle_bridge.bpf_f_rdonly_prog,
    };

    try std.testing.expectEqual(
        @as(u32, 0),
        file_path_handle_bridge.normalizeReuseCompatibilityMapFlags(expected.map_type, actual.map_flags),
    );
    try std.testing.expect(file_path_handle_bridge.isMapReuseCompatible(expected, actual));
    try std.testing.expectEqual(
        @as(u32, 0x20),
        file_path_handle_bridge.normalizeReuseCompatibilityMapFlags(
            file_path_handle_bridge.bpf_map_type_devmap_hash,
            file_path_handle_bridge.bpf_f_rdonly_prog | 0x20,
        ),
    );
}

test "phase 8 file-path-handle bridge keeps non-DEVMAP reuse mismatches explicit" {
    const expected = file_path_handle_bridge.FdInfoMapInfo{
        .map_type = 3,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 32,
        .map_flags = 0,
    };
    const actual = file_path_handle_bridge.FdInfoMapInfo{
        .map_type = 3,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 32,
        .map_flags = file_path_handle_bridge.bpf_f_rdonly_prog,
    };

    try std.testing.expectEqual(
        file_path_handle_bridge.bpf_f_rdonly_prog,
        file_path_handle_bridge.normalizeReuseCompatibilityMapFlags(expected.map_type, actual.map_flags),
    );
    try std.testing.expect(!file_path_handle_bridge.isMapReuseCompatible(expected, actual));
    try std.testing.expect(!file_path_handle_bridge.isMapReuseCompatible(expected, .{
        .map_type = 3,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 32,
        .map_flags = 0,
        .map_extra = 1,
    }));
}
