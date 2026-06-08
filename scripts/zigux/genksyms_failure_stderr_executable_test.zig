const std = @import("std");

const testing = std.testing;

const version_text = "genksyms version 2.5.60\n";

fn expectExited(term: std.process.Child.Term, expected_code: u8) !void {
    switch (term) {
        .exited => |code| try testing.expectEqual(expected_code, code),
        else => return error.ExpectedExitedProcess,
    }
}

fn expectFailureRun(
    exe_path: []const u8,
    args: []const []const u8,
    expected_stderr_prefix: []const u8,
    expected_error_line: []const u8,
    expect_usage: bool,
) !void {
    var argv = std.ArrayList([]const u8).empty;
    defer argv.deinit(testing.allocator);
    try argv.append(testing.allocator, exe_path);
    try argv.appendSlice(testing.allocator, args);

    const result = try std.process.run(testing.allocator, testing.io, .{
        .argv = argv.items,
        .stdout_limit = .limited(4096),
        .stderr_limit = .limited(8192),
    });
    defer testing.allocator.free(result.stdout);
    defer testing.allocator.free(result.stderr);

    try expectExited(result.term, 1);
    try testing.expectEqualStrings("", result.stdout);
    try testing.expect(std.mem.startsWith(u8, result.stderr, expected_stderr_prefix));
    try testing.expect(std.mem.containsAtLeast(u8, result.stderr, 1, expected_error_line));

    const has_usage = std.mem.containsAtLeast(u8, result.stderr, 1, "Usage:\n");
    try testing.expectEqual(expect_usage, has_usage);
}

test "genksyms executable sends parse failures to stderr without request JSON" {
    var tmp = testing.tmpDir(.{});
    defer tmp.cleanup();

    var exe_path_buffer: [256]u8 = undefined;
    const exe_path = try std.fmt.bufPrint(
        &exe_path_buffer,
        ".zig-cache/tmp/{s}/genksyms-failure-stderr",
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

    try expectFailureRun(
        exe_path,
        &.{ "--version", "--reference" },
        version_text,
        "option '--reference' requires an argument\n",
        true,
    );

    try expectFailureRun(
        exe_path,
        &.{"-Vx"},
        version_text,
        "invalid option -- 'x'\n",
        true,
    );

    var reference_args = std.ArrayList([]const u8).empty;
    defer reference_args.deinit(testing.allocator);
    for (0..17) |index| {
        try reference_args.append(testing.allocator, "-r");
        const name = try std.fmt.allocPrint(testing.allocator, "ref-{d}.sym", .{index + 1});
        errdefer testing.allocator.free(name);
        try reference_args.append(testing.allocator, name);
    }
    defer {
        var index: usize = 1;
        while (index < reference_args.items.len) : (index += 2) {
            testing.allocator.free(reference_args.items[index]);
        }
    }

    try expectFailureRun(
        exe_path,
        reference_args.items,
        "too many reference files\n",
        "too many reference files\n",
        false,
    );
}
