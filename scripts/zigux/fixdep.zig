const std = @import("std");
const Io = std.Io;

// Keep file reads aligned with the C helper, which consumes the full file size.
const max_file_bytes: usize = std.math.maxInt(usize);

const FixdepError = error{
    NoTargets,
    ReadDependencyFile,
    OutputWrite,
};

const DependencyFileFailure = enum {
    open,
    stat,
    read,
};

fn isIdentByte(ch: u8) bool {
    return std.ascii.isAlphanumeric(ch) or ch == '_';
}

fn isIgnoredFile(path: []const u8) bool {
    return std.mem.endsWith(u8, path, "include/generated/autoconf.h");
}

fn isNoParseFile(path: []const u8) bool {
    return std.mem.endsWith(u8, path, ".rlib") or
        std.mem.endsWith(u8, path, ".rmeta") or
        std.mem.endsWith(u8, path, ".so");
}

fn describeFileReadError(err: anyerror) []const u8 {
    return switch (err) {
        error.FileNotFound => "No such file or directory",
        error.AccessDenied => "Permission denied",
        error.PermissionDenied => "Permission denied",
        error.IsDir => "Is a directory",
        error.NotDir => "Not a directory",
        error.NameTooLong => "File name too long",
        error.BadPathName => "Bad path name",
        error.SymLinkLoop => "Too many levels of symbolic links",
        error.ProcessFdQuotaExceeded, error.SystemFdQuotaExceeded => "Too many open files",
        error.DeviceBusy => "Device or resource busy",
        error.NoDevice => "No such device",
        error.FileTooBig => "File too large",
        error.InputOutput => "Input/output error",
        error.EndOfStream => "Success",
        else => @errorName(err),
    };
}

fn bytesBeforeFirstNull(text: []const u8) []const u8 {
    return text[0 .. (std.mem.indexOfScalar(u8, text, 0) orelse text.len)];
}

fn formatDependencyFileErrorMessage(
    buffer: []u8,
    kind: DependencyFileFailure,
    path: []const u8,
    err: anyerror,
) ![]const u8 {
    return switch (kind) {
        .open => std.fmt.bufPrint(buffer, "fixdep: error opening file: {s}: {s}\n", .{
            path,
            describeFileReadError(err),
        }),
        .stat => std.fmt.bufPrint(buffer, "fixdep: error fstat'ing file: {s}: {s}\n", .{
            path,
            describeFileReadError(err),
        }),
        .read => std.fmt.bufPrint(buffer, "fixdep: read: {s}\n", .{describeFileReadError(err)}),
    };
}

fn emitDependencyFileError(
    io: std.Io,
    kind: DependencyFileFailure,
    path: []const u8,
    err: anyerror,
) !noreturn {
    var stderr_buffer: [512]u8 = undefined;
    var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
    const stderr = &stderr_writer.interface;
    var message_buffer: [512]u8 = undefined;
    const message = try formatDependencyFileErrorMessage(&message_buffer, kind, path, err);
    try stderr.writeAll(message);
    try stderr.flush();
    std.process.exit(2);
}

fn OutputWriter(comptime WriterType: type) type {
    return struct {
        inner: WriterType,

        fn init(inner: WriterType) @This() {
            return .{ .inner = inner };
        }

        fn print(self: *@This(), comptime fmt: []const u8, args: anytype) FixdepError!void {
            self.inner.print(fmt, args) catch return error.OutputWrite;
        }

        fn flush(self: *@This()) FixdepError!void {
            self.inner.flush() catch return error.OutputWrite;
        }
    };
}

fn flushOutput(writer: anytype) FixdepError!void {
    writer.flush() catch return error.OutputWrite;
}

fn emitOutputWriteError(io: std.Io) !noreturn {
    var stderr_buffer: [128]u8 = undefined;
    var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
    const stderr = &stderr_writer.interface;
    try stderr.writeAll("fixdep: not all data was written to the output\n");
    try stderr.flush();
    std.process.exit(1);
}

fn flushOutputPreservingPrimaryError(writer: anytype) void {
    // Match the C helper: once parsing or file-open logic has already failed,
    // a late stdout flush failure must not replace the original error surface.
    writer.flush() catch {};
}

fn shouldNormalizeDependencyFileFailure(err: anyerror) bool {
    return switch (err) {
        error.OutOfMemory, error.StreamTooLong => false,
        else => true,
    };
}

