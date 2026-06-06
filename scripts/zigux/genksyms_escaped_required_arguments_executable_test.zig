const std = @import("std");
const testing = std.testing;

const zig_exe = "zig";
const wrapper_source = "scripts/zigux/genksyms.zig";

fn buildWrapper(allocator: std.mem.Allocator, tmp: testing.TmpDir) ![]u8 {
    const exe_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/genksyms-wrapper",
        .{tmp.sub_path},
    );
    errdefer allocator.free(exe_path);

    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{exe_path});
    defer allocator.free(emit_arg);

    const build_result = try std.process.run(allocator, testing.io, .{
        .argv = &.{
            zig_exe,
            "build-exe",
            wrapper_source,
            "-O",
            "Debug",
            emit_arg,
        },
        .stdout_limit = .limited(16 * 1024),
        .stderr_limit = .limited(16 * 1024),
    });
    defer allocator.free(build_result.stdout);
    defer allocator.free(build_result.stderr);

    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, build_result.term);
    try testing.expectEqualStrings("", build_result.stdout);
    try testing.expectEqualStrings("", build_result.stderr);

    return exe_path;
}

test "escaped required option values stay valid JSON at executable boundary" {
    const allocator = testing.allocator;
    var tmp = testing.tmpDir(.{});
    defer tmp.cleanup();

    const exe_path = try buildWrapper(allocator, tmp);
    defer allocator.free(exe_path);

    const run_result = try std.process.run(allocator, testing.io, .{
        .argv = &.{
            exe_path,
            "--reference=ref\"quote\\slash\tname\nline\rcr.sym",
            "-T",
            "types\t\"quoted\\path\r.out",
            "-w",
            "unit.c",
        },
        .stdout_limit = .limited(16 * 1024),
        .stderr_limit = .limited(16 * 1024),
    });
    defer allocator.free(run_result.stdout);
    defer allocator.free(run_result.stderr);

    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, run_result.term);
    try testing.expectEqualStrings("", run_result.stderr);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference=ref\\\"quote\\\\slash\\tname\\nline\\rcr.sym\",\"-T\",\"types\\t\\\"quoted\\\\path\\r.out\",\"-w\",\"unit.c\"],\"options\":{\"debug_level\":0,\"warnings\":true,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"ref\\\"quote\\\\slash\\tname\\nline\\rcr.sym\"],\"dump_types_file\":\"types\\t\\\"quoted\\\\path\\r.out\"}}\n",
        run_result.stdout,
    );
}
