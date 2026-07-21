// Ported from check-phase1-reminder-companion-packet.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_REMINDER_COMPANION_PACKET_SELF_TEST=pass";

const DIRECT_OWNER_REL = "scripts\\zigux/check_phase1_direct_owner_markers.zig";

const DOCS_ROOT_REL = "Documentation/zigux/README.md";

const PHASE1_CLOSURE_REL = "Documentation/zigux/phase1-closure.md";

const REQUIRED_EXACT_LINES_ENTRIES = [_]struct { file: []const u8, marker: []const u8 }{
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "- `scripts\\zigux/check_phase1_string_review_packet.zig`" },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "- `scripts\\zigux/check_phase1_direct_owner_markers.zig`" },
    .{ .file = "Documentation/zigux/README.md", .marker = "- `scripts\\zigux/check_phase1_string_review_packet.zig`" },
    .{ .file = "Documentation/zigux/README.md", .marker = "- `scripts\\zigux/check_phase1_direct_owner_markers.zig`" },
    .{ .file = "Documentation/zigux/README.md", .marker = "  * the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts\\zigux/validate_phase1_closure.zig` keep the current-master-safe closure packet explicit, `scripts\\zigux/check_phase1_string_review_packet.zig`, `scripts\\zigux/check_phase1_direct_owner_markers.zig`, and `scripts\\zigux/check_phase1_bench.zig` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces." },
    .{ .file = "Documentation/zigux/README.md", .marker = "  * `zig run scripts/zigux/validate_phase1_closure.zig`, `zig run scripts/zigux/check_phase1_string_review_packet.zig -- --self-test`, `zig run scripts/zigux/check_phase1_direct_owner_markers.zig -- --self-test`, and `zig run scripts/zigux/check_phase1_bench.zig -- --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack." },
    .{ .file = "Documentation/zigux/review-checklist.md", .marker = "  * if the change touches the shared Phase 1 host-tools closure packet, do `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts\\zigux/validate_phase1_closure.zig`, `scripts\\zigux/check_phase1_string_review_packet.zig`, `scripts\\zigux/check_phase1_direct_owner_markers.zig`, `scripts\\zigux/check_phase1_bench.zig`, `scripts\\zigux/check_phase1_shared_reminder_packet.zig`, `zigux/tests/README.md`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?" },
    .{ .file = "scripts/zigux/README.md", .marker = "- `zig run scripts/zigux/validate_phase1_closure.zig`, `zig run scripts/zigux/check_phase1_string_review_packet.zig -- --self-test`, `zig run scripts/zigux/check_phase1_direct_owner_markers.zig -- --self-test`, and `zig run scripts/zigux/check_phase1_bench.zig -- --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route" },
    .{ .file = "scripts/zigux/README.md", .marker = "- `scripts\\zigux/check_phase1_string_review_packet.zig`, `scripts\\zigux/check_phase1_direct_owner_markers.zig`, `scripts\\zigux/check_phase1_bench.zig`, and `scripts\\zigux/validate_phase1_closure.zig` keep the shipped string-review, direct-owner, bench, and closure-validator packet explicit from the scripts root" },
    .{ .file = "scripts\\zigux/validate_phase1_closure.zig", .marker = "        \"scripts\\zigux/check_phase1_string_review_packet.zig,scripts\\zigux/check_phase1_direct_owner_markers.zig,\"" },
};

const REQUIRED_FILES = [_][]const u8{
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts\\zigux/validate_phase1_closure.zig",
    "scripts\\zigux/check_phase1_string_review_packet.zig",
    "scripts\\zigux/check_phase1_direct_owner_markers.zig",
};

const REVIEW_CHECKLIST_REL = "Documentation/zigux/review-checklist.md";

const SCRIPTS_README_REL = "scripts/zigux/README.md";

const STRING_REVIEW_REL = "scripts\\zigux/check_phase1_string_review_packet.zig";

const VALIDATOR_REL = "scripts\\zigux/validate_phase1_closure.zig";

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
        const relative_path = "Documentation/zigux/phase1-closure.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "Documentation/zigux/README.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "Documentation/zigux/review-checklist.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "scripts/zigux/README.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "scripts\\zigux/validate_phase1_closure.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "scripts\\zigux/check_phase1_string_review_packet.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "scripts\\zigux/check_phase1_direct_owner_markers.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures;

    for (REQUIRED_EXACT_LINES_ENTRIES) |entry| {
        const full_path = try guard.joinPath(allocator, root, entry.file);
        defer allocator.free(full_path);
        const text = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{entry.file});
                try failures.append(allocator, issue);
                continue;
            },
            else => return err,
        };
        defer allocator.free(text);
        const label = try std.fmt.allocPrint(allocator, "{s}:{s}", .{ entry.file, entry.marker });
        defer allocator.free(label);
        try guard.appendExactTrimmedLineIssue(allocator, &failures, text, label, entry.marker);
    }

    return failures;
}

fn buildSampleRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (REQUIRED_EXACT_LINES_ENTRIES) |entry| {
        const full_path = try guard.joinPath(allocator, root, entry.file);
        defer allocator.free(full_path);
        const existing = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => try allocator.dupe(u8, "# sample\n\n"),
            else => return err,
        };
        defer allocator.free(existing);
        const updated = try std.fmt.allocPrint(allocator, "{s}{s}\n", .{ existing, entry.marker });
        defer allocator.free(updated);
        try guard.writeUtf8File(io, full_path, updated);
    }
    for (REQUIRED_FILES) |relative_path| {
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            try guard.writeUtf8File(io, full_path, "# placeholder\n");
        }
    }
}

fn applyMutation(io: Io, allocator: std.mem.Allocator, root: []const u8, file: []const u8, needle: []const u8, operation: []const u8) !void {
    const full_path = try guard.joinPath(allocator, root, file);
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
    for (REQUIRED_EXACT_LINES_ENTRIES) |entry| {
        try applyMutation(io, allocator, root, entry.file, entry.marker, "remove");
        var failures = try collectFailures(io, allocator, root);
        try guard.expectSelfTest(failures.items.len > 0);
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
        try buildSampleRepo(io, allocator, root);
        try applyMutation(io, allocator, root, entry.file, entry.marker, "duplicate");
        failures = try collectFailures(io, allocator, root);
        try guard.expectSelfTest(failures.items.len > 0);
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
        try buildSampleRepo(io, allocator, root);
    }
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_REMINDER_COMPANION_PACKET_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 21)});
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
        try guard.printLine(io, "PHASE1_REMINDER_COMPANION_PACKET_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
