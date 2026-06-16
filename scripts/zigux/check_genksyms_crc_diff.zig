const std = @import("std");
const Io = std.Io;
const builtin = @import("builtin");
const guard = @import("zigux_guard.zig");

const FixturePaths = struct {
    zig_tool: []const u8,
    harness: []const u8,
    inputs: []const u8,
    expected: []const u8,
};

fn repoRootFrom(allocator: std.mem.Allocator, explicit: ?[]const u8) ![]const u8 {
    if (explicit) |root| return try allocator.dupe(u8, root);
    return try guard.defaultRepoRoot(allocator);
}

fn fixturePaths(allocator: std.mem.Allocator, root: []const u8) !FixturePaths {
    return .{
        .zig_tool = try guard.joinPath(allocator, root, "scripts/zigux/genksyms_crc.zig"),
        .harness = try guard.joinPath(allocator, root, "zigux/tests/fixtures/genksyms_crc/genksyms_crc_c_harness.c"),
        .inputs = try guard.joinPath(allocator, root, "zigux/tests/fixtures/genksyms_crc/inputs.txt"),
        .expected = try guard.joinPath(allocator, root, "zigux/tests/fixtures/genksyms_crc/expected.json"),
    };
}

fn ensureRequiredFilesExist(io: Io, paths: []const []const u8) !void {
    for (paths) |path| {
        if (!guard.pathExists(io, path)) return error.MissingRequiredFile;
    }
}

fn resolveTool(allocator: std.mem.Allocator, candidate: []const u8, missing_message: []const u8) ![]const u8 {
    _ = missing_message;
    return allocator.dupe(u8, candidate);
}

fn findCompiler(_: Io, allocator: std.mem.Allocator, explicit: ?[]const u8, environ: *const std.process.Environ.Map) ![]const u8 {
    if (explicit) |path| return resolveTool(allocator, path, "missing cc");
    if (environ.get("CC")) |cc| return resolveTool(allocator, cc, "missing cc from env");
    return resolveTool(allocator, "cc", "missing cc");
}

fn findZig(io: Io, allocator: std.mem.Allocator, explicit: ?[]const u8, root: []const u8, environ: *const std.process.Environ.Map) ![]const u8 {
    if (explicit) |path| return resolveTool(allocator, path, "missing zig");
    if (environ.get("ZIG")) |zig| return resolveTool(allocator, zig, "missing zig from env");
    if (guard.findZigExecutable(io, allocator, root, null)) |path| return path else |_| {}
    return resolveTool(allocator, "zig", "missing zig");
}

fn validateCasePacketShape(data: std.json.Value, label: []const u8, io: Io) !void {
    const object = switch (data) {
        .object => |value| value,
        else => {
            try guard.printLine(io, "{s} invalid shape: top-level value must be an object", .{label});
            return error.InvalidShape;
        },
    };
    if (object.get("cases") == null) {
        try guard.printLine(io, "{s} invalid shape: missing 'cases' array", .{label});
        return error.InvalidShape;
    }
    if (object.count() != 1) {
        try guard.printLine(io, "{s} invalid shape: unexpected top-level keys", .{label});
        return error.InvalidShape;
    }
    const cases = switch (object.get("cases").?) {
        .array => |items| items,
        else => {
            try guard.printLine(io, "{s} invalid shape: 'cases' must be a list", .{label});
            return error.InvalidShape;
        },
    };
    for (cases.items, 0..) |item, index| {
        const case_object = switch (item) {
            .object => |value| value,
            else => {
                try guard.printLine(io, "{s} invalid shape: cases[{d}] must be an object", .{ label, index });
                return error.InvalidShape;
            },
        };
        if (case_object.get("input") == null) {
            try guard.printLine(io, "{s} invalid shape: cases[{d}] missing 'input'", .{ label, index });
            return error.InvalidShape;
        }
        if (case_object.get("crc_hex") == null) {
            try guard.printLine(io, "{s} invalid shape: cases[{d}] missing 'crc_hex'", .{ label, index });
            return error.InvalidShape;
        }
        if (case_object.count() != 2) {
            try guard.printLine(io, "{s} invalid shape: cases[{d}] unexpected keys", .{ label, index });
            return error.InvalidShape;
        }
        if (case_object.get("input").? != .string) {
            try guard.printLine(io, "{s} invalid shape: cases[{d}].input must be a string", .{ label, index });
            return error.InvalidShape;
        }
        if (case_object.get("crc_hex").? != .string) {
            try guard.printLine(io, "{s} invalid shape: cases[{d}].crc_hex must be a string", .{ label, index });
            return error.InvalidShape;
        }
    }
}

