const std = @import("std");

const testing = std.testing;

fn expectExited(term: std.process.Child.Term, expected_code: u8) !void {
    switch (term) {
        .exited => |code| try testing.expectEqual(expected_code, code),
        else => return error.ExpectedProcessExit,
    }
}

test "inline required values stay data while delayed positionals normalize at executable boundary" {
    var tmp = testing.tmpDir(.{});
    defer tmp.cleanup();

    var exe_path_buffer: [256]u8 = undefined;
    const exe_path = try std.fmt.bufPrint(
        &exe_path_buffer,
        ".zig-cache/tmp/{s}/genksyms-inline-required-positionals",
        .{tmp.sub_path},
    );
    const emit_arg = try std.fmt.allocPrint(testing.allocator, "-femit-bin={s}", .{exe_path});
    defer testing.allocator.free(emit_arg);

    const build_result = try std.process.run(testing.allocator, testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            "scripts/zigux/genksyms.zig",
            emit_arg,
        },
        .stdout_limit = .limited(4096),
        .stderr_limit = .limited(4096),
    });
    defer testing.allocator.free(build_result.stdout);
    defer testing.allocator.free(build_result.stderr);

    try expectExited(build_result.term, 0);
    try testing.expectEqualStrings("", build_result.stdout);
    try testing.expectEqualStrings("", build_result.stderr);

    const run_result = try std.process.run(testing.allocator, testing.io, .{
        .argv = &.{
            exe_path,
            "alpha.c",
            "--reference=--debug",
            "--dump-types=--types",
            "-V",
            "--warnings",
            "beta.c",
            "-d",
        },
        .stdout_limit = .limited(16 * 1024),
        .stderr_limit = .limited(16 * 1024),
    });
    defer testing.allocator.free(run_result.stdout);
    defer testing.allocator.free(run_result.stderr);

    try expectExited(run_result.term, 0);
    try testing.expectEqualStrings("genksyms version 2.5.60\n", run_result.stderr);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference=--debug\",\"--dump-types=--types\",\"-V\",\"--warnings\",\"-d\",\"alpha.c\",\"beta.c\"],\"options\":{\"debug_level\":1,\"warnings\":true,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"--debug\"],\"dump_types_file\":\"--types\"}}\n",
        run_result.stdout,
    );
}