const Processor = struct {
    io: std.Io,
    arena: std.heap.ArenaAllocator,
    config_seen: std.ArrayListUnmanaged([]const u8),
    file_seen: std.ArrayListUnmanaged([]const u8),
    last_file_error_path: []const u8,
    last_file_error: ?anyerror,
    last_file_error_kind: DependencyFileFailure,

    pub fn init(backing_allocator: std.mem.Allocator, io: std.Io) Processor {
        var self: Processor = undefined;
        self.io = io;
        self.arena = std.heap.ArenaAllocator.init(backing_allocator);
        self.config_seen = .empty;
        self.file_seen = .empty;
        self.last_file_error_path = "";
        self.last_file_error = null;
        self.last_file_error_kind = .open;
        return self;
    }

    pub fn deinit(self: *Processor) void {
        self.config_seen.deinit(self.arena.allocator());
        self.file_seen.deinit(self.arena.allocator());
        self.arena.deinit();
    }

    fn remember(self: *Processor, table: *std.ArrayListUnmanaged([]const u8), token: []const u8) !bool {
        for (table.items) |existing| {
            if (std.mem.eql(u8, existing, token)) {
                return true;
            }
        }

        const copy = try self.arena.allocator().dupe(u8, token);
        try table.append(self.arena.allocator(), copy);
        return false;
    }

    fn useConfig(self: *Processor, writer: anytype, token: []const u8) !void {
        if (try self.remember(&self.config_seen, token)) {
            return;
        }
        try writer.print("    $(wildcard include/config/{s}) \\\n", .{token});
    }

    fn rememberFileError(self: *Processor, path: []const u8, err: anyerror, kind: DependencyFileFailure) FixdepError {
        self.last_file_error_path = self.arena.allocator().dupe(u8, path) catch path;
        self.last_file_error = err;
        self.last_file_error_kind = kind;
        return error.ReadDependencyFile;
    }

    fn normalizeReadDependencyFailure(
        self: *Processor,
        path: []const u8,
        err: anyerror,
        reader_err: ?anyerror,
    ) anyerror!void {
        if (!shouldNormalizeDependencyFileFailure(err)) {
            return err;
        }

        const actual_err = if (err == error.ReadFailed and reader_err != null)
            reader_err.?
        else
            err;
        return self.rememberFileError(path, actual_err, .read);
    }

    fn parseConfigFile(self: *Processor, writer: anytype, text: []const u8) !void {
        const scan_text = bytesBeforeFirstNull(text);
        var index: usize = 0;
        while (std.mem.indexOfPos(u8, scan_text, index, "CONFIG_")) |start| {
            if (start > 0 and isIdentByte(scan_text[start - 1])) {
                index = start + 7;
                continue;
            }

            var end = start + 7;
            while (end < scan_text.len and isIdentByte(scan_text[end])) : (end += 1) {}

            var trimmed_end = end;
            const token = scan_text[start + 7 .. end];
            if (std.mem.endsWith(u8, token, "_MODULE")) {
                trimmed_end -= 7;
            }

            if (trimmed_end > start + 7) {
                try self.useConfig(writer, scan_text[start + 7 .. trimmed_end]);
            }
            index = end;
        }
    }

    fn readDependencyFile(self: *Processor, path: []const u8) ![]const u8 {
        var file = Io.Dir.cwd().openFile(self.io, path, .{ .allow_directory = true }) catch |err| {
            if (!shouldNormalizeDependencyFileFailure(err)) {
                return err;
            }
            return self.rememberFileError(path, err, .open);
        };
        defer file.close(self.io);

        const stat = file.stat(self.io) catch |err| {
            if (!shouldNormalizeDependencyFileFailure(err)) {
                return err;
            }
            return self.rememberFileError(path, err, .stat);
        };
        const file_bytes = std.math.cast(usize, stat.size) orelse return error.StreamTooLong;

        var reader = file.reader(self.io, &.{});
        return reader.interface.readAlloc(self.arena.allocator(), file_bytes) catch |err| {
            const actual_err = switch (err) {
                error.EndOfStream => error.EndOfStream,
                error.ReadFailed => reader.err orelse err,
                else => err,
            };
            try self.normalizeReadDependencyFailure(path, actual_err, null);
            unreachable;
        };
    }

    fn parseDepFile(self: *Processor, writer: anytype, dep_text: []const u8, target: []const u8) !void {
        const scan_text = bytesBeforeFirstNull(dep_text);
        var saw_any_target = false;
        var is_target = true;
        var is_source = false;
        var index: usize = 0;
        var token = try std.ArrayList(u8).initCapacity(self.arena.allocator(), 64);
        defer token.deinit(self.arena.allocator());

        while (index < scan_text.len) {
            switch (scan_text[index]) {
                '#' => {
                    index += 1;
                    while (index < scan_text.len and scan_text[index] != '\n') {
                        if (scan_text[index] == '\\' and index + 1 < scan_text.len) {
                            index += 1;
                        }
                        index += 1;
                    }
                    continue;
                },
                ' ', '\t' => {
                    index += 1;
                    continue;
                },
                '\\' => {
                    if (index + 1 < scan_text.len and scan_text[index + 1] == '\n') {
                        index += 2;
                        continue;
                    }
                },
                '\n' => {
                    index += 1;
                    is_target = true;
                    continue;
                },
                ':' => {
                    index += 1;
                    is_target = false;
                    is_source = true;
                    continue;
                },
                else => {},
            }

            token.clearRetainingCapacity();
            var cursor = index;
            while (cursor < scan_text.len and scan_text[cursor] != ' ' and scan_text[cursor] != '\t' and scan_text[cursor] != '\n' and scan_text[cursor] != '#' and scan_text[cursor] != ':') {
                if (scan_text[cursor] == '\\') {
                    if (cursor + 1 < scan_text.len and scan_text[cursor + 1] == '\n') {
                        break;
                    }
                    if (cursor + 1 < scan_text.len and (scan_text[cursor + 1] == '#' or scan_text[cursor + 1] == ':')) {
                        cursor += 1;
                        try token.append(self.arena.allocator(), scan_text[cursor]);
                        cursor += 1;
                        continue;
                    }
                    if (cursor + 1 < scan_text.len and (scan_text[cursor + 1] == ' ' or scan_text[cursor + 1] == '\t')) {
                        try token.append(self.arena.allocator(), scan_text[cursor]);
                        cursor += 1;
                        try token.append(self.arena.allocator(), scan_text[cursor]);
                        cursor += 1;
                        continue;
                    }
                    try token.append(self.arena.allocator(), scan_text[cursor]);
                    cursor += 1;
                    if (cursor < scan_text.len) {
                        try token.append(self.arena.allocator(), scan_text[cursor]);
                        cursor += 1;
                    }
                    continue;
                }

                try token.append(self.arena.allocator(), scan_text[cursor]);
                cursor += 1;
            }

            if (token.items.len == 0) {
                index = cursor;
                continue;
            }

            if (is_target) {
                index = cursor;
                continue;
            }

            var need_parse = false;
            if (is_source) {
                if (!saw_any_target) {
                    saw_any_target = true;
                    try writer.print("source_{s} := {s}\n\n", .{ target, token.items });
                    try writer.print("deps_{s} := \\\n", .{target});
                    need_parse = true;
                }
            } else if (!isIgnoredFile(token.items) and !try self.remember(&self.file_seen, token.items)) {
                try writer.print("  {s} \\\n", .{token.items});
                need_parse = true;
            }

            if (need_parse and !isNoParseFile(token.items)) {
                const dependency_text = try self.readDependencyFile(token.items);
                try self.parseConfigFile(writer, dependency_text);
            }

            is_source = false;
            index = cursor;
        }

        if (!saw_any_target) {
            return error.NoTargets;
        }

        try writer.print("\n{s}: $(deps_{s})\n\n", .{ target, target });
        try writer.print("$(deps_{s}):\n", .{target});
    }
};

