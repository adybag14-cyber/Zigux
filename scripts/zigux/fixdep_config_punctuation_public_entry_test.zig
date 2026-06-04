const std = @import("std");
const fixdep = @import("fixdep.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 512),
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

test "runFixdep parses punctuation-delimited CONFIG tokens from real dependencies" {
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
        "{s}/punct_source.c",
        .{base_path},
    );
    defer std.testing.allocator.free(source_path);

    const header_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/punct_header.h",
        .{base_path},
    );
    defer std.testing.allocator.free(header_path);

    const no_parse_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/punct_payload.so",
        .{base_path},
    );
    defer std.testing.allocator.free(no_parse_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/punctuation.d",
        .{base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        std.testing.allocator,
        "clang -c {s} -o punctuation.o",
        .{source_path},
    );
    defer std.testing.allocator.free(cmdline);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "punct_source.c",
        .data =
        \\int zigux_fixdep_punctuation(void) {
        \\    return CONFIG_ZIGUX_PARENTHESIS + (CONFIG_ZIGUX_COMMA_MODULE);
        \\}
        \\
        ,
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "punct_header.h",
        .data =
        \\#define ZIGUX_PUNCT_SET { CONFIG_ZIGUX_BRACE, CONFIG_ZIGUX_SEMICOLON_MODULE; }
        \\#define ZIGUX_PUNCT_DASH CONFIG_ZIGUX_DASH - CONFIG_ZIGUX_DOT.
        \\
        ,
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "punct_payload.so",
        .data = "CONFIG_ZIGUX_SO_SHOULD_NOT_PARSE\n",
    });

    const depfile_text = try std.fmt.allocPrint(
        std.testing.allocator,
        "punctuation.o: {s} {s} {s}\n",
        .{ source_path, header_path, no_parse_path },
    );
    defer std.testing.allocator.free(depfile_text);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "punctuation.d",
        .data = depfile_text,
    });

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "punctuation.o",
        cmdline,
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_punctuation.o := {s}\n\n" ++
            "source_punctuation.o := {s}\n\n" ++
            "deps_punctuation.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_PARENTHESIS) \\\n" ++
            "    $(wildcard include/config/ZIGUX_COMMA) \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_BRACE) \\\n" ++
            "    $(wildcard include/config/ZIGUX_SEMICOLON) \\\n" ++
            "    $(wildcard include/config/ZIGUX_DASH) \\\n" ++
            "    $(wildcard include/config/ZIGUX_DOT) \\\n" ++
            "  {s} \\\n" ++
            "\n" ++
            "punctuation.o: $(deps_punctuation.o)\n\n" ++
            "$(deps_punctuation.o):\n",
        .{ cmdline, source_path, header_path, no_parse_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}
