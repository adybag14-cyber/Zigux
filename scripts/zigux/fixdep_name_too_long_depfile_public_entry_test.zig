const std = @import("std");

fn tmpBasePath(tmp: anytype) ![]u8 {
    return std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
}

test "fixdep reports a too-long depfile path through the public entry path" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const base_path = try tmpBasePath(tmp);
    defer std.testing.allocator.free(base_path);

    var too_long_component: [300]u8 = undefined;
    @memset(&too_long_component, 'a');

    const cwd = try std.process.currentPathAlloc(std.testing.io, std.testing.allocator);
    defer std.testing.allocator.free(cwd);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/{s}/{s}.d",
        .{ cwd, base_path, too_long_component[0..] },
    );
    defer std.testing.allocator.free(depfile_path);

    const argv: []const []const u8 = &.{
        "/usr/bin/env",
        "zig",
        "run",
        "scripts/zigux/fixdep.zig",
        "--",
        depfile_path,
        "nametoolong_depfile.o",
        "clang -c nametoolong_depfile.c -o nametoolong_depfile.o",
    };
    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = argv,
        .cwd = .{ .path = "../.." },
        .stdout_limit = .unlimited,
        .stderr_limit = .unlimited,
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    const expected_stderr = try std.fmt.allocPrint(
        std.testing.allocator,
        "fixdep: error opening file: {s}: File name too long\n",
        .{depfile_path},
    );
    defer std.testing.allocator.free(expected_stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 2 }, result.term);
    try std.testing.expectEqualStrings(
        "savedcmd_nametoolong_depfile.o := clang -c nametoolong_depfile.c -o nametoolong_depfile.o\n\n",
        result.stdout,
    );
    try std.testing.expectEqualStrings(expected_stderr, result.stderr);
}