pub fn runFixdep(allocator: std.mem.Allocator, io: std.Io, writer: anytype, depfile: []const u8, target: []const u8, cmdline: []const u8) !void {
    var processor = Processor.init(allocator, io);
    defer processor.deinit();

    try writer.print("savedcmd_{s} := {s}\n\n", .{ target, cmdline });
    const dep_text = processor.readDependencyFile(depfile) catch |err| switch (err) {
        error.ReadDependencyFile => {
            flushOutputPreservingPrimaryError(writer);
            try emitDependencyFileError(io, processor.last_file_error_kind, processor.last_file_error_path, processor.last_file_error.?);
        },
        else => return err,
    };
    processor.parseDepFile(writer, dep_text, target) catch |err| switch (err) {
        error.ReadDependencyFile => {
            flushOutputPreservingPrimaryError(writer);
            try emitDependencyFileError(io, processor.last_file_error_kind, processor.last_file_error_path, processor.last_file_error.?);
        },
        else => return err,
    };
}

fn emitNoTargetsParseError(io: std.Io) !noreturn {
    var stderr_buffer: [128]u8 = undefined;
    var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
    const stderr = &stderr_writer.interface;
    try stderr.writeAll("fixdep: parse error; no targets found\n");
    try stderr.flush();
    std.process.exit(1);
}

