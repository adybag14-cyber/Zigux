const std = @import("std");

const unexpected_bridge_option = "Error: unexpected bridge option for mode\n";

fn expectExit(result: std.process.RunResult, expected_stderr: []const u8) !void {
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 1 }, result.term);
    try std.testing.expectEqualStrings("", result.stdout);
    try std.testing.expectEqualStrings(expected_stderr, result.stderr);
}

fn expectSuccess(result: std.process.RunResult, expected_stdout_fragments: []const []const u8) !void {
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
    for (expected_stdout_fragments) |fragment| {
        try std.testing.expect(std.mem.indexOf(u8, result.stdout, fragment) != null);
    }
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

test "conf bridge CLI rejects mode-specific options for rewrite modes" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const binary_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/conf_bridge_rewrite_mode_options",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(binary_path);

    try buildConfBridge(binary_path);

    try expectExit(try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{ binary_path, "yes2modconfig", "Kconfig", "rewrite/.config", "x86_64", "allconfig=mini.config" },
        .stdout_limit = .limited(1024),
        .stderr_limit = .limited(1024),
    }), unexpected_bridge_option);

    try expectExit(try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{ binary_path, "mod2yesconfig", "Kconfig", "promote/.config", "x86_64", "seed=0xC0FFEE" },
        .stdout_limit = .limited(1024),
        .stderr_limit = .limited(1024),
    }), unexpected_bridge_option);

    try expectExit(try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{ binary_path, "mod2noconfig", "Kconfig", "demote/.config", "x86_64", "nosilentupdate=1" },
        .stdout_limit = .limited(1024),
        .stderr_limit = .limited(1024),
    }), unexpected_bridge_option);

    try expectSuccess(try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{ binary_path, "yes2modconfig", "Kconfig", "rewrite/.config", "x86_64", "silent" },
        .stdout_limit = .limited(2048),
        .stderr_limit = .limited(1024),
    }), &.{
        "\"mode\":\"yes2modconfig\"",
        "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--yes2modconfig\",\"Kconfig\"]",
        "\"KCONFIG_CONFIG\":\"rewrite/.config\"",
    });
}
