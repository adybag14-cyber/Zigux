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
    version_count: usize = 0,
};

pub const Command = union(enum) {
    help: usize,
    version: usize,
    request: Request,
};

pub const ParseFailure = union(enum) {
    invalid_option: []const u8,
    ambiguous_option: []const u8,
    missing_option_argument: []const u8,
    unexpected_option_argument: []const u8,
    too_many_reference_files,
};

pub const ParsedFailure = struct {
    reason: ParseFailure,
    version_count: usize = 0,
};

pub const ParseOutcome = union(enum) {
    command: Command,
    failure: ParsedFailure,
};

const usage_text =
    "Usage:\n" ++
    "genksyms [-adDTwqhVR] > /path/to/.tmp_obj.ver\n" ++
    "\n" ++
    " -d, --debug Increment the debug level (repeatable)\n" ++
    " -D, --dump Dump expanded symbol defs (for debugging only)\n" ++
    " -r, --reference file Read reference symbols from a file\n" ++
    " -T, --dump-types file Dump expanded types into file\n" ++
    " -p, --preserve Preserve reference modversions or fail\n" ++
    " -w, --warnings Enable warnings\n" ++
    " -q, --quiet Disable warnings (default)\n" ++
    " -h, --help Print this message\n" ++
    " -V, --version Print the release version\n";

const version_text = "genksyms version 2.5.60\n";
const max_reference_files: usize = 16;

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

