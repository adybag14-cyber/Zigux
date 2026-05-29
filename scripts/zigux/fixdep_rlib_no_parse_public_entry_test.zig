const std = @import("std");

fn tmpBasePath(tmp: anytype) ![]u8 {
    return std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
}

test "fixdep lists rlib dependencies without parsing them through the public entry path" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "rlib-no-parse.d",
        .data = "rlib_no_parse.o: libzigux_source.rlib libzigux_dep.rlib\n",
    });

    const base_path = try tmpBasePath(tmp);
    defer std.testing.allocator.free(base_path);

    const cwd = try std.process.currentPathAlloc(std.testing.io, std.testing.allocator);
    defer std.testing.allocator.free(cwd);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/{s}/rlib-no-parse.d",
        .{ cwd, base_path },
    );
    defer std.testing.allocator.free(depfile_path);

    const argv: []const []const u8 = &.{
        "/usr/bin/env",
        "zig",
        "run",
        "scripts/zigux/fixdep.zig",
        "--",
        depfile_path,
        "rlib_no_parse.o",
        "rustc --emit=obj rlib_no_parse.rs -o rlib_no_parse.o",
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
    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings(
        "savedcmd_rlib_no_parse.o := rustc --emit=obj rlib_no_parse.rs -o rlib_no_parse.o\n" ++
            "\n" ++
            "source_rlib_no_parse.o := libzigux_source.rlib\n" ++
            "\n" ++
            "deps_rlib_no_parse.o := " ++ slash ++ "\n" ++
            "  libzigux_dep.rlib " ++ slash ++ "\n" ++
            "\n" ++
            "rlib_no_parse.o: $(deps_rlib_no_parse.o)\n" ++
            "\n" ++
            "$(deps_rlib_no_parse.o):\n",
        result.stdout,
    );
    try std.testing.expectEqualStrings("", result.stderr);
}
