const std = @import("std");
const fixdep = @import("fixdep.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 640),
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

test "runFixdep keeps mixed escaped dependency paths and deduplicates shared configs" {
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
        "{s}/sample_mixed_escaped_source.c",
        .{base_path},
    );
    defer std.testing.allocator.free(source_path);

    const escaped_space_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/escaped\\ space-config.h",
        .{base_path},
    );
    defer std.testing.allocator.free(escaped_space_dep_path);

    const escaped_space_visible_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/escaped\\ space-config.h",
        .{base_path},
    );
    defer std.testing.allocator.free(escaped_space_visible_path);

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

    const escaped_colon_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/shared\\:config.h",
        .{base_path},
    );
    defer std.testing.allocator.free(escaped_colon_dep_path);

    const escaped_colon_visible_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/shared:config.h",
        .{base_path},
    );
    defer std.testing.allocator.free(escaped_colon_visible_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_mixed_escaped_paths.d",
        .{base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        std.testing.allocator,
        "clang -c {s} -o sample_mixed_escaped_paths.o",
        .{source_path},
    );
    defer std.testing.allocator.free(cmdline);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_mixed_escaped_source.c",
        .data = "int zigux_fixdep_sample_mixed_escaped_paths(void) { return 0; }\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "escaped\\ space-config.h",
        .data = "#define CONFIG_ZIGUX_SPACE_ONLY 1\n" ++
            "#define CONFIG_ZIGUX_SHARED_ESCAPED_MODULE 1\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "shared#config.h",
        .data = "#define CONFIG_ZIGUX_HASH_ONLY 1\n" ++
            "#define CONFIG_ZIGUX_SHARED_ESCAPED_MODULE 1\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "shared:config.h",
        .data = "#define CONFIG_ZIGUX_COLON_ONLY 1\n" ++
            "#define CONFIG_ZIGUX_SHARED_ESCAPED_MODULE 1\n",
    });

    const depfile_text = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample_mixed_escaped_paths.o: {s} \\\n {s} \\\n {s} \\\n {s} \\\n {s}\n",
        .{
            source_path,
            escaped_space_dep_path,
            escaped_hash_dep_path,
            escaped_colon_dep_path,
            escaped_hash_dep_path,
        },
    );
    defer std.testing.allocator.free(depfile_text);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_mixed_escaped_paths.d",
        .data = depfile_text,
    });

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "sample_mixed_escaped_paths.o",
        cmdline,
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample_mixed_escaped_paths.o := {s}\n\n" ++
            "source_sample_mixed_escaped_paths.o := {s}\n\n" ++
            "deps_sample_mixed_escaped_paths.o := \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_SPACE_ONLY) \\\n" ++
            "    $(wildcard include/config/ZIGUX_SHARED_ESCAPED) \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_HASH_ONLY) \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_COLON_ONLY) \\\n" ++
            "\n" ++
            "sample_mixed_escaped_paths.o: $(deps_sample_mixed_escaped_paths.o)\n\n" ++
            "$(deps_sample_mixed_escaped_paths.o):\n",
        .{
            cmdline,
            source_path,
            escaped_space_visible_path,
            escaped_hash_visible_path,
            escaped_colon_visible_path,
        },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}
