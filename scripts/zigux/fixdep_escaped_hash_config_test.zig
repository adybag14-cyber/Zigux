const std = @import("std");
const fixdep = @import("fixdep.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 384),
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

test "runFixdep reads escaped-hash dependency paths and deduplicates shared configs" {
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
        "{s}/sample_escaped_hash_source.c",
        .{base_path},
    );
    defer std.testing.allocator.free(source_path);

    const escaped_hash_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/shared\\#config.h",
        .{base_path},
    );
    defer std.testing.allocator.free(escaped_hash_dep_path);

    const escaped_hash_visible_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/shared#config.h",
        .{base_path},
    );
    defer std.testing.allocator.free(escaped_hash_visible_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_escaped_hash.d",
        .{base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        std.testing.allocator,
        "clang -c {s} -o sample_escaped_hash.o",
        .{source_path},
    );
    defer std.testing.allocator.free(cmdline);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_escaped_hash_source.c",
        .data = "int zigux_fixdep_sample_escaped_hash(void) { return 0; }\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "shared#config.h",
        .data = "#define CONFIG_ZIGUX_HASH 1\n" ++
            "#define CONFIG_ZIGUX_SHARED_HASH_MODULE 1\n" ++
            "#define CONFIG_ZIGUX_HASH 1\n",
    });

    const depfile_text = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample_escaped_hash.o: {s} \\\n {s} \\\n {s}\n",
        .{ source_path, escaped_hash_dep_path, escaped_hash_dep_path },
    );
    defer std.testing.allocator.free(depfile_text);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_escaped_hash.d",
        .data = depfile_text,
    });

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "sample_escaped_hash.o",
        cmdline,
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample_escaped_hash.o := {s}\n\n" ++
            "source_sample_escaped_hash.o := {s}\n\n" ++
            "deps_sample_escaped_hash.o := \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_HASH) \\\n" ++
            "    $(wildcard include/config/ZIGUX_SHARED_HASH) \\\n" ++
            "\n" ++
            "sample_escaped_hash.o: $(deps_sample_escaped_hash.o)\n\n" ++
            "$(deps_sample_escaped_hash.o):\n",
        .{ cmdline, source_path, escaped_hash_visible_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}
