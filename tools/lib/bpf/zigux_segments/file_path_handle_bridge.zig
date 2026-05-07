const std = @import("std");

pub const BridgeError = error{
    InvalidPid,
    InvalidFd,
    PathTooLong,
    MissingSeparator,
    EmptyFieldName,
    EmptyFieldValue,
    InvalidInteger,
};

pub const ParsedFdinfoLine = struct {
    field_name: []const u8,
    field_value: []const u8,
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

pub const bpf_obj_name_len: usize = 16;
pub const bpf_obj_name_capacity_without_nul: usize = bpf_obj_name_len - 1;
pub const bpf_f_rdonly_prog: u32 = 1 << 7;
pub const bpf_map_type_devmap: u32 = 14;
pub const bpf_map_type_devmap_hash: u32 = 25;

pub const ReusedMapNameSource = enum {
    object_name,
    kernel_name,
};

pub const ReusedMapName = struct {
    source: ReusedMapNameSource,
    value: []const u8,
};

pub const MapReuseExpectation = struct {
    name: []const u8,
    map_type: u32,
    key_size: u32,
    value_size: u32,
    max_entries: u32,
    map_flags: u32,
    map_extra: u64 = 0,
};

pub const MapReuseObservation = struct {
    name: []const u8,
    map_type: u32,
    key_size: u32,
    value_size: u32,
    max_entries: u32,
    map_flags: u32,
    map_extra: u64 = 0,
};

pub const ReusePinnedMapAttemptDisposition = enum {
    missing_pinned_path,
    missing_map_observation,
    incompatible_name,
    incompatible_map_definition,
    ready_for_reopen_attempt,
};

pub const ReusePinnedMapAttemptPlan = struct {
    disposition: ReusePinnedMapAttemptDisposition,
    pinned_path: ?[]const u8 = null,
    resolved_name: ?ReusedMapName = null,
    should_attempt_reopen: bool,
    compatibility: ?MapReuseCompatibilitySummary = null,
};

pub const MapReuseCompatibility = enum {
    compatible,
    map_type_mismatch,
    key_size_mismatch,
    value_size_mismatch,
    max_entries_mismatch,
    map_flags_mismatch,
    map_extra_mismatch,
};

pub const MapReuseCompatibilitySummary = struct {
    outcome: MapReuseCompatibility,
    normalized_observed_map_flags: u32,
};

fn noSpaceToPathTooLong(err: anyerror) BridgeError {
    return switch (err) {
        error.NoSpaceLeft => error.PathTooLong,
        else => unreachable,
    };
}

fn parseAutoBaseU32(text: []const u8) BridgeError!u32 {
    const trimmed = std.mem.trim(u8, text, " \t\r\n");
    if (trimmed.len == 0) return error.InvalidInteger;

    if (trimmed[0] == '-') return error.InvalidInteger;

    if (trimmed.len > 2 and trimmed[0] == '0' and (trimmed[1] == 'x' or trimmed[1] == 'X')) {
        return std.fmt.parseUnsigned(u32, trimmed[2..], 16) catch error.InvalidInteger;
    }
    if (trimmed.len > 1 and trimmed[0] == '0') {
        return std.fmt.parseUnsigned(u32, trimmed[1..], 8) catch error.InvalidInteger;
    }

    return std.fmt.parseUnsigned(u32, trimmed, 10) catch error.InvalidInteger;
}

fn parseAutoBaseU64(text: []const u8) BridgeError!u64 {
    const trimmed = std.mem.trim(u8, text, " \t\r\n");
    if (trimmed.len == 0) return error.InvalidInteger;

    if (trimmed[0] == '-') return error.InvalidInteger;

    if (trimmed.len > 2 and trimmed[0] == '0' and (trimmed[1] == 'x' or trimmed[1] == 'X')) {
        return std.fmt.parseUnsigned(u64, trimmed[2..], 16) catch error.InvalidInteger;
    }
    if (trimmed.len > 1 and trimmed[0] == '0') {
        return std.fmt.parseUnsigned(u64, trimmed[1..], 8) catch error.InvalidInteger;
    }

    return std.fmt.parseUnsigned(u64, trimmed, 10) catch error.InvalidInteger;
}

pub fn buildProcFdinfoPath(buffer: []u8, pid: i32, fd: i32) BridgeError![]u8 {
    if (pid < 0) return error.InvalidPid;
    if (fd < 0) return error.InvalidFd;

    return std.fmt.bufPrint(buffer, "/proc/{d}/fdinfo/{d}", .{ pid, fd }) catch |err| noSpaceToPathTooLong(err);
}

pub fn parseFdinfoLine(line: []const u8) BridgeError!ParsedFdinfoLine {
    const trimmed = std.mem.trim(u8, line, " \t\r\n");
    const separator_index = std.mem.indexOfScalar(u8, trimmed, ':') orelse return error.MissingSeparator;

    const field_name = std.mem.trim(u8, trimmed[0..separator_index], " \t");
    const field_value = std.mem.trim(u8, trimmed[separator_index + 1 ..], " \t");

    if (field_name.len == 0) return error.EmptyFieldName;
    if (field_value.len == 0) return error.EmptyFieldValue;

    return .{
        .field_name = field_name,
        .field_value = field_value,
    };
}

pub fn applyFdinfoMapInfoLine(info: *FdinfoMapInfo, line: []const u8) BridgeError!bool {
    const trimmed = std.mem.trim(u8, line, " \t\r\n");
    if (trimmed.len == 0) return false;

    const parsed = try parseFdinfoLine(trimmed);

    if (std.mem.eql(u8, parsed.field_name, "map_type")) {
        info.map_type = try parseAutoBaseU32(parsed.field_value);
        return true;
    }
    if (std.mem.eql(u8, parsed.field_name, "key_size")) {
        info.key_size = try parseAutoBaseU32(parsed.field_value);
        return true;
    }
    if (std.mem.eql(u8, parsed.field_name, "value_size")) {
        info.value_size = try parseAutoBaseU32(parsed.field_value);
        return true;
    }
    if (std.mem.eql(u8, parsed.field_name, "max_entries")) {
        info.max_entries = try parseAutoBaseU32(parsed.field_value);
        return true;
    }
    if (std.mem.eql(u8, parsed.field_name, "map_flags")) {
        info.map_flags = try parseAutoBaseU32(parsed.field_value);
        return true;
    }
    if (std.mem.eql(u8, parsed.field_name, "map_extra")) {
        info.map_extra = try parseAutoBaseU64(parsed.field_value);
        return true;
    }

    return false;
}

pub fn parseFdinfoMapInfo(text: []const u8) BridgeError!FdinfoMapInfo {
    var info = FdinfoMapInfo{};
    var lines = std.mem.splitScalar(u8, text, '\n');

    while (lines.next()) |line| {
        _ = try applyFdinfoMapInfoLine(&info, line);
    }

    return info;
}

pub fn summarizeFdinfoMapInfo(info: FdinfoMapInfo) FdinfoMapInfoSummary {
    var parsed_field_count: usize = 0;

    inline for (.{ info.map_type, info.key_size, info.value_size, info.max_entries, info.map_flags }) |field| {
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

pub fn mapReuseObservationFromFdinfo(name: []const u8, info: FdinfoMapInfo) ?MapReuseObservation {
    return .{
        .name = name,
        .map_type = info.map_type orelse return null,
        .key_size = info.key_size orelse return null,
        .value_size = info.value_size orelse return null,
        .max_entries = info.max_entries orelse return null,
        .map_flags = info.map_flags orelse return null,
        .map_extra = info.map_extra orelse 0,
    };
}

pub fn resolveReusedMapName(expected_name: []const u8, observed_name: []const u8) ReusedMapName {
    if (observed_name.len == bpf_obj_name_capacity_without_nul and
        expected_name.len >= observed_name.len and
        std.mem.eql(u8, expected_name[0..observed_name.len], observed_name))
    {
        return .{
            .source = .object_name,
            .value = expected_name,
        };
    }

    return .{
        .source = .kernel_name,
        .value = observed_name,
    };
}

pub fn normalizeObservedReuseMapFlags(expected_map_type: u32, observed_map_flags: u32) u32 {
    if (expected_map_type == bpf_map_type_devmap or expected_map_type == bpf_map_type_devmap_hash) {
        return observed_map_flags & ~bpf_f_rdonly_prog;
    }
    return observed_map_flags;
}

pub fn summarizeMapReuseCompatibility(
    expected: MapReuseExpectation,
    observed: MapReuseObservation,
) MapReuseCompatibilitySummary {
    const normalized_observed_map_flags = normalizeObservedReuseMapFlags(expected.map_type, observed.map_flags);

    if (observed.map_type != expected.map_type) {
        return .{
            .outcome = .map_type_mismatch,
            .normalized_observed_map_flags = normalized_observed_map_flags,
        };
    }
    if (observed.key_size != expected.key_size) {
        return .{
            .outcome = .key_size_mismatch,
            .normalized_observed_map_flags = normalized_observed_map_flags,
        };
    }
    if (observed.value_size != expected.value_size) {
        return .{
            .outcome = .value_size_mismatch,
            .normalized_observed_map_flags = normalized_observed_map_flags,
        };
    }
    if (observed.max_entries != expected.max_entries) {
        return .{
            .outcome = .max_entries_mismatch,
            .normalized_observed_map_flags = normalized_observed_map_flags,
        };
    }
    if (normalized_observed_map_flags != expected.map_flags) {
        return .{
            .outcome = .map_flags_mismatch,
            .normalized_observed_map_flags = normalized_observed_map_flags,
        };
    }
    if (observed.map_extra != expected.map_extra) {
        return .{
            .outcome = .map_extra_mismatch,
            .normalized_observed_map_flags = normalized_observed_map_flags,
        };
    }

    return .{
        .outcome = .compatible,
        .normalized_observed_map_flags = normalized_observed_map_flags,
    };
}

pub fn isMapReuseCompatible(expected: MapReuseExpectation, observed: MapReuseObservation) bool {
    return summarizeMapReuseCompatibility(expected, observed).outcome == .compatible;
}

pub fn resolveReusePinnedMapAttempt(
    pinned_path: ?[]const u8,
    expected: MapReuseExpectation,
    observed: ?MapReuseObservation,
) ReusePinnedMapAttemptPlan {
    const path = pinned_path orelse return .{
        .disposition = .missing_pinned_path,
        .should_attempt_reopen = false,
    };
    const trimmed_path = std.mem.trim(u8, path, " \t\r\n");
    if (trimmed_path.len == 0) {
        return .{
            .disposition = .missing_pinned_path,
            .should_attempt_reopen = false,
        };
    }

    const observed_map = observed orelse return .{
        .disposition = .missing_map_observation,
        .pinned_path = trimmed_path,
        .should_attempt_reopen = false,
    };

    const resolved_name = resolveReusedMapName(expected.name, observed_map.name);
    if (!std.mem.eql(u8, resolved_name.value, expected.name)) {
        return .{
            .disposition = .incompatible_name,
            .pinned_path = trimmed_path,
            .resolved_name = resolved_name,
            .should_attempt_reopen = false,
        };
    }

    const compatibility = summarizeMapReuseCompatibility(expected, observed_map);
    if (compatibility.outcome != .compatible) {
        return .{
            .disposition = .incompatible_map_definition,
            .pinned_path = trimmed_path,
            .resolved_name = resolved_name,
            .should_attempt_reopen = false,
            .compatibility = compatibility,
        };
    }

    return .{
        .disposition = .ready_for_reopen_attempt,
        .pinned_path = trimmed_path,
        .resolved_name = resolved_name,
        .should_attempt_reopen = true,
        .compatibility = compatibility,
    };
}

test "buildProcFdinfoPath keeps the bounded procfs pathname contract explicit" {
    var buffer: [64]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/proc/4321/fdinfo/17",
        try buildProcFdinfoPath(&buffer, 4321, 17),
    );
    try std.testing.expectError(error.InvalidPid, buildProcFdinfoPath(&buffer, -1, 17));
    try std.testing.expectError(error.InvalidFd, buildProcFdinfoPath(&buffer, 4321, -1));
}

test "buildProcFdinfoPath keeps overflow failures explicit" {
    var buffer: [12]u8 = undefined;

    try std.testing.expectError(
        error.PathTooLong,
        buildProcFdinfoPath(&buffer, 4321, 17),
    );
}

test "parseFdinfoLine trims libbpf style field names and values" {
    const parsed = try parseFdinfoLine(" key_size:\t64 \r");

    try std.testing.expectEqualStrings("key_size", parsed.field_name);
    try std.testing.expectEqualStrings("64", parsed.field_value);
}

test "parseFdinfoMapInfo keeps the legacy map info fields compact and ignores unrelated lines" {
    const parsed = try parseFdinfoMapInfo(
        \\pos: 0
        \\flags: 02000002
        \\mnt_id: 27
        \\map_type: 5
        \\key_size: 8
        \\value_size: 16
        \\max_entries: 1024
        \\map_flags: 0x20
    );

    try std.testing.expectEqual(@as(?u32, 5), parsed.map_type);
    try std.testing.expectEqual(@as(?u32, 8), parsed.key_size);
    try std.testing.expectEqual(@as(?u32, 16), parsed.value_size);
    try std.testing.expectEqual(@as(?u32, 1024), parsed.max_entries);
    try std.testing.expectEqual(@as(?u32, 0x20), parsed.map_flags);
    try std.testing.expectEqual(@as(?u64, null), parsed.map_extra);
}

test "applyFdinfoMapInfoLine keeps repeated fields last-write-wins and octal or decimal parsing explicit" {
    var info = FdinfoMapInfo{};

    try std.testing.expect(try applyFdinfoMapInfoLine(&info, "map_flags:\t010"));
    try std.testing.expect(try applyFdinfoMapInfoLine(&info, "map_flags:\t12"));
    try std.testing.expect(try applyFdinfoMapInfoLine(&info, "key_size:\t4"));
    try std.testing.expectEqual(@as(?u32, 12), info.map_flags);
    try std.testing.expectEqual(@as(?u32, 4), info.key_size);
}

test "fdinfo map info parsing keeps malformed lines and values explicit" {
    var info = FdinfoMapInfo{};

    try std.testing.expect(!try applyFdinfoMapInfoLine(&info, ""));
    try std.testing.expect(!try applyFdinfoMapInfoLine(&info, "ignored:\t17"));
    try std.testing.expectError(error.MissingSeparator, parseFdinfoLine("map_type"));
    try std.testing.expectError(error.EmptyFieldValue, parseFdinfoLine("map_type:\t"));
    try std.testing.expectError(error.InvalidInteger, applyFdinfoMapInfoLine(&info, "map_type:\tnope"));
    try std.testing.expectError(error.InvalidInteger, applyFdinfoMapInfoLine(&info, "map_flags:\t-1"));
    try std.testing.expectError(error.InvalidInteger, applyFdinfoMapInfoLine(&info, "map_extra:\tnope"));
}

test "parseFdinfoMapInfo keeps map_extra numeric parsing explicit" {
    const parsed = try parseFdinfoMapInfo(
        \\map_type: 14
        \\map_flags: 010
        \\map_extra: 0X2A
    );

    try std.testing.expectEqual(@as(?u32, 14), parsed.map_type);
    try std.testing.expectEqual(@as(?u32, 8), parsed.map_flags);
    try std.testing.expectEqual(@as(?u64, 42), parsed.map_extra);
}

test "summarizeFdinfoMapInfo keeps bounded completion state reviewable" {
    const partial = summarizeFdinfoMapInfo(.{
        .map_type = 5,
        .key_size = 8,
    });
    try std.testing.expectEqual(@as(usize, 2), partial.parsed_field_count);
    try std.testing.expect(!partial.has_complete_legacy_fields);
    try std.testing.expect(!partial.has_map_extra);

    const complete = summarizeFdinfoMapInfo(.{
        .map_type = 5,
        .key_size = 8,
        .value_size = 16,
        .max_entries = 1024,
        .map_flags = 0x20,
        .map_extra = 42,
    });
    try std.testing.expectEqual(@as(usize, 6), complete.parsed_field_count);
    try std.testing.expect(complete.has_complete_legacy_fields);
    try std.testing.expect(complete.has_map_extra);
}

test "mapReuseObservationFromFdinfo keeps the fdinfo bridge packet helper-only" {
    try std.testing.expectEqual(@as(?MapReuseObservation, null), mapReuseObservationFromFdinfo("stats", .{
        .map_type = 5,
        .key_size = 8,
    }));

    const observation = mapReuseObservationFromFdinfo("stats", .{
        .map_type = 5,
        .key_size = 8,
        .value_size = 16,
        .max_entries = 1024,
        .map_flags = 0x20,
        .map_extra = 42,
    }).?;
    try std.testing.expectEqualStrings("stats", observation.name);
    try std.testing.expectEqual(@as(u32, 5), observation.map_type);
    try std.testing.expectEqual(@as(u64, 42), observation.map_extra);
}

test "resolveReusedMapName keeps truncated kernel names tied to the object-side name" {
    const resolved = resolveReusedMapName("process_pinned_map", "process_pinned_");
    try std.testing.expectEqual(ReusedMapNameSource.object_name, resolved.source);
    try std.testing.expectEqualStrings("process_pinned_map", resolved.value);

    const exact = resolveReusedMapName("process_pinned_", "process_pinned_");
    try std.testing.expectEqual(ReusedMapNameSource.object_name, exact.source);
    try std.testing.expectEqualStrings("process_pinned_", exact.value);

    const unrelated = resolveReusedMapName("stats_map", "perf_map");
    try std.testing.expectEqual(ReusedMapNameSource.kernel_name, unrelated.source);
    try std.testing.expectEqualStrings("perf_map", unrelated.value);
}

test "normalizeObservedReuseMapFlags mirrors the devmap readonly-prog exception from libbpf.c" {
    try std.testing.expectEqual(
        @as(u32, 0x20),
        normalizeObservedReuseMapFlags(bpf_map_type_devmap, 0x20 | bpf_f_rdonly_prog),
    );
    try std.testing.expectEqual(
        @as(u32, 0x20),
        normalizeObservedReuseMapFlags(bpf_map_type_devmap_hash, 0x20 | bpf_f_rdonly_prog),
    );
    try std.testing.expectEqual(
        @as(u32, 0x20 | bpf_f_rdonly_prog),
        normalizeObservedReuseMapFlags(5, 0x20 | bpf_f_rdonly_prog),
    );
}

test "summarizeMapReuseCompatibility keeps the first bounded mismatch explicit" {
    const expected = MapReuseExpectation{
        .name = "stats_map",
        .map_type = bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 64,
        .map_flags = 0x20,
        .map_extra = 7,
    };

    const compatible = summarizeMapReuseCompatibility(expected, .{
        .name = "stats_map",
        .map_type = bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 64,
        .map_flags = 0x20 | bpf_f_rdonly_prog,
        .map_extra = 7,
    });
    try std.testing.expectEqual(MapReuseCompatibility.compatible, compatible.outcome);
    try std.testing.expectEqual(@as(u32, 0x20), compatible.normalized_observed_map_flags);

    try std.testing.expectEqual(MapReuseCompatibility.map_type_mismatch, summarizeMapReuseCompatibility(expected, .{
        .name = "stats_map",
        .map_type = 5,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 64,
        .map_flags = 0x20,
        .map_extra = 7,
    }).outcome);
    try std.testing.expectEqual(MapReuseCompatibility.key_size_mismatch, summarizeMapReuseCompatibility(expected, .{
        .name = "stats_map",
        .map_type = bpf_map_type_devmap,
        .key_size = 8,
        .value_size = 8,
        .max_entries = 64,
        .map_flags = 0x20 | bpf_f_rdonly_prog,
        .map_extra = 7,
    }).outcome);
    try std.testing.expectEqual(MapReuseCompatibility.value_size_mismatch, summarizeMapReuseCompatibility(expected, .{
        .name = "stats_map",
        .map_type = bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 4,
        .max_entries = 64,
        .map_flags = 0x20 | bpf_f_rdonly_prog,
        .map_extra = 7,
    }).outcome);
    try std.testing.expectEqual(MapReuseCompatibility.max_entries_mismatch, summarizeMapReuseCompatibility(expected, .{
        .name = "stats_map",
        .map_type = bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 32,
        .map_flags = 0x20 | bpf_f_rdonly_prog,
        .map_extra = 7,
    }).outcome);
    try std.testing.expectEqual(MapReuseCompatibility.map_flags_mismatch, summarizeMapReuseCompatibility(expected, .{
        .name = "stats_map",
        .map_type = bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 64,
        .map_flags = 0x40 | bpf_f_rdonly_prog,
        .map_extra = 7,
    }).outcome);
    try std.testing.expectEqual(MapReuseCompatibility.map_extra_mismatch, summarizeMapReuseCompatibility(expected, .{
        .name = "stats_map",
        .map_type = bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 64,
        .map_flags = 0x20 | bpf_f_rdonly_prog,
        .map_extra = 9,
    }).outcome);
}

test "isMapReuseCompatible keeps the bounded reused-map comparison explicit" {
    const expected = MapReuseExpectation{
        .name = "stats_map",
        .map_type = bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 64,
        .map_flags = 0x20,
        .map_extra = 7,
    };

    try std.testing.expect(isMapReuseCompatible(expected, .{
        .name = "stats_map",
        .map_type = bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 64,
        .map_flags = 0x20 | bpf_f_rdonly_prog,
        .map_extra = 7,
    }));
    try std.testing.expect(!isMapReuseCompatible(expected, .{
        .name = "stats_map",
        .map_type = bpf_map_type_devmap,
        .key_size = 8,
        .value_size = 8,
        .max_entries = 64,
        .map_flags = 0x20 | bpf_f_rdonly_prog,
        .map_extra = 7,
    }));
    try std.testing.expect(!isMapReuseCompatible(expected, .{
        .name = "stats_map",
        .map_type = bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 64,
        .map_flags = 0x20 | bpf_f_rdonly_prog,
        .map_extra = 9,
    }));
}

test "resolveReusePinnedMapAttempt keeps path presence and fdinfo reuse compatibility explicit" {
    const expected = MapReuseExpectation{
        .name = "process_pinned_map",
        .map_type = bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 64,
        .map_flags = 0x20,
        .map_extra = 7,
    };

    const missing_path = resolveReusePinnedMapAttempt(null, expected, null);
    try std.testing.expectEqual(
        ReusePinnedMapAttemptDisposition.missing_pinned_path,
        missing_path.disposition,
    );
    try std.testing.expect(!missing_path.should_attempt_reopen);
    try std.testing.expectEqual(@as(?MapReuseCompatibilitySummary, null), missing_path.compatibility);

    const blank_path = resolveReusePinnedMapAttempt(" \t\r\n ", expected, .{
        .name = "process_pinned_",
        .map_type = bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 64,
        .map_flags = 0x20 | bpf_f_rdonly_prog,
        .map_extra = 7,
    });
    try std.testing.expectEqual(
        ReusePinnedMapAttemptDisposition.missing_pinned_path,
        blank_path.disposition,
    );
    try std.testing.expectEqual(@as(?[]const u8, null), blank_path.pinned_path);
    try std.testing.expectEqual(@as(?ReusedMapName, null), blank_path.resolved_name);
    try std.testing.expect(!blank_path.should_attempt_reopen);
    try std.testing.expectEqual(@as(?MapReuseCompatibilitySummary, null), blank_path.compatibility);

    const missing_observation = resolveReusePinnedMapAttempt(" /sys/fs/bpf/stats ", expected, null);
    try std.testing.expectEqual(
        ReusePinnedMapAttemptDisposition.missing_map_observation,
        missing_observation.disposition,
    );
    try std.testing.expectEqualStrings("/sys/fs/bpf/stats", missing_observation.pinned_path.?);
    try std.testing.expect(!missing_observation.should_attempt_reopen);
    try std.testing.expectEqual(@as(?MapReuseCompatibilitySummary, null), missing_observation.compatibility);

    const incompatible_name = resolveReusePinnedMapAttempt("/sys/fs/bpf/stats", expected, .{
        .name = "perf_map",
        .map_type = bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 64,
        .map_flags = 0x20 | bpf_f_rdonly_prog,
        .map_extra = 7,
    });
    try std.testing.expectEqual(
        ReusePinnedMapAttemptDisposition.incompatible_name,
        incompatible_name.disposition,
    );
    try std.testing.expectEqual(ReusedMapNameSource.kernel_name, incompatible_name.resolved_name.?.source);
    try std.testing.expect(!incompatible_name.should_attempt_reopen);
    try std.testing.expectEqual(@as(?MapReuseCompatibilitySummary, null), incompatible_name.compatibility);

    const incompatible_definition = resolveReusePinnedMapAttempt("/sys/fs/bpf/stats", expected, .{
        .name = "process_pinned_",
        .map_type = bpf_map_type_devmap,
        .key_size = 8,
        .value_size = 8,
        .max_entries = 64,
        .map_flags = 0x20 | bpf_f_rdonly_prog,
        .map_extra = 7,
    });
    try std.testing.expectEqual(
        ReusePinnedMapAttemptDisposition.incompatible_map_definition,
        incompatible_definition.disposition,
    );
    try std.testing.expectEqual(ReusedMapNameSource.object_name, incompatible_definition.resolved_name.?.source);
    try std.testing.expectEqual(MapReuseCompatibility.key_size_mismatch, incompatible_definition.compatibility.?.outcome);
    try std.testing.expect(!incompatible_definition.should_attempt_reopen);

    const ready = resolveReusePinnedMapAttempt("/sys/fs/bpf/stats", expected, .{
        .name = "process_pinned_",
        .map_type = bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 64,
        .map_flags = 0x20 | bpf_f_rdonly_prog,
        .map_extra = 7,
    });
    try std.testing.expectEqual(
        ReusePinnedMapAttemptDisposition.ready_for_reopen_attempt,
        ready.disposition,
    );
    try std.testing.expectEqual(ReusedMapNameSource.object_name, ready.resolved_name.?.source);
    try std.testing.expectEqualStrings("process_pinned_map", ready.resolved_name.?.value);
    try std.testing.expectEqualStrings("/sys/fs/bpf/stats", ready.pinned_path.?);
    try std.testing.expectEqual(MapReuseCompatibility.compatible, ready.compatibility.?.outcome);
    try std.testing.expect(ready.should_attempt_reopen);
}

test "resolveReusePinnedMapAttempt keeps the readonly-prog normalization devmap-only" {
    const expected = MapReuseExpectation{
        .name = "stats_map",
        .map_type = 5,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 64,
        .map_flags = 0x20,
    };

    const incompatible_flags = resolveReusePinnedMapAttempt("/sys/fs/bpf/stats", expected, .{
        .name = "stats_map",
        .map_type = 5,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 64,
        .map_flags = 0x20 | bpf_f_rdonly_prog,
    });
    try std.testing.expectEqual(
        ReusePinnedMapAttemptDisposition.incompatible_map_definition,
        incompatible_flags.disposition,
    );
    try std.testing.expectEqual(ReusedMapNameSource.kernel_name, incompatible_flags.resolved_name.?.source);
    try std.testing.expectEqual(MapReuseCompatibility.map_flags_mismatch, incompatible_flags.compatibility.?.outcome);
    try std.testing.expectEqual(
        @as(u32, 0x20 | bpf_f_rdonly_prog),
        incompatible_flags.compatibility.?.normalized_observed_map_flags,
    );
    try std.testing.expect(!incompatible_flags.should_attempt_reopen);
}
