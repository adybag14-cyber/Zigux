const std = @import("std");

pub const LibbpfLogLevel = enum(u8) {
    warn = 0,
    info = 1,
    debug = 2,
};

pub const ParsedLogLevel = struct {
    min_level: LibbpfLogLevel,
    recognized: bool,
};

pub const LibbpfVersion = struct {
    major: u32,
    minor: u32,

    pub fn writeString(self: LibbpfVersion, buffer: []u8) error{NoSpaceLeft}![]const u8 {
        return std.fmt.bufPrint(buffer, "v{d}.{d}", .{ self.major, self.minor });
    }
};

pub const current_version = LibbpfVersion{
    .major = 1,
    .minor = 7,
};

pub const libbpf_errno_start: i32 = 4000;

pub const LibbpfErrno = enum(i32) {
    libelf = libbpf_errno_start,
    format,
    kversion,
    endian,
    internal,
    reloc,
    load,
    verify,
    prog2big,
    kver,
    progtype,
    wrngpid,
    invseq,
    nlparse,
};

fn normalizeLibbpfErrno(err: i32) u32 {
    const widened: i64 = err;
    return @intCast(if (widened < 0) -widened else widened);
}

pub fn parseLogLevelSetting(value: ?[]const u8) ParsedLogLevel {
    if (value) |raw| {
        if (std.ascii.eqlIgnoreCase(raw, "warn")) {
            return .{ .min_level = .warn, .recognized = true };
        }
        if (std.ascii.eqlIgnoreCase(raw, "info")) {
            return .{ .min_level = .info, .recognized = true };
        }
        if (std.ascii.eqlIgnoreCase(raw, "debug")) {
            return .{ .min_level = .debug, .recognized = true };
        }

        return .{ .min_level = .info, .recognized = false };
    }

    return .{ .min_level = .info, .recognized = true };
}

pub fn shouldLog(level: LibbpfLogLevel, min_level: LibbpfLogLevel) bool {
    return @intFromEnum(level) <= @intFromEnum(min_level);
}

pub fn shouldLogWithEnv(level: LibbpfLogLevel, env_value: ?[]const u8) bool {
    return shouldLog(level, parseLogLevelSetting(env_value).min_level);
}

pub fn formatUnrecognizedLogLevel(buffer: []u8, value: []const u8) error{NoSpaceLeft}![]const u8 {
    return std.fmt.bufPrint(
        buffer,
        "libbpf: unrecognized 'LIBBPF_LOG_LEVEL' envvar value: '{s}', should be one of 'warn', 'debug', or 'info'.\n",
        .{value},
    );
}

pub fn libbpfMajorVersion() u32 {
    return current_version.major;
}

pub fn libbpfMinorVersion() u32 {
    return current_version.minor;
}

pub fn libbpfVersionString(buffer: []u8) error{NoSpaceLeft}![]const u8 {
    return current_version.writeString(buffer);
}

pub fn libbpfErrorCode(err: i32) u32 {
    return normalizeLibbpfErrno(err);
}

pub fn libbpfErrorMessage(err: i32) ?[]const u8 {
    const normalized = libbpfErrorCode(err);

    return switch (normalized) {
        @intFromEnum(LibbpfErrno.libelf) => "Something wrong in libelf",
        @intFromEnum(LibbpfErrno.format) => "BPF object format invalid",
        @intFromEnum(LibbpfErrno.kversion) => "'version' section incorrect or lost",
        @intFromEnum(LibbpfErrno.endian) => "Endian mismatch",
        @intFromEnum(LibbpfErrno.internal) => "Internal error in libbpf",
        @intFromEnum(LibbpfErrno.reloc) => "Relocation failed",
        @intFromEnum(LibbpfErrno.load) => "Load program failure for unknown reason",
        @intFromEnum(LibbpfErrno.verify) => "Kernel verifier blocks program loading",
        @intFromEnum(LibbpfErrno.prog2big) => "Program too big",
        @intFromEnum(LibbpfErrno.kver) => "Incorrect kernel version",
        @intFromEnum(LibbpfErrno.progtype) => "Kernel doesn't support this program type",
        @intFromEnum(LibbpfErrno.wrngpid) => "Wrong pid in netlink message",
        @intFromEnum(LibbpfErrno.invseq) => "Invalid netlink sequence",
        @intFromEnum(LibbpfErrno.nlparse) => "Incorrect netlink message parsing",
        else => null,
    };
}

