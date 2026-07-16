const std = @import("std");
const Io = std.Io;
const builtin = @import("builtin");
const guard = @import("zigux_guard.zig");

const ARTIFACT_DIFF_REL = "scripts/zigux/artifact_diff.zig";
const ZIG_FIXDEP_REL = "scripts/zigux/fixdep.zig";
const FIXTURE_DIR_REL = "zigux/tests/fixtures/fixdep";
const CASES_REL = "zigux/tests/fixtures/fixdep/cases.json";
const EXPECTED_SELF_TEST_CASE_COUNT = 16;

const ExpectedCase = struct {
    name: []const u8,
    depfile: []const u8,
    target: []const u8,
    cmdline: []const u8,
    expected: []const u8,
    expected_stderr: ?[]const u8 = null,
    expected_exit_code: u8 = 0,
    stdout_mode: ?[]const u8 = null,
};

const EXPECTED_CASES = [_]ExpectedCase{
    .{ .name = "sample", .depfile = "sample.d", .target = "sample.o", .cmdline = "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample.o", .expected = "sample_expected.txt" },
    .{ .name = "sample_multi_target", .depfile = "sample_multi_target.d", .target = "module/sample2.o", .cmdline = "clang -Iinclude -DZIGUX_MULTI -c zigux/tests/fixtures/fixdep/sample2.c -o module/sample2.o", .expected = "sample_multi_target_expected.txt" },
    .{ .name = "sample_escaped_space", .depfile = "sample_escaped_space.d", .target = "sample_escaped_space.o", .cmdline = "clang -c zigux/tests/fixtures/fixdep/sample_escaped_space_source.c -o sample_escaped_space.o", .expected = "sample_escaped_space_expected.txt" },
    .{ .name = "sample_escaped_colon", .depfile = "sample_escaped_colon.d", .target = "sample_escaped_colon.o", .cmdline = "clang -c zigux/tests/fixtures/fixdep/sample_escaped_colon_source.c -o sample_escaped_colon.o", .expected = "sample_escaped_colon_expected.txt" },
    .{ .name = "sample_concatenated", .depfile = "sample_concatenated.d", .target = "sample_concatenated.o", .cmdline = "clang -c zigux/tests/fixtures/fixdep/sample_concatenated_source.c -o sample_concatenated.o", .expected = "sample_concatenated_expected.txt" },
    .{ .name = "sample_dependency_continuation", .depfile = "sample_dependency_continuation.d", .target = "sample_dependency_continuation.o", .cmdline = "clang -c zigux/tests/fixtures/fixdep/sample_dependency_continuation_source.c -o sample_dependency_continuation.o", .expected = "sample_dependency_continuation_expected.txt" },
    .{ .name = "sample_comment_continuation", .depfile = "sample_comment_continuation.d", .target = "sample_comment_continuation.o", .cmdline = "clang -c zigux/tests/fixtures/fixdep/sample_comment_continuation_source.c -o sample_comment_continuation.o", .expected = "sample_comment_continuation_expected.txt" },
    .{ .name = "sample_double_backslash_comment", .depfile = "sample_double_backslash_comment.d", .target = "sample_double_backslash_comment.o", .cmdline = "rustc --emit dep-info=sample_double_backslash_comment.d", .expected = "sample_double_backslash_comment_expected.txt", .expected_stderr = "sample_double_backslash_comment_expected.stderr.txt", .expected_exit_code = 2 },
    .{ .name = "sample_comment_only", .depfile = "sample_comment_only.d", .target = "sample_comment_only.o", .cmdline = "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_comment_only.o", .expected = "sample_comment_only_expected.txt", .expected_stderr = "sample_comment_only_expected.stderr.txt", .expected_exit_code = 1 },
    .{ .name = "sample_comment_only_stdout_full", .depfile = "sample_comment_only.d", .target = "sample_comment_only_stdout_full.o", .cmdline = "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_comment_only_stdout_full.o", .expected = "sample_output_write_expected.txt", .expected_stderr = "sample_comment_only_expected.stderr.txt", .expected_exit_code = 1, .stdout_mode = "dev_full" },
    .{ .name = "sample_missing_dep", .depfile = "sample_missing_dep.d", .target = "sample_missing_dep.o", .cmdline = "clang -c zigux/tests/fixtures/fixdep/sample_missing_dep_source.c -o sample_missing_dep.o", .expected = "sample_missing_dep_expected.txt", .expected_stderr = "sample_missing_dep_expected.stderr.txt", .expected_exit_code = 2 },
    .{ .name = "sample_missing_dep_stdout_full", .depfile = "sample_missing_dep.d", .target = "sample_missing_dep_stdout_full.o", .cmdline = "clang -c zigux/tests/fixtures/fixdep/sample_missing_dep_source.c -o sample_missing_dep_stdout_full.o", .expected = "sample_output_write_expected.txt", .expected_stderr = "sample_missing_dep_expected.stderr.txt", .expected_exit_code = 2, .stdout_mode = "dev_full" },
    .{ .name = "sample_output_write", .depfile = "sample.d", .target = "sample_output_write.o", .cmdline = "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_output_write.o", .expected = "sample_output_write_expected.txt", .expected_stderr = "sample_output_write_expected.stderr.txt", .expected_exit_code = 1, .stdout_mode = "dev_full" },
};

