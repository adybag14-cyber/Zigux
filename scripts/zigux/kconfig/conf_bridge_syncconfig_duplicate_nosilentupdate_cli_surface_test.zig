const std = @import("std");

const conf_bridge_source = "scripts/zigux/kconfig/conf_bridge.zig";

fn buildConfBridge(allocator: std.mem.Allocator, temp_path: []const u8) ![]const u8 {
    const exe_path = try std.fs.path.join(allocator, &.{ temp_path, "conf_bridge_test" });
    errdefer allocator.free(exe_path);

    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{exe_path});
    defer allocator.free(emit_arg);

    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            conf_bridge_source,
            emit_arg,
        },
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    switch (result.term) {
        .exited => |code| try std.testing.expectEqual(@as(u8, 0), code),
        else => return error.UnexpectedChildExit,
    }
    try std.testing.expectEqualStrings("", result.stderr);
    return exe_path;
}

test "syncconfig duplicate nosilentupdate is rejected at CLI boundary" {
    const allocator = std.testing.allocator;

    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const tmp_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
    defer allocator.free(tmp_path);

    const exe_path = try buildConfBridge(allocator, tmp_path);
    defer allocator.free(exe_path);

    const duplicate = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            exe_path,
            "syncconfig",
            "Kconfig",
            "out/.config",
            "riscv64",
            "nosilentupdate=1",
            "nosilentupdate=0",
        },
    });
    defer allocator.free(duplicate.stdout);
    defer allocator.free(duplicate.stderr);

    switch (duplicate.term) {
        .exited => |code| try std.testing.expectEqual(@as(u8, 1), code),
        else => return error.UnexpectedChildExit,
    }
    try std.testing.expectEqualStrings("", duplicate.stdout);
    try std.testing.expectEqualStrings(
        "Error: duplicate syncconfig nosilentupdate option\n",
        duplicate.stderr,
    );

    const duplicate_empty = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            exe_path,
            "syncconfig",
            "Kconfig",
            "out/.config",
            "riscv64",
            "nosilentupdate=",
            "nosilentupdate=1",
        },
    });
    defer allocator.free(duplicate_empty.stdout);
    defer allocator.free(duplicate_empty.stderr);

    switch (duplicate_empty.term) {
        .exited => |code| try std.testing.expectEqual(@as(u8, 1), code),
        else => return error.UnexpectedChildExit,
    }
    try std.testing.expectEqualStrings("", duplicate_empty.stdout);
    try std.testing.expectEqualStrings(
        "Error: duplicate syncconfig nosilentupdate option\n",
        duplicate_empty.stderr,
    );
}