pub fn main(init: std.process.Init) !void {
    const arena = init.arena.allocator();
    const io = init.io;
    const args = try init.minimal.args.toSlice(arena);

    if (args.len != 4) {
        var stderr_buffer: [128]u8 = undefined;
        var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
        const stderr = &stderr_writer.interface;
        try stderr.writeAll("Usage: fixdep <depfile> <target> <cmdline>\n");
        try stderr.flush();
        std.process.exit(1);
    }

    var stdout_buffer: [1024]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const stdout_interface = &stdout_writer.interface;
    var stdout = OutputWriter(@TypeOf(stdout_interface)).init(stdout_interface);

    runFixdep(arena, io, &stdout, args[1], args[2], args[3]) catch |err| switch (err) {
        error.NoTargets => {
            flushOutputPreservingPrimaryError(&stdout);
            try emitNoTargetsParseError(io);
        },
        error.OutputWrite => try emitOutputWriteError(io),
        else => return err,
    };
    flushOutput(&stdout) catch |err| switch (err) {
        error.OutputWrite => try emitOutputWriteError(io),
        else => return err,
    };
}

test "config parsing trims _MODULE and deduplicates symbols" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 64),
                .allocator = allocator,
            };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }
    };

    var processor = Processor.init(std.testing.allocator, std.testing.io);
    defer processor.deinit();

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try processor.parseConfigFile(
        &capture,
        "CONFIG_ZIGUX_CORE CONFIG_ZIGUX_DEBUG_MODULE CONFIG_ZIGUX_CORE",
    );

    try std.testing.expectEqualStrings(
        "    $(wildcard include/config/ZIGUX_CORE) \\\n    $(wildcard include/config/ZIGUX_DEBUG) \\\n",
        capture.list.items,
    );
}

test "config parsing stops at the first embedded NUL" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 64),
                .allocator = allocator,
            };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }
    };

    var processor = Processor.init(std.testing.allocator, std.testing.io);
    defer processor.deinit();

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try processor.parseConfigFile(
        &capture,
        "CONFIG_ZIGUX_VISIBLE\x00CONFIG_ZIGUX_HIDDEN_MODULE",
    );

    try std.testing.expectEqualStrings(
        "    $(wildcard include/config/ZIGUX_VISIBLE) \\\n",
        capture.list.items,
    );
}

test "dep parsing returns NoTargets for comment-only depfiles" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 8),
                .allocator = allocator,
            };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }
    };

    var processor = Processor.init(std.testing.allocator, std.testing.io);
    defer processor.deinit();

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try std.testing.expectError(
        error.NoTargets,
        processor.parseDepFile(&capture, "# comment only\n# still no targets\n", "sample.o"),
    );
    try std.testing.expectEqual(@as(usize, 0), capture.list.items.len);
}

test "dep parsing skips bytes after the first embedded NUL" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 128),
                .allocator = allocator,
            };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }
    };

    var processor = Processor.init(std.testing.allocator, std.testing.io);
    defer processor.deinit();

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try processor.parseDepFile(
        &capture,
        "embedded_nul.o: visible.rmeta visible_dep.so\x00embedded_nul.o: hidden.rmeta hidden_dep.so\n",
        "embedded_nul.o",
    );

    try std.testing.expectEqualStrings(
        "source_embedded_nul.o := visible.rmeta\n\n" ++
            "deps_embedded_nul.o := \\\n" ++
            "  visible_dep.so \\\n" ++
            "\n" ++
            "embedded_nul.o: $(deps_embedded_nul.o)\n\n" ++
            "$(deps_embedded_nul.o):\n",
        capture.list.items,
    );
}

