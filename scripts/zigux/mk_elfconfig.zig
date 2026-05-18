const std = @import("std");
const Io = std.Io;

const ei_nident: usize = 16;
const ei_class: usize = 4;
const elf_magic = [_]u8{ 0x7f, 'E', 'L', 'F' };
const elfclass32: u8 = 1;
const elfclass64: u8 = 2;

const truncated_text = "Error: input truncated\n";
const not_elf_text = "Error: not ELF\n";
const elfclass32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elfclass64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";

const HeaderReadResult = struct {
    bytes: [ei_nident]u8,
    len: usize,
};

pub const Outcome = enum {
    elf32,
    elf64,
    truncated,
    not_elf,
    invalid_class,
};

pub fn classify(header: []const u8) Outcome {
    if (header.len < ei_nident) {
        return .truncated;
    }
    if (!std.mem.eql(u8, header[0..elf_magic.len], &elf_magic)) {
        return .not_elf;
    }
    return switch (header[ei_class]) {
        elfclass32 => .elf32,
        elfclass64 => .elf64,
        else => .invalid_class,
    };
}

pub fn renderOutcome(stdout: anytype, stderr: anytype, outcome: Outcome) !u8 {
    switch (outcome) {
        .elf32 => {
            try stdout.writeAll(elfclass32_define);
            return 0;
        },
        .elf64 => {
            try stdout.writeAll(elfclass64_define);
            return 0;
        },
        .truncated => {
            try stderr.writeAll(truncated_text);
            return 1;
        },
        .not_elf => {
            try stderr.writeAll(not_elf_text);
            return 1;
        },
        .invalid_class => return 1,
    }
}

pub fn runMkElfconfig(stdin_bytes: []const u8, stdout: anytype, stderr: anytype) !u8 {
    return renderOutcome(stdout, stderr, classify(stdin_bytes));
}

fn runMkElfconfigFromReader(reader: anytype, stdout: anytype, stderr: anytype) !u8 {
    const header = try readHeaderFromReader(reader);
    return renderOutcome(stdout, stderr, classify(header.bytes[0..header.len]));
}

fn readHeaderFromReader(reader: anytype) !HeaderReadResult {
    var header: [ei_nident]u8 = undefined;
    var filled: usize = 0;
    while (filled < header.len) {
        const count = reader.read(header[filled..]) catch break;
        if (count == 0) break;
        filled += count;
    }
    return .{ .bytes = header, .len = filled };
}

fn readHeader(fd: std.posix.fd_t) !HeaderReadResult {
    var reader = FdReader{ .fd = fd };
    return readHeaderFromReader(&reader);
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [128]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    var stderr_buffer: [128]u8 = undefined;
    var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
    var reader = FdReader{ .fd = std.posix.STDIN_FILENO };
    const exit_code = try runMkElfconfigFromReader(
        &reader,
        &stdout_writer.interface,
        &stderr_writer.interface,
    );
    try stdout_writer.interface.flush();
    try stderr_writer.interface.flush();
    std.process.exit(exit_code);
}

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

const FdReader = struct {
    fd: std.posix.fd_t,

    fn read(self: *@This(), buffer: []u8) !usize {
        return std.posix.read(self.fd, buffer);
    }
};

const SplitReader = struct {
    bytes: []const u8,
    chunk_sizes: []const usize,
    offset: usize = 0,
    read_index: usize = 0,
    call_count: usize = 0,

    fn read(self: *@This(), buffer: []u8) !usize {
        self.call_count += 1;
        if (self.offset >= self.bytes.len or self.read_index >= self.chunk_sizes.len) {
            return 0;
        }

        const planned = self.chunk_sizes[self.read_index];
        self.read_index += 1;

        const remaining = self.bytes.len - self.offset;
        const count = @min(planned, @min(buffer.len, remaining));
        @memcpy(buffer[0..count], self.bytes[self.offset .. self.offset + count]);
        self.offset += count;
        return count;
    }
};

