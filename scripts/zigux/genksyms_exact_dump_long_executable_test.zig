const std = @import("std");
const testing = std.testing;

fn run(
    allocator: std.mem.Allocator,
    argv: []const []const u8,
) !std.process.RunResult {
    return std.process.run(allocator, testing.io, .{
        .argv = argv,
        .reserve_amount = 8192,
    });
}

fn expectExit(term: std.process.Child.Term, expected: u8) !void {
    switch (term) {
        .exited => |code| try testing.expectEqual(expected, code),
        else => return error.UnexpectedProcessTermination,
    }
}

fn buildGenksyms(allocator: std.mem.Allocator, binary_path: []const u8, cache_name: []const u8) !void {
    const mkdir_result = try run(allocator, &.{
        "mkdir",
        "-p",
        ".zig-cache/lane23-genksyms-exact-dump-long-bin",
    });
    defer allocator.free(mkdir_result.stdout);
    defer allocator.free(mkdir_result.stderr);
    try expectExit(mkdir_result.term, 0);

    const cache_dir = try std.mem.concat(allocator, u8, &.{
        ".zig-cache/lane23-genksyms-exact-dump-long-build-",
        cache_name,
    });
    defer allocator.free(cache_dir);
    const global_cache_dir = try std.mem.concat(allocator, u8, &.{ cache_dir, "/global" });
    defer allocator.free(global_cache_dir);
    const emit_arg = try std.mem.concat(allocator, u8, &.{ "-femit-bin=", binary_path });
    defer allocator.free(emit_arg);

    const build_result = try run(allocator, &.{
        "zig",
        "build-exe",
        "scripts/zigux/genksyms.zig",
        emit_arg,
        "--cache-dir",
        cache_dir,
        "--global-cache-dir",
        global_cache_dir,
    });
    defer allocator.free(build_result.stdout);
    defer allocator.free(build_result.stderr);

    switch (build_result.term) {
        .exited => |code| if (code != 0) {
            std.debug.print("genksyms build stderr:\n{s}\n", .{build_result.stderr});
        },
        else => std.debug.print("genksyms build terminated unexpectedly; stderr:\n{s}\n", .{build_result.stderr}),
    }
    try expectExit(build_result.term, 0);
}

test "genksyms executable keeps exact dump distinct from dump-types" {
    const allocator = testing.allocator;
    const binary_path = ".zig-cache/lane23-genksyms-exact-dump-long-bin/genksyms-exact-dump-long";
    try buildGenksyms(allocator, binary_path, "combined");

    const success_result = try run(allocator, &.{
        binary_path,
        "--dump",
        "--dump-t=types.symtypes",
        "--reference",
        "base.symref",
        "unit.c",
    });
    defer allocator.free(success_result.stdout);
    defer allocator.free(success_result.stderr);

    try expectExit(success_result.term, 0);
    try testing.expectEqualStrings("", success_result.stderr);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--dump\",\"--dump-t=types.symtypes\",\"--reference\",\"base.symref\",\"unit.c\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":true,\"preserve\":false,\"reference_files\":[\"base.symref\"],\"dump_types_file\":\"types.symtypes\"}}\n",
        success_result.stdout,
    );

    const failure_result = try run(allocator, &.{
        binary_path,
        "--version",
        "--dump",
        "--d",
    });
    defer allocator.free(failure_result.stdout);
    defer allocator.free(failure_result.stderr);

    try expectExit(failure_result.term, 1);
    try testing.expectEqualStrings("", failure_result.stdout);
    try testing.expect(std.mem.startsWith(
        u8,
        failure_result.stderr,
        "genksyms version 2.5.60\noption '--d' is ambiguous",
    ));
}
