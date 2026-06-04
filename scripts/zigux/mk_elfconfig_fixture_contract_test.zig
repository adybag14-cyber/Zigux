const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const fixture_dir_from_root = "zigux/tests/fixtures/mk_elfconfig";
const fixture_dir_from_scripts = "../../zigux/tests/fixtures/mk_elfconfig";

const ExpectedCase = struct {
    name: []const u8,
    input_file: []const u8,
    expected_file: []const u8,
    stdout: []const u8,
    stderr: []const u8,
    exit_code: u8,
};

const expected_cases = [_]ExpectedCase{
    .{
        .name = "elf32",
        .input_file = "elf32.hex",
        .expected_file = "elf32_expected.json",
        .stdout = "#define KERNEL_ELFCLASS ELFCLASS32\n",
        .stderr = "",
        .exit_code = 0,
    },
    .{
        .name = "elf64",
        .input_file = "elf64.hex",
        .expected_file = "elf64_expected.json",
        .stdout = "#define KERNEL_ELFCLASS ELFCLASS64\n",
        .stderr = "",
        .exit_code = 0,
    },
    .{
        .name = "invalid_class",
        .input_file = "invalid_class.hex",
        .expected_file = "invalid_class_expected.json",
        .stdout = "",
        .stderr = "",
        .exit_code = 1,
    },
    .{
        .name = "not_elf",
        .input_file = "not_elf.hex",
        .expected_file = "not_elf_expected.json",
        .stdout = "",
        .stderr = "Error: not ELF\n",
        .exit_code = 1,
    },
    .{
        .name = "truncated",
        .input_file = "truncated.hex",
        .expected_file = "truncated_expected.json",
        .stdout = "",
        .stderr = "Error: input truncated\n",
        .exit_code = 1,
    },
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

fn fixturePath(buffer: []u8, base: []const u8, name: []const u8) ![]const u8 {
    return std.fmt.bufPrint(buffer, "{s}/{s}", .{ base, name });
}

fn readFixture(allocator: std.mem.Allocator, name: []const u8) ![]u8 {
    var path_buffer: [256]u8 = undefined;
    const root_path = try fixturePath(&path_buffer, fixture_dir_from_root, name);
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, root_path, allocator, .limited(4096)) catch |err| switch (err) {
        error.FileNotFound => {
            const scripts_path = try fixturePath(&path_buffer, fixture_dir_from_scripts, name);
            return std.Io.Dir.cwd().readFileAlloc(std.testing.io, scripts_path, allocator, .limited(4096));
        },
        else => err,
    };
}

fn decodeHexFixture(allocator: std.mem.Allocator, text: []const u8) ![]u8 {
    var decoded = try std.ArrayList(u8).initCapacity(allocator, 16);
    errdefer decoded.deinit(allocator);

    var line_it = std.mem.splitScalar(u8, text, '\n');
    while (line_it.next()) |line| {
        const without_comment = if (std.mem.indexOfScalar(u8, line, '#')) |comment|
            line[0..comment]
        else
            line;
        var token_it = std.mem.tokenizeAny(u8, without_comment, " \t\r");
        while (token_it.next()) |token| {
            try decoded.append(allocator, try std.fmt.parseInt(u8, token, 16));
        }
    }

    return try decoded.toOwnedSlice(allocator);
}

fn expectManifestEntry(manifest: []const u8, case: ExpectedCase, cursor: *usize) !void {
    const name_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "\"name\": \"{s}\"",
        .{case.name},
    );
    defer std.testing.allocator.free(name_marker);

    const input_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "\"input\": \"{s}\"",
        .{case.input_file},
    );
    defer std.testing.allocator.free(input_marker);

    const expected_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "\"expected\": \"{s}\"",
        .{case.expected_file},
    );
    defer std.testing.allocator.free(expected_marker);

    const name_at = std.mem.indexOfPos(u8, manifest, cursor.*, name_marker) orelse return error.MissingCaseName;
    const input_at = std.mem.indexOfPos(u8, manifest, name_at, input_marker) orelse return error.MissingInputFile;
    const expected_at = std.mem.indexOfPos(u8, manifest, input_at, expected_marker) orelse return error.MissingExpectedFile;
    try std.testing.expect(name_at >= cursor.*);
    try std.testing.expect(input_at > name_at);
    try std.testing.expect(expected_at > input_at);
    cursor.* = expected_at + expected_marker.len;
}

test "mk_elfconfig fixture manifest keeps canonical five-case order" {
    const manifest = try readFixture(std.testing.allocator, "cases.json");
    defer std.testing.allocator.free(manifest);

    var cursor: usize = 0;
    for (expected_cases) |case| {
        try expectManifestEntry(manifest, case, &cursor);
    }
}

test "committed mk_elfconfig hex fixtures match public Zig helper outputs" {
    for (expected_cases) |case| {
        const hex_text = try readFixture(std.testing.allocator, case.input_file);
        defer std.testing.allocator.free(hex_text);

        const input = try decodeHexFixture(std.testing.allocator, hex_text);
        defer std.testing.allocator.free(input);

        var stdout = try Capture.init(std.testing.allocator);
        defer stdout.deinit();
        var stderr = try Capture.init(std.testing.allocator);
        defer stderr.deinit();

        const exit_code = try mk_elfconfig.runMkElfconfig(input, &stdout, &stderr);
        try std.testing.expectEqual(case.exit_code, exit_code);
        try std.testing.expectEqualStrings(case.stdout, stdout.list.items);
        try std.testing.expectEqualStrings(case.stderr, stderr.list.items);
    }
}
