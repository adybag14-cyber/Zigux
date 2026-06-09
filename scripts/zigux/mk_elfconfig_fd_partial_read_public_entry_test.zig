const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elfclass32: u8 = 1;
const elfclass64: u8 = 2;
const elfclass32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elfclass64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";
const truncated_text = "Error: input truncated\n";
const not_elf_text = "Error: not ELF\n";
const chunk_delay = std.os.linux.timespec{ .sec = 0, .nsec = 2 * 1000 * 1000 };

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

    pub fn writeAll(self: *@This(), bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }
};

const PipeScript = struct {
    write_fd: std.posix.fd_t,
    chunks: []const []const u8,
};

fn closeFd(fd: std.posix.fd_t) void {
    _ = std.os.linux.close(fd);
}

fn writeAllToFd(fd: std.posix.fd_t, bytes: []const u8) !void {
    var written: usize = 0;
    while (written < bytes.len) {
        const rc = std.os.linux.write(fd, bytes[written..].ptr, bytes.len - written);
        switch (std.posix.errno(rc)) {
            .SUCCESS => written += @intCast(rc),
            .INTR => continue,
            .INVAL => unreachable,
            .FAULT => unreachable,
            .BADF => return error.Unexpected,
            .FBIG => return error.FileTooBig,
            .IO => return error.InputOutput,
            .NOSPC => return error.NoSpaceLeft,
            .PERM => return error.AccessDenied,
            .PIPE => return error.BrokenPipe,
            else => |err| return std.posix.unexpectedErrno(err),
        }
    }
}

fn sleepBetweenChunks() void {
    _ = std.os.linux.nanosleep(&chunk_delay, null);
}

fn writePipeChunks(script: PipeScript) !void {
    defer closeFd(script.write_fd);
    for (script.chunks) |chunk| {
        try writeAllToFd(script.write_fd, chunk);
        sleepBetweenChunks();
    }
}

fn makePipe() ![2]std.posix.fd_t {
    var fds: [2]std.posix.fd_t = undefined;
    switch (std.posix.errno(std.os.linux.pipe(&fds))) {
        .SUCCESS => return fds,
        .FAULT => unreachable,
        .INVAL => unreachable,
        .MFILE => return error.ProcessFdQuotaExceeded,
        .NFILE => return error.SystemFdQuotaExceeded,
        else => |err| return std.posix.unexpectedErrno(err),
    }
}

fn runFromPipeChunks(chunks: []const []const u8, stdout: anytype, stderr: anytype) !u8 {
    const fds = try makePipe();
    defer closeFd(fds[0]);

    const writer = try std.Thread.spawn(.{}, writePipeChunks, .{PipeScript{
        .write_fd = fds[1],
        .chunks = chunks,
    }});
    defer writer.join();

    return mk_elfconfig.runMkElfconfigFromFd(fds[0], stdout, stderr);
}

test "fd-backed partial reads assemble ELF64 ident before classifying" {
    const header = [_]u8{
        0x7f, 'E', 'L', 'F', elfclass64, 1, 1, 0,
        0,    0,   0,   0,   0,          0, 0, 0,
    };
    const chunks = [_][]const u8{
        header[0..1],
        header[1..4],
        header[4..7],
        header[7..16],
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runFromPipeChunks(&chunks, &stdout, &stderr);

    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqualStrings(elfclass64_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "fd-backed partial reads report truncation only after chunked EOF" {
    const chunks = [_][]const u8{
        &[_]u8{ 0x7f, 'E' },
        &[_]u8{ 'L', 'F', elfclass32, 1 },
        &[_]u8{ 1, 0, 0, 0, 0 },
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runFromPipeChunks(&chunks, &stdout, &stderr);

    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(truncated_text, stderr.list.items);
}

test "fd-backed partial reads keep first full non-ELF ident authoritative" {
    const header = [_]u8{
        0x00, 'E', 'L', 'F', elfclass32, 1, 1, 0,
        0,    0,   0,   0,   0,          0, 0, 0,
    };
    const later_elf = [_]u8{
        0x7f, 'E', 'L', 'F', elfclass64, 1, 1, 0,
        0,    0,   0,   0,   0,          0, 0, 0,
    };
    const chunks = [_][]const u8{
        header[0..3],
        header[3..9],
        header[9..16],
        later_elf[0..],
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try runFromPipeChunks(&chunks, &stdout, &stderr);

    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(not_elf_text, stderr.list.items);
}