test "dep parsing skips escaped-newline comments before the first target" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 128),
                .allocator = allocator,
            };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }
    };

    var processor = Processor.init(std.testing.allocator, std.testing.io);
    defer processor.deinit();

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try processor.parseDepFile(
        &capture,
        "# rustc note \\\n" ++
            "continues across lines \\\n" ++
            "until the first real newline\n" ++
            "continued_comment.o: source.rmeta dep.so\n",
        "continued_comment.o",
    );

    try std.testing.expectEqualStrings(
        "source_continued_comment.o := source.rmeta\n\n" ++
            "deps_continued_comment.o := \\\n" ++
            "  dep.so \\\n" ++
            "\n" ++
            "continued_comment.o: $(deps_continued_comment.o)\n\n" ++
            "$(deps_continued_comment.o):\n",
        capture.list.items,
    );
}

test "dep parsing continues dependency tokens across escaped newlines" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 128),
                .allocator = allocator,
            };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }
    };

    var processor = Processor.init(std.testing.allocator, std.testing.io);
    defer processor.deinit();

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try processor.parseDepFile(
        &capture,
        "continued.o: source.rmeta dep_one.so \\\n" ++
            " dep_two.so \\\n" ++
            " dep_three.so\n",
        "continued.o",
    );

    try std.testing.expectEqualStrings(
        "source_continued.o := source.rmeta\n\n" ++
            "deps_continued.o := \\\n" ++
            "  dep_one.so \\\n" ++
            "  dep_two.so \\\n" ++
            "  dep_three.so \\\n" ++
            "\n" ++
            "continued.o: $(deps_continued.o)\n\n" ++
            "$(deps_continued.o):\n",
        capture.list.items,
    );
}

test "dep parsing keeps escaped whitespace inside dependency tokens" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 128),
                .allocator = allocator,
            };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }
    };

    var processor = Processor.init(std.testing.allocator, std.testing.io);
    defer processor.deinit();

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try processor.parseDepFile(
        &capture,
        "escaped.o: src\\ with\\ space.so dep\\ with\\ space.so dep\\\twith\\\ttab.so\n",
        "escaped.o",
    );

    try std.testing.expectEqualStrings(
        "source_escaped.o := src\\ with\\ space.so\n\n" ++
            "deps_escaped.o := \\\n" ++
            "  dep\\ with\\ space.so \\\n" ++
            "  dep\\\twith\\\ttab.so \\\n" ++
            "\n" ++
            "escaped.o: $(deps_escaped.o)\n\n" ++
            "$(deps_escaped.o):\n",
        capture.list.items,
    );
}

test "dep parsing unescapes escaped hash and colon dependency tokens" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 128),
                .allocator = allocator,
            };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }
    };

    var processor = Processor.init(std.testing.allocator, std.testing.io);
    defer processor.deinit();

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try processor.parseDepFile(
        &capture,
        "escaped.o: src.rmeta dep\\#hash.so dep\\:colon.so dep\\#hash.so\n",
        "escaped.o",
    );

    try std.testing.expectEqualStrings(
        "source_escaped.o := src.rmeta\n\n" ++
            "deps_escaped.o := \\\n" ++
            "  dep#hash.so \\\n" ++
            "  dep:colon.so \\\n" ++
            "\n" ++
            "escaped.o: $(deps_escaped.o)\n\n" ++
            "$(deps_escaped.o):\n",
        capture.list.items,
    );
}

test "double backslash before hash still starts a comment like C fixdep" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 128),
                .allocator = allocator,
            };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }
    };

    var processor = Processor.init(std.testing.allocator, std.testing.io);
    defer processor.deinit();

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try std.testing.expectError(
        error.ReadDependencyFile,
        processor.parseDepFile(&capture, "missing_hash.o: source.rmeta missing\\\\#dep.h\n", "missing_hash.o"),
    );
    try std.testing.expectEqualStrings(
        "source_missing_hash.o := source.rmeta\n\n" ++
            "deps_missing_hash.o := \\\n" ++
            "  missing\\\\ \\\n",
        capture.list.items,
    );
    try std.testing.expectEqualStrings("missing\\\\", processor.last_file_error_path);
    try std.testing.expectEqual(error.FileNotFound, processor.last_file_error.?);
    try std.testing.expectEqual(DependencyFileFailure.open, processor.last_file_error_kind);
}

