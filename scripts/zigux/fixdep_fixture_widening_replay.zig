const std = @import("std");
const fixdep = @import("fixdep.zig");

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

fn expectFixdepReplay(
    depfile_name: []const u8,
    depfile_contents: []const u8,
    target: []const u8,
    cmdline: []const u8,
    expected_output: []const u8,
) !void {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = depfile_name,
        .data = depfile_contents,
    });

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/{s}",
        .{ tmp.sub_path[0..], depfile_name },
    );
    defer std.testing.allocator.free(depfile_path);

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        target,
        cmdline,
    );

    try std.testing.expectEqualStrings(expected_output, capture.list.items);
}

test "fixdep fixture replay keeps ignored autoconf hops out of widened escaped-space fixtures" {
    try expectFixdepReplay(
        "sample_escaped_space.d",
        "sample_escaped_space.o: zigux/tests/fixtures/fixdep/sample_escaped_space_source.rmeta \\\n" ++
            " zigux/tests/fixtures/fixdep/dep\\ name.rmeta \\\n" ++
            " include/generated/autoconf.h \\\n" ++
            " zigux/tests/fixtures/fixdep/dep\\ name.rmeta\n",
        "sample_escaped_space.o",
        "clang -c zigux/tests/fixtures/fixdep/sample_escaped_space_source.c -o sample_escaped_space.o",
        "savedcmd_sample_escaped_space.o := clang -c zigux/tests/fixtures/fixdep/sample_escaped_space_source.c -o sample_escaped_space.o\n\n" ++
            "source_sample_escaped_space.o := zigux/tests/fixtures/fixdep/sample_escaped_space_source.rmeta\n\n" ++
            "deps_sample_escaped_space.o := \\\n" ++
            "  zigux/tests/fixtures/fixdep/dep\\ name.rmeta \\\n" ++
            "\n" ++
            "sample_escaped_space.o: $(deps_sample_escaped_space.o)\n\n" ++
            "$(deps_sample_escaped_space.o):\n",
    );
}

test "fixdep fixture replay keeps escaped colons literal across widened repeated dependency tails" {
    try expectFixdepReplay(
        "sample_escaped_colon.d",
        "sample_escaped_colon.o: zigux/tests/fixtures/fixdep/sample_escaped_colon_source.rmeta \\\n" ++
            " zigux/tests/fixtures/fixdep/dep\\:colon.so \\\n" ++
            " include/generated/autoconf.h \\\n" ++
            " zigux/tests/fixtures/fixdep/dep\\:colon.so\n",
        "sample_escaped_colon.o",
        "clang -c zigux/tests/fixtures/fixdep/sample_escaped_colon_source.c -o sample_escaped_colon.o",
        "savedcmd_sample_escaped_colon.o := clang -c zigux/tests/fixtures/fixdep/sample_escaped_colon_source.c -o sample_escaped_colon.o\n\n" ++
            "source_sample_escaped_colon.o := zigux/tests/fixtures/fixdep/sample_escaped_colon_source.rmeta\n\n" ++
            "deps_sample_escaped_colon.o := \\\n" ++
            "  zigux/tests/fixtures/fixdep/dep:colon.so \\\n" ++
            "\n" ++
            "sample_escaped_colon.o: $(deps_sample_escaped_colon.o)\n\n" ++
            "$(deps_sample_escaped_colon.o):\n",
    );
}
