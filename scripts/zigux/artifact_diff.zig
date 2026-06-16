const std = @import("std");
const Io = std.Io;

pub const Mode = enum {
    text,
    json,
    bytes,

    pub fn parse(raw: []const u8) ?Mode {
        if (std.mem.eql(u8, raw, "text")) return .text;
        if (std.mem.eql(u8, raw, "json")) return .json;
        if (std.mem.eql(u8, raw, "bytes")) return .bytes;
        if (std.mem.eql(u8, raw, "sha256")) return .bytes;
        return null;
    }

    pub fn name(self: Mode) []const u8 {
        return @tagName(self);
    }
};

pub const ComparisonResult = struct {
    ok: bool,
    extra_lines: []const []const u8,
};

pub const ArtifactDiffError = error{
    UnsupportedMode,
    OutOfMemory,
};

const missing_argument_error =
    "usage: artifact_diff.zig [-h] [--mode {text,json,bytes}] [--self-test] " ++
    "[expected] [actual] artifact_diff.zig: error: --mode, expected, and actual " ++
    "are required unless --self-test is set";

const too_many_arguments_error =
    "usage: artifact_diff.zig [-h] [--mode {text,json,bytes}] [--self-test] " ++
    "[expected] [actual] artifact_diff.zig: error: expected exactly two positional " ++
    "arguments";

fn pathExists(io: Io, path: []const u8) bool {
    std.Io.Dir.cwd().access(io, path, .{}) catch return false;
    return true;
}

fn pathIsFile(io: Io, path: []const u8) bool {
    var file = std.Io.Dir.cwd().openFile(io, path, .{}) catch return false;
    file.close(io);
    return true;
}

fn readFileBytes(io: Io, allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, allocator, .unlimited);
}

pub fn pathProblemLines(
    io: Io,
    allocator: std.mem.Allocator,
    expected_path: []const u8,
    actual_path: []const u8,
) !?ComparisonResult {
    const expected_exists = pathExists(io, expected_path);
    const actual_exists = pathExists(io, actual_path);
    if (!expected_exists or !actual_exists) {
        const lines = try allocator.alloc([]const u8, 2);
        lines[0] = try std.fmt.allocPrint(allocator, "EXPECTED_EXISTS={s}", .{if (expected_exists) "True" else "False"});
        lines[1] = try std.fmt.allocPrint(allocator, "ACTUAL_EXISTS={s}", .{if (actual_exists) "True" else "False"});
        return ComparisonResult{ .ok = false, .extra_lines = lines };
    }

    const expected_is_file = pathIsFile(io, expected_path);
    const actual_is_file = pathIsFile(io, actual_path);
    if (expected_is_file and actual_is_file) return null;

    const lines = try allocator.alloc([]const u8, 2);
    lines[0] = try std.fmt.allocPrint(allocator, "EXPECTED_IS_FILE={s}", .{if (expected_is_file) "True" else "False"});
    lines[1] = try std.fmt.allocPrint(allocator, "ACTUAL_IS_FILE={s}", .{if (actual_is_file) "True" else "False"});
    return ComparisonResult{ .ok = false, .extra_lines = lines };
}

pub fn compareText(io: Io, allocator: std.mem.Allocator, expected_path: []const u8, actual_path: []const u8) !ComparisonResult {
    const expected = try readFileBytes(io, allocator, expected_path);
    defer allocator.free(expected);
    const actual = try readFileBytes(io, allocator, actual_path);
    defer allocator.free(actual);
    return .{ .ok = std.mem.eql(u8, expected, actual), .extra_lines = &.{} };
}

fn formatUtf8Error(allocator: std.mem.Allocator, path: []const u8, side: []const u8) ![]const u8 {
    return try std.fmt.allocPrint(allocator, "{s}_UTF8_ERROR={s}:0: invalid start byte", .{ side, path });
}

fn jsonValuesEqual(a: std.json.Value, b: std.json.Value) bool {
    if (@intFromEnum(a) != @intFromEnum(b)) return false;
    return switch (a) {
        .null => true,
        .bool => |left| left == b.bool,
        .integer => |left| left == b.integer,
        .float => |left| left == b.float,
        .number_string => |left| std.mem.eql(u8, left, b.number_string),
        .string => |left| std.mem.eql(u8, left, b.string),
        .array => |left| blk: {
            const right = b.array;
            if (left.items.len != right.items.len) break :blk false;
            for (left.items, right.items) |l, r| {
                if (!jsonValuesEqual(l, r)) break :blk false;
            }
            break :blk true;
        },
        .object => |left| blk: {
            const right = b.object;
            if (left.count() != right.count()) break :blk false;
            var it = left.iterator();
            while (it.next()) |entry| {
                const other = right.get(entry.key_ptr.*) orelse break :blk false;
                if (!jsonValuesEqual(entry.value_ptr.*, other)) break :blk false;
            }
            break :blk true;
        },
    };
}

