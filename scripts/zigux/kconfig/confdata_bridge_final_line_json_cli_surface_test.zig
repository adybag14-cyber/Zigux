const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "confdata bridge JSON CLI preserves final unterminated config lines" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const bridge_bin = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/confdata_bridge_final_line",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(bridge_bin);

    const emit_bin_arg = try std.fmt.allocPrint(
        std.testing.allocator,
        "-femit-bin={s}",
        .{bridge_bin},
    );
    defer std.testing.allocator.free(emit_bin_arg);

    const build_result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            "scripts/zigux/kconfig/confdata_bridge.zig",
            emit_bin_arg,
            "--cache-dir",
            ".zig-cache/confdata-final-line-build",
            "--global-cache-dir",
            ".zig-cache/confdata-final-line-build/global",
        },
    });
    defer std.testing.allocator.free(build_result.stdout);
    defer std.testing.allocator.free(build_result.stderr);
    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, build_result.term);
    try std.testing.expectEqualStrings("", build_result.stderr);

    const config_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/final-line.config",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(config_path);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "final-line.config",
        .data = "CONFIG_FIRST=y\n" ++
            "CONFIG_FINAL_VALUE=last-line\r\n" ++
            "# CONFIG_FINAL_UNSET is not set",
    });

    const run_result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{ bridge_bin, config_path },
    });
    defer std.testing.allocator.free(run_result.stdout);
    defer std.testing.allocator.free(run_result.stderr);
    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, run_result.term);
    try std.testing.expectEqualStrings("", run_result.stderr);

    try expectContains(run_result.stdout, "\"set\":2");
    try expectContains(run_result.stdout, "\"unset\":1");
    try expectContains(run_result.stdout, "\"name\":\"CONFIG_FINAL_VALUE\",\"kind\":\"value\",\"value\":\"last-line\"");
    try expectContains(run_result.stdout, "\"name\":\"CONFIG_FINAL_UNSET\",\"kind\":\"unset\",\"value\":\"n\"");
    try expectNotContains(run_result.stdout, "last-line\\r");
    try std.testing.expect(std.mem.endsWith(u8, run_result.stdout, "\n"));
}
