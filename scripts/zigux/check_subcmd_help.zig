const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");
const resolver = @import("toolchain_resolver.zig");

const help_rel = "tools/lib/subcmd/help.zig";
const fixture_dir_rel = "zigux/tests/fixtures/subcmd_help";
const cases_fixture_rel = "zigux/tests/fixtures/subcmd_help/cases.json";
const wrapper_rel = ".subcmd_help_fixture_runner.zig";

const REQUIRED_HELPER_ANCHORS = [_][]const u8{
    "buildOtherCommandSearchPlan keeps PATH ordering while marking empty and exec-path entries",
    "buildOtherCommandSearchPlan preserves duplicate and relative scan targets when they are not the exec path",
    "renderCommandSections keeps stable headers for main and fallback command groups",
    "renderCommandSections emits the fallback-only packet without a blank main header",
    "renderCommandSections keeps an empty exec path unquoted while sharing longest width with fallback commands",
};

const wrapper_source =
    \\const std = @import("std");
    \\const Io = std.Io;
    \\const help = @import("tools/lib/subcmd/help.zig");
    \\
    \\const SearchPlanPacket = struct {
    \\    entries: []SearchPlanEntryPacket,
    \\    scannable_count: usize,
    \\};
    \\
    \\const SearchPlanEntryPacket = struct {
    \\    path: []const u8,
    \\    disposition: []const u8,
    \\};
    \\
    \\fn dispositionName(value: help.SearchPathEntryDisposition) []const u8 {
    \\    return switch (value) {
    \\        .scan => "scan",
    \\        .skip_exec_path => "skip_exec_path",
    \\        .skip_empty => "skip_empty",
    \\    };
    \\}
    \\
    \\fn emitSearchPlan(io: Io) !void {
    \\    const allocator = std.heap.page_allocator;
    \\    const plan = try help.buildOtherCommandSearchPlan(
    \\        allocator,
    \\        ":/usr/libexec/perf-core:/bin::/usr/bin:",
    \\        "/usr/libexec/perf-core",
    \\    );
    \\    defer help.freeOtherCommandSearchPlan(allocator, plan);
    \\
    \\    var entries = try allocator.alloc(SearchPlanEntryPacket, plan.len);
    \\    defer allocator.free(entries);
    \\
    \\    for (plan, 0..) |entry, index| {
    \\        entries[index] = .{
    \\            .path = entry.path,
    \\            .disposition = dispositionName(entry.disposition),
    \\        };
    \\    }
    \\
    \\    const packet = SearchPlanPacket{
    \\        .entries = entries,
    \\        .scannable_count = help.countScannableSearchPathEntries(plan),
    \\    };
    \\
    \\    var stdout_buffer: [1024]u8 = undefined;
    \\    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    \\    const stdout = &stdout_writer.interface;
    \\    try std.json.Stringify.value(packet, .{ .whitespace = .indent_2 }, stdout);
    \\    try stdout.writeByte('\n');
    \\    try stdout.flush();
    \\}
    \\
    \\fn emitMainAndOtherSections(io: Io) !void {
    \\    const allocator = std.heap.page_allocator;
    \\
    \\    var main_cmds = help.CommandNames.init(allocator);
    \\    defer main_cmds.deinit();
    \\    try main_cmds.add("annotate");
    \\    try main_cmds.add("bench");
    \\
    \\    var other_cmds = help.CommandNames.init(allocator);
    \\    defer other_cmds.deinit();
    \\    try other_cmds.add("report");
    \\
    \\    const rendered = try help.renderCommandSections(
    \\        allocator,
    \\        "subcommands",
    \\        "/usr/libexec/perf-core",
    \\        &main_cmds,
    \\        &other_cmds,
    \\        80,
    \\    );
    \\    defer allocator.free(rendered);
    \\
    \\    var stdout_buffer: [1024]u8 = undefined;
    \\    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    \\    const stdout = &stdout_writer.interface;
    \\    try stdout.writeAll(rendered);
    \\    try stdout.flush();
    \\}
    \\
    \\fn emitFallbackOnlySections(io: Io) !void {
    \\    const allocator = std.heap.page_allocator;
    \\
    \\    var main_cmds = help.CommandNames.init(allocator);
    \\    defer main_cmds.deinit();
    \\
    \\    var other_cmds = help.CommandNames.init(allocator);
    \\    defer other_cmds.deinit();
    \\    try other_cmds.add("report");
    \\    try other_cmds.add("script");
    \\
    \\    const rendered = try help.renderCommandSections(
    \\        allocator,
    \\        "subcommands",
    \\        "/usr/libexec/perf-core",
    \\        &main_cmds,
    \\        &other_cmds,
    \\        80,
    \\    );
    \\    defer allocator.free(rendered);
    \\
    \\    var stdout_buffer: [1024]u8 = undefined;
    \\    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    \\    const stdout = &stdout_writer.interface;
    \\    try stdout.writeAll(rendered);
    \\    try stdout.flush();
    \\}
    \\
    \\pub fn main(init: std.process.Init) !void {
    \\    const io = init.io;
    \\    const args = try init.minimal.args.toSlice(init.arena.allocator());
    \\    const case_name = if (args.len >= 2) args[1] else return error.MissingCaseName;
    \\    if (args.len != 2) return error.UnexpectedArguments;
    \\
    \\    if (std.mem.eql(u8, case_name, "search_plan")) {
    \\        try emitSearchPlan(io);
    \\        return;
    \\    }
    \\    if (std.mem.eql(u8, case_name, "main_and_other_sections")) {
    \\        try emitMainAndOtherSections(io);
    \\        return;
    \\    }
    \\    if (std.mem.eql(u8, case_name, "fallback_only_sections")) {
    \\        try emitFallbackOnlySections(io);
    \\        return;
    \\    }
    \\
    \\    return error.UnknownCaseName;
    \\}
    \\