pub fn formatLibbpfError(buffer: []u8, err: i32) error{NoSpaceLeft}![]const u8 {
    if (libbpfErrorMessage(err)) |message| {
        return std.fmt.bufPrint(buffer, "{s}", .{message});
    }

    return std.fmt.bufPrint(buffer, "Unknown libbpf error {d}", .{libbpfErrorCode(err)});
}

test "log level parsing matches the base libbpf env contract" {
    try std.testing.expectEqualDeep(
        ParsedLogLevel{ .min_level = .warn, .recognized = true },
        parseLogLevelSetting("warn"),
    );
    try std.testing.expectEqualDeep(
        ParsedLogLevel{ .min_level = .debug, .recognized = true },
        parseLogLevelSetting("DEBUG"),
    );
    try std.testing.expectEqualDeep(
        ParsedLogLevel{ .min_level = .info, .recognized = true },
        parseLogLevelSetting(null),
    );
    try std.testing.expectEqualDeep(
        ParsedLogLevel{ .min_level = .info, .recognized = false },
        parseLogLevelSetting("chatty"),
    );
}

test "log gating keeps warn and info visible at info default" {
    try std.testing.expect(shouldLog(.warn, .info));
    try std.testing.expect(shouldLog(.info, .info));
    try std.testing.expect(!shouldLog(.debug, .info));
    try std.testing.expect(shouldLogWithEnv(.debug, "debug"));
}

test "unrecognized log level warning mirrors libbpf wording" {
    var buffer: [128]u8 = undefined;
    const warning = try formatUnrecognizedLogLevel(buffer[0..], "chatty");

    try std.testing.expectEqualStrings(
        "libbpf: unrecognized 'LIBBPF_LOG_LEVEL' envvar value: 'chatty', should be one of 'warn', 'debug', or 'info'.\n",
        warning,
    );
}

test "version helpers format the bounded libbpf release string" {
    var buffer: [16]u8 = undefined;

    try std.testing.expectEqual(@as(u32, 1), libbpfMajorVersion());
    try std.testing.expectEqual(@as(u32, 7), libbpfMinorVersion());
    try std.testing.expectEqualStrings("v1.7", try libbpfVersionString(buffer[0..]));
}

test "error-code helper keeps normalized libbpf magnitudes stable" {
    try std.testing.expectEqual(@as(u32, @intFromEnum(LibbpfErrno.load)), libbpfErrorCode(@intFromEnum(LibbpfErrno.load)));
    try std.testing.expectEqual(@as(u32, @intFromEnum(LibbpfErrno.load)), libbpfErrorCode(-@intFromEnum(LibbpfErrno.load)));
    try std.testing.expectEqual(@as(u32, 4999), libbpfErrorCode(-4999));
    try std.testing.expectEqual(@as(u32, 2147483648), libbpfErrorCode(std.math.minInt(i32)));
}

test "error helpers cover the bounded libbpf internal errno range" {
    try std.testing.expectEqualStrings(
        "Something wrong in libelf",
        libbpfErrorMessage(@intFromEnum(LibbpfErrno.libelf)).?,
    );
    try std.testing.expectEqualStrings(
        "Load program failure for unknown reason",
        libbpfErrorMessage(@intFromEnum(LibbpfErrno.load)).?,
    );
    try std.testing.expectEqual(
        @as(u32, @intFromEnum(LibbpfErrno.nlparse)),
        libbpfErrorCode(-@intFromEnum(LibbpfErrno.nlparse)),
    );
    try std.testing.expectEqualStrings(
        "Incorrect netlink message parsing",
        libbpfErrorMessage(-@intFromEnum(LibbpfErrno.nlparse)).?,
    );
    try std.testing.expect(libbpfErrorMessage(4999) == null);
}

test "unknown errors stay reviewable instead of silently disappearing" {
    var buffer: [32]u8 = undefined;
    const message = try formatLibbpfError(buffer[0..], -4999);

    try std.testing.expectEqualStrings("Unknown libbpf error 4999", message);
}

test "error normalization stays defined for the i32 minimum edge" {
    var buffer: [40]u8 = undefined;

    try std.testing.expectEqual(@as(u32, 2147483648), libbpfErrorCode(std.math.minInt(i32)));
    try std.testing.expect(libbpfErrorMessage(std.math.minInt(i32)) == null);
    try std.testing.expectEqualStrings(
        "Unknown libbpf error 2147483648",
        try formatLibbpfError(buffer[0..], std.math.minInt(i32)),
    );
}
