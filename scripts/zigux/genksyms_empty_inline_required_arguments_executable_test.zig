const std = @import("std");

const testing = std.testing;

const wrapper_source = "scripts/zigux/genksyms.zig";
const binary_path = ".zig-cache/lane23-empty-inline-genksyms";

fn runProcess(allocator: std.mem.Allocator, argv: []const []const u8) !std.process.RunResult {
    return std.process.run(allocator, testing.io, .{
        .argv = argv,
        .cwd = .{ .path = "." },
        .stdout_limit = .limited(4096),
        .stderr_limit = .limited(4096),
    });
}

fn buildWrapper(allocator: std.mem.Allocator) !void {
    const result = try runProcess(allocator, &.{
        "zig",
        "build-exe",
        wrapper_source,
        "-femit-bin=" ++ binary_path,
        "--cache-dir",
        ".zig-cache/lane23-empty-inline-build",
        "--global-cache-dir",
        ".zig-cache/lane23-empty-inline-build/global",
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try testing.expectEqualStrings("", result.stderr);
}

fn expectRun(
    allocator: std.mem.Allocator,
    argv: []const []const u8,
    expected_stdout: []const u8,
    expected_stderr: []const u8,
) !void {
    const result = try runProcess(allocator, argv);
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try testing.expectEqualStrings(expected_stderr, result.stderr);
    try testing.expectEqualStrings(expected_stdout, result.stdout);
}

test "genksyms executable preserves empty inline required arguments" {
    try buildWrapper(testing.allocator);

    try expectRun(
        testing.allocator,
        &.{
            binary_path,
            "--reference=",
        },
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference=\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"\"],\"dump_types_file\":null}}\n",
        "",
    );

    try expectRun(
        testing.allocator,
        &.{
            binary_path,
            "-V",
            "--dump-t=",
        },
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-V\",\"--dump-t=\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":\"\"}}\n",
        "genksyms version 2.5.60\n",
    );
}
