const std = @import("std");
const Io = std.Io;

const fixdep = @import("fixdep.zig");

test "runFixdep parses config symbols from continued dependency lines" {
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

    const depfile_name = "zigux_fixdep_line_continuation_config_test.d";
    const source_name = "zigux_fixdep_line_continuation_source.rmeta";
    const lf_header_name = "zigux_fixdep_line_continuation_lf.h";
    const second_header_name = "zigux_fixdep_line_continuation_second.h";

    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = source_name,
        .data = "CONFIG_ZIGUX_LINE_CONTINUATION_SOURCE_SHOULD_NOT_PARSE\n",
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, source_name) catch {};

    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = lf_header_name,
        .data = "CONFIG_ZIGUX_LINE_CONTINUATION_LF CONFIG_ZIGUX_LINE_CONTINUATION_SHARED\n",
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, lf_header_name) catch {};

    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = second_header_name,
        .data = "CONFIG_ZIGUX_LINE_CONTINUATION_SECOND_MODULE CONFIG_ZIGUX_LINE_CONTINUATION_SHARED\n",
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, second_header_name) catch {};

    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = depfile_name,
        .data = "line_continuation.o: zigux_fixdep_line_continuation_source.rmeta \\\n" ++
            " zigux_fixdep_line_continuation_lf.h \\\n" ++
            " zigux_fixdep_line_continuation_second.h \\\n" ++
            " zigux_fixdep_line_continuation_lf.h\n",
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, depfile_name) catch {};

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_name,
        "line_continuation.o",
        "clang -MMD -MF zigux_fixdep_line_continuation_config_test.d",
    );

    try std.testing.expectEqualStrings(
        "savedcmd_line_continuation.o := clang -MMD -MF zigux_fixdep_line_continuation_config_test.d\n\n" ++
            "source_line_continuation.o := zigux_fixdep_line_continuation_source.rmeta\n\n" ++
            "deps_line_continuation.o := \\\n" ++
            "  zigux_fixdep_line_continuation_lf.h \\\n" ++
            "    $(wildcard include/config/ZIGUX_LINE_CONTINUATION_LF) \\\n" ++
            "    $(wildcard include/config/ZIGUX_LINE_CONTINUATION_SHARED) \\\n" ++
            "  zigux_fixdep_line_continuation_second.h \\\n" ++
            "    $(wildcard include/config/ZIGUX_LINE_CONTINUATION_SECOND) \\\n" ++
            "\n" ++
            "line_continuation.o: $(deps_line_continuation.o)\n\n" ++
            "$(deps_line_continuation.o):\n",
        capture.list.items,
    );
}
