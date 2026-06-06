const std = @import("std");

fn expectExit(term: std.process.Child.Term, expected_code: u8) !void {
    switch (term) {
        .exited => |code| try std.testing.expectEqual(expected_code, code),
        else => return error.UnexpectedChildTermination,
    }
}

fn expectConfBridgeRun(args: []const []const u8, expected_fragments: []const []const u8, rejected_fragments: []const []const u8) !void {
    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = args,
        .stdout_limit = .limited(4096),
        .stderr_limit = .limited(4096),
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try expectExit(result.term, 0);
    try std.testing.expectEqualStrings("", result.stderr);
    for (expected_fragments) |fragment| {
        try std.testing.expect(std.mem.indexOf(u8, result.stdout, fragment) != null);
    }
    for (rejected_fragments) |fragment| {
        try std.testing.expect(std.mem.indexOf(u8, result.stdout, fragment) == null);
    }
}

test "conf bridge CLI preserves allconfig path override split" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const exe_path = try std.fs.path.join(std.testing.allocator, &.{
        ".zig-cache",
        "tmp",
        tmp.sub_path[0..],
        "conf_bridge_cli_probe",
    });
    defer std.testing.allocator.free(exe_path);

    const emit_arg = try std.fmt.allocPrint(std.testing.allocator, "-femit-bin={s}", .{exe_path});
    defer std.testing.allocator.free(emit_arg);

    const build_result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            "scripts/zigux/kconfig/conf_bridge.zig",
            emit_arg,
        },
        .stdout_limit = .limited(4096),
        .stderr_limit = .limited(4096),
    });
    defer std.testing.allocator.free(build_result.stdout);
    defer std.testing.allocator.free(build_result.stderr);
    try expectExit(build_result.term, 0);
    try std.testing.expectEqualStrings("", build_result.stderr);

    try expectConfBridgeRun(
        &.{ exe_path, "allnoconfig", "Kconfig", "none/.config", "arm64", "allconfig=mini-all.config" },
        &.{
            "\"mode\":\"allnoconfig\"",
            "\"--allnoconfig\"",
            "\"KCONFIG_CONFIG\":\"none/.config\"",
            "\"ARCH\":\"arm64\"",
            "\"KCONFIG_ALLCONFIG\":\"mini-all.config\"",
        },
        &.{
            "\"KCONFIG_ALLCONFIG\":\"1\"",
        },
    );

    try expectConfBridgeRun(
        &.{ exe_path, "alldefconfig", "Kconfig", "def/.config", "riscv", "allconfig=arch/riscv/configs/tiny.config" },
        &.{
            "\"mode\":\"alldefconfig\"",
            "\"--alldefconfig\"",
            "\"KCONFIG_CONFIG\":\"def/.config\"",
            "\"ARCH\":\"riscv\"",
            "\"KCONFIG_ALLCONFIG\":\"arch/riscv/configs/tiny.config\"",
        },
        &.{
            "\"KCONFIG_ALLCONFIG\":\"1\"",
        },
    );
}
