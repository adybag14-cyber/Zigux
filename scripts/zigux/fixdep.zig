const builtin = @import("builtin");
const std = @import("std");
const Io = std.Io;

const max_file_bytes: usize = std.math.maxInt(usize);

const FixdepError = error{
    NoTargets,
    OpenDependencyFile,
    StatDependencyFile,
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

fn lineBreakLen(bytes: []const u8, index: usize) usize {
    if (bytes[index] == '\r' and index + 1 < bytes.len and bytes[index + 1] == '\n') {
        return 2;
    }
    return 1;
}

fn lineContinuationLen(bytes: []const u8, index: usize) ?usize {
    if (bytes[index] != '\\' or index + 1 >= bytes.len) return null;
    return switch (bytes[index + 1]) {
        '\n' => 2,
        '\r' => if (index + 2 < bytes.len and bytes[index + 2] == '\n') 3 else null,
        else => null,
    };
}

fn isBareCarriageReturnEscape(bytes: []const u8, index: usize) bool {
    return bytes[index] == '\\' and
        index + 1 < bytes.len and
        bytes[index + 1] == '\r' and
        (index + 2 >= bytes.len or bytes[index + 2] != '\n');
}

fn describeFileReadError(err: anyerror) []const u8 {
    return switch (err) {
        error.FileNotFound => "No such file or directory",
        error.AccessDenied, error.PermissionDenied => "Permission denied",
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
        error.EndOfStream => "Unexpected end of file",
        else => @errorName(err),
    };
}

fn expectExactReadSize(bytes: []const u8, expected_size: usize) ![]const u8 {
    if (bytes.len != expected_size) return error.EndOfStream;
    return bytes;
}

fn writePathError(writer: anytype, prefix: []const u8, path: []const u8, err: anyerror) !void {
    try writer.writeAll(prefix);
    try writer.writeAll(path);
    try writer.writeAll(": ");
    try writer.writeAll(describeFileReadError(err));
    try writer.writeAll("\n");
}

fn emitPathError(io: std.Io, prefix: []const u8, path: []const u8, err: anyerror) !noreturn {
    var stderr_buffer: [512]u8 = undefined;
    var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
    const stderr = &stderr_writer.interface;
    try writePathError(stderr, prefix, path, err);
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
    config_seen: std.StringHashMapUnmanaged(void),
    file_seen: std.StringHashMapUnmanaged(void),
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

    fn remember(self: *Processor, table: *std.StringHashMapUnmanaged(void), token: []const u8) !bool {
        if (table.contains(token)) {
            return true;
        }

        const copy = try self.arena.allocator().dupe(u8, token);
        try table.put(self.arena.allocator(), copy, {});
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

        const file_stat = file.stat(self.io) catch |err| {
            self.last_file_error_path = try self.arena.allocator().dupe(u8, path);
            self.last_file_error = err;
            return error.StatDependencyFile;
        };
        const expected_size = std.math.cast(usize, file_stat.size) orelse return error.StreamTooLong;
        const read_limit: std.Io.Limit = if (expected_size == std.math.maxInt(usize))
            .unlimited
        else
            .limited(expected_size + 1);

        var file_reader = file.reader(self.io, &.{});
        const dependency_text = file_reader.interface.allocRemaining(self.arena.allocator(), read_limit) catch |err| switch (err) {
            error.ReadFailed => {
                self.last_file_error_path = try self.arena.allocator().dupe(u8, path);
                self.last_file_error = file_reader.err.?;
                return error.ReadDependencyFile;
            },
            error.OutOfMemory, error.StreamTooLong => |e| return e,
        };
        return expectExactReadSize(dependency_text, expected_size) catch |err| {
            self.last_file_error_path = try self.arena.allocator().dupe(u8, path);
            self.last_file_error = err;
            return error.ReadDependencyFile;
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
                    while (index < dep_text.len and dep_text[index] != '\n' and dep_text[index] != '\r') {
                        if (lineContinuationLen(dep_text, index)) |continuation_len| {
                            index += continuation_len;
                            continue;
                        }
                        if (isBareCarriageReturnEscape(dep_text, index)) {
                            index += 1;
                            continue;
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
                    if (lineContinuationLen(dep_text, index)) |continuation_len| {
                        index += continuation_len;
                        continue;
                    }
                    if (isBareCarriageReturnEscape(dep_text, index)) {
                        index += 1;
                        continue;
                    }
                },
                '\n', '\r' => {
                    index += lineBreakLen(dep_text, index);
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
            while (cursor < dep_text.len and dep_text[cursor] != ' ' and dep_text[cursor] != '\t' and dep_text[cursor] != '\n' and dep_text[cursor] != '\r' and dep_text[cursor] != '#' and dep_text[cursor] != ':') {
                if (dep_text[cursor] == '\\') {
                    if (lineContinuationLen(dep_text, cursor) != null or isBareCarriageReturnEscape(dep_text, cursor)) {
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
            try emitPathError(io, "fixdep: error opening file: ", processor.last_file_error_path, processor.last_file_error.?);
        },
        error.StatDependencyFile => {
            flushOutputIgnoringError(writer);
            try emitPathError(io, "fixdep: error fstat'ing file: ", processor.last_file_error_path, processor.last_file_error.?);
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
            try emitPathError(io, "fixdep: error opening file: ", processor.last_file_error_path, processor.last_file_error.?);
        },
        error.StatDependencyFile => {
            flushOutputIgnoringError(writer);
            try emitPathError(io, "fixdep: error fstat'ing file: ", processor.last_file_error_path, processor.last_file_error.?);
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
