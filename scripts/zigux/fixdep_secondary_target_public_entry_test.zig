const std = @import("std");

fn expectExit(term: std.process.Child.Term, expected_code: u8) !void {
    switch (term) {
        .exited => |code| try std.testing.expectEqual(expected_code, code),
        else => return error.UnexpectedChildTermination,
    }
}

test "fixdep public entry preserves later dependencies after a secondary target" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const depfile_name = "secondary_target.d";
    const target_name = "sample.o";
    const secondary_target_name = "module/sample.o";
    const first_source_name = "primary.c";
    const first_dep_name = "primary.rmeta";
    const secondary_source_name = "secondary.rmeta";
    const secondary_dep_name = "secondary.h";

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = first_source_name,
        .data = "int primary = CONFIG_ZIGUX_PRIMARY_SOURCE;\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = first_dep_name,
        .data = "",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = secondary_source_name,
        .data = "",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = secondary_dep_name,
        .data = "#define enabled CONFIG_ZIGUX_SECONDARY_DEP\n",
    });

    const depfile_path = try std.fs.path.join(std.testing.allocator, &.{
        ".zig-cache",
        "tmp",
        tmp.sub_path[0..],
        depfile_name,
    });
    defer std.testing.allocator.free(depfile_path);
    const first_source_path = try std.fs.path.join(std.testing.allocator, &.{
        ".zig-cache",
        "tmp",
        tmp.sub_path[0..],
        first_source_name,
    });
    defer std.testing.allocator.free(first_source_path);
    const first_dep_path = try std.fs.path.join(std.testing.allocator, &.{
        ".zig-cache",
        "tmp",
        tmp.sub_path[0..],
        first_dep_name,
    });
    defer std.testing.allocator.free(first_dep_path);
    const secondary_source_path = try std.fs.path.join(std.testing.allocator, &.{
        ".zig-cache",
        "tmp",
        tmp.sub_path[0..],
        secondary_source_name,
    });
    defer std.testing.allocator.free(secondary_source_path);
    const secondary_dep_path = try std.fs.path.join(std.testing.allocator, &.{
        ".zig-cache",
        "tmp",
        tmp.sub_path[0..],
        secondary_dep_name,
    });
    defer std.testing.allocator.free(secondary_dep_path);

    const depfile_data = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}: {s} {s}\n{s}: {s} {s}\n",
        .{
            target_name,
            first_source_path,
            first_dep_path,
            secondary_target_name,
            secondary_source_path,
            secondary_dep_path,
        },
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
            "cc -MMD -MF secondary_target.d -c primary.c",
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
        "savedcmd_{s} := cc -MMD -MF secondary_target.d -c primary.c\n\n" ++
            "source_{s} := {s}\n\n" ++
            "deps_{s} := \\\n" ++
            "    $(wildcard include/config/ZIGUX_PRIMARY_SOURCE) \\\n" ++
            "  {s} \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_SECONDARY_DEP) \\\n" ++
            "\n" ++
            "{s}: $(deps_{s})\n\n" ++
            "$(deps_{s}):\n",
        .{
            target_name,
            target_name,
            first_source_path,
            target_name,
            first_dep_path,
            secondary_dep_path,
            target_name,
            target_name,
            target_name,
        },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, result.stdout);
}