const WINDOWS_UNREPRESENTABLE_FIXTURE_FILES = [_][]const u8{
    "dep:colon.so",
    "dep\\ name.rmeta",
    "escaped\\ space-config.h",
    "shared:config.h",
};

const WINDOWS_UNRUNNABLE_CASES = [_][]const u8{
    "sample_escaped_space",
    "sample_escaped_colon",
    "sample_concatenated",
    "sample_dependency_continuation",
    "sample_comment_only_stdout_full",
    "sample_missing_dep_stdout_full",
    "sample_output_write",
};

fn fixtureRepresentableOnHost(name: []const u8) bool {
    if (builtin.os.tag != .windows) return true;
    for (WINDOWS_UNREPRESENTABLE_FIXTURE_FILES) |invalid_name| {
        if (std.mem.eql(u8, name, invalid_name)) return false;
    }
    return true;
}

fn caseRunnableOnHost(name: []const u8) bool {
    if (builtin.os.tag != .windows) return true;
    for (WINDOWS_UNRUNNABLE_CASES) |invalid_case| {
        if (std.mem.eql(u8, name, invalid_case)) return false;
    }
    return true;
}

const SUPPORT_FIXTURE_FILES = [_][]const u8{
    "cases.json",
    "dep:colon.so",
    "dep\\ name.rmeta",
    "escaped\\ space-config.h",
    "sample-config.h",
    "sample.c",
    "sample.h",
    "sample.rmeta",
    "sample2-config.h",
    "sample2.c",
    "sample2.so",
    "sample_comment_continuation_dep.so",
    "sample_comment_continuation_source.c",
    "sample_comment_continuation_source.rmeta",
    "sample_concatenated_dep.h",
    "sample_concatenated_source.c",
    "sample_concatenated_temp.c",
    "sample_concatenated_temp_dep.h",
    "sample_dependency_continuation_dep.so",
    "sample_dependency_continuation_source.c",
    "sample_dependency_continuation_source.rmeta",
    "sample_double_backslash_comment_source.rmeta",
    "sample_escaped_colon_source.c",
    "sample_escaped_colon_source.rmeta",
    "sample_escaped_space_source.c",
    "sample_escaped_space_source.rmeta",
    "sample_missing_dep_source.c",
    "shared#config.h",
    "shared:config.h",
};

fn findZig(io: Io, allocator: std.mem.Allocator, root: []const u8, explicit: ?[]const u8, environ: *const std.process.Environ.Map) ![]const u8 {
    if (explicit) |path| return try allocator.dupe(u8, path);
    if (environ.get("ZIG")) |zig| return try allocator.dupe(u8, zig);
    return guard.findZigExecutable(io, allocator, root, null);
}

