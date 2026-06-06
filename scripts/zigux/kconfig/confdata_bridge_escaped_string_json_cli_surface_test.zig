const std = @import("std");

test "confdata bridge escaped strings survive json cli surface" {
    const allocator = std.testing.allocator;

    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const config_path = try std.fmt.allocPrint(allocator, ".zig-cache/tmp/{s}/escaped_strings.config", .{tmp.sub_path});
    defer allocator.free(config_path);
    const exe_path = try std.fmt.allocPrint(allocator, ".zig-cache/tmp/{s}/confdata_bridge_escaped_string_json_cli", .{tmp.sub_path});
    defer allocator.free(exe_path);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "escaped_strings.config",
        .data =
        \\CONFIG_MESSAGE="zigux\"bridge\\"
        \\CONFIG_PATH="root\\subdir"
        \\# CONFIG_DEBUG is not set
        \\
        ,
    });

    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{exe_path});
    defer allocator.free(emit_arg);

    const build = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            "scripts/zigux/kconfig/confdata_bridge.zig",
            emit_arg,
        },
    });
    defer {
        allocator.free(build.stdout);
        allocator.free(build.stderr);
    }
    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, build.term);
    try std.testing.expectEqualStrings("", build.stderr);

    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{ exe_path, config_path },
    });
    defer {
        allocator.free(result.stdout);
        allocator.free(result.stderr);
    }

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"set\":2") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"unset\":1") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"name\":\"CONFIG_MESSAGE\",\"kind\":\"string\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"value\":\"zigux\\\"bridge\\\\\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"name\":\"CONFIG_PATH\",\"kind\":\"string\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"value\":\"root\\\\subdir\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "CONFIG_MESSAGE=\\\"") == null);
}