const FailingReader = struct {
    bytes: []const u8,
    chunk_sizes: []const usize,
    fail_on_call: usize,
    offset: usize = 0,
    read_index: usize = 0,
    call_count: usize = 0,

    const ReadError = error{InjectedFailure};

    fn read(self: *@This(), buffer: []u8) ReadError!usize {
        self.call_count += 1;
        if (self.call_count == self.fail_on_call) {
            return error.InjectedFailure;
        }
        if (self.offset >= self.bytes.len or self.read_index >= self.chunk_sizes.len) {
            return 0;
        }

        const planned = self.chunk_sizes[self.read_index];
        self.read_index += 1;

        const remaining = self.bytes.len - self.offset;
        const count = @min(planned, @min(buffer.len, remaining));
        @memcpy(buffer[0..count], self.bytes[self.offset .. self.offset + count]);
        self.offset += count;
        return count;
    }
};

test "classifies 32-bit ELF header" {
    const header = [_]u8{ 0x7f, 'E', 'L', 'F', elfclass32, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    try std.testing.expectEqual(Outcome.elf32, classify(&header));
}

test "classifies 32-bit ELF input even when trailing bytes are present" {
    const header = [_]u8{
        0x7f, 'E',  'L',  'F', elfclass32, 1, 1, 0,
        0,    0,    0,    0,   0,          0, 0, 0,
        0xaa, 0xbb, 0xcc,
    };
    try std.testing.expectEqual(Outcome.elf32, classify(&header));
}

test "classifies 64-bit ELF header" {
    const header = [_]u8{ 0x7f, 'E', 'L', 'F', elfclass64, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    try std.testing.expectEqual(Outcome.elf64, classify(&header));
}

test "classifies truncated input before checking magic" {
    const header = [_]u8{ 0x7f, 'E', 'L', 'F', elfclass32, 1, 1, 0 };
    try std.testing.expectEqual(Outcome.truncated, classify(&header));
}

test "classifies non-ELF input" {
    const header = [_]u8{ 0x00, 'E', 'L', 'F', elfclass32, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    try std.testing.expectEqual(Outcome.not_elf, classify(&header));
}

test "classifies non-ELF input with trailing bytes" {
    const header = [_]u8{
        0x00, 'E',  'L',  'F', elfclass32, 1, 1, 0,
        0,    0,    0,    0,   0,          0, 0, 0,
        0xaa, 0xbb, 0xcc,
    };
    try std.testing.expectEqual(Outcome.not_elf, classify(&header));
}

test "classifies unsupported ELF class silently" {
    const header = [_]u8{ 0x7f, 'E', 'L', 'F', 3, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    try std.testing.expectEqual(Outcome.invalid_class, classify(&header));
}

test "classifies unsupported ELF class with trailing bytes silently" {
    const header = [_]u8{
        0x7f, 'E',  'L',  'F', 3, 1, 1, 0,
        0,    0,    0,    0,   0, 0, 0, 0,
        0xaa, 0xbb, 0xcc,
    };
    try std.testing.expectEqual(Outcome.invalid_class, classify(&header));
}

test "classifies valid ELF input even when trailing bytes are present" {
    const header = [_]u8{
        0x7f, 'E',  'L',  'F', elfclass64, 1, 1, 0,
        0,    0,    0,    0,   0,          0, 0, 0,
        0xaa, 0xbb, 0xcc,
    };
    try std.testing.expectEqual(Outcome.elf64, classify(&header));
}

test "readHeader returns zero bytes on immediate EOF" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "empty.bin", .{ .read = true });
    defer file.close(io);

    const header = try readHeader(file.handle);
    try std.testing.expectEqual(@as(usize, 0), header.len);
}

test "readHeader stops after filling the first ELF header across split reads" {
    var reader = SplitReader{
        .bytes = &[_]u8{
            0x7f, 'E',  'L',  'F',  elfclass64, 1, 1, 0,
            0,    0,    0,    0,    0,          0, 0, 0,
            0xaa, 0xbb, 0xcc, 0xdd,
        },
        .chunk_sizes = &[_]usize{ 5, 3, 8, 4 },
    };

    const header = try readHeaderFromReader(&reader);
    try std.testing.expectEqual(@as(usize, ei_nident), header.len);
    try std.testing.expectEqual(@as(usize, 3), reader.call_count);
    try std.testing.expectEqualSlices(u8, &[_]u8{
        0x7f, 'E', 'L', 'F', elfclass64, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    }, header.bytes[0..header.len]);
}

test "readHeader preserves truncated byte count across split reads" {
    var reader = SplitReader{
        .bytes = &[_]u8{ 0x7f, 'E', 'L', 'F', elfclass32, 1, 1, 0 },
        .chunk_sizes = &[_]usize{ 3, 2, 3 },
    };

    const header = try readHeaderFromReader(&reader);
    try std.testing.expectEqual(@as(usize, 8), header.len);
    try std.testing.expectEqual(@as(usize, 4), reader.call_count);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x7f, 'E', 'L', 'F', elfclass32, 1, 1, 0 }, header.bytes[0..header.len]);
}

