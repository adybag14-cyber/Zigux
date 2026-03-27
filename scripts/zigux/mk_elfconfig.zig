const std = @import("std");
const Io = std.Io;

const ei_nident = 16;
const elf_mag = "\x7fELF";
const ei_class_index = 4;
const elfclass32: u8 = 1;
const elfclass64: u8 = 2;

pub const MkElfconfigError = error{
    InputTruncated,
    NotElf,
    InvalidClass,
};

pub fn runMkElfconfig(reader: *Io.Reader, writer: anytype) !void {
    var ident: [ei_nident]u8 = undefined;
    const amt = try reader.readSliceShort(&ident);
    if (amt != ei_nident) {
        return error.InputTruncated;
    }
    if (!std.mem.eql(u8, ident[0..elf_mag.len], elf_mag)) {
        return error.NotElf;
    }

    switch (ident[ei_class_index]) {
        elfclass32 => try writer.writeAll("#define KERNEL_ELFCLASS ELFCLASS32\n"),
        elfclass64 => try writer.writeAll("#define KERNEL_ELFCLASS ELFCLASS64\n"),
        else => return error.InvalidClass,
    }
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;

    var stdin_buffer: [64]u8 = undefined;
    var stdin_reader = Io.File.stdin().reader(io, &stdin_buffer);
    var stdout_buffer: [128]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    var stderr_buffer: [128]u8 = undefined;
    var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);

    runMkElfconfig(&stdin_reader.interface, &stdout_writer.interface) catch |err| switch (err) {
        error.InputTruncated => {
            try stderr_writer.interface.writeAll("Error: input truncated\n");
            try stderr_writer.interface.flush();
            std.process.exit(1);
        },
        error.NotElf => {
            try stderr_writer.interface.writeAll("Error: not ELF\n");
            try stderr_writer.interface.flush();
            std.process.exit(1);
        },
        error.InvalidClass => std.process.exit(1),
        else => return err,
    };

    try stdout_writer.interface.flush();
}

test "mk_elfconfig emits ELFCLASS32 define" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 32),
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

    var input: [ei_nident]u8 = .{ 0x7f, 'E', 'L', 'F', elfclass32, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    var reader: Io.Reader = .fixed(&input);
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try runMkElfconfig(&reader, &capture);
    try std.testing.expectEqualStrings("#define KERNEL_ELFCLASS ELFCLASS32\n", capture.list.items);
}

test "mk_elfconfig rejects truncated input" {
    var input = [_]u8{ 0x7f, 'E', 'L', 'F' };
    var reader: Io.Reader = .fixed(&input);
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 16),
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

    try std.testing.expectError(error.InputTruncated, runMkElfconfig(&reader, &capture));
}

test "mk_elfconfig rejects non-ELF and invalid class" {
    var not_elf: [ei_nident]u8 = .{ 0, 0, 0, 0, elfclass32, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    var not_elf_reader: Io.Reader = .fixed(&not_elf);
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 16),
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
    try std.testing.expectError(error.NotElf, runMkElfconfig(&not_elf_reader, &capture));

    var invalid: [ei_nident]u8 = .{ 0x7f, 'E', 'L', 'F', 3, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    var invalid_reader: Io.Reader = .fixed(&invalid);
    try std.testing.expectError(error.InvalidClass, runMkElfconfig(&invalid_reader, &capture));
}