test "dep parsing keeps the first source across concatenated target entries" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 128),
                .allocator = allocator,
            };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }
    };

    var processor = Processor.init(std.testing.allocator, std.testing.io);
    defer processor.deinit();

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try processor.parseDepFile(
        &capture,
        "sample_concatenated.o: sample_concatenated_source.rmeta sample_concatenated_dep.so\n" ++
            "# concatenated dep-info continues with an intermediate source\n" ++
            "sample_concatenated.o: sample_concatenated_temp.rmeta sample_concatenated_temp_dep.so\n",
        "sample_concatenated.o",
    );

    try std.testing.expectEqualStrings(
        "source_sample_concatenated.o := sample_concatenated_source.rmeta\n\n" ++
            "deps_sample_concatenated.o := \\\n" ++
            "  sample_concatenated_dep.so \\\n" ++
            "  sample_concatenated_temp_dep.so \\\n" ++
            "\n" ++
            "sample_concatenated.o: $(deps_sample_concatenated.o)\n\n" ++
            "$(deps_sample_concatenated.o):\n",
        capture.list.items,
    );
}

test "escaped-newline comments between concatenated target entries keep the first source" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 128),
                .allocator = allocator,
            };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }
    };

    var processor = Processor.init(std.testing.allocator, std.testing.io);
    defer processor.deinit();

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try processor.parseDepFile(
        &capture,
        "sample_concatenated.o: sample_concatenated_source.rmeta sample_concatenated_dep.so\n" ++
            "# rustc comment continues \\\n" ++
            "across an intermediate physical line \\\n" ++
            "before the next real target\n" ++
            "sample_concatenated.o: sample_concatenated_temp.rmeta sample_concatenated_temp_dep.so\n",
        "sample_concatenated.o",
    );

    try std.testing.expectEqualStrings(
        "source_sample_concatenated.o := sample_concatenated_source.rmeta\n\n" ++
            "deps_sample_concatenated.o := \\\n" ++
            "  sample_concatenated_dep.so \\\n" ++
            "  sample_concatenated_temp_dep.so \\\n" ++
            "\n" ++
            "sample_concatenated.o: $(deps_sample_concatenated.o)\n\n" ++
            "$(deps_sample_concatenated.o):\n",
        capture.list.items,
    );
}

test "dep parsing unescapes escaped hash and colon tokens once" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 128),
                .allocator = allocator,
            };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }
    };

    var processor = Processor.init(std.testing.allocator, std.testing.io);
    defer processor.deinit();

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try processor.parseDepFile(
        &capture,
        "module.o: source\\:one.rmeta shared\\#config.so shared\\#config.so generated\\:two.so\n",
        "module.o",
    );

    try std.testing.expectEqualStrings(
        "source_module.o := source:one.rmeta\n\n" ++
            "deps_module.o := \\\n" ++
            "  shared#config.so \\\n" ++
            "  generated:two.so \\\n" ++
            "\n" ++
            "module.o: $(deps_module.o)\n\n" ++
            "$(deps_module.o):\n",
        capture.list.items,
    );
}

test "dep parsing stays deterministic across concatenated target and comment packets" {
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

        fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }
    };

    const dep_text =
        "deterministic.o: source.rmeta dep_one.so \\\n" ++
        " dep_two.so\n" ++
        "# rustc comment continues \\\n" ++
        "across a physical line \\\n" ++
        "before the next real target\n" ++
        "deterministic.o: replacement.rmeta dep_three.so dep\\#hash.so dep\\:colon.so\n";
    const expected =
        "source_deterministic.o := source.rmeta\n\n" ++
        "deps_deterministic.o := \\\n" ++
        "  dep_one.so \\\n" ++
        "  dep_two.so \\\n" ++
        "  dep_three.so \\\n" ++
        "  dep#hash.so \\\n" ++
        "  dep:colon.so \\\n" ++
        "\n" ++
        "deterministic.o: $(deps_deterministic.o)\n\n" ++
        "$(deps_deterministic.o):\n";

    var first_processor = Processor.init(std.testing.allocator, std.testing.io);
    defer first_processor.deinit();
    var first_capture = try Capture.init(std.testing.allocator);
    defer first_capture.deinit();
    try first_processor.parseDepFile(&first_capture, dep_text, "deterministic.o");

    var second_processor = Processor.init(std.testing.allocator, std.testing.io);
    defer second_processor.deinit();
    var second_capture = try Capture.init(std.testing.allocator);
    defer second_capture.deinit();
    try second_processor.parseDepFile(&second_capture, dep_text, "deterministic.o");

    try std.testing.expectEqualStrings(expected, first_capture.list.items);
    try std.testing.expectEqualStrings(first_capture.list.items, second_capture.list.items);
}

