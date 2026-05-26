const std = @import("std");

test "fixdep accepts an exact-size depfile on the public entry path" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const base_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(base_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_exact_size.d",
        .{base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const target = "sample_exact_size.o";
    const cmdline = "clang -c sample_exact_size_source.rmeta -o sample_exact_size.o";
    const depfile_text = "sample_exact_size.o: sample_exact_size_source.rmeta\n";

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_exact_size.d",
        .data = depfile_text,
    });

    const argv: []const []const u8 = &.{
        "zig",
        "run",
        "fixdep.zig",
        "--",
        depfile_path,
        target,
        cmdline,
    };
    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = argv,
        .cwd = .{ .path = "." },
        .stdout_limit = .unlimited,
        .stderr_limit = .unlimited,
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings(
        "savedcmd_sample_exact_size.o := clang -c sample_exact_size_source.rmeta -o sample_exact_size.o\n\n" ++
            "source_sample_exact_size.o := sample_exact_size_source.rmeta\n\n" ++
            "deps_sample_exact_size.o := \\\n" ++
            "\n" ++
            "sample_exact_size.o: $(deps_sample_exact_size.o)\n\n" ++
            "$(deps_sample_exact_size.o):\n",
        result.stdout,
    );
    try std.testing.expectEqualStrings("", result.stderr);
}
