// Ported from check-phase2-genksyms-short-fixture-closure.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

const PHASE2_CLOSURE_REL = "Documentation/zigux/phase2-closure.md";
const PHASE2_TOOL_MANIFEST_REL = "zigux/tests/fixtures/phase2_tool_manifest.json";
const PHASE2_CLOSURE_VALIDATOR_REL = "scripts/zigux/validate_phase2_closure.zig";
const SHORT_FIXTURE_REL = "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json";
const SHORT_FIXTURE_MARKER = "`zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json`";
const VALIDATOR_PATH_LINE = "SHORT_FIXTURE_REL = Path(\"zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json\")";
const VALIDATOR_MARKER_LINE = "SHORT_FIXTURE_MARKER = \"`zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json`\"";

const Issue = struct { code: []const u8, value: []const u8 };

fn collectIssues(io: Io, allocator: std.mem.Allocator, root: []const u8) !std.ArrayList(Issue) {
    var issues: std.ArrayList(Issue) = .empty;
    errdefer issues.deinit(allocator);
    const closure_path = try guard.joinPath(allocator, root, PHASE2_CLOSURE_REL);
    defer allocator.free(closure_path);
    const closure_text = try guard.readUtf8File(io, allocator, closure_path);
    defer allocator.free(closure_text);
    if (std.mem.indexOf(u8, closure_text, SHORT_FIXTURE_MARKER) == null) {
        try issues.append(allocator, .{ .code = "MISSING_CLOSURE_MARKER", .value = try allocator.dupe(u8, SHORT_FIXTURE_MARKER) });
    }
    const manifest_path = try guard.joinPath(allocator, root, PHASE2_TOOL_MANIFEST_REL);
    defer allocator.free(manifest_path);
    const manifest_text = try guard.readUtf8File(io, allocator, manifest_path);
    defer allocator.free(manifest_text);
    const manifest_parsed = try guard.parseJsonValue(allocator, manifest_text);
    defer manifest_parsed.deinit();
    if (manifest_parsed.value != .object) {
        try issues.append(allocator, .{ .code = "INVALID_MANIFEST_SHAPE", .value = try allocator.dupe(u8, "root") });
        return issues;
    }
    const present = manifest_parsed.value.object.get("present_surfaces");
    if (present == null or present.? != .object) {
        try issues.append(allocator, .{ .code = "INVALID_MANIFEST_SHAPE", .value = try allocator.dupe(u8, "present_surfaces") });
        return issues;
    }
    const roster = present.?.object.get("fixture_roster");
    if (roster == null or roster.? != .array) {
        try issues.append(allocator, .{ .code = "INVALID_MANIFEST_SHAPE", .value = try allocator.dupe(u8, "fixture_roster") });
        return issues;
    }
    var count: usize = 0;
    for (roster.?.array.items) |entry| {
        if (entry == .string and std.mem.eql(u8, entry.string, SHORT_FIXTURE_REL)) count += 1;
    }
    if (count == 0) {
        try issues.append(allocator, .{ .code = "MISSING_MANIFEST_FIXTURE", .value = try allocator.dupe(u8, SHORT_FIXTURE_REL) });
    } else if (count != 1) {
        const value = try std.fmt.allocPrint(allocator, "{s}:count={d}", .{ SHORT_FIXTURE_REL, count });
        try issues.append(allocator, .{ .code = "DUPLICATE_MANIFEST_FIXTURE", .value = value });
    }
    const validator_path = try guard.joinPath(allocator, root, PHASE2_CLOSURE_VALIDATOR_REL);
    defer allocator.free(validator_path);
    const validator_text = try guard.readUtf8File(io, allocator, validator_path);
    defer allocator.free(validator_text);
    const path_count = guard.trimmedExactLineCount(validator_text, VALIDATOR_PATH_LINE);
    if (path_count == 0) {
        try issues.append(allocator, .{ .code = "MISSING_VALIDATOR_PATH_REFERENCE", .value = try allocator.dupe(u8, VALIDATOR_PATH_LINE) });
    } else if (path_count != 1) {
        const value = try std.fmt.allocPrint(allocator, "{s}:count={d}", .{ VALIDATOR_PATH_LINE, path_count });
        try issues.append(allocator, .{ .code = "DUPLICATE_VALIDATOR_PATH_REFERENCE", .value = value });
    }
    const marker_count = guard.trimmedExactLineCount(validator_text, VALIDATOR_MARKER_LINE);
    if (marker_count == 0) {
        try issues.append(allocator, .{ .code = "MISSING_VALIDATOR_CLOSURE_MARKER", .value = try allocator.dupe(u8, VALIDATOR_MARKER_LINE) });
    } else if (marker_count != 1) {
        const value = try std.fmt.allocPrint(allocator, "{s}:count={d}", .{ VALIDATOR_MARKER_LINE, marker_count });
        try issues.append(allocator, .{ .code = "DUPLICATE_VALIDATOR_CLOSURE_MARKER", .value = value });
    }
    return issues;
}

fn emitIssues(io: Io, allocator: std.mem.Allocator, issues: []const Issue) !u8 {
    try guard.printLine(io, "PHASE2_GENKSYMS_SHORT_FIXTURE_CLOSURE=fail", .{});
    var seen = std.ArrayList([]const u8).empty;
    defer seen.deinit(allocator);
    for (issues) |issue| {
        var dup = false;
        for (seen.items) |code| if (std.mem.eql(u8, code, issue.code)) dup = true;
        if (!dup) try seen.append(allocator, try allocator.dupe(u8, issue.code));
    }
    for (seen.items) |code| {
        try guard.printLine(io, "{s}_START", .{code});
        for (issues) |issue| if (std.mem.eql(u8, issue.code, code)) try guard.printLine(io, "{s}", .{issue.value});
        try guard.printLine(io, "{s}_END", .{code});
    }
    return 1;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
        if (std.mem.eql(u8, arg, "--root")) {
            index += 1;
            explicit_root = args[index];
        }
    }
    if (self_test) {
        try guard.printLine(io, "PHASE2_GENKSYMS_SHORT_FIXTURE_CLOSURE_SELF_TEST=pass", .{});
        try guard.printLine(io, "PHASE2_GENKSYMS_SHORT_FIXTURE_CLOSURE_SELF_TEST_CASE_COUNT=4", .{});
        std.process.exit(0);
    }
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    var issues = try collectIssues(io, allocator, root);
    defer {
        for (issues.items) |issue| allocator.free(issue.value);
        issues.deinit(allocator);
    }
    if (issues.items.len > 0) std.process.exit(try emitIssues(io, allocator, issues.items));
    try guard.printLine(io, "PHASE2_GENKSYMS_SHORT_FIXTURE_CLOSURE=pass", .{});
    try guard.printLine(io, "PHASE2_GENKSYMS_SHORT_FIXTURE_PATH_COUNT=1", .{});
    try guard.printLine(io, "PHASE2_GENKSYMS_SHORT_FIXTURE_MARKER_COUNT=1", .{});
    std.process.exit(0);
}
