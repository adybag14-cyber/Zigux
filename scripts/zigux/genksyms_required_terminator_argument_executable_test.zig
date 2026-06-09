const std = @import("std");

const testing = std.testing;

const wrapper_source = "scripts/zigux/genksyms.zig";
const binary_path = ".zig-cache/lane23-required-terminator-genksyms";

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
        ".zig-cache/lane23-required-terminator-build",
        "--global-cache-dir",
        ".zig-cache/lane23-required-terminator-build/global",
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try testing.expectEqualStrings("", result.stdout);
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

test "genksyms executable treats terminator-looking required arguments as data" {
    try buildWrapper(testing.allocator);

    try expectRun(
        testing.allocator,
        &.{
            binary_path,
            "--reference",
            "--",
            "--debug",
        },
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference\",\"--\",\"--debug\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"--\"],\"dump_types_file\":null}}\n",
        "",
    );

    try expectRun(
        testing.allocator,
        &.{
            binary_path,
            "-T",
            "--",
            "-w",
            "unit.c",
        },
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-T\",\"--\",\"-w\",\"unit.c\"],\"options\":{\"debug_level\":0,\"warnings\":true,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":\"--\"}}\n",
        "",
    );
}
