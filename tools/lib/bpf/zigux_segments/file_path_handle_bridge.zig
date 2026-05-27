const std = @import("std");

pub const default_proc_fdinfo_root = "/proc/self/fdinfo";

const bpf_f_rdonly_prog: u32 = 1 << 7;
const bpf_map_type_devmap: u32 = 14;
const bpf_map_type_devmap_hash: u32 = 15;

pub const FilePathHandleBridgeError = error{
    EmptyMapName,
    EmptyFdinfoLine,
    EmptyFdinfoLineKey,
    EmptyFdinfoLineValue,
    MissingSeparator,
    InvalidProcRoot,
    NameTooLong,
    NegativeFd,
    NegativePid,
    InvalidInteger,
};

pub const FdinfoLine = struct {
    key: []const u8,
    value: []const u8,
};

pub const FdinfoMapInfo = struct {
    map_type: ?u32 = null,
    key_size: ?u32 = null,
    value_size: ?u32 = null,
    max_entries: ?u32 = null,
    map_flags: ?u32 = null,
    map_extra: ?u64 = null,
};

pub const FdinfoMapInfoSummary = struct {
    parsed_field_count: usize,
    has_complete_legacy_fields: bool,
    has_map_extra: bool,
};

pub const MapReuseObservation = struct {
    map_type: ?u32 = null,
    key_size: ?u32 = null,
    value_size: ?u32 = null,
    max_entries: ?u32 = null,
    map_flags: ?u32 = null,
    map_extra: ?u64 = null,
};

pub const MapReuseCompatibilityDisposition = enum {
    compatible,
    map_type_mismatch,
    key_size_mismatch,
    value_size_mismatch,
    max_entries_mismatch,
    map_flags_mismatch,
    map_extra_mismatch,
};

pub const MapReuseCompatibilitySummary = struct {
    disposition: MapReuseCompatibilityDisposition,
    compatible: bool,
    normalized_observed_map_flags: ?u32,
    normalized_expected_map_flags: ?u32,
    observed: MapReuseObservation,
    expected: MapReuseObservation,
};

pub const ReusedMapNameDisposition = enum {
    exact_name,
    terminated_prefix,
    truncated_fixed_width,
};

pub const ReusedMapNameSummary = struct {
    source_len: usize,
    retained_len: usize,
    terminator_index: ?usize,
    disposition: ReusedMapNameDisposition,
    name: []const u8,
};

pub const ReusePinnedMapAttemptDisposition = enum {
    missing_map_name,
    truncated_map_name,
    incomplete_fdinfo_map_info,
    ready_for_reopen_attempt,
};

pub const ReusePinnedMapAttemptSummary = struct {
    disposition: ReusePinnedMapAttemptDisposition,
    should_attempt_reopen: bool,
    retained_name: ?[]const u8,
    retained_name_disposition: ?ReusedMapNameDisposition,
    fdinfo_summary: FdinfoMapInfoSummary,
    reuse_observation: MapReuseObservation,
};

pub const TokenPreparationDisposition = enum {
    skip_token_open_attempt,
    ready_for_token_open_attempt,
};

pub const TokenPreparationPlan = struct {
    disposition: TokenPreparationDisposition,
    should_attempt_token_open: bool,
};

fn noSpaceToNameTooLong(err: anyerror) FilePathHandleBridgeError {
    return switch (err) {
        error.NoSpaceLeft => error.NameTooLong,
        else => unreachable,
    };
}

fn parseUnsignedAuto(comptime T: type, text: []const u8) FilePathHandleBridgeError!T {
    const trimmed = std.mem.trim(u8, text, " \t");
    if (trimmed.len == 0) {
        return error.InvalidInteger;
    }

    const base: u8 = if (std.mem.startsWith(u8, trimmed, "0x") or std.mem.startsWith(u8, trimmed, "0X"))
        16
    else
        10;
    const digits = if (base == 16) trimmed[2..] else trimmed;
    if (digits.len == 0) {
        return error.InvalidInteger;
    }

    return std.fmt.parseUnsigned(T, digits, base) catch error.InvalidInteger;
}

pub fn validateProcFdinfoRoot(root: []const u8) FilePathHandleBridgeError!void {
    if (root.len == 0 or root[0] != '/') {
        return error.InvalidProcRoot;
    }
    if (std.mem.indexOfScalar(u8, root, 0) != null) {
        return error.InvalidProcRoot;
    }
    if (root.len > 1 and root[root.len - 1] == '/') {
        return error.InvalidProcRoot;
    }
}

