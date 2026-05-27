const std = @import("std");

const bridge = @import("file_path_handle_bridge.zig");

test "phase8 file-path bridge entrypoints stay explicit" {
    try std.testing.expect(@hasDecl(bridge, "default_proc_fdinfo_root"));
    try std.testing.expect(@hasDecl(bridge, "FilePathHandleBridgeError"));
    try std.testing.expect(@hasDecl(bridge, "FdinfoLine"));
    try std.testing.expect(@hasDecl(bridge, "FdinfoMapInfo"));
    try std.testing.expect(@hasDecl(bridge, "FdinfoMapInfoSummary"));
    try std.testing.expect(@hasDecl(bridge, "MapReuseObservation"));
    try std.testing.expect(@hasDecl(bridge, "MapReuseCompatibilityDisposition"));
    try std.testing.expect(@hasDecl(bridge, "MapReuseCompatibilitySummary"));
    try std.testing.expect(@hasDecl(bridge, "ReusedMapNameDisposition"));
    try std.testing.expect(@hasDecl(bridge, "ReusedMapNameSummary"));
    try std.testing.expect(@hasDecl(bridge, "ReusePinnedMapAttemptDisposition"));
    try std.testing.expect(@hasDecl(bridge, "ReusePinnedMapAttemptSummary"));
    try std.testing.expect(@hasDecl(bridge, "TokenPreparationDisposition"));
    try std.testing.expect(@hasDecl(bridge, "TokenPreparationPlan"));
    try std.testing.expect(@hasDecl(bridge, "validateProcFdinfoRoot"));
    try std.testing.expect(@hasDecl(bridge, "buildProcFdinfoPath"));
    try std.testing.expect(@hasDecl(bridge, "buildCurrentProcessFdinfoPath"));
    try std.testing.expect(@hasDecl(bridge, "buildProcFdinfoPathReturn"));
    try std.testing.expect(@hasDecl(bridge, "buildCurrentProcessFdinfoPathReturn"));
    try std.testing.expect(@hasDecl(bridge, "parseFdinfoLine"));
    try std.testing.expect(@hasDecl(bridge, "applyFdinfoMapInfoLine"));
    try std.testing.expect(@hasDecl(bridge, "parseFdinfoMapInfo"));
    try std.testing.expect(@hasDecl(bridge, "summarizeFdinfoMapInfo"));
    try std.testing.expect(@hasDecl(bridge, "mapReuseObservationFromFdinfo"));
    try std.testing.expect(@hasDecl(bridge, "normalizeObservedReuseMapFlags"));
    try std.testing.expect(@hasDecl(bridge, "summarizeMapReuseCompatibility"));
    try std.testing.expect(@hasDecl(bridge, "isMapReuseCompatible"));
    try std.testing.expect(@hasDecl(bridge, "summarizeReusedMapName"));
    try std.testing.expect(@hasDecl(bridge, "resolveReusedMapName"));
    try std.testing.expect(@hasDecl(bridge, "resolveReusedMapNameReturn"));
    try std.testing.expect(@hasDecl(bridge, "resolveReusePinnedMapAttempt"));
    try std.testing.expect(@hasDecl(bridge, "planTokenPreparation"));
}

