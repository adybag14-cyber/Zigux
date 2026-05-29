const std = @import("std");

fn expectExit(term: std.process.Child.Term, expected_code: u8) !void {
    switch (term) {
        .exited => |code| try std.testing.expectEqual(expected_code, code),
        else => return error.UnexpectedChildTermination,
    }
}

test "fixdep public entry emits source-only dependency body" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const source_name = "source_only.c";
    const depfile_name = "source_only.d";
    const target_name = "source-only.o";

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = source_name,
        .data = "int enabled = CONFIG_ZIGUX_SOURCE_ONLY;\n",
    });
    const depfile_path = try std.fs.path.join(std.testing.allocator, &.{
        ".zig-cache",
        "tmp",
        tmp.sub_path[0..],
        depfile_name,
    });
    defer std.testing.allocator.free(depfile_path);

    const source_path = try std.fs.path.join(std.testing.allocator, &.{
        ".zig-cache",
        "tmp",
        tmp.sub_path[0..],
        source_name,
    });
    defer std.testing.allocator.free(source_path);

    const depfile_data = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}: {s}\n",
        .{ target_name, source_path },
    );
    defer std.testing.allocator.free(depfile_data);
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = depfile_name,
        .data = depfile_data,
    });

    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "run",
            "fixdep.zig",
            "--",
            depfile_path,
            target_name,
            "cc -MMD -MF source_only.d -c source_only.c",
        },
        .stdout_limit = .limited(4096),
        .stderr_limit = .limited(4096),
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try expectExit(result.term, 0);
    try std.testing.expectEqualStrings("", result.stderr);

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_{s} := cc -MMD -MF source_only.d -c source_only.c\n\n" ++
            "source_{s} := {s}\n\n" ++
            "deps_{s} := \\\n" ++
            "    $(wildcard include/config/ZIGUX_SOURCE_ONLY) \\\n" ++
            "\n" ++
            "{s}: $(deps_{s})\n\n" ++
            "$(deps_{s}):\n",
        .{ target_name, target_name, source_path, target_name, target_name, target_name, target_name },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, result.stdout);
}