fn writeAmbiguousOptionError(writer: anytype, option: []const u8) !void {
    try writer.print("option '{s}' is ambiguous\n", .{option});
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

fn writeTooManyReferenceFilesError(writer: anytype) !void {
    try writer.writeAll("too many reference files\n");
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

const LongOptionResolution = union(enum) {
    none,
    ambiguous,
    match: LongOptionSpec,
};

fn resolveLongOption(name: []const u8) LongOptionResolution {
    var prefix_match: ?LongOptionSpec = null;
    var prefix_count: usize = 0;

    for (long_option_specs) |spec| {
        if (std.mem.eql(u8, name, spec.name)) return .{ .match = spec };
        if (std.mem.startsWith(u8, spec.name, name)) {
            prefix_match = spec;
            prefix_count += 1;
        }
    }

    if (prefix_count == 1) return .{ .match = prefix_match.? };
    if (prefix_count > 1) return .ambiguous;
    return .none;
}

fn isPureVersionLongOption(arg: []const u8) bool {
    if (!std.mem.startsWith(u8, arg, "--")) return false;

    const name_end = std.mem.indexOfScalar(u8, arg, '=') orelse arg.len;
    if (name_end < arg.len) return false;

    return switch (resolveLongOption(arg[2..name_end])) {
        .match => |spec| spec.kind == .version,
        else => false,
    };
}

fn isPureVersionShortCluster(arg: []const u8) bool {
    if (arg.len < 2 or arg[0] != '-' or std.mem.startsWith(u8, arg, "--")) return false;

    for (arg[1..]) |flag| {
        if (flag != 'V') return false;
    }
    return true;
}

fn appendReferenceFile(
    allocator: std.mem.Allocator,
    references: *std.ArrayList([]const u8),
    value: []const u8,
) !?ParseFailure {
    if (references.items.len >= max_reference_files) {
        return .too_many_reference_files;
    }
    try references.append(allocator, value);
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
    const option = switch (resolveLongOption(arg[2..name_end])) {
        .match => |spec| spec,
        .ambiguous => return .{ .failure = .{ .ambiguous_option = arg } },
        .none => return .{ .failure = .{ .invalid_option = arg } },
    };
    const inline_value = if (name_end < arg.len) arg[name_end + 1 ..] else null;
    if (inline_value != null and !option.takes_argument) {
        return .{ .failure = .{ .unexpected_option_argument = option.failure_name } };
    }

    switch (option.kind) {
        .help => return .{ .command = .{ .help = request.version_count } },
        .version => {
            request.version_count += 1;
            return .none;
        },
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
                if (try appendReferenceFile(allocator, references, value)) |failure| {
                    return .{ .failure = failure };
                }
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
            'h' => return .{ .command = .{ .help = request.version_count } },
            'V' => request.version_count += 1,
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
                    if (try appendReferenceFile(allocator, references, value)) |failure| {
                        return .{ .failure = failure };
                    }
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
    var request = Request{
        .raw_args = args,
        .rendered_args = &.{},
    };
    var references = std.ArrayList([]const u8).empty;
    var rendered_args = std.ArrayList([]const u8).empty;
    var positional_args = std.ArrayList([]const u8).empty;
    var saw_non_version_request_input = false;
    defer references.deinit(allocator);
    defer rendered_args.deinit(allocator);
    defer positional_args.deinit(allocator);

    var index: usize = 0;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--")) {
            saw_non_version_request_input = true;
            try rendered_args.append(allocator, arg);
            try rendered_args.appendSlice(allocator, positional_args.items);
            if (index + 1 < args.len) {
                try rendered_args.appendSlice(allocator, args[index + 1 ..]);
            }
            break;
        }
        if (arg.len == 0 or arg[0] != '-' or std.mem.eql(u8, arg, "-")) {
            saw_non_version_request_input = true;
            try positional_args.append(allocator, arg);
            continue;
        }
        if (std.mem.startsWith(u8, arg, "--")) {
            const long_option_index = index;
            const pure_version = isPureVersionLongOption(arg);
            switch (try parseLongOption(allocator, args, &index, &request, &references)) {
                .none => {
                    if (!pure_version) saw_non_version_request_input = true;
                    try rendered_args.append(allocator, arg);
                    if (index != long_option_index and index < args.len) {
                        try rendered_args.append(allocator, args[index]);
                    }
                },
                .command => |command| return .{ .command = command },
                .failure => |failure| return .{ .failure = .{
                    .reason = failure,
                    .version_count = request.version_count,
                } },
            }
        } else {
            const short_option_index = index;
            const pure_version = isPureVersionShortCluster(arg);
            switch (try parseShortOptions(allocator, args, &index, &request, &references)) {
                .none => {
                    if (!pure_version) saw_non_version_request_input = true;
                    try rendered_args.append(allocator, arg);
                    if (index != short_option_index and index < args.len) {
                        try rendered_args.append(allocator, args[index]);
                    }
                },
                .command => |command| return .{ .command = command },
                .failure => |failure| return .{ .failure = .{
                    .reason = failure,
                    .version_count = request.version_count,
                } },
            }
        }
    }

    if (index >= args.len) {
        try rendered_args.appendSlice(allocator, positional_args.items);
    }
    if (!saw_non_version_request_input and request.version_count != 0) {
        return .{ .command = .{ .version = request.version_count } };
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
        .failure => |parsed_failure| {
            var stderr_buffer: [512]u8 = undefined;
            var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
            for (0..parsed_failure.version_count) |_| {
                try stderr_writer.interface.writeAll(version_text);
            }
            switch (parsed_failure.reason) {
                .invalid_option => |option| try writeInvalidOptionError(&stderr_writer.interface, option),
                .ambiguous_option => |option| try writeAmbiguousOptionError(&stderr_writer.interface, option),
                .missing_option_argument => |option| try writeMissingOptionArgumentError(&stderr_writer.interface, option),
                .unexpected_option_argument => |option| try writeUnexpectedOptionArgumentError(&stderr_writer.interface, option),
                .too_many_reference_files => try writeTooManyReferenceFilesError(&stderr_writer.interface),
            }
            try stderr_writer.interface.flush();
            std.process.exit(1);
        },
    };

    switch (command) {
        .help => |version_count| {
            var stderr_buffer: [512]u8 = undefined;
            var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
            for (0..version_count) |_| {
                try stderr_writer.interface.writeAll(version_text);
            }
            try stderr_writer.interface.writeAll(usage_text);
            try stderr_writer.interface.flush();
        },
        .version => |version_count| {
            var stderr_buffer: [128]u8 = undefined;
            var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
            for (0..version_count) |_| {
                try stderr_writer.interface.writeAll(version_text);
            }
            try stderr_writer.interface.flush();
        },
        .request => |request| {
            if (request.version_count != 0) {
                var stderr_buffer: [128]u8 = undefined;
                var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
                for (0..request.version_count) |_| {
                    try stderr_writer.interface.writeAll(version_text);
                }
                try stderr_writer.interface.flush();
            }
            var stdout_buffer: [2048]u8 = undefined;
            var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
            try renderGenksymsBridge(&stdout_writer.interface, request);
            try stdout_writer.interface.flush();
        },
    }
}

const testing = std.testing;

test "genksyms bridge parses repeated short flags and arguments" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-d",
        "-d",
        "-D",
        "-w",
        "-p",
        "-r",
        "foo.symref",
        "-r",
        "bar.symref",
        "-T",
        "out.symtypes",
    };
    const outcome = try parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 2), request.debug_level);
                try testing.expect(request.warnings);
                try testing.expect(request.dump_defs);
                try testing.expect(request.preserve);
                try testing.expectEqual(@as(usize, 2), request.reference_files.len);
                try testing.expectEqualStrings("foo.symref", request.reference_files[0]);
                try testing.expectEqualStrings("bar.symref", request.reference_files[1]);
                try testing.expectEqualStrings("out.symtypes", request.dump_types_file.?);
                try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "genksyms bridge parses long options and quiet override" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--debug",
        "--warnings",
        "--quiet",
        "--reference=foo.symref",
        "--dump-types",
        "types.symtypes",
        "--preserve",
    };
    const outcome = try parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expect(!request.warnings);
                try testing.expect(!request.dump_defs);
                try testing.expect(request.preserve);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("foo.symref", request.reference_files[0]);
                try testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);
                try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "genksyms bridge keeps version as a side effect while parsing later options" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-Vd",
        "--reference",
        "foo.symref",
    };
    const outcome = try parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("foo.symref", request.reference_files[0]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "genksyms bridge treats pure version requests as version command" {
    const short_args = [_][]const u8{"-V"};
    const short_outcome = try parseArgs(testing.allocator, &short_args);
    switch (short_outcome) {
        .command => |command| switch (command) {
            .version => |count| try testing.expectEqual(@as(usize, 1), count),
            else => return error.ExpectedVersionCommand,
        },
        else => return error.ExpectedVersionCommand,
    }

    const long_args = [_][]const u8{"--ver"};
    const long_outcome = try parseArgs(testing.allocator, &long_args);
    switch (long_outcome) {
        .command => |command| switch (command) {
            .version => |count| try testing.expectEqual(@as(usize, 1), count),
            else => return error.ExpectedVersionCommand,
        },
        else => return error.ExpectedVersionCommand,
    }
}

test "genksyms bridge preserves repeated pure version invocations" {
    const short_args = [_][]const u8{"-VV"};
    const short_outcome = try parseArgs(testing.allocator, &short_args);
    switch (short_outcome) {
        .command => |command| switch (command) {
            .version => |count| try testing.expectEqual(@as(usize, 2), count),
            else => return error.ExpectedVersionCommand,
        },
        else => return error.ExpectedVersionCommand,
    }

    const long_args = [_][]const u8{
        "--version",
        "--ver",
    };
    const long_outcome = try parseArgs(testing.allocator, &long_args);
    switch (long_outcome) {
        .command => |command| switch (command) {
            .version => |count| try testing.expectEqual(@as(usize, 2), count),
            else => return error.ExpectedVersionCommand,
        },
        else => return error.ExpectedVersionCommand,
    }
}

test "genksyms bridge preserves version side effects before later parse failures" {
    const args = [_][]const u8{"-Vx"};
    const outcome = try parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try testing.expectEqualStrings("x", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "genksyms bridge preserves long version side effects before later parse failures" {
    const args = [_][]const u8{
        "--version",
        "--unknown",
    };
    const outcome = try parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try testing.expectEqualStrings("--unknown", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "genksyms bridge preserves long version side effects before missing long option arguments" {
    const args = [_][]const u8{
        "--version",
        "--dump-types",
    };
    const outcome = try parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .missing_option_argument => |option| try testing.expectEqualStrings("--dump-types", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "genksyms bridge accepts unambiguous abbreviated long options" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--deb",
        "--warn",
        "--qui",
        "--ref=foo.symref",
        "--dump-t",
        "types.symtypes",
        "--pres",
    };
    const outcome = try parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expect(!request.warnings);
                try testing.expect(request.preserve);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("foo.symref", request.reference_files[0]);
                try testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);
                try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "genksyms bridge prefers exact long option matches over longer prefixed siblings" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{"--dump"};
    const outcome = try parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 0), request.debug_level);
                try testing.expect(!request.warnings);
                try testing.expect(request.dump_defs);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
                try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "parseArgs reports ambiguous abbreviated long options" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{"--d"};
    const outcome = try parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| switch (failure.reason) {
            .ambiguous_option => |option| try testing.expectEqualStrings("--d", option),
            else => return error.UnexpectedParseFailure,
        },
        else => return error.ExpectedAmbiguousLongOptionFailure,
    }
}

test "genksyms bridge renders ambiguous long option failure like the fixture" {
    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try writeAmbiguousOptionError(&output.writer, "--du");
    try testing.expectEqualStrings(
        "option '--du' is ambiguous\n",
        output.written(),
    );
}

test "genksyms bridge renders invalid short option failure like the fixture" {
    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try writeInvalidOptionError(&output.writer, "x");
    try testing.expectEqualStrings(
        "invalid option -- 'x'\n",
        output.written(),
    );
}

test "genksyms bridge renders invalid long option failure like the fixture" {
    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try writeInvalidOptionError(&output.writer, "--unknown");
    try testing.expectEqualStrings(
        "unrecognized option '--unknown'\n",
        output.written(),
    );
}

test "genksyms bridge renders missing long option argument like the fixture" {
    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try writeMissingOptionArgumentError(&output.writer, "--reference");
    try testing.expectEqualStrings(
        "option '--reference' requires an argument\n",
        output.written(),
    );
}

test "genksyms bridge renders missing short option argument like the fixture" {
    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try writeMissingOptionArgumentError(&output.writer, "T");
    try testing.expectEqualStrings(
        "option requires an argument -- 'T'\n",
        output.written(),
    );
}

test "genksyms bridge renders unexpected long option argument like the fixture" {
    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try writeUnexpectedOptionArgumentError(&output.writer, "--help");
    try testing.expectEqualStrings(
        "option '--help' doesn't allow an argument\n",
        output.written(),
    );
}

test "genksyms bridge keeps version side effect before long help" {
    const args = [_][]const u8{
        "-V",
        "--help",
    };
    const outcome = try parseArgs(testing.allocator, &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(@as(usize, 1), version_count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedCommand,
    }
}

test "genksyms bridge keeps version side effect before short help" {
    const args = [_][]const u8{"-Vh"};
    const outcome = try parseArgs(testing.allocator, &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(@as(usize, 1), version_count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedCommand,
    }
}

test "genksyms bridge keeps long version side effect before short help" {
    const args = [_][]const u8{
        "--version",
        "-h",
    };
    const outcome = try parseArgs(testing.allocator, &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(@as(usize, 1), version_count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedCommand,
    }
}

test "genksyms bridge keeps long version side effect before long help" {
    const args = [_][]const u8{
        "--version",
        "--help",
    };
    const outcome = try parseArgs(testing.allocator, &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(@as(usize, 1), version_count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedCommand,
    }
}

test "genksyms bridge keeps abbreviated long version side effect before long help" {
    const args = [_][]const u8{
        "--ver",
        "--help",
    };
    const outcome = try parseArgs(testing.allocator, &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(@as(usize, 1), version_count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedCommand,
    }
}

test "genksyms bridge keeps abbreviated long version side effect before short help" {
    const args = [_][]const u8{
        "--ver",
        "-h",
    };
    const outcome = try parseArgs(testing.allocator, &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(@as(usize, 1), version_count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedCommand,
    }
}

test "genksyms bridge canonicalizes unexpected long option argument failures" {
    const args = [_][]const u8{"--help=extra"};
    const outcome = try parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| switch (failure.reason) {
            .unexpected_option_argument => |option| try testing.expectEqualStrings("--help", option),
            else => return error.UnexpectedParseFailure,
        },
        else => return error.TestExpectedFailure,
    }
}

test "genksyms bridge treats lone dash as positional passthrough" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-",
        "-d",
    };
    const outcome = try parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expectEqual(@as(usize, 2), request.rendered_args.len);
                try testing.expectEqualStrings("-d", request.rendered_args[0]);
                try testing.expectEqualStrings("-", request.rendered_args[1]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "genksyms bridge accepts explicit option terminator" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--",
        "--leftover",
        "positional",
    };
    const outcome = try parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 3), request.rendered_args.len);
                try testing.expectEqualStrings("--", request.rendered_args[0]);
                try testing.expectEqualStrings("--leftover", request.rendered_args[1]);
                try testing.expectEqualStrings("positional", request.rendered_args[2]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "genksyms bridge reports invalid short option in getopt style" {
    const args = [_][]const u8{"-x"};
    const outcome = try parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| switch (failure.reason) {
            .invalid_option => |option| try testing.expectEqualStrings("x", option),
            else => return error.UnexpectedParseFailure,
        },
        else => return error.TestExpectedFailure,
    }
}

test "genksyms bridge reports missing short option argument in getopt style" {
    const args = [_][]const u8{"-T"};
    const outcome = try parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| switch (failure.reason) {
            .missing_option_argument => |option| try testing.expectEqualStrings("T", option),
            else => return error.UnexpectedParseFailure,
        },
        else => return error.TestExpectedFailure,
    }
}

test "genksyms bridge rejects more than sixteen reference files like the C harness" {
    const args = [_][]const u8{
        "-r", "01.symref",
        "-r", "02.symref",
        "-r", "03.symref",
        "-r", "04.symref",
        "-r", "05.symref",
        "-r", "06.symref",
        "-r", "07.symref",
        "-r", "08.symref",
        "-r", "09.symref",
        "-r", "10.symref",
        "-r", "11.symref",
        "-r", "12.symref",
        "-r", "13.symref",
        "-r", "14.symref",
        "-r", "15.symref",
        "-r", "16.symref",
        "-r", "17.symref",
    };
    const outcome = try parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| try testing.expectEqual(ParseFailure.too_many_reference_files, failure.reason),
        else => return error.TestExpectedFailure,
    }
}

test "genksyms bridge renders normalized invocation plan" {
    const rendered_args = [_][]const u8{
        "-d",
        "-r",
        "foo.symref",
    };
    const reference_files = [_][]const u8{"foo.symref"};
    const request = Request{
        .raw_args = &rendered_args,
        .rendered_args = &rendered_args,
        .debug_level = 1,
        .warnings = false,
        .dump_defs = false,
        .preserve = false,
        .reference_files = &reference_files,
        .dump_types_file = null,
    };

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-d\",\"-r\",\"foo.symref\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"foo.symref\"],\"dump_types_file\":null}}\n",
        output.written(),
    );
}

test "genksyms bridge ignores positional args while still parsing later options" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "leftover.c",
        "-d",
        "rightover.h",
        "-r",
        "foo.symref",
    };
    const outcome = try parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("foo.symref", request.reference_files[0]);
                try testing.expectEqual(@as(usize, 5), request.rendered_args.len);
                try testing.expectEqualStrings("-d", request.rendered_args[0]);
                try testing.expectEqualStrings("-r", request.rendered_args[1]);
                try testing.expectEqualStrings("foo.symref", request.rendered_args[2]);
                try testing.expectEqualStrings("leftover.c", request.rendered_args[3]);
                try testing.expectEqualStrings("rightover.h", request.rendered_args[4]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
