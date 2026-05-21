const std = @import("std");
const fixdep = @import("fixdep.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator, capacity: usize) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
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

fn tmpBasePath(tmp: anytype) ![]u8 {
    return std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
}

test "runFixdep reads escaped-space dependency paths and emits config deps" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const base_path = try tmpBasePath(tmp);
    defer std.testing.allocator.free(base_path);

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_escaped_space_source.c",
        .{base_path},
    );
    defer std.testing.allocator.free(source_path);

    const escaped_space_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/escaped\\ space-config.h",
        .{base_path},
    );
    defer std.testing.allocator.free(escaped_space_dep_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_escaped_space.d",
        .{base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        std.testing.allocator,
        "clang -c {s} -o sample_escaped_space.o",
        .{source_path},
    );
    defer std.testing.allocator.free(cmdline);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_escaped_space_source.c",
        .data = "int zigux_fixdep_sample_escaped_space(void) { return 0; }\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "escaped\\ space-config.h",
        .data = "/* CONFIG_ZIGUX_ESCAPED_SPACE */\n",
    });

    const depfile_text = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample_escaped_space.o: {s} \\\n {s}\n",
        .{ source_path, escaped_space_dep_path },
    );
    defer std.testing.allocator.free(depfile_text);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_escaped_space.d",
        .data = depfile_text,
    });

    var capture = try Capture.init(std.testing.allocator, 384);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "sample_escaped_space.o",
        cmdline,
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample_escaped_space.o := {s}\n\n" ++
            "source_sample_escaped_space.o := {s}\n\n" ++
            "deps_sample_escaped_space.o := \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_ESCAPED_SPACE) \\\n" ++
            "\n" ++
            "sample_escaped_space.o: $(deps_sample_escaped_space.o)\n\n" ++
            "$(deps_sample_escaped_space.o):\n",
        .{ cmdline, source_path, escaped_space_dep_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}

test "runFixdep reads escaped-colon dependency paths and trims shared _MODULE configs" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const base_path = try tmpBasePath(tmp);
    defer std.testing.allocator.free(base_path);

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_escaped_colon_source.c",
        .{base_path},
    );
    defer std.testing.allocator.free(source_path);

    const escaped_colon_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/shared\\:config.h",
        .{base_path},
    );
    defer std.testing.allocator.free(escaped_colon_dep_path);

    const escaped_colon_visible_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/shared:config.h",
        .{base_path},
    );
    defer std.testing.allocator.free(escaped_colon_visible_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_escaped_colon.d",
        .{base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        std.testing.allocator,
        "clang -c {s} -o sample_escaped_colon.o",
        .{source_path},
    );
    defer std.testing.allocator.free(cmdline);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_escaped_colon_source.c",
        .data = "int zigux_fixdep_sample_escaped_colon(void) { return 0; }\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "shared:config.h",
        .data = "#define CONFIG_ZIGUX_COLON 1\n" ++
            "#define CONFIG_ZIGUX_SHARED_COLON_MODULE 1\n" ++
            "#define CONFIG_ZIGUX_COLON 1\n",
    });

    const depfile_text = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample_escaped_colon.o: {s} \\\n {s}\n",
        .{ source_path, escaped_colon_dep_path },
    );
    defer std.testing.allocator.free(depfile_text);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_escaped_colon.d",
        .data = depfile_text,
    });

    var capture = try Capture.init(std.testing.allocator, 416);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "sample_escaped_colon.o",
        cmdline,
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample_escaped_colon.o := {s}\n\n" ++
            "source_sample_escaped_colon.o := {s}\n\n" ++
            "deps_sample_escaped_colon.o := \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_COLON) \\\n" ++
            "    $(wildcard include/config/ZIGUX_SHARED_COLON) \\\n" ++
            "\n" ++
            "sample_escaped_colon.o: $(deps_sample_escaped_colon.o)\n\n" ++
            "$(deps_sample_escaped_colon.o):\n",
        .{ cmdline, source_path, escaped_colon_visible_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}
