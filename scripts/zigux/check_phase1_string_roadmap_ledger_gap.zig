// Ported from check-phase1-string-roadmap-ledger-gap.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

const GAP_NOTE_REL = "Documentation/zigux/phase1-string-roadmap-ledger-gap.md";

const REQUIRED_EXACT_LINES = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "roadmap_target", .marker = "- `ROADMAP_PHASE1_TARGET=tools/lib/string.zig`" },
    .{ .label = "ledger_target", .marker = "- `LEDGER_COMMIT6_TARGET=tools/lib/string.zig`" },
    .{ .label = "public_tree_gap", .marker = "- current public-tree readback of `tools/lib` shows `cmdline.zig` as the only directly readable `.zig` helper in that directory in this environment" },
    .{ .label = "authenticated_gap", .marker = "- authenticated contents reads for `tools/lib/string.zig` on current `master` return missing" },
    .{ .label = "reminder_surface_gap", .marker = "- current Phase 1 reminder surfaces still name `tools/lib/string.zig` as a direct-anchor helper in `Documentation/zigux/phase1-host-helper-lane-sequencing.md` and `zigux/tests/fixtures/phase1_helper_manifest.json`" },
    .{ .label = "lane_decision", .marker = "- treat `tools/lib/string.zig` as a roadmap-and-ledger target that is not currently materialized on readable `master`" },
    .{ .label = "proof_boundary", .marker = "- do not present the current string manifest anchors as direct helper-file proof while `tools/lib/string.zig` remains unreadable on current `master`" },
    .{ .label = "next_step", .marker = "- align the current Phase 1 reminder packet one surface at a time so it distinguishes the roadmap-ledger string target from direct current-master helper evidence" },
};

fn collectFailures(
    io: Io,
    allocator: std.mem.Allocator,
    root: []const u8,
) !std.ArrayList([]const u8) {
    var failures: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    {
        const relative_path = "Documentation/zigux/phase1-string-roadmap-ledger-gap.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures;

    {
        const relative_path = "Documentation/zigux/phase1-string-roadmap-ledger-gap.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        const text = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
                try failures.append(allocator, issue);
                return failures;
            },
            else => return err,
        };
        defer allocator.free(text);
        for (REQUIRED_EXACT_LINES) |entry| {
            const label = try std.fmt.allocPrint(allocator, "gap_note:{s}", .{entry.label});
            defer allocator.free(label);
            try guard.appendExactTrimmedLineIssue(allocator, &failures, text, label, entry.marker);
        }
    }

    return failures;
}

fn buildSampleRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    var content = std.ArrayList(u8).empty;
    defer content.deinit(allocator);
    try content.appendSlice(allocator, "# sample\n\n");
    for (REQUIRED_EXACT_LINES) |entry| {
        try content.appendSlice(allocator, entry.marker);
        try content.append(allocator, '\n');
    }
    const full_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase1-string-roadmap-ledger-gap.md");
    defer allocator.free(full_path);
    try guard.writeUtf8File(io, full_path, content.items);
}

fn applyMutation(io: Io, allocator: std.mem.Allocator, root: []const u8, needle: []const u8, operation: []const u8) !void {
    const relative_path = "Documentation/zigux/phase1-string-roadmap-ledger-gap.md";
    const full_path = try guard.joinPath(allocator, root, relative_path);
    defer allocator.free(full_path);
    const text = try guard.readUtf8File(io, allocator, full_path);
    defer allocator.free(text);
    const updated = if (std.mem.eql(u8, operation, "remove")) blk: {
        const pattern = try std.fmt.allocPrint(allocator, "{s}\n", .{needle});
        defer allocator.free(pattern);
        const index = std.mem.indexOf(u8, text, pattern) orelse return;
        break :blk try std.fmt.allocPrint(allocator, "{s}{s}", .{ text[0..index], text[index + pattern.len ..] });
    } else if (std.mem.eql(u8, operation, "duplicate")) blk: {
        const index = std.mem.indexOf(u8, text, needle) orelse return;
        break :blk try std.fmt.allocPrint(allocator, "{s}{s}\n{s}{s}", .{ text[0..index], needle, needle, text[index + needle.len ..] });
    } else return;
    defer allocator.free(updated);
    try guard.writeUtf8File(io, full_path, updated);
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "selftest");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    try buildSampleRepo(io, allocator, root);
    {
        var failures = try collectFailures(io, allocator, root);
        defer {
            for (failures.items) |item| allocator.free(item);
            failures.deinit(allocator);
        }
        try guard.expectSelfTest(failures.items.len == 0);
    }
    for (REQUIRED_EXACT_LINES) |entry| {
        try applyMutation(io, allocator, root, entry.marker, "remove");
        var failures = try collectFailures(io, allocator, root);
        try guard.expectSelfTest(failures.items.len > 0);
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
        try buildSampleRepo(io, allocator, root);
        try applyMutation(io, allocator, root, entry.marker, "duplicate");
        failures = try collectFailures(io, allocator, root);
        try guard.expectSelfTest(failures.items.len > 0);
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
        try buildSampleRepo(io, allocator, root);
    }
    try guard.printLine(io, "self-test:ok", .{});
    try guard.printLine(io, "SELF_TEST_CASE_COUNT={d}", .{@as(usize, 17)});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var explicit_root: ?[]const u8 = null;
    var self_test = false;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    const root = if (explicit_root) |value| value else try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);

    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    if (failures.items.len > 0) {
        try guard.printLine(io, "PHASE1_GUARD=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "PHASE1_GUARD=pass", .{});
    std.process.exit(0);
}