;

const FixtureCase = struct {
    name: []const u8,
    expected_file: []const u8,
    output_kind: []const u8,
};

fn fail(io: Io, message: []const u8) noreturn {
    var buffer: [1024]u8 = undefined;
    var writer = Io.File.stderr().writer(io, &buffer);
    writer.interface.writeAll(message) catch {};
    writer.interface.writeAll("\n") catch {};
    writer.interface.flush() catch {};
    std.process.exit(1);
}

fn findLocalToolchainZig(io: Io, allocator: std.mem.Allocator, root: []const u8) !?[]const u8 {
    const toolchain_root = try guard.joinPath(allocator, root, ".zig-toolchain");
    defer allocator.free(toolchain_root);
    if (!guard.pathExists(io, toolchain_root)) return null;

    var dir = try std.Io.Dir.cwd().openDir(io, toolchain_root, .{ .iterate = true });
    defer dir.close(io);

    var iter = dir.iterate();
    while (try iter.next(io)) |entry| {
        if (entry.kind != .directory) continue;
        for (&[_][]const u8{ "zig.exe", "zig", "bin/zig.exe", "bin/zig" }) |leaf| {
            const candidate = try std.fmt.allocPrint(allocator, "{s}/{s}/{s}", .{ toolchain_root, entry.name, leaf });
            defer allocator.free(candidate);
            if (guard.pathExists(io, candidate)) return try allocator.dupe(u8, candidate);
        }
    }
    return null;
}

fn findZig(io: Io, allocator: std.mem.Allocator, root: []const u8, explicit: ?[]const u8) ![]const u8 {
    if (explicit) |zig| {
        const resolved = try resolver.resolveZigExecutable(io, allocator, root, zig, null);
        if (resolved) |path| return path;
        fail(io, "zig executable not found at --zig path");
    }

    if (try findLocalToolchainZig(io, allocator, root)) |local_zig| return local_zig;

    const resolved = try resolver.resolveZigExecutable(io, allocator, root, null, null);
    if (resolved) |zig| return zig;
    fail(io, "zig not found; pass --zig, install the repo-local .zig-toolchain, or add zig to PATH");
}