test "ignored and no-parse file classification matches fixdep rules" {
    try std.testing.expect(isIgnoredFile("include/generated/autoconf.h"));
    try std.testing.expect(isNoParseFile("foo.rmeta"));
    try std.testing.expect(isNoParseFile("foo.rlib"));
    try std.testing.expect(isNoParseFile("foo.so"));
    try std.testing.expect(!isIgnoredFile("include/generated/autoconf.hpp"));
}

test "file read errors map to C-style messages" {
    try std.testing.expectEqualStrings("No such file or directory", describeFileReadError(error.FileNotFound));
    try std.testing.expectEqualStrings("Permission denied", describeFileReadError(error.AccessDenied));
    try std.testing.expectEqualStrings("File too large", describeFileReadError(error.FileTooBig));
    try std.testing.expectEqualStrings("Success", describeFileReadError(error.EndOfStream));
}

test "dependency file failure normalization keeps runtime io errors on the C-style path" {
    try std.testing.expect(shouldNormalizeDependencyFileFailure(error.PermissionDenied));
    try std.testing.expect(shouldNormalizeDependencyFileFailure(error.Unexpected));
    try std.testing.expect(!shouldNormalizeDependencyFileFailure(error.OutOfMemory));
    try std.testing.expect(!shouldNormalizeDependencyFileFailure(error.StreamTooLong));
}

test "dependency file error messages keep C helper wording" {
    var buffer: [512]u8 = undefined;

    try std.testing.expectEqualStrings(
        "fixdep: error opening file: sample.d: No such file or directory\n",
        try formatDependencyFileErrorMessage(&buffer, .open, "sample.d", error.FileNotFound),
    );
    try std.testing.expectEqualStrings(
        "fixdep: error fstat'ing file: sample.d: Permission denied\n",
        try formatDependencyFileErrorMessage(&buffer, .stat, "sample.d", error.PermissionDenied),
    );
    try std.testing.expectEqualStrings(
        "fixdep: read: Input/output error\n",
        try formatDependencyFileErrorMessage(&buffer, .read, "sample.d", error.InputOutput),
    );
    try std.testing.expectEqualStrings(
        "fixdep: read: Success\n",
        try formatDependencyFileErrorMessage(&buffer, .read, "sample.d", error.EndOfStream),
    );
}

test "missing dependency path is preserved for later error reporting" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 64),
                .allocator = allocator,
            };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }
    };

    var processor = Processor.init(std.testing.allocator, std.testing.io);
    defer processor.deinit();

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try std.testing.expectError(
        error.ReadDependencyFile,
        processor.parseDepFile(&capture, "missing.o: source.rmeta missing\\#dep.h\n", "missing.o"),
    );
    try std.testing.expectEqualStrings("missing#dep.h", processor.last_file_error_path);
    try std.testing.expectEqual(error.FileNotFound, processor.last_file_error.?);
    try std.testing.expectEqual(DependencyFileFailure.open, processor.last_file_error_kind);
}

test "direct dependency read errors stay on the C-style read path" {
    var processor = Processor.init(std.testing.allocator, std.testing.io);
    defer processor.deinit();

    try std.testing.expectError(
        error.ReadDependencyFile,
        processor.normalizeReadDependencyFailure("dirdep", error.IsDir, null),
    );
    try std.testing.expectEqualStrings("dirdep", processor.last_file_error_path);
    try std.testing.expectEqual(error.IsDir, processor.last_file_error.?);
    try std.testing.expectEqual(DependencyFileFailure.read, processor.last_file_error_kind);
    try std.testing.expectError(
        error.OutOfMemory,
        processor.normalizeReadDependencyFailure("dirdep", error.OutOfMemory, null),
    );
}

