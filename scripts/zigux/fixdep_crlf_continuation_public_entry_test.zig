const std = @import("std");

fn expectExit(term: std.process.Child.Term, expected_code: u8) !void {
    switch (term) {
        .exited => |code| try std.testing.expectEqual(expected_code, code),
        else => return error.UnexpectedChildTermination,
    }
}

test "fixdep public entry continues CRLF dependency lines" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const depfile_name = "crlf_continuation.d";
    const target_name = "sample.o";
    const source_name = "source.rmeta";
    const first_dep_name = "first.so";
    const second_dep_name = "second.h";

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = source_name,
        .data = "",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = second_dep_name,
        .data = "#define enabled CONFIG_ZIGUX_CRLF_CONTINUED\n",
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
    const first_dep_path = try std.fs.path.join(std.testing.allocator, &.{
        ".zig-cache",
        "tmp",
        tmp.sub_path[0..],
        first_dep_name,
    });
    defer std.testing.allocator.free(first_dep_path);
    const second_dep_path = try std.fs.path.join(std.testing.allocator, &.{
        ".zig-cache",
        "tmp",
        tmp.sub_path[0..],
        second_dep_name,
    });
    defer std.testing.allocator.free(second_dep_path);

    const depfile_data = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}: {s} {s} \\\r\n {s}\r\n",
        .{ target_name, source_path, first_dep_path, second_dep_path },
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
            "cc -MMD -MF crlf_continuation.d -c source.c",
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
        "savedcmd_{s} := cc -MMD -MF crlf_continuation.d -c source.c\n\n" ++
            "source_{s} := {s}\n\n" ++
            "deps_{s} := \\\n" ++
            "  {s} \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_CRLF_CONTINUED) \\\n" ++
            "\n" ++
            "{s}: $(deps_{s})\n\n" ++
            "$(deps_{s}):\n",
        .{
            target_name,
            target_name,
            source_path,
            target_name,
            first_dep_path,
            second_dep_path,
            target_name,
            target_name,
            target_name,
        },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, result.stdout);
}
