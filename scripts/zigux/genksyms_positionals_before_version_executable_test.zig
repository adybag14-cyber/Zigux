const std = @import("std");
const testing = std.testing;

const version_line = "genksyms version 2.5.60\n";

fn buildGenksymsExecutable(exe_path: []const u8) !void {
    const emit_arg = try std.fmt.allocPrint(testing.allocator, "-femit-bin={s}", .{exe_path});
    defer testing.allocator.free(emit_arg);

    const build_result = try std.process.run(testing.allocator, testing.io, .{
        .argv = &.{ "zig", "build-exe", "scripts/zigux/genksyms.zig", emit_arg },
        .stdout_limit = .limited(4096),
        .stderr_limit = .limited(4096),
    });
    defer testing.allocator.free(build_result.stdout);
    defer testing.allocator.free(build_result.stderr);

    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, build_result.term);
    try testing.expectEqualStrings("", build_result.stdout);
    try testing.expectEqualStrings("", build_result.stderr);
}

test "delayed positionals keep later version flags as request side effects at executable boundary" {
    var tmp = testing.tmpDir(.{});
    defer tmp.cleanup();

    const exe_path = try std.fmt.allocPrint(
        testing.allocator,
        ".zig-cache/tmp/{s}/genksyms-positionals-before-version",
        .{tmp.sub_path},
    );
    defer testing.allocator.free(exe_path);

    try buildGenksymsExecutable(exe_path);

    const run_result = try std.process.run(testing.allocator, testing.io, .{
        .argv = &.{
            exe_path,
            "alpha.c",
            "--version",
            "beta.c",
            "-V",
            "--debug",
        },
        .stdout_limit = .limited(16 * 1024),
        .stderr_limit = .limited(16 * 1024),
    });
    defer testing.allocator.free(run_result.stdout);
    defer testing.allocator.free(run_result.stderr);

    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, run_result.term);
    try testing.expectEqualStrings(version_line ++ version_line, run_result.stderr);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--version\",\"-V\",\"--debug\",\"alpha.c\",\"beta.c\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":null}}\n",
        run_result.stdout,
    );
}
