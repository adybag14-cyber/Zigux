const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const RenderCase = struct {
    name: []const u8,
    outcome: mk_elfconfig.Outcome,
    exit_code: u8,
    stdout: []const u8,
    stderr: []const u8,
};

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

fn expectRender(case: RenderCase) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.renderOutcome(&stdout, &stderr, case.outcome);
    try std.testing.expectEqual(case.exit_code, exit_code);
    try std.testing.expectEqualStrings(case.stdout, stdout.list.items);
    try std.testing.expectEqualStrings(case.stderr, stderr.list.items);
}

test "renderOutcome public surface matrix" {
    const cases = [_]RenderCase{
        .{
            .name = "elf32 emits define on stdout only",
            .outcome = .elf32,
            .exit_code = 0,
            .stdout = "#define KERNEL_ELFCLASS ELFCLASS32\n",
            .stderr = "",
        },
        .{
            .name = "elf64 emits define on stdout only",
            .outcome = .elf64,
            .exit_code = 0,
            .stdout = "#define KERNEL_ELFCLASS ELFCLASS64\n",
            .stderr = "",
        },
        .{
            .name = "truncated reports stderr diagnostic",
            .outcome = .truncated,
            .exit_code = 1,
            .stdout = "",
            .stderr = "Error: input truncated\n",
        },
        .{
            .name = "not_elf reports stderr diagnostic",
            .outcome = .not_elf,
            .exit_code = 1,
            .stdout = "",
            .stderr = "Error: not ELF\n",
        },
        .{
            .name = "invalid_class fails silently",
            .outcome = .invalid_class,
            .exit_code = 1,
            .stdout = "",
            .stderr = "",
        },
    };

    for (cases) |case| {
        errdefer std.debug.print("failed render case: {s}\n", .{case.name});
        try expectRender(case);
    }
}

test "renderOutcome appends only to the selected stream" {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    try stdout.writeAll("stdout-prefix:");
    try stderr.writeAll("stderr-prefix:");

    const exit_code = try mk_elfconfig.renderOutcome(&stdout, &stderr, .not_elf);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("stdout-prefix:", stdout.list.items);
    try std.testing.expectEqualStrings("stderr-prefix:Error: not ELF\n", stderr.list.items);
}
