const std = @import("std");

const testing = std.testing;

fn expectExited(term: std.process.Child.Term, expected_code: u8) !void {
    switch (term) {
        .exited => |code| try testing.expectEqual(expected_code, code),
        else => return error.ExpectedProcessExit,
    }
}

test "genksyms executable reports reference limit without usage text" {
    var tmp = testing.tmpDir(.{});
    defer tmp.cleanup();

    var exe_path_buffer: [256]u8 = undefined;
    const exe_path = try std.fmt.bufPrint(
        &exe_path_buffer,
        ".zig-cache/tmp/{s}/genksyms-reference-limit",
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
            "-V",
            "-r",
            "01.symref",
            "-r",
            "02.symref",
            "-r",
            "03.symref",
            "-r",
            "04.symref",
            "-r",
            "05.symref",
            "-r",
            "06.symref",
            "-r",
            "07.symref",
            "-r",
            "08.symref",
            "-r",
            "09.symref",
            "-r",
            "10.symref",
            "-r",
            "11.symref",
            "-r",
            "12.symref",
            "-r",
            "13.symref",
            "-r",
            "14.symref",
            "-r",
            "15.symref",
            "-r",
            "16.symref",
            "-r",
            "17.symref",
        },
        .stdout_limit = .limited(4096),
        .stderr_limit = .limited(4096),
    });
    defer testing.allocator.free(run_result.stdout);
    defer testing.allocator.free(run_result.stderr);

    try expectExited(run_result.term, 1);
    try testing.expectEqualStrings("", run_result.stdout);
    try testing.expectEqualStrings(
        "genksyms version 2.5.60\n" ++
            "too many reference files\n",
        run_result.stderr,
    );
}
