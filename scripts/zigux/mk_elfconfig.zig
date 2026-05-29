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

fn readHeader(fd: std.posix.fd_t) !struct { bytes: [ei_nident]u8, len: usize } {
    var header: [ei_nident]u8 = undefined;
    var filled: usize = 0;
    while (filled < header.len) {
        const count = try std.posix.read(fd, header[filled..]);
        if (count == 0) break;
        filled += count;
    }
    return .{ .bytes = header, .len = filled };
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    const header = try readHeader(std.posix.STDIN_FILENO);
    var stdout_buffer: [128]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    var stderr_buffer: [128]u8 = undefined;
    var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
    const exit_code = try renderOutcome(
        &stdout_writer.interface,
        &stderr_writer.interface,
        classify(header.bytes[0..header.len]),
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

test "classifies 32-bit ELF header" {
    const header = [_]u8{ 0x7f, 'E', 'L', 'F', elfclass32, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
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

test "classifies unsupported ELF class silently" {
    const header = [_]u8{ 0x7f, 'E', 'L', 'F', 3, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    try std.testing.expectEqual(Outcome.invalid_class, classify(&header));
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

test "ELF64 prefix ignores trailing ELF32 header" {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const elf64_header = [_]u8{ 0x7f, 'E', 'L', 'F', elfclass64, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const trailing_elf32 = [_]u8{ 0x7f, 'E', 'L', 'F', elfclass32, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const stdin_bytes = elf64_header ++ trailing_elf32;

    const exit_code = try runMkElfconfig(&stdin_bytes, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqualStrings(elfclass64_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}