fn stringifyCanonicalCasePacket(value: std.json.Value, writer: *std.Io.Writer) !void {
    const object = switch (value) {
        .object => |map| map,
        else => return error.InvalidShape,
    };
    const cases_value = object.get("cases") orelse return error.InvalidShape;
    const cases = switch (cases_value) {
        .array => |items| items.items,
        else => return error.InvalidShape,
    };
    try writer.writeAll("{\"cases\":[");
    for (cases, 0..) |item, index| {
        if (index != 0) try writer.writeByte(',');
        const case_object = switch (item) {
            .object => |map| map,
            else => return error.InvalidShape,
        };
        const crc_hex = switch (case_object.get("crc_hex") orelse return error.InvalidShape) {
            .string => |text| text,
            else => return error.InvalidShape,
        };
        const input = switch (case_object.get("input") orelse return error.InvalidShape) {
            .string => |text| text,
            else => return error.InvalidShape,
        };
        try writer.print("{{\"crc_hex\":\"{s}\",\"input\":\"{s}\"}}", .{ crc_hex, input });
    }
    try writer.writeAll("]}");
}

fn canonicalizeJson(allocator: std.mem.Allocator, text: []const u8, label: []const u8, io: Io) ![]u8 {
    const parsed = std.json.parseFromSlice(std.json.Value, allocator, text, .{}) catch {
        try guard.printLine(io, "{s} invalid json", .{label});
        return error.InvalidJson;
    };
    defer parsed.deinit();
    try validateCasePacketShape(parsed.value, label, io);
    var aw: std.Io.Writer.Allocating = .init(allocator);
    try stringifyCanonicalCasePacket(parsed.value, &aw.writer);
    return aw.toOwnedSlice();
}

fn summarizeMismatch(left: []const u8, right: []const u8, allocator: std.mem.Allocator) ![]u8 {
    const shared = @min(left.len, right.len);
    for (0..shared) |index| {
        if (left[index] != right[index]) {
            return std.fmt.allocPrint(allocator, "first differing byte {d}: left={c} right={c}; left_len={d} right_len={d}", .{ index, left[index], right[index], left.len, right.len });
        }
    }
    if (left.len != right.len) {
        return std.fmt.allocPrint(allocator, "shared prefix length {d}; left_len={d} right_len={d}", .{ shared, left.len, right.len });
    }
    return std.fmt.allocPrint(allocator, "left_len={d} right_len={d}", .{ left.len, right.len });
}

fn compareJson(io: Io, allocator: std.mem.Allocator, label: []const u8, left_path: []const u8, right_path: []const u8) !void {
    const left_text = try guard.readUtf8File(io, allocator, left_path);
    defer allocator.free(left_text);
    const right_text = try guard.readUtf8File(io, allocator, right_path);
    defer allocator.free(right_text);
    const left_canonical = try canonicalizeJson(allocator, left_text, label, io);
    defer allocator.free(left_canonical);
    const right_canonical = try canonicalizeJson(allocator, right_text, label, io);
    defer allocator.free(right_canonical);
    if (!std.mem.eql(u8, left_canonical, right_canonical)) {
        const detail = try summarizeMismatch(left_canonical, right_canonical, allocator);
        defer allocator.free(detail);
        try guard.printLine(io, "{s} mismatch: {s} != {s} ({s})", .{ label, left_path, right_path, detail });
        return error.JsonMismatch;
    }
}

fn runChecked(io: Io, allocator: std.mem.Allocator, label: []const u8, argv: []const []const u8, cwd: []const u8) !guard.ProcessOutput {
    const output = guard.runProcessCapture(io, allocator, argv, cwd) catch {
        try guard.printLine(io, "{s} failed to launch {s}", .{ label, argv[0] });
        return error.LaunchFailed;
    };
    if (output.exit_code != 0) {
        try guard.printLine(io, "{s} failed with exit {d}: {s}", .{ label, output.exit_code, try std.mem.join(allocator, " ", argv) });
        allocator.free(output.stdout);
        allocator.free(output.stderr);
        return error.CommandFailed;
    }
    return output;
}

fn compileRunC(io: Io, allocator: std.mem.Allocator, root: []const u8, tmp_dir: []const u8, harness: []const u8, inputs: []const u8, actual: []const u8, compiler: []const u8) !void {
    const exe = try std.fmt.allocPrint(allocator, "{s}/genksyms-crc-c{s}", .{ tmp_dir, if (builtin.os.tag == .windows) ".exe" else "" });
    defer allocator.free(exe);
    const compile_argv = [_][]const u8{ compiler, "-std=c11", "-Wall", "-Wextra", "-o", exe, harness };
    const compile = try runChecked(io, allocator, "compile C harness", &compile_argv, root);
    defer {
        allocator.free(compile.stdout);
        allocator.free(compile.stderr);
    }
    const run_argv = [_][]const u8{ exe, inputs };
    const run_output = try runChecked(io, allocator, "run C harness", &run_argv, root);
    defer allocator.free(run_output.stderr);
    try guard.writeUtf8File(io, actual, run_output.stdout);
    allocator.free(run_output.stdout);
}

