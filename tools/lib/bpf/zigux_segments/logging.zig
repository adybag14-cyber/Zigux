const std = @import("std");

pub const libbpf_major_version: u32 = 1;
pub const libbpf_minor_version: u32 = 8;
pub const libbpf_log_level_env_var = "LIBBPF_LOG_LEVEL";

pub const PrintLevel = enum(u8) {
    warn = 0,
    info = 1,
    debug = 2,
};

pub const ResolvedMinLevel = struct {
    min_level: PrintLevel,
    invalid_value: ?[]const u8,
};

pub const LibbpfErrno = enum(i32) {
    libelf = 4000,
    format = 4001,
    kversion = 4002,
    endian = 4003,
    internal = 4004,
    reloc = 4005,
    load = 4006,
    verify = 4007,
    prog2big = 4008,
    kver = 4009,
    progtype = 4010,
    wrngpid = 4011,
    invseq = 4012,
    nlparse = 4013,
};

fn eqlIgnoreCase(lhs: []const u8, rhs: []const u8) bool {
    return std.ascii.eqlIgnoreCase(lhs, rhs);
}

pub fn parsePrintLevel(value: []const u8) ?PrintLevel {
    if (eqlIgnoreCase(value, "warn")) {
        return .warn;
    }
    if (eqlIgnoreCase(value, "info")) {
        return .info;
    }
    if (eqlIgnoreCase(value, "debug")) {
        return .debug;
    }
    return null;
}

pub fn resolveMinPrintLevel(env_value: ?[]const u8) ResolvedMinLevel {
    if (env_value) |value| {
        if (parsePrintLevel(value)) |level| {
            return .{
                .min_level = level,
                .invalid_value = null,
            };
        }
        return .{
            .min_level = .info,
            .invalid_value = value,
        };
    }
    return .{
        .min_level = .info,
        .invalid_value = null,
    };
}

pub fn shouldPrint(level: PrintLevel, min_level: PrintLevel) bool {
    return @intFromEnum(level) <= @intFromEnum(min_level);
}

pub fn libbpfMajorVersion() u32 {
    return libbpf_major_version;
}

pub fn libbpfMinorVersion() u32 {
    return libbpf_minor_version;
}

pub fn libbpfVersionString() []const u8 {
    return "v1.8";
}

pub fn libbpfCustomErrorMessage(err: i32) ?[]const u8 {
    const normalized = if (err < 0) -err else err;
    return switch (normalized) {
        @intFromEnum(LibbpfErrno.libelf) => "Something wrong in libelf",
        @intFromEnum(LibbpfErrno.format) => "BPF object format invalid",
        @intFromEnum(LibbpfErrno.kversion) => "'version' section incorrect or lost",
        @intFromEnum(LibbpfErrno.endian) => "Endian mismatch",
        @intFromEnum(LibbpfErrno.internal) => "Internal error in libbpf",
        @intFromEnum(LibbpfErrno.reloc) => "Relocation failed",
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

pub fn formatErrorString(buffer: []u8, err: i32) ![]const u8 {
    if (libbpfCustomErrorMessage(err)) |message| {
        return std.fmt.bufPrint(buffer, "{s}", .{message});
    }

    const normalized = if (err < 0) -err else err;
    return std.fmt.bufPrint(buffer, "Unknown libbpf error {d}", .{normalized});
}

pub fn formatInvalidLogLevelWarning(
    buffer: []u8,
    env_var: []const u8,
    value: []const u8,
) ![]const u8 {
    return std.fmt.bufPrint(
        buffer,
        "libbpf: unrecognized '{s}' envvar value: '{s}', should be one of 'warn', 'debug', or 'info'.\n",
        .{ env_var, value },
    );
}

pub fn formatDefaultInvalidLogLevelWarning(buffer: []u8, value: []const u8) ![]const u8 {
    return formatInvalidLogLevelWarning(buffer, libbpf_log_level_env_var, value);
}

test "resolveMinPrintLevel preserves warn info and debug case-insensitively" {
    try std.testing.expectEqual(.warn, resolveMinPrintLevel("warn").min_level);
    try std.testing.expectEqual(.info, resolveMinPrintLevel("INFO").min_level);
    try std.testing.expectEqual(.debug, resolveMinPrintLevel("Debug").min_level);
}

test "resolveMinPrintLevel keeps invalid values explicit while defaulting to info" {
    const missing = resolveMinPrintLevel(null);
    try std.testing.expectEqual(.info, missing.min_level);
    try std.testing.expectEqual(@as(?[]const u8, null), missing.invalid_value);

    const invalid = resolveMinPrintLevel("trace");
    try std.testing.expectEqual(.info, invalid.min_level);
    try std.testing.expectEqualStrings("trace", invalid.invalid_value.?);
}

test "shouldPrint matches libbpf verbosity ordering" {
    try std.testing.expect(shouldPrint(.warn, .warn));
    try std.testing.expect(shouldPrint(.warn, .info));
    try std.testing.expect(shouldPrint(.info, .info));
    try std.testing.expect(shouldPrint(.debug, .debug));
    try std.testing.expect(!shouldPrint(.info, .warn));
    try std.testing.expect(!shouldPrint(.debug, .info));
}

test "version helpers report the current libbpf version tuple" {
    try std.testing.expectEqual(@as(u32, 1), libbpfMajorVersion());
    try std.testing.expectEqual(@as(u32, 8), libbpfMinorVersion());
    try std.testing.expectEqualStrings("v1.8", libbpfVersionString());
}

test "custom libbpf errors resolve through the bounded helper table" {
    try std.testing.expectEqualStrings("Something wrong in libelf", libbpfCustomErrorMessage(4000).?);
    try std.testing.expectEqualStrings("Relocation failed", libbpfCustomErrorMessage(-4005).?);
    try std.testing.expectEqualStrings("Incorrect netlink message parsing", libbpfCustomErrorMessage(4013).?);
    try std.testing.expectEqual(@as(?[]const u8, null), libbpfCustomErrorMessage(@intFromEnum(LibbpfErrno.load)));
}

test "formatErrorString falls back cleanly for unmapped custom errors" {
    var buffer: [64]u8 = undefined;

    try std.testing.expectEqualStrings(
        "Internal error in libbpf",
        try formatErrorString(&buffer, -4004),
    );
    try std.testing.expectEqualStrings(
        "Unknown libbpf error 4006",
        try formatErrorString(&buffer, 4006),
    );
    try std.testing.expectEqualStrings(
        "Unknown libbpf error 4999",
        try formatErrorString(&buffer, -4999),
    );
}

test "formatInvalidLogLevelWarning matches libbpf's explicit invalid envvar guidance" {
    var buffer: [128]u8 = undefined;

    try std.testing.expectEqualStrings(
        "libbpf: unrecognized 'LIBBPF_LOG_LEVEL' envvar value: 'trace', should be one of 'warn', 'debug', or 'info'.\n",
        try formatDefaultInvalidLogLevelWarning(&buffer, "trace"),
    );
    try std.testing.expectEqualStrings(
        "libbpf: unrecognized 'CUSTOM_LOG_LEVEL' envvar value: 'verbose', should be one of 'warn', 'debug', or 'info'.\n",
        try formatInvalidLogLevelWarning(&buffer, "CUSTOM_LOG_LEVEL", "verbose"),
    );
}

test "formatInvalidLogLevelWarning keeps buffer exhaustion explicit" {
    var short_buffer: [32]u8 = undefined;

    try std.testing.expectError(
        error.NoSpaceLeft,
        formatDefaultInvalidLogLevelWarning(&short_buffer, "trace"),
    );
}
