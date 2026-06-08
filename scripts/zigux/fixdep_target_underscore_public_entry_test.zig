const std = @import("std");
const fixdep = @import("fixdep.zig");

test "runFixdep preserves underscores in target output" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 768),
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
        .sub_path = "zigux_fixdep_target_underscore_source.c",
        .data = "CONFIG_ZIGUX_TARGET_UNDERSCORE_SOURCE\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "zigux_fixdep_target_underscore_dep.h",
        .data = "CONFIG_ZIGUX_TARGET_UNDERSCORE_HEADER\n",
    });

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/zigux_fixdep_target_underscore_source.c",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(source_path);

    const header_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/zigux_fixdep_target_underscore_dep.h",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(header_path);

    const target = "module_zigux_underscore_target.o";

    const depfile_bytes = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}: {s} {s}\n",
        .{ target, source_path, header_path },
    );
    defer std.testing.allocator.free(depfile_bytes);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "target_underscore.d",
        .data = depfile_bytes,
    });

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/target_underscore.d",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        std.testing.allocator,
        "cc -DZIGUX_TARGET_UNDERSCORE=1 -c {s} -o {s}",
        .{ source_path, target },
    );
    defer std.testing.allocator.free(cmdline);

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        target,
        cmdline,
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_{s} := {s}\n\n" ++
            "source_{s} := {s}\n\n" ++
            "deps_{s} := \\\n" ++
            "    $(wildcard include/config/ZIGUX_TARGET_UNDERSCORE_SOURCE) \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_TARGET_UNDERSCORE_HEADER) \\\n" ++
            "\n" ++
            "{s}: $(deps_{s})\n\n" ++
            "$(deps_{s}):\n",
        .{ target, cmdline, target, source_path, target, header_path, target, target, target },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "savedcmd_module_zigux_underscore_target.o") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "module_zigux_underscore_target.o: $(deps_module_zigux_underscore_target.o)") != null);
}
