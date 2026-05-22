const std = @import("std");

fn tmpBasePath(tmp: anytype) ![]u8 {
    return std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
}

test "fixdep reports the C-style output-write failure on the public entry path" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const allocator = std.testing.allocator;
    const base_path = try tmpBasePath(tmp);
    defer allocator.free(base_path);

    const depfile_path = try std.fmt.allocPrint(allocator, "{s}/sample_output_write.d", .{base_path});
    defer allocator.free(depfile_path);
    const source_path = try std.fmt.allocPrint(allocator, "{s}/sample_output_write_source.c", .{base_path});
    defer allocator.free(source_path);
    const config_path = try std.fmt.allocPrint(allocator, "{s}/sample-output-write-config.h", .{base_path});
    defer allocator.free(config_path);

    const cmdline = try std.fmt.allocPrint(
        allocator,
        "clang -c {s} -o sample_output_write.o",
        .{source_path},
    );
    defer allocator.free(cmdline);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_output_write_source.c",
        .data = "/* sample output write path */\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample-output-write-config.h",
        .data = "#define CONFIG_ZIGUX_OUTPUT_WRITE 1\n#define CONFIG_ZIGUX_OUTPUT_WRITE_MODULE 1\n",
    });

    const depfile_text = try std.fmt.allocPrint(
        allocator,
        "sample_output_write.o: {s} {s}\n",
        .{ source_path, config_path },
    );
    defer allocator.free(depfile_text);
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_output_write.d",
        .data = depfile_text,
    });

    const argv: []const []const u8 = &.{
        "sh",
        "-c",
        "zig run fixdep.zig -- \"$1\" \"$2\" \"$3\" >/dev/full",
        "ignored",
        depfile_path,
        "sample_output_write.o",
        cmdline,
    };
    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = argv,
        .cwd = .{ .path = "." },
        .stdout_limit = .unlimited,
        .stderr_limit = .unlimited,
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 1 }, result.term);
    try std.testing.expectEqualStrings("", result.stdout);
    try std.testing.expectEqualStrings(
        "fixdep: not all data was written to the output\n",
        result.stderr,
    );
}
