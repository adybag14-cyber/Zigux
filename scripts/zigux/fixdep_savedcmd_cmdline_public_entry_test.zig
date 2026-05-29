const std = @import("std");

fn tmpBasePath(tmp: anytype) ![]u8 {
    return std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
}

test "fixdep preserves the command line verbatim through the public entry path" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "savedcmd.d",
        .data = "savedcmd.o: source.rmeta retained.rmeta\n",
    });

    const base_path = try tmpBasePath(tmp);
    defer std.testing.allocator.free(base_path);

    const cwd = try std.process.currentPathAlloc(std.testing.io, std.testing.allocator);
    defer std.testing.allocator.free(cwd);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/{s}/savedcmd.d",
        .{ cwd, base_path },
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = "zig cc -DNAME=\"two words\" -DCONFIG_ZIGUX_CMDLINE_SHOULD_STAY_TEXT source.c";
    const argv: []const []const u8 = &.{
        "/usr/bin/env",
        "zig",
        "run",
        "scripts/zigux/fixdep.zig",
        "--",
        depfile_path,
        "savedcmd.o",
        cmdline,
    };
    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = argv,
        .cwd = .{ .path = "../.." },
        .stdout_limit = .unlimited,
        .stderr_limit = .unlimited,
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    const slash = "\\";
    const expected_stdout = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_savedcmd.o := {s}\n" ++
            "\n" ++
            "source_savedcmd.o := source.rmeta\n" ++
            "\n" ++
            "deps_savedcmd.o := {s}\n" ++
            "  retained.rmeta {s}\n" ++
            "\n" ++
            "savedcmd.o: $(deps_savedcmd.o)\n" ++
            "\n" ++
            "$(deps_savedcmd.o):\n",
        .{ cmdline, slash, slash },
    );
    defer std.testing.allocator.free(expected_stdout);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings(expected_stdout, result.stdout);
    try std.testing.expectEqualStrings("", result.stderr);
}