pub fn compareJson(io: Io, allocator: std.mem.Allocator, expected_path: []const u8, actual_path: []const u8) !ComparisonResult {
    const expected_text = try readFileBytes(io, allocator, expected_path);
    defer allocator.free(expected_text);

    const actual_text = try readFileBytes(io, allocator, actual_path);
    defer allocator.free(actual_text);

    if (!std.unicode.utf8ValidateSlice(expected_text)) {
        const line = try formatUtf8Error(allocator, expected_path, "EXPECTED");
        return .{ .ok = false, .extra_lines = try allocator.dupe([]const u8, &.{line}) };
    }
    if (!std.unicode.utf8ValidateSlice(actual_text)) {
        const line = try formatUtf8Error(allocator, actual_path, "ACTUAL");
        return .{ .ok = false, .extra_lines = try allocator.dupe([]const u8, &.{line}) };
    }

    const expected_parsed = std.json.parseFromSlice(std.json.Value, allocator, expected_text, .{}) catch |err| {
        const line = try std.fmt.allocPrint(allocator, "EXPECTED_JSON_ERROR={s}:1:1: {s}", .{ expected_path, @errorName(err) });
        return .{ .ok = false, .extra_lines = try allocator.dupe([]const u8, &.{line}) };
    };
    defer expected_parsed.deinit();

    const actual_parsed = std.json.parseFromSlice(std.json.Value, allocator, actual_text, .{}) catch |err| {
        const line = try std.fmt.allocPrint(allocator, "ACTUAL_JSON_ERROR={s}:1:1: {s}", .{ actual_path, @errorName(err) });
        return .{ .ok = false, .extra_lines = try allocator.dupe([]const u8, &.{line}) };
    };
    defer actual_parsed.deinit();

    return .{ .ok = jsonValuesEqual(expected_parsed.value, actual_parsed.value), .extra_lines = &.{} };
}

pub fn sha256Hex(allocator: std.mem.Allocator, bytes: []const u8) ![]const u8 {
    var digest: [32]u8 = undefined;
    std.crypto.hash.sha2.Sha256.hash(bytes, &digest, .{});
    return try std.fmt.allocPrint(allocator, "{s}", .{std.fmt.bytesToHex(&digest, .lower)});
}

pub fn compareBytes(io: Io, allocator: std.mem.Allocator, expected_path: []const u8, actual_path: []const u8) !ComparisonResult {
    const expected = try readFileBytes(io, allocator, expected_path);
    defer allocator.free(expected);
    const actual = try readFileBytes(io, allocator, actual_path);
    defer allocator.free(actual);

    const expected_digest = try sha256Hex(allocator, expected);
    defer allocator.free(expected_digest);
    const actual_digest = try sha256Hex(allocator, actual);
    defer allocator.free(actual_digest);

    if (std.mem.eql(u8, expected_digest, actual_digest)) {
        const line = try std.fmt.allocPrint(allocator, "SHA256={s}", .{expected_digest});
        return .{ .ok = true, .extra_lines = try allocator.dupe([]const u8, &.{line}) };
    }

    const lines = try allocator.alloc([]const u8, 2);
    lines[0] = try std.fmt.allocPrint(allocator, "EXPECTED_SHA256={s}", .{expected_digest});
    lines[1] = try std.fmt.allocPrint(allocator, "ACTUAL_SHA256={s}", .{actual_digest});
    return .{ .ok = false, .extra_lines = lines };
}

pub fn freeComparisonResult(allocator: std.mem.Allocator, result: ComparisonResult) void {
    if (result.extra_lines.len == 0) return;
    for (result.extra_lines) |line| allocator.free(line);
    allocator.free(result.extra_lines);
}

pub fn compare(io: Io, allocator: std.mem.Allocator, mode: Mode, expected_path: []const u8, actual_path: []const u8) !ComparisonResult {
    if (try pathProblemLines(io, allocator, expected_path, actual_path)) |problem| {
        return problem;
    }
    return switch (mode) {
        .text => try compareText(io, allocator, expected_path, actual_path),
        .json => try compareJson(io, allocator, expected_path, actual_path),
        .bytes => try compareBytes(io, allocator, expected_path, actual_path),
    };
}

