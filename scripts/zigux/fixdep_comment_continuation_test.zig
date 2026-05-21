const std = @import("std");
const fixdep = @import("fixdep.zig");

test "runFixdep ignores escaped-newline comments before the first real target" {
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
        "{s}/sample_comment_continuation_source.rmeta",
        .{base_path},
    );
    defer std.testing.allocator.free(source_path);

    const dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_comment_continuation_dep.so",
        .{base_path},
    );
    defer std.testing.allocator.free(dep_path);

    const config_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_comment_continuation-config.h",
        .{base_path},
    );
    defer std.testing.allocator.free(config_dep_path);

    const later_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_comment_continuation_later_dep.so",
        .{base_path},
    );
    defer std.testing.allocator.free(later_dep_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_comment_continuation.d",
        .{base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        std.testing.allocator,
        "clang -c {s} -o sample_comment_continuation.o",
        .{source_path},
    );
    defer std.testing.allocator.free(cmdline);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_comment_continuation-config.h",
        .data = "#define CONFIG_ZIGUX_COMMENT_CONTINUATION_MODULE 1\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_comment_continuation_later_dep.so",
        .data = "",
    });

    const depfile_text = try std.fmt.allocPrint(
        std.testing.allocator,
        "# rustc note \\\ncontinues across lines \\\nuntil the first real newline\n" ++
            "sample_comment_continuation.o: {s} \\\n {s} \\\n {s}\n" ++
            "sample_comment_continuation.o: ignored_second_source.rmeta {s}\n",
        .{ source_path, dep_path, config_dep_path, later_dep_path },
    );
    defer std.testing.allocator.free(depfile_text);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_comment_continuation.d",
        .data = depfile_text,
    });

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "sample_comment_continuation.o",
        cmdline,
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample_comment_continuation.o := {s}\n\n" ++
            "source_sample_comment_continuation.o := {s}\n\n" ++
            "deps_sample_comment_continuation.o := \\\n" ++
            "  {s} \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_COMMENT_CONTINUATION) \\\n" ++
            "  {s} \\\n" ++
            "\n" ++
            "sample_comment_continuation.o: $(deps_sample_comment_continuation.o)\n\n" ++
            "$(deps_sample_comment_continuation.o):\n",
        .{ cmdline, source_path, dep_path, config_dep_path, later_dep_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}
