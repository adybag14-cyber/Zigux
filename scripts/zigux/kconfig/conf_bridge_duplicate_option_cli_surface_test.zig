const std = @import("std");

const duplicate_silent = "Error: duplicate silent option\n";
const duplicate_allconfig = "Error: duplicate allconfig override option\n";
const duplicate_seed = "Error: duplicate randconfig seed option\n";
const duplicate_probability = "Error: duplicate randconfig probability option\n";
const duplicate_nosilentupdate = "Error: duplicate syncconfig nosilentupdate option\n";

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

test "conf bridge CLI rejects duplicate bridge options before emitting json" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const binary_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/conf_bridge_duplicate_options",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(binary_path);

    try buildConfBridge(binary_path);

    try expectExit(try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{ binary_path, "olddefconfig", "Kconfig", ".config", "x86_64", "silent", "silent" },
        .stdout_limit = .limited(1024),
        .stderr_limit = .limited(1024),
    }), duplicate_silent);

    try expectExit(try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{ binary_path, "randconfig", "Kconfig", ".config", "x86_64", "allconfig=one", "allconfig=two" },
        .stdout_limit = .limited(1024),
        .stderr_limit = .limited(1024),
    }), duplicate_allconfig);

    try expectExit(try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{ binary_path, "randconfig", "Kconfig", ".config", "x86_64", "seed=1", "seed=2" },
        .stdout_limit = .limited(1024),
        .stderr_limit = .limited(1024),
    }), duplicate_seed);

    try expectExit(try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{ binary_path, "randconfig", "Kconfig", ".config", "x86_64", "probability=10", "probability=20" },
        .stdout_limit = .limited(1024),
        .stderr_limit = .limited(1024),
    }), duplicate_probability);

    try expectExit(try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{ binary_path, "syncconfig", "Kconfig", ".config", "x86_64", "nosilentupdate=1", "nosilentupdate=0" },
        .stdout_limit = .limited(1024),
        .stderr_limit = .limited(1024),
    }), duplicate_nosilentupdate);
}
