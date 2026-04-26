const std = @import("std");
const logging = @import("logging");

test "phase 8 logging segment imports cleanly" {
    _ = logging;
}

test "phase 8 logging segment keeps libbpf log-level parsing bounded and explicit" {
    const warn_level = logging.resolveMinPrintLevel("warn");
    try std.testing.expectEqual(logging.PrintLevel.warn, warn_level.min_level);
    try std.testing.expectEqual(@as(?[]const u8, null), warn_level.invalid_value);
    try std.testing.expect(logging.shouldPrint(.warn, warn_level.min_level));
    try std.testing.expect(!logging.shouldPrint(.info, warn_level.min_level));

    const invalid_level = logging.resolveMinPrintLevel("trace");
    try std.testing.expectEqual(logging.PrintLevel.info, invalid_level.min_level);
    try std.testing.expectEqualStrings("trace", invalid_level.invalid_value.?);
}

test "phase 8 logging segment reports the bounded libbpf version helpers" {
    try std.testing.expectEqual(@as(u32, 1), logging.libbpfMajorVersion());
    try std.testing.expectEqual(@as(u32, 8), logging.libbpfMinorVersion());
    try std.testing.expectEqualStrings("v1.8", logging.libbpfVersionString());
}

test "phase 8 logging segment keeps libbpf-specific error text stable" {
    var buffer: [64]u8 = undefined;

    try std.testing.expectEqualStrings(
        "Kernel verifier blocks program loading",
        logging.libbpfCustomErrorMessage(4007).?,
    );
    try std.testing.expectEqualStrings(
        "Unknown libbpf error 4006",
        try logging.formatErrorString(&buffer, 4006),
    );
}