test "phase8 file-path bridge keeps helper-only outputs stable" {
    var path_buffer: [64]u8 = undefined;
    var name_buffer: [64]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/proc/self/fdinfo/41",
        try bridge.buildProcFdinfoPath(&path_buffer, null, 41),
    );
    try std.testing.expectEqualStrings(
        "/proc/4242/fdinfo/7",
        try bridge.buildCurrentProcessFdinfoPath(&path_buffer, 4242, 7),
    );
    try std.testing.expectEqualStrings(
        "stats_map",
        try bridge.resolveReusedMapName(&name_buffer, "stats_map\x00"),
    );
    const fdinfo = try bridge.parseFdinfoLine("map_flags:\t0x20\n");
    try std.testing.expectEqualStrings("map_flags", fdinfo.key);
    try std.testing.expectEqualStrings("0x20", fdinfo.value);

    const terminated = try bridge.summarizeReusedMapName("stats_map\x00stale");
    try std.testing.expectEqual(bridge.ReusedMapNameDisposition.terminated_prefix, terminated.disposition);
    try std.testing.expectEqual(@as(?usize, 9), terminated.terminator_index);
    try std.testing.expectEqualStrings("stats_map", terminated.name);
    try std.testing.expectEqualStrings(
        "stats_map",
        try bridge.resolveReusedMapName(&name_buffer, "stats_map\x00stale"),
    );

    const truncated = try bridge.summarizeReusedMapName("truncated_name");
    try std.testing.expectEqual(bridge.ReusedMapNameDisposition.truncated_fixed_width, truncated.disposition);
    try std.testing.expectEqual(@as(?usize, null), truncated.terminator_index);
    try std.testing.expectEqualStrings("truncated_name", truncated.name);
    try std.testing.expectEqualStrings(
        "truncated_name",
        try bridge.resolveReusedMapName(&name_buffer, "truncated_name"),
    );
}

test "phase8 file-path bridge keeps fdinfo-map-info and planning helpers stable" {
    const parsed = try bridge.parseFdinfoMapInfo(
        \\map_type: 14
        \\key_size: 4
        \\value_size: 8
        \\max_entries: 16
        \\map_flags: 0x80
        \\map_extra: 0x20
    );
    const summary = bridge.summarizeFdinfoMapInfo(parsed);
    const observation = bridge.mapReuseObservationFromFdinfo(parsed);
    const compatibility = bridge.summarizeMapReuseCompatibility(observation, .{
        .map_type = 14,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 16,
        .map_flags = 0,
        .map_extra = 0x20,
    });

    try std.testing.expectEqual(@as(?u32, 14), parsed.map_type);
    try std.testing.expectEqual(@as(?u32, 0x80), parsed.map_flags);
    try std.testing.expectEqual(@as(?u64, 0x20), parsed.map_extra);
    try std.testing.expectEqual(@as(usize, 6), summary.parsed_field_count);
    try std.testing.expect(summary.has_complete_legacy_fields);
    try std.testing.expect(summary.has_map_extra);
    try std.testing.expectEqual(@as(?u32, 14), observation.map_type);
    try std.testing.expectEqual(@as(?u32, 0x80), observation.map_flags);
    try std.testing.expectEqual(@as(?u64, 0x20), observation.map_extra);
    try std.testing.expectEqual(@as(?u32, 0), compatibility.normalized_observed_map_flags);
    try std.testing.expectEqual(@as(?u32, 0), compatibility.normalized_expected_map_flags);
    try std.testing.expect(compatibility.compatible);
    try std.testing.expect(bridge.isMapReuseCompatible(observation, compatibility.expected));

    const reuse_attempt = try bridge.resolveReusePinnedMapAttempt("stats_map\x00", parsed);
    try std.testing.expectEqual(
        bridge.ReusePinnedMapAttemptDisposition.ready_for_reopen_attempt,
        reuse_attempt.disposition,
    );
    try std.testing.expect(reuse_attempt.should_attempt_reopen);
    try std.testing.expectEqualStrings("stats_map", reuse_attempt.retained_name.?);

    const token_plan = bridge.planTokenPreparation(reuse_attempt);
    try std.testing.expectEqual(
        bridge.TokenPreparationDisposition.ready_for_token_open_attempt,
        token_plan.disposition,
    );
    try std.testing.expect(token_plan.should_attempt_token_open);
}

