const std = @import("std");

fn tmpBasePath(tmp: anytype) ![]u8 {
    return std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
}

test "fixdep reports a directory depfile read through the public entry path" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const base_path = try tmpBasePath(tmp);
    defer std.testing.allocator.free(base_path);

    try tmp.dir.createDir(std.testing.io, "directory-input.d", .default_dir);

    const cwd = try std.process.currentPathAlloc(std.testing.io, std.testing.allocator);
    defer std.testing.allocator.free(cwd);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/{s}/directory-input.d",
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
        "directory_depfile.o",
        "clang -c directory_depfile.c -o directory_depfile.o",
    };
    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = argv,
        .cwd = .{ .path = "../.." },
        .stdout_limit = .unlimited,
        .stderr_limit = .unlimited,
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 2 }, result.term);
    try std.testing.expectEqualStrings(
        "savedcmd_directory_depfile.o := clang -c directory_depfile.c -o directory_depfile.o\n\n",
        result.stdout,
    );
    try std.testing.expectEqualStrings("fixdep: read: Is a directory\n", result.stderr);
}
