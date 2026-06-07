const std = @import("std");

const testing = std.testing;

const zig_exe = "zig";
const genksyms_bin = ".zig-cache/lane23-warning-order/genksyms";
const version_text = "genksyms version 2.5.60\n";

fn expectExit(result: std.process.RunResult, code: u8) !void {
    switch (result.term) {
        .exited => |actual| try testing.expectEqual(code, actual),
        else => return error.ProcessDidNotExit,
    }
}

fn run(argv: []const []const u8) !std.process.RunResult {
    return std.process.run(testing.allocator, testing.io, .{
        .argv = argv,
        .reserve_amount = 4096,
    });
}

test "genksyms executable keeps final warning order after delayed positionals" {
    try std.Io.Dir.cwd().createDirPath(testing.io, ".zig-cache/lane23-warning-order");

    const build_result = try run(&.{
        zig_exe,
        "build-exe",
        "scripts/zigux/genksyms.zig",
        "-femit-bin=" ++ genksyms_bin,
        "--cache-dir",
        ".zig-cache/lane23-warning-order/build-cache",
        "--global-cache-dir",
        ".zig-cache/lane23-warning-order/global-cache",
    });
    defer testing.allocator.free(build_result.stdout);
    defer testing.allocator.free(build_result.stderr);
    try expectExit(build_result, 0);
    try testing.expectEqualStrings("", build_result.stderr);

    const genksyms_result = try run(&.{
        genksyms_bin,
        "alpha.c",
        "--warnings",
        "-V",
        "beta.c",
        "--quiet",
        "--version",
        "--warnings",
        "-d",
    });
    defer testing.allocator.free(genksyms_result.stdout);
    defer testing.allocator.free(genksyms_result.stderr);

    try expectExit(genksyms_result, 0);
    try testing.expectEqualStrings(version_text ++ version_text, genksyms_result.stderr);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--warnings\",\"-V\",\"--quiet\",\"--version\",\"--warnings\",\"-d\",\"alpha.c\",\"beta.c\"],\"options\":{\"debug_level\":1,\"warnings\":true,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":null}}\n",
        genksyms_result.stdout,
    );
}