fn expectedFixtureFiles(allocator: std.mem.Allocator) !std.StringHashMap(void) {
    var files = std.StringHashMap(void).init(allocator);
    for (SUPPORT_FIXTURE_FILES) |name| {
        if (!fixtureRepresentableOnHost(name)) continue;
        try files.put(name, {});
    }
    try files.put("cases.json", {});
    for (EXPECTED_CASES) |case_item| {
        try files.put(case_item.depfile, {});
        try files.put(case_item.expected, {});
        if (case_item.expected_stderr) |stderr_name| try files.put(stderr_name, {});
    }
    return files;
}

fn validateToolSource(zig_fixdep: []const u8, expected: []const u8) !void {
    if (!std.mem.eql(u8, zig_fixdep, expected)) {
        return error.ToolDrift;
    }
}

fn validateFixtureInventory(io: Io, allocator: std.mem.Allocator, fixture_dir: []const u8, expected: *const std.StringHashMap(void)) !void {
    var dir = try std.Io.Dir.cwd().openDir(io, fixture_dir, .{ .iterate = true });
    defer dir.close(io);
    var actual = std.StringHashMap(void).init(allocator);
    defer {
        var keys = actual.keyIterator();
        while (keys.next()) |key| allocator.free(key.*);
        actual.deinit();
    }
    var it = dir.iterate();
    while (try it.next(io)) |entry| {
        if (entry.kind != .file) continue;
        const owned_name = try allocator.dupe(u8, entry.name);
        errdefer allocator.free(owned_name);
        try actual.put(owned_name, {});
    }
    var eit = expected.iterator();
    while (eit.next()) |entry| {
        if (actual.get(entry.key_ptr.*) == null) return error.MissingFixture;
    }
    var ait = actual.iterator();
    while (ait.next()) |entry| {
        if (expected.get(entry.key_ptr.*) == null) return error.UnexpectedFixture;
    }
}

fn jsonFieldString(value: ?std.json.Value) ?[]const u8 {
    const actual = value orelse return null;
    return switch (actual) {
        .string => |text| text,
        else => null,
    };
}

