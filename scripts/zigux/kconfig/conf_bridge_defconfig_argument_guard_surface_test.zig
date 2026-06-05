const std = @import("std");

const missing_defconfig_path = "Error: defconfig mode requires <defconfig>\n";

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
}

test "defconfig rejects missing and option-shaped mode arguments before emitting json" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const binary_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/conf_bridge_defconfig_arg_guard",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(binary_path);

    try buildConfBridge(binary_path);

    try expectExit(try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{ binary_path, "defconfig", "Kconfig", ".config", "x86_64" },
        .stdout_limit = .limited(1024),
        .stderr_limit = .limited(1024),
    }), missing_defconfig_path);

    const option_shaped_paths = [_][]const u8{
        "silent",
        "allconfig=mini.config",
        "seed=0xC0FFEE",
        "probability=15:25",
        "nosilentupdate=1",
    };

    for (option_shaped_paths) |arg| {
        try expectExit(try std.process.run(std.testing.allocator, std.testing.io, .{
            .argv = &.{ binary_path, "defconfig", "Kconfig", ".config", "x86_64", arg },
            .stdout_limit = .limited(1024),
            .stderr_limit = .limited(1024),
        }), missing_defconfig_path);
    }
}
