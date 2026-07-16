const std = @import("std");
const Io = std.Io;

pub const GuardError = error{
    MissingMarker,
    MissingOrderedMarkers,
    WrongOrder,
    WrongCount,
    WrongLineCount,
    IOError,
    OutOfMemory,
    JsonError,
    ValidationFailed,
    SelfTestFailed,
};

pub fn repoRootFromScript(allocator: std.mem.Allocator) ![]const u8 {
    return defaultRepoRoot(allocator);
}

pub fn defaultRepoRoot(allocator: std.mem.Allocator) ![]const u8 {
    const script_path = @src().file;
    if (std.fs.path.dirname(script_path)) |script_dir| {
        if (std.fs.path.dirname(script_dir)) |scripts_dir| {
            if (std.fs.path.dirname(scripts_dir)) |root| {
                return try allocator.dupe(u8, root);
            }
        }
    }
    return try allocator.dupe(u8, ".");
}

pub fn joinPath(allocator: std.mem.Allocator, root: []const u8, suffix: []const u8) ![]const u8 {
    return std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, suffix });
}

pub fn pathExists(io: Io, path: []const u8) bool {
    std.Io.Dir.cwd().access(io, path, .{}) catch return false;
    return true;
}

pub fn readUtf8File(
    io: Io,
    allocator: std.mem.Allocator,
    path: []const u8,
) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, allocator, .unlimited) catch |err| switch (err) {
        error.FileNotFound => return GuardError.IOError,
        else => return err,
    };
}

pub fn writeUtf8File(io: Io, path: []const u8, data: []const u8) !void {
    if (std.fs.path.dirname(path)) |parent| {
        try std.Io.Dir.cwd().createDirPath(io, parent);
    }
    try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = path, .data = data });
}

pub fn deleteFile(io: Io, path: []const u8) !void {
    try std.Io.Dir.cwd().deleteFile(io, path);
}

pub fn trimmedExactLineCount(text: []const u8, line: []const u8) usize {
    const want = std.mem.trim(u8, line, " \t\r");
    var count: usize = 0;
    var iter = std.mem.splitScalar(u8, text, '\n');
    while (iter.next()) |current| {
        if (std.mem.eql(u8, std.mem.trim(u8, current, " \t\r"), want)) count += 1;
    }
    return count;
}

pub fn requireExactTrimmedLine(text: []const u8, label: []const u8, line: []const u8) GuardError!void {
    const count = trimmedExactLineCount(text, line);
    if (count != 1) return GuardError.WrongLineCount;
    _ = label;
}

pub fn appendExactTrimmedLineIssue(
    allocator: std.mem.Allocator,
    failures: *std.ArrayList([]const u8),
    text: []const u8,
    label: []const u8,
    line: []const u8,
) !void {
    const count = trimmedExactLineCount(text, line);
    if (count == 1) return;
    const issue = try std.fmt.allocPrint(allocator, "{s}:expected=1:actual={d}", .{ label, count });
    try failures.append(allocator, issue);
}

pub fn appendAbsentTrimmedLineIssue(
    allocator: std.mem.Allocator,
    failures: *std.ArrayList([]const u8),
    text: []const u8,
    label: []const u8,
    line: []const u8,
) !void {
    const count = trimmedExactLineCount(text, line);
    if (count == 0) return;
    const issue = try std.fmt.allocPrint(allocator, "{s}:expected=0:actual={d}", .{ label, count });
    try failures.append(allocator, issue);
}

pub fn requireMarker(haystack: []const u8, marker: []const u8) GuardError!void {
    if (std.mem.indexOf(u8, haystack, marker) == null) return GuardError.MissingMarker;
}

pub fn requireAnyMarker(haystack: []const u8, markers: []const []const u8) GuardError!void {
    for (markers) |marker| {
        if (std.mem.indexOf(u8, haystack, marker) != null) return;
    }
    return GuardError.MissingMarker;
}

pub fn requireOrder(haystack: []const u8, earlier: []const u8, later: []const u8) GuardError!void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return GuardError.MissingOrderedMarkers;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return GuardError.MissingOrderedMarkers;
    if (earlier_index >= later_index) return GuardError.WrongOrder;
}

pub fn requireExactCount(haystack: []const u8, marker: []const u8, expected: usize) GuardError!void {
    if (countOccurrences(haystack, marker) != expected) return GuardError.WrongCount;
}