test "phase8 file-path bridge keeps reuse-flag normalization and mismatch reporting stable" {
    const devmap_observed = bridge.MapReuseObservation{
        .map_type = 14,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 16,
        .map_flags = 0x80,
        .map_extra = 0x20,
    };
    const devmap_expected = bridge.MapReuseObservation{
        .map_type = 14,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 16,
        .map_flags = 0,
        .map_extra = 0x20,
    };
    const devmap_compatibility = bridge.summarizeMapReuseCompatibility(devmap_observed, devmap_expected);
    try std.testing.expectEqual(@as(?u32, 0), bridge.normalizeObservedReuseMapFlags(14, 0x80));
    try std.testing.expectEqual(@as(?u32, 0), bridge.normalizeObservedReuseMapFlags(15, 0x80));
    try std.testing.expectEqual(bridge.MapReuseCompatibilityDisposition.compatible, devmap_compatibility.disposition);
    try std.testing.expect(devmap_compatibility.compatible);
    try std.testing.expect(bridge.isMapReuseCompatible(devmap_observed, devmap_expected));

    const plain_flags_mismatch = bridge.summarizeMapReuseCompatibility(.{
        .map_type = 5,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 16,
        .map_flags = 0x80,
        .map_extra = 0x20,
    }, .{
        .map_type = 5,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 16,
        .map_flags = 0,
        .map_extra = 0x20,
    });
    try std.testing.expectEqual(@as(?u32, 0x80), bridge.normalizeObservedReuseMapFlags(5, 0x80));
    try std.testing.expectEqual(
        bridge.MapReuseCompatibilityDisposition.map_flags_mismatch,
        plain_flags_mismatch.disposition,
    );
    try std.testing.expect(!plain_flags_mismatch.compatible);

    const map_extra_mismatch = bridge.summarizeMapReuseCompatibility(devmap_observed, .{
        .map_type = 14,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 16,
        .map_flags = 0,
        .map_extra = 0x21,
    });
    try std.testing.expectEqual(
        bridge.MapReuseCompatibilityDisposition.map_extra_mismatch,
        map_extra_mismatch.disposition,
    );
    try std.testing.expect(!map_extra_mismatch.compatible);
    try std.testing.expect(!bridge.isMapReuseCompatible(devmap_observed, map_extra_mismatch.expected));
}

test "phase8 file-path bridge keeps validation and errno outputs stable" {
    var path_buffer: [64]u8 = undefined;
    var name_buffer: [64]u8 = undefined;

    try std.testing.expectError(error.InvalidProcRoot, bridge.buildProcFdinfoPath(&path_buffer, "proc/fdinfo", 1));
    try std.testing.expectError(error.NegativeFd, bridge.buildProcFdinfoPath(&path_buffer, null, -1));
    try std.testing.expectError(error.NegativePid, bridge.buildCurrentProcessFdinfoPath(&path_buffer, -1, 1));
    try std.testing.expectError(error.EmptyFdinfoLine, bridge.parseFdinfoLine(""));
    try std.testing.expectError(error.MissingSeparator, bridge.parseFdinfoLine("map_flags 0x20"));
    try std.testing.expectError(error.InvalidInteger, bridge.parseFdinfoMapInfo("map_flags:\t-1\n"));
    try std.testing.expectError(error.EmptyMapName, bridge.resolveReusedMapName(&name_buffer, ""));

    var tiny_name_buffer: [4]u8 = undefined;
    try std.testing.expectError(error.NameTooLong, bridge.resolveReusedMapName(&tiny_name_buffer, "stats_map"));

    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        bridge.buildProcFdinfoPathReturn(&path_buffer, "proc/fdinfo", 1),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        bridge.buildCurrentProcessFdinfoPathReturn(&path_buffer, -1, 1),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        bridge.resolveReusedMapNameReturn(&name_buffer, ""),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NAMETOOLONG)),
        bridge.resolveReusedMapNameReturn(&tiny_name_buffer, "stats_map"),
    );

    const incomplete = try bridge.resolveReusePinnedMapAttempt("stats_map\x00", .{
        .map_type = 14,
        .key_size = 4,
    });
    try std.testing.expectEqual(
        bridge.ReusePinnedMapAttemptDisposition.incomplete_fdinfo_map_info,
        incomplete.disposition,
    );
    try std.testing.expect(!incomplete.should_attempt_reopen);
    const skipped = bridge.planTokenPreparation(incomplete);
    try std.testing.expectEqual(
        bridge.TokenPreparationDisposition.skip_token_open_attempt,
        skipped.disposition,
    );
    try std.testing.expect(!skipped.should_attempt_token_open);
}
