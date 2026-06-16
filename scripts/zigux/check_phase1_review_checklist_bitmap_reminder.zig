// Ported from check-phase1-review-checklist-bitmap-reminder.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_REVIEW_CHECKLIST_BITMAP_REMINDER_SELF_TEST=pass";

const EXPECTED_BITMAP_REMINDER_LINE = "  * if the change touches the shared Phase 5 sample packet, do the docs still say clearly that there is no standalone `samples/zigux/*bitmap*` reference sample and that direct bitmap helper reviewability remains under `tools/lib/bitmap.zig`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, and `Documentation/zigux/phase4-reversible-delivery-evidence.md`, while runtime bitmap work stays in the separate Phase 9 lane through `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, and `zigux/tests/phase9_build.zig` rather than the four shipped Phase 5 samples?";

const FORBIDDEN_SNIPPETS = [_][]const u8{
    "`Documentation/zigux/phase1-closure.md`",
    "`Documentation/zigux/phase4-validation-matrix.md`",
    "`samples/zigux/README.md`, `Documentation/zigux/phase9-runtime-bitmap-survey.md`",
    "`zigux/kernel/runtime_loader.zig`",
    "`zigux/kernel/runtime_loader_contract.zig`",
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

    const relative_path = "Documentation/zigux/review-checklist.md";
    const full_path = try guard.joinPath(allocator, root, relative_path);
    defer allocator.free(full_path);
    if (!guard.pathExists(io, full_path)) {
        try guard.appendMissingFileIssue(allocator, &failures, relative_path);
        return failures;
    }
    const text = try guard.readUtf8File(io, allocator, full_path);
    defer allocator.free(text);

    const count = guard.trimmedExactLineCount(text, EXPECTED_BITMAP_REMINDER_LINE);
    if (count != 1) {
        const issue = try std.fmt.allocPrint(allocator, "expected_bitmap_reminder_line_once:actual={d}", .{count});
        try failures.append(allocator, issue);
    }
    for (FORBIDDEN_SNIPPETS) |snippet| {
        if (std.mem.indexOf(u8, text, snippet) != null) {
            const issue = try std.fmt.allocPrint(allocator, "forbidden_snippet_present:{s}", .{snippet});
            try failures.append(allocator, issue);
        }
    }

    return failures;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "selftest");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    try guard.expectSelfTest(failures.items.len == 0);
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_GUARD_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_REVIEW_CHECKLIST_BITMAP_REMINDER_CHECK=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "FAILURE={s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "PHASE1_REVIEW_CHECKLIST_BITMAP_REMINDER_CHECK=pass", .{});
    std.process.exit(0);
}

