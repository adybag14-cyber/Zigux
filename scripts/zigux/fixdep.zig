const builtin = @import("builtin");
const std = @import("std");
const Io = std.Io;

const max_file_bytes: usize = std.math.maxInt(usize);

const FixdepError = error{
    NoTargets,
    OpenDependencyFile,
    ReadDependencyFile,
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

fn bytesBeforeFirstNull(bytes: []const u8) []const u8 {
    return bytes[0 .. std.mem.indexOfScalar(u8, bytes, 0) orelse bytes.len];
}

fn describeFileReadError(err: anyerror) []const u8 {
    return switch (err) {
        error.FileNotFound => "No such file or directory",
        error.AccessDenied => "Permission denied",
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
        else => @errorName(err),
    };
}

fn emitOpenFileError(io: std.Io, path: []const u8, err: anyerror) !noreturn {
    var stderr_buffer: [512]u8 = undefined;
    var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
    const stderr = &stderr_writer.interface;
    try stderr.writeAll("fixdep: error opening file: ");
    try stderr.writeAll(path);
    try stderr.writeAll(": ");
    try stderr.writeAll(describeFileReadError(err));
    try stderr.writeAll("\n");
    try stderr.flush();
    std.process.exit(2);
}

fn writeReadFileError(writer: anytype, err: anyerror) !void {
    try writer.writeAll("fixdep: read: ");
    try writer.writeAll(describeFileReadError(err));
    try writer.writeAll("\n");
}

fn emitReadFileError(io: std.Io, err: anyerror) !noreturn {
    var stderr_buffer: [256]u8 = undefined;
    var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
    const stderr = &stderr_writer.interface;
    try writeReadFileError(stderr, err);
    try stderr.flush();
    std.process.exit(2);
}

fn writeOutputWriteError(writer: anytype) !void {
    try writer.writeAll("fixdep: not all data was written to the output\n");
}

fn emitOutputWriteError(io: std.Io) !noreturn {
    var stderr_buffer: [128]u8 = undefined;
    var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
    const stderr = &stderr_writer.interface;
    try writeOutputWriteError(stderr);
    try stderr.flush();
    std.process.exit(1);
}

fn flushOutputIgnoringError(writer: anytype) void {
    writer.flush() catch {};
}

fn flushOutputPreservingPrimaryError(writer: anytype, primary_err: anyerror) anyerror!void {
    flushOutputIgnoringError(writer);
    return primary_err;
}

const Processor = struct {
    io: std.Io,
    arena: std.heap.ArenaAllocator,
    config_seen: std.ArrayListUnmanaged([]const u8),
    file_seen: std.ArrayListUnmanaged([]const u8),
    last_file_error_path: []const u8,
    last_file_error: ?anyerror,

    pub fn init(backing_allocator: std.mem.Allocator, io: std.Io) Processor {
        var self: Processor = undefined;
        self.io = io;
        self.arena = std.heap.ArenaAllocator.init(backing_allocator);
        self.config_seen = .empty;
        self.file_seen = .empty;
        self.last_file_error_path = "";
        self.last_file_error = null;
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

    fn parseConfigFile(self: *Processor, writer: anytype, text: []const u8) !void {
        const visible_text = bytesBeforeFirstNull(text);
        var index: usize = 0;
        while (std.mem.indexOfPos(u8, visible_text, index, "CONFIG_")) |start| {
            if (start > 0 and isIdentByte(visible_text[start - 1])) {
                index = start + 7;
                continue;
            }

            var end: usize = start + 7;
            while (end < visible_text.len and isIdentByte(visible_text[end])) : (end += 1) {}

            var trimmed_end = end;
            const token = visible_text[start + 7 .. end];
            if (std.mem.endsWith(u8, token, "_MODULE")) {
                trimmed_end -= 7;
            }

            if (trimmed_end > start + 7) {
                try self.useConfig(writer, visible_text[start + 7 .. trimmed_end]);
            }
            index = end;
        }
    }

    fn captureOpenDependencyFileError(self: *Processor, path: []const u8, err: anyerror) !bool {
        switch (err) {
            error.FileNotFound,
            error.AccessDenied,
            error.IsDir,
            error.NotDir,
            error.NameTooLong,
            error.BadPathName,
            error.SymLinkLoop,
            error.ProcessFdQuotaExceeded,
            error.SystemFdQuotaExceeded,
            error.DeviceBusy,
            error.NoDevice,
            error.FileTooBig,
            error.InputOutput,
            => {
                self.last_file_error_path = try self.arena.allocator().dupe(u8, path);
                self.last_file_error = err;
                return true;
            },
            else => return false,
        }
    }

    fn readDependencyFile(self: *Processor, path: []const u8) ![]const u8 {
        const file = Io.Dir.cwd().openFile(self.io, path, .{
            .allow_directory = if (builtin.os.tag == .windows) false else true,
        }) catch |err| {
            if (try self.captureOpenDependencyFileError(path, err)) {
                return error.OpenDependencyFile;
            }
            return err;
        };
        defer file.close(self.io);

        var file_reader = file.reader(self.io, &.{});
        return file_reader.interface.allocRemaining(self.arena.allocator(), .limited(max_file_bytes)) catch |err| switch (err) {
            error.ReadFailed => {
                self.last_file_error_path = try self.arena.allocator().dupe(u8, path);
                self.last_file_error = file_reader.err.?;
                return error.ReadDependencyFile;
            },
            error.OutOfMemory, error.StreamTooLong => |e| return e,
        };
    }

    fn parseDepFile(self: *Processor, writer: anytype, dep_text_with_tail: []const u8, target: []const u8) !void {
        const dep_text = bytesBeforeFirstNull(dep_text_with_tail);
        var saw_any_target = false;
        var is_target = true;
        var is_source = false;
        var index: usize = 0;
        var token = try std.ArrayList(u8).initCapacity(self.arena.allocator(), 64);
        defer token.deinit(self.arena.allocator());

        while (index < dep_text.len) {
            switch (dep_text[index]) {
                '#' => {
                    index += 1;
                    while (index < dep_text.len and dep_text[index] != '\n') {
                        if (dep_text[index] == '\\' and index + 1 < dep_text.len) {
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
                    if (index + 1 < dep_text.len and dep_text[index + 1] == '\n') {
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
            while (cursor < dep_text.len and dep_text[cursor] != ' ' and dep_text[cursor] != '\t' and dep_text[cursor] != '\n' and dep_text[cursor] != '#' and dep_text[cursor] != ':') {
                if (dep_text[cursor] == '\\') {
                    if (cursor + 1 < dep_text.len and dep_text[cursor + 1] == '\n') {
                        break;
                    }
                    if (cursor + 1 < dep_text.len and (dep_text[cursor + 1] == '#' or dep_text[cursor + 1] == ':')) {
                        cursor += 1;
                        try token.append(self.arena.allocator(), dep_text[cursor]);
                        cursor += 1;
                        continue;
                    }
                    try token.append(self.arena.allocator(), dep_text[cursor]);
                    cursor += 1;
                    if (cursor == dep_text.len) {
                        break;
                    }
                    try token.append(self.arena.allocator(), dep_text[cursor]);
                    cursor += 1;
                    continue;
                }

                try token.append(self.arena.allocator(), dep_text[cursor]);
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
                    try writer.print("source_{s} := {s}\n\ndeps_{s} := \\\n", .{ target, token.items, target });
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
        error.OpenDependencyFile => {
            flushOutputIgnoringError(writer);
            try emitOpenFileError(io, processor.last_file_error_path, processor.last_file_error.?);
        },
        error.ReadDependencyFile => {
            flushOutputIgnoringError(writer);
            try emitReadFileError(io, processor.last_file_error.?);
        },
        else => return flushOutputPreservingPrimaryError(writer, err),
    };
    processor.parseDepFile(writer, dep_text, target) catch |err| switch (err) {
        error.OpenDependencyFile => {
            flushOutputIgnoringError(writer);
            try emitOpenFileError(io, processor.last_file_error_path, processor.last_file_error.?);
        },
        error.ReadDependencyFile => {
            flushOutputIgnoringError(writer);
            try emitReadFileError(io, processor.last_file_error.?);
        },
        else => return flushOutputPreservingPrimaryError(writer, err),
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
    const stdout = &stdout_writer.interface;

    runFixdep(arena, io, stdout, args[1], args[2], args[3]) catch |err| switch (err) {
        error.NoTargets => {
            flushOutputIgnoringError(stdout);
            try emitNoTargetsParseError(io);
        },
        else => return err,
    };
    stdout.flush() catch {
        try emitOutputWriteError(io);
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

test "config parsing ignores prefixed CONFIG tokens like upstream fixdep" {
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
        "UML_CONFIG_ZIGUX_CORE HELLO_CONFIG_ZIGUX_DEBUG_MODULE",
    );

    try std.testing.expectEqualStrings(
        "",
        capture.list.items,
    );
}

test "config parsing accepts CONFIG tokens after punctuation" {
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
        "(CONFIG_ZIGUX_WRAP) + CONFIG_ZIGUX_AFTER_MODULE",
    );

    try std.testing.expectEqualStrings(
        "    $(wildcard include/config/ZIGUX_WRAP) \\\n    $(wildcard include/config/ZIGUX_AFTER) \\\n",
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
        "CONFIG_ZIGUX_CORE\x00CONFIG_ZIGUX_AFTER_NUL",
    );

    try std.testing.expectEqualStrings(
        "    $(wildcard include/config/ZIGUX_CORE) \\\n",
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

test "dep parsing keeps escaped spaces inside tokens" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 160),
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
        "sample.o: sample.rmeta dep\\ name.rmeta\n",
        "sample.o",
    );

    try std.testing.expectEqualStrings(
        "source_sample.o := sample.rmeta\n\ndeps_sample.o := \\\n  dep\\ name.rmeta \\\n\nsample.o: $(deps_sample.o)\n\n$(deps_sample.o):\n",
        capture.list.items,
    );
}

test "dep parsing continues dependency lines across escaped newlines" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 192),
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
        "continued.o: continued.rmeta dep-first.so \\\n dep-second.so \\\n dep-third.so\n",
        "continued.o",
    );

    try std.testing.expectEqualStrings(
        "source_continued.o := continued.rmeta\n\ndeps_continued.o := \\\n" ++
            "  dep-first.so \\\n" ++
            "  dep-second.so \\\n" ++
            "  dep-third.so \\\n" ++
            "\n" ++
            "continued.o: $(deps_continued.o)\n\n" ++
            "$(deps_continued.o):\n",
        capture.list.items,
    );
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
        "sample.o: sample.rmeta\x00ignored.o: ignored.h\n",
        "sample.o",
    );

    try std.testing.expectEqualStrings(
        "source_sample.o := sample.rmeta\n\ndeps_sample.o := \\\n\nsample.o: $(deps_sample.o)\n\n$(deps_sample.o):\n",
        capture.list.items,
    );
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
}

test "open dependency file classification keeps input-output failures on the C-style path" {
    var processor = Processor.init(std.testing.allocator, std.testing.io);
    defer processor.deinit();

    try std.testing.expect(try processor.captureOpenDependencyFileError("broken.d", error.InputOutput));
    try std.testing.expectEqualStrings("broken.d", processor.last_file_error_path);
    try std.testing.expectEqual(error.InputOutput, processor.last_file_error.?);
}

test "open dependency file classification preserves unrelated open failures" {
    var processor = Processor.init(std.testing.allocator, std.testing.io);
    defer processor.deinit();

    try std.testing.expect(!(try processor.captureOpenDependencyFileError("broken.d", error.OutOfMemory)));
    try std.testing.expectEqualStrings("", processor.last_file_error_path);
    try std.testing.expect(processor.last_file_error == null);
}

test "read failure wording matches C perror prefix" {
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

        fn writeAll(self: *@This(), bytes: []const u8) !void {
            try self.list.appendSlice(self.allocator, bytes);
        }
    };

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try writeReadFileError(&capture, error.InputOutput);

    try std.testing.expectEqualStrings(
        "fixdep: read: Input/output error\n",
        capture.list.items,
    );
}

test "output write failure uses C-style wording" {
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

        fn writeAll(self: *@This(), bytes: []const u8) !void {
            try self.list.appendSlice(self.allocator, bytes);
        }
    };

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try writeOutputWriteError(&capture);

    try std.testing.expectEqualStrings(
        "fixdep: not all data was written to the output\n",
        capture.list.items,
    );
}

test "flush helper preserves the primary error" {
    const FlushFailWriter = struct {
        fn flush(_: *@This()) !void {
            return error.FlushFailed;
        }
    };

    var writer = FlushFailWriter{};
    try std.testing.expectError(
        error.PrimaryFailure,
        flushOutputPreservingPrimaryError(&writer, error.PrimaryFailure),
    );
}

test "dependency file reads beyond the legacy one mebibyte ceiling" {
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

    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const padding_len = (1024 * 1024) + 64;
    const header = "sample.o: sample.rmeta\n# ";
    var file_bytes = try std.ArrayList(u8).initCapacity(std.testing.allocator, header.len + padding_len + 1);
    defer file_bytes.deinit(std.testing.allocator);
    try file_bytes.appendSlice(std.testing.allocator, header);
    try file_bytes.appendNTimes(std.testing.allocator, 'a', padding_len);
    try file_bytes.append(std.testing.allocator, '\n');

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "large.d",
        .data = file_bytes.items,
    });

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/large.d",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(depfile_path);

    const dep_text = try processor.readDependencyFile(depfile_path);
    try std.testing.expect(dep_text.len > 1024 * 1024);
    try processor.parseDepFile(&capture, dep_text, "sample.o");
    try std.testing.expectEqualStrings(
        "source_sample.o := sample.rmeta\n\ndeps_sample.o := \\\n\nsample.o: $(deps_sample.o)\n\n$(deps_sample.o):\n",
        capture.list.items,
    );
}

test "escaped hash dependency survives concatenated target comment path" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 160),
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
        "sample.o: sample.rmeta dir\\#crate.rmeta \\\n# generated by rustc\\\\\n  still comment\nmodule/sample.o: temp.rmeta later.rmeta\n",
        "sample.o",
    );

    try std.testing.expectEqualStrings(
        "source_sample.o := sample.rmeta\n\ndeps_sample.o := \\\n  dir#crate.rmeta \\\n  later.rmeta \\\n\nsample.o: $(deps_sample.o)\n\n$(deps_sample.o):\n",
        capture.list.items,
    );
}

test "escaped colon dependency survives concatenated target comment path" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 160),
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
        "sample.o: sample.rmeta dir\\:crate.rmeta \\\n# generated by rustc\\\\\n  still comment\nmodule/sample.o: temp.rmeta later.rmeta\n",
        "sample.o",
    );

    try std.testing.expectEqualStrings(
        "source_sample.o := sample.rmeta\n\ndeps_sample.o := \\\n  dir:crate.rmeta \\\n  later.rmeta \\\n\nsample.o: $(deps_sample.o)\n\n$(deps_sample.o):\n",
        capture.list.items,
    );
}