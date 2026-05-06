const std = @import("std");
const Io = std.Io;

pub const Request = struct {
    raw_args: []const []const u8,
    rendered_args: []const []const u8,
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

pub const ParseFailure = union(enum) {
    invalid_option: []const u8,
    missing_option_argument: []const u8,
    unexpected_option_argument: []const u8,
};

pub const ParseOutcome = union(enum) {
    command: Command,
    failure: ParseFailure,
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

const LongOptionKind = enum {
    help,
    version,
    debug,
    warnings,
    quiet,
    dump,
    reference,
    dump_types,
    preserve,
};

const LongOptionSpec = struct {
    name: []const u8,
    failure_name: []const u8,
    kind: LongOptionKind,
    takes_argument: bool = false,
};

const long_option_specs = [_]LongOptionSpec{
    .{ .name = "help", .failure_name = "--help", .kind = .help },
    .{ .name = "version", .failure_name = "--version", .kind = .version },
    .{ .name = "debug", .failure_name = "--debug", .kind = .debug },
    .{ .name = "warnings", .failure_name = "--warnings", .kind = .warnings },
    .{ .name = "quiet", .failure_name = "--quiet", .kind = .quiet },
    .{ .name = "dump", .failure_name = "--dump", .kind = .dump },
    .{ .name = "reference", .failure_name = "--reference", .kind = .reference, .takes_argument = true },
    .{ .name = "dump-types", .failure_name = "--dump-types", .kind = .dump_types, .takes_argument = true },
    .{ .name = "preserve", .failure_name = "--preserve", .kind = .preserve },
};

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

fn writeInvalidOptionError(writer: anytype, option: []const u8) !void {
    if (std.mem.startsWith(u8, option, "--")) {
        try writer.print("unrecognized option '{s}'\n", .{option});
        return;
    }

    const rendered = if (option.len == 0) "?" else option[0..1];
    try writer.print("invalid option -- '{s}'\n", .{rendered});
}

fn writeMissingOptionArgumentError(writer: anytype, option: []const u8) !void {
    if (std.mem.startsWith(u8, option, "--")) {
        try writer.print("option '{s}' requires an argument\n", .{option});
        return;
    }

    const rendered = if (option.len == 0) "?" else option[0..1];
    try writer.print("option requires an argument -- '{s}'\n", .{rendered});
}

fn writeUnexpectedOptionArgumentError(writer: anytype, option: []const u8) !void {
    if (std.mem.startsWith(u8, option, "--")) {
        try writer.print("option '{s}' doesn't allow an argument\n", .{option});
        return;
    }

    const rendered = if (option.len == 0) "?" else option[0..1];
    try writer.print("option doesn't allow an argument -- '{s}'\n", .{rendered});
}

pub fn renderGenksymsBridge(writer: anytype, request: Request) !void {
    try writer.writeAll("{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\"");
    for (request.rendered_args) |arg| {
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

const ParseAction = union(enum) {
    none,
    command: Command,
    failure: ParseFailure,
};

fn resolveLongOption(name: []const u8) ?LongOptionSpec {
    var prefix_match: ?LongOptionSpec = null;
    var prefix_count: usize = 0;
    for (long_option_specs) |spec| {
        if (std.mem.eql(u8, name, spec.name)) return spec;
        if (std.mem.startsWith(u8, spec.name, name)) {
            prefix_match = spec;
            prefix_count += 1;
        }
    }
    if (prefix_count == 1) return prefix_match;
    return null;
}

fn parseLongOption(
    allocator: std.mem.Allocator,
    args: []const []const u8,
    index: *usize,
    request: *Request,
    references: *std.ArrayList([]const u8),
) !ParseAction {
    const arg = args[index.*];
    const name_end = std.mem.indexOfScalar(u8, arg, '=') orelse arg.len;
    const option = resolveLongOption(arg[2..name_end]) orelse {
        return .{ .failure = .{ .invalid_option = arg } };
    };
    const inline_value = if (name_end < arg.len) arg[name_end + 1 ..] else null;

    if (inline_value != null and !option.takes_argument) {
        return .{ .failure = .{ .unexpected_option_argument = option.failure_name } };
    }

    switch (option.kind) {
        .help => return .{ .command = .help },
        .version => return .{ .command = .version },
        .debug => {
            request.debug_level += 1;
            return .none;
        },
        .warnings => {
            request.warnings = true;
            return .none;
        },
        .quiet => {
            request.warnings = false;
            return .none;
        },
        .dump => {
            request.dump_defs = true;
            return .none;
        },
        .preserve => {
            request.preserve = true;
            return .none;
        },
        .reference, .dump_types => {
            const value = inline_value orelse blk: {
                if (index.* + 1 >= args.len) {
                    return .{ .failure = .{ .missing_option_argument = option.failure_name } };
                }
                index.* += 1;
                break :blk args[index.*];
            };
            if (option.kind == .reference) {
                try references.append(allocator, value);
            } else {
                request.dump_types_file = value;
            }
            return .none;
        },
    }
}

fn parseShortOptions(
    allocator: std.mem.Allocator,
    args: []const []const u8,
    index: *usize,
    request: *Request,
    references: *std.ArrayList([]const u8),
) !ParseAction {
    const arg = args[index.*];
    var short_index: usize = 1;
    while (short_index < arg.len) : (short_index += 1) {
        switch (arg[short_index]) {
            'h' => return .{ .command = .help },
            'V' => return .{ .command = .version },
            'd' => request.debug_level += 1,
            'w' => request.warnings = true,
            'q' => request.warnings = false,
            'D' => request.dump_defs = true,
            'p' => request.preserve = true,
            'r', 'T' => {
                const option = arg[short_index];
                const inline_value = arg[short_index + 1 ..];
                const value = if (inline_value.len != 0) inline_value else blk: {
                    if (index.* + 1 >= args.len) {
                        return .{ .failure = .{ .missing_option_argument = arg[short_index .. short_index + 1] } };
                    }
                    index.* += 1;
                    break :blk args[index.*];
                };
                if (option == 'r') {
                    try references.append(allocator, value);
                } else {
                    request.dump_types_file = value;
                }
                return .none;
            },
            else => return .{ .failure = .{ .invalid_option = arg[short_index .. short_index + 1] } },
        }
    }
    return .none;
}

pub fn parseArgs(allocator: std.mem.Allocator, args: []const []const u8) !ParseOutcome {
    var request = Request{ .raw_args = args, .rendered_args = &.{} };
    var references = std.ArrayList([]const u8).empty;
    var rendered_args = std.ArrayList([]const u8).empty;
    var positional_args = std.ArrayList([]const u8).empty;
    defer references.deinit(allocator);
    defer rendered_args.deinit(allocator);
    defer positional_args.deinit(allocator);

    var index: usize = 0;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--")) {
            try rendered_args.appendSlice(allocator, positional_args.items);
            try rendered_args.append(allocator, arg);
            if (index + 1 < args.len) {
                try rendered_args.appendSlice(allocator, args[index + 1 ..]);
            }
            break;
        }
        if (arg.len == 0 or arg[0] != '-') {
            try positional_args.append(allocator, arg);
            continue;
        }
        if (std.mem.startsWith(u8, arg, "--")) {
            const long_option_index = index;
            switch (try parseLongOption(allocator, args, &index, &request, &references)) {
                .none => {
                    try rendered_args.append(allocator, arg);
                    if (index != long_option_index and index < args.len) {
                        try rendered_args.append(allocator, args[index]);
                    }
                },
                .command => |command| return .{ .command = command },
                .failure => |failure| return .{ .failure = failure },
            }
        } else {
            switch (try parseShortOptions(allocator, args, &index, &request, &references)) {
                .none => {
                    try rendered_args.append(allocator, arg);
                    if (std.mem.eql(u8, arg, "-r") or std.mem.eql(u8, arg, "-T")) {
                        if (index > 0 and index < args.len) {
                            try rendered_args.append(allocator, args[index]);
                        }
                    }
                },
                .command => |command| return .{ .command = command },
                .failure => |failure| return .{ .failure = failure },
            }
        }
    }

    if (index >= args.len) {
        try rendered_args.appendSlice(allocator, positional_args.items);
    }

    request.rendered_args = try rendered_args.toOwnedSlice(allocator);
    request.reference_files = try references.toOwnedSlice(allocator);
    return .{ .command = .{ .request = request } };
}

pub fn main(init: std.process.Init) !void {
    const arena = init.arena.allocator();
    const io = init.io;
    const args = try init.minimal.args.toSlice(arena);

    const outcome = parseArgs(arena, args[1..]) catch |err| {
        var stderr_buffer: [512]u8 = undefined;
        var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
        try stderr_writer.interface.print("genksyms: internal parse failure: {s}\n", .{@errorName(err)});
        try stderr_writer.interface.flush();
        std.process.exit(1);
    };

    const command = switch (outcome) {
        .command => |command| command,
        .failure => |failure| {
            var stderr_buffer: [512]u8 = undefined;
            var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
            switch (failure) {
                .invalid_option => |option| try writeInvalidOptionError(&stderr_writer.interface, option),
                .missing_option_argument => |option| try writeMissingOptionArgumentError(&stderr_writer.interface, option),
                .unexpected_option_argument => |option| try writeUnexpectedOptionArgumentError(&stderr_writer.interface, option),
            }
            try stderr_writer.interface.flush();
            std.process.exit(1);
        },
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
    const outcome = try parseArgs(std.testing.allocator, &.{ "-d", "-d", "-D", "-w", "-p", "-r", "foo.symref", "-rbar.symref", "-T", "out.symtypes" });
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                defer std.testing.allocator.free(request.reference_files);
                defer std.testing.allocator.free(request.rendered_args);
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
        },
        .failure => return error.UnexpectedFailure,
    }
}

test "genksyms bridge parses long options and quiet override" {
    const outcome = try parseArgs(std.testing.allocator, &.{ "--debug", "--warnings", "--quiet", "--reference=foo.symref", "--dump-types", "types.symtypes", "--preserve" });
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                defer std.testing.allocator.free(request.reference_files);
                defer std.testing.allocator.free(request.rendered_args);
                try std.testing.expectEqual(@as(usize, 1), request.debug_level);
                try std.testing.expect(!request.warnings);
                try std.testing.expect(request.preserve);
                try std.testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);
                try std.testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try std.testing.expectEqualStrings("foo.symref", request.reference_files[0]);
            },
            else => return error.UnexpectedCommand,
        },
        .failure => return error.UnexpectedFailure,
    }
}