pub fn requireExactLineCount(haystack: []const u8, marker: []const u8, expected: usize) GuardError!void {
    var actual: usize = 0;
    var iter = std.mem.splitScalar(u8, haystack, '\n');
    while (iter.next()) |line| {
        const logical_line = std.mem.trimEnd(u8, line, "\r");
        if (std.mem.eql(u8, logical_line, marker) or
            std.mem.eql(u8, std.mem.trim(u8, logical_line, " \t"), marker))
        {
            actual += 1;
        }
    }
    if (actual != expected) return GuardError.WrongLineCount;
}

pub fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (start < haystack.len) {
        const slice = haystack[start..];
        const index = std.mem.indexOf(u8, slice, needle) orelse break;
        count += 1;
        start += index + needle.len;
    }
    return count;
}

pub fn findFirstMarker(haystack: []const u8, markers: []const []const u8) ?[]const u8 {
    var earliest_index: ?usize = null;
    var earliest_marker: ?[]const u8 = null;
    for (markers) |marker| {
        const index = std.mem.indexOf(u8, haystack, marker) orelse continue;
        if (earliest_index) |prev| {
            if (index < prev) {
                earliest_index = index;
                earliest_marker = marker;
            }
        } else {
            earliest_index = index;
            earliest_marker = marker;
        }
    }
    return earliest_marker;
}

pub fn findFirstMarkerAfter(haystack: []const u8, anchor: []const u8, markers: []const []const u8) ?[]const u8 {
    const anchor_index = std.mem.indexOf(u8, haystack, anchor) orelse return null;
    return findFirstMarker(haystack[anchor_index..], markers);
}

pub fn extractBetween(haystack: []const u8, start_marker: []const u8, end_marker: []const u8) GuardError![]const u8 {
    const start = std.mem.indexOf(u8, haystack, start_marker) orelse return GuardError.MissingMarker;
    const after_start = start + start_marker.len;
    const end = std.mem.indexOfPos(u8, haystack, after_start, end_marker) orelse return GuardError.MissingMarker;
    return haystack[start..end];
}

pub fn failMessage(
    io: Io,
    allocator: std.mem.Allocator,
    comptime prefix: []const u8,
    detail: []const u8,
) !void {
    const message = try std.fmt.allocPrint(allocator, "{s}: {s}", .{ prefix, detail });
    defer allocator.free(message);
    try printLine(io, "{s}", .{message});
}

pub fn printLine(io: Io, comptime fmt: []const u8, args: anytype) !void {
    var buffer: [1024]u8 = undefined;
    var writer = Io.File.stdout().writer(io, &buffer);
    try writer.interface.print(fmt ++ "\n", args);
    try writer.interface.flush();
}

pub fn gitBlobSha(allocator: std.mem.Allocator, data: []const u8) ![]const u8 {
    const header = try std.fmt.allocPrint(allocator, "blob {d}\x00", .{data.len});
    defer allocator.free(header);
    var hasher = std.crypto.hash.Sha1.init(.{});
    hasher.update(header);
    hasher.update(data);
    var digest: [20]u8 = undefined;
    hasher.final(&digest);
    return try std.fmt.allocPrint(allocator, "{s}", .{std.fmt.fmtSliceHexLower(&digest)});
}

pub fn pyScriptToZigBasename(py_script: []const u8) []const u8 {
    if (!std.mem.endsWith(u8, py_script, ".py")) return py_script;
    var buffer: [256]u8 = undefined;
    const stem = py_script[0 .. py_script.len - ".py".len];
    var out_len: usize = 0;
    for (stem) |ch| {
        const out_ch: u8 = if (ch == '-') '_' else ch;
        buffer[out_len] = out_ch;
        out_len += 1;
    }
    const copied = std.fmt.bufPrint(buffer[out_len..], ".zig", .{}) catch return py_script;
    out_len += copied.len;
    return buffer[0..out_len];
}

