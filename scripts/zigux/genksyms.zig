const std = @import("std");
const Io = std.Io;

pub const Request = struct {
    raw_args: []const []const u8,
    debug_level: usize = 0,
    warnings: bool = false,
    dump_defs: bool = false,
    preserve: bool = false,
    reference_files: []const []const u8 = &.{},
    dump_types_file: ?[]const u8 = null,
};

pub const Command = union(enum) {
    help,
    version,
    request: Request,
};

const usage_text =
    "Usage:\n" ++
    "genksyms [-adDTwqhVR] > /path/to/.tmp_obj.ver\n" ++
    "\n" ++
    "  -d, --debug           Increment the debug level (repeatable)\n" ++
    "  -D, --dump            Dump expanded symbol defs (for debugging only)\n" ++
    "  -r, --reference file  Read reference symbols from a file\n" ++
    "  -T, --dump-types file Dump expanded types into file\n" ++
    "  -p, --preserve        Preserve reference modversions or fail\n" ++
    "  -w, --warnings        Enable warnings\n" ++
    "  -q, --quiet           Disable warnings (default)\n" ++
    "  -h, --help            Print this message\n" ++
    "  -V, --version         Print the release version\n";

const version_text = "genksyms version 2.5.60\n";

fn writeJsonEscaped(writer: anytype, text: []const u8) !void {
    for (text) |c| switch (c) {
        '\\' => try writer.writeAll("\\\\"),
        '"' => try writer.writeAll("\\\""),
        '\n' => try writer.writeAll("\\n"),
        '\r' => try writer.writeAll("\\r"),
        '\t' => try writer.writeAll("\\t"),
        else => try writer.writeByte(c),
    };
}

fn writeJsonArray(writer: anytype, values: []const []const u8) !void {
    try writer.writeByte('[');
    for (values, 0..) |value, index| {
        if (index != 0) try writer.writeByte(',');
        try writer.writeByte('"');
        try writeJsonEscaped(writer, value);
        try writer.writeByte('"');
    }
    try writer.writeByte(']');
}

pub fn renderGenksymsBridge(writer: anytype, request: Request) !void {
    try writer.writeAll("{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\"");
    for (request.raw_args) |arg| {
        try writer.writeByte(',');
        try writer.writeByte('"');
        try writeJsonEscaped(writer, arg);
        try writer.writeByte('"');
    }
    try writer.writeAll("],\"options\":{\"debug_level\":");
    try writer.print("{d}", .{request.debug_level});
    try writer.writeAll(",\"warnings\":");
    try writer.writeAll(if (request.warnings) "true" else "false");
    try writer.writeAll(",\"dump_defs\":");
    try writer.writeAll(if (request.dump_defs) "true" else "false");
    try writer.writeAll(",\"preserve\":");
    try writer.writeAll(if (request.preserve) "true" else "false");
    try writer.writeAll(",\"reference_files\":");
    try writeJsonArray(writer, request.reference_files);
    try writer.writeAll(",\"dump_types_file\":");
    if (request.dump_types_file) |file| {
        try writer.writeByte('"');
        try writeJsonEscaped(writer, file);
        try writer.writeByte('"');
    } else {
        try writer.writeAll("null");
    }
    try writer.writeAll("}}\n");
}

fn parseLongOption(allocator: std.mem.Allocator, args: []const []const u8, index: *usize, request: *Request, references: *std.ArrayList([]const u8)) !?Command {
    const arg = args[index.*];
    if (std.mem.eql(u8, arg, "--help")) return .help;
    if (std.mem.eql(u8, arg, "--version")) return .version;
    if (std.mem.eql(u8, arg, "--debug")) {
        request.debug_level += 1;
        return null;
    }
    if (std.mem.eql(u8, arg, "--warnings")) {
        request.warnings = true;
        return null;
    }
    if (std.mem.eql(u8, arg, "--quiet")) {
        request.warnings = false;
        return null;
    }
    if (std.mem.eql(u8, arg, "--dump")) {
        request.dump_defs = true;
        return null;
    }
    if (std.mem.eql(u8, arg, "--preserve")) {
        request.preserve = true;
        return null;
    }
    if (std.mem.startsWith(u8, arg, "--reference=")) {
        try references.append(allocator, arg["--reference=".len..]);
        return null;
    }
    if (std.mem.eql(u8, arg, "--reference")) {
        if (index.* + 1 >= args.len) return error.MissingOptionArgument;
        index.* += 1;
        try references.append(allocator, args[index.*]);
        return null;
    }
    if (std.mem.startsWith(u8, arg, "--dump-types=")) {
        request.dump_types_file = arg["--dump-types=".len..];
        return null;
    }
    if (std.mem.eql(u8, arg, "--dump-types")) {
        if (index.* + 1 >= args.len) return error.MissingOptionArgument;
        index.* += 1;
        request.dump_types_file = args[index.*];
        return null;
    }
    return error.InvalidOption;
}

