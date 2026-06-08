const std = @import("std");
const testing = std.testing;

const binary_path = ".zig-cache/lane23-genksyms-short-cluster-state-bin/genksyms-short-cluster-state";

fn run(
    allocator: std.mem.Allocator,
    argv: []const []const u8,
) !std.process.RunResult {
    return std.process.run(allocator, testing.io, .{
        .argv = argv,
        .reserve_amount = 8192,
    });
}

fn buildGenksyms(allocator: std.mem.Allocator) !void {
    const mkdir_result = try run(allocator, &.{
        "mkdir",
        "-p",
        ".zig-cache/lane23-genksyms-short-cluster-state-bin",
    });
    defer allocator.free(mkdir_result.stdout);
    defer allocator.free(mkdir_result.stderr);
    try testing.expectEqual(@as(u8, 0), mkdir_result.term.exited);

    const build_result = try run(allocator, &.{
        "zig",
        "build-exe",
        "scripts/zigux/genksyms.zig",
        "-femit-bin=" ++ binary_path,
        "--cache-dir",
        ".zig-cache/lane23-genksyms-short-cluster-state-build",
        "--global-cache-dir",
        ".zig-cache/lane23-genksyms-short-cluster-state-build/global",
    });
    defer allocator.free(build_result.stdout);
    defer allocator.free(build_result.stderr);

    if (build_result.term.exited != 0) {
        std.debug.print("genksyms build stderr:\n{s}\n", .{build_result.stderr});
    }
    try testing.expectEqual(@as(u8, 0), build_result.term.exited);
}

test "genksyms executable preserves compact short cluster request state" {
    const allocator = testing.allocator;
    try buildGenksyms(allocator);

    const result = try run(allocator, &.{
        binary_path,
        "-VdDpwq",
        "unit.c",
        "-r",
        "base.symref",
        "-Ttypes.symtypes",
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try testing.expectEqual(@as(u8, 0), result.term.exited);
    try testing.expectEqualStrings("genksyms version 2.5.60\n", result.stderr);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-VdDpwq\",\"-r\",\"base.symref\",\"-Ttypes.symtypes\",\"unit.c\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":true,\"preserve\":true,\"reference_files\":[\"base.symref\"],\"dump_types_file\":\"types.symtypes\"}}\n",
        result.stdout,
    );
}

test "genksyms executable keeps short cluster invalid tail after version side effect" {
    const allocator = testing.allocator;
    try buildGenksyms(allocator);

    const result = try run(allocator, &.{
        binary_path,
        "-Vdqx",
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try testing.expectEqual(@as(u8, 1), result.term.exited);
    try testing.expectEqualStrings("", result.stdout);
    try testing.expect(std.mem.startsWith(
        u8,
        result.stderr,
        "genksyms version 2.5.60\ninvalid option -- 'x'\n",
    ));
}