pub fn buildProcFdinfoPath(
    buffer: []u8,
    proc_root: ?[]const u8,
    fd: i32,
) FilePathHandleBridgeError![]const u8 {
    const root = proc_root orelse default_proc_fdinfo_root;
    try validateProcFdinfoRoot(root);
    if (fd < 0) {
        return error.NegativeFd;
    }
    return std.fmt.bufPrint(buffer, "{s}/{d}", .{ root, fd }) catch |err| noSpaceToNameTooLong(err);
}

pub fn buildCurrentProcessFdinfoPath(
    buffer: []u8,
    pid: i32,
    fd: i32,
) FilePathHandleBridgeError![]const u8 {
    if (pid < 0) {
        return error.NegativePid;
    }
    if (fd < 0) {
        return error.NegativeFd;
    }
    return std.fmt.bufPrint(buffer, "/proc/{d}/fdinfo/{d}", .{ pid, fd }) catch |err| noSpaceToNameTooLong(err);
}

pub fn parseFdinfoLine(line: []const u8) FilePathHandleBridgeError!FdinfoLine {
    const trimmed_line = std.mem.trim(u8, line, " \t\r\n");
    if (trimmed_line.len == 0) {
        return error.EmptyFdinfoLine;
    }

    const separator_index = std.mem.indexOfScalar(u8, trimmed_line, ':') orelse {
        return error.MissingSeparator;
    };

    const key = std.mem.trim(u8, trimmed_line[0..separator_index], " \t");
    if (key.len == 0) {
        return error.EmptyFdinfoLineKey;
    }

    const value = std.mem.trim(u8, trimmed_line[separator_index + 1 ..], " \t");
    if (value.len == 0) {
        return error.EmptyFdinfoLineValue;
    }

    return .{
        .key = key,
        .value = value,
    };
}

pub fn applyFdinfoMapInfoLine(
    info: *FdinfoMapInfo,
    line: []const u8,
) FilePathHandleBridgeError!void {
    const parsed = try parseFdinfoLine(line);

    if (std.mem.eql(u8, parsed.key, "map_type")) {
        info.map_type = try parseUnsignedAuto(u32, parsed.value);
        return;
    }
    if (std.mem.eql(u8, parsed.key, "key_size")) {
        info.key_size = try parseUnsignedAuto(u32, parsed.value);
        return;
    }
    if (std.mem.eql(u8, parsed.key, "value_size")) {
        info.value_size = try parseUnsignedAuto(u32, parsed.value);
        return;
    }
    if (std.mem.eql(u8, parsed.key, "max_entries")) {
        info.max_entries = try parseUnsignedAuto(u32, parsed.value);
        return;
    }
    if (std.mem.eql(u8, parsed.key, "map_flags")) {
        info.map_flags = try parseUnsignedAuto(u32, parsed.value);
        return;
    }
    if (std.mem.eql(u8, parsed.key, "map_extra")) {
        info.map_extra = try parseUnsignedAuto(u64, parsed.value);
    }
}

pub fn parseFdinfoMapInfo(text: []const u8) FilePathHandleBridgeError!FdinfoMapInfo {
    var info = FdinfoMapInfo{};
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        if (std.mem.trim(u8, line, " \t\r").len == 0) {
            continue;
        }
        try applyFdinfoMapInfoLine(&info, line);
    }
    return info;
}

pub fn summarizeFdinfoMapInfo(info: FdinfoMapInfo) FdinfoMapInfoSummary {
    var parsed_field_count: usize = 0;
    inline for (.{
        info.map_type,
        info.key_size,
        info.value_size,
        info.max_entries,
        info.map_flags,
    }) |field| {
        if (field != null) parsed_field_count += 1;
    }
    if (info.map_extra != null) parsed_field_count += 1;

    return .{
        .parsed_field_count = parsed_field_count,
        .has_complete_legacy_fields = info.map_type != null and
            info.key_size != null and
            info.value_size != null and
            info.max_entries != null and
            info.map_flags != null,
        .has_map_extra = info.map_extra != null,
    };
}

pub fn mapReuseObservationFromFdinfo(info: FdinfoMapInfo) MapReuseObservation {
    return .{
        .map_type = info.map_type,
        .key_size = info.key_size,
        .value_size = info.value_size,
        .max_entries = info.max_entries,
        .map_flags = info.map_flags,
        .map_extra = info.map_extra,
    };
}

