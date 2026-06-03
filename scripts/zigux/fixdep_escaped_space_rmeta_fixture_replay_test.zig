const std = @import("std");
const fixdep = @import("fixdep.zig");

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

fn writeFixture(path: []const u8, contents: []const u8) !void {
    const file = try std.Io.Dir.cwd().createFile(std.testing.io, path, .{ .truncate = true });
    defer file.close(std.testing.io);

    var buffer: [256]u8 = undefined;
    var writer = file.writer(std.testing.io, &buffer);
    try writer.interface.writeAll(contents);
    try writer.interface.flush();
}

test "escaped-space rmeta fixture replay keeps no-parse payloads inert" {
    const depfile = "zigux_lane13_escaped_space_rmeta.d";
    const source = "zigux_lane13_escaped_space_source.rmeta";
    const escaped_dep = "zigux_lane13_dep\\ name.rmeta";
    const actual_dep = "zigux_lane13_dep name.rmeta";
    const target = "zigux_lane13_escaped_space.o";
    const cmdline = "clang -c zigux/tests/fixtures/fixdep/sample_escaped_space_source.c -o zigux_lane13_escaped_space.o";

    defer std.Io.Dir.cwd().deleteFile(std.testing.io, depfile) catch {};
    defer std.Io.Dir.cwd().deleteFile(std.testing.io, source) catch {};
    defer std.Io.Dir.cwd().deleteFile(std.testing.io, actual_dep) catch {};

    try writeFixture(
        depfile,
        target ++ ": " ++ source ++ " \\\n " ++ escaped_dep ++ "\n",
    );
    try writeFixture(
        source,
        "CONFIG_ZIGUX_ESCAPED_SPACE_RMETA_SOURCE_SHOULD_NOT_PARSE\n",
    );
    try writeFixture(
        actual_dep,
        "CONFIG_ZIGUX_ESCAPED_SPACE_RMETA_DEP_SHOULD_NOT_PARSE\n",
    );

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile,
        target,
        cmdline,
    );

    try std.testing.expectEqualStrings(
        "savedcmd_zigux_lane13_escaped_space.o := " ++ cmdline ++ "\n\n" ++
            "source_zigux_lane13_escaped_space.o := " ++ source ++ "\n\n" ++
            "deps_zigux_lane13_escaped_space.o := \\\n" ++
            "  " ++ escaped_dep ++ " \\\n" ++
            "\n" ++
            "zigux_lane13_escaped_space.o: $(deps_zigux_lane13_escaped_space.o)\n\n" ++
            "$(deps_zigux_lane13_escaped_space.o):\n",
        capture.list.items,
    );
    try std.testing.expectEqual(
        @as(?usize, null),
        std.mem.indexOf(u8, capture.list.items, "include/config/ZIGUX_ESCAPED_SPACE_RMETA"),
    );
}
