const std = @import("std");

const allocator = std.testing.allocator;

const DuplicateOptionCase = struct {
    name: []const u8,
    mode: []const u8,
    args: []const []const u8,
    stderr: []const u8,
};

fn runAndCapture(argv: []const []const u8) !std.process.RunResult {
    return try std.process.run(allocator, std.testing.io, .{
        .argv = argv,
        .stdout_limit = .limited(1024),
        .stderr_limit = .limited(1024),
    });
}

fn buildConfBridge(output_path: []const u8) !void {
    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{output_path});
    defer allocator.free(emit_arg);

    const result = try runAndCapture(&.{
        "zig",
        "build-exe",
        "scripts/zigux/kconfig/conf_bridge.zig",
        emit_arg,
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
}

fn expectDuplicateOptionFailure(exe_path: []const u8, case: DuplicateOptionCase) !void {
    var argv = std.ArrayList([]const u8).empty;
    defer argv.deinit(allocator);

    try argv.append(allocator, exe_path);
    try argv.append(allocator, case.mode);
    try argv.append(allocator, "Kconfig");
    try argv.append(allocator, ".config");
    try argv.append(allocator, "x86_64");
    try argv.appendSlice(allocator, case.args);

    const result = try runAndCapture(argv.items);
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 1 }, result.term);
    try std.testing.expectEqualStrings("", result.stdout);
    try std.testing.expectEqualStrings(case.stderr, result.stderr);
}

test "conf bridge CLI reports duplicate bridge options before emitting JSON" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const exe_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/conf-bridge-duplicate-option-surface",
        .{tmp.sub_path[0..]},
    );
    defer allocator.free(exe_path);

    try buildConfBridge(exe_path);

    const cases = [_]DuplicateOptionCase{
        .{
            .name = "silent",
            .mode = "oldconfig",
            .args = &.{ "silent", "silent" },
            .stderr = "Error: duplicate silent option\n",
        },
        .{
            .name = "allconfig",
            .mode = "randconfig",
            .args = &.{ "allconfig=one", "allconfig=two" },
            .stderr = "Error: duplicate allconfig override option\n",
        },
        .{
            .name = "seed",
            .mode = "randconfig",
            .args = &.{ "seed=1", "seed=2" },
            .stderr = "Error: duplicate randconfig seed option\n",
        },
        .{
            .name = "probability",
            .mode = "randconfig",
            .args = &.{ "probability=10", "probability=20" },
            .stderr = "Error: duplicate randconfig probability option\n",
        },
        .{
            .name = "nosilentupdate",
            .mode = "syncconfig",
            .args = &.{ "nosilentupdate=1", "nosilentupdate=0" },
            .stderr = "Error: duplicate syncconfig nosilentupdate option\n",
        },
    };

    for (cases) |case| {
        try expectDuplicateOptionFailure(exe_path, case);
    }
}
