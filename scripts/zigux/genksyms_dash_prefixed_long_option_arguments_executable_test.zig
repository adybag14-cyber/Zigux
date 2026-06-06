const std = @import("std");

const testing = std.testing;

fn expectExitedZero(term: std.process.Child.Term) !void {
    switch (term) {
        .exited => |code| try testing.expectEqual(@as(u8, 0), code),
        else => return error.ExpectedExitedZero,
    }
}

test "genksyms executable keeps dash-prefixed long option arguments as data" {
    var tmp = testing.tmpDir(.{});
    defer tmp.cleanup();

    var exe_path_buffer: [256]u8 = undefined;
    const exe_path = try std.fmt.bufPrint(
        &exe_path_buffer,
        ".zig-cache/tmp/{s}/genksyms-dash-prefixed-long-args",
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

    try expectExitedZero(build_result.term);
    try testing.expectEqualStrings("", build_result.stdout);
    try testing.expectEqualStrings("", build_result.stderr);

    const run_result = try std.process.run(testing.allocator, testing.io, .{
        .argv = &.{
            exe_path,
            "--reference",
            "--debug",
            "--dump-types",
            "--types",
        },
        .stdout_limit = .limited(4096),
        .stderr_limit = .limited(4096),
    });
    defer testing.allocator.free(run_result.stdout);
    defer testing.allocator.free(run_result.stderr);

    try expectExitedZero(run_result.term);
    try testing.expectEqualStrings("", run_result.stderr);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference\",\"--debug\",\"--dump-types\",\"--types\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"--debug\"],\"dump_types_file\":\"--types\"}}\n",
        run_result.stdout,
    );
}