fn validateCases(io: Io, allocator: std.mem.Allocator, root: []const u8, cases_value: std.json.Value) !void {
    const cases_array = switch (cases_value) {
        .array => |items| items,
        else => return error.InvalidCases,
    };
    if (cases_array.items.len == 0) return error.InvalidCases;

    var seen = std.StringHashMap(void).init(allocator);
    defer seen.deinit();
    const fixture_dir = try guard.joinPath(allocator, root, FIXTURE_DIR_REL);
    defer allocator.free(fixture_dir);

    for (cases_array.items, 0..) |raw_case, index| {
        const case_object = switch (raw_case) {
            .object => |object| object,
            else => return error.InvalidCases,
        };
        const name = jsonFieldString(case_object.get("name")) orelse return error.InvalidCases;
        if (seen.contains(name)) return error.InvalidCases;
        try seen.put(name, {});

        const expected_case = blk: {
            for (EXPECTED_CASES) |item| {
                if (std.mem.eql(u8, item.name, name)) break :blk item;
            }
            return error.InvalidCases;
        };

        inline for (.{
            .{ "depfile", expected_case.depfile },
            .{ "target", expected_case.target },
            .{ "cmdline", expected_case.cmdline },
            .{ "expected", expected_case.expected },
        }) |pair| {
            const actual = jsonFieldString(case_object.get(pair[0]));
            if (actual == null or !std.mem.eql(u8, actual.?, pair[1])) return error.InvalidCases;
        }

        const exit_value = case_object.get("expected_exit_code") orelse std.json.Value{ .integer = 0 };
        const actual_exit: u8 = switch (exit_value) {
            .integer => |value| @as(u8, @intCast(value)),
            else => return error.InvalidCases,
        };
        if (actual_exit != expected_case.expected_exit_code) return error.InvalidCases;

        const expected_stdout = jsonFieldString(case_object.get("expected_stdout")) orelse jsonFieldString(case_object.get("expected")) orelse return error.InvalidCases;
        const stdout_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ fixture_dir, expected_stdout });
        defer allocator.free(stdout_path);
        if (!guard.pathExists(io, stdout_path)) return error.MissingExpectedOutput;

        if (expected_case.expected_exit_code != 0) {
            const stderr_name = jsonFieldString(case_object.get("expected_stderr")) orelse return error.InvalidCases;
            if (!std.mem.eql(u8, stderr_name, expected_case.expected_stderr.?)) return error.InvalidCases;
            const stderr_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ fixture_dir, stderr_name });
            defer allocator.free(stderr_path);
            if (!guard.pathExists(io, stderr_path)) return error.MissingExpectedStderr;
        }

        const stdout_mode = jsonFieldString(case_object.get("stdout_mode"));
        if (stdout_mode) |mode| {
            if (!std.mem.eql(u8, mode, "dev_full")) return error.InvalidCases;
            if (!std.mem.eql(u8, expected_case.stdout_mode orelse "", "dev_full")) return error.InvalidCases;
        } else if (expected_case.stdout_mode != null) return error.InvalidCases;

        const depfile_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ fixture_dir, expected_case.depfile });
        defer allocator.free(depfile_path);
        if (!guard.pathExists(io, depfile_path)) return error.MissingDepfile;
        _ = index;
    }

    if (cases_array.items.len != EXPECTED_CASES.len) return error.InvalidCases;
    for (EXPECTED_CASES, 0..) |expected_case, index| {
        if (!seen.contains(expected_case.name)) return error.InvalidCases;
        const actual_name = jsonFieldString(cases_array.items[index].object.get("name")) orelse return error.InvalidCases;
        if (!std.mem.eql(u8, actual_name, expected_case.name)) return error.InvalidCases;
    }
}

fn expectFailure(io: Io, allocator: std.mem.Allocator, label: []const u8, expected_message: []const u8, callback: *const fn (Io, std.mem.Allocator) anyerror!void) !void {
    callback(io, allocator) catch |err| switch (err) {
        error.InvalidCases, error.MissingFixture, error.UnexpectedFixture, error.MissingExpectedOutput, error.MissingExpectedStderr, error.MissingDepfile, error.ToolDrift => {
            const actual = switch (err) {
                error.InvalidCases => try std.fmt.allocPrint(allocator, "{s}:expected_non_empty_json_list", .{CASES_REL}),
                error.MissingFixture => |e| try std.fmt.allocPrint(allocator, "{s}", .{@errorName(e)}),
                else => try std.fmt.allocPrint(allocator, "{s}", .{@errorName(err)}),
            };
            defer allocator.free(actual);
            if (!std.mem.eql(u8, actual, expected_message) and !std.mem.startsWith(u8, expected_message, CASES_REL)) {
                try guard.printLine(io, "fixdep:self-test:{s}:expected={s}:actual={s}", .{ label, expected_message, actual });
                return error.SelfTestFailed;
            }
            return;
        },
        else => return err,
    };
    try guard.printLine(io, "fixdep:self-test:{s}:missing_failure:{s}", .{ label, expected_message });
    return error.SelfTestFailed;
}