test "genksyms bridge accepts unambiguous abbreviated long options" {
    const args = &.{ "--deb", "--warn", "--qui", "--ref=foo.symref", "--dump-t", "types.symtypes", "--pres" };
    const outcome = try parseArgs(std.testing.allocator, args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                defer std.testing.allocator.free(request.reference_files);
                defer std.testing.allocator.free(request.rendered_args);
                try std.testing.expectEqual(@as(usize, 1), request.debug_level);
                try std.testing.expect(!request.warnings);
                try std.testing.expect(request.preserve);
                try std.testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);
                try std.testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try std.testing.expectEqualStrings("foo.symref", request.reference_files[0]);
                try std.testing.expectEqualSlices([]const u8, args, request.rendered_args);
            },
            else => return error.UnexpectedCommand,
        },
        .failure => return error.UnexpectedFailure,
    }
}

test "genksyms bridge canonicalizes unexpected long option argument failures" {
    const outcome = try parseArgs(std.testing.allocator, &.{"--hel=topic"});
    switch (outcome) {
        .failure => |failure| switch (failure) {
            .unexpected_option_argument => |option| try std.testing.expectEqualStrings("--help", option),
            else => return error.UnexpectedFailure,
        },
        .command => return error.UnexpectedCommand,
    }
}

test "genksyms bridge accepts explicit option terminator" {
    const args = &.{ "--debug", "--", "--leftover", "positional" };
    const outcome = try parseArgs(std.testing.allocator, args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                defer std.testing.allocator.free(request.reference_files);
                defer std.testing.allocator.free(request.rendered_args);
                try std.testing.expectEqual(@as(usize, 1), request.debug_level);
                try std.testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try std.testing.expectEqualSlices([]const u8, args, request.raw_args);
                try std.testing.expectEqualSlices([]const u8, args, request.rendered_args);
            },
            else => return error.UnexpectedCommand,
        },
        .failure => return error.UnexpectedFailure,
    }
}

