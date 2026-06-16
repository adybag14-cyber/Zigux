const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const RouteEntry = struct {
    script_path: []const u8,
    args: []const []const u8,
};

pub fn routeEntryEql(a: RouteEntry, b: RouteEntry) bool {
    if (!pathsEqual(a.script_path, b.script_path)) return false;
    if (a.args.len != b.args.len) return false;
    for (a.args, b.args) |left, right| {
        if (!std.mem.eql(u8, left, right)) return false;
    }
    return true;
}

pub fn pathsEqual(left: []const u8, right: []const u8) bool {
    if (std.mem.eql(u8, left, right)) return true;
    var left_norm: [512]u8 = undefined;
    var right_norm: [512]u8 = undefined;
    const left_len = normalizeSlashes(&left_norm, left);
    const right_len = normalizeSlashes(&right_norm, right);
    return left_len == right_len and std.mem.eql(u8, left_norm[0..left_len], right_norm[0..right_len]);
}

fn normalizeSlashes(buffer: []u8, path: []const u8) usize {
    var out: usize = 0;
    for (path) |ch| {
        buffer[out] = if (ch == '\\') '/' else ch;
        out += 1;
    }
    return out;
}

pub fn shlexSplit(allocator: std.mem.Allocator, route: []const u8) ![]const []const u8 {
    var parts: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (parts.items) |part| allocator.free(part);
        parts.deinit(allocator);
    }

    var index: usize = 0;
    while (index < route.len) {
        while (index < route.len and route[index] == ' ') : (index += 1) {}
        if (index >= route.len) break;

        const quote = route[index];
        if (quote == '"' or quote == '\'') {
            index += 1;
            const start = index;
            while (index < route.len and route[index] != quote) : (index += 1) {}
            try parts.append(allocator, try allocator.dupe(u8, route[start..index]));
            if (index < route.len) index += 1;
            continue;
        }

        const start = index;
        while (index < route.len and route[index] != ' ') : (index += 1) {}
        try parts.append(allocator, try allocator.dupe(u8, route[start..index]));
    }

    return try parts.toOwnedSlice(allocator);
}

fn pyRelPathToZig(allocator: std.mem.Allocator, rel_path: []const u8) ![]const u8 {
    const normalized = try normalizeRelPath(allocator, rel_path);
    defer allocator.free(normalized);

    if (!std.mem.endsWith(u8, normalized, ".py")) {
        return try allocator.dupe(u8, normalized);
    }

    const dir = std.fs.path.dirname(normalized) orelse "";
    const base = std.fs.path.basename(normalized);
    const zig_base = guard.pyScriptToZigBasename(base);

    if (dir.len == 0) return try allocator.dupe(u8, zig_base);
    return try std.fmt.allocPrint(allocator, "{s}/{s}", .{ dir, zig_base });
}

fn normalizeRelPath(allocator: std.mem.Allocator, rel_path: []const u8) ![]const u8 {
    var buffer: [512]u8 = undefined;
    const len = normalizeSlashes(&buffer, rel_path);
    return try allocator.dupe(u8, buffer[0..len]);
}

fn ensureScriptsZiguxPath(allocator: std.mem.Allocator, script_path: []const u8) ![]const u8 {
    const normalized = try normalizeRelPath(allocator, script_path);
    defer allocator.free(normalized);

    if (std.mem.startsWith(u8, normalized, "scripts/zigux/")) {
        return try allocator.dupe(u8, normalized);
    }

    const base = std.fs.path.basename(normalized);
    return try std.fmt.allocPrint(allocator, "scripts/zigux/{s}", .{base});
}

fn argsContainSelfTest(args: []const []const u8) bool {
    for (args) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) return true;
    }
    return false;
}

fn isIgnoredScript(script_path: []const u8, ignored_scripts: []const []const u8) bool {
    for (ignored_scripts) |ignored| {
        if (pathsEqual(script_path, ignored)) return true;
    }
    return false;
}

fn appendIssue(allocator: std.mem.Allocator, issues: *std.ArrayList([]const u8), comptime fmt: []const u8, args: anytype) !void {
    const issue = try std.fmt.allocPrint(allocator, fmt, args);
    try issues.append(allocator, issue);
}

