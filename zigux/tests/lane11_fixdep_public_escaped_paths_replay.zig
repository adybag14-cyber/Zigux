const std = @import("std");
const Io = std.Io;

const fixdep = @import("fixdep");

test "fixdep public entry unescapes colon and hash dependency paths" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 768),
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

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "source:main.c",
        .data = "CONFIG_ZIGUX_ESCAPED_SOURCE CONFIG_ZIGUX_ESCAPED_SOURCE_MODULE\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "shared#config.h",
        .data = "CONFIG_ZIGUX_ESCAPED_HASH CONFIG_ZIGUX_ESCAPED_HASH_MODULE\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "dep:crate#feature.h",
        .data = "CONFIG_ZIGUX_ESCAPED_MIXED CONFIG_ZIGUX_ESCAPED_SOURCE\n",
    });

    const root = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(root);

    const source_path = try std.fmt.allocPrint(std.testing.allocator, "{s}/source:main.c", .{root});
    defer std.testing.allocator.free(source_path);
    const hash_path = try std.fmt.allocPrint(std.testing.allocator, "{s}/shared#config.h", .{root});
    defer std.testing.allocator.free(hash_path);
    const mixed_path = try std.fmt.allocPrint(std.testing.allocator, "{s}/dep:crate#feature.h", .{root});
    defer std.testing.allocator.free(mixed_path);
    const depfile_path = try std.fmt.allocPrint(std.testing.allocator, "{s}/sample.d", .{root});
    defer std.testing.allocator.free(depfile_path);

    const escaped_source_path = try std.fmt.allocPrint(std.testing.allocator, "{s}/source\\:main.c", .{root});
    defer std.testing.allocator.free(escaped_source_path);
    const escaped_hash_path = try std.fmt.allocPrint(std.testing.allocator, "{s}/shared\\#config.h", .{root});
    defer std.testing.allocator.free(escaped_hash_path);
    const escaped_mixed_path = try std.fmt.allocPrint(std.testing.allocator, "{s}/dep\\:crate\\#feature.h", .{root});
    defer std.testing.allocator.free(escaped_mixed_path);

    const depfile = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample.o: {s} {s} {s}\n",
        .{ escaped_source_path, escaped_hash_path, escaped_mixed_path },
    );
    defer std.testing.allocator.free(depfile);
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample.d",
        .data = depfile,
    });

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "sample.o",
        "cc -Wp,-MMD,sample.d -c source:main.c",
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample.o := cc -Wp,-MMD,sample.d -c source:main.c\n\n" ++
            "source_sample.o := {s}\n\n" ++
            "deps_sample.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_ESCAPED_SOURCE) \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_ESCAPED_HASH) \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_ESCAPED_MIXED) \\\n" ++
            "\n" ++
            "sample.o: $(deps_sample.o)\n\n" ++
            "$(deps_sample.o):\n",
        .{ source_path, hash_path, mixed_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}
