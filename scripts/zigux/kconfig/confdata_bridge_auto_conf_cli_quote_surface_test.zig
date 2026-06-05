const std = @import("std");

const allocator = std.testing.allocator;
const io = std.testing.io;

const RunResult = struct {
    stdout: []u8,
    stderr: []u8,

    fn deinit(self: RunResult) void {
        allocator.free(self.stdout);
        allocator.free(self.stderr);
    }
};

fn expectExited(term: std.process.Child.Term, expected: u8) !void {
    switch (term) {
        .exited => |code| try std.testing.expectEqual(expected, code),
        else => try std.testing.expect(false),
    }
}

fn run(argv: []const []const u8) !RunResult {
    const result = try std.process.run(allocator, io, .{
        .argv = argv,
        .stdout_limit = .limited(16 * 1024),
        .stderr_limit = .limited(16 * 1024),
    });
    errdefer allocator.free(result.stdout);
    errdefer allocator.free(result.stderr);
    try expectExited(result.term, 0);
    return .{ .stdout = result.stdout, .stderr = result.stderr };
}

test "confdata bridge auto.conf CLI quotes string exports" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const config_bytes =
        "CONFIG_ALPHA=y\n" ++
        "CONFIG_MODULE=m\n" ++
        "CONFIG_PATH=\"drivers\\\\misc\\\"zigux\"\n" ++
        "CONFIG_EMPTY=\n" ++
        "CONFIG_QUOTED_EMPTY=\"\"\n" ++
        "CONFIG_COUNT=42\n" ++
        "CONFIG_EXPLICIT_N=n\n" ++
        "# CONFIG_DEBUG is not set\n";

    try tmp.dir.writeFile(io, .{
        .sub_path = "auto-conf-quote.config",
        .data = config_bytes,
    });

    const config_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/auto-conf-quote.config",
        .{tmp.sub_path[0..]},
    );
    defer allocator.free(config_path);

    const exe_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/confdata-bridge-auto-conf",
        .{tmp.sub_path[0..]},
    );
    defer allocator.free(exe_path);
    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{exe_path});
    defer allocator.free(emit_arg);

    {
        const build_result = try run(&.{
            "zig",
            "build-exe",
            "scripts/zigux/kconfig/confdata_bridge.zig",
            emit_arg,
        });
        defer build_result.deinit();
        try std.testing.expectEqualStrings("", build_result.stdout);
        try std.testing.expectEqualStrings("", build_result.stderr);
    }

    const output = try run(&.{ exe_path, "auto.conf", config_path });
    defer output.deinit();

    try std.testing.expectEqualStrings("", output.stderr);
    try std.testing.expectEqualStrings(
        "CONFIG_ALPHA=y\n" ++
            "CONFIG_MODULE=m\n" ++
            "CONFIG_PATH=\"drivers\\\\misc\\\"zigux\"\n" ++
            "CONFIG_EMPTY=\n" ++
            "CONFIG_QUOTED_EMPTY=\"\"\n" ++
            "CONFIG_COUNT=42\n" ++
            "CONFIG_EXPLICIT_N=n\n",
        output.stdout,
    );
}