const AnchorError = error{ MissingAnchors, OutOfMemory };

fn orderedTestAnchors(allocator: std.mem.Allocator, text: []const u8) AnchorError![]const []const u8 {
    var anchors: std.ArrayList([]const u8) = .empty;
    defer anchors.deinit(allocator);

    var iter = std.mem.splitScalar(u8, text, '\n');
    while (iter.next()) |line| {
        const trimmed = std.mem.trim(u8, line, " \t\r");
        if (!std.mem.startsWith(u8, trimmed, "test \"")) continue;
        if (!std.mem.endsWith(u8, trimmed, "\" {")) continue;
        const anchor = try allocator.dupe(u8, trimmed["test \"".len .. trimmed.len - "\" {".len]);
        try anchors.append(allocator, anchor);
    }

    if (anchors.items.len == 0) return error.MissingAnchors;
    return try anchors.toOwnedSlice(allocator);
}

fn readCases(io: Io, allocator: std.mem.Allocator, root: []const u8) ![]FixtureCase {
    const cases_path = try guard.joinPath(allocator, root, cases_fixture_rel);
    defer allocator.free(cases_path);
    const text = try guard.readUtf8File(io, allocator, cases_path);
    defer allocator.free(text);

    const parsed = try std.json.parseFromSlice(std.json.Value, allocator, text, .{});
    defer parsed.deinit();

    const payload = parsed.value;
    if (payload != .array) fail(io, "subcmd help fixture cases must be a JSON list");

    var cases: std.ArrayList(FixtureCase) = .empty;
    errdefer {
        for (cases.items) |item| {
            allocator.free(item.name);
            allocator.free(item.expected_file);
            allocator.free(item.output_kind);
        }
        cases.deinit(allocator);
    }

    for (payload.array.items) |item| {
        if (item != .object) fail(io, "each subcmd help fixture case must be an object");
        const name_value = item.object.get("name") orelse fail(io, "subcmd help fixture case fields must be strings");
        const expected_value = item.object.get("expected_file") orelse fail(io, "subcmd help fixture case fields must be strings");
        const kind_value = item.object.get("output_kind") orelse fail(io, "subcmd help fixture case fields must be strings");
        if (name_value != .string or expected_value != .string or kind_value != .string) {
            fail(io, "subcmd help fixture case fields must be strings");
        }
        try cases.append(allocator, .{
            .name = try allocator.dupe(u8, name_value.string),
            .expected_file = try allocator.dupe(u8, expected_value.string),
            .output_kind = try allocator.dupe(u8, kind_value.string),
        });
    }

    return try cases.toOwnedSlice(allocator);
}

fn normalizeExpected(allocator: std.mem.Allocator, kind: []const u8, text: []const u8) !struct { value: std.json.Value, parsed: ?std.json.Parsed(std.json.Value) } {
    if (std.mem.eql(u8, kind, "json")) {
        const parsed = try std.json.parseFromSlice(std.json.Value, allocator, text, .{});
        return .{ .value = parsed.value, .parsed = parsed };
    }
    if (std.mem.eql(u8, kind, "text")) {
        return .{ .value = .{ .string = try allocator.dupe(u8, text) }, .parsed = null };
    }
    return error.UnsupportedOutputKind;
}