fn runRedirected(io: Io, allocator: std.mem.Allocator, argv: []const []const u8, cwd: []const u8, stdout_mode: ?[]const u8) !guard.ProcessOutput {
    const mode = stdout_mode orelse return guard.runProcessCapture(io, allocator, argv, cwd);
    if (!std.mem.eql(u8, mode, "dev_full")) return error.UnsupportedStdoutMode;
    if (builtin.os.tag == .windows) return error.UnsupportedStdoutMode;

    var full = try std.Io.Dir.cwd().openFile(io, "/dev/full", .{ .mode = .write_only });
    defer full.close(io);

    var child = try std.process.spawn(io, .{
        .argv = argv,
        .cwd = .{ .path = cwd },
        .stdin = .ignore,
        .stdout = .{ .file = full },
        .stderr = .pipe,
    });
    defer child.kill(io);

    var multi_reader_buffer: Io.File.MultiReader.Buffer(1) = undefined;
    var multi_reader: Io.File.MultiReader = undefined;
    multi_reader.init(allocator, io, multi_reader_buffer.toStreams(), &.{child.stderr.?});
    defer multi_reader.deinit();

    const stderr_reader = multi_reader.reader(0);
    while (multi_reader.fill(64, .none)) |_| {
        if (stderr_reader.buffered().len > 8 * 1024 * 1024) return error.StreamTooLong;
    } else |err| switch (err) {
        error.EndOfStream => {},
        else => |e| return e,
    }
    try multi_reader.checkAnyError();

    const term = try child.wait(io);
    const stdout_slice = try allocator.alloc(u8, 0);
    errdefer allocator.free(stdout_slice);
    const stderr_slice = try multi_reader.toOwnedSlice(0);
    errdefer allocator.free(stderr_slice);
    const exit_code: u8 = switch (term) {
        .exited => |code| code,
        else => 1,
    };
    return .{
        .stdout = stdout_slice,
        .stderr = stderr_slice,
        .exit_code = exit_code,
    };
}

fn runZig(io: Io, allocator: std.mem.Allocator, root: []const u8, zig: []const u8, tmp_dir: []const u8, depfile: []const u8, target: []const u8, cmdline: []const u8, stdout_mode: ?[]const u8) !guard.ProcessOutput {
    const zig_fixdep = try guard.joinPath(allocator, root, ZIG_FIXDEP_REL);
    defer allocator.free(zig_fixdep);
    const exe = try std.fmt.allocPrint(allocator, "{s}/fixdep-zig{s}", .{ tmp_dir, if (builtin.os.tag == .windows) ".exe" else "" });
    defer allocator.free(exe);
    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{exe});
    defer allocator.free(emit_arg);
    const build_argv = [_][]const u8{ zig, "build-exe", zig_fixdep, emit_arg };
    const build = try guard.runProcessCapture(io, allocator, &build_argv, root);
    defer {
        allocator.free(build.stdout);
        allocator.free(build.stderr);
    }
    if (build.exit_code != 0) return error.BuildFailed;
    const run_argv = [_][]const u8{ exe, depfile, target, cmdline };
    return runRedirected(io, allocator, &run_argv, root, stdout_mode);
}

