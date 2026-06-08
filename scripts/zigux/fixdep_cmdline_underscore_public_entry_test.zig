const std = @import("std");
const fixdep = @import("fixdep.zig");

test "runFixdep preserves underscores in savedcmd output" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 512),
                .allocator = allocator,
            };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        pub fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }

        pub fn flush(_: *@This()) !void {}
    };

    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "zigux_fixdep_underscore_cmdline_source.c",
        .data = "CONFIG_ZIGUX_CMDLINE_UNDERSCORE_SOURCE\n",
    });

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/zigux_fixdep_underscore_cmdline_source.c",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(source_path);

    const depfile_bytes = try std.fmt.allocPrint(
        std.testing.allocator,
        "underscore.o: {s}\n",
        .{source_path},
    );
    defer std.testing.allocator.free(depfile_bytes);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "underscore.d",
        .data = depfile_bytes,
    });

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/underscore.d",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        std.testing.allocator,
        "cc -DUNDER_SCORE_VALUE=zigux_value_1 -Dsnake_case_flag=enabled_value -c {s}",
        .{source_path},
    );
    defer std.testing.allocator.free(cmdline);

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "underscore.o",
        cmdline,
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_underscore.o := {s}\n\n" ++
            "source_underscore.o := {s}\n\n" ++
            "deps_underscore.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_CMDLINE_UNDERSCORE_SOURCE) \\\n" ++
            "\n" ++
            "underscore.o: $(deps_underscore.o)\n\n" ++
            "$(deps_underscore.o):\n",
        .{ cmdline, source_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "UNDER_SCORE_VALUE=zigux_value_1") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "snake_case_flag=enabled_value") != null);
}
