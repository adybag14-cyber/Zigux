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

test "runFixdep keeps the first target while parsing richer multi-target dependency packets" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const allocator = std.testing.allocator;
    const base_path = try tmpBasePath(tmp);
    defer allocator.free(base_path);

    const depfile_path = try std.fmt.allocPrint(allocator, "{s}/sample_multi_target.d", .{base_path});
    defer allocator.free(depfile_path);
    const source_path = try std.fmt.allocPrint(allocator, "{s}/sample2.c", .{base_path});
    defer allocator.free(source_path);
    const shared_config_path = try std.fmt.allocPrint(allocator, "{s}/shared#config.h", .{base_path});
    defer allocator.free(shared_config_path);
    const config_dep_path = try std.fmt.allocPrint(allocator, "{s}/sample2-config.h", .{base_path});
    defer allocator.free(config_dep_path);
    const shared_object_path = try std.fmt.allocPrint(allocator, "{s}/sample2.so", .{base_path});
    defer allocator.free(shared_object_path);
    const escaped_shared_config_path = try std.mem.replaceOwned(
        u8,
        allocator,
        shared_config_path,
        "#",
        "\\#",
    );
    defer allocator.free(escaped_shared_config_path);

    const cmdline = try std.fmt.allocPrint(
        allocator,
        "clang -Iinclude -DZIGUX_MULTI -c {s} -o module/sample2.o",
        .{source_path},
    );
    defer allocator.free(cmdline);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample2.c",
        .data = "#define CONFIG_ZIGUX_MULTI 1\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "shared#config.h",
        .data = "#define CONFIG_ZIGUX_HASH 1\n#define CONFIG_ZIGUX_SHARED_MODULE 1\n#define CONFIG_ZIGUX_HASH 1\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample2-config.h",
        .data = "#define CONFIG_ZIGUX_SECOND 1\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample2.so",
        .data = "placeholder shared-object fixture for fixdep multi-target coverage\n",
    });

    const depfile_text = try std.fmt.allocPrint(
        allocator,
        "module/sample2.o module/sample2.dwo: {s} {s} {s} {s}\n",
        .{ source_path, escaped_shared_config_path, config_dep_path, shared_object_path },
    );
    defer allocator.free(depfile_text);
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_multi_target.d",
        .data = depfile_text,
    });

    var capture = try Capture.init(allocator, 1024);
    defer capture.deinit();

    try fixdep.runFixdep(
        allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "module/sample2.o",
        cmdline,
    );

    const expected = try std.fmt.allocPrint(
        allocator,
        "savedcmd_module/sample2.o := {s}\n\n" ++
            "source_module/sample2.o := {s}\n\n" ++
            "deps_module/sample2.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_MULTI) \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_HASH) \\\n" ++
            "    $(wildcard include/config/ZIGUX_SHARED) \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_SECOND) \\\n" ++
            "  {s} \\\n" ++
            "\n" ++
            "module/sample2.o: $(deps_module/sample2.o)\n\n" ++
            "$(deps_module/sample2.o):\n",
        .{ cmdline, source_path, shared_config_path, config_dep_path, shared_object_path },
    );
    defer allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}