pub fn normalizeObservedReuseMapFlags(map_type: ?u32, map_flags: ?u32) ?u32 {
    const flags = map_flags orelse return null;
    const observed_map_type = map_type orelse return flags;
    return switch (observed_map_type) {
        bpf_map_type_devmap, bpf_map_type_devmap_hash => flags & ~bpf_f_rdonly_prog,
        else => flags,
    };
}

pub fn summarizeMapReuseCompatibility(
    observed: MapReuseObservation,
    expected: MapReuseObservation,
) MapReuseCompatibilitySummary {
    const normalized_observed_flags = normalizeObservedReuseMapFlags(observed.map_type, observed.map_flags);
    const normalized_expected_flags = normalizeObservedReuseMapFlags(expected.map_type, expected.map_flags);

    const disposition: MapReuseCompatibilityDisposition =
        if (observed.map_type != expected.map_type)
            .map_type_mismatch
        else if (observed.key_size != expected.key_size)
            .key_size_mismatch
        else if (observed.value_size != expected.value_size)
            .value_size_mismatch
        else if (observed.max_entries != expected.max_entries)
            .max_entries_mismatch
        else if (normalized_observed_flags != normalized_expected_flags)
            .map_flags_mismatch
        else if (observed.map_extra != expected.map_extra)
            .map_extra_mismatch
        else
            .compatible;

    return .{
        .disposition = disposition,
        .compatible = disposition == .compatible,
        .normalized_observed_map_flags = normalized_observed_flags,
        .normalized_expected_map_flags = normalized_expected_flags,
        .observed = observed,
        .expected = expected,
    };
}

pub fn isMapReuseCompatible(
    observed: MapReuseObservation,
    expected: MapReuseObservation,
) bool {
    return summarizeMapReuseCompatibility(observed, expected).compatible;
}

fn retainedNameSlice(observed_name: []const u8) FilePathHandleBridgeError!ReusedMapNameSummary {
    if (observed_name.len == 0) {
        return error.EmptyMapName;
    }

    const terminator_index = std.mem.indexOfScalar(u8, observed_name, 0);
    const retained_len = terminator_index orelse observed_name.len;
    if (retained_len == 0) {
        return error.EmptyMapName;
    }

    const disposition: ReusedMapNameDisposition = if (terminator_index) |index|
        if (index + 1 == observed_name.len) .exact_name else .terminated_prefix
    else
        .truncated_fixed_width;

    return .{
        .source_len = observed_name.len,
        .retained_len = retained_len,
        .terminator_index = terminator_index,
        .disposition = disposition,
        .name = observed_name[0..retained_len],
    };
}

pub fn summarizeReusedMapName(observed_name: []const u8) FilePathHandleBridgeError!ReusedMapNameSummary {
    return retainedNameSlice(observed_name);
}

pub fn resolveReusedMapName(
    buffer: []u8,
    observed_name: []const u8,
) FilePathHandleBridgeError![]const u8 {
    const summary = try retainedNameSlice(observed_name);
    return std.fmt.bufPrint(buffer, "{s}", .{summary.name}) catch |err| noSpaceToNameTooLong(err);
}

pub fn resolveReusePinnedMapAttempt(
    observed_name: []const u8,
    fdinfo: FdinfoMapInfo,
) FilePathHandleBridgeError!ReusePinnedMapAttemptSummary {
    const fdinfo_summary = summarizeFdinfoMapInfo(fdinfo);
    const reuse_observation = mapReuseObservationFromFdinfo(fdinfo);

    if (observed_name.len == 0) {
        return .{
            .disposition = .missing_map_name,
            .should_attempt_reopen = false,
            .retained_name = null,
            .retained_name_disposition = null,
            .fdinfo_summary = fdinfo_summary,
            .reuse_observation = reuse_observation,
        };
    }

    const retained_name = summarizeReusedMapName(observed_name) catch |err| switch (err) {
        error.EmptyMapName => return .{
            .disposition = .missing_map_name,
            .should_attempt_reopen = false,
            .retained_name = null,
            .retained_name_disposition = null,
            .fdinfo_summary = fdinfo_summary,
            .reuse_observation = reuse_observation,
        },
        else => return err,
    };

    if (retained_name.disposition == .truncated_fixed_width) {
        return .{
            .disposition = .truncated_map_name,
            .should_attempt_reopen = false,
            .retained_name = retained_name.name,
            .retained_name_disposition = retained_name.disposition,
            .fdinfo_summary = fdinfo_summary,
            .reuse_observation = reuse_observation,
        };
    }

    if (!fdinfo_summary.has_complete_legacy_fields) {
        return .{
            .disposition = .incomplete_fdinfo_map_info,
            .should_attempt_reopen = false,
            .retained_name = retained_name.name,
            .retained_name_disposition = retained_name.disposition,
            .fdinfo_summary = fdinfo_summary,
            .reuse_observation = reuse_observation,
        };
    }

    return .{
        .disposition = .ready_for_reopen_attempt,
        .should_attempt_reopen = true,
        .retained_name = retained_name.name,
        .retained_name_disposition = retained_name.disposition,
        .fdinfo_summary = fdinfo_summary,
        .reuse_observation = reuse_observation,
    };
}