fn routeAlreadyPresent(entries: []const RouteEntry, candidate: RouteEntry) bool {
    for (entries) |entry| {
        if (routeEntryEql(entry, candidate)) return true;
    }
    return false;
}

pub fn loadManifestPythonRoutes(
    io: Io,
    allocator: std.mem.Allocator,
    repo_root: []const u8,
    manifest_rel_path: []const u8,
    want_selftest: bool,
    ignored_scripts: []const []const u8,
) !struct { entries: []RouteEntry, issues: []const []const u8 } {
    var issues: std.ArrayList([]const u8) = .empty;
    var expected: std.ArrayList(RouteEntry) = .empty;
    errdefer {
        for (issues.items) |issue| allocator.free(issue);
        issues.deinit(allocator);
        for (expected.items) |entry| freeRouteEntry(allocator, entry);
        expected.deinit(allocator);
    }

    const manifest_path = try guard.joinPath(allocator, repo_root, manifest_rel_path);
    defer allocator.free(manifest_path);

    const manifest_text = guard.readUtf8File(io, allocator, manifest_path) catch |err| switch (err) {
        guard.GuardError.IOError => {
            try appendIssue(allocator, &issues, "missing phase3 manifest: {s}", .{manifest_rel_path});
            return .{ .entries = &.{}, .issues = try issues.toOwnedSlice(allocator) };
        },
        else => return err,
    };
    defer allocator.free(manifest_text);

    var parsed = try guard.parseJsonValue(allocator, manifest_text);
    defer parsed.deinit();

    const replay_routes = guard.nestedJsonValue(parsed.value, &.{ "replay_routes" }) orelse {
        try appendIssue(allocator, &issues, "phase3 manifest replay_routes is not a list: {s}", .{manifest_rel_path});
        return .{ .entries = &.{}, .issues = try issues.toOwnedSlice(allocator) };
    };

    const routes_array = switch (replay_routes) {
        .array => |array| array,
        else => {
            try appendIssue(allocator, &issues, "phase3 manifest replay_routes is not a list: {s}", .{manifest_rel_path});
            return .{ .entries = &.{}, .issues = try issues.toOwnedSlice(allocator) };
        },
    };

    for (routes_array.items, 0..) |route_value, index| {
        const route = switch (route_value) {
            .string => |text| text,
            else => {
                try appendIssue(allocator, &issues, "phase3 manifest replay_routes has non-string entry at index {d}: {any}", .{ index, route_value });
                continue;
            },
        };

        const parts = try shlexSplit(allocator, route);
        defer {
            for (parts) |part| allocator.free(part);
            allocator.free(parts);
        }

        if (parts.len >= 2 and std.mem.eql(u8, parts[0], "python3")) {
            if (parts.len < 2) {
                try appendIssue(allocator, &issues, "phase3 manifest python replay route missing script path at index {d}: {s}", .{ index, route });
                continue;
            }

            const raw_script = parts[1];
            const args = parts[2..];
            const has_selftest = argsContainSelfTest(args);
            if (want_selftest != has_selftest) continue;

            const normalized_script = try normalizeRelPath(allocator, raw_script);
            defer allocator.free(normalized_script);

            if (!std.mem.startsWith(u8, normalized_script, "scripts/zigux/") or
                (!std.mem.endsWith(u8, normalized_script, ".py") and !std.mem.endsWith(u8, normalized_script, ".zig")))
            {
                try appendIssue(allocator, &issues, "phase3 manifest python replay route outside scripts/zigux at index {d}: {s}", .{ index, route });
                continue;
            }

            const zig_script = try pyRelPathToZig(allocator, normalized_script);
            defer allocator.free(zig_script);

            if (isIgnoredScript(zig_script, ignored_scripts)) continue;

            const owned_args = try dupArgs(allocator, args);
            const entry = RouteEntry{
                .script_path = try allocator.dupe(u8, zig_script),
                .args = owned_args,
            };
            if (!routeAlreadyPresent(expected.items, entry)) {
                try expected.append(allocator, entry);
            } else {
                freeRouteEntry(allocator, entry);
            }
            continue;
        }

        if (parts.len >= 3 and std.mem.eql(u8, parts[0], "zig") and std.mem.eql(u8, parts[1], "run")) {
            const raw_script = parts[2];
            var arg_start: usize = 3;
            if (arg_start < parts.len and std.mem.eql(u8, parts[arg_start], "--")) {
                arg_start += 1;
            }
            const args = parts[arg_start..];
            const has_selftest = argsContainSelfTest(args);
            if (want_selftest != has_selftest) continue;

            const zig_script = try ensureScriptsZiguxPath(allocator, raw_script);
            defer allocator.free(zig_script);

            if (!std.mem.endsWith(u8, zig_script, ".zig")) {
                try appendIssue(allocator, &issues, "phase3 manifest zig replay route outside scripts/zigux at index {d}: {s}", .{ index, route });
                continue;
            }

            if (isIgnoredScript(zig_script, ignored_scripts)) continue;

            const owned_args = try dupArgs(allocator, args);
            const entry = RouteEntry{
                .script_path = try allocator.dupe(u8, zig_script),
                .args = owned_args,
            };
            if (!routeAlreadyPresent(expected.items, entry)) {
                try expected.append(allocator, entry);
            } else {
                freeRouteEntry(allocator, entry);
            }
            continue;
        }
    }

    return .{
        .entries = try expected.toOwnedSlice(allocator),
        .issues = try issues.toOwnedSlice(allocator),
    };
}

