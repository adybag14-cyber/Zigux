const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elf32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elf64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";
const not_elf_text = "Error: not ELF\n";

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

const RunResult = struct {
    exit_code: u8,
    stdout: []const u8,
    stderr: []const u8,
};

fn run(input: []const u8, stdout: *Capture, stderr: *Capture) !RunResult {
    stdout.list.clearRetainingCapacity();
    stderr.list.clearRetainingCapacity();

    return .{
        .exit_code = try mk_elfconfig.runMkElfconfig(input, stdout, stderr),
        .stdout = stdout.list.items,
        .stderr = stderr.list.items,
    };
}

fn expectRun(
    input: []const u8,
    expected_exit_code: u8,
    expected_stdout: []const u8,
    expected_stderr: []const u8,
    stdout: *Capture,
    stderr: *Capture,
) !void {
    const result = try run(input, stdout, stderr);
    try std.testing.expectEqual(expected_exit_code, result.exit_code);
    try std.testing.expectEqualStrings(expected_stdout, result.stdout);
    try std.testing.expectEqualStrings(expected_stderr, result.stderr);
}

fn ident(class: u8) [16]u8 {
    return .{ 0x7f, 'E', 'L', 'F', class, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
}

test "slice public entry rejects invalid class boundaries silently" {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const invalid_classes = [_]u8{ 0, 3, 255 };
    for (invalid_classes) |class| {
        const header = ident(class);
        try expectRun(&header, 1, "", "", &stdout, &stderr);
    }
}

test "slice invalid class keeps first fixed ident authoritative before valid tails" {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const invalid_zero_then_elf32 = ident(0) ++ ident(1);
    const invalid_high_then_elf64 = ident(255) ++ ident(2);

    try expectRun(&invalid_zero_then_elf32, 1, "", "", &stdout, &stderr);
    try expectRun(&invalid_high_then_elf64, 1, "", "", &stdout, &stderr);
}

test "slice invalid class remains distinct from success and non-ELF output" {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    var not_elf = ident(1);
    not_elf[0] = 0;

    const elf32 = ident(1);
    const elf64 = ident(2);
    const invalid = ident(3);

    try expectRun(&elf32, 0, elf32_define, "", &stdout, &stderr);
    try expectRun(&elf64, 0, elf64_define, "", &stdout, &stderr);
    try expectRun(&not_elf, 1, "", not_elf_text, &stdout, &stderr);
    try expectRun(&invalid, 1, "", "", &stdout, &stderr);
}
