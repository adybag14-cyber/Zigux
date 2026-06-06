const std = @import("std");

const confdata_bridge_source = "confdata_bridge.zig";
const confdata_bridge_exe = "confdata_bridge_uppercase_tristate_test_bin";
const uppercase_config = "confdata_bridge_uppercase_tristate.config";

fn cleanupLocalArtifacts() void {
    const cwd = std.Io.Dir.cwd();
    cwd.deleteFile(std.testing.io, confdata_bridge_exe) catch {};
    cwd.deleteFile(std.testing.io, uppercase_config) catch {};
}

fn buildConfdataBridgeExecutable(allocator: std.mem.Allocator) !void {
    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{confdata_bridge_exe});
    defer allocator.free(emit_arg);

    const build_result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            confdata_bridge_source,
            emit_arg,
        },
    });
    defer allocator.free(build_result.stdout);
    defer allocator.free(build_result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, build_result.term);
    try std.testing.expectEqualStrings("", build_result.stderr);
}

fn runConfdataBridge(allocator: std.mem.Allocator, config_path: []const u8) !std.process.RunResult {
    return std.process.run(allocator, std.testing.io, .{
        .argv = &.{ "./" ++ confdata_bridge_exe, config_path },
    });
}

test "confdata bridge JSON CLI canonicalizes uppercase tristate assignments" {
    cleanupLocalArtifacts();
    defer cleanupLocalArtifacts();

    const allocator = std.testing.allocator;
    try buildConfdataBridgeExecutable(allocator);

    try std.Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = uppercase_config,
        .data =
        \\CONFIG_ALPHA=Y
        \\CONFIG_BETA=M
        \\CONFIG_GAMMA=N
        \\CONFIG_WORD=YES
        \\# CONFIG_DEBUG is not set
        \\
        ,
    });

    const result = try runConfdataBridge(allocator, uppercase_config);
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"counts\":{\"set\":4,\"unset\":1}") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"name\":\"CONFIG_BETA\",\"kind\":\"tristate\",\"value\":\"m\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"name\":\"CONFIG_GAMMA\",\"kind\":\"tristate\",\"value\":\"n\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"name\":\"CONFIG_WORD\",\"kind\":\"value\",\"value\":\"YES\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"value\":\"Y\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"value\":\"M\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"value\":\"N\"") == null);
}
