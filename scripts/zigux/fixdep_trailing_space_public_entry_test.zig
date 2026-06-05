const std = @import("std");

test "public entry ignores final-line trailing spaces after dependencies" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "source.c",
        .data = "CONFIG_ZIGUX_TRAILING_SOURCE\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "header.h",
        .data = "CONFIG_ZIGUX_TRAILING_HEADER_MODULE\n",
    });

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/source.c",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(source_path);

    const header_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/header.h",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(header_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/trailing-space.d",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(depfile_path);

    const depfile_body = try std.fmt.allocPrint(
        std.testing.allocator,
        "trailing_space.o: {s} {s}  \t  ",
        .{ source_path, header_path },
    );
    defer std.testing.allocator.free(depfile_body);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "trailing-space.d",
        .data = depfile_body,
    });

    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "run",
            "scripts/zigux/fixdep.zig",
            "--",
            depfile_path,
            "trailing_space.o",
            "clang -MD -MF trailing-space.d -c source.c",
        },
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_trailing_space.o := clang -MD -MF trailing-space.d -c source.c\n\n" ++
            "source_trailing_space.o := {s}\n\n" ++
            "deps_trailing_space.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_TRAILING_SOURCE) \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_TRAILING_HEADER) \\\n" ++
            "\n" ++
            "trailing_space.o: $(deps_trailing_space.o)\n\n" ++
            "$(deps_trailing_space.o):\n",
        .{ source_path, header_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, result.stdout);
}
