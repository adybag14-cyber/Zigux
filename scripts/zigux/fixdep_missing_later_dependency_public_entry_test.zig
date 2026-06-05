const std = @import("std");

test "missing later dependency preserves emitted public-entry prelude" {
    const allocator = std.testing.allocator;

    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();

    try temp_dir.dir.writeFile(std.testing.io, .{
        .sub_path = "present.h",
        .data = "CONFIG_LANE11_PRESENT CONFIG_LANE11_PRESENT_MODULE\n",
    });

    const present_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/present.h",
        .{temp_dir.sub_path},
    );
    defer allocator.free(present_path);

    const missing_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/missing.h",
        .{temp_dir.sub_path},
    );
    defer allocator.free(missing_path);

    const depfile_body = try std.fmt.allocPrint(
        allocator,
        "missing_later.o: {s} {s}\n",
        .{ present_path, missing_path },
    );
    defer allocator.free(depfile_body);

    try temp_dir.dir.writeFile(std.testing.io, .{
        .sub_path = "missing_later.d",
        .data = depfile_body,
    });

    const depfile_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/missing_later.d",
        .{temp_dir.sub_path},
    );
    defer allocator.free(depfile_path);

    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "/usr/bin/env",
            "zig",
            "run",
            "fixdep.zig",
            "--",
            depfile_path,
            "missing_later.o",
            "cc -c missing_later.c -o missing_later.o",
        },
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(
        std.process.Child.Term{ .exited = 2 },
        result.term,
    );

    const expected_stdout = try std.fmt.allocPrint(
        allocator,
        "savedcmd_missing_later.o := cc -c missing_later.c -o missing_later.o\n\n" ++
            "source_missing_later.o := {s}\n\n" ++
            "deps_missing_later.o := \\\n" ++
            "    $(wildcard include/config/LANE11_PRESENT) \\\n" ++
            "  {s} \\\n",
        .{ present_path, missing_path },
    );
    defer allocator.free(expected_stdout);

    const expected_stderr = try std.fmt.allocPrint(
        allocator,
        "fixdep: error opening file: {s}: No such file or directory\n",
        .{missing_path},
    );
    defer allocator.free(expected_stderr);

    try std.testing.expectEqualStrings(expected_stdout, result.stdout);
    try std.testing.expectEqualStrings(expected_stderr, result.stderr);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "LANE11_PRESENT_MODULE") == null);
}
