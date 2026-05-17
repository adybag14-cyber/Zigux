const std = @import("std");
const logging = @import("logging");

test "phase 8 logging helper keeps bounded log-level parsing and warning text explicit" {
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

    var buffer: [128]u8 = undefined;
    try std.testing.expectEqualStrings(
        "libbpf: unrecognized 'LIBBPF_LOG_LEVEL' envvar value: 'chatty', should be one of 'warn', 'debug', or 'info'.\n",
        try logging.formatUnrecognizedLogLevel(buffer[0..], "chatty"),
    );
}

test "phase 8 logging helper keeps bounded version and errno formatting reviewable" {
    var version_buffer: [16]u8 = undefined;
    try std.testing.expectEqual(@as(u32, 1), logging.libbpfMajorVersion());
    try std.testing.expectEqual(@as(u32, 7), logging.libbpfMinorVersion());
    try std.testing.expectEqualStrings("v1.7", try logging.libbpfVersionString(version_buffer[0..]));

    try std.testing.expectEqualStrings(
        "Something wrong in libelf",
        logging.libbpfErrorMessage(@intFromEnum(logging.LibbpfErrno.libelf)).?,
    );
    try std.testing.expectEqualStrings(
        "Load program failure for unknown reason",
        logging.libbpfErrorMessage(@intFromEnum(logging.LibbpfErrno.load)).?,
    );
    try std.testing.expectEqualStrings(
        "Incorrect netlink message parsing",
        logging.libbpfErrorMessage(-@intFromEnum(logging.LibbpfErrno.nlparse)).?,
    );
    try std.testing.expect(logging.libbpfErrorMessage(4999) == null);

    var error_buffer: [40]u8 = undefined;
    try std.testing.expectEqualStrings(
        "Unknown libbpf error 4999",
        try logging.formatLibbpfError(error_buffer[0..], -4999),
    );
    try std.testing.expect(logging.libbpfErrorMessage(std.math.minInt(i32)) == null);
    try std.testing.expectEqualStrings(
        "Unknown libbpf error 2147483648",
        try logging.formatLibbpfError(error_buffer[0..], std.math.minInt(i32)),
    );
}
