const std = @import("std");
const testing = std.testing;

fn expectExitedZero(term: std.process.Child.Term) !void {
    switch (term) {
        .exited => |code| try testing.expectEqual(@as(u8, 0), code),
        else => return error.UnexpectedProcessTermination,
    }
}

test "genksyms executable keeps repeated version side effects before request output" {
    const allocator = testing.allocator;

    const binary_path = ".zig-cache/lane23-repeated-version-request/genksyms";
    const build_args = [_][]const u8{
        "zig",
        "build-exe",
        "scripts/zigux/genksyms.zig",
        "-femit-bin=" ++ binary_path,
        "--cache-dir",
        ".zig-cache/lane23-repeated-version-request/build",
        "--global-cache-dir",
        ".zig-cache/lane23-repeated-version-request/global",
    };
    const build = try std.process.run(allocator, testing.io, .{
        .argv = &build_args,
        .stderr_limit = .limited(16 * 1024),
        .stdout_limit = .limited(16 * 1024),
    });
    defer allocator.free(build.stdout);
    defer allocator.free(build.stderr);
    try expectExitedZero(build.term);
    try testing.expectEqualStrings("", build.stdout);
    try testing.expectEqualStrings("", build.stderr);

    const run_args = [_][]const u8{
        binary_path,
        "-V",
        "--ver",
        "-d",
        "--reference",
        "alpha.symref",
        "--dump-types=types.symtypes",
        "unit.c",
    };
    const run = try std.process.run(allocator, testing.io, .{
        .argv = &run_args,
        .stderr_limit = .limited(16 * 1024),
        .stdout_limit = .limited(16 * 1024),
    });
    defer allocator.free(run.stdout);
    defer allocator.free(run.stderr);

    try expectExitedZero(run.term);
    try testing.expectEqualStrings(
        "genksyms version 2.5.60\n" ++
            "genksyms version 2.5.60\n",
        run.stderr,
    );
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-V\",\"--ver\",\"-d\",\"--reference\",\"alpha.symref\",\"--dump-types=types.symtypes\",\"unit.c\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"alpha.symref\"],\"dump_types_file\":\"types.symtypes\"}}\n",
        run.stdout,
    );
}
