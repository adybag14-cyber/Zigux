const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const default_doc_rel = "Documentation/zigux/release-sequencing.md";

const REQUIRED_SNIPPETS = [_][]const u8{
    "# Zigux Release Sequencing",
    "`RELEASE_PLAN_STATE=active`",
    "`RELEASE_FOUNDATION_PHASES=phase1,phase2`",
    "`RELEASE_ACTIVE_GATING_PHASES=phase3,phase4`",
    "`RELEASE_CONDITIONAL_RELEASE_PHASES=phase5`",
    "`RELEASE_SUPPORTING_PHASES=phase6,phase8,phase13`",
    "`RELEASE_RISK_PHASE3_SHARED_REMINDER=active`",
    "`RELEASE_RISK_PHASE4_MISSING_COMPANIONS=active`",
    "`RELEASE_RISK_PHASE13_VALIDATE_ROUTE=active`",
    "`RELEASE_NEXT_PMO_STEP=",
};

const REQUIRED_SECTIONS = [_][]const u8{
    "## Status",
    "## Sequencing Baseline",
    "## Current Tranche Map",
    "## Release Order For Current Master",
    "## Open Coordination Risks",
    "## Review Use",
    "## Boundaries",
    "## Next PMO Step",
};

fn validateDoc(text: []const u8, errors: *std.ArrayList([]const u8), allocator: std.mem.Allocator) !void {
    var missing_markers: std.ArrayList([]const u8) = .empty;
    defer missing_markers.deinit(allocator);

    for (REQUIRED_SNIPPETS) |snippet| {
        if (std.mem.indexOf(u8, text, snippet) == null) {
            try missing_markers.append(allocator, snippet);
        }
    }
    if (missing_markers.items.len != 0) {
        var joined: std.ArrayList(u8) = .empty;
        defer joined.deinit(allocator);
        for (missing_markers.items, 0..) |marker, index| {
            if (index != 0) try joined.appendSlice(allocator, ", ");
            try joined.appendSlice(allocator, marker);
        }
        const message = try std.fmt.allocPrint(allocator, "missing required sequencing markers: {s}", .{joined.items});
        try errors.append(allocator, message);
    }

    var missing_sections: std.ArrayList([]const u8) = .empty;
    defer missing_sections.deinit(allocator);
    for (REQUIRED_SECTIONS) |section| {
        if (std.mem.indexOf(u8, text, section) == null) {
            try missing_sections.append(allocator, section);
        }
    }
    if (missing_sections.items.len != 0) {
        var joined: std.ArrayList(u8) = .empty;
        defer joined.deinit(allocator);
        for (missing_sections.items, 0..) |section, index| {
            if (index != 0) try joined.appendSlice(allocator, ", ");
            try joined.appendSlice(allocator, section);
        }
        const message = try std.fmt.allocPrint(allocator, "missing required sections: {s}", .{joined.items});
        try errors.append(allocator, message);
    }
}

fn printStderr(io: Io, comptime fmt: []const u8, args: anytype) !void {
    var buffer: [1024]u8 = undefined;
    var writer = Io.File.stderr().writer(io, &buffer);
    try writer.interface.print(fmt ++ "\n", args);
    try writer.interface.flush();
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

    var doc_rel: []const u8 = default_doc_rel;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--doc")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            doc_rel = args[index];
            continue;
        }
        std.process.exit(2);
    }

    if (!guard.pathExists(io, doc_rel)) {
        try printStderr(io, "release sequencing document not found: {s}", .{doc_rel});
        std.process.exit(1);
    }

    const text = try guard.readUtf8File(io, allocator, doc_rel);
    defer allocator.free(text);

    var errors: std.ArrayList([]const u8) = .empty;
    defer {
        for (errors.items) |message| allocator.free(message);
        errors.deinit(allocator);
    }
    try validateDoc(text, &errors, allocator);

    if (errors.items.len != 0) {
        for (errors.items) |message| try printStderr(io, "{s}", .{message});
        std.process.exit(1);
    }

    try guard.printLine(io, "release sequencing note OK: {s}", .{doc_rel});
}