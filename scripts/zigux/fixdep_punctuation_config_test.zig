const std = @import("std");
const fixdep = @import("fixdep.zig");

fn relTmpPath(allocator: std.mem.Allocator, tmp: std.testing.TmpDir, name: []const u8) ![]u8 {
    return std.fmt.allocPrint(allocator, ".zig-cache/tmp/{s}/{s}", .{ tmp.sub_path[0..], name });
}

test "runFixdep keeps punctuation-delimited CONFIG tokens while ignoring prefixed ones" {
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

    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const allocator = std.testing.allocator;
    const depfile_path = try relTmpPath(allocator, tmp, "sample.d");
    defer allocator.free(depfile_path);
    const source_path = try relTmpPath(allocator, tmp, "sample_source.c");
    defer allocator.free(source_path);

    const depfile_text = try std.fmt.allocPrint(
        allocator,
        "sample.o: {s}\n",
        .{source_path},
    );
    defer allocator.free(depfile_text);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample.d",
        .data = depfile_text,
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_source.c",
        .data = "(CONFIG_ZIGUX_WRAP) HELLO_CONFIG_ZIGUX_SKIP + CONFIG_ZIGUX_AFTER_MODULE\n",
    });

    var capture = try Capture.init(allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "sample.o",
        "clang -c sample_source.c -o sample.o",
    );

    const expected = try std.fmt.allocPrint(
        allocator,
        "savedcmd_sample.o := clang -c sample_source.c -o sample.o\n\n" ++
            "source_sample.o := {s}\n\n" ++
            "deps_sample.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_WRAP) \\\n" ++
            "    $(wildcard include/config/ZIGUX_AFTER) \\\n" ++
            "\n" ++
            "sample.o: $(deps_sample.o)\n\n" ++
            "$(deps_sample.o):\n",
        .{source_path},
    );
    defer allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}