fn jsonValuesEqual(a: std.json.Value, b: std.json.Value) bool {
    return guard.jsonValuesEqual(a, b);
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

    var zig_arg: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        if (std.mem.eql(u8, args[index], "--zig")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            zig_arg = args[index];
        }
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);

    const help_path = try guard.joinPath(allocator, root, help_rel);
    defer allocator.free(help_path);
    const fixture_dir = try guard.joinPath(allocator, root, fixture_dir_rel);
    defer allocator.free(fixture_dir);
    const cases_path = try guard.joinPath(allocator, root, cases_fixture_rel);
    defer allocator.free(cases_path);

    if (!guard.pathExists(io, help_path) or !guard.pathExists(io, cases_path)) {
        fail(io, "missing required files: tools/lib/subcmd/help.zig and/or zigux/tests/fixtures/subcmd_help/cases.json");
    }

    const help_text = try guard.readUtf8File(io, allocator, help_path);
    defer allocator.free(help_text);

    const anchors = orderedTestAnchors(allocator, help_text) catch |err| switch (err) {
        error.MissingAnchors => fail(io, "no Zig test anchors found in tools/lib/subcmd/help.zig"),
        else => |e| return e,
    };
    defer {
        for (anchors) |anchor| allocator.free(anchor);
        allocator.free(anchors);
    }

    for (REQUIRED_HELPER_ANCHORS) |required| {
        var found = false;
        for (anchors) |anchor| {
            if (std.mem.eql(u8, anchor, required)) found = true;
        }
        if (!found) fail(io, "missing required help.zig test anchors");
    }

    const zig = try findZig(io, allocator, root, zig_arg);
    defer allocator.free(zig);

    const test_output = try guard.runProcessCapture(io, allocator, &.{ zig, "test", help_path }, root);
    defer allocator.free(test_output.stdout);
    defer allocator.free(test_output.stderr);
    if (test_output.exit_code != 0) {
        fail(io, test_output.stderr);
    }

    const cases = try readCases(io, allocator, root);
    defer {
        for (cases) |item| {
            allocator.free(item.name);
            allocator.free(item.expected_file);
            allocator.free(item.output_kind);
        }
        allocator.free(cases);
    }

    const wrapper_path = try guard.joinPath(allocator, root, wrapper_rel);
    defer allocator.free(wrapper_path);
    try guard.writeUtf8File(io, wrapper_path, wrapper_source);
    defer guard.deleteFile(io, wrapper_path) catch {};

    var case_names: std.ArrayList([]const u8) = .empty;
    defer case_names.deinit(allocator);

    for (cases) |case_item| {
        const expected_path = try guard.joinPath(allocator, fixture_dir, case_item.expected_file);
        defer allocator.free(expected_path);
        if (!guard.pathExists(io, expected_path)) fail(io, "missing expected fixture");

        const expected_text = try guard.readUtf8File(io, allocator, expected_path);
        defer allocator.free(expected_text);

        const expected = try normalizeExpected(allocator, case_item.output_kind, expected_text);
        defer {
            if (expected.parsed) |*parsed| parsed.deinit();
            if (expected.value == .string) allocator.free(expected.value.string);
        }

        const run_output = try guard.runProcessCapture(io, allocator, &.{ zig, "run", wrapper_path, "--", case_item.name }, root);
        defer allocator.free(run_output.stdout);
        defer allocator.free(run_output.stderr);
        if (run_output.exit_code != 0) {
            fail(io, if (run_output.stderr.len != 0) run_output.stderr else "fixture runner failed");
        }

        if (std.mem.eql(u8, case_item.output_kind, "json")) {
            const actual_parsed = try std.json.parseFromSlice(std.json.Value, allocator, run_output.stdout, .{});
            defer actual_parsed.deinit();
            if (!jsonValuesEqual(expected.value, actual_parsed.value)) {
                fail(io, "fixture mismatch for json case");
            }
        } else if (std.mem.eql(u8, case_item.output_kind, "text")) {
            if (!std.mem.eql(u8, expected.value.string, run_output.stdout)) {
                fail(io, "fixture mismatch for text case");
            }
        } else {
            fail(io, "unsupported output_kind");
        }

        try case_names.append(allocator, case_item.name);
    }

    var summary: std.ArrayList(u8) = .empty;
    defer summary.deinit(allocator);
    try summary.appendSlice(allocator, "subcmd help verification passed: ");
    for (case_names.items, 0..) |name, name_index| {
        if (name_index != 0) try summary.appendSlice(allocator, ", ");
        try summary.appendSlice(allocator, name);
    }
    try summary.appendSlice(allocator, ", plus zig test tools/lib/subcmd/help.zig");
    try guard.printLine(io, "{s}", .{summary.items});
}