const std = @import("std");

const unsupported_mode_message = "Error: unsupported kconfig mode\n";

fn expectExit(result: std.process.RunResult, expected_stderr: []const u8) !void {
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 1 }, result.term);
    try std.testing.expectEqualStrings("", result.stdout);
    try std.testing.expectEqualStrings(expected_stderr, result.stderr);
}

fn buildConfBridge(binary_path: []const u8) !void {
    const emit_arg = try std.fmt.allocPrint(std.testing.allocator, "-femit-bin={s}", .{binary_path});
    defer std.testing.allocator.free(emit_arg);

    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{ "zig", "build-exe", "scripts/zigux/kconfig/conf_bridge.zig", emit_arg },
        .stdout_limit = .limited(8192),
        .stderr_limit = .limited(8192),
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
}

test "conf bridge CLI rejects unsupported modes before emitting json" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const binary_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/conf_bridge_unsupported_mode",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(binary_path);

    try buildConfBridge(binary_path);

    const unsupported_modes = [_][]const u8{
        "menuconfig",
        "nconfig",
        "--olddefconfig",
        "olddefconfig ",
        "",
    };

    for (unsupported_modes) |mode| {
        try expectExit(try std.process.run(std.testing.allocator, std.testing.io, .{
            .argv = &.{ binary_path, mode, "Kconfig", ".config", "x86_64" },
            .stdout_limit = .limited(1024),
            .stderr_limit = .limited(1024),
        }), unsupported_mode_message);
    }
}