pub fn substitutePhase1PyRoutes(allocator: std.mem.Allocator, text: []const u8) ![]const u8 {
    var result = try allocator.dupe(u8, text);
    errdefer allocator.free(result);

    const replacements = [_]struct { py: []const u8, zig: []const u8 }{
        .{ .py = "python3 scripts/zigux/check-phase1-", .zig = "zig run scripts/zigux/check_phase1_" },
        .{ .py = "scripts/zigux/check-phase1-", .zig = "scripts/zigux/check_phase1_" },
        .{ .py = "check-phase1-", .zig = "check_phase1_" },
    };

    for (replacements) |pair| {
        if (std.mem.indexOf(u8, result, pair.py) == null) continue;
        var parts: std.ArrayList(u8) = .empty;
        defer parts.deinit(allocator);
        var start: usize = 0;
        while (start < result.len) {
            const slice = result[start..];
            const index = std.mem.indexOf(u8, slice, pair.py) orelse {
                try parts.appendSlice(allocator, slice);
                break;
            };
            try parts.appendSlice(allocator, slice[0..index]);
            try parts.appendSlice(allocator, pair.zig);
            start += index + pair.py.len;
            if (std.mem.startsWith(u8, pair.py, "check-phase1-") or std.mem.startsWith(u8, pair.py, "scripts/zigux/check-phase1-")) {
                var end = start;
                while (end < result.len and result[end] != '.' and result[end] != '`' and result[end] != ' ' and result[end] != ',') : (end += 1) {}
                while (start < end) : (start += 1) {
                    const ch = result[start];
                    try parts.append(allocator, if (ch == '-') '_' else ch);
                }
            }
        }
        allocator.free(result);
        result = try parts.toOwnedSlice(allocator);
    }
    return result;
}

pub const RoutePair = struct {
    python_route: []const u8,
    zig_route: []const u8,

    pub fn contains(self: RoutePair, haystack: []const u8) bool {
        return std.mem.indexOf(u8, haystack, self.python_route) != null or
            std.mem.indexOf(u8, haystack, self.zig_route) != null;
    }

    pub fn require(self: RoutePair, haystack: []const u8) GuardError!void {
        if (!self.contains(haystack)) return GuardError.MissingMarker;
    }

    pub fn index(self: RoutePair, haystack: []const u8) ?usize {
        const py = std.mem.indexOf(u8, haystack, self.python_route);
        const zi = std.mem.indexOf(u8, haystack, self.zig_route);
        if (py) |p| {
            if (zi) |z| return @min(p, z);
            return p;
        }
        return zi;
    }

    pub fn requireOrder(self: RoutePair, haystack: []const u8, later: RoutePair) GuardError!void {
        const earlier_index = self.index(haystack) orelse return GuardError.MissingOrderedMarkers;
        const later_index = later.index(haystack) orelse return GuardError.MissingOrderedMarkers;
        if (earlier_index >= later_index) return GuardError.WrongOrder;
    }
};

pub fn scriptRoutePair(py_script: []const u8, zig_script: []const u8) RoutePair {
    return .{ .python_route = py_script, .zig_route = zig_script };
}