fn parseShortOptions(allocator: std.mem.Allocator, args: []const []const u8, index: *usize, request: *Request, references: *std.ArrayList([]const u8)) !?Command {
    const arg = args[index.*];
    var short_index: usize = 1;
    while (short_index < arg.len) : (short_index += 1) {
        switch (arg[short_index]) {
            'h' => return .help,
            'V' => return .version,
            'd' => request.debug_level += 1,
            'w' => request.warnings = true,
            'q' => request.warnings = false,
            'D' => request.dump_defs = true,
            'p' => request.preserve = true,
            'r', 'T' => {
                const option = arg[short_index];
                const inline_value = arg[short_index + 1 ..];
                const value = if (inline_value.len != 0) inline_value else blk: {
                    if (index.* + 1 >= args.len) return error.MissingOptionArgument;
                    index.* += 1;
                    break :blk args[index.*];
                };
                if (option == 'r') {
                    try references.append(allocator, value);
                } else {
                    request.dump_types_file = value;
                }
                return null;
            },
            else => return error.InvalidOption,
        }
    }
    return null;
}

pub fn parseArgs(allocator: std.mem.Allocator, args: []const []const u8) !Command {
    var request = Request{ .raw_args = args };
    var references = std.ArrayList([]const u8).empty;
    defer references.deinit(allocator);

    var index: usize = 0;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (arg.len == 0 or arg[0] != '-') return error.InvalidOption;
        if (std.mem.startsWith(u8, arg, "--")) {
            if (try parseLongOption(allocator, args, &index, &request, &references)) |command| {
                return command;
            }
        } else {
            if (try parseShortOptions(allocator, args, &index, &request, &references)) |command| {
                return command;
            }
        }
    }

    request.reference_files = try references.toOwnedSlice(allocator);
    return .{ .request = request };
}

pub fn main(init: std.process.Init) !void {
    const arena = init.arena.allocator();
    const io = init.io;
    const args = try init.minimal.args.toSlice(arena);

    const command = parseArgs(arena, args[1..]) catch |err| {
        var stderr_buffer: [512]u8 = undefined;
        var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
        switch (err) {
            error.MissingOptionArgument => try stderr_writer.interface.writeAll("Error: missing genksyms option argument\n"),
            error.InvalidOption => try stderr_writer.interface.writeAll(usage_text),
            else => return err,
        }
        try stderr_writer.interface.flush();
        std.process.exit(1);
    };

    switch (command) {
        .help => {
            var stdout_buffer: [512]u8 = undefined;
            var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
            try stdout_writer.interface.writeAll(usage_text);
            try stdout_writer.interface.flush();
        },
        .version => {
            var stderr_buffer: [128]u8 = undefined;
            var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
            try stderr_writer.interface.writeAll(version_text);
            try stderr_writer.interface.flush();
        },
        .request => |request| {
            var stdout_buffer: [2048]u8 = undefined;
            var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
            try renderGenksymsBridge(&stdout_writer.interface, request);
            try stdout_writer.interface.flush();
        },
    }
}

test "genksyms bridge parses repeated short flags and arguments" {
    const command = try parseArgs(std.testing.allocator, &.{ "-d", "-d", "-D", "-w", "-p", "-r", "foo.symref", "-rbar.symref", "-T", "out.symtypes" });
    switch (command) {
        .request => |request| {
            defer std.testing.allocator.free(request.reference_files);
            try std.testing.expectEqual(@as(usize, 2), request.debug_level);
            try std.testing.expect(request.warnings);
            try std.testing.expect(request.dump_defs);
            try std.testing.expect(request.preserve);
            try std.testing.expectEqualStrings("out.symtypes", request.dump_types_file.?);
            try std.testing.expectEqual(@as(usize, 2), request.reference_files.len);
            try std.testing.expectEqualStrings("foo.symref", request.reference_files[0]);
            try std.testing.expectEqualStrings("bar.symref", request.reference_files[1]);
        },
        else => return error.UnexpectedCommand,
    }
}

test "genksyms bridge parses long options and quiet override" {
    const command = try parseArgs(std.testing.allocator, &.{ "--debug", "--warnings", "--quiet", "--reference=foo.symref", "--dump-types", "types.symtypes", "--preserve" });
    switch (command) {
        .request => |request| {
            defer std.testing.allocator.free(request.reference_files);
            try std.testing.expectEqual(@as(usize, 1), request.debug_level);
            try std.testing.expect(!request.warnings);
            try std.testing.expect(request.preserve);
            try std.testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);
            try std.testing.expectEqual(@as(usize, 1), request.reference_files.len);
            try std.testing.expectEqualStrings("foo.symref", request.reference_files[0]);
        },
        else => return error.UnexpectedCommand,
    }
}

test "genksyms bridge renders normalized invocation plan" {
    const request = Request{ .raw_args = &.{ "-d", "-r", "foo.symref" }, .debug_level = 1, .reference_files = &.{"foo.symref"} };
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,
        fn init(allocator: std.mem.Allocator) !@This() { return .{ .list = try std.ArrayList(u8).initCapacity(allocator, 256), .allocator = allocator }; }
        fn deinit(self: *@This()) void { self.list.deinit(self.allocator); }
        fn writeAll(self: *@This(), bytes: []const u8) !void { try self.list.appendSlice(self.allocator, bytes); }
        fn writeByte(self: *@This(), byte: u8) !void { try self.list.append(self.allocator, byte); }
        fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }
    };
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();
    try renderGenksymsBridge(&capture, request);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"tool\":\"scripts/genksyms/genksyms\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"debug_level\":1") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"reference_files\":[\"foo.symref\"]") != null);
}
