const std = @import("std");

const logging = @import("logging.zig");

test "phase8 logging helper entrypoints stay explicit" {
    try std.testing.expect(@hasDecl(logging, "parseLogLevelSetting"));
    try std.testing.expect(@hasDecl(logging, "shouldLog"));
    try std.testing.expect(@hasDecl(logging, "shouldLogWithEnv"));
    try std.testing.expect(@hasDecl(logging, "formatUnrecognizedLogLevel"));
    try std.testing.expect(@hasDecl(logging, "libbpfMajorVersion"));
    try std.testing.expect(@hasDecl(logging, "libbpfMinorVersion"));
    try std.testing.expect(@hasDecl(logging, "libbpfVersionString"));
    try std.testing.expect(@hasDecl(logging, "libbpfErrorCode"));
    try std.testing.expect(@hasDecl(logging, "libbpfErrorMessage"));
    try std.testing.expect(@hasDecl(logging, "formatLibbpfError"));
}

test "phase8 logging helpers keep parsed env and gate outputs stable" {
    try std.testing.expectEqualDeep(
        logging.ParsedLogLevel{ .min_level = .warn, .recognized = true },
        logging.parseLogLevelSetting("warn"),
    );
    try std.testing.expectEqualDeep(
        logging.ParsedLogLevel{ .min_level = .debug, .recognized = true },
        logging.parseLogLevelSetting("DEBUG"),
    );
    try std.testing.expectEqualDeep(
        logging.ParsedLogLevel{ .min_level = .info, .recognized = true },
        logging.parseLogLevelSetting(null),
    );
    try std.testing.expectEqualDeep(
        logging.ParsedLogLevel{ .min_level = .info, .recognized = false },
        logging.parseLogLevelSetting("chatty"),
    );

    try std.testing.expect(logging.shouldLog(.warn, .info));
    try std.testing.expect(logging.shouldLog(.info, .info));
    try std.testing.expect(!logging.shouldLog(.debug, .info));
    try std.testing.expect(logging.shouldLogWithEnv(.debug, "debug"));
    try std.testing.expect(!logging.shouldLogWithEnv(.debug, "warn"));
}

test "phase8 logging helpers keep version and error text outputs stable" {
    var version_buffer: [16]u8 = undefined;
    var warning_buffer: [128]u8 = undefined;
    var error_buffer: [40]u8 = undefined;

    try std.testing.expectEqual(@as(u32, 1), logging.libbpfMajorVersion());
    try std.testing.expectEqual(@as(u32, 7), logging.libbpfMinorVersion());
    try std.testing.expectEqualStrings("v1.7", try logging.libbpfVersionString(version_buffer[0..]));
    try std.testing.expectEqualStrings(
        "libbpf: unrecognized 'LIBBPF_LOG_LEVEL' envvar value: 'chatty', should be one of 'warn', 'debug', or 'info'.\n",
        try logging.formatUnrecognizedLogLevel(warning_buffer[0..], "chatty"),
    );

    try std.testing.expectEqual(
        @as(u32, @intFromEnum(logging.LibbpfErrno.load)),
        logging.libbpfErrorCode(-@intFromEnum(logging.LibbpfErrno.load)),
    );
    try std.testing.expectEqualStrings(
        "Kernel verifier blocks program loading",
        logging.libbpfErrorMessage(@intFromEnum(logging.LibbpfErrno.verify)).?,
    );
    try std.testing.expect(logging.libbpfErrorMessage(4999) == null);
    try std.testing.expectEqualStrings(
        "Unknown libbpf error 4999",
        try logging.formatLibbpfError(error_buffer[0..], -4999),
    );
    try std.testing.expectEqual(
        @as(u32, 2147483648),
        logging.libbpfErrorCode(std.math.minInt(i32)),
    );
}