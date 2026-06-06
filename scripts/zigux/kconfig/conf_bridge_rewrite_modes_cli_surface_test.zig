const std = @import("std");

const testing = std.testing;

const Case = struct {
    mode: []const u8,
    flag: []const u8,
    config: []const u8,
    arch: []const u8,
};

test "conf bridge rewrite modes run through executable CLI surface" {
    var tmp = testing.tmpDir(.{});
    defer tmp.cleanup();

    const exe_path = try std.fmt.allocPrint(
        testing.allocator,
        ".zig-cache/tmp/{s}/conf_bridge_rewrite_modes",
        .{tmp.sub_path[0..]},
    );
    defer testing.allocator.free(exe_path);

    const emit_arg = try std.fmt.allocPrint(testing.allocator, "-femit-bin={s}", .{exe_path});
    defer testing.allocator.free(emit_arg);

    const build_result = try std.process.run(testing.allocator, testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            "scripts/zigux/kconfig/conf_bridge.zig",
            emit_arg,
        },
    });
    defer testing.allocator.free(build_result.stdout);
    defer testing.allocator.free(build_result.stderr);

    switch (build_result.term) {
        .exited => |code| try testing.expectEqual(@as(u8, 0), code),
        else => return error.ConfBridgeBuildDidNotExitCleanly,
    }
    try testing.expectEqualStrings("", build_result.stderr);

    const cases = [_]Case{
        .{
            .mode = "yes2modconfig",
            .flag = "--yes2modconfig",
            .config = "rewrite/.config",
            .arch = "x86",
        },
        .{
            .mode = "mod2yesconfig",
            .flag = "--mod2yesconfig",
            .config = "promote/.config",
            .arch = "arm64",
        },
        .{
            .mode = "mod2noconfig",
            .flag = "--mod2noconfig",
            .config = "demote/.config",
            .arch = "riscv",
        },
    };

    for (cases) |case| {
        const run_result = try std.process.run(testing.allocator, testing.io, .{
            .argv = &.{
                exe_path,
                case.mode,
                "Kconfig",
                case.config,
                case.arch,
                "silent",
            },
        });
        defer testing.allocator.free(run_result.stdout);
        defer testing.allocator.free(run_result.stderr);

        switch (run_result.term) {
            .exited => |code| try testing.expectEqual(@as(u8, 0), code),
            else => return error.ConfBridgeRunDidNotExitCleanly,
        }

        try testing.expectEqualStrings("", run_result.stderr);
        try expectContains(run_result.stdout, "\"tool\":\"scripts/kconfig/conf\"");
        const mode_json = try std.fmt.allocPrint(testing.allocator, "\"mode\":\"{s}\"", .{case.mode});
        defer testing.allocator.free(mode_json);
        try expectContains(run_result.stdout, mode_json);
        try expectContains(run_result.stdout, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",");
        try expectContains(run_result.stdout, case.flag);
        try expectContains(run_result.stdout, "\"Kconfig\"]");
        const arch_json = try std.fmt.allocPrint(testing.allocator, "\"ARCH\":\"{s}\"", .{case.arch});
        defer testing.allocator.free(arch_json);
        try expectContains(run_result.stdout, arch_json);
        const config_json = try std.fmt.allocPrint(testing.allocator, "\"KCONFIG_CONFIG\":\"{s}\"", .{case.config});
        defer testing.allocator.free(config_json);
        try expectContains(run_result.stdout, config_json);
        try testing.expect(std.mem.indexOf(u8, run_result.stdout, "KCONFIG_ALLCONFIG") == null);
        try testing.expect(std.mem.indexOf(u8, run_result.stdout, "allconfig_fallbacks") == null);
    }
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}