pub fn freeRouteEntries(allocator: std.mem.Allocator, entries: []RouteEntry) void {
    for (entries) |entry| freeRouteEntry(allocator, entry);
    allocator.free(entries);
}

pub fn freeRouteEntry(allocator: std.mem.Allocator, entry: RouteEntry) void {
    allocator.free(entry.script_path);
    freeArgs(allocator, entry.args);
}

fn dupArgs(allocator: std.mem.Allocator, args: []const []const u8) ![]const []const u8 {
    const owned = try allocator.alloc([]const u8, args.len);
    for (args, 0..) |arg, index| {
        owned[index] = try allocator.dupe(u8, arg);
    }
    return owned;
}

fn freeArgs(allocator: std.mem.Allocator, args: []const []const u8) void {
    for (args) |arg| allocator.free(arg);
    allocator.free(args);
}

pub fn formatRouteEntry(allocator: std.mem.Allocator, entry: RouteEntry) ![]const u8 {
    if (entry.args.len == 0) return try allocator.dupe(u8, entry.script_path);
    var parts: std.ArrayList([]const u8) = .empty;
    defer parts.deinit(allocator);
    try parts.append(allocator, entry.script_path);
    for (entry.args) |arg| try parts.append(allocator, arg);
    return try std.mem.join(allocator, " ", parts.items);
}

pub fn appendMissingManifestRouteIssues(
    allocator: std.mem.Allocator,
    issues: *std.ArrayList([]const u8),
    expected: []const RouteEntry,
    actual: []const RouteEntry,
    comptime label: []const u8,
) !void {
    for (expected) |expected_entry| {
        var found = false;
        for (actual) |actual_entry| {
            if (routeEntryEql(expected_entry, actual_entry)) {
                found = true;
                break;
            }
        }
        if (found) continue;
        const formatted = try formatRouteEntry(allocator, expected_entry);
        defer allocator.free(formatted);
        try appendIssue(allocator, issues, "{s} {s}", .{ label, formatted });
    }
}

pub fn appendMissingManifestScriptIssues(
    allocator: std.mem.Allocator,
    issues: *std.ArrayList([]const u8),
    expected_scripts: []const []const u8,
    actual_scripts: []const []const u8,
    comptime label: []const u8,
) !void {
    for (expected_scripts) |expected_script| {
        var found = false;
        for (actual_scripts) |actual_script| {
            if (pathsEqual(expected_script, actual_script)) {
                found = true;
                break;
            }
        }
        if (found) continue;
        try appendIssue(allocator, issues, "{s} {s}", .{ label, expected_script });
    }
}