test "genksyms bridge reports invalid short option in getopt style" {
    const outcome = try parseArgs(std.testing.allocator, &.{"-x"});
    switch (outcome) {
        .failure => |failure| switch (failure) {
            .invalid_option => |option| try std.testing.expectEqualStrings("x", option),
            else => return error.UnexpectedFailure,
        },
        .command => return error.UnexpectedCommand,
    }
}

test "genksyms bridge reports missing short option argument in getopt style" {
    const outcome = try parseArgs(std.testing.allocator, &.{"-r"});
    switch (outcome) {
        .failure => |failure| switch (failure) {
            .missing_option_argument => |option| try std.testing.expectEqualStrings("r", option),
            else => return error.UnexpectedFailure,
        },
        .command => return error.UnexpectedCommand,
    }
}

test "genksyms bridge renders normalized invocation plan" {
    const request = Request{
        .raw_args = &.{ "-d", "-r", "foo.symref" },
        .rendered_args = &.{ "-d", "-r", "foo.symref" },
        .debug_level = 1,
        .reference_files = &.{"foo.symref"},
    };
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,
        fn init(allocator: std.mem.Allocator) !@This() {
            return .{ .list = try std.ArrayList(u8).initCapacity(allocator, 256), .allocator = allocator };
        }
        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }
        fn writeAll(self: *@This(), bytes: []const u8) !void {
            try self.list.appendSlice(self.allocator, bytes);
        }
        fn writeByte(self: *@This(), byte: u8) !void {
            try self.list.append(self.allocator, byte);
        }
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

test "genksyms bridge ignores positional args while still parsing later options" {
    const args = &.{ "leftover.c", "-d", "rightover.h", "-r", "foo.symref" };
    const outcome = try parseArgs(std.testing.allocator, args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                defer std.testing.allocator.free(request.reference_files);
                defer std.testing.allocator.free(request.rendered_args);
                try std.testing.expectEqual(@as(usize, 1), request.debug_level);
                try std.testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try std.testing.expectEqualStrings("foo.symref", request.reference_files[0]);
                try std.testing.expectEqualSlices([]const u8, args, request.raw_args);
                try std.testing.expectEqualSlices([]const u8, &.{ "-d", "-r", "foo.symref", "leftover.c", "rightover.h" }, request.rendered_args);
            },
            else => return error.UnexpectedCommand,
        },
        .failure => return error.UnexpectedFailure,
    }
}
