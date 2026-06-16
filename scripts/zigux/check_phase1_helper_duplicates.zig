// Ported from check-phase1-helper-duplicates.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

const DEFAULT_FILES = [_][]const u8{
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/string.zig",
    "tools/lib/rbtree.zig",
};

const TopLevelDecl = struct {
    line: usize,
    kind: []const u8,
    name: []const u8,
};

fn isTopLevelDeclLine(line: []const u8) bool {
    if (line.len == 0) return false;
    return line[0] != ' ' and line[0] != '\t';
}

fn topLevelDeclarations(text: []const u8, allocator: std.mem.Allocator) !std.ArrayList(TopLevelDecl) {
    var declarations: std.ArrayList(TopLevelDecl) = .empty;
    errdefer declarations.deinit(allocator);

    var line_no: usize = 1;
    var iter = std.mem.splitScalar(u8, text, '\n');
    while (iter.next()) |line| {
        if (!isTopLevelDeclLine(line)) {
            line_no += 1;
            continue;
        }
        const trimmed = std.mem.trim(u8, line, " \t\r");
        if (std.mem.startsWith(u8, trimmed, "pub fn ") or std.mem.startsWith(u8, trimmed, "fn ")) {
            const rest = if (std.mem.startsWith(u8, trimmed, "pub fn "))
                trimmed["pub fn ".len..]
            else
                trimmed["fn ".len..];
            const name_end = std.mem.indexOfScalar(u8, rest, '(') orelse {
                line_no += 1;
                continue;
            };
            const name = try allocator.dupe(u8, rest[0..name_end]);
            try declarations.append(allocator, .{ .line = line_no, .kind = "fn", .name = name });
        } else if (std.mem.startsWith(u8, trimmed, "pub const ") or std.mem.startsWith(u8, trimmed, "const ")) {
            const rest = if (std.mem.startsWith(u8, trimmed, "pub const "))
                trimmed["pub const ".len..]
            else
                trimmed["const ".len..];
            const name_end = std.mem.indexOfScalar(u8, rest, ':') orelse std.mem.indexOfScalar(u8, rest, '=') orelse {
                line_no += 1;
                continue;
            };
            const name = try allocator.dupe(u8, std.mem.trim(u8, rest[0..name_end], " \t"));
            try declarations.append(allocator, .{ .line = line_no, .kind = "const", .name = name });
        }
        line_no += 1;
    }
    return declarations;
}

fn duplicateReport(
    io: Io,
    allocator: std.mem.Allocator,
    path: []const u8,
) !std.ArrayList([]const u8) {
    var problems: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (problems.items) |item| allocator.free(item);
        problems.deinit(allocator);
    }

    const text = try guard.readUtf8File(io, allocator, path);
    defer allocator.free(text);

    var declarations = try topLevelDeclarations(text, allocator);
    defer {
        for (declarations.items) |entry| allocator.free(entry.name);
        declarations.deinit(allocator);
    }

    var seen = std.StringHashMap(std.ArrayList(usize)).init(allocator);
    defer {
        var it = seen.iterator();
        while (it.next()) |entry| {
            entry.value_ptr.deinit(allocator);
        }
        seen.deinit();
    }

    for (declarations.items) |entry| {
        const gop = try seen.getOrPut(entry.name);
        if (!gop.found_existing) {
            gop.value_ptr.* = .empty;
        }
        try gop.value_ptr.append(allocator, entry.line);
    }

    var names = std.ArrayList([]const u8).empty;
    defer names.deinit(allocator);
    var it = seen.iterator();
    while (it.next()) |entry| {
        try names.append(allocator, entry.key_ptr.*);
    }
    std.sort.block(
        []const u8,
        names.items,
        {},
        struct {
            fn lessThan(_: void, a: []const u8, b: []const u8) bool {
                return std.mem.order(u8, a, b) == .lt;
            }
        }.lessThan,
    );

    for (names.items) |name| {
        const lines = seen.get(name).?;
        if (lines.items.len <= 1) continue;
        var rendered = std.ArrayList(u8).empty;
        defer rendered.deinit(allocator);
        for (lines.items, 0..) |line, index| {
            if (index > 0) try rendered.appendSlice(allocator, ", ");
            const piece = try std.fmt.allocPrint(allocator, "{d}", .{line});
            defer allocator.free(piece);
            try rendered.appendSlice(allocator, piece);
        }
        const issue = try std.fmt.allocPrint(
            allocator,
            "{s}: duplicate top-level declaration `{s}` at lines {s}",
            .{ path, name, rendered.items },
        );
        try problems.append(allocator, issue);
    }

    return problems;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    const paths: []const []const u8 = if (args.len > 1) args[1..] else &DEFAULT_FILES;

    var missing: std.ArrayList([]const u8) = .empty;
    defer {
        for (missing.items) |item| allocator.free(item);
        missing.deinit(allocator);
    }

    for (paths) |path| {
        if (!guard.pathExists(io, path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing file: {s}", .{path});
            try missing.append(allocator, issue);
        }
    }

    if (missing.items.len > 0) {
        for (missing.items) |item| {
            var buffer: [512]u8 = undefined;
            var writer = Io.File.stderr().writer(io, &buffer);
            try writer.interface.print("{s}\n", .{item});
            try writer.interface.flush();
        }
        std.process.exit(2);
    }

    var problems: std.ArrayList([]const u8) = .empty;
    defer {
        for (problems.items) |item| allocator.free(item);
        problems.deinit(allocator);
    }

    for (paths) |path| {
        var report = try duplicateReport(io, allocator, path);
        defer {
            for (report.items) |item| allocator.free(item);
            report.deinit(allocator);
        }
        try problems.appendSlice(allocator, report.items);
    }

    if (problems.items.len > 0) {
        for (problems.items) |problem| {
            var buffer: [1024]u8 = undefined;
            var writer = Io.File.stderr().writer(io, &buffer);
            try writer.interface.print("{s}\n", .{problem});
            try writer.interface.flush();
        }
        std.process.exit(1);
    }

    try guard.printLine(io, "ok: scanned {d} Phase 1 helper file(s) with no duplicate top-level declarations", .{paths.len});
    std.process.exit(0);
}