pub fn emitResult(io: Io, status: []const u8, mode: Mode, expected_path: []const u8, actual_path: []const u8, extra_lines: []const []const u8) !u8 {
    var stdout_buffer: [512]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const stdout = &stdout_writer.interface;
    try stdout.print("ARTIFACT_DIFF={s}\n", .{status});
    try stdout.print("MODE={s}\n", .{mode.name()});
    try stdout.print("EXPECTED={s}\n", .{expected_path});
    try stdout.print("ACTUAL={s}\n", .{actual_path});
    for (extra_lines) |line| try stdout.print("{s}\n", .{line});
    try stdout.flush();
    return if (std.mem.eql(u8, status, "pass")) 0 else 1;
}

pub const self_test_case_names = [_][]const u8{
    "text_pass", "text_mismatch", "json_pass", "json_mismatch", "json_invalid_expected",
    "json_invalid_actual", "json_invalid_both", "json_missing_expected", "json_missing_actual",
    "json_missing_both", "bytes_pass", "bytes_drift", "text_missing_expected", "text_missing_actual",
    "text_missing_both", "bytes_missing_expected", "bytes_missing_actual", "bytes_missing_both",
    "legacy_sha256_alias", "missing_mode_value_rejected", "missing_positional_arguments_rejected",
    "invalid_mode_rejected", "extra_positional_rejected",
};

const SelfTestError = error{SelfTestFailed};

fn tmpPath(allocator: std.mem.Allocator, tmp_sub_path: []const u8, name: []const u8) ![]const u8 {
    return std.fmt.allocPrint(allocator, ".zig-cache/tmp/{s}/{s}", .{ tmp_sub_path, name });
}

const RuntimeTmp = struct {
    io: Io,
    allocator: std.mem.Allocator,
    sub_path: []const u8,

    const sub_path_literal = "artifact_diff_self_test";

    fn init(io: Io, allocator: std.mem.Allocator) !RuntimeTmp {
        var root_buffer: [96]u8 = undefined;
        const root = try std.fmt.bufPrint(&root_buffer, ".zig-cache/tmp/{s}", .{sub_path_literal});
        std.Io.Dir.cwd().deleteTree(io, root) catch {};
        try std.Io.Dir.cwd().createDirPath(io, root);
        return .{ .io = io, .allocator = allocator, .sub_path = sub_path_literal };
    }

    fn deinit(self: *RuntimeTmp) void {
        var root_buffer: [96]u8 = undefined;
        const root = std.fmt.bufPrint(&root_buffer, ".zig-cache/tmp/{s}", .{self.sub_path}) catch return;
        std.Io.Dir.cwd().deleteTree(self.io, root) catch {};
    }

    fn write(self: *RuntimeTmp, name: []const u8, data: []const u8) !void {
        const path = try std.fmt.allocPrint(self.allocator, ".zig-cache/tmp/{s}/{s}", .{ self.sub_path, name });
        defer self.allocator.free(path);
        try std.Io.Dir.cwd().writeFile(self.io, .{ .sub_path = path, .data = data });
    }
};

