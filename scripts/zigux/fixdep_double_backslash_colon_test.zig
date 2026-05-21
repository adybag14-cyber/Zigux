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

test "runFixdep keeps double-backslash-before-colon dependency splits aligned with C fixdep" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const base_path = try tmpBasePath(tmp);
    defer std.testing.allocator.free(base_path);

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_double_backslash_colon_source.rmeta",
        .{base_path},
    );
    defer std.testing.allocator.free(source_path);

    const double_backslash_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/missing\\",
        .{base_path},
    );
    defer std.testing.allocator.free(double_backslash_dep_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_double_backslash_colon.d",
        .{base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        std.testing.allocator,
        "clang -c {s} -o sample_double_backslash_colon.o",
        .{source_path},
    );
    defer std.testing.allocator.free(cmdline);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "missing\\",
        .data = "#define CONFIG_ZIGUX_DOUBLE_BACKSLASH_COLON 1\n",
    });

    const depfile_text = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample_double_backslash_colon.o: {s} {s}:ignored_second_source.rmeta\n",
        .{ source_path, double_backslash_dep_path },
    );
    defer std.testing.allocator.free(depfile_text);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_double_backslash_colon.d",
        .data = depfile_text,
    });

    var capture = try Capture.init(std.testing.allocator, 512);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "sample_double_backslash_colon.o",
        cmdline,
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample_double_backslash_colon.o := {s}\n\n" ++
            "source_sample_double_backslash_colon.o := {s}\n\n" ++
            "deps_sample_double_backslash_colon.o := \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_DOUBLE_BACKSLASH_COLON) \\\n" ++
            "\n" ++
            "sample_double_backslash_colon.o: $(deps_sample_double_backslash_colon.o)\n\n" ++
            "$(deps_sample_double_backslash_colon.o):\n",
        .{ cmdline, source_path, double_backslash_dep_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}
