const std = @import("std");

const testing = std.testing;

fn genksymsSourcePath() []const u8 {
    std.Io.Dir.cwd().access(testing.io, "scripts/zigux/genksyms.zig", .{}) catch {
        return "genksyms.zig";
    };
    return "scripts/zigux/genksyms.zig";
}

fn buildGenksymsExecutable(allocator: std.mem.Allocator) ![]const u8 {
    const cache_dir = ".zig-cache/lane23-delayed-positionals-executable";
    try std.Io.Dir.cwd().createDirPath(testing.io, cache_dir);
    try std.Io.Dir.cwd().createDirPath(testing.io, cache_dir ++ "/global");

    const exe_path = cache_dir ++ "/genksyms-delayed-positionals";
    const build_result = try std.process.run(allocator, testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            genksymsSourcePath(),
            "-femit-bin=" ++ exe_path,
            "--cache-dir",
            cache_dir,
            "--global-cache-dir",
            cache_dir ++ "/global",
        },
    });
    defer allocator.free(build_result.stdout);
    defer allocator.free(build_result.stderr);

    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, build_result.term);
    try testing.expectEqualStrings("", build_result.stdout);
    try testing.expectEqualStrings("", build_result.stderr);
    return exe_path;
}

test "genksyms executable preserves delayed positionals before later request options" {
    const allocator = testing.allocator;
    const exe_path = try buildGenksymsExecutable(allocator);

    const run_result = try std.process.run(allocator, testing.io, .{
        .argv = &.{
            exe_path,
            "alpha.c",
            "--version",
            "beta.c",
            "-V",
            "--debug",
            "-w",
            "--reference",
            "ref.symref",
            "-Ttypes.symtypes",
        },
    });
    defer allocator.free(run_result.stdout);
    defer allocator.free(run_result.stderr);

    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, run_result.term);
    try testing.expectEqualStrings(
        "genksyms version 2.5.60\n" ++
            "genksyms version 2.5.60\n",
        run_result.stderr,
    );
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--version\",\"-V\",\"--debug\",\"-w\",\"--reference\",\"ref.symref\",\"-Ttypes.symtypes\",\"alpha.c\",\"beta.c\"],\"options\":{\"debug_level\":1,\"warnings\":true,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"ref.symref\"],\"dump_types_file\":\"types.symtypes\"}}\n",
        run_result.stdout,
    );
}