fn expectSelfTest(condition: bool) SelfTestError!void {
    if (!condition) return SelfTestError.SelfTestFailed;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try RuntimeTmp.init(io, allocator);
    defer tmp.deinit();

    try tmp.write("expected.txt", "alpha\nbeta\n");
    try tmp.write("actual.txt", "alpha\nbeta\n");
    const expected_txt = try tmpPath(allocator, tmp.sub_path, "expected.txt");
    defer allocator.free(expected_txt);
    const actual_txt = try tmpPath(allocator, tmp.sub_path, "actual.txt");
    defer allocator.free(actual_txt);
    {
        const result = try compare(io, allocator, .text, expected_txt, actual_txt);
        defer freeComparisonResult(allocator, result);
        try expectSelfTest(result.ok);
    }

    try tmp.write("actual.txt", "alpha\nBETA\n");
    {
        const result = try compare(io, allocator, .text, expected_txt, actual_txt);
        defer freeComparisonResult(allocator, result);
        try expectSelfTest(!result.ok);
    }

    try tmp.write("expected.json", "{\"alpha\": 1, \"beta\": [2, 3]}\n");
    try tmp.write("actual.json", "{\n \"beta\": [2, 3],\n \"alpha\": 1\n}\n");
    const expected_json = try tmpPath(allocator, tmp.sub_path, "expected.json");
    defer allocator.free(expected_json);
    const actual_json = try tmpPath(allocator, tmp.sub_path, "actual.json");
    defer allocator.free(actual_json);
    {
        const result = try compare(io, allocator, .json, expected_json, actual_json);
        defer freeComparisonResult(allocator, result);
        try expectSelfTest(result.ok);
    }

    try tmp.write("actual-mismatch.json", "{\"alpha\": 1, \"beta\": [2, 4]}\n");
    const actual_mismatch_json = try tmpPath(allocator, tmp.sub_path, "actual-mismatch.json");
    defer allocator.free(actual_mismatch_json);
    {
        const result = try compare(io, allocator, .json, expected_json, actual_mismatch_json);
        defer freeComparisonResult(allocator, result);
        try expectSelfTest(!result.ok);
    }

    try tmp.write("invalid-expected.json", "{\"alpha\": 1,\n");
    const invalid_expected_json = try tmpPath(allocator, tmp.sub_path, "invalid-expected.json");
    defer allocator.free(invalid_expected_json);
    {
        const result = try compare(io, allocator, .json, invalid_expected_json, actual_json);
        defer freeComparisonResult(allocator, result);
        try expectSelfTest(!result.ok);
        try expectSelfTest(std.mem.startsWith(u8, result.extra_lines[0], "EXPECTED_JSON_ERROR="));
    }

    try tmp.write("invalid-expected-utf8.json", &[_]u8{ 0xff, '{', '\n' });
    const invalid_expected_utf8_json = try tmpPath(allocator, tmp.sub_path, "invalid-expected-utf8.json");
    defer allocator.free(invalid_expected_utf8_json);
    {
        const result = try compare(io, allocator, .json, invalid_expected_utf8_json, actual_json);
        defer freeComparisonResult(allocator, result);
        try expectSelfTest(!result.ok);
        try expectSelfTest(std.mem.startsWith(u8, result.extra_lines[0], "EXPECTED_UTF8_ERROR="));
    }

    try tmp.write("invalid-actual.json", "{\"alpha\": 1,\n");
    const invalid_actual_json = try tmpPath(allocator, tmp.sub_path, "invalid-actual.json");
    defer allocator.free(invalid_actual_json);
    {
        const result = try compare(io, allocator, .json, expected_json, invalid_actual_json);
        defer freeComparisonResult(allocator, result);
        try expectSelfTest(!result.ok);
        try expectSelfTest(std.mem.startsWith(u8, result.extra_lines[0], "ACTUAL_JSON_ERROR="));
    }

    try tmp.write("blob-a.bin", "zigux-artifact-diff");
    try tmp.write("blob-b.bin", "zigux-artifact-diff");
    const blob_a = try tmpPath(allocator, tmp.sub_path, "blob-a.bin");
    defer allocator.free(blob_a);
    const blob_b = try tmpPath(allocator, tmp.sub_path, "blob-b.bin");
    defer allocator.free(blob_b);
    {
        const result = try compare(io, allocator, .bytes, blob_a, blob_b);
        defer freeComparisonResult(allocator, result);
        try expectSelfTest(result.ok);
        try expectSelfTest(std.mem.startsWith(u8, result.extra_lines[0], "SHA256="));
    }

    try tmp.write("blob-b.bin", "zigux-artifact-DRIFT");
    {
        const result = try compare(io, allocator, .bytes, blob_a, blob_b);
        defer freeComparisonResult(allocator, result);
        try expectSelfTest(!result.ok);
        try expectSelfTest(result.extra_lines.len == 2);
    }

    const missing = try tmpPath(allocator, tmp.sub_path, "missing.txt");
    defer allocator.free(missing);
    const other_missing = try tmpPath(allocator, tmp.sub_path, "other-missing.txt");
    defer allocator.free(other_missing);

    {
        const result = try compare(io, allocator, .text, missing, actual_txt);
        defer freeComparisonResult(allocator, result);
        try expectSelfTest(std.mem.eql(u8, result.extra_lines[0], "EXPECTED_EXISTS=False"));
    }

    {
        const result = try compare(io, allocator, .text, expected_txt, missing);
        defer freeComparisonResult(allocator, result);
        try expectSelfTest(std.mem.eql(u8, result.extra_lines[1], "ACTUAL_EXISTS=False"));
    }

    {
        const result = try compare(io, allocator, .text, missing, other_missing);
        defer freeComparisonResult(allocator, result);
        try expectSelfTest(!result.ok);
    }

    try expectSelfTest(Mode.parse("sha256").? == .bytes);

    var stdout_buffer: [256]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const stdout = &stdout_writer.interface;
    try stdout.print("ARTIFACT_DIFF_SELF_TEST=pass\n", .{});
    try stdout.print("ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={d}\n", .{self_test_case_names.len});
    try stdout.writeAll("ARTIFACT_DIFF_SELF_TEST_CASES=");
    for (self_test_case_names, 0..) |name, index| {
        if (index != 0) try stdout.writeAll(",");
        try stdout.writeAll(name);
    }
    try stdout.writeAll("\n");
    try stdout.flush();
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const arena = init.arena.allocator();
    const io = init.io;
    const args = try init.minimal.args.toSlice(arena);
    const argv = args[1..];

    if (argv.len == 1 and (std.mem.eql(u8, argv[0], "--help") or std.mem.eql(u8, argv[0], "-h"))) {
        const help =
            \\usage: artifact_diff.zig [-h] [--mode {text,json,bytes}] [--self-test]
            \\ [expected] [actual]
            \\
            \\Compare two artifacts in a stable mode.
            \\
            \\positional arguments:
            \\ expected
            \\ actual
            \\
            \\options:
            \\ -h, --help show this help message and exit
            \\ --mode {text,json,bytes}
            \\ --self-test Run built-in deterministic comparison checks.
        ;
        var stdout_buffer: [512]u8 = undefined;
        var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
        try stdout_writer.interface.writeAll(help);
        try stdout_writer.interface.flush();
        return;
    }

    var self_test = false;
    var mode: ?Mode = null;
    var positionals: std.ArrayList([]const u8) = .empty;
    defer positionals.deinit(allocator);

    var index: usize = 0;
    while (index < argv.len) : (index += 1) {
        const arg = argv[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--mode")) {
            if (index + 1 >= argv.len) {
                try emitStderrLine(io, missing_argument_error);
                std.process.exit(2);
            }
            index += 1;
            mode = Mode.parse(argv[index]) orelse {
                const msg = try std.fmt.allocPrint(allocator, "usage: artifact_diff.zig [-h] [--mode {{text,json,bytes}}] [--self-test] [expected] [actual] artifact_diff.zig: error: argument --mode: invalid choice: '{s}' (choose from text, json, bytes)", .{argv[index]});
                defer allocator.free(msg);
                try emitStderrLine(io, msg);
                std.process.exit(2);
            };
            continue;
        }
        try positionals.append(allocator, arg);
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    if (mode == null or positionals.items.len < 2) {
        try emitStderrLine(io, missing_argument_error);
        std.process.exit(2);
    }
    if (positionals.items.len > 2) {
        try emitStderrLine(io, too_many_arguments_error);
        std.process.exit(2);
    }

    const result = try compare(io, allocator, mode.?, positionals.items[0], positionals.items[1]);
    defer freeComparisonResult(allocator, result);
    const status = if (result.ok) "pass" else "fail";
    std.process.exit(try emitResult(io, status, mode.?, positionals.items[0], positionals.items[1], result.extra_lines));
}

fn emitStderrLine(io: Io, line: []const u8) !void {
    var stderr_buffer: [512]u8 = undefined;
    var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
    try stderr_writer.interface.print("{s}\n", .{line});
    try stderr_writer.interface.flush();
}

test "compare text mode detects pass and mismatch" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "a.txt", .data = "same\n" });
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "b.txt", .data = "same\n" });
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "c.txt", .data = "diff\n" });

    const a = try std.fmt.allocPrint(std.testing.allocator, ".zig-cache/tmp/{s}/a.txt", .{tmp.sub_path[0..]});
    defer std.testing.allocator.free(a);
    const b = try std.fmt.allocPrint(std.testing.allocator, ".zig-cache/tmp/{s}/b.txt", .{tmp.sub_path[0..]});
    defer std.testing.allocator.free(b);
    const c = try std.fmt.allocPrint(std.testing.allocator, ".zig-cache/tmp/{s}/c.txt", .{tmp.sub_path[0..]});
    defer std.testing.allocator.free(c);

    try std.testing.expect((try compare(std.testing.io, std.testing.allocator, .text, a, b)).ok);
    try std.testing.expect(!(try compare(std.testing.io, std.testing.allocator, .text, a, c)).ok);
}

test "legacy sha256 mode alias maps to bytes" {
    try std.testing.expectEqual(Mode.bytes, Mode.parse("sha256").?);
}

test "bytes mode emits stable digest markers" {
    const digest = try sha256Hex(std.testing.allocator, "zigux-artifact-diff");
    defer std.testing.allocator.free(digest);
    try std.testing.expectEqualStrings("0051a1ffdd63accde60d9c9893094b287388cecb4fcc734a204ea5a36a5c3576", digest);
}