test "readHeader treats an immediate read error like truncated input" {
    var reader = FailingReader{
        .bytes = &[_]u8{},
        .chunk_sizes = &[_]usize{},
        .fail_on_call = 1,
    };

    const header = try readHeaderFromReader(&reader);
    try std.testing.expectEqual(@as(usize, 0), header.len);
    try std.testing.expectEqual(@as(usize, 1), reader.call_count);
}

test "readHeader keeps partial bytes when a later read fails" {
    var reader = FailingReader{
        .bytes = &[_]u8{ 0x7f, 'E', 'L', 'F', elfclass32, 1, 1, 0 },
        .chunk_sizes = &[_]usize{ 8, 8 },
        .fail_on_call = 2,
    };

    const header = try readHeaderFromReader(&reader);
    try std.testing.expectEqual(@as(usize, 8), header.len);
    try std.testing.expectEqual(@as(usize, 2), reader.call_count);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x7f, 'E', 'L', 'F', elfclass32, 1, 1, 0 }, header.bytes[0..header.len]);
}

test "readHeader stops at the first ELF header" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "header.bin", .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, &[_]u8{
        0x7f, 'E',  'L',  'F',  elfclass64, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0xaa, 0xbb, 0xcc, 0xdd,
    }, 0);

    const header = try readHeader(file.handle);
    try std.testing.expectEqual(@as(usize, ei_nident), header.len);
    try std.testing.expectEqualSlices(u8, &[_]u8{
        0x7f, 'E', 'L', 'F', elfclass64, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    }, header.bytes[0..header.len]);
}

test "readHeader reports the exact truncated byte count" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "truncated.bin", .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, &[_]u8{ 0x7f, 'E', 'L', 'F', elfclass32, 1, 1, 0 }, 0);

    const header = try readHeader(file.handle);
    try std.testing.expectEqual(@as(usize, 8), header.len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x7f, 'E', 'L', 'F', elfclass32, 1, 1, 0 }, header.bytes[0..header.len]);
}

