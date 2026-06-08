const std = @import("std");
const testing = std.testing;

const version_text = "genksyms version 2.5.60\n";

fn run(allocator: std.mem.Allocator, argv: []const []const u8) !std.process.RunResult {
    return std.process.run(allocator, testing.io, .{
        .argv = argv,
        .stdout_limit = .limited(8192),
        .stderr_limit = .limited(8192),
    });
}

test "genksyms executable keeps inline long required values as data" {
    const allocator = testing.allocator;
    const exe_path = try std.fs.path.join(allocator, &.{ ".zig-cache", "lane23-inline-long-required-exe", "genksyms-inline-long-required" });
    defer allocator.free(exe_path);

    const mkdir_result = try run(allocator, &.{ "mkdir", "-p", std.fs.path.dirname(exe_path).? });
    defer allocator.free(mkdir_result.stdout);
    defer allocator.free(mkdir_result.stderr);
    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, mkdir_result.term);

    const build_result = try run(allocator, &.{
        "zig",
        "build-exe",
        "scripts/zigux/genksyms.zig",
        "-femit-bin=.zig-cache/lane23-inline-long-required-exe/genksyms-inline-long-required",
        "--cache-dir",
        ".zig-cache/lane23-inline-long-required-build",
        "--global-cache-dir",
        ".zig-cache/lane23-inline-long-required-build/global",
    });
    defer allocator.free(build_result.stdout);
    defer allocator.free(build_result.stderr);
    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, build_result.term);
    try testing.expectEqualStrings("", build_result.stdout);
    try testing.expectEqualStrings("", build_result.stderr);

    const exact_inline = try run(allocator, &.{
        exe_path,
        "--reference=--debug",
        "--dump-types=--types",
        "--debug",
        "--warnings",
        "--quiet",
        "unit.c",
    });
    defer allocator.free(exact_inline.stdout);
    defer allocator.free(exact_inline.stderr);
    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, exact_inline.term);
    try testing.expectEqualStrings("", exact_inline.stderr);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference=--debug\",\"--dump-types=--types\",\"--debug\",\"--warnings\",\"--quiet\",\"unit.c\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"--debug\"],\"dump_types_file\":\"--types\"}}\n",
        exact_inline.stdout,
    );

    const abbreviated_inline = try run(allocator, &.{
        exe_path,
        "--ver",
        "--ref=--quiet",
        "--dump-t=--preserve",
        "--preserve",
        "unit.c",
    });
    defer allocator.free(abbreviated_inline.stdout);
    defer allocator.free(abbreviated_inline.stderr);
    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, abbreviated_inline.term);
    try testing.expectEqualStrings(version_text, abbreviated_inline.stderr);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--ver\",\"--ref=--quiet\",\"--dump-t=--preserve\",\"--preserve\",\"unit.c\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":true,\"reference_files\":[\"--quiet\"],\"dump_types_file\":\"--preserve\"}}\n",
        abbreviated_inline.stdout,
    );
}
