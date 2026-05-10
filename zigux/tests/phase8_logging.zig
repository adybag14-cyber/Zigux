const std = @import("std");
const logging = @import("logging");

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

test "phase 8 logging module imports cleanly" {
    _ = logging;
}

test "phase 8 logging slice note keeps the focused replay surface explicit" {
    const note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-logging-slice.md",
        16 * 1024,
    );
    defer std.testing.allocator.free(note);

    try expectContains(note, "tools/lib/bpf/zigux_segments/logging.zig");
    try expectContains(note, "zigux/tests/phase8_logging.zig");
    try expectContains(note, "zigux/tests/phase8_logging_only_build.zig");
    try expectContains(note, "zig build test --build-file zigux/tests/phase8_logging_only_build.zig --summary all");
}

test "phase 8 logging helper keeps invalid print-level values explicit" {
    const resolved = logging.resolveMinPrintLevel("trace");
    try std.testing.expectEqual(logging.PrintLevel.info, resolved.min_level);
    try std.testing.expectEqualStrings("trace", resolved.invalid_value.?);
}

test "phase 8 logging helper keeps custom and unknown libbpf error strings stable" {
    var buffer: [64]u8 = undefined;

    try std.testing.expectEqualStrings(
        "Something wrong in libelf",
        try logging.formatErrorString(&buffer, 4000),
    );
    try std.testing.expectEqualStrings(
        "Kernel verifier blocks program loading",
        try logging.formatErrorString(&buffer, -4007),
    );
    try std.testing.expectEqualStrings(
        "Unknown libbpf error 4999",
        try logging.formatErrorString(&buffer, 4999),
    );
}
