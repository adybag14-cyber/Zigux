const std = @import("std");
const Io = std.Io;

const fixdep = @import("fixdep.zig");

test "runFixdep preserves EOT command bytes in savedcmd prelude" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 256),
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

    const depfile_name = "zigux_fixdep_eot_cmdline_test.d";
    const source_name = "zigux_fixdep_eot_cmdline_source.c";

    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = source_name,
        .data = "/* CONFIG_ZIGUX_CMDLINE_EOT */\n",
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, source_name) catch {};

    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = depfile_name,
        .data = "sample.o: " ++ source_name ++ "\n",
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, depfile_name) catch {};

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    const cmdline = "cc\x04-DZIGUX_CMDLINE_EOT=1 -c " ++ source_name;

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_name,
        "sample.o",
        cmdline,
    );

    try std.testing.expectEqualStrings(
        "savedcmd_sample.o := " ++ cmdline ++ "\n\n" ++
            "source_sample.o := " ++ source_name ++ "\n\n" ++
            "deps_sample.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_CMDLINE_EOT) \\\n" ++
            "\n" ++
            "sample.o: $(deps_sample.o)\n\n" ++
            "$(deps_sample.o):\n",
        capture.list.items,
    );
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, 0x04) != null);
}
