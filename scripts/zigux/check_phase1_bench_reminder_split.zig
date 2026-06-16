// Ported from check-phase1-bench-reminder-split.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_BENCH_REMINDER_SPLIT_SELF_TEST=pass";

const HISTORICAL_GAP_CONTEXT = "historical";

const HISTORICAL_GAP_HINT = "`scripts\\zigux/check_phase1_bench.zig`";

const SHIPPED_BENCH_CHECKER = "current `master` does ship `scripts\\zigux/check_phase1_bench.zig`, and `.github/workflows/zigux-bootstrap.yml` self-tests it";

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
    const scripts_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(scripts_path);
    const docs_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(docs_path);
    const review_path = try guard.joinPath(allocator, root, "Documentation/zigux/review-checklist.md");
    defer allocator.free(review_path);
    const tests_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(tests_path);

    const scripts_readme = try guard.readUtf8File(io, allocator, scripts_path);
    defer allocator.free(scripts_readme);
    const docs_readme = try guard.readUtf8File(io, allocator, docs_path);
    defer allocator.free(docs_readme);
    const review_checklist = try guard.readUtf8File(io, allocator, review_path);
    defer allocator.free(review_checklist);
    const tests_readme = try guard.readUtf8File(io, allocator, tests_path);
    defer allocator.free(tests_readme);

    if (std.mem.indexOf(u8, scripts_readme, SHIPPED_BENCH_CHECKER) == null) {
        const issue = try std.fmt.allocPrint(allocator, "scripts_readme_missing_shipped_checker_wording", .{});
        try failures.append(allocator, issue);
    }

    const shared_texts = [_][]const u8{ docs_readme, review_checklist, tests_readme };
    for (shared_texts) |text| {
        if (std.mem.indexOf(u8, text, HISTORICAL_GAP_HINT) == null) {
            const issue = try std.fmt.allocPrint(allocator, "missing_gap_marker", .{});
            try failures.append(allocator, issue);
            continue;
        }
        const lower = try std.ascii.allocLowerString(allocator, text);
        defer allocator.free(lower);
        if (std.mem.indexOf(u8, lower, HISTORICAL_GAP_CONTEXT) == null and std.mem.indexOf(u8, lower, "missing") == null) {
            const issue = try std.fmt.allocPrint(allocator, "missing_gap_context", .{});
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
    try guard.printLine(io, "PHASE1_BENCH_REMINDER_SPLIT_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_BENCH_REMINDER_SPLIT_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
