const std = @import("std");

const unexpected_option = "Error: unexpected bridge option for mode\n";

fn expectWrongModeOption(result: std.process.RunResult) !void {
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 1 }, result.term);
    try std.testing.expectEqualStrings("", result.stdout);
    try std.testing.expectEqualStrings(unexpected_option, result.stderr);
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

test "conf bridge CLI rejects mode specific options on the wrong mode" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const binary_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/conf_bridge_wrong_mode_options",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(binary_path);

    try buildConfBridge(binary_path);

    const cases = [_][]const []const u8{
        &.{ binary_path, "oldconfig", "Kconfig", ".config", "x86_64", "seed=1" },
        &.{ binary_path, "oldconfig", "Kconfig", ".config", "x86_64", "probability=10" },
        &.{ binary_path, "oldconfig", "Kconfig", ".config", "x86_64", "nosilentupdate=1" },
        &.{ binary_path, "syncconfig", "Kconfig", ".config", "x86_64", "allconfig=mini.config" },
        &.{ binary_path, "syncconfig", "Kconfig", ".config", "x86_64", "seed=0xC0FFEE" },
        &.{ binary_path, "randconfig", "Kconfig", ".config", "x86_64", "nosilentupdate=1" },
    };

    for (cases) |argv| {
        try expectWrongModeOption(try std.process.run(std.testing.allocator, std.testing.io, .{
            .argv = argv,
            .stdout_limit = .limited(1024),
            .stderr_limit = .limited(1024),
        }));
    }
}
