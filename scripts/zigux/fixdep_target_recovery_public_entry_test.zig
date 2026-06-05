const std = @import("std");

test "public entry recovers after a target-only stanza" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "source.rmeta",
        .data = "",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "config.h",
        .data = "CONFIG_ZIGUX_TARGET_RECOVERY CONFIG_ZIGUX_TARGET_RECOVERY_MODULE\n",
    });

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/source.rmeta",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(source_path);

    const config_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/config.h",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(config_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/target-recovery.d",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(depfile_path);

    const depfile_body = try std.fmt.allocPrint(
        std.testing.allocator,
        "empty-target.o:\nreal-target.o: {s} {s}\n",
        .{ source_path, config_path },
    );
    defer std.testing.allocator.free(depfile_body);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "target-recovery.d",
        .data = depfile_body,
    });

    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "run",
            "scripts/zigux/fixdep.zig",
            "--",
            depfile_path,
            "target_recovery.o",
            "clang -c target_recovery.c -o target_recovery.o",
        },
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_target_recovery.o := clang -c target_recovery.c -o target_recovery.o\n\n" ++
            "source_target_recovery.o := {s}\n\n" ++
            "deps_target_recovery.o := \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_TARGET_RECOVERY) \\\n" ++
            "\n" ++
            "target_recovery.o: $(deps_target_recovery.o)\n\n" ++
            "$(deps_target_recovery.o):\n",
        .{ source_path, config_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, result.stdout);
}