pub fn jsonValuesEqual(a: std.json.Value, b: std.json.Value) bool {
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

pub fn nestedJsonValue(data: std.json.Value, path: []const []const u8) ?std.json.Value {
    var current = data;
    for (path) |key| {
        switch (current) {
            .object => |object| {
                current = object.get(key) orelse return null;
            },
            else => return null,
        }
    }
    return current;
}

pub fn collectDuplicateJsonKeyPaths(
    allocator: std.mem.Allocator,
    data: std.json.Value,
    prefix: []const u8,
    paths: *std.ArrayList([]const u8),
) !void {
    switch (data) {
        .object => |object| {
            var counts = std.StringHashMap(usize).init(allocator);
            defer counts.deinit();
            var it = object.iterator();
            while (it.next()) |entry| {
                const count = counts.get(entry.key_ptr.*) orelse 0;
                if (count == 1) {
                    const path = if (prefix.len == 0)
                        try allocator.dupe(u8, entry.key_ptr.*)
                    else
                        try std.fmt.allocPrint(allocator, "{s}.{s}", .{ prefix, entry.key_ptr.* });
                    try paths.append(allocator, path);
                }
                try counts.put(entry.key_ptr.*, count + 1);
            }
            it = object.iterator();
            while (it.next()) |entry| {
                const child_prefix = if (prefix.len == 0)
                    entry.key_ptr.*
                else
                    try std.fmt.allocPrint(allocator, "{s}.{s}", .{ prefix, entry.key_ptr.* });
                defer if (prefix.len != 0) allocator.free(child_prefix);
                try collectDuplicateJsonKeyPaths(allocator, entry.value_ptr.*, child_prefix, paths);
            }
        },
        .array => |array| {
            for (array.items) |item| {
                try collectDuplicateJsonKeyPaths(allocator, item, prefix, paths);
            }
        },
        else => {},
    }
}

pub fn appendJsonValueMismatch(
    allocator: std.mem.Allocator,
    failures: *std.ArrayList([]const u8),
    label: []const u8,
    actual: ?std.json.Value,
    comptime expected_fmt: []const u8,
    expected_args: anytype,
) !void {
    const expected = try std.fmt.allocPrint(allocator, expected_fmt, expected_args);
    defer allocator.free(expected);
    const actual_text = try jsonValueToDisplay(allocator, actual);
    defer allocator.free(actual_text);
    const issue = try std.fmt.allocPrint(allocator, "{s}:expected={s}:actual={s}", .{ label, expected, actual_text });
    try failures.append(allocator, issue);
}

pub fn jsonValueToDisplay(allocator: std.mem.Allocator, value: ?std.json.Value) ![]const u8 {
    const actual = value orelse return try allocator.dupe(u8, "null");
    return switch (actual) {
        .string => |text| try allocator.dupe(u8, text),
        .integer => |number| try std.fmt.allocPrint(allocator, "{d}", .{number}),
        .float => |number| try std.fmt.allocPrint(allocator, "{d}", .{number}),
        .bool => |flag| try allocator.dupe(u8, if (flag) "true" else "false"),
        .null => try allocator.dupe(u8, "null"),
        else => try allocator.dupe(u8, "non_scalar"),
    };
}

pub fn appendExactOccurrenceIssue(
    allocator: std.mem.Allocator,
    failures: *std.ArrayList([]const u8),
    text: []const u8,
    label: []const u8,
    marker: []const u8,
) !void {
    const count = countOccurrences(text, marker);
    if (count == 1) return;
    const issue = try std.fmt.allocPrint(allocator, "{s}:expected=1:actual={d}", .{ label, count });
    try failures.append(allocator, issue);
}

pub fn appendOnceOccurrenceIssue(
    allocator: std.mem.Allocator,
    failures: *std.ArrayList([]const u8),
    text: []const u8,
    label: []const u8,
    needle: []const u8,
) !void {
    const count = countOccurrences(text, needle);
    if (count == 1) return;
    const issue = try std.fmt.allocPrint(allocator, "{s}:expected_once:actual_count={d}:{s}", .{ label, count, needle });
    try failures.append(allocator, issue);
}

pub fn appendExactTrimmedLineOnceIssue(
    allocator: std.mem.Allocator,
    failures: *std.ArrayList([]const u8),
    text: []const u8,
    label: []const u8,
    needle: []const u8,
) !void {
    const count = trimmedExactLineCount(text, needle);
    if (count == 1) return;
    const issue = try std.fmt.allocPrint(allocator, "{s}:expected_once:actual_count={d}:{s}", .{ label, count, needle });
    try failures.append(allocator, issue);
}

pub fn appendMissingMarkerIssue(
    allocator: std.mem.Allocator,
    failures: *std.ArrayList([]const u8),
    marker: []const u8,
) !void {
    const issue = try std.fmt.allocPrint(allocator, "missing_marker:{s}", .{marker});
    try failures.append(allocator, issue);
}

pub fn appendMissingFileIssue(
    allocator: std.mem.Allocator,
    failures: *std.ArrayList([]const u8),
    relative_path: []const u8,
) !void {
    const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
    try failures.append(allocator, issue);
}

pub fn requireJsonFieldEqual(
    allocator: std.mem.Allocator,
    failures: *std.ArrayList([]const u8),
    label: []const u8,
    actual: ?std.json.Value,
    expected: std.json.Value,
) !void {
    if (actual) |value| {
        if (jsonValuesEqual(value, expected)) return;
    }
    try appendJsonValueMismatch(allocator, failures, label, actual, "{any}", .{expected});
}

pub fn findZigExecutable(
    io: Io,
    allocator: std.mem.Allocator,
    root: []const u8,
    explicit: ?[]const u8,
) ![]const u8 {
    if (explicit) |path| return try allocator.dupe(u8, path);
    const toolchain_glob = try std.fmt.allocPrint(allocator, "{s}/.zig-toolchain", .{root});
    defer allocator.free(toolchain_glob);
    if (pathExists(io, toolchain_glob)) {
        var dir = try std.Io.Dir.cwd().openDir(io, toolchain_glob, .{ .iterate = true });
        defer dir.close(io);
        var it = dir.iterate();
        var latest: ?[]const u8 = null;
        while (try it.next(io)) |entry| {
            if (entry.kind != .directory) continue;
            const candidate = try std.fmt.allocPrint(allocator, "{s}/.zig-toolchain/{s}/zig.exe", .{ root, entry.name });
            defer allocator.free(candidate);
            if (pathExists(io, candidate)) {
                if (latest) |prev| allocator.free(prev);
                latest = try std.fmt.allocPrint(allocator, "{s}/.zig-toolchain/{s}/zig.exe", .{ root, entry.name });
            }
        }
        if (latest) |path| return path;
    }
    return error.FileNotFound;
}

pub fn parseJsonValue(allocator: std.mem.Allocator, text: []const u8) !std.json.Parsed(std.json.Value) {
    return std.json.parseFromSlice(std.json.Value, allocator, text, .{});
}

pub const ProcessOutput = struct {
    stdout: []const u8,
    stderr: []const u8,
    exit_code: u8,
};

pub fn runProcessCapture(
    io: Io,
    allocator: std.mem.Allocator,
    argv: []const []const u8,
    cwd: ?[]const u8,
) !ProcessOutput {
    const cwd_arg: std.process.Child.Cwd = if (cwd) |path| .{ .path = path } else .inherit;
    const result = try std.process.run(allocator, io, .{
        .argv = argv,
        .cwd = cwd_arg,
        .stdout_limit = .limited(8 * 1024 * 1024),
        .stderr_limit = .limited(8 * 1024 * 1024),
    });
    const exit_code: u8 = switch (result.term) {
        .exited => |code| @intCast(code),
        else => 1,
    };
    return .{
        .stdout = result.stdout,
        .stderr = result.stderr,
        .exit_code = exit_code,
    };
}

var tmp_counter: std.atomic.Value(u32) = .init(0);

pub const TempWorkspace = struct {
    io: Io,
    allocator: std.mem.Allocator,
    sub_path: []const u8,

    pub fn init(io: Io, allocator: std.mem.Allocator, prefix: []const u8) !TempWorkspace {
        const id = tmp_counter.fetchAdd(1, .monotonic);
        const sub_path = try std.fmt.allocPrint(allocator, "phase1_guard_{s}_{d}", .{ prefix, id });
        const root = try std.fmt.allocPrint(allocator, ".zig-cache/tmp/{s}", .{sub_path});
        defer allocator.free(root);
        std.Io.Dir.cwd().deleteTree(io, root) catch {};
        try std.Io.Dir.cwd().createDirPath(io, root);
        return .{ .io = io, .allocator = allocator, .sub_path = sub_path };
    }

    pub fn deinit(self: *TempWorkspace) void {
        const root = std.fmt.allocPrint(self.allocator, ".zig-cache/tmp/{s}", .{self.sub_path}) catch return;
        defer self.allocator.free(root);
        std.Io.Dir.cwd().deleteTree(self.io, root) catch {};
        self.allocator.free(self.sub_path);
    }

    pub fn rootPath(self: *const TempWorkspace, allocator: std.mem.Allocator) ![]const u8 {
        return std.fmt.allocPrint(allocator, ".zig-cache/tmp/{s}", .{self.sub_path});
    }

    pub fn write(self: *const TempWorkspace, relative: []const u8, data: []const u8) !void {
        const path = try std.fmt.allocPrint(self.allocator, ".zig-cache/tmp/{s}/{s}", .{ self.sub_path, relative });
        defer self.allocator.free(path);
        try writeUtf8File(self.io, path, data);
    }
};

pub fn expectSelfTest(condition: bool) GuardError!void {
    if (!condition) return GuardError.SelfTestFailed;
}

test "requireMarker finds embedded marker" {
    try requireMarker("alpha beta gamma", "beta");
}

test "requireOrder enforces earlier-before-later" {
    try requireOrder("abc def ghi", "abc", "ghi");
}

test "requireExactCount counts non-overlapping hits" {
    try requireExactCount("foo bar foo", "foo", 2);
}

test "pyScriptToZigBasename converts hyphenated script names" {
    try std.testing.expectEqualStrings("check_phase1_route_summary_counts.zig", pyScriptToZigBasename("check-phase1-route-summary-counts.py"));
}