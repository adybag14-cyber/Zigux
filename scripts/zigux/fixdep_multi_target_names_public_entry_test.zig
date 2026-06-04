const std = @import("std");
const Io = std.Io;
const fixdep = @import("fixdep.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 256),
            .allocator = allocator,
        };
    }

    fn deinit(self: *Capture) void {
        self.list.deinit(self.allocator);
    }

    pub fn print(self: *Capture, comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.list.appendSlice(self.allocator, rendered);
    }

    pub fn flush(_: *Capture) !void {}
};

fn writeFixture(path: []const u8, contents: []const u8) !void {
    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = path,
        .data = contents,
    });
}

test "runFixdep ignores multiple depfile target names before the dependency list" {
    const depfile_path = "zigux_fixdep_multi_target_names_test.d";
    const source_path = "zigux_fixdep_multi_target_names_source.c";
    const header_path = "zigux_fixdep_multi_target_names_header.h";
    const sentinel_path = "zigux_fixdep_multi_target_names_sentinel.so";

    try writeFixture(source_path, "int main(void) { return CONFIG_ZIGUX_MULTI_SOURCE; }\n");
    defer Io.Dir.cwd().deleteFile(std.testing.io, source_path) catch {};
    try writeFixture(header_path, "#define VALUE CONFIG_ZIGUX_MULTI_HEADER_MODULE\n");
    defer Io.Dir.cwd().deleteFile(std.testing.io, header_path) catch {};
    try writeFixture(sentinel_path, "CONFIG_ZIGUX_MULTI_SO_SHOULD_NOT_PARSE\n");
    defer Io.Dir.cwd().deleteFile(std.testing.io, sentinel_path) catch {};
    try writeFixture(
        depfile_path,
        "build/first-target.o build/second-target.o: " ++
            source_path ++ " " ++ header_path ++ " " ++ sentinel_path ++ "\n",
    );
    defer Io.Dir.cwd().deleteFile(std.testing.io, depfile_path) catch {};

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "build/requested-target.o",
        "cc -c " ++ source_path ++ " -o build/requested-target.o",
    );

    const output = capture.list.items;
    try std.testing.expectEqualStrings(
        "savedcmd_build/requested-target.o := cc -c " ++ source_path ++ " -o build/requested-target.o\n\n" ++
            "source_build/requested-target.o := " ++ source_path ++ "\n\n" ++
            "deps_build/requested-target.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_MULTI_SOURCE) \\\n" ++
            "  " ++ header_path ++ " \\\n" ++
            "    $(wildcard include/config/ZIGUX_MULTI_HEADER) \\\n" ++
            "  " ++ sentinel_path ++ " \\\n" ++
            "\n" ++
            "build/requested-target.o: $(deps_build/requested-target.o)\n\n" ++
            "$(deps_build/requested-target.o):\n",
        output,
    );

    try std.testing.expect(std.mem.indexOf(u8, output, "source_build/first-target.o") == null);
    try std.testing.expect(std.mem.indexOf(u8, output, "deps_build/second-target.o") == null);
    try std.testing.expect(std.mem.indexOf(u8, output, "ZIGUX_MULTI_SO_SHOULD_NOT_PARSE") == null);
}
