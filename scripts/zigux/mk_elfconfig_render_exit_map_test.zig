const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const stdout_elf32 = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const stdout_elf64 = "#define KERNEL_ELFCLASS ELFCLASS64\n";
const stderr_truncated = "Error: input truncated\n";
const stderr_not_elf = "Error: not ELF\n";

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

const RenderCase = struct {
    name: []const u8,
    outcome: mk_elfconfig.Outcome,
    exit_code: u8,
    stdout: []const u8,
    stderr: []const u8,
};

const render_cases = [_]RenderCase{
    .{
        .name = "ELF32 success writes stdout and exits zero",
        .outcome = .elf32,
        .exit_code = 0,
        .stdout = stdout_elf32,
        .stderr = "",
    },
    .{
        .name = "ELF64 success writes stdout and exits zero",
        .outcome = .elf64,
        .exit_code = 0,
        .stdout = stdout_elf64,
        .stderr = "",
    },
    .{
        .name = "truncated input writes stderr and exits one",
        .outcome = .truncated,
        .exit_code = 1,
        .stdout = "",
        .stderr = stderr_truncated,
    },
    .{
        .name = "non-ELF input writes stderr and exits one",
        .outcome = .not_elf,
        .exit_code = 1,
        .stdout = "",
        .stderr = stderr_not_elf,
    },
    .{
        .name = "invalid class exits one without output",
        .outcome = .invalid_class,
        .exit_code = 1,
        .stdout = "",
        .stderr = "",
    },
};

test "renderOutcome keeps every outcome on its Linux mk_elfconfig channel" {
    for (render_cases) |case| {
        var stdout = try Capture.init(std.testing.allocator);
        defer stdout.deinit();
        var stderr = try Capture.init(std.testing.allocator);
        defer stderr.deinit();

        const exit_code = try mk_elfconfig.renderOutcome(&stdout, &stderr, case.outcome);
        errdefer std.debug.print("case failed: {s}\n", .{case.name});

        try std.testing.expectEqual(case.exit_code, exit_code);
        try std.testing.expectEqualStrings(case.stdout, stdout.list.items);
        try std.testing.expectEqualStrings(case.stderr, stderr.list.items);
    }
}

test "renderOutcome output routing is independent across repeated outcomes" {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    try std.testing.expectEqual(@as(u8, 1), try mk_elfconfig.renderOutcome(&stdout, &stderr, .invalid_class));
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);

    try std.testing.expectEqual(@as(u8, 0), try mk_elfconfig.renderOutcome(&stdout, &stderr, .elf32));
    try std.testing.expectEqualStrings(stdout_elf32, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);

    try std.testing.expectEqual(@as(u8, 1), try mk_elfconfig.renderOutcome(&stdout, &stderr, .not_elf));
    try std.testing.expectEqualStrings(stdout_elf32, stdout.list.items);
    try std.testing.expectEqualStrings(stderr_not_elf, stderr.list.items);
}
