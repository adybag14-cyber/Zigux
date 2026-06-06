const std = @import("std");

const confdata_bridge_source = "confdata_bridge.zig";
const confdata_bridge_exe = "confdata_bridge_final_cr_test_bin";
const newline_config = "confdata_bridge_final_cr_with_newline.config";
const final_cr_config = "confdata_bridge_final_cr_without_newline.config";

fn cleanupLocalArtifacts() void {
    const cwd = std.Io.Dir.cwd();
    cwd.deleteFile(std.testing.io, confdata_bridge_exe) catch {};
    cwd.deleteFile(std.testing.io, newline_config) catch {};
    cwd.deleteFile(std.testing.io, final_cr_config) catch {};
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

test "confdata bridge JSON CLI preserves final unterminated carriage return boundary" {
    cleanupLocalArtifacts();
    defer cleanupLocalArtifacts();

    const allocator = std.testing.allocator;
    try buildConfdataBridgeExecutable(allocator);

    const cwd = std.Io.Dir.cwd();
    try cwd.writeFile(std.testing.io, .{
        .sub_path = newline_config,
        .data = "CONFIG_ALPHA=value\r\nCONFIG_BETA=y\n",
    });
    try cwd.writeFile(std.testing.io, .{
        .sub_path = final_cr_config,
        .data = "CONFIG_ALPHA=value\r",
    });

    const newline_result = try runConfdataBridge(allocator, newline_config);
    defer allocator.free(newline_result.stdout);
    defer allocator.free(newline_result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, newline_result.term);
    try std.testing.expectEqualStrings("", newline_result.stderr);
    try std.testing.expect(std.mem.indexOf(u8, newline_result.stdout, "\"name\":\"CONFIG_ALPHA\",\"kind\":\"value\",\"value\":\"value\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, newline_result.stdout, "\"name\":\"CONFIG_BETA\",\"kind\":\"tristate\",\"value\":\"y\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, newline_result.stdout, "value\\r") == null);

    const final_cr_result = try runConfdataBridge(allocator, final_cr_config);
    defer allocator.free(final_cr_result.stdout);
    defer allocator.free(final_cr_result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, final_cr_result.term);
    try std.testing.expectEqualStrings("", final_cr_result.stderr);
    try std.testing.expect(std.mem.indexOf(u8, final_cr_result.stdout, "\"counts\":{\"set\":1,\"unset\":0}") != null);
    try std.testing.expect(std.mem.indexOf(u8, final_cr_result.stdout, "\"name\":\"CONFIG_ALPHA\",\"kind\":\"value\",\"value\":\"value\\r\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, final_cr_result.stdout, "\"name\":\"CONFIG_BETA\"") == null);
}
