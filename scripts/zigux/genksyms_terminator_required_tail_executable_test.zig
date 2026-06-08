const std = @import("std");
const testing = std.testing;

const zig_path = "zig";
const genksyms_source = "scripts/zigux/genksyms.zig";

fn expectExited(term: std.process.Child.Term, expected_code: u8) !void {
    switch (term) {
        .exited => |code| try testing.expectEqual(expected_code, code),
        else => return error.UnexpectedChildTermination,
    }
}

fn runCaptured(allocator: std.mem.Allocator, argv: []const []const u8) !std.process.RunResult {
    return std.process.run(allocator, testing.io, .{
        .argv = argv,
        .expand_arg0 = .expand,
        .stdout_limit = .limited(4096),
        .stderr_limit = .limited(4096),
    });
}

test "genksyms executable keeps required-looking args after terminator as data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();
    const allocator = arena_state.allocator();

    var tmp_dir = testing.tmpDir(.{});
    defer tmp_dir.cleanup();

    var tmp_path_buffer: [std.fs.max_path_bytes]u8 = undefined;
    const tmp_path_len = try tmp_dir.dir.realPath(testing.io, &tmp_path_buffer);
    const binary_path = try std.fmt.allocPrint(
        allocator,
        "{s}/genksyms-terminator-required-tail",
        .{tmp_path_buffer[0..tmp_path_len]},
    );
    const emit_bin_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{binary_path});
    const build_result = try runCaptured(allocator, &.{
        zig_path,
        "build-exe",
        genksyms_source,
        emit_bin_arg,
        "--cache-dir",
        ".zig-cache/lane23-terminator-required-build",
        "--global-cache-dir",
        ".zig-cache/lane23-terminator-required-global",
    });
    try expectExited(build_result.term, 0);
    try testing.expectEqualStrings("", build_result.stderr);

    const run_result = try runCaptured(allocator, &.{
        binary_path,
        "-d",
        "--",
        "-r",
        "after.symref",
        "--dump-types",
        "after.symtypes",
        "unit.c",
    });

    try expectExited(run_result.term, 0);
    try testing.expectEqualStrings("", run_result.stderr);
    try testing.expect(std.mem.containsAtLeast(
        u8,
        run_result.stdout,
        1,
        "\"argv\":[\"scripts/genksyms/genksyms\",\"-d\",\"--\",\"-r\",\"after.symref\",\"--dump-types\",\"after.symtypes\",\"unit.c\"]",
    ));
    try testing.expect(std.mem.containsAtLeast(u8, run_result.stdout, 1, "\"debug_level\":1"));
    try testing.expect(std.mem.containsAtLeast(u8, run_result.stdout, 1, "\"reference_files\":[]"));
    try testing.expect(std.mem.containsAtLeast(u8, run_result.stdout, 1, "\"dump_types_file\":null"));
    try testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"reference_files\":[\"after.symref\"]") == null);
    try testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"dump_types_file\":\"after.symtypes\"") == null);
}