pub fn planTokenPreparation(reuse_attempt: ReusePinnedMapAttemptSummary) TokenPreparationPlan {
    return if (reuse_attempt.should_attempt_reopen) .{
        .disposition = .ready_for_token_open_attempt,
        .should_attempt_token_open = true,
    } else .{
        .disposition = .skip_token_open_attempt,
        .should_attempt_token_open = false,
    };
}

fn bridgeErrorReturn(err: FilePathHandleBridgeError) i32 {
    return switch (err) {
        error.NameTooLong => -@as(i32, @intFromEnum(std.os.linux.E.NAMETOOLONG)),
        error.EmptyMapName,
        error.EmptyFdinfoLine,
        error.EmptyFdinfoLineKey,
        error.EmptyFdinfoLineValue,
        error.MissingSeparator,
        error.InvalidProcRoot,
        error.NegativeFd,
        error.NegativePid,
        error.InvalidInteger,
        => -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
    };
}

fn bridgeLengthReturn(result: FilePathHandleBridgeError![]const u8) i32 {
    const value = result catch |err| return bridgeErrorReturn(err);
    return std.math.cast(i32, value.len) orelse -@as(i32, @intFromEnum(std.os.linux.E.OVERFLOW));
}

pub fn buildProcFdinfoPathReturn(
    buffer: []u8,
    proc_root: ?[]const u8,
    fd: i32,
) i32 {
    return bridgeLengthReturn(buildProcFdinfoPath(buffer, proc_root, fd));
}

pub fn buildCurrentProcessFdinfoPathReturn(
    buffer: []u8,
    pid: i32,
    fd: i32,
) i32 {
    return bridgeLengthReturn(buildCurrentProcessFdinfoPath(buffer, pid, fd));
}

pub fn resolveReusedMapNameReturn(buffer: []u8, observed_name: []const u8) i32 {
    return bridgeLengthReturn(resolveReusedMapName(buffer, observed_name));
}

test "phase8 file-path bridge keeps proc fdinfo path outputs stable" {
    var buffer: [64]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/proc/self/fdinfo/17",
        try buildProcFdinfoPath(&buffer, null, 17),
    );
    try std.testing.expectEqualStrings(
        "/proc/4242/fdinfo/9",
        try buildCurrentProcessFdinfoPath(&buffer, 4242, 9),
    );
}

test "phase8 file-path bridge keeps proc fdinfo validation failures explicit" {
    var buffer: [64]u8 = undefined;

    try std.testing.expectError(error.InvalidProcRoot, buildProcFdinfoPath(&buffer, "proc/fdinfo", 7));
    try std.testing.expectError(error.InvalidProcRoot, buildProcFdinfoPath(&buffer, "/proc/fdinfo/", 7));
    try std.testing.expectError(error.NegativeFd, buildProcFdinfoPath(&buffer, null, -1));
    try std.testing.expectError(error.NegativePid, buildCurrentProcessFdinfoPath(&buffer, -1, 7));
}

test "phase8 file-path bridge keeps proc fdinfo errno-shaped return helpers explicit" {
    var buffer: [64]u8 = undefined;

    try std.testing.expectEqual(
        @as(i32, "/proc/self/fdinfo/33".len),
        buildProcFdinfoPathReturn(&buffer, null, 33),
    );
    try std.testing.expectEqualStrings(
        "/proc/self/fdinfo/33",
        buffer[0.."/proc/self/fdinfo/33".len],
    );
    try std.testing.expectEqual(
        @as(i32, "/proc/77/fdinfo/33".len),
        buildCurrentProcessFdinfoPathReturn(&buffer, 77, 33),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        buildCurrentProcessFdinfoPathReturn(&buffer, -1, 33),
    );
}