test "renders 32-bit define" {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try renderOutcome(&stdout, &stderr, .elf32);
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqualStrings(elfclass32_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "renders 64-bit define" {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try renderOutcome(&stdout, &stderr, .elf64);
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqualStrings(elfclass64_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "renders truncated error" {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try renderOutcome(&stdout, &stderr, .truncated);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(truncated_text, stderr.list.items);
}

test "renders non-ELF error" {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try renderOutcome(&stdout, &stderr, .not_elf);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(not_elf_text, stderr.list.items);
}

test "renders invalid class silently" {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try renderOutcome(&stdout, &stderr, .invalid_class);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "32-bit ELF input exits with stdout" {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfig(
        &[_]u8{ 0x7f, 'E', 'L', 'F', elfclass32, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
        &stdout,
        &stderr,
    );
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqualStrings(elfclass32_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "32-bit ELF input with trailing bytes exits with stdout" {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfig(
        &[_]u8{
            0x7f, 'E',  'L', 'F', elfclass32, 1, 1, 0,
            0,    0,    0,   0,   0,          0, 0, 0,
            0xaa, 0xbb,
        },
        &stdout,
        &stderr,
    );
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqualStrings(elfclass32_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "64-bit ELF input exits with stdout" {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfig(
        &[_]u8{ 0x7f, 'E', 'L', 'F', elfclass64, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
        &stdout,
        &stderr,
    );
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqualStrings(elfclass64_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "valid ELF input with trailing bytes exits with stdout" {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfig(
        &[_]u8{
            0x7f, 'E',  'L', 'F', elfclass64, 1, 1, 0,
            0,    0,    0,   0,   0,          0, 0, 0,
            0xaa, 0xbb,
        },
        &stdout,
        &stderr,
    );
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqualStrings(elfclass64_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "empty input exits with stderr" {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfig(&[_]u8{}, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(truncated_text, stderr.list.items);
}

test "truncated input exits with stderr" {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfig(
        &[_]u8{ 0x7f, 'E', 'L', 'F', elfclass32, 1, 1, 0 },
        &stdout,
        &stderr,
    );
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(truncated_text, stderr.list.items);
}

test "non-ELF input exits with stderr" {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfig(
        &[_]u8{ 0x00, 'E', 'L', 'F', elfclass32, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
        &stdout,
        &stderr,
    );
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(not_elf_text, stderr.list.items);
}

test "non-ELF input with trailing bytes exits with stderr" {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfig(
        &[_]u8{
            0x00, 'E',  'L', 'F', elfclass32, 1, 1, 0,
            0,    0,    0,   0,   0,          0, 0, 0,
            0xaa, 0xbb,
        },
        &stdout,
        &stderr,
    );
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(not_elf_text, stderr.list.items);
}

test "invalid class exits without stderr" {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfig(
        &[_]u8{ 0x7f, 'E', 'L', 'F', 3, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
        &stdout,
        &stderr,
    );
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "invalid class input with trailing bytes exits silently" {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfig(
        &[_]u8{
            0x7f, 'E',  'L', 'F', 3, 1, 1, 0,
            0,    0,    0,   0,   0, 0, 0, 0,
            0xaa, 0xbb,
        },
        &stdout,
        &stderr,
    );
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "split-read ELF input exits with stdout and ignores trailing bytes" {
    var reader = SplitReader{
        .bytes = &[_]u8{
            0x7f, 'E',  'L',  'F', elfclass64, 1, 1, 0,
            0,    0,    0,    0,   0,          0, 0, 0,
            0xaa, 0xbb, 0xcc,
        },
        .chunk_sizes = &[_]usize{ 4, 4, 8, 3 },
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfigFromReader(&reader, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqual(@as(usize, 3), reader.call_count);
    try std.testing.expectEqualStrings(elfclass64_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "split-read 32-bit ELF input exits with stdout and ignores trailing bytes" {
    var reader = SplitReader{
        .bytes = &[_]u8{
            0x7f, 'E',  'L',  'F', elfclass32, 1, 1, 0,
            0,    0,    0,    0,   0,          0, 0, 0,
            0xaa, 0xbb, 0xcc,
        },
        .chunk_sizes = &[_]usize{ 6, 5, 5, 3 },
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfigFromReader(&reader, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqual(@as(usize, 3), reader.call_count);
    try std.testing.expectEqualStrings(elfclass32_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "split-read full 32-bit header in first chunk exits after one read" {
    var reader = SplitReader{
        .bytes = &[_]u8{
            0x7f, 'E',  'L',  'F', elfclass32, 1, 1, 0,
            0,    0,    0,    0,   0,          0, 0, 0,
            0xaa, 0xbb, 0xcc,
        },
        .chunk_sizes = &[_]usize{ 16, 3 },
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfigFromReader(&reader, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqual(@as(usize, 1), reader.call_count);
    try std.testing.expectEqualStrings(elfclass32_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "split-read full 64-bit header in first chunk exits after one read" {
    var reader = SplitReader{
        .bytes = &[_]u8{
            0x7f, 'E',  'L',  'F', elfclass64, 1, 1, 0,
            0,    0,    0,    0,   0,          0, 0, 0,
            0xaa, 0xbb, 0xcc,
        },
        .chunk_sizes = &[_]usize{ 16, 3 },
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfigFromReader(&reader, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqual(@as(usize, 1), reader.call_count);
    try std.testing.expectEqualStrings(elfclass64_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "split-read exact 32-bit ELF header in first chunk exits after one read" {
    var reader = SplitReader{
        .bytes = &[_]u8{
            0x7f, 'E', 'L', 'F', elfclass32, 1, 1, 0,
            0,    0,   0,   0,   0,          0, 0, 0,
        },
        .chunk_sizes = &[_]usize{ 16, 4 },
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfigFromReader(&reader, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqual(@as(usize, 1), reader.call_count);
    try std.testing.expectEqualStrings(elfclass32_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "split-read exact 64-bit ELF header in first chunk exits after one read" {
    var reader = SplitReader{
        .bytes = &[_]u8{
            0x7f, 'E', 'L', 'F', elfclass64, 1, 1, 0,
            0,    0,   0,   0,   0,          0, 0, 0,
        },
        .chunk_sizes = &[_]usize{ 16, 4 },
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfigFromReader(&reader, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqual(@as(usize, 1), reader.call_count);
    try std.testing.expectEqualStrings(elfclass64_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "split-read full invalid-class header in first chunk exits after one read" {
    var reader = SplitReader{
        .bytes = &[_]u8{
            0x7f, 'E',  'L',  'F', 3, 1, 1, 0,
            0,    0,    0,    0,   0, 0, 0, 0,
            0xaa, 0xbb, 0xcc,
        },
        .chunk_sizes = &[_]usize{ 16, 3 },
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfigFromReader(&reader, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqual(@as(usize, 1), reader.call_count);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "split-read exact invalid-class header in first chunk exits after one read" {
    var reader = SplitReader{
        .bytes = &[_]u8{
            0x7f, 'E', 'L', 'F', 3, 1, 1, 0,
            0,    0,   0,   0,   0, 0, 0, 0,
        },
        .chunk_sizes = &[_]usize{ 16, 4 },
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfigFromReader(&reader, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqual(@as(usize, 1), reader.call_count);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "split-read full non-ELF header in first chunk exits after one read" {
    var reader = SplitReader{
        .bytes = &[_]u8{
            0x00, 'E',  'L',  'F', elfclass32, 1, 1, 0,
            0,    0,    0,    0,   0,          0, 0, 0,
            0xaa, 0xbb, 0xcc,
        },
        .chunk_sizes = &[_]usize{ 16, 3 },
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfigFromReader(&reader, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqual(@as(usize, 1), reader.call_count);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(not_elf_text, stderr.list.items);
}

test "split-read exact non-ELF header in first chunk exits after one read" {
    var reader = SplitReader{
        .bytes = &[_]u8{
            0x00, 'E', 'L', 'F', elfclass32, 1, 1, 0,
            0,    0,   0,   0,   0,          0, 0, 0,
        },
        .chunk_sizes = &[_]usize{ 16, 4 },
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfigFromReader(&reader, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqual(@as(usize, 1), reader.call_count);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(not_elf_text, stderr.list.items);
}

test "split-read exact 32-bit ELF header exits with stdout at EOF" {
    var reader = SplitReader{
        .bytes = &[_]u8{
            0x7f, 'E', 'L', 'F', elfclass32, 1, 1, 0,
            0,    0,   0,   0,   0,          0, 0, 0,
        },
        .chunk_sizes = &[_]usize{ 5, 4, 7 },
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfigFromReader(&reader, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqual(@as(usize, 3), reader.call_count);
    try std.testing.expectEqualStrings(elfclass32_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "split-read exact 64-bit ELF header exits with stdout at EOF" {
    var reader = SplitReader{
        .bytes = &[_]u8{
            0x7f, 'E', 'L', 'F', elfclass64, 1, 1, 0,
            0,    0,   0,   0,   0,          0, 0, 0,
        },
        .chunk_sizes = &[_]usize{ 3, 6, 7 },
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfigFromReader(&reader, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqual(@as(usize, 3), reader.call_count);
    try std.testing.expectEqualStrings(elfclass64_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "split-read exact invalid-class header exits silently at EOF" {
    var reader = SplitReader{
        .bytes = &[_]u8{
            0x7f, 'E', 'L', 'F', 3, 1, 1, 0,
            0,    0,   0,   0,   0, 0, 0, 0,
        },
        .chunk_sizes = &[_]usize{ 6, 3, 7 },
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfigFromReader(&reader, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqual(@as(usize, 3), reader.call_count);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "split-read exact non-ELF header exits with stderr at EOF" {
    var reader = SplitReader{
        .bytes = &[_]u8{
            0x00, 'E', 'L', 'F', elfclass32, 1, 1, 0,
            0,    0,   0,   0,   0,          0, 0, 0,
        },
        .chunk_sizes = &[_]usize{ 4, 5, 7 },
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfigFromReader(&reader, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqual(@as(usize, 3), reader.call_count);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(not_elf_text, stderr.list.items);
}

test "split-read empty input exits with stderr after immediate EOF" {
    var reader = SplitReader{
        .bytes = &[_]u8{},
        .chunk_sizes = &[_]usize{},
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfigFromReader(&reader, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqual(@as(usize, 1), reader.call_count);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(truncated_text, stderr.list.items);
}

test "split-read invalid class exits silently and ignores trailing bytes" {
    var reader = SplitReader{
        .bytes = &[_]u8{
            0x7f, 'E',  'L',  'F', 3, 1, 1, 0,
            0,    0,    0,    0,   0, 0, 0, 0,
            0xaa, 0xbb, 0xcc,
        },
        .chunk_sizes = &[_]usize{ 6, 4, 6, 3 },
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfigFromReader(&reader, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqual(@as(usize, 3), reader.call_count);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "split-read non-ELF input exits with stderr and ignores trailing bytes" {
    var reader = SplitReader{
        .bytes = &[_]u8{
            0x00, 'E',  'L',  'F', elfclass32, 1, 1, 0,
            0,    0,    0,    0,   0,          0, 0, 0,
            0xaa, 0xbb, 0xcc,
        },
        .chunk_sizes = &[_]usize{ 7, 2, 7, 3 },
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfigFromReader(&reader, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqual(@as(usize, 3), reader.call_count);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(not_elf_text, stderr.list.items);
}

test "split-read truncated input exits with stderr after final EOF read" {
    var reader = SplitReader{
        .bytes = &[_]u8{ 0x7f, 'E', 'L', 'F', elfclass32, 1, 1, 0 },
        .chunk_sizes = &[_]usize{ 2, 2, 4 },
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfigFromReader(&reader, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqual(@as(usize, 4), reader.call_count);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(truncated_text, stderr.list.items);
}

test "split-read immediate read error exits with stderr" {
    var reader = FailingReader{
        .bytes = &[_]u8{},
        .chunk_sizes = &[_]usize{},
        .fail_on_call = 1,
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfigFromReader(&reader, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqual(@as(usize, 1), reader.call_count);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(truncated_text, stderr.list.items);
}

test "split-read later read error exits with truncated stderr" {
    var reader = FailingReader{
        .bytes = &[_]u8{ 0x7f, 'E', 'L', 'F', elfclass32, 1, 1, 0 },
        .chunk_sizes = &[_]usize{ 8, 8 },
        .fail_on_call = 2,
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runMkElfconfigFromReader(&reader, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqual(@as(usize, 2), reader.call_count);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(truncated_text, stderr.list.items);
}
