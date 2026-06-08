const std = @import("std");

const unexpected_option = "Error: unexpected bridge option for mode\n";

const Case = struct {
    name: []const u8,
    argv: []const []const u8,
};

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

fn expectUnexpectedOption(case: Case) !void {
    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = case.argv,
        .stdout_limit = .limited(1024),
        .stderr_limit = .limited(1024),
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    errdefer std.debug.print("case failed: {s}\n", .{case.name});
    try std.testing.expectEqual(std.process.Child.Term{ .exited = 1 }, result.term);
    try std.testing.expectEqualStrings("", result.stdout);
    try std.testing.expectEqualStrings(unexpected_option, result.stderr);
}

test "conf bridge CLI rejects bridge options that belong to other modes" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const binary_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/conf_bridge_wrong_mode_options",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(binary_path);

    try buildConfBridge(binary_path);

    const allconfig_on_oldconfig = [_][]const u8{ binary_path, "oldconfig", "Kconfig", ".config", "x86_64", "allconfig=all.config" };
    const seed_on_syncconfig = [_][]const u8{ binary_path, "syncconfig", "Kconfig", ".config", "x86_64", "seed=123" };
    const probability_on_allmodconfig = [_][]const u8{ binary_path, "allmodconfig", "Kconfig", ".config", "x86_64", "probability=50" };
    const nosilentupdate_on_randconfig = [_][]const u8{ binary_path, "randconfig", "Kconfig", ".config", "x86_64", "nosilentupdate=1" };

    const cases = [_]Case{
        .{ .name = "allconfig rejected for oldconfig", .argv = &allconfig_on_oldconfig },
        .{ .name = "seed rejected for syncconfig", .argv = &seed_on_syncconfig },
        .{ .name = "probability rejected for allmodconfig", .argv = &probability_on_allmodconfig },
        .{ .name = "nosilentupdate rejected for randconfig", .argv = &nosilentupdate_on_randconfig },
    };

    for (cases) |case| {
        try expectUnexpectedOption(case);
    }
}