test "phase8 file-path bridge keeps fdinfo line splitting outputs stable" {
    const simple = try parseFdinfoLine("map_flags:\t0x20\n");
    try std.testing.expectEqualStrings("map_flags", simple.key);
    try std.testing.expectEqualStrings("0x20", simple.value);
}

test "phase8 file-path bridge keeps fdinfo line parser failures explicit" {
    try std.testing.expectError(error.EmptyFdinfoLine, parseFdinfoLine(""));
    try std.testing.expectError(error.MissingSeparator, parseFdinfoLine("map_flags 0x20"));
    try std.testing.expectError(error.EmptyFdinfoLineKey, parseFdinfoLine(" : 0x20"));
    try std.testing.expectError(error.EmptyFdinfoLineValue, parseFdinfoLine("map_flags:\t "));
}

test "phase8 file-path bridge keeps fdinfo map info parsing compact" {
    const parsed = try parseFdinfoMapInfo(
        \\map_type: 5
        \\key_size: 8
        \\value_size: 16
        \\max_entries: 1024
        \\map_flags: 0x20
        \\map_extra: 0X2A
    );
    const summary = summarizeFdinfoMapInfo(parsed);

    try std.testing.expectEqual(@as(?u32, 5), parsed.map_type);
    try std.testing.expectEqual(@as(?u32, 0x20), parsed.map_flags);
    try std.testing.expectEqual(@as(?u64, 42), parsed.map_extra);
    try std.testing.expectEqual(@as(usize, 6), summary.parsed_field_count);
    try std.testing.expect(summary.has_complete_legacy_fields);
    try std.testing.expect(summary.has_map_extra);
}

test "phase8 file-path bridge keeps malformed fdinfo values explicit" {
    var info = FdinfoMapInfo{};
    try std.testing.expectError(
        error.InvalidInteger,
        applyFdinfoMapInfoLine(&info, "map_flags:\t-1"),
    );
    try std.testing.expectError(
        error.MissingSeparator,
        parseFdinfoLine("map_type"),
    );
}

test "phase8 file-path bridge keeps reuse observations and planning-only bridge summaries explicit" {
    const parsed = try parseFdinfoMapInfo(
        \\map_type: 14
        \\key_size: 4
        \\value_size: 8
        \\max_entries: 16
        \\map_flags: 0x80
    );
    const observation = mapReuseObservationFromFdinfo(parsed);
    const compatibility = summarizeMapReuseCompatibility(observation, .{
        .map_type = 14,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 16,
        .map_flags = 0,
    });
    try std.testing.expect(compatibility.compatible);

    const reuse_attempt = try resolveReusePinnedMapAttempt("stats_map\x00", parsed);
    try std.testing.expectEqual(
        ReusePinnedMapAttemptDisposition.ready_for_reopen_attempt,
        reuse_attempt.disposition,
    );
    try std.testing.expect(reuse_attempt.should_attempt_reopen);
    try std.testing.expectEqualStrings("stats_map", reuse_attempt.retained_name.?);
    try std.testing.expectEqual(
        ReusedMapNameDisposition.exact_name,
        reuse_attempt.retained_name_disposition.?,
    );

    const token_plan = planTokenPreparation(reuse_attempt);
    try std.testing.expectEqual(
        TokenPreparationDisposition.ready_for_token_open_attempt,
        token_plan.disposition,
    );
    try std.testing.expect(token_plan.should_attempt_token_open);
}

test "phase8 file-path bridge keeps missing-map-name reuse planning explicit" {
    const parsed = try parseFdinfoMapInfo(
        \\map_type: 14
        \\key_size: 4
        \\value_size: 8
        \\max_entries: 16
        \\map_flags: 0x80
    );

    const reuse_attempt = try resolveReusePinnedMapAttempt("", parsed);
    try std.testing.expectEqual(
        ReusePinnedMapAttemptDisposition.missing_map_name,
        reuse_attempt.disposition,
    );
    try std.testing.expect(!reuse_attempt.should_attempt_reopen);
    try std.testing.expectEqual(@as(?[]const u8, null), reuse_attempt.retained_name);
    try std.testing.expectEqual(@as(?ReusedMapNameDisposition, null), reuse_attempt.retained_name_disposition);
    try std.testing.expect(reuse_attempt.fdinfo_summary.has_complete_legacy_fields);

    const token_plan = planTokenPreparation(reuse_attempt);
    try std.testing.expectEqual(
        TokenPreparationDisposition.skip_token_open_attempt,
        token_plan.disposition,
    );
    try std.testing.expect(!token_plan.should_attempt_token_open);
}

