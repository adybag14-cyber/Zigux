const std = @import("std");

const allocator = std.testing.allocator;
const unexpected_mode_argument_message = "Error: unexpected mode argument\n";

const UnexpectedModeArgumentCase = struct {
    mode: []const u8,
    arg: []const u8,
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

fn expectUnexpectedModeArgument(exe_path: []const u8, case: UnexpectedModeArgumentCase) !void {
    const result = try runAndCapture(&.{
        exe_path,
        case.mode,
        "Kconfig",
        ".config",
        "x86_64",
        case.arg,
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 1 }, result.term);
    try std.testing.expectEqualStrings("", result.stdout);
    try std.testing.expectEqualStrings(unexpected_mode_argument_message, result.stderr);
}

test "conf bridge CLI rejects stray mode arguments before bridge option parsing" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const exe_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/conf-bridge-unexpected-mode-argument-surface",
        .{tmp.sub_path[0..]},
    );
    defer allocator.free(exe_path);

    try buildConfBridge(exe_path);

    const cases = [_]UnexpectedModeArgumentCase{
        .{ .mode = "oldconfig", .arg = "arch/x86/configs/debug_defconfig" },
        .{ .mode = "olddefconfig", .arg = "extra.config" },
        .{ .mode = "syncconfig", .arg = "include/config/auto.conf" },
        .{ .mode = "listnewconfig", .arg = "CONFIG_NEW_SYMBOL" },
        .{ .mode = "mod2noconfig", .arg = "rewrite/.config" },
    };

    for (cases) |case| {
        try expectUnexpectedModeArgument(exe_path, case);
    }

    const option_shaped = try runAndCapture(&.{
        exe_path,
        "oldconfig",
        "Kconfig",
        ".config",
        "x86_64",
        "allconfig=mini.config",
    });
    defer allocator.free(option_shaped.stdout);
    defer allocator.free(option_shaped.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 1 }, option_shaped.term);
    try std.testing.expectEqualStrings("", option_shaped.stdout);
    try std.testing.expectEqualStrings("Error: unexpected bridge option for mode\n", option_shaped.stderr);
}
