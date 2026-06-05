const std = @import("std");

const usage = "Usage: confdata_bridge [json|auto.conf|autoconf.h] <config>\n";

fn expectExit(result: std.process.RunResult, expected_stderr: []const u8) !void {
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 1 }, result.term);
    try std.testing.expectEqualStrings("", result.stdout);
    try std.testing.expectEqualStrings(expected_stderr, result.stderr);
}

fn expectSuccess(result: std.process.RunResult, expected_stdout: []const u8) !void {
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings(expected_stdout, result.stdout);
    try std.testing.expectEqualStrings("", result.stderr);
}

fn buildConfdataBridge(binary_path: []const u8) !void {
    const emit_arg = try std.fmt.allocPrint(std.testing.allocator, "-femit-bin={s}", .{binary_path});
    defer std.testing.allocator.free(emit_arg);

    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{ "zig", "build-exe", "scripts/zigux/kconfig/confdata_bridge.zig", emit_arg },
        .stdout_limit = .limited(8192),
        .stderr_limit = .limited(8192),
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
}

test "confdata bridge CLI rejects invalid output modes before reading config" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const binary_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/confdata_bridge_mode_guard",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(binary_path);

    try buildConfdataBridge(binary_path);

    try expectExit(try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{binary_path},
        .stdout_limit = .limited(1024),
        .stderr_limit = .limited(1024),
    }), usage);

    try expectExit(try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{ binary_path, "yaml", "missing.config" },
        .stdout_limit = .limited(1024),
        .stderr_limit = .limited(1024),
    }), usage);

    try expectExit(try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{ binary_path, "json", "missing.config", "extra" },
        .stdout_limit = .limited(1024),
        .stderr_limit = .limited(1024),
    }), usage);
}

test "confdata bridge CLI accepts explicit output modes with one config path" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample.config",
        .data =
        \\CONFIG_ALPHA=y
        \\CONFIG_BETA=m
        \\CONFIG_NAME="zigux"
        \\# CONFIG_DEBUG is not set
        \\
        ,
    });

    const binary_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/confdata_bridge_mode_guard",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(binary_path);

    const config_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/sample.config",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(config_path);

    try buildConfdataBridge(binary_path);

    try expectSuccess(try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{ binary_path, "auto.conf", config_path },
        .stdout_limit = .limited(1024),
        .stderr_limit = .limited(1024),
    }), "CONFIG_ALPHA=y\n" ++
        "CONFIG_BETA=m\n" ++
        "CONFIG_NAME=\"zigux\"\n");

    try expectSuccess(try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{ binary_path, "autoconf.h", config_path },
        .stdout_limit = .limited(1024),
        .stderr_limit = .limited(1024),
    }), "#define CONFIG_ALPHA 1\n" ++
        "#define CONFIG_BETA_MODULE 1\n" ++
        "#define CONFIG_NAME \"zigux\"\n");
}