test "phase8 file-path bridge treats a leading NUL map name as missing" {
    const parsed = try parseFdinfoMapInfo(
        \\map_type: 14
        \\key_size: 4
        \\value_size: 8
        \\max_entries: 16
        \\map_flags: 0x80
    );

    try std.testing.expectError(error.EmptyMapName, summarizeReusedMapName("\x00hidden"));

    var buffer: [32]u8 = undefined;
    try std.testing.expectError(error.EmptyMapName, resolveReusedMapName(&buffer, "\x00hidden"));
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        resolveReusedMapNameReturn(&buffer, "\x00hidden"),
    );

    const reuse_attempt = try resolveReusePinnedMapAttempt("\x00hidden", parsed);
    try std.testing.expectEqual(
        ReusePinnedMapAttemptDisposition.missing_map_name,
        reuse_attempt.disposition,
    );
    try std.testing.expect(!reuse_attempt.should_attempt_reopen);
    try std.testing.expectEqual(@as(?[]const u8, null), reuse_attempt.retained_name);
    try std.testing.expectEqual(@as(?ReusedMapNameDisposition, null), reuse_attempt.retained_name_disposition);

    const token_plan = planTokenPreparation(reuse_attempt);
    try std.testing.expectEqual(
        TokenPreparationDisposition.skip_token_open_attempt,
        token_plan.disposition,
    );
    try std.testing.expect(!token_plan.should_attempt_token_open);
}

test "phase8 file-path bridge keeps reused-map name retention summaries stable" {
    const exact = try summarizeReusedMapName("stats_map\x00");
    try std.testing.expectEqual(ReusedMapNameDisposition.exact_name, exact.disposition);
    try std.testing.expectEqualStrings("stats_map", exact.name);

    const terminated_prefix = try summarizeReusedMapName("stats_map\x00shadow");
    try std.testing.expectEqual(
        ReusedMapNameDisposition.terminated_prefix,
        terminated_prefix.disposition,
    );
    try std.testing.expectEqualStrings("stats_map", terminated_prefix.name);

    const truncated = try summarizeReusedMapName("stats_map_truncated");
    try std.testing.expectEqual(
        ReusedMapNameDisposition.truncated_fixed_width,
        truncated.disposition,
    );
    try std.testing.expectEqualStrings("stats_map_truncated", truncated.name);
}

test "phase8 file-path bridge keeps truncated retained names off the reopen path" {
    const parsed = try parseFdinfoMapInfo(
        \\map_type: 14
        \\key_size: 4
        \\value_size: 8
        \\max_entries: 16
        \\map_flags: 0x80
    );

    const terminated_prefix_attempt = try resolveReusePinnedMapAttempt("stats_map\x00shadow", parsed);
    try std.testing.expectEqual(
        ReusePinnedMapAttemptDisposition.ready_for_reopen_attempt,
        terminated_prefix_attempt.disposition,
    );
    try std.testing.expect(terminated_prefix_attempt.should_attempt_reopen);
    try std.testing.expectEqualStrings("stats_map", terminated_prefix_attempt.retained_name.?);
    try std.testing.expectEqual(
        ReusedMapNameDisposition.terminated_prefix,
        terminated_prefix_attempt.retained_name_disposition.?,
    );

    const truncated_attempt = try resolveReusePinnedMapAttempt("stats_map_truncated", parsed);
    try std.testing.expectEqual(
        ReusePinnedMapAttemptDisposition.truncated_map_name,
        truncated_attempt.disposition,
    );
    try std.testing.expect(!truncated_attempt.should_attempt_reopen);
    try std.testing.expectEqualStrings("stats_map_truncated", truncated_attempt.retained_name.?);
    try std.testing.expectEqual(
        ReusedMapNameDisposition.truncated_fixed_width,
        truncated_attempt.retained_name_disposition.?,
    );

    const token_plan = planTokenPreparation(truncated_attempt);
    try std.testing.expectEqual(
        TokenPreparationDisposition.skip_token_open_attempt,
        token_plan.disposition,
    );
    try std.testing.expect(!token_plan.should_attempt_token_open);
}
