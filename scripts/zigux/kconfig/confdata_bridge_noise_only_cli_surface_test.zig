const std = @import("std");

fn expectExitedZero(result: std.process.RunResult) !void {
    switch (result.term) {
        .exited => |code| try std.testing.expectEqual(@as(u8, 0), code),
        else => return error.UnexpectedChildTermination,
    }
}

fn tempPath(allocator: std.mem.Allocator, tmp_sub_path: []const u8, name: []const u8) ![]u8 {
    return std.fmt.allocPrint(allocator, ".zig-cache/tmp/{s}/{s}", .{ tmp_sub_path, name });
}

test "confdata bridge CLI ignores blank and comment-only config noise" {
    const allocator = std.testing.allocator;

    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const config_path = try tempPath(allocator, tmp.sub_path[0..], "noise.config");
    defer allocator.free(config_path);
    const exe_path = try tempPath(allocator, tmp.sub_path[0..], "confdata_bridge_noise_cli");
    defer allocator.free(exe_path);

    const config_text =
        "\n" ++
        "   \t\n" ++
        "# ordinary comment text that must not become an unset symbol\n" ++
        "#CONFIG_NO_SPACE is not set\n" ++
        "# CONFIG_TRAILING is not set today\n" ++
        "CONFIG_ALPHA=y\n" ++
        "\n" ++
        "# CONFIG_DEBUG is not set\n" ++
        "# another plain comment\n" ++
        "CONFIG_NAME=\"zigux\"\n";
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "noise.config",
        .data = config_text,
    });

    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{exe_path});
    defer allocator.free(emit_arg);
    const build_result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            "scripts/zigux/kconfig/confdata_bridge.zig",
            emit_arg,
        },
    });
    defer allocator.free(build_result.stdout);
    defer allocator.free(build_result.stderr);
    try expectExitedZero(build_result);
    try std.testing.expectEqualStrings("", build_result.stderr);

    const run_result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{ exe_path, config_path },
    });
    defer allocator.free(run_result.stdout);
    defer allocator.free(run_result.stderr);
    try expectExitedZero(run_result);
    try std.testing.expectEqualStrings("", run_result.stderr);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"},{\"name\":\"CONFIG_NAME\",\"kind\":\"string\",\"value\":\"zigux\"}]}\n",
        run_result.stdout,
    );
}