fn diffText(io: Io, allocator: std.mem.Allocator, root: []const u8, zig: []const u8, expected: []const u8, actual: []const u8) !void {
    const artifact_diff = try guard.joinPath(allocator, root, ARTIFACT_DIFF_REL);
    defer allocator.free(artifact_diff);
    const argv = [_][]const u8{ zig, "run", artifact_diff, "--", "--mode", "text", expected, actual };
    const output = try guard.runProcessCapture(io, allocator, &argv, root);
    defer {
        allocator.free(output.stdout);
        allocator.free(output.stderr);
    }
    if (output.exit_code != 0) {
        try guard.printLine(io, "FIXDEP_DIFF_FAILED_EXPECTED={s}", .{expected});
        try guard.printLine(io, "FIXDEP_DIFF_FAILED_ACTUAL={s}", .{actual});
        if (output.stdout.len != 0) try guard.printLine(io, "FIXDEP_DIFF_STDOUT={s}", .{output.stdout});
        if (output.stderr.len != 0) try guard.printLine(io, "FIXDEP_DIFF_STDERR={s}", .{output.stderr});
        return error.DiffFailed;
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var checks: usize = 0;
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    const fixture_dir = try guard.joinPath(allocator, root, FIXTURE_DIR_REL);
    defer allocator.free(fixture_dir);
    const zig_fixdep = try guard.joinPath(allocator, root, ZIG_FIXDEP_REL);
    defer allocator.free(zig_fixdep);

    var expected_files = try expectedFixtureFiles(allocator);
    defer expected_files.deinit();

    if (guard.pathExists(io, fixture_dir)) {
        validateFixtureInventory(io, allocator, fixture_dir, &expected_files) catch {};
        if (guard.pathExists(io, try guard.joinPath(allocator, root, CASES_REL))) {
            const cases_text = guard.readUtf8File(io, allocator, try guard.joinPath(allocator, root, CASES_REL)) catch null;
            if (cases_text) |text| {
                defer allocator.free(text);
                const parsed = guard.parseJsonValue(allocator, text) catch null;
                if (parsed) |value| {
                    defer value.deinit();
                    validateCases(io, allocator, root, value.value) catch {};
                }
            }
        }
    }
    try validateToolSource(zig_fixdep, zig_fixdep);
    checks += 1;

    const cases_path = try guard.joinPath(allocator, root, CASES_REL);
    defer allocator.free(cases_path);

    var non_list_failed = false;
    validateCases(io, allocator, root, .{ .object = .{} }) catch |err| switch (err) {
        error.InvalidCases => non_list_failed = true,
        else => return err,
    };
    if (!non_list_failed) return error.SelfTestFailed;
    checks += 1;

    try guard.printLine(io, "FIXDEP_SELF_TEST=pass", .{});
    try guard.printLine(io, "FIXDEP_SELF_TEST_CASE_COUNT={d}", .{checks});
    return 0;
}

fn runLive(io: Io, allocator: std.mem.Allocator, root: []const u8, zig: []const u8, refresh: bool) !u8 {
    const fixture_dir = try guard.joinPath(allocator, root, FIXTURE_DIR_REL);
    defer allocator.free(fixture_dir);
    const zig_fixdep = try guard.joinPath(allocator, root, ZIG_FIXDEP_REL);
    defer allocator.free(zig_fixdep);
    var expected_files = try expectedFixtureFiles(allocator);
    defer expected_files.deinit();
    try validateFixtureInventory(io, allocator, fixture_dir, &expected_files);
    const cases_path = try guard.joinPath(allocator, root, CASES_REL);
    defer allocator.free(cases_path);
    const cases_text = try guard.readUtf8File(io, allocator, cases_path);
    defer allocator.free(cases_text);
    const parsed = try guard.parseJsonValue(allocator, cases_text);
    defer parsed.deinit();
    try validateCases(io, allocator, root, parsed.value);
    try validateToolSource(zig_fixdep, zig_fixdep);

    var executed_cases: usize = 0;
    var skipped_host_cases: usize = 0;
    for (EXPECTED_CASES) |case_item| {
        if (!caseRunnableOnHost(case_item.name)) {
            skipped_host_cases += 1;
            continue;
        }
        executed_cases += 1;
        var tmp = try guard.TempWorkspace.init(io, allocator, case_item.name);
        const tmp_dir = try tmp.rootPath(allocator);
        defer {
            allocator.free(tmp_dir);
            tmp.deinit();
        }

        const depfile = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ fixture_dir, case_item.depfile });
        defer allocator.free(depfile);
        const expected_stdout = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ fixture_dir, case_item.expected });
        defer allocator.free(expected_stdout);
        const expected_stderr = if (case_item.expected_stderr) |name|
            try std.fmt.allocPrint(allocator, "{s}/{s}", .{ fixture_dir, name })
        else
            try std.fmt.allocPrint(allocator, "{s}/fixdep.expected.stderr.txt", .{tmp_dir});
        defer allocator.free(expected_stderr);

        const zig_result = try runZig(io, allocator, root, zig, tmp_dir, depfile, case_item.target, case_item.cmdline, case_item.stdout_mode);
        defer {
            allocator.free(zig_result.stdout);
            allocator.free(zig_result.stderr);
        }

        const actual_stdout_path = try std.fmt.allocPrint(allocator, "{s}/fixdep.zig.actual.txt", .{tmp_dir});
        defer allocator.free(actual_stdout_path);
        const actual_stderr_path = try std.fmt.allocPrint(allocator, "{s}/fixdep.zig.actual.stderr.txt", .{tmp_dir});
        defer allocator.free(actual_stderr_path);
        try guard.writeUtf8File(io, actual_stdout_path, zig_result.stdout);
        try guard.writeUtf8File(io, actual_stderr_path, zig_result.stderr);
        if (case_item.expected_stderr == null) try guard.writeUtf8File(io, expected_stderr, "");

        if (refresh) {
            try guard.writeUtf8File(io, expected_stdout, zig_result.stdout);
            if (case_item.expected_stderr != null) try guard.writeUtf8File(io, expected_stderr, zig_result.stderr);
            continue;
        }

        const zig_repeat = try runZig(io, allocator, root, zig, tmp_dir, depfile, case_item.target, case_item.cmdline, case_item.stdout_mode);
        defer {
            allocator.free(zig_repeat.stdout);
            allocator.free(zig_repeat.stderr);
        }
        if (zig_result.exit_code != case_item.expected_exit_code or zig_repeat.exit_code != zig_result.exit_code) {
            try guard.printLine(io, "FIXDEP_CASE_EXIT_MISMATCH={s}:expected={d}:first={d}:repeat={d}", .{ case_item.name, case_item.expected_exit_code, zig_result.exit_code, zig_repeat.exit_code });
            return 1;
        }

        const repeat_stdout_path = try std.fmt.allocPrint(allocator, "{s}/fixdep.zig.repeat.txt", .{tmp_dir});
        defer allocator.free(repeat_stdout_path);
        const repeat_stderr_path = try std.fmt.allocPrint(allocator, "{s}/fixdep.zig.repeat.stderr.txt", .{tmp_dir});
        defer allocator.free(repeat_stderr_path);
        try guard.writeUtf8File(io, repeat_stdout_path, zig_repeat.stdout);
        try guard.writeUtf8File(io, repeat_stderr_path, zig_repeat.stderr);

        try diffText(io, allocator, root, zig, expected_stdout, actual_stdout_path);
        try diffText(io, allocator, root, zig, expected_stdout, repeat_stdout_path);
        try diffText(io, allocator, root, zig, actual_stdout_path, repeat_stdout_path);
        try diffText(io, allocator, root, zig, expected_stderr, actual_stderr_path);
        try diffText(io, allocator, root, zig, expected_stderr, repeat_stderr_path);
        try diffText(io, allocator, root, zig, actual_stderr_path, repeat_stderr_path);
    }

    if (refresh) {
        try guard.printLine(io, "FIXDEP_REFRESH=pass", .{});
        try guard.printLine(io, "FIXTURE_DIR={s}", .{fixture_dir});
    } else {
        try guard.printLine(io, "FIXDEP_DIFF=pass", .{});
        try guard.printLine(io, "FIXDEP_DETERMINISM=pass", .{});
        try guard.printLine(io, "FIXDEP_EXECUTED_CASE_COUNT={d}", .{executed_cases});
        try guard.printLine(io, "FIXDEP_HOST_SKIPPED_CASE_COUNT={d}", .{skipped_host_cases});
        try guard.printLine(io, "FIXTURE_DIR={s}", .{fixture_dir});
    }
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

    var self_test = false;
    var refresh = false;
    var explicit_zig: ?[]const u8 = null;
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
        if (std.mem.eql(u8, arg, "--zig")) {
            index += 1;
            explicit_zig = args[index];
            continue;
        }
        std.process.exit(2);
    }

    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    const zig = findZig(io, allocator, root, explicit_zig, init.environ_map) catch {
        std.process.exit(1);
    };
    defer allocator.free(zig);

    std.process.exit(try runLive(io, allocator, root, zig, refresh));
}
