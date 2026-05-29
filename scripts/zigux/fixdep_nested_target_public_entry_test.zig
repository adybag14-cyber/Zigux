const std = @import("std");

fn tmpBasePath(tmp: anytype) ![]u8 {
    return std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
}

test "fixdep preserves nested target paths through the public entry path" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "nested-target.d",
        .data = "drivers/zigux/nested.o: source.rmeta retained.rmeta\n",
    });

    const base_path = try tmpBasePath(tmp);
    defer std.testing.allocator.free(base_path);

    const cwd = try std.process.currentPathAlloc(std.testing.io, std.testing.allocator);
    defer std.testing.allocator.free(cwd);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/{s}/nested-target.d",
        .{ cwd, base_path },
    );
    defer std.testing.allocator.free(depfile_path);

    const target = "drivers/zigux/nested.o";
    const cmdline = "zig cc -MMD -MF nested-target.d -c drivers/zigux/nested.c";
    const argv: []const []const u8 = &.{
        "/usr/bin/env",
        "zig",
        "run",
        "scripts/zigux/fixdep.zig",
        "--",
        depfile_path,
        target,
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
        "savedcmd_{s} := {s}\n" ++
            "\n" ++
            "source_{s} := source.rmeta\n" ++
            "\n" ++
            "deps_{s} := {s}\n" ++
            "  retained.rmeta {s}\n" ++
            "\n" ++
            "{s}: $(deps_{s})\n" ++
            "\n" ++
            "$(deps_{s}):\n",
        .{ target, cmdline, target, target, slash, slash, target, target, target },
    );
    defer std.testing.allocator.free(expected_stdout);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings(expected_stdout, result.stdout);
    try std.testing.expectEqualStrings("", result.stderr);
}
