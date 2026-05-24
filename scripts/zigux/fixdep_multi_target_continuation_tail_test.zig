const std = @import("std");
const fixdep = @import("./fixdep.zig");

test "runFixdep preserves widened multi-target continuation tail output" {
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

    const base_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(base_path);

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample2.c",
        .{base_path},
    );
    defer std.testing.allocator.free(source_path);

    const second_config_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample2-config.h",
        .{base_path},
    );
    defer std.testing.allocator.free(second_config_path);

    const no_parse_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample2.so",
        .{base_path},
    );
    defer std.testing.allocator.free(no_parse_path);

    const ignored_autoconf_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/include/generated/autoconf.h",
        .{base_path},
    );
    defer std.testing.allocator.free(ignored_autoconf_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_multi_target_continuation.d",
        .{base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        std.testing.allocator,
        "clang -Iinclude -DZIGUX_MULTI -c {s} -o module/sample2.o",
        .{source_path},
    );
    defer std.testing.allocator.free(cmdline);

    _ = try tmp.dir.createDirPathStatus(std.testing.io, "include/generated", .default_dir);
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample2.c",
        .data = "#define CONFIG_ZIGUX_MULTI 1\nint zigux_fixdep_sample2(void) { return 0; }\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample2-config.h",
        .data = "#define CONFIG_ZIGUX_SECOND 1\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample2.so",
        .data = "",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "include/generated/autoconf.h",
        .data = "#define CONFIG_ZIGUX_AUTOCONF 1\n",
    });

    const depfile_text = try std.fmt.allocPrint(
        std.testing.allocator,
        "module/sample2.o: {s} {s} {s} \\\n {s} {s}\n",
        .{
            source_path,
            second_config_path,
            no_parse_path,
            ignored_autoconf_path,
            no_parse_path,
        },
    );
    defer std.testing.allocator.free(depfile_text);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_multi_target_continuation.d",
        .data = depfile_text,
    });

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "module/sample2.o",
        cmdline,
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_module/sample2.o := {s}\n\n" ++
            "source_module/sample2.o := {s}\n\n" ++
            "deps_module/sample2.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_MULTI) \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_SECOND) \\\n" ++
            "  {s} \\\n\n" ++
            "module/sample2.o: $(deps_module/sample2.o)\n\n" ++
            "$(deps_module/sample2.o):\n",
        .{ cmdline, source_path, second_config_path, no_parse_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}