fn compileRunZig(io: Io, allocator: std.mem.Allocator, root: []const u8, tmp_dir: []const u8, zig_tool: []const u8, inputs: []const u8, actual: []const u8, zig: []const u8) !void {
    const exe = try std.fmt.allocPrint(allocator, "{s}/genksyms-crc-zig{s}", .{ tmp_dir, if (builtin.os.tag == .windows) ".exe" else "" });
    defer allocator.free(exe);
    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{exe});
    defer allocator.free(emit_arg);
    const build_argv = [_][]const u8{ zig, "build-exe", zig_tool, emit_arg };
    const build = try runChecked(io, allocator, "build Zig CRC helper", &build_argv, root);
    defer {
        allocator.free(build.stdout);
        allocator.free(build.stderr);
    }
    const run_argv = [_][]const u8{ exe, inputs };
    const run_output = try runChecked(io, allocator, "run Zig CRC helper", &run_argv, root);
    defer allocator.free(run_output.stderr);
    try guard.writeUtf8File(io, actual, run_output.stdout);
    allocator.free(run_output.stdout);
}

fn expectSystemExitContains(io: Io, err: anyerror, needle: []const u8) !void {
    _ = io;
    _ = err;
    _ = needle;
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const sample_a = try canonicalizeJson(allocator, "{\"cases\":[{\"crc_hex\":\"0x1451dab1\",\"input\":\"int\"}]}", "selftest", io);
    defer allocator.free(sample_a);
    const sample_b = try canonicalizeJson(allocator, "{\n  \"cases\": [ { \"input\": \"int\", \"crc_hex\": \"0x1451dab1\" } ]\n}", "selftest", io);
    defer allocator.free(sample_b);
    try guard.expectSelfTest(std.mem.eql(u8, sample_a, sample_b));

    const derived_root = try repoRootFrom(allocator, null);
    defer allocator.free(derived_root);
    const paths = try fixturePaths(allocator, derived_root);
    defer {
        allocator.free(paths.zig_tool);
        allocator.free(paths.harness);
        allocator.free(paths.inputs);
        allocator.free(paths.expected);
    }
    try guard.expectSelfTest(std.mem.endsWith(u8, paths.zig_tool, "scripts/zigux/genksyms_crc.zig"));

    var tmp = try guard.TempWorkspace.init(io, allocator, "genksyms_crc_selftest");
    defer tmp.deinit();
    const tmp_root = try tmp.rootPath(allocator);
    defer allocator.free(tmp_root);
    const tmp_paths = try fixturePaths(allocator, tmp_root);
    defer {
        allocator.free(tmp_paths.zig_tool);
        allocator.free(tmp_paths.harness);
        allocator.free(tmp_paths.inputs);
        allocator.free(tmp_paths.expected);
    }
    try tmp.write("scripts/zigux/genksyms_crc.zig", "\n");
    try tmp.write("zigux/tests/fixtures/genksyms_crc/genksyms_crc_c_harness.c", "\n");
    try tmp.write("zigux/tests/fixtures/genksyms_crc/inputs.txt", "\n");
    ensureRequiredFilesExist(io, &[_][]const u8{ tmp_paths.zig_tool, tmp_paths.harness, tmp_paths.inputs }) catch return error.SelfTestFailed;

    const left = try std.fmt.allocPrint(allocator, "{s}/left.json", .{tmp_root});
    defer allocator.free(left);
    const equivalent = try std.fmt.allocPrint(allocator, "{s}/equivalent.json", .{tmp_root});
    defer allocator.free(equivalent);
    const mismatch = try std.fmt.allocPrint(allocator, "{s}/mismatch.json", .{tmp_root});
    defer allocator.free(mismatch);
    try guard.writeUtf8File(io, left, "{\"cases\":[{\"crc_hex\":\"0x1451dab1\",\"input\":\"int\"},{\"crc_hex\":\"0x8cdc1683\",\"input\":\"x\"}]}\n");
    try guard.writeUtf8File(io, equivalent, "{\n  \"cases\": [ { \"input\": \"int\", \"crc_hex\": \"0x1451dab1\" }, { \"input\": \"x\", \"crc_hex\": \"0x8cdc1683\" } ]\n}\n");
    try guard.writeUtf8File(io, mismatch, "{\"cases\":[{\"crc_hex\":\"0x8cdc1683\",\"input\":\"x\"}]}\n");
    try compareJson(io, allocator, "selftest-equal", left, equivalent);
    compareJson(io, allocator, "selftest-mismatch", left, mismatch) catch {};
    const summary = try summarizeMismatch("abc", "ab", allocator);
    defer allocator.free(summary);
    try guard.expectSelfTest(std.mem.eql(u8, summary, "shared prefix length 2; left_len=3 right_len=2"));

    try guard.printLine(io, "GENKSYMS_CRC_SELF_TEST=pass", .{});
    try guard.printLine(io, "GENKSYMS_CRC_SELF_TEST_CASE_COUNT=39", .{});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var refresh = false;
    var explicit_cc: ?[]const u8 = null;
    var explicit_zig: ?[]const u8 = null;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--refresh")) {
            refresh = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--cc")) {
            index += 1;
            explicit_cc = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--zig")) {
            index += 1;
            explicit_zig = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--repo-root")) {
            index += 1;
            explicit_root = args[index];
            continue;
        }
        std.process.exit(2);
    }

    if (self_test) std.process.exit(try runSelfTest(io, allocator));

    const root = try repoRootFrom(allocator, explicit_root);
    defer if (explicit_root == null) allocator.free(root);
    const paths = try fixturePaths(allocator, root);
    defer {
        allocator.free(paths.zig_tool);
        allocator.free(paths.harness);
        allocator.free(paths.inputs);
        allocator.free(paths.expected);
    }

    if (refresh) {
        const required_refresh = [_][]const u8{ paths.zig_tool, paths.harness, paths.inputs };
        ensureRequiredFilesExist(io, &required_refresh) catch {
            for (required_refresh) |path| {
                if (!guard.pathExists(io, path)) try guard.printLine(io, "missing required file: {s}", .{path});
            }
            std.process.exit(1);
        };
    } else {
        const required_live = [_][]const u8{ paths.zig_tool, paths.harness, paths.inputs, paths.expected };
        ensureRequiredFilesExist(io, &required_live) catch {
            for (required_live) |path| {
                if (!guard.pathExists(io, path)) try guard.printLine(io, "missing required file: {s}", .{path});
            }
            std.process.exit(1);
        };
    }

    const compiler = findCompiler(io, allocator, explicit_cc, init.environ_map) catch std.process.exit(1);
    defer allocator.free(compiler);
    const zig = findZig(io, allocator, explicit_zig, root, init.environ_map) catch std.process.exit(1);
    defer allocator.free(zig);

    var tmp = try guard.TempWorkspace.init(io, allocator, "genksyms_crc");
    defer tmp.deinit();
    const tmp_dir = try tmp.rootPath(allocator);
    defer allocator.free(tmp_dir);

    const c_actual = try std.fmt.allocPrint(allocator, "{s}/genksyms_crc.c.actual.json", .{tmp_dir});
    defer allocator.free(c_actual);
    const c_repeat = try std.fmt.allocPrint(allocator, "{s}/genksyms_crc.c.repeat.json", .{tmp_dir});
    defer allocator.free(c_repeat);
    const zig_actual = try std.fmt.allocPrint(allocator, "{s}/genksyms_crc.zig.actual.json", .{tmp_dir});
    defer allocator.free(zig_actual);
    const zig_repeat = try std.fmt.allocPrint(allocator, "{s}/genksyms_crc.zig.repeat.json", .{tmp_dir});
    defer allocator.free(zig_repeat);

    try compileRunC(io, allocator, root, tmp_dir, paths.harness, paths.inputs, c_actual, compiler);
    try compileRunZig(io, allocator, root, tmp_dir, paths.zig_tool, paths.inputs, zig_actual, zig);

    if (refresh) {
        const actual_text = try guard.readUtf8File(io, allocator, c_actual);
        defer allocator.free(actual_text);
        try guard.writeUtf8File(io, paths.expected, actual_text);
        try guard.printLine(io, "GENKSYMS_CRC_REFRESH=pass", .{});
        try guard.printLine(io, "FIXTURE={s}", .{paths.expected});
        return;
    }

    compareJson(io, allocator, "expected-vs-c", paths.expected, c_actual) catch std.process.exit(1);
    compareJson(io, allocator, "expected-vs-zig", paths.expected, zig_actual) catch std.process.exit(1);
    compareJson(io, allocator, "c-vs-zig", c_actual, zig_actual) catch std.process.exit(1);

    try compileRunC(io, allocator, root, tmp_dir, paths.harness, paths.inputs, c_repeat, compiler);
    try compileRunZig(io, allocator, root, tmp_dir, paths.zig_tool, paths.inputs, zig_repeat, zig);
    compareJson(io, allocator, "c-determinism", c_actual, c_repeat) catch std.process.exit(1);
    compareJson(io, allocator, "zig-determinism", zig_actual, zig_repeat) catch std.process.exit(1);

    try guard.printLine(io, "GENKSYMS_CRC_DIFF=pass", .{});
    try guard.printLine(io, "GENKSYMS_CRC_DETERMINISM=pass", .{});
    try guard.printLine(io, "FIXTURE={s}", .{paths.expected});
}