test "output writer maps print and flush failures to fixdep output-write errors" {
    const FailingWriter = struct {
        fn print(_: *@This(), comptime _: []const u8, _: anytype) error{NoSpaceLeft}!void {
            return error.NoSpaceLeft;
        }

        fn flush(_: *@This()) error{NoSpaceLeft}!void {
            return error.NoSpaceLeft;
        }
    };

    var inner = FailingWriter{};
    var writer = OutputWriter(*FailingWriter).init(&inner);

    try std.testing.expectError(error.OutputWrite, writer.print("savedcmd_sample := cmd\n", .{}));
    try std.testing.expectError(error.OutputWrite, writer.flush());
}

test "preserving a primary error ignores late output flush failures" {
    const FailingWriter = struct {
        fn flush(_: *@This()) error{NoSpaceLeft}!void {
            return error.NoSpaceLeft;
        }
    };

    var inner = FailingWriter{};
    var writer = OutputWriter(*FailingWriter).init(&inner);

    flushOutputPreservingPrimaryError(&writer);
}

test "runFixdep keeps the savedcmd prelude before no-target parse errors" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 64),
                .allocator = allocator,
            };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }

        fn flush(_: *@This()) !void {}
    };

    const depfile_name = "zigux_fixdep_comment_only_test.d";
    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = depfile_name,
        .data = "# comment only\n# still no targets\n",
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, depfile_name) catch {};

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try std.testing.expectError(
        error.NoTargets,
        runFixdep(
            std.testing.allocator,
            std.testing.io,
            &capture,
            depfile_name,
            "sample.o",
            "clang -c sample.c -o sample.o",
        ),
    );
    try std.testing.expectEqualStrings(
        "savedcmd_sample.o := clang -c sample.c -o sample.o\n\n",
        capture.list.items,
    );
}

test "dep parsing keeps partial stdout before missing dependency read errors" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 128),
                .allocator = allocator,
            };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }

        fn flush(_: *@This()) !void {}
    };

    var processor = Processor.init(std.testing.allocator, std.testing.io);
    defer processor.deinit();

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try std.testing.expectError(
        error.ReadDependencyFile,
        processor.parseDepFile(&capture, "missing_dep.o: source.rmeta missing\\#dep.h\n", "missing_dep.o"),
    );
    try std.testing.expectEqualStrings(
        "source_missing_dep.o := source.rmeta\n\n" ++
            "deps_missing_dep.o := \\\n" ++
            "  missing#dep.h \\\n",
        capture.list.items,
    );
    try std.testing.expectEqualStrings("missing#dep.h", processor.last_file_error_path);
    try std.testing.expectEqual(error.FileNotFound, processor.last_file_error.?);
    try std.testing.expectEqual(DependencyFileFailure.open, processor.last_file_error_kind);
}

test "dep parsing reads source and header configs while ignoring autoconf.h" {
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

        fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }
    };

    const src_path = "zigux_fixdep_recursive_source_test.c";
    const cfg_path = "zigux_fixdep_recursive_cfg_test.h";
    const autoconf_path = "include/generated/autoconf.h";

    _ = try Io.Dir.cwd().createDirPathStatus(std.testing.io, "include/generated", .default_dir);
    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = src_path,
        .data = "/* CONFIG_ZIGUX_SRC */\n",
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, src_path) catch {};
    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = cfg_path,
        .data = "#define CONFIG_ZIGUX_CFG 1\n#define CONFIG_ZIGUX_SRC 1\n",
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, cfg_path) catch {};
    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = autoconf_path,
        .data = "#define CONFIG_AUTOCONF_ONLY 1\n",
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, autoconf_path) catch {};

    var processor = Processor.init(std.testing.allocator, std.testing.io);
    defer processor.deinit();

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try processor.parseDepFile(
        &capture,
        "module.o module.alias.o: " ++ src_path ++ " " ++ cfg_path ++ " include/generated/autoconf.h tail.so\n",
        "module.o",
    );

    try std.testing.expectEqualStrings(
        "source_module.o := " ++ src_path ++ "\n\n" ++
            "deps_module.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_SRC) \\\n" ++
            "  " ++ cfg_path ++ " \\\n" ++
            "    $(wildcard include/config/ZIGUX_CFG) \\\n" ++
            "  tail.so \\\n" ++
            "\n" ++
            "module.o: $(deps_module.o)\n\n" ++
            "$(deps_module.o):\n",
        capture.list.items,
    